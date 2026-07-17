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


def _topology(suffix: str) -> RabbitMQTopology:
    return RabbitMQTopology(
        exchange=f"phase04.verify.ordering.exchange.{suffix}",
        queue=f"phase04.verify.ordering.queue.{suffix}",
        routing_key=f"phase04.verify.ordering.route.{suffix}",
        dead_letter_exchange=f"phase04.verify.ordering.dlx.{suffix}",
        dead_letter_queue=f"phase04.verify.ordering.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.verify.ordering.dead.{suffix}",
    )


async def _verify() -> list[str]:
    suffix = uuid4().hex
    tenant_id = f"tenant-ordering-{suffix}"
    other_tenant_id = f"tenant-ordering-other-{suffix}"
    consumer = f"consumer-ordering-{suffix}"
    ordering_key = f"run:{suffix}"
    topic = f"phase04.ordering.{suffix}"
    topology = _topology(suffix)
    engine = create_foundation_engine(DATABASE_URL)
    errors: list[str] = []
    event_ids: list[str] = []
    try:
        with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
            event_ids = [
                repo.enqueue_outbox(
                    aggregate_id=ordering_key,
                    topic=topic,
                    payload={"sequence": sequence, "marker": suffix},
                    idempotency_key=f"{suffix}:{sequence}",
                    ordering_key=ordering_key,
                )
                for sequence in (1, 2, 3)
            ]
        with InfrastructureUnitOfWork(engine, tenant_id=other_tenant_id) as repo:
            other_event_id = repo.enqueue_outbox(
                aggregate_id=ordering_key,
                topic=topic,
                payload={"sequence": 1, "marker": suffix, "tenant": "other"},
                idempotency_key=f"{suffix}:other:1",
                ordering_key=ordering_key,
            )

        with engine.connect() as conn:
            allocated = conn.execute(
                text(
                    """
                    SELECT event_id, tenant_id, ordering_sequence
                    FROM infra_outbox_events
                    WHERE event_id = ANY(CAST(:event_ids AS text[]))
                    ORDER BY tenant_id, ordering_sequence
                    """
                ),
                {"event_ids": [*event_ids, other_event_id]},
            ).all()
        tenant_sequences = [int(row.ordering_sequence) for row in allocated if row.tenant_id == tenant_id]
        other_sequences = [
            int(row.ordering_sequence) for row in allocated if row.tenant_id == other_tenant_id
        ]
        if tenant_sequences != [1, 2, 3] or other_sequences != [1]:
            errors.append(
                f"tenant-scoped ordering allocation mismatch: {tenant_sequences!r}, {other_sequences!r}"
            )

        async with RabbitMQTransport(RABBITMQ_URL) as transport:
            await transport.declare_topology(topology)
            try:
                publisher = PostgresOutboxRabbitMQPublisher(
                    engine=engine,
                    transport=transport,
                    topology=topology,
                    worker_id=f"publisher-{suffix}",
                    tenant_id=tenant_id,
                    trace_id=f"trace-ordering-{suffix}",
                )
                for event_id in (event_ids[2], event_ids[0], event_ids[1]):
                    await publisher.publish_event(event_id=event_id)

                deliveries = []
                for expected_sequence in (3, 1, 2):
                    delivery = await transport.get(topology.queue)
                    if delivery is None:
                        errors.append(f"missing RabbitMQ delivery for sequence {expected_sequence}")
                        break
                    deliveries.append(delivery)
                    if delivery.headers.get("tenant_id") != tenant_id:
                        errors.append("RabbitMQ ordering delivery lost tenant header")
                    if delivery.headers.get("ordering_key") != ordering_key:
                        errors.append("RabbitMQ ordering delivery lost ordering key header")
                    if int(delivery.headers.get("ordering_sequence", 0)) != expected_sequence:
                        errors.append(
                            f"RabbitMQ out-of-order sequence mismatch for {expected_sequence}"
                        )

                if len(deliveries) == 3:
                    third = deliveries[0]
                    with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
                        receipt = repo.record_inbox_receipt(
                            consumer=consumer,
                            message_id=third.message_id,
                            payload=third.payload,
                            ordering_key=str(third.headers["ordering_key"]),
                            ordering_sequence=int(third.headers["ordering_sequence"]),
                        )
                        watermark = repo.delivery_watermark(
                            tenant_id=tenant_id,
                            consumer=consumer,
                            ordering_key=ordering_key,
                        )
                    if receipt.status != "buffered" or receipt.processable:
                        errors.append("sequence 3 was not durably buffered while sequence 1 was missing")
                    if (watermark.contiguous_sequence, watermark.max_seen_sequence) != (0, 3):
                        errors.append(f"initial delivery watermark mismatch: {watermark!r}")
                    await third.ack()

                    engine.dispose()
                    engine = create_foundation_engine(DATABASE_URL)

                    first = deliveries[1]
                    with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
                        receipt = repo.record_inbox_receipt(
                            consumer=consumer,
                            message_id=first.message_id,
                            payload=first.payload,
                            ordering_key=str(first.headers["ordering_key"]),
                            ordering_sequence=int(first.headers["ordering_sequence"]),
                        )
                        if not receipt.processable or receipt.contiguous_sequence != 1:
                            errors.append(f"sequence 1 did not advance ordering watermark: {receipt!r}")
                        repo.mark_inbox_processed(
                            tenant_id=tenant_id,
                            consumer=consumer,
                            message_id=first.message_id,
                        )
                    await first.ack()

                    second = deliveries[2]
                    with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
                        receipt = repo.record_inbox_receipt(
                            consumer=consumer,
                            message_id=second.message_id,
                            payload=second.payload,
                            ordering_key=str(second.headers["ordering_key"]),
                            ordering_sequence=int(second.headers["ordering_sequence"]),
                        )
                        if receipt.released_message_ids != (third.message_id,):
                            errors.append(f"contiguous release mismatch: {receipt.released_message_ids!r}")
                        released = repo.load_processable_inbox_messages(
                            tenant_id=tenant_id,
                            consumer=consumer,
                            message_ids=receipt.released_message_ids,
                        )
                        if [item.payload["payload"]["sequence"] for item in released] != [3]:
                            errors.append("restart reconciliation did not reload buffered sequence 3")
                        repo.mark_inbox_processed(
                            tenant_id=tenant_id,
                            consumer=consumer,
                            message_id=second.message_id,
                        )
                        for item in released:
                            repo.mark_inbox_processed(
                                tenant_id=tenant_id,
                                consumer=consumer,
                                message_id=item.message_id,
                            )
                        watermark = repo.delivery_watermark(
                            tenant_id=tenant_id,
                            consumer=consumer,
                            ordering_key=ordering_key,
                        )
                    if (watermark.contiguous_sequence, watermark.max_seen_sequence) != (3, 3):
                        errors.append(f"final delivery watermark mismatch: {watermark!r}")
                    await second.ack()

                    await transport.publish(
                        topology,
                        message_id=second.message_id,
                        payload=second.payload,
                        tenant_id=tenant_id,
                        trace_id=f"trace-ordering-duplicate-{suffix}",
                        ordering_key=ordering_key,
                        ordering_sequence=2,
                    )
                    duplicate = await transport.get(topology.queue)
                    if duplicate is None:
                        errors.append("duplicate ordered delivery was not received")
                    else:
                        with InfrastructureUnitOfWork(engine, tenant_id=tenant_id) as repo:
                            duplicate_receipt = repo.record_inbox_receipt(
                                consumer=consumer,
                                message_id=duplicate.message_id,
                                payload=duplicate.payload,
                                ordering_key=str(duplicate.headers["ordering_key"]),
                                ordering_sequence=int(duplicate.headers["ordering_sequence"]),
                            )
                        if duplicate_receipt.first_seen or duplicate_receipt.processable:
                            errors.append("duplicate ordered delivery was processed twice")
                        await duplicate.ack()

                with engine.connect() as conn:
                    statuses = conn.execute(
                        text(
                            """
                            SELECT ordering_sequence, status
                            FROM infra_inbox_messages
                            WHERE tenant_id = :tenant_id
                              AND consumer = :consumer
                              AND ordering_key = :ordering_key
                            ORDER BY ordering_sequence
                            """
                        ),
                        {
                            "tenant_id": tenant_id,
                            "consumer": consumer,
                            "ordering_key": ordering_key,
                        },
                    ).all()
                if [(int(row.ordering_sequence), row.status) for row in statuses] != [
                    (1, "processed"),
                    (2, "processed"),
                    (3, "processed"),
                ]:
                    errors.append(f"ordered inbox final statuses mismatch: {statuses!r}")
            finally:
                await transport.delete_topology(topology)
    finally:
        with engine.begin() as conn:
            tenant_params = {
                "tenant_id": tenant_id,
                "other_tenant_id": other_tenant_id,
            }
            conn.execute(
                text(
                    """
                    DELETE FROM infra_inbox_messages
                    WHERE tenant_id IN (:tenant_id, :other_tenant_id) AND consumer = :consumer
                    """
                ),
                {**tenant_params, "consumer": consumer},
            )
            conn.execute(
                text(
                    """
                    DELETE FROM infra_delivery_watermarks
                    WHERE tenant_id IN (:tenant_id, :other_tenant_id) AND consumer = :consumer
                    """
                ),
                {**tenant_params, "consumer": consumer},
            )
            conn.execute(
                text(
                    """
                    DELETE FROM infra_outbox_events
                    WHERE tenant_id IN (:tenant_id, :other_tenant_id) AND topic = :topic
                    """
                ),
                {**tenant_params, "topic": topic},
            )
            conn.execute(
                text(
                    """
                    DELETE FROM infra_outbox_sequences
                    WHERE tenant_id IN (:tenant_id, :other_tenant_id)
                      AND ordering_key = :ordering_key
                    """
                ),
                {**tenant_params, "ordering_key": ordering_key},
            )
        engine.dispose()
    return errors


def verify_phase04_rabbitmq_out_of_order() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_rabbitmq_out_of_order()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 RabbitMQ out-of-order verification failed.")
        return 1
    print("PHASE04 RabbitMQ out-of-order verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
