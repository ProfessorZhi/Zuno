from __future__ import annotations

import asyncio
from copy import deepcopy
from uuid import uuid4

from sqlalchemy import text

from zuno.api.services.message_events import (
    ProductFeedbackOutboxService,
)
from zuno.memory.feedback_consumer import (
    InvalidProductFeedbackDeliveryError,
    ProductFeedbackMemoryConsumer,
)
from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.queue import (
    PostgresOutboxRabbitMQPublisher,
    RabbitMQTopology,
    RabbitMQTransport,
)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


class _CrashBeforeProducerCommit(ProductFeedbackOutboxService):
    @classmethod
    def _after_domain_write(cls) -> None:
        raise RuntimeError("simulated producer crash before commit")


class _CrashBeforeConsumerCommit(ProductFeedbackMemoryConsumer):
    def _after_domain_write(self) -> None:
        raise RuntimeError("simulated consumer crash before commit")


def _count(engine, sql: str, params: dict) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar_one())


def _cleanup(
    engine, *, feedback_id: str | None, event_id: str | None, rollback_marker: str
) -> None:
    with engine.begin() as connection:
        if event_id is not None:
            connection.execute(
                text(
                    "DELETE FROM infra_inbox_messages "
                    "WHERE consumer = 'memory.product-feedback.v1' AND message_id = :event_id"
                ),
                {"event_id": event_id},
            )
            connection.execute(
                text("DELETE FROM infra_outbox_events WHERE event_id = :event_id"),
                {"event_id": event_id},
            )
        if feedback_id is not None:
            connection.execute(
                text("DELETE FROM memory_raw_event WHERE event_id = :event_id"),
                {"event_id": f"memory-feedback:{feedback_id}"},
            )
            connection.execute(
                text("DELETE FROM message_like WHERE id = :feedback_id"),
                {"feedback_id": feedback_id},
            )
        connection.execute(
            text("DELETE FROM message_like WHERE user_input = :rollback_marker"),
            {"rollback_marker": rollback_marker},
        )


async def _verify() -> list[str]:
    errors: list[str] = []
    run_id = uuid4().hex
    tenant_id = f"tenant-domain-event-{run_id}"
    workspace_id = f"workspace-domain-event-{run_id}"
    principal_ref = f"principal-context:{run_id}"
    trace_id = f"trace-domain-event-{run_id}"
    rollback_marker = f"rollback-domain-event-{run_id}"
    engine = create_foundation_engine(DATABASE_URL)
    feedback_id: str | None = None
    event_id: str | None = None
    topology = RabbitMQTopology(
        exchange=f"zuno.phase04.domain.{run_id}",
        queue=f"zuno.phase04.domain.{run_id}.q",
        routing_key="product.feedback.recorded.v1",
        dead_letter_exchange=f"zuno.phase04.domain.{run_id}.dlx",
        dead_letter_queue=f"zuno.phase04.domain.{run_id}.dlq",
        dead_letter_routing_key="product.feedback.recorded.v1.dead",
    )
    transport = RabbitMQTransport(RABBITMQ_URL)
    try:
        try:
            _CrashBeforeProducerCommit.record_like(
                user_input=rollback_marker,
                agent_output="must-roll-back",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                principal_context_ref=principal_ref,
                trace_id=trace_id,
            )
            errors.append("producer crash simulation did not raise")
        except RuntimeError as exc:
            if "simulated producer crash" not in str(exc):
                raise

        rolled_back_domain = _count(
            engine,
            "SELECT count(*) FROM message_like WHERE user_input = :marker",
            {"marker": rollback_marker},
        )
        rolled_back_outbox = _count(
            engine,
            "SELECT count(*) FROM infra_outbox_events WHERE payload::text LIKE :marker",
            {"marker": f"%{trace_id}%"},
        )
        if rolled_back_domain != 0 or rolled_back_outbox != 0:
            errors.append(
                "producer domain write and outbox did not roll back atomically"
            )

        producer_receipt = ProductFeedbackOutboxService.record_like(
            user_input=f"domain-event-{run_id}",
            agent_output="adopted",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_context_ref=principal_ref,
            trace_id=trace_id,
        )
        feedback_id = producer_receipt.feedback_id
        event_id = producer_receipt.event_id
        with engine.connect() as connection:
            producer_row = connection.execute(
                text("""
                    SELECT
                        (SELECT count(*) FROM message_like WHERE id = :feedback_id) AS domain_count,
                        (SELECT count(*) FROM infra_outbox_events
                         WHERE event_id = :event_id AND aggregate_id = :feedback_id
                           AND status = 'pending' AND tenant_id = :tenant_id) AS outbox_count
                    """),
                {
                    "feedback_id": feedback_id,
                    "event_id": event_id,
                    "tenant_id": tenant_id,
                },
            ).one()
        if int(producer_row.domain_count) != 1 or int(producer_row.outbox_count) != 1:
            errors.append(
                "real Product domain write and outbox were not committed together"
            )

        await transport.connect()
        await transport.declare_topology(topology)
        publisher = PostgresOutboxRabbitMQPublisher(
            engine=engine,
            transport=transport,
            topology=topology,
            worker_id=f"publisher-{run_id}",
            tenant_id=tenant_id,
            trace_id=trace_id,
        )
        published = await publisher.publish_event(event_id=event_id)
        if published.event_id != event_id:
            errors.append("publisher did not confirm the domain outbox event")

        first_delivery = await transport.get(topology.queue, timeout=10)
        if first_delivery is None:
            errors.append("RabbitMQ did not deliver the Product domain event")
            return errors
        original_payload = deepcopy(first_delivery.payload)
        original_headers = deepcopy(first_delivery.headers)

        try:
            await _CrashBeforeConsumerCommit().consume_delivery(first_delivery)
            errors.append("consumer crash simulation did not raise")
        except RuntimeError as exc:
            if "simulated consumer crash" not in str(exc):
                raise

        if (
            _count(
                engine,
                "SELECT count(*) FROM infra_inbox_messages WHERE consumer = :consumer AND message_id = :event_id",
                {"consumer": "memory.product-feedback.v1", "event_id": event_id},
            )
            != 0
            or _count(
                engine,
                "SELECT count(*) FROM memory_raw_event WHERE event_id = :event_id",
                {"event_id": f"memory-feedback:{feedback_id}"},
            )
            != 0
        ):
            errors.append(
                "consumer crash did not roll back Inbox and Memory domain write"
            )

        redelivery = await transport.get(topology.queue, timeout=10)
        if redelivery is None:
            errors.append("consumer crash did not cause RabbitMQ redelivery")
            return errors
        if not redelivery.redelivered:
            errors.append("RabbitMQ redelivery flag was not set after consumer crash")
        consumed = await ProductFeedbackMemoryConsumer().consume_delivery(redelivery)
        if (
            not consumed.first_seen
            or consumed.domain_event_id != f"memory-feedback:{feedback_id}"
        ):
            errors.append(
                "Memory consumer did not atomically commit Inbox and domain event"
            )

        await transport.publish(
            topology,
            message_id=event_id,
            payload=original_payload,
            tenant_id=tenant_id,
            trace_id=trace_id,
            ordering_key=str(original_headers["ordering_key"]),
            ordering_sequence=int(original_headers["ordering_sequence"]),
        )
        duplicate_delivery = await transport.get(topology.queue, timeout=10)
        if duplicate_delivery is None:
            errors.append("duplicate Product event was not delivered")
            return errors
        duplicate = await ProductFeedbackMemoryConsumer().consume_delivery(
            duplicate_delivery
        )
        if duplicate.first_seen or duplicate.domain_event_id is not None:
            errors.append("same-hash duplicate repeated the Memory domain effect")

        conflicting_payload = deepcopy(original_payload)
        conflicting_envelope = deepcopy(conflicting_payload["payload"])
        conflicting_command = deepcopy(conflicting_envelope["payload"])
        conflicting_command["command_kind"] = "RECORD_TAMPERED_FEEDBACK_SIGNAL"
        conflicting_envelope["payload"] = conflicting_command
        conflicting_envelope["payload_hash"] = canonical_sha256(conflicting_command)
        conflicting_payload["payload"] = conflicting_envelope
        conflicting_payload["payload_hash"] = canonical_sha256(conflicting_envelope)
        await transport.publish(
            topology,
            message_id=event_id,
            payload=conflicting_payload,
            tenant_id=tenant_id,
            trace_id=trace_id,
            ordering_key=str(original_headers["ordering_key"]),
            ordering_sequence=int(original_headers["ordering_sequence"]),
        )
        conflict_delivery = await transport.get(topology.queue, timeout=10)
        if conflict_delivery is None:
            errors.append("different-hash Product event was not delivered")
            return errors
        conflict = await ProductFeedbackMemoryConsumer().consume_delivery(
            conflict_delivery
        )
        if not conflict.quarantined:
            errors.append("same message id with a different hash was not quarantined")

        with engine.connect() as connection:
            inbox = connection.execute(
                text("""
                    SELECT status, conflict_hash
                    FROM infra_inbox_messages
                    WHERE consumer = :consumer AND message_id = :event_id
                    """),
                {"consumer": "memory.product-feedback.v1", "event_id": event_id},
            ).one()
            memory_count = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM memory_raw_event WHERE event_id = :event_id"
                    ),
                    {"event_id": f"memory-feedback:{feedback_id}"},
                ).scalar_one()
            )
        if inbox.status != "quarantined" or not inbox.conflict_hash:
            errors.append("Inbox quarantine state was not durably persisted")
        if memory_count != 1:
            errors.append("hash conflict changed the Memory domain effect count")

        dead_letter = await transport.get(topology.dead_letter_queue, timeout=10)
        if dead_letter is None:
            errors.append("quarantined delivery did not reach the RabbitMQ DLQ")
        else:
            await dead_letter.ack()

        await transport.publish(
            topology,
            message_id=event_id,
            payload=original_payload,
            tenant_id=tenant_id,
            trace_id=trace_id,
            version="v2",
            ordering_key=str(original_headers["ordering_key"]),
            ordering_sequence=int(original_headers["ordering_sequence"]),
        )
        unsupported_delivery = await transport.get(topology.queue, timeout=10)
        if unsupported_delivery is None:
            errors.append("unsupported-version Product event was not delivered")
            return errors
        try:
            await ProductFeedbackMemoryConsumer().consume_delivery(unsupported_delivery)
            errors.append("unsupported RabbitMQ message version was accepted")
        except InvalidProductFeedbackDeliveryError:
            pass
        unsupported_dead_letter = await transport.get(
            topology.dead_letter_queue,
            timeout=10,
        )
        if unsupported_dead_letter is None:
            errors.append("unsupported message version did not reach the RabbitMQ DLQ")
        else:
            await unsupported_dead_letter.ack()
    finally:
        if transport._connection is not None:
            try:
                await transport.delete_topology(topology)
            except Exception:
                pass
        await transport.close()
        _cleanup(
            engine,
            feedback_id=feedback_id,
            event_id=event_id,
            rollback_marker=rollback_marker,
        )
        engine.dispose()
    return errors


def verify_phase04_domain_event_adoption() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_domain_event_adoption()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 domain event adoption verification failed.")
        return 1
    print("PHASE04 domain event adoption verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
