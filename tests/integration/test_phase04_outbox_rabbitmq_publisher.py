from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
from zuno.platform.queue import (
    PostgresOutboxRabbitMQPublisher,
    RabbitMQTopology,
    RabbitMQTransport,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    infra_outbox_events,
                    infra_inbox_messages,
                    infra_idempotency_claims,
                    infra_worker_leases,
                    infra_object_manifests,
                    infra_checkpoints
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.outbox.exchange.{suffix}",
        queue=f"phase04.outbox.queue.{suffix}",
        routing_key=f"phase04.outbox.route.{suffix}",
        dead_letter_exchange=f"phase04.outbox.dlx.{suffix}",
        dead_letter_queue=f"phase04.outbox.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.outbox.dead.{suffix}",
    )


def test_postgres_outbox_publishes_to_rabbitmq_and_records_inbox(engine) -> None:
    asyncio.run(_verify_outbox_publisher(engine))


def test_outbox_publish_crash_before_complete_is_reclaimed_and_deduped(engine) -> None:
    asyncio.run(_verify_publish_crash_before_complete_recovery(engine))


async def _verify_outbox_publisher(engine) -> None:
    topology = _topology()
    payload = {"kind": "phase04-outbox", "sequence": 1}
    with InfrastructureUnitOfWork(engine) as repo:
        event_id = repo.enqueue_outbox(
            aggregate_id="phase04-run",
            topic="phase04.outbox.publisher",
            payload=payload,
            idempotency_key="phase04-outbox-idem",
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
            published = await publisher.publish_pending(limit=10)
            assert [item.event_id for item in published] == [event_id]

            delivery = await transport.get(topology.queue)
            assert delivery is not None
            assert delivery.message_id == event_id
            assert delivery.payload["event_id"] == event_id
            assert delivery.payload["payload"] == payload
            assert delivery.headers["tenant_id"] == "tenant-phase04"

            with InfrastructureUnitOfWork(engine) as repo:
                repo.record_inbox(
                    consumer="phase04-consumer",
                    message_id=delivery.message_id,
                    payload=delivery.payload,
                )
            await delivery.ack()

            with engine.connect() as conn:
                assert conn.execute(
                    text("SELECT status FROM infra_outbox_events WHERE event_id = :event_id"),
                    {"event_id": event_id},
                ).scalar_one() == "published"
                assert conn.execute(
                    text(
                        """
                        SELECT status
                        FROM infra_inbox_messages
                        WHERE consumer = 'phase04-consumer' AND message_id = :event_id
                        """
                    ),
                    {"event_id": event_id},
                ).scalar_one() == "received"
        finally:
            await transport.delete_topology(topology)


async def _verify_publish_crash_before_complete_recovery(engine) -> None:
    topology = _topology()
    payload = {"kind": "phase04-outbox-crash", "sequence": 2}
    with InfrastructureUnitOfWork(engine) as repo:
        event_id = repo.enqueue_outbox(
            aggregate_id="phase04-run-crash",
            topic="phase04.outbox.publisher",
            payload=payload,
            idempotency_key="phase04-outbox-crash-idem",
        )
        claimed = repo.claim_outbox(worker_id="crashed-publisher", limit=1)
        assert claimed == [event_id]
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
            assert first_delivery is not None
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
                assert repo.reclaim_stale_outbox_claims(older_than_seconds=1) == [event_id]

            publisher = PostgresOutboxRabbitMQPublisher(
                engine=engine,
                transport=transport,
                topology=topology,
                worker_id="recovery-publisher",
                tenant_id="tenant-phase04",
                trace_id="trace-phase04-recovery",
            )
            assert [item.event_id for item in await publisher.publish_pending(limit=1)] == [event_id]

            duplicate_delivery = await transport.get(topology.queue)
            assert duplicate_delivery is not None
            with InfrastructureUnitOfWork(engine) as repo:
                assert (
                    repo.record_inbox(
                        consumer="phase04-crash-consumer",
                        message_id=duplicate_delivery.message_id,
                        payload=duplicate_delivery.payload,
                    )
                    == first_hash
                )
            await duplicate_delivery.ack()

            with engine.connect() as conn:
                assert conn.execute(
                    text("SELECT status FROM infra_outbox_events WHERE event_id = :event_id"),
                    {"event_id": event_id},
                ).scalar_one() == "published"
                assert conn.execute(
                    text(
                        """
                        SELECT count(*)
                        FROM infra_inbox_messages
                        WHERE consumer = 'phase04-crash-consumer' AND message_id = :event_id
                        """
                    ),
                    {"event_id": event_id},
                ).scalar_one() == 1
        finally:
            await transport.delete_topology(topology)
