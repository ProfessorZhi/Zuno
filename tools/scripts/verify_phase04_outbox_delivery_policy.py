from __future__ import annotations

import asyncio
import socket
import subprocess
import time
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
from zuno.platform.queue import (
    OutboxPublishPolicy,
    PostgresOutboxRabbitMQPublisher,
    RabbitMQTopology,
    RabbitMQTransport,
)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
RABBITMQ_CONTAINER = "zuno-rabbitmq"


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.outbox.policy.exchange.{suffix}",
        queue=f"phase04.outbox.policy.queue.{suffix}",
        routing_key=f"phase04.outbox.policy.route.{suffix}",
        dead_letter_exchange=f"phase04.outbox.policy.dlx.{suffix}",
        dead_letter_queue=f"phase04.outbox.policy.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.outbox.policy.dead.{suffix}",
    )


def _docker(action: str) -> None:
    result = subprocess.run(
        ["docker", action, RABBITMQ_CONTAINER],
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def _migrate_database() -> None:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def _wait_for_port(*, available: bool, timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with socket.create_connection(("localhost", 5672), timeout=1):
                current = True
        except OSError:
            current = False
        if current is available:
            return
        time.sleep(0.5)
    state = "available" if available else "unavailable"
    raise TimeoutError(f"RabbitMQ AMQP port did not become {state}")


def _wait_for_health(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    last_status = ""
    while time.time() < deadline:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", RABBITMQ_CONTAINER],
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
        last_status = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0 and last_status == "healthy":
            return
        time.sleep(1)
    raise TimeoutError(f"RabbitMQ container did not become healthy: {last_status}")


async def _close_transport(transport: RabbitMQTransport | None) -> None:
    if transport is None:
        return
    try:
        await asyncio.wait_for(transport.close(), timeout=5)
    except Exception:
        pass


async def _verify() -> list[str]:
    errors: list[str] = []
    _migrate_database()
    engine = create_foundation_engine(DATABASE_URL)
    topology = _topology()
    topic = f"phase04.outbox.delivery-policy.{uuid4().hex}"
    transport: RabbitMQTransport | None = RabbitMQTransport(RABBITMQ_URL, robust=False)
    rabbitmq_stopped = False
    topology_declared = False
    event_id = ""
    try:
        await transport.connect()
        await transport.declare_topology(topology)
        topology_declared = True
        with InfrastructureUnitOfWork(engine, tenant_id="tenant-phase04") as repo:
            event_id = repo.enqueue_outbox(
                aggregate_id="phase04-outbox-delivery-policy",
                topic=topic,
                payload={"scenario": "outbox_delivery_policy", "marker": uuid4().hex},
                idempotency_key=f"phase04-outbox-delivery-policy-{uuid4().hex}",
            )

        publisher = PostgresOutboxRabbitMQPublisher(
            engine=engine,
            transport=transport,
            topology=topology,
            worker_id="phase04-outage-publisher",
            tenant_id="tenant-phase04",
            trace_id="trace-phase04-outbox-outage",
            policy=OutboxPublishPolicy(
                max_attempts=2,
                base_backoff_seconds=2,
                max_backoff_seconds=2,
                publish_timeout_seconds=1,
            ),
        )

        _docker("stop")
        rabbitmq_stopped = True
        _wait_for_port(available=False)

        first_batch = await publisher.publish_batch(limit=1)
        if first_batch.published or len(first_batch.failed) != 1:
            errors.append("first broker outage did not produce one persisted outbox failure")
        else:
            first_failure = first_batch.failed[0]
            if first_failure.status != "pending" or first_failure.retry_count != 1:
                errors.append("first outbox failure did not schedule retry_count=1")
        with InfrastructureUnitOfWork(engine) as repo:
            first_backlog = repo.outbox_backlog(topic=topic)
        if first_backlog.delayed != 1 or first_backlog.dead_letter != 0:
            errors.append("first outbox failure was not visible as delayed backlog")

        await asyncio.sleep(2.1)
        second_batch = await publisher.publish_batch(limit=1)
        if second_batch.published or len(second_batch.failed) != 1:
            errors.append("second broker outage did not produce one persisted outbox failure")
        else:
            second_failure = second_batch.failed[0]
            if second_failure.status != "dead_letter" or second_failure.retry_count != 2:
                errors.append("retry exhaustion did not move the outbox event to dead_letter")
        with InfrastructureUnitOfWork(engine) as repo:
            exhausted_backlog = repo.outbox_backlog(topic=topic)
        if exhausted_backlog.dead_letter != 1 or any(
            [exhausted_backlog.ready, exhausted_backlog.delayed, exhausted_backlog.claimed]
        ):
            errors.append("dead-lettered outbox event was not isolated from publishable backlog")

        await _close_transport(transport)
        transport = None
        _docker("start")
        rabbitmq_stopped = False
        _wait_for_port(available=True)
        _wait_for_health()

        transport = RabbitMQTransport(RABBITMQ_URL)
        await transport.connect(timeout_seconds=30)
        with InfrastructureUnitOfWork(engine) as repo:
            replay = repo.replay_dead_letter_outbox(
                event_id=event_id,
                replay_owner="phase04-operator",
            )
        if replay.status != "pending" or replay.replay_count != 1:
            errors.append("manual outbox replay did not return the event to pending")

        recovery_publisher = PostgresOutboxRabbitMQPublisher(
            engine=engine,
            transport=transport,
            topology=topology,
            worker_id="phase04-recovery-publisher",
            tenant_id="tenant-phase04",
            trace_id="trace-phase04-outbox-replay",
        )
        recovered = await recovery_publisher.publish_batch(limit=1)
        if [item.event_id for item in recovered.published] != [event_id] or recovered.failed:
            errors.append("replayed outbox event was not confirmed after RabbitMQ recovery")

        delivery = await transport.get(topology.queue, timeout=10)
        if delivery is None:
            errors.append("replayed outbox event was missing from RabbitMQ")
        else:
            if delivery.message_id != event_id:
                errors.append("replayed RabbitMQ message id changed")
            expected_headers = {
                "outbox_publish_attempt": 3,
                "outbox_retry_count": 0,
                "outbox_replay_count": 1,
            }
            for header, expected in expected_headers.items():
                if delivery.headers.get(header) != expected:
                    errors.append(f"RabbitMQ delivery header {header} was not {expected}")
            with InfrastructureUnitOfWork(engine, tenant_id="tenant-phase04") as repo:
                receipt = repo.record_inbox_receipt(
                    consumer="phase04-outbox-policy-consumer",
                    message_id=delivery.message_id,
                    payload=delivery.payload,
                    tenant_id="tenant-phase04",
                )
            if not receipt.first_seen:
                errors.append("replayed outbox delivery did not create a first-seen inbox receipt")
            await delivery.ack()

        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT status, publish_attempts, retry_count, replay_count,
                           last_error_code, last_replay_owner
                    FROM infra_outbox_events
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": event_id},
            ).one()
        if (
            row.status != "published"
            or row.publish_attempts != 3
            or row.retry_count != 0
            or row.replay_count != 1
            or not row.last_error_code
            or row.last_replay_owner != "phase04-operator"
        ):
            errors.append("final outbox delivery audit state did not preserve failure/replay history")
        with InfrastructureUnitOfWork(engine) as repo:
            final_backlog = repo.outbox_backlog(topic=topic)
        if any([final_backlog.ready, final_backlog.delayed, final_backlog.claimed, final_backlog.dead_letter]):
            errors.append("published outbox event remained in backlog visibility counts")
    finally:
        if rabbitmq_stopped:
            _docker("start")
        _wait_for_port(available=True)
        _wait_for_health()
        await _close_transport(transport)
        transport = None
        if topology_declared:
            cleanup_transport = RabbitMQTransport(RABBITMQ_URL)
            try:
                await cleanup_transport.connect(timeout_seconds=30)
                await cleanup_transport.delete_topology(topology)
            finally:
                await _close_transport(cleanup_transport)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM infra_inbox_messages "
                    "WHERE consumer = 'phase04-outbox-policy-consumer'"
                )
            )
            connection.execute(text("DELETE FROM infra_outbox_events WHERE topic = :topic"), {"topic": topic})
        engine.dispose()
    return errors


def verify_phase04_outbox_delivery_policy() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_outbox_delivery_policy()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 outbox delivery policy verification failed.")
        return 1
    print("PHASE04 outbox delivery policy verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
