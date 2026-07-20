from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Engine

from zuno.platform.database.foundation import InfrastructureUnitOfWork, OutboxEventRecord
from zuno.platform.queue.rabbitmq import RabbitMQTopology, RabbitMQTransport


@dataclass(frozen=True, slots=True)
class PublishedOutboxEvent:
    event_id: str
    topic: str
    payload_hash: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class OutboxPublishPolicy:
    max_attempts: int = 5
    base_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 300.0
    publish_timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if not math.isfinite(self.base_backoff_seconds) or not math.isfinite(self.max_backoff_seconds):
            raise ValueError("outbox backoff seconds must be finite")
        if self.base_backoff_seconds < 0:
            raise ValueError("base_backoff_seconds must not be negative")
        if self.max_backoff_seconds < self.base_backoff_seconds:
            raise ValueError("max_backoff_seconds must be greater than or equal to base_backoff_seconds")
        if not math.isfinite(self.publish_timeout_seconds) or self.publish_timeout_seconds <= 0:
            raise ValueError("publish_timeout_seconds must be finite and positive")


@dataclass(frozen=True, slots=True)
class FailedOutboxEvent:
    event_id: str
    status: str
    publish_attempts: int
    retry_count: int
    next_attempt_at: datetime
    error_code: str


@dataclass(frozen=True, slots=True)
class OutboxPublishBatch:
    published: tuple[PublishedOutboxEvent, ...]
    failed: tuple[FailedOutboxEvent, ...]


class PostgresOutboxRabbitMQPublisher:
    def __init__(
        self,
        *,
        engine: Engine,
        transport: RabbitMQTransport,
        topology: RabbitMQTopology,
        worker_id: str,
        tenant_id: str | None,
        trace_id: str,
        topics: tuple[str, ...] | None = None,
        policy: OutboxPublishPolicy | None = None,
    ) -> None:
        self.engine = engine
        self.transport = transport
        self.topology = topology
        self.worker_id = worker_id
        self.tenant_id = tenant_id
        self.trace_id = trace_id
        self.topics = topics
        self.policy = policy or OutboxPublishPolicy()

    async def publish_pending(self, *, limit: int = 10) -> list[PublishedOutboxEvent]:
        batch = await self.publish_batch(limit=limit)
        return list(batch.published)

    async def publish_batch(self, *, limit: int = 10) -> OutboxPublishBatch:
        published: list[PublishedOutboxEvent] = []
        failed: list[FailedOutboxEvent] = []
        with InfrastructureUnitOfWork(self.engine) as repo:
            event_ids = repo.claim_outbox(
                worker_id=self.worker_id,
                limit=limit,
                topics=self.topics,
            )
            records = [
                repo.load_claimed_outbox_event(event_id=event_id, worker_id=self.worker_id)
                for event_id in event_ids
            ]

        for record in records:
            try:
                await self._publish_record(record)
            except Exception as exc:
                with InfrastructureUnitOfWork(self.engine) as repo:
                    receipt = repo.record_outbox_publish_failure(
                        event_id=record.event_id,
                        worker_id=self.worker_id,
                        error_code=type(exc).__name__,
                        max_attempts=self.policy.max_attempts,
                        base_backoff_seconds=self.policy.base_backoff_seconds,
                        max_backoff_seconds=self.policy.max_backoff_seconds,
                    )
                failed.append(
                    FailedOutboxEvent(
                        event_id=receipt.event_id,
                        status=receipt.status,
                        publish_attempts=receipt.publish_attempts,
                        retry_count=receipt.retry_count,
                        next_attempt_at=receipt.next_attempt_at,
                        error_code=receipt.error_code,
                    )
                )
                continue
            with InfrastructureUnitOfWork(self.engine) as repo:
                repo.complete_outbox(event_id=record.event_id, worker_id=self.worker_id)
            published.append(self._published_event(record))
        return OutboxPublishBatch(published=tuple(published), failed=tuple(failed))

    async def publish_event(self, *, event_id: str) -> PublishedOutboxEvent:
        with InfrastructureUnitOfWork(self.engine) as repo:
            if not repo.claim_outbox_event(event_id=event_id, worker_id=self.worker_id):
                raise RuntimeError("outbox event is not pending")
            record = repo.load_claimed_outbox_event(event_id=event_id, worker_id=self.worker_id)
        try:
            await self._publish_record(record)
        except Exception as exc:
            with InfrastructureUnitOfWork(self.engine) as repo:
                repo.record_outbox_publish_failure(
                    event_id=record.event_id,
                    worker_id=self.worker_id,
                    error_code=type(exc).__name__,
                    max_attempts=self.policy.max_attempts,
                    base_backoff_seconds=self.policy.base_backoff_seconds,
                    max_backoff_seconds=self.policy.max_backoff_seconds,
                )
            raise
        with InfrastructureUnitOfWork(self.engine) as repo:
            repo.complete_outbox(event_id=record.event_id, worker_id=self.worker_id)
        return self._published_event(record)

    @staticmethod
    def _published_event(record: OutboxEventRecord) -> PublishedOutboxEvent:
        return PublishedOutboxEvent(
            event_id=record.event_id,
            topic=record.topic,
            payload_hash=record.payload_hash,
            idempotency_key=record.idempotency_key,
        )

    async def _publish_record(self, record: OutboxEventRecord) -> None:
        if self.tenant_id is not None and record.tenant_id and record.tenant_id != self.tenant_id:
            raise RuntimeError("outbox publisher tenant does not match the claimed event tenant")
        tenant_id = record.tenant_id or self.tenant_id
        if tenant_id is None:
            raise RuntimeError("outbox publisher requires tenant_id when the outbox record is tenantless")
        security_epoch_ref = self._security_epoch_ref(record.payload)
        workspace_id = self._workspace_id(record.payload)
        trace_id = self._trace_id(record.payload) or self.trace_id
        await asyncio.wait_for(
            self.transport.publish(
                self.topology,
                message_id=record.event_id,
                payload={
                    "aggregate_id": record.aggregate_id,
                    "event_id": record.event_id,
                    "idempotency_key": record.idempotency_key,
                    "payload": record.payload,
                    "payload_hash": record.payload_hash,
                    "topic": record.topic,
                },
                tenant_id=tenant_id,
                trace_id=trace_id,
                workspace_id=workspace_id,
                security_epoch_ref=security_epoch_ref,
                ordering_key=record.ordering_key,
                ordering_sequence=record.ordering_sequence,
                outbox_publish_attempt=record.publish_attempts + 1,
                outbox_retry_count=record.retry_count,
                outbox_replay_count=record.replay_count,
            ),
            timeout=self.policy.publish_timeout_seconds,
        )

    @staticmethod
    def _security_epoch_ref(payload: dict) -> str | None:
        envelope_epoch = payload.get("effective_security_epoch_ref")
        if envelope_epoch is not None:
            return str(envelope_epoch)
        inner_payload = payload.get("payload")
        if isinstance(inner_payload, dict) and inner_payload.get("security_epoch_ref") is not None:
            return str(inner_payload["security_epoch_ref"])
        return None

    @staticmethod
    def _workspace_id(payload: dict) -> str | None:
        envelope_workspace_id = payload.get("workspace_id")
        if envelope_workspace_id is not None:
            return str(envelope_workspace_id)
        inner_payload = payload.get("payload")
        if isinstance(inner_payload, dict) and inner_payload.get("workspace_id") is not None:
            return str(inner_payload["workspace_id"])
        return None

    @staticmethod
    def _trace_id(payload: dict) -> str | None:
        envelope_trace_id = payload.get("trace_id")
        if envelope_trace_id is not None:
            return str(envelope_trace_id)
        inner_payload = payload.get("payload")
        if isinstance(inner_payload, dict) and inner_payload.get("trace_id") is not None:
            return str(inner_payload["trace_id"])
        return None


__all__ = [
    "FailedOutboxEvent",
    "OutboxPublishBatch",
    "OutboxPublishPolicy",
    "PostgresOutboxRabbitMQPublisher",
    "PublishedOutboxEvent",
]
