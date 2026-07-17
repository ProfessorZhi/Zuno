from __future__ import annotations

import asyncio
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
from zuno.platform.queue import PostgresOutboxRabbitMQPublisher, RabbitMQTopology, RabbitMQTransport

RABBITMQ_HOST = "127.0.0.1"
RABBITMQ_PORT = 5672
DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


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


async def _verify_outbox_partition_recovery() -> list[str]:
    errors: list[str] = []
    engine = create_foundation_engine(DATABASE_URL)
    proxy = _TcpPartitionProxy(RABBITMQ_HOST, RABBITMQ_PORT)
    proxy_port = await proxy.start()
    proxy_url = f"amqp://guest:guest@127.0.0.1:{proxy_port}/"
    topology = _topology()
    transport = RabbitMQTransport(proxy_url)
    payload = {"scenario": "outbox_partition", "marker": uuid4().hex}
    try:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM infra_inbox_messages WHERE consumer = 'phase04-partition-consumer'")
            )
            connection.execute(
                text("DELETE FROM infra_outbox_events WHERE topic = 'phase04.outbox.partition'")
            )
        with InfrastructureUnitOfWork(engine) as repo:
            event_id = repo.enqueue_outbox(
                aggregate_id="phase04-outbox-partition",
                topic="phase04.outbox.partition",
                payload=payload,
                idempotency_key=f"phase04-outbox-partition-{payload['marker']}",
            )
            if not repo.claim_outbox_event(event_id=event_id, worker_id="partitioned-publisher"):
                return ["partitioned outbox exact-event claim failed"]
            record = repo.load_claimed_outbox_event(
                event_id=event_id,
                worker_id="partitioned-publisher",
            )

        await transport.connect()
        await transport.declare_topology(topology)
        await proxy.partition()
        publish_task = asyncio.create_task(
            transport.publish(
                topology,
                message_id=record.event_id,
                payload={
                    "aggregate_id": record.aggregate_id,
                    "event_id": record.event_id,
                    "idempotency_key": record.idempotency_key,
                    "payload": record.payload,
                    "payload_hash": record.payload_hash,
                    "topic": record.topic,
                },
                tenant_id="tenant-phase04",
                trace_id="trace-phase04-outbox-partition-unknown",
            )
        )
        try:
            await asyncio.wait_for(asyncio.shield(publish_task), timeout=3)
            errors.append("outbox publish reported success during network partition")
        except TimeoutError:
            pass
        with engine.connect() as connection:
            status = connection.execute(
                text("SELECT status FROM infra_outbox_events WHERE event_id = :event_id"),
                {"event_id": event_id},
            ).scalar_one()
        if status != "claimed":
            errors.append(f"outbox status during confirm-UNKNOWN is {status!r}, expected 'claimed'")

        proxy.restore()
        try:
            await asyncio.wait_for(publish_task, timeout=10)
        except Exception as exc:
            errors.append(f"outbox UNKNOWN publish did not reconcile to a confirm after restore: {exc}")
        await transport.close()
        transport = RabbitMQTransport(proxy_url)
        await transport.connect(timeout_seconds=30)

        first_delivery = await transport.get(topology.queue, timeout=5)
        first_hash: str | None = None
        if first_delivery is None:
            errors.append("outbox partition-confirmed delivery was missing after restore")
        else:
            with InfrastructureUnitOfWork(engine) as repo:
                first_hash = repo.record_inbox(
                    consumer="phase04-partition-consumer",
                    message_id=first_delivery.message_id,
                    payload=first_delivery.payload,
                )
            await first_delivery.ack()

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE infra_outbox_events
                    SET claimed_at = now() - interval '5 minutes'
                    WHERE event_id = :event_id
                    """
                ),
                {"event_id": event_id},
            )
        with InfrastructureUnitOfWork(engine) as repo:
            reclaimed = repo.reclaim_stale_outbox_event(
                event_id=event_id,
                older_than_seconds=1,
            )
        if not reclaimed:
            errors.append("partition UNKNOWN exact-event outbox reclaim failed")

        publisher = PostgresOutboxRabbitMQPublisher(
            engine=engine,
            transport=transport,
            topology=topology,
            worker_id="partition-recovery-publisher",
            tenant_id="tenant-phase04",
            trace_id="trace-phase04-outbox-partition-recovery",
        )
        published = await publisher.publish_event(event_id=event_id)
        if published.event_id != event_id:
            errors.append("recovery publisher did not republish the partition UNKNOWN event")
        duplicate_delivery = await transport.get(topology.queue, timeout=5)
        if duplicate_delivery is None:
            errors.append("outbox partition recovery duplicate delivery was missing")
        else:
            with InfrastructureUnitOfWork(engine) as repo:
                duplicate_hash = repo.record_inbox(
                    consumer="phase04-partition-consumer",
                    message_id=duplicate_delivery.message_id,
                    payload=duplicate_delivery.payload,
                )
            if first_hash is not None and duplicate_hash != first_hash:
                errors.append("partition recovery duplicate inbox hash changed")
            await duplicate_delivery.ack()

        with engine.connect() as connection:
            outbox_status = connection.execute(
                text("SELECT status FROM infra_outbox_events WHERE event_id = :event_id"),
                {"event_id": event_id},
            ).scalar_one()
            inbox_count = connection.execute(
                text(
                    """
                    SELECT count(*)
                    FROM infra_inbox_messages
                    WHERE consumer = 'phase04-partition-consumer' AND message_id = :event_id
                    """
                ),
                {"event_id": event_id},
            ).scalar_one()
        if outbox_status != "published":
            errors.append(f"partition-recovered outbox status is {outbox_status!r}")
        if inbox_count != 1:
            errors.append(f"partition recovery inbox dedup row count is {inbox_count!r}")
        await transport.delete_topology(topology)
    finally:
        proxy.restore()
        await transport.close()
        await proxy.close()
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM infra_inbox_messages WHERE consumer = 'phase04-partition-consumer'")
            )
            connection.execute(
                text("DELETE FROM infra_outbox_events WHERE topic = 'phase04.outbox.partition'")
            )
        engine.dispose()
    return errors


async def _verify_consumer_crash_redelivery() -> list[str]:
    errors: list[str] = []
    engine = create_foundation_engine(DATABASE_URL)
    topology = _topology()
    transport = RabbitMQTransport(f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/")
    message_id = f"phase04-consumer-crash-{uuid4().hex}"
    payload = {"scenario": "consumer_crash", "message_id": message_id}
    followup_aggregate_id = f"phase04-consumer-result-{uuid4().hex}"
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM infra_inbox_messages "
                    "WHERE consumer = 'phase04-crash-redelivery-consumer'"
                )
            )
            connection.execute(
                text("DELETE FROM infra_outbox_events WHERE topic = 'phase04.consumer.result'")
            )
        await transport.connect()
        await transport.declare_topology(topology)
        await transport.publish(
            topology,
            message_id=message_id,
            payload=payload,
            tenant_id="tenant-phase04",
            trace_id="trace-phase04-consumer-crash",
        )
        first_delivery = await transport.get(topology.queue, timeout=5)
        if first_delivery is None:
            return ["consumer crash scenario did not receive the first delivery"]
        try:
            with InfrastructureUnitOfWork(engine) as repo:
                receipt = repo.record_inbox_receipt(
                    consumer="phase04-crash-redelivery-consumer",
                    message_id=first_delivery.message_id,
                    payload=first_delivery.payload,
                )
                if not receipt.first_seen:
                    errors.append("first consumer delivery was already recorded as duplicate")
                repo.enqueue_outbox(
                    aggregate_id=followup_aggregate_id,
                    topic="phase04.consumer.result",
                    payload={"source_message_id": first_delivery.message_id},
                    idempotency_key=f"phase04-consumer-result-{first_delivery.message_id}",
                )
                raise RuntimeError("simulated consumer process exit before transaction commit and ACK")
        except RuntimeError:
            pass

        await transport.close()
        transport = RabbitMQTransport(f"amqp://guest:guest@{RABBITMQ_HOST}:{RABBITMQ_PORT}/")
        await transport.connect(timeout_seconds=30)
        redelivery = await transport.get(topology.queue, timeout=10)
        if redelivery is None:
            errors.append("unacked consumer delivery was not redelivered after connection loss")
        else:
            if redelivery.message_id != message_id or not redelivery.redelivered:
                errors.append("consumer crash redelivery lost message identity or redelivered flag")
            with InfrastructureUnitOfWork(engine) as repo:
                receipt = repo.record_inbox_receipt(
                    consumer="phase04-crash-redelivery-consumer",
                    message_id=redelivery.message_id,
                    payload=redelivery.payload,
                )
                if not receipt.first_seen:
                    errors.append("rolled-back inbox receipt survived the consumer crash")
                repo.enqueue_outbox(
                    aggregate_id=followup_aggregate_id,
                    topic="phase04.consumer.result",
                    payload={"source_message_id": redelivery.message_id},
                    idempotency_key=f"phase04-consumer-result-{redelivery.message_id}",
                )
            await redelivery.ack()

        await transport.publish(
            topology,
            message_id=message_id,
            payload=payload,
            tenant_id="tenant-phase04",
            trace_id="trace-phase04-consumer-duplicate",
        )
        duplicate = await transport.get(topology.queue, timeout=5)
        if duplicate is None:
            errors.append("consumer duplicate delivery was missing")
        else:
            with InfrastructureUnitOfWork(engine) as repo:
                receipt = repo.record_inbox_receipt(
                    consumer="phase04-crash-redelivery-consumer",
                    message_id=duplicate.message_id,
                    payload=duplicate.payload,
                )
                if receipt.first_seen:
                    errors.append("duplicate consumer delivery was incorrectly treated as first-seen")
            await duplicate.ack()

        with engine.connect() as connection:
            inbox_count = connection.execute(
                text(
                    """
                    SELECT count(*)
                    FROM infra_inbox_messages
                    WHERE consumer = 'phase04-crash-redelivery-consumer'
                      AND message_id = :message_id
                    """
                ),
                {"message_id": message_id},
            ).scalar_one()
            followup_count = connection.execute(
                text("SELECT count(*) FROM infra_outbox_events WHERE aggregate_id = :aggregate_id"),
                {"aggregate_id": followup_aggregate_id},
            ).scalar_one()
        if inbox_count != 1:
            errors.append(f"consumer crash inbox receipt count is {inbox_count!r}")
        if followup_count != 1:
            errors.append(f"consumer crash follow-up outbox count is {followup_count!r}")
        await transport.delete_topology(topology)
    finally:
        await transport.close()
        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM infra_inbox_messages "
                    "WHERE consumer = 'phase04-crash-redelivery-consumer'"
                )
            )
            connection.execute(
                text("DELETE FROM infra_outbox_events WHERE topic = 'phase04.consumer.result'")
            )
        engine.dispose()
    return errors


def verify_phase04_rabbitmq_network_partition() -> list[str]:
    async def _run_all() -> list[str]:
        errors = await _verify()
        errors.extend(await _verify_outbox_partition_recovery())
        errors.extend(await _verify_consumer_crash_redelivery())
        return errors

    return asyncio.run(_run_all())


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
