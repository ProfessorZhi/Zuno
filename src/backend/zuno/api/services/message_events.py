from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from zuno.database.dao.message import MessageLikeDao
from zuno.platform.contracts import (
    CrossModuleEnvelopeV1,
    ProductCommandV1,
    build_wave1_contract_registry,
    canonical_sha256,
)
from zuno.platform.database.session import domain_uow
from zuno.platform.queue.domain import SessionOutbox

TOPIC = "product.feedback.recorded.v1"


@dataclass(frozen=True, slots=True)
class ProductFeedbackOutboxReceipt:
    feedback_id: str
    event_id: str
    envelope_hash: str


class ProductFeedbackOutboxService:
    @classmethod
    def record_like(
        cls,
        *,
        user_input: str,
        agent_output: str,
        tenant_id: str,
        workspace_id: str,
        principal_context_ref: str,
        trace_id: str,
    ) -> ProductFeedbackOutboxReceipt:
        if not all(
            value.strip()
            for value in (
                tenant_id,
                workspace_id,
                principal_context_ref,
                trace_id,
            )
        ):
            raise ValueError(
                "feedback event security and trace context must not be empty"
            )

        now = datetime.now(tz=UTC)
        event_id = f"outbox:{uuid4()}"
        registry = build_wave1_contract_registry()
        command_entry = registry.get("ProductCommandV1", "1.0")
        bundle = registry.manifest()

        with domain_uow(tenant_id=tenant_id) as session:
            feedback = MessageLikeDao.create_message_like(
                user_input=user_input,
                agent_output=agent_output,
            )
            command = ProductCommandV1(
                command_id=feedback.id,
                command_kind="RECORD_LIKE_FEEDBACK_SIGNAL",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                principal_context_ref=principal_context_ref,
                idempotency_key=f"product-feedback:{feedback.id}",
                payload_schema_hash=command_entry.schema_hash,
                payload_hash=canonical_sha256(
                    {
                        "feedback_id": feedback.id,
                        "feedback_kind": "LIKE",
                    }
                ),
                submitted_at=now,
            )
            command_payload = command.model_dump(mode="json")
            envelope = CrossModuleEnvelopeV1(
                contract_name="ProductCommandV1",
                contract_version="1.0",
                contract_bundle_version=bundle.bundle_version,
                message_id=event_id,
                producer_module="Product Surface",
                consumer_module="Memory",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                correlation_id=trace_id,
                idempotency_key=command.idempotency_key,
                aggregate_type="product_feedback",
                aggregate_id=feedback.id,
                principal_context_ref=principal_context_ref,
                trace_id=trace_id,
                data_classification="INTERNAL",
                occurred_at=now,
                created_at=now,
                payload=command_payload,
                payload_hash=canonical_sha256(command_payload),
                payload_schema_hash=command_entry.schema_hash,
            )
            SessionOutbox(session).enqueue_envelope(
                envelope=envelope,
                topic=TOPIC,
                ordering_key=f"product-feedback:{principal_context_ref}",
            )
            cls._after_domain_write()

        return ProductFeedbackOutboxReceipt(
            feedback_id=feedback.id,
            event_id=event_id,
            envelope_hash=canonical_sha256(envelope.model_dump(mode="json")),
        )

    @classmethod
    def _after_domain_write(cls) -> None:
        """Extension point used by fault tests to crash before transaction commit."""


__all__ = [
    "ProductFeedbackOutboxReceipt",
    "ProductFeedbackOutboxService",
    "TOPIC",
]
