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


def verify_phase04_outbox_rabbitmq_publisher() -> list[str]:
    return asyncio.run(_verify())


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
