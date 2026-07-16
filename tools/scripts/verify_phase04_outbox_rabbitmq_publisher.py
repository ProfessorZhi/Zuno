from __future__ import annotations

import asyncio
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
from zuno.platform.queue import (
    PostgresOutboxRabbitMQPublisher,
    RabbitMQTopology,
    RabbitMQTransport,
)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.verify.outbox.exchange.{suffix}",
        queue=f"phase04.verify.outbox.queue.{suffix}",
        routing_key=f"phase04.verify.outbox.route.{suffix}",
        dead_letter_exchange=f"phase04.verify.outbox.dlx.{suffix}",
        dead_letter_queue=f"phase04.verify.outbox.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.verify.outbox.dead.{suffix}",
    )


async def _verify() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    topology = _topology()
    payload = {"kind": "phase04-outbox", "marker": uuid4().hex}
    errors: list[str] = []
    try:
        with InfrastructureUnitOfWork(engine) as repo:
            event_id = repo.enqueue_outbox(
                aggregate_id="phase04-run",
                topic="phase04.outbox.publisher",
                payload=payload,
                idempotency_key=f"phase04-outbox-{payload['marker']}",
            )

        async with RabbitMQTransport(RABBITMQ_URL) as transport:
            await transport.declare_topology(topology)
            try:
                publisher = PostgresOutboxRabbitMQPublisher(
                    engine=engine,
                    transport=transport,
                    topology=topology,
                    worker_id="phase04-publisher",
                    tenant_id="tenant-phase04",
                    trace_id="trace-phase04-outbox",
                )
                published = await publisher.publish_pending(limit=1)
                if [item.event_id for item in published] != [event_id]:
                    errors.append("outbox publisher did not return the claimed event id")

                delivery = await transport.get(topology.queue)
                if delivery is None:
                    errors.append("RabbitMQ did not receive the outbox event")
                else:
                    if delivery.message_id != event_id:
                        errors.append("RabbitMQ delivery message id does not match outbox event id")
                    if delivery.payload.get("payload") != payload:
                        errors.append("RabbitMQ delivery payload does not match outbox payload")
                    with InfrastructureUnitOfWork(engine) as repo:
                        repo.record_inbox(
                            consumer="phase04-consumer",
                            message_id=delivery.message_id,
                            payload=delivery.payload,
                        )
                    await delivery.ack()

                with engine.connect() as conn:
                    outbox_status = conn.execute(
                        text("SELECT status FROM infra_outbox_events WHERE event_id = :event_id"),
                        {"event_id": event_id},
                    ).scalar_one()
                    if outbox_status != "published":
                        errors.append(f"outbox status after publish is {outbox_status!r}")
                    inbox_status = conn.execute(
                        text(
                            """
                            SELECT status
                            FROM infra_inbox_messages
                            WHERE consumer = 'phase04-consumer' AND message_id = :event_id
                            """
                        ),
                        {"event_id": event_id},
                    ).scalar_one_or_none()
                    if inbox_status != "received":
                        errors.append(f"inbox status after consume is {inbox_status!r}")
            finally:
                await transport.delete_topology(topology)
    finally:
        engine.dispose()
    return errors


async def _verify_publish_crash_recovery() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    topology = _topology()
    payload = {"kind": "phase04-outbox-crash", "marker": uuid4().hex}
    errors: list[str] = []
    try:
        with InfrastructureUnitOfWork(engine) as repo:
            event_id = repo.enqueue_outbox(
                aggregate_id="phase04-run-crash",
                topic="phase04.outbox.publisher",
                payload=payload,
                idempotency_key=f"phase04-outbox-crash-{payload['marker']}",
            )
            claimed = repo.claim_outbox(worker_id="crashed-publisher", limit=1)
            if claimed != [event_id]:
                return [f"initial outbox claim mismatch: {claimed!r}"]
            record = repo.load_claimed_outbox_event(event_id=event_id, worker_id="crashed-publisher")

        async with RabbitMQTransport(RABBITMQ_URL) as transport:
            await transport.declare_topology(topology)
            try:
                await transport.publish(
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
                    trace_id="trace-phase04-crash-before-complete",
                )
                first_delivery = await transport.get(topology.queue)
                if first_delivery is None:
                    errors.append("first publish before simulated crash was not delivered")
                else:
                    with InfrastructureUnitOfWork(engine) as repo:
                        first_hash = repo.record_inbox(
                            consumer="phase04-crash-consumer",
                            message_id=first_delivery.message_id,
                            payload=first_delivery.payload,
                        )
                    await first_delivery.ack()

                    with engine.begin() as conn:
                        conn.execute(
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
                        reclaimed = repo.reclaim_stale_outbox_claims(older_than_seconds=1)
                    if reclaimed != [event_id]:
                        errors.append(f"stale outbox reclaim mismatch: {reclaimed!r}")

                    publisher = PostgresOutboxRabbitMQPublisher(
                        engine=engine,
                        transport=transport,
                        topology=topology,
                        worker_id="recovery-publisher",
                        tenant_id="tenant-phase04",
                        trace_id="trace-phase04-recovery",
                    )
                    published = await publisher.publish_pending(limit=1)
                    if [item.event_id for item in published] != [event_id]:
                        errors.append("recovery publisher did not republish reclaimed event")
                    duplicate_delivery = await transport.get(topology.queue)
                    if duplicate_delivery is None:
                        errors.append("duplicate recovery delivery was not received")
                    else:
                        with InfrastructureUnitOfWork(engine) as repo:
                            duplicate_hash = repo.record_inbox(
                                consumer="phase04-crash-consumer",
                                message_id=duplicate_delivery.message_id,
                                payload=duplicate_delivery.payload,
                            )
                        if duplicate_hash != first_hash:
                            errors.append("duplicate inbox receipt hash changed")
                        await duplicate_delivery.ack()

                with engine.connect() as conn:
                    outbox_status = conn.execute(
                        text("SELECT status FROM infra_outbox_events WHERE event_id = :event_id"),
                        {"event_id": event_id},
                    ).scalar_one()
                    if outbox_status != "published":
                        errors.append(f"recovered outbox status is {outbox_status!r}")
                    inbox_count = conn.execute(
                        text(
                            """
                            SELECT count(*)
                            FROM infra_inbox_messages
                            WHERE consumer = 'phase04-crash-consumer' AND message_id = :event_id
                            """
                        ),
                        {"event_id": event_id},
                    ).scalar_one()
                    if inbox_count != 1:
                        errors.append(f"inbox dedup row count after duplicate delivery is {inbox_count!r}")
            finally:
                await transport.delete_topology(topology)
    finally:
        engine.dispose()
    return errors


def verify_phase04_outbox_rabbitmq_publisher() -> list[str]:
    async def _run_all() -> list[str]:
        errors: list[str] = []
        errors.extend(await _verify())
        errors.extend(await _verify_publish_crash_recovery())
        return errors

    return asyncio.run(_run_all())


def main() -> int:
    errors = verify_phase04_outbox_rabbitmq_publisher()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 outbox RabbitMQ publisher verification failed.")
        return 1
    print("PHASE04 outbox RabbitMQ publisher verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
