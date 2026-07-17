from __future__ import annotations

import asyncio
from uuid import uuid4

from zuno.platform.queue import RabbitMQTopology, RabbitMQTransport

RABBITMQ_HOST = "127.0.0.1"
RABBITMQ_PORT = 5672


class _TcpPartitionProxy:
    def __init__(self, upstream_host: str, upstream_port: int) -> None:
        self.upstream_host = upstream_host
        self.upstream_port = upstream_port
        self.server: asyncio.AbstractServer | None = None
        self.partitioned = False
        self.forwarding = asyncio.Event()
        self.forwarding.set()
        self.connections: set[tuple[asyncio.StreamWriter, asyncio.StreamWriter]] = set()

    async def start(self) -> int:
        self.server = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        socket = self.server.sockets[0]
        return int(socket.getsockname()[1])

    async def partition(self) -> None:
        self.partitioned = True
        self.forwarding.clear()

    def restore(self) -> None:
        self.partitioned = False
        self.forwarding.set()

    async def close(self) -> None:
        self.partitioned = True
        self.forwarding.set()
        connections = list(self.connections)
        self.connections.clear()
        for client_writer, upstream_writer in connections:
            client_writer.close()
            upstream_writer.close()
        await asyncio.gather(
            *(
                writer.wait_closed()
                for pair in connections
                for writer in pair
            ),
            return_exceptions=True,
        )
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()

    async def _handle(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter) -> None:
        try:
            upstream_reader, upstream_writer = await asyncio.open_connection(
                self.upstream_host,
                self.upstream_port,
            )
        except OSError:
            client_writer.close()
            await client_writer.wait_closed()
            return

        pair = (client_writer, upstream_writer)
        self.connections.add(pair)
        try:
            await asyncio.gather(
                self._pipe(client_reader, upstream_writer),
                self._pipe(upstream_reader, client_writer),
            )
        finally:
            self.connections.discard(pair)
            client_writer.close()
            upstream_writer.close()
            await asyncio.gather(
                client_writer.wait_closed(),
                upstream_writer.wait_closed(),
                return_exceptions=True,
            )

    async def _pipe(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while data := await reader.read(64 * 1024):
                await self.forwarding.wait()
                writer.write(data)
                await writer.drain()
        except (ConnectionError, OSError):
            pass
def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.partition.exchange.{suffix}",
        queue=f"phase04.partition.queue.{suffix}",
        routing_key=f"phase04.partition.route.{suffix}",
        dead_letter_exchange=f"phase04.partition.dlx.{suffix}",
        dead_letter_queue=f"phase04.partition.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.partition.dead.{suffix}",
    )


async def _verify() -> list[str]:
    errors: list[str] = []
    proxy = _TcpPartitionProxy(RABBITMQ_HOST, RABBITMQ_PORT)
    proxy_port = await proxy.start()
    topology = _topology()
    transport = RabbitMQTransport(f"amqp://guest:guest@127.0.0.1:{proxy_port}/")
    pre_partition_id = f"phase04-pre-partition-{uuid4().hex}"
    partition_attempt_id = f"phase04-during-partition-{uuid4().hex}"
    post_recovery_id = f"phase04-post-recovery-{uuid4().hex}"
    partition_confirmed_after_restore = False
    try:
        await transport.connect()
        await transport.declare_topology(topology)
        await transport.publish(
            topology,
            message_id=pre_partition_id,
            payload={"scenario": "network_partition", "stage": "before"},
            tenant_id="tenant-phase04",
            trace_id="trace-phase04-partition-before",
        )

        await proxy.partition()
        await asyncio.sleep(0.5)
        partition_failed_closed = False
        partition_publish_task = asyncio.create_task(
            transport.publish(
                topology,
                message_id=partition_attempt_id,
                payload={"scenario": "network_partition", "stage": "during"},
                tenant_id="tenant-phase04",
                trace_id="trace-phase04-partition-during",
            )
        )
        try:
            await asyncio.wait_for(
                asyncio.shield(partition_publish_task),
                timeout=3,
            )
        except Exception:
            partition_failed_closed = True
        if not partition_failed_closed:
            errors.append("RabbitMQ publish reported success while the client/broker network was partitioned")

        proxy.restore()
        try:
            await asyncio.wait_for(partition_publish_task, timeout=10)
            partition_confirmed_after_restore = True
        except Exception as exc:
            errors.append(f"RabbitMQ partition UNKNOWN publish could not be reconciled after restore: {exc}")
        await asyncio.sleep(0.5)
        await transport.close()
        transport = RabbitMQTransport(f"amqp://guest:guest@127.0.0.1:{proxy_port}/")
        try:
            await transport.connect(timeout_seconds=30)
            await asyncio.wait_for(
                transport.publish(
                    topology,
                    message_id=post_recovery_id,
                    payload={"scenario": "network_partition", "stage": "after"},
                    tenant_id="tenant-phase04",
                    trace_id="trace-phase04-partition-after",
                ),
                timeout=30,
            )
        except Exception as exc:
            errors.append(f"RabbitMQ robust transport did not recover after network restore: {exc}")

        deliveries: dict[str, tuple[dict[str, object], dict[str, object]]] = {}
        for _ in range(5):
            delivery = await transport.get(topology.queue, timeout=3)
            if delivery is None:
                break
            deliveries[delivery.message_id] = (delivery.payload, delivery.headers)
            await delivery.ack()
        if pre_partition_id not in deliveries:
            errors.append("RabbitMQ pre-partition persistent message was missing after recovery")
        if post_recovery_id not in deliveries:
            errors.append("RabbitMQ post-recovery confirmed message was missing")
        if partition_confirmed_after_restore and partition_attempt_id not in deliveries:
            errors.append("RabbitMQ partition UNKNOWN publish was confirmed but missing during reconciliation")
        for message_id in [pre_partition_id, partition_attempt_id, post_recovery_id]:
            if message_id not in deliveries:
                continue
            _payload, headers = deliveries[message_id]
            if headers.get("tenant_id") != "tenant-phase04":
                errors.append(f"RabbitMQ tenant header was lost for {message_id}")
            if not str(headers.get("trace_id", "")).startswith("trace-phase04-partition-"):
                errors.append(f"RabbitMQ trace header was lost for {message_id}")
        await transport.delete_topology(topology)
    finally:
        proxy.restore()
        await transport.close()
        await proxy.close()
    return errors


def verify_phase04_rabbitmq_network_partition() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_rabbitmq_network_partition()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 RabbitMQ network partition verification failed.")
        return 1
    print("PHASE04 RabbitMQ network partition verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
