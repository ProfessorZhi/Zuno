from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256
from zuno.platform.database.foundation import (
    InboxReceipt,
    InfrastructureRepository,
)


class CanonicalOutboxDeliveryV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    aggregate_id: str
    event_id: str
    idempotency_key: str
    payload: dict[str, Any]
    payload_hash: str
    topic: str

    def verified_envelope(self) -> CrossModuleEnvelopeV1:
        if canonical_sha256(self.payload) != self.payload_hash:
            raise ValueError("outbox delivery payload hash does not match")
        envelope = CrossModuleEnvelopeV1.model_validate(self.payload)
        if envelope.message_id != self.event_id:
            raise ValueError("envelope message_id does not match outbox event_id")
        if envelope.aggregate_id != self.aggregate_id:
            raise ValueError("envelope aggregate_id does not match outbox aggregate_id")
        if envelope.idempotency_key != self.idempotency_key:
            raise ValueError(
                "envelope idempotency_key does not match outbox idempotency_key"
            )
        return envelope


class SessionOutbox:
    def __init__(self, session: Session) -> None:
        self.repository = InfrastructureRepository(session.connection())

    def enqueue_envelope(
        self,
        *,
        envelope: CrossModuleEnvelopeV1,
        topic: str,
        ordering_key: str | None = None,
    ) -> str:
        if envelope.aggregate_id is None or envelope.idempotency_key is None:
            raise ValueError(
                "outbox envelope requires aggregate_id and idempotency_key"
            )
        return self.repository.enqueue_outbox(
            event_id=envelope.message_id,
            aggregate_id=envelope.aggregate_id,
            topic=topic,
            payload=envelope.model_dump(mode="json"),
            idempotency_key=envelope.idempotency_key,
            tenant_id=envelope.tenant_id,
            ordering_key=ordering_key,
        )


class SessionInbox:
    def __init__(self, session: Session) -> None:
        self.repository = InfrastructureRepository(session.connection())

    def record_delivery(
        self,
        *,
        consumer: str,
        message_id: str,
        delivery: CanonicalOutboxDeliveryV1,
        tenant_id: str,
        ordering_key: str | None = None,
        ordering_sequence: int | None = None,
    ) -> InboxReceipt:
        return self.repository.record_inbox_receipt(
            consumer=consumer,
            message_id=message_id,
            payload=delivery.model_dump(mode="json"),
            tenant_id=tenant_id,
            ordering_key=ordering_key,
            ordering_sequence=ordering_sequence,
        )


__all__ = [
    "CanonicalOutboxDeliveryV1",
    "SessionInbox",
    "SessionOutbox",
]
