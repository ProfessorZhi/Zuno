from __future__ import annotations

import asyncio
import socket
import subprocess
import time
from uuid import uuid4

from aiormq.exceptions import AMQPConnectionError

from zuno.platform.queue import RabbitMQTopology, RabbitMQTransport

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.restart.exchange.{suffix}",
        queue=f"phase04.restart.queue.{suffix}",
        routing_key=f"phase04.restart.route.{suffix}",
        dead_letter_exchange=f"phase04.restart.dlx.{suffix}",
        dead_letter_queue=f"phase04.restart.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.restart.dead.{suffix}",
    )


def _docker_restart_rabbitmq() -> str:
    result = subprocess.run(
        ["docker", "restart", "zuno-rabbitmq"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        if "is not running" in message:
            start = subprocess.run(
                ["docker", "start", "zuno-rabbitmq"],
                text=True,
                capture_output=True,
                check=False,
            )
            if start.returncode == 0:
                return start.stdout.strip()
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def _wait_for_amqp(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    last_error: OSError | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("localhost", 5672), timeout=2):
                return
        except OSError as exc:
            last_error = exc
            time.sleep(1)
    raise TimeoutError(f"RabbitMQ AMQP port did not recover: {last_error}")


def _wait_for_container_health(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    last_status = ""
    while time.time() < deadline:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", "zuno-rabbitmq"],
            text=True,
            capture_output=True,
            check=False,
        )
        last_status = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0 and last_status == "healthy":
            return
        time.sleep(1)
    raise TimeoutError(f"RabbitMQ container did not become healthy: {last_status}")


async def _connect_transport_with_retry(timeout_seconds: int = 90) -> RabbitMQTransport:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        transport = RabbitMQTransport(RABBITMQ_URL)
        try:
            await transport.connect()
            return transport
        except (AMQPConnectionError, ConnectionError, OSError) as exc:
            last_error = exc
            await transport.close()
            await asyncio.sleep(1)
    raise TimeoutError(f"RabbitMQ transport did not connect after restart: {last_error}")


async def _verify() -> list[str]:
    topology = _topology()
    message_id = f"phase04-broker-restart-{uuid4().hex}"
    payload = {"scenario": "broker_restart", "message_id": message_id}
    errors: list[str] = []

    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        await transport.publish(
            topology,
            message_id=message_id,
            payload=payload,
            tenant_id="tenant-phase04",
            trace_id="trace-phase04-broker-restart",
        )

    try:
        _docker_restart_rabbitmq()
        _wait_for_amqp()
        _wait_for_container_health()

        transport = await _connect_transport_with_retry()
        try:
            delivery = await transport.get(topology.queue, timeout=10)
            if delivery is None:
                errors.append("persistent RabbitMQ message was missing after broker restart")
            else:
                if delivery.message_id != message_id:
                    errors.append("RabbitMQ message id changed after broker restart")
                if delivery.payload != payload:
                    errors.append("RabbitMQ payload changed after broker restart")
                if delivery.headers.get("tenant_id") != "tenant-phase04":
                    errors.append("RabbitMQ tenant header was not preserved after broker restart")
                await delivery.ack()
            await transport.delete_topology(topology)
        finally:
            await transport.close()
    finally:
        _wait_for_amqp()
    return errors


def verify_phase04_rabbitmq_broker_restart() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_rabbitmq_broker_restart()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 RabbitMQ broker restart verification failed.")
        return 1
    print("PHASE04 RabbitMQ broker restart verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
