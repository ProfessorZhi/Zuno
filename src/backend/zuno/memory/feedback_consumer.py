from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from zuno.database.models.memory_runtime import MemoryRawEventTable
from zuno.platform.contracts import ProductCommandV1, build_wave1_contract_registry
from zuno.platform.database.foundation import InfrastructureConflictError
from zuno.platform.database.session import domain_uow
from zuno.platform.queue.domain import CanonicalOutboxDeliveryV1, SessionInbox
from zuno.platform.queue.rabbitmq import RabbitMQDelivery

CONSUMER = "memory.product-feedback.v1"
TOPIC = "product.feedback.recorded.v1"


class InvalidProductFeedbackDeliveryError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ProductFeedbackConsumeReceipt:
    message_id: str
    inbox_status: str
    domain_event_id: str | None
    first_seen: bool
    quarantined: bool


class ProductFeedbackMemoryConsumer:
    async def consume_delivery(
        self,
        delivery: RabbitMQDelivery,
    ) -> ProductFeedbackConsumeReceipt:
        try:
            receipt = self.consume(
                message_id=delivery.message_id,
                payload=delivery.payload,
                headers=delivery.headers,
            )
        except InvalidProductFeedbackDeliveryError:
            await delivery.reject(requeue=False)
            raise
        except Exception:
            await delivery.nack(requeue=True)
            raise

        if receipt.quarantined:
            await delivery.reject(requeue=False)
        else:
            await delivery.ack()
        return receipt

    def consume(
        self,
        *,
        message_id: str,
        payload: dict,
        headers: dict,
    ) -> ProductFeedbackConsumeReceipt:
        try:
            delivery = CanonicalOutboxDeliveryV1.model_validate(payload)
            envelope = delivery.verified_envelope()
            command = ProductCommandV1.model_validate(envelope.payload)
            self._validate_boundaries(
                message_id=message_id,
                delivery=delivery,
                envelope=envelope,
                command=command,
                headers=headers,
            )
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            raise InvalidProductFeedbackDeliveryError(str(exc)) from exc

        conflict: InfrastructureConflictError | None = None
        inbox_receipt = None
        domain_event_id: str | None = None
        with domain_uow(tenant_id=envelope.tenant_id) as session:
            try:
                inbox_receipt = SessionInbox(session).record_delivery(
                    consumer=CONSUMER,
                    message_id=message_id,
                    delivery=delivery,
                    tenant_id=envelope.tenant_id,
                    ordering_key=self._header(headers, "ordering_key"),
                    ordering_sequence=self._ordering_sequence(headers),
                )
            except InfrastructureConflictError as exc:
                conflict = exc

            if (
                conflict is None
                and inbox_receipt is not None
                and inbox_receipt.processable
            ):
                domain_event_id = f"memory-feedback:{command.command_id}"
                session.add(
                    MemoryRawEventTable(
                        event_id=domain_event_id,
                        user_id=command.principal_context_ref,
                        project_id=command.workspace_id,
                        trace_id=envelope.trace_id,
                        task_id=command.command_id,
                        event_type=command.command_kind,
                        layer="interaction",
                        payload=command.model_dump(mode="json"),
                        memory_metadata={
                            "source_message_id": message_id,
                            "source_topic": delivery.topic,
                            "tenant_id": envelope.tenant_id,
                        },
                    )
                )
                session.flush()
                self._after_domain_write()

        if conflict is not None:
            return ProductFeedbackConsumeReceipt(
                message_id=message_id,
                inbox_status="quarantined",
                domain_event_id=None,
                first_seen=False,
                quarantined=True,
            )
        if inbox_receipt is None:
            raise RuntimeError("inbox receipt was not created")
        return ProductFeedbackConsumeReceipt(
            message_id=message_id,
            inbox_status=inbox_receipt.status,
            domain_event_id=domain_event_id,
            first_seen=inbox_receipt.first_seen,
            quarantined=False,
        )

    def _after_domain_write(self) -> None:
        """Extension point used by fault tests to crash before transaction commit."""

    @staticmethod
    def _header(headers: dict, name: str) -> str | None:
        value = headers.get(name)
        return None if value is None else str(value)

    @staticmethod
    def _ordering_sequence(headers: dict) -> int | None:
        value = headers.get("ordering_sequence")
        return None if value is None else int(value)

    @staticmethod
    def _validate_boundaries(
        *,
        message_id: str,
        delivery: CanonicalOutboxDeliveryV1,
        envelope,
        command: ProductCommandV1,
        headers: dict,
    ) -> None:
        registry_entry = build_wave1_contract_registry().get("ProductCommandV1", "1.0")
        expected = {
            "message_id": delivery.event_id,
            "topic": TOPIC,
            "contract_name": "ProductCommandV1",
            "producer_module": "Product Surface",
            "consumer_module": "Memory",
            "tenant_id": envelope.tenant_id,
            "trace_id": envelope.trace_id,
            "message_version": "v1",
            "payload_schema_hash": registry_entry.schema_hash,
        }
        actual = {
            "message_id": message_id,
            "topic": delivery.topic,
            "contract_name": envelope.contract_name,
            "producer_module": envelope.producer_module,
            "consumer_module": envelope.consumer_module,
            "tenant_id": str(headers.get("tenant_id") or ""),
            "trace_id": str(headers.get("trace_id") or ""),
            "message_version": str(headers.get("message_version") or ""),
            "payload_schema_hash": envelope.payload_schema_hash,
        }
        if actual != expected:
            raise ValueError("product feedback delivery boundary mismatch")
        if command.tenant_id != envelope.tenant_id:
            raise ValueError("product command crossed the tenant boundary")
        if command.workspace_id != envelope.workspace_id:
            raise ValueError("product command crossed the workspace boundary")
        if command.command_id != envelope.aggregate_id:
            raise ValueError("product command does not own the envelope aggregate")
        if command.idempotency_key != envelope.idempotency_key:
            raise ValueError("product command idempotency key does not match envelope")


__all__ = [
    "CONSUMER",
    "InvalidProductFeedbackDeliveryError",
    "ProductFeedbackConsumeReceipt",
    "ProductFeedbackMemoryConsumer",
    "TOPIC",
]
