from __future__ import annotations

import math
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DBAPIError

from zuno.platform.contracts import canonical_json, canonical_sha256


class InfrastructureConflictError(RuntimeError):
    pass


class CapacityBackpressureError(RuntimeError):
    pass


class AuditCapacityError(RuntimeError):
    pass


class FencingRejectedError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FencingToken:
    resource_id: str
    owner_id: str
    epoch: int
    lease_id: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class OutboxEventRecord:
    event_id: str
    aggregate_id: str
    topic: str
    payload: dict[str, Any]
    payload_hash: str
    idempotency_key: str
    claim_owner: str
    tenant_id: str
    ordering_key: str | None
    ordering_sequence: int | None
    publish_attempts: int
    retry_count: int
    replay_count: int


@dataclass(frozen=True, slots=True)
class ObjectManifestRecord:
    object_ref: str
    owner: str
    content_hash: str
    size_bytes: int
    visibility: str
    conflict_hash: str | None


@dataclass(frozen=True, slots=True)
class OutboxFailureReceipt:
    event_id: str
    status: str
    publish_attempts: int
    retry_count: int
    next_attempt_at: datetime
    error_code: str


@dataclass(frozen=True, slots=True)
class OutboxReplayReceipt:
    event_id: str
    status: str
    replay_count: int
    replay_owner: str


@dataclass(frozen=True, slots=True)
class OutboxBacklogReceipt:
    ready: int
    delayed: int
    claimed: int
    dead_letter: int
    oldest_pending_at: datetime | None


@dataclass(frozen=True, slots=True)
class IdempotencyClaimReceipt:
    status: str
    generation: int
    result_ref: str
    owner: str
    acquired: bool


@dataclass(frozen=True, slots=True)
class InboxReceipt:
    consumer: str
    message_id: str
    payload_hash: str
    status: str
    first_seen: bool
    processable: bool = True
    ordering_key: str | None = None
    ordering_sequence: int | None = None
    contiguous_sequence: int | None = None
    released_message_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class InboxMessageRecord:
    tenant_id: str
    consumer: str
    message_id: str
    payload: dict[str, Any]
    payload_hash: str
    status: str
    ordering_key: str | None
    ordering_sequence: int | None


@dataclass(frozen=True, slots=True)
class DeliveryWatermarkReceipt:
    tenant_id: str
    consumer: str
    ordering_key: str
    contiguous_sequence: int
    max_seen_sequence: int


@dataclass(frozen=True, slots=True)
class CapacityReservationReceipt:
    reservation_id: str
    resource_id: str
    owner_id: str
    amount: int
    generation: int
    remaining_capacity: int
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class AuditPersistenceReceipt:
    audit_id: str
    channel_id: str
    effect_id: str
    owner_id: str
    payload_hash: str
    generation: int
    remaining_capacity: int
    durable_at: datetime


@dataclass(frozen=True, slots=True)
class CutoverActivationReceipt:
    target_id: str
    snapshot_id: str
    previous_generation: int
    active_generation: int
    activated_at: datetime


@dataclass(frozen=True, slots=True)
class ActiveSnapshotRefReceipt:
    ref_id: str
    target_id: str
    snapshot_id: str
    generation: int
    owner_id: str


@dataclass(frozen=True, slots=True)
class RecoveryWatermarkReceipt:
    component_id: str
    service_kind: str
    authority: str
    watermark: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class RecoverySetReceipt:
    recovery_set_id: str
    recovery_point: str
    component_ids: tuple[str, ...]
    verification_hash: str


@dataclass(frozen=True, slots=True)
class SecretVersionReceipt:
    secret_ref: str
    tenant_id: str
    version: int
    status: str
    generation: int


@dataclass(frozen=True, slots=True)
class SecretLeaseReceipt:
    lease_id: str
    secret_ref: str
    tenant_id: str
    version: int
    generation: int
    payload_hash: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class CrossTenantHitReceipt:
    hit_id: str
    service_kind: str
    resource_ref: str
    expected_tenant_id: str
    observed_tenant_id: str
    action: str
    status: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class TransactionRetryReceipt:
    result: Any
    attempts: int
    retried_sqlstates: tuple[str, ...]


def create_foundation_engine(database_url: str, **kwargs: Any) -> Engine:
    return create_engine(database_url, pool_pre_ping=True, future=True, **kwargs)


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


class InfrastructureUnitOfWork:
    def __init__(
        self,
        engine: Engine,
        *,
        tenant_id: str | None = None,
        statement_timeout_ms: int | None = None,
        lock_timeout_ms: int | None = None,
        isolation_level: str | None = None,
    ) -> None:
        self.engine = engine
        self.tenant_id = tenant_id
        self.statement_timeout_ms = statement_timeout_ms
        self.lock_timeout_ms = lock_timeout_ms
        self.isolation_level = isolation_level
        self._active = False

    def __enter__(self) -> InfrastructureRepository:
        if self._active:
            raise RuntimeError("InfrastructureUnitOfWork cannot be nested or entered concurrently")
        self._active = True
        self._context = None
        self._transaction = None
        try:
            if self.isolation_level is None:
                self._context = self.engine.begin()
                self.connection = self._context.__enter__()
            else:
                self._context = self.engine.connect()
                self.connection = self._context.__enter__().execution_options(isolation_level=self.isolation_level)
                self._transaction = self.connection.begin()
            if self.tenant_id is not None:
                self.connection.execute(
                    text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                    {"tenant_id": self.tenant_id},
                )
            if self.statement_timeout_ms is not None:
                self.connection.execute(
                    text("SELECT set_config('statement_timeout', :timeout_ms, true)"),
                    {"timeout_ms": str(self.statement_timeout_ms)},
                )
            if self.lock_timeout_ms is not None:
                self.connection.execute(
                    text("SELECT set_config('lock_timeout', :timeout_ms, true)"),
                    {"timeout_ms": str(self.lock_timeout_ms)},
                )
            return InfrastructureRepository(self.connection)
        except BaseException:
            exc_info = sys.exc_info()
            try:
                if self._transaction is not None:
                    try:
                        self._transaction.__exit__(*exc_info)
                    finally:
                        self._context.__exit__(*exc_info)
                elif self._context is not None:
                    self._context.__exit__(*exc_info)
            finally:
                self._active = False
            raise

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if self._transaction is not None:
                try:
                    self._transaction.__exit__(exc_type, exc, tb)
                finally:
                    self._context.__exit__(exc_type, exc, tb)
                return
            self._context.__exit__(exc_type, exc, tb)
        finally:
            self._active = False


def run_transaction_with_retry(
    engine: Engine,
    operation: Callable[[InfrastructureRepository], Any],
    *,
    max_attempts: int = 3,
    retry_sqlstates: tuple[str, ...] = ("40P01", "40001"),
    backoff_seconds: float = 0.05,
    tenant_id: str | None = None,
    statement_timeout_ms: int | None = None,
    lock_timeout_ms: int | None = None,
    isolation_level: str | None = None,
) -> TransactionRetryReceipt:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    retried_sqlstates: list[str] = []
    for attempt in range(1, max_attempts + 1):
        try:
            with InfrastructureUnitOfWork(
                engine,
                tenant_id=tenant_id,
                statement_timeout_ms=statement_timeout_ms,
                lock_timeout_ms=lock_timeout_ms,
                isolation_level=isolation_level,
            ) as repo:
                result = operation(repo)
            return TransactionRetryReceipt(result=result, attempts=attempt, retried_sqlstates=tuple(retried_sqlstates))
        except DBAPIError as exc:
            sqlstate = _sqlstate(exc)
            if sqlstate not in retry_sqlstates or attempt >= max_attempts:
                raise
            retried_sqlstates.append(sqlstate)
            time.sleep(backoff_seconds * attempt)
    raise RuntimeError("transaction retry loop exited unexpectedly")


class InfrastructureRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def check_readiness(self) -> bool:
        return self.connection.execute(text("SELECT 1")).scalar_one() == 1

    def current_tenant_id(self) -> str:
        return str(self.connection.execute(text("SELECT current_setting('app.tenant_id', true)")).scalar_one() or "")

    def enqueue_outbox(
        self,
        *,
        aggregate_id: str,
        topic: str,
        payload: dict[str, Any],
        idempotency_key: str,
        event_id: str | None = None,
        tenant_id: str | None = None,
        ordering_key: str | None = None,
    ) -> str:
        event_id = event_id or f"outbox:{uuid4()}"
        if not event_id.strip():
            raise ValueError("event_id must not be empty")
        payload_hash = canonical_sha256(payload)
        resolved_tenant_id = self.current_tenant_id() if tenant_id is None else tenant_id
        ordering_sequence: int | None = None
        if ordering_key is not None:
            if not ordering_key:
                raise ValueError("ordering_key must not be empty")
            if not resolved_tenant_id:
                raise ValueError("tenant_id is required for ordered outbox events")
            ordering_sequence = int(
                self.connection.execute(
                    text(
                        """
                        INSERT INTO infra_outbox_sequences(
                            tenant_id, ordering_key, last_sequence
                        ) VALUES (
                            :tenant_id, :ordering_key, 1
                        )
                        ON CONFLICT (tenant_id, ordering_key) DO UPDATE
                        SET last_sequence = infra_outbox_sequences.last_sequence + 1,
                            updated_at = now()
                        RETURNING last_sequence
                        """
                    ),
                    {"tenant_id": resolved_tenant_id, "ordering_key": ordering_key},
                ).scalar_one()
            )
        self.connection.execute(
            text(
                """
                INSERT INTO infra_outbox_events(
                    event_id, aggregate_id, topic, payload, payload_hash, idempotency_key,
                    status, tenant_id, ordering_key, ordering_sequence
                ) VALUES (
                    :event_id, :aggregate_id, :topic, CAST(:payload AS jsonb), :payload_hash,
                    :idempotency_key, 'pending', :tenant_id, :ordering_key, :ordering_sequence
                )
                """
            ),
            {
                "event_id": event_id,
                "aggregate_id": aggregate_id,
                "topic": topic,
                "payload": _json(payload),
                "payload_hash": payload_hash,
                "idempotency_key": idempotency_key,
                "tenant_id": resolved_tenant_id,
                "ordering_key": ordering_key,
                "ordering_sequence": ordering_sequence,
            },
        )
        return event_id

    def claim_outbox(self, *, worker_id: str, limit: int = 10) -> list[str]:
        rows = self.connection.execute(
            text(
                """
                WITH selected AS (
                    SELECT event_id
                    FROM infra_outbox_events
                    WHERE status = 'pending'
                      AND next_attempt_at <= now()
                    ORDER BY created_at, event_id
                    FOR UPDATE SKIP LOCKED
                    LIMIT :limit
                )
                UPDATE infra_outbox_events AS event
                SET status = 'claimed', claim_owner = :worker_id, claimed_at = now()
                FROM selected
                WHERE event.event_id = selected.event_id
                RETURNING event.event_id
                """
            ),
            {"worker_id": worker_id, "limit": limit},
        ).all()
        return [str(row.event_id) for row in rows]

    def claim_outbox_event(self, *, event_id: str, worker_id: str) -> bool:
        row = self.connection.execute(
            text(
                """
                UPDATE infra_outbox_events
                SET status = 'claimed', claim_owner = :worker_id, claimed_at = now()
                WHERE event_id = :event_id
                  AND status = 'pending'
                  AND next_attempt_at <= now()
                RETURNING event_id
                """
            ),
            {"event_id": event_id, "worker_id": worker_id},
        ).first()
        return row is not None

    def reclaim_stale_outbox_claims(self, *, older_than_seconds: int) -> list[str]:
        rows = self.connection.execute(
            text(
                """
                UPDATE infra_outbox_events
                SET status = 'pending', claim_owner = NULL, claimed_at = NULL,
                    next_attempt_at = now()
                WHERE status = 'claimed'
                  AND claimed_at < now() - (:older_than_seconds * interval '1 second')
                RETURNING event_id
                """
            ),
            {"older_than_seconds": older_than_seconds},
        ).all()
        return [str(row.event_id) for row in rows]

    def reclaim_stale_outbox_event(self, *, event_id: str, older_than_seconds: int) -> bool:
        row = self.connection.execute(
            text(
                """
                UPDATE infra_outbox_events
                SET status = 'pending', claim_owner = NULL, claimed_at = NULL,
                    next_attempt_at = now()
                WHERE event_id = :event_id
                  AND status = 'claimed'
                  AND claimed_at < now() - (:older_than_seconds * interval '1 second')
                RETURNING event_id
                """
            ),
            {"event_id": event_id, "older_than_seconds": older_than_seconds},
        ).first()
        return row is not None

    def complete_outbox(self, *, event_id: str, worker_id: str) -> None:
        result = self.connection.execute(
            text(
                """
                UPDATE infra_outbox_events
                SET status = 'published',
                    publish_attempts = publish_attempts + 1,
                    published_at = now(),
                    claim_owner = NULL,
                    claimed_at = NULL
                WHERE event_id = :event_id AND claim_owner = :worker_id AND status = 'claimed'
                """
            ),
            {"event_id": event_id, "worker_id": worker_id},
        )
        if result.rowcount != 1:
            raise FencingRejectedError("outbox event is not claimed by this worker")

    def load_claimed_outbox_event(self, *, event_id: str, worker_id: str) -> OutboxEventRecord:
        row = self.connection.execute(
            text(
                """
                SELECT event_id, aggregate_id, topic, payload, payload_hash, idempotency_key,
                       claim_owner, tenant_id, ordering_key, ordering_sequence,
                       publish_attempts, retry_count, replay_count
                FROM infra_outbox_events
                WHERE event_id = :event_id AND claim_owner = :worker_id AND status = 'claimed'
                """
            ),
            {"event_id": event_id, "worker_id": worker_id},
        ).first()
        if row is None:
            raise FencingRejectedError("outbox event is not claimed by this worker")
        payload = dict(row.payload)
        if canonical_sha256(payload) != row.payload_hash:
            raise InfrastructureConflictError("outbox payload hash mismatch")
        return OutboxEventRecord(
            event_id=str(row.event_id),
            aggregate_id=str(row.aggregate_id),
            topic=str(row.topic),
            payload=payload,
            payload_hash=str(row.payload_hash),
            idempotency_key=str(row.idempotency_key),
            claim_owner=str(row.claim_owner),
            tenant_id=str(row.tenant_id),
            ordering_key=None if row.ordering_key is None else str(row.ordering_key),
            ordering_sequence=None if row.ordering_sequence is None else int(row.ordering_sequence),
            publish_attempts=int(row.publish_attempts),
            retry_count=int(row.retry_count),
            replay_count=int(row.replay_count),
        )

    def record_outbox_publish_failure(
        self,
        *,
        event_id: str,
        worker_id: str,
        error_code: str,
        max_attempts: int,
        base_backoff_seconds: float,
        max_backoff_seconds: float,
    ) -> OutboxFailureReceipt:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if not math.isfinite(base_backoff_seconds) or not math.isfinite(max_backoff_seconds):
            raise ValueError("outbox backoff seconds must be finite")
        if base_backoff_seconds < 0 or max_backoff_seconds < 0:
            raise ValueError("outbox backoff seconds must not be negative")
        if max_backoff_seconds < base_backoff_seconds:
            raise ValueError("max_backoff_seconds must be greater than or equal to base_backoff_seconds")
        normalized_error_code = error_code.strip()
        if not normalized_error_code or len(normalized_error_code) > 128:
            raise ValueError("error_code must contain between 1 and 128 characters")

        row = self.connection.execute(
            text(
                """
                SELECT retry_count
                FROM infra_outbox_events
                WHERE event_id = :event_id
                  AND claim_owner = :worker_id
                  AND status = 'claimed'
                FOR UPDATE
                """
            ),
            {"event_id": event_id, "worker_id": worker_id},
        ).first()
        if row is None:
            raise FencingRejectedError("outbox event is not claimed by this worker")

        next_retry_count = int(row.retry_count) + 1
        exhausted = next_retry_count >= max_attempts
        delay_seconds = 0.0
        if base_backoff_seconds:
            exponent = min(max(0, next_retry_count - 1), 62)
            delay_seconds = min(max_backoff_seconds, base_backoff_seconds * (2**exponent))
        next_attempt_at = utcnow() + timedelta(seconds=0 if exhausted else delay_seconds)
        receipt = self.connection.execute(
            text(
                """
                UPDATE infra_outbox_events
                SET status = CASE WHEN :exhausted THEN 'dead_letter' ELSE 'pending' END,
                    publish_attempts = publish_attempts + 1,
                    retry_count = retry_count + 1,
                    next_attempt_at = :next_attempt_at,
                    last_error_code = :error_code,
                    last_failed_at = now(),
                    dead_lettered_at = CASE WHEN :exhausted THEN now() ELSE NULL END,
                    claim_owner = NULL,
                    claimed_at = NULL
                WHERE event_id = :event_id
                  AND claim_owner = :worker_id
                  AND status = 'claimed'
                RETURNING event_id, status, publish_attempts, retry_count,
                          next_attempt_at, last_error_code
                """
            ),
            {
                "event_id": event_id,
                "worker_id": worker_id,
                "exhausted": exhausted,
                "next_attempt_at": next_attempt_at,
                "error_code": normalized_error_code,
            },
        ).one()
        return OutboxFailureReceipt(
            event_id=str(receipt.event_id),
            status=str(receipt.status),
            publish_attempts=int(receipt.publish_attempts),
            retry_count=int(receipt.retry_count),
            next_attempt_at=receipt.next_attempt_at,
            error_code=str(receipt.last_error_code),
        )

    def replay_dead_letter_outbox(self, *, event_id: str, replay_owner: str) -> OutboxReplayReceipt:
        normalized_owner = replay_owner.strip()
        if not normalized_owner or len(normalized_owner) > 128:
            raise ValueError("replay_owner must contain between 1 and 128 characters")
        row = self.connection.execute(
            text(
                """
                UPDATE infra_outbox_events
                SET status = 'pending',
                    retry_count = 0,
                    next_attempt_at = now(),
                    replay_count = replay_count + 1,
                    last_replay_owner = :replay_owner,
                    replayed_at = now(),
                    dead_lettered_at = NULL,
                    claim_owner = NULL,
                    claimed_at = NULL
                WHERE event_id = :event_id
                  AND status = 'dead_letter'
                RETURNING event_id, status, replay_count, last_replay_owner
                """
            ),
            {"event_id": event_id, "replay_owner": normalized_owner},
        ).first()
        if row is None:
            raise InfrastructureConflictError("outbox event is not dead-lettered")
        return OutboxReplayReceipt(
            event_id=str(row.event_id),
            status=str(row.status),
            replay_count=int(row.replay_count),
            replay_owner=str(row.last_replay_owner),
        )

    def outbox_backlog(self, *, topic: str | None = None) -> OutboxBacklogReceipt:
        row = self.connection.execute(
            text(
                """
                SELECT
                    count(*) FILTER (WHERE status = 'pending' AND next_attempt_at <= now()) AS ready,
                    count(*) FILTER (WHERE status = 'pending' AND next_attempt_at > now()) AS delayed,
                    count(*) FILTER (WHERE status = 'claimed') AS claimed,
                    count(*) FILTER (WHERE status = 'dead_letter') AS dead_letter,
                    min(created_at) FILTER (WHERE status IN ('pending', 'claimed')) AS oldest_pending_at
                FROM infra_outbox_events
                WHERE (
                    CAST(:topic AS varchar) IS NULL
                    OR topic = CAST(:topic AS varchar)
                )
                """
            ),
            {"topic": topic},
        ).one()
        return OutboxBacklogReceipt(
            ready=int(row.ready),
            delayed=int(row.delayed),
            claimed=int(row.claimed),
            dead_letter=int(row.dead_letter),
            oldest_pending_at=row.oldest_pending_at,
        )

    def record_inbox(self, *, consumer: str, message_id: str, payload: dict[str, Any]) -> str:
        return self.record_inbox_receipt(
            consumer=consumer,
            message_id=message_id,
            payload=payload,
        ).payload_hash

    def record_inbox_receipt(
        self,
        *,
        consumer: str,
        message_id: str,
        payload: dict[str, Any],
        tenant_id: str | None = None,
        ordering_key: str | None = None,
        ordering_sequence: int | None = None,
    ) -> InboxReceipt:
        if (ordering_key is None) != (ordering_sequence is None):
            raise ValueError("ordering_key and ordering_sequence must be provided together")
        if ordering_sequence is not None and ordering_sequence < 1:
            raise ValueError("ordering_sequence must be positive")
        resolved_tenant_id = self.current_tenant_id() if tenant_id is None else tenant_id
        if ordering_key is not None and not resolved_tenant_id:
            raise ValueError("tenant_id is required for ordered inbox messages")
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                SELECT pg_advisory_xact_lock(
                    hashtextextended(:consumer || ':' || :message_id, 0)
                )
                """
            ),
            {"consumer": consumer, "message_id": message_id},
        )
        existing = self.connection.execute(
            text(
                """
                SELECT tenant_id, status, payload_hash, ordering_key, ordering_sequence
                FROM infra_inbox_messages
                WHERE consumer = :consumer AND message_id = :message_id
                """
            ),
            {"consumer": consumer, "message_id": message_id},
        ).first()
        if existing is not None:
            if existing.tenant_id != resolved_tenant_id:
                raise InfrastructureConflictError("inbox message id crossed the tenant boundary")
            if existing.status == "quarantined":
                raise InfrastructureConflictError("inbox message is quarantined")
            if existing.payload_hash != payload_hash:
                self.connection.execute(
                    text(
                        """
                        UPDATE infra_inbox_messages
                        SET conflict_hash = :payload_hash, status = 'quarantined'
                        WHERE tenant_id = :tenant_id
                          AND consumer = :consumer
                          AND message_id = :message_id
                        """
                    ),
                    {
                        "tenant_id": resolved_tenant_id,
                        "consumer": consumer,
                        "message_id": message_id,
                        "payload_hash": payload_hash,
                    },
                )
                raise InfrastructureConflictError(
                    "same inbox message id received with a different payload hash"
                )
            if existing.ordering_key != ordering_key or existing.ordering_sequence != ordering_sequence:
                raise InfrastructureConflictError("duplicate inbox message changed ordering metadata")
            return InboxReceipt(
                consumer=consumer,
                message_id=message_id,
                payload_hash=str(existing.payload_hash),
                status=str(existing.status),
                first_seen=False,
                processable=False,
                ordering_key=None if existing.ordering_key is None else str(existing.ordering_key),
                ordering_sequence=(
                    None if existing.ordering_sequence is None else int(existing.ordering_sequence)
                ),
            )

        status = "received"
        contiguous_sequence: int | None = None
        released_message_ids: tuple[str, ...] = ()
        if ordering_key is not None and ordering_sequence is not None:
            self.connection.execute(
                text(
                    """
                    SELECT pg_advisory_xact_lock(
                        hashtextextended(
                            :tenant_id || ':' || :consumer || ':' || :ordering_key,
                            0
                        )
                    )
                    """
                ),
                {
                    "tenant_id": resolved_tenant_id,
                    "consumer": consumer,
                    "ordering_key": ordering_key,
                },
            )
            sequence_owner = self.connection.execute(
                text(
                    """
                    SELECT message_id
                    FROM infra_inbox_messages
                    WHERE tenant_id = :tenant_id
                      AND consumer = :consumer
                      AND ordering_key = :ordering_key
                      AND ordering_sequence = :ordering_sequence
                    """
                ),
                {
                    "tenant_id": resolved_tenant_id,
                    "consumer": consumer,
                    "ordering_key": ordering_key,
                    "ordering_sequence": ordering_sequence,
                },
            ).first()
            if sequence_owner is not None:
                self.connection.execute(
                    text(
                        """
                        UPDATE infra_inbox_messages
                        SET conflict_hash = :payload_hash, status = 'quarantined'
                        WHERE tenant_id = :tenant_id
                          AND consumer = :consumer
                          AND ordering_key = :ordering_key
                          AND ordering_sequence = :ordering_sequence
                        """
                    ),
                    {
                        "tenant_id": resolved_tenant_id,
                        "consumer": consumer,
                        "ordering_key": ordering_key,
                        "ordering_sequence": ordering_sequence,
                        "payload_hash": payload_hash,
                    },
                )
                raise InfrastructureConflictError("ordering sequence is already owned by another message")
            self.connection.execute(
                text(
                    """
                    INSERT INTO infra_delivery_watermarks(
                        tenant_id, consumer, ordering_key, contiguous_sequence, max_seen_sequence
                    ) VALUES (
                        :tenant_id, :consumer, :ordering_key, 0, 0
                    )
                    ON CONFLICT (tenant_id, consumer, ordering_key) DO NOTHING
                    """
                ),
                {
                    "tenant_id": resolved_tenant_id,
                    "consumer": consumer,
                    "ordering_key": ordering_key,
                },
            )
            watermark = self.connection.execute(
                text(
                    """
                    SELECT contiguous_sequence, max_seen_sequence
                    FROM infra_delivery_watermarks
                    WHERE tenant_id = :tenant_id
                      AND consumer = :consumer
                      AND ordering_key = :ordering_key
                    FOR UPDATE
                    """
                ),
                {
                    "tenant_id": resolved_tenant_id,
                    "consumer": consumer,
                    "ordering_key": ordering_key,
                },
            ).one()
            contiguous_sequence = int(watermark.contiguous_sequence)
            if ordering_sequence <= contiguous_sequence:
                status = "quarantined"
            elif ordering_sequence > contiguous_sequence + 1:
                status = "buffered"

        self.connection.execute(
            text(
                """
                INSERT INTO infra_inbox_messages(
                    consumer, message_id, payload_hash, payload, status,
                    tenant_id, ordering_key, ordering_sequence
                ) VALUES (
                    :consumer, :message_id, :payload_hash, CAST(:payload AS jsonb), :status,
                    :tenant_id, :ordering_key, :ordering_sequence
                )
                """
            ),
            {
                "consumer": consumer,
                "message_id": message_id,
                "payload_hash": payload_hash,
                "payload": _json(payload),
                "status": status,
                "tenant_id": resolved_tenant_id,
                "ordering_key": ordering_key,
                "ordering_sequence": ordering_sequence,
            },
        )
        if ordering_key is not None and ordering_sequence is not None:
            self.connection.execute(
                text(
                    """
                    UPDATE infra_delivery_watermarks
                    SET max_seen_sequence = GREATEST(max_seen_sequence, :ordering_sequence),
                        updated_at = now()
                    WHERE tenant_id = :tenant_id
                      AND consumer = :consumer
                      AND ordering_key = :ordering_key
                    """
                ),
                {
                    "tenant_id": resolved_tenant_id,
                    "consumer": consumer,
                    "ordering_key": ordering_key,
                    "ordering_sequence": ordering_sequence,
                },
            )
            if status == "received":
                contiguous_sequence, released_message_ids = self._advance_delivery_watermark(
                    tenant_id=resolved_tenant_id,
                    consumer=consumer,
                    ordering_key=ordering_key,
                    starting_sequence=ordering_sequence,
                )

        return InboxReceipt(
            consumer=consumer,
            message_id=message_id,
            payload_hash=payload_hash,
            status=status,
            first_seen=True,
            processable=status == "received",
            ordering_key=ordering_key,
            ordering_sequence=ordering_sequence,
            contiguous_sequence=contiguous_sequence,
            released_message_ids=released_message_ids,
        )

    def _advance_delivery_watermark(
        self,
        *,
        tenant_id: str,
        consumer: str,
        ordering_key: str,
        starting_sequence: int,
    ) -> tuple[int, tuple[str, ...]]:
        contiguous_sequence = starting_sequence
        released: list[str] = []
        while True:
            buffered = self.connection.execute(
                text(
                    """
                    SELECT message_id
                    FROM infra_inbox_messages
                    WHERE tenant_id = :tenant_id
                      AND consumer = :consumer
                      AND ordering_key = :ordering_key
                      AND ordering_sequence = :next_sequence
                      AND status = 'buffered'
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "consumer": consumer,
                    "ordering_key": ordering_key,
                    "next_sequence": contiguous_sequence + 1,
                },
            ).first()
            if buffered is None:
                break
            contiguous_sequence += 1
            released.append(str(buffered.message_id))
            self.connection.execute(
                text(
                    """
                    UPDATE infra_inbox_messages
                    SET status = 'received'
                    WHERE tenant_id = :tenant_id
                      AND consumer = :consumer
                      AND message_id = :message_id
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "consumer": consumer,
                    "message_id": buffered.message_id,
                },
            )
        self.connection.execute(
            text(
                """
                UPDATE infra_delivery_watermarks
                SET contiguous_sequence = :contiguous_sequence,
                    updated_at = now()
                WHERE tenant_id = :tenant_id
                  AND consumer = :consumer
                  AND ordering_key = :ordering_key
                """
            ),
            {
                "tenant_id": tenant_id,
                "consumer": consumer,
                "ordering_key": ordering_key,
                "contiguous_sequence": contiguous_sequence,
            },
        )
        return contiguous_sequence, tuple(released)

    def delivery_watermark(
        self,
        *,
        tenant_id: str,
        consumer: str,
        ordering_key: str,
    ) -> DeliveryWatermarkReceipt:
        row = self.connection.execute(
            text(
                """
                SELECT contiguous_sequence, max_seen_sequence
                FROM infra_delivery_watermarks
                WHERE tenant_id = :tenant_id
                  AND consumer = :consumer
                  AND ordering_key = :ordering_key
                """
            ),
            {
                "tenant_id": tenant_id,
                "consumer": consumer,
                "ordering_key": ordering_key,
            },
        ).first()
        return DeliveryWatermarkReceipt(
            tenant_id=tenant_id,
            consumer=consumer,
            ordering_key=ordering_key,
            contiguous_sequence=0 if row is None else int(row.contiguous_sequence),
            max_seen_sequence=0 if row is None else int(row.max_seen_sequence),
        )

    def mark_inbox_processed(
        self,
        *,
        tenant_id: str,
        consumer: str,
        message_id: str,
    ) -> None:
        result = self.connection.execute(
            text(
                """
                UPDATE infra_inbox_messages
                SET status = 'processed'
                WHERE tenant_id = :tenant_id
                  AND consumer = :consumer
                  AND message_id = :message_id
                  AND status = 'received'
                """
            ),
            {
                "tenant_id": tenant_id,
                "consumer": consumer,
                "message_id": message_id,
            },
        )
        if result.rowcount != 1:
            raise InfrastructureConflictError("inbox message is not ready for processing")

    def load_processable_inbox_messages(
        self,
        *,
        tenant_id: str,
        consumer: str,
        message_ids: tuple[str, ...],
    ) -> tuple[InboxMessageRecord, ...]:
        if not message_ids:
            return ()
        rows = self.connection.execute(
            text(
                """
                SELECT tenant_id, consumer, message_id, payload, payload_hash, status,
                       ordering_key, ordering_sequence
                FROM infra_inbox_messages
                WHERE tenant_id = :tenant_id
                  AND consumer = :consumer
                  AND message_id = ANY(CAST(:message_ids AS text[]))
                  AND status = 'received'
                ORDER BY ordering_key NULLS FIRST, ordering_sequence NULLS FIRST, message_id
                """
            ),
            {
                "tenant_id": tenant_id,
                "consumer": consumer,
                "message_ids": list(message_ids),
            },
        ).all()
        records: list[InboxMessageRecord] = []
        for row in rows:
            payload = dict(row.payload)
            if canonical_sha256(payload) != row.payload_hash:
                raise InfrastructureConflictError("inbox payload hash mismatch")
            records.append(
                InboxMessageRecord(
                    tenant_id=str(row.tenant_id),
                    consumer=str(row.consumer),
                    message_id=str(row.message_id),
                    payload=payload,
                    payload_hash=str(row.payload_hash),
                    status=str(row.status),
                    ordering_key=None if row.ordering_key is None else str(row.ordering_key),
                    ordering_sequence=(
                        None if row.ordering_sequence is None else int(row.ordering_sequence)
                    ),
                )
            )
        if len(records) != len(set(message_ids)):
            raise InfrastructureConflictError("not every inbox message is ready for processing")
        return tuple(records)

    def claim_idempotency(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        request: dict[str, Any],
        ttl_seconds: int = 60,
    ) -> tuple[str, int, str]:
        receipt = self.claim_idempotency_receipt(
            scope=scope,
            key=key,
            owner=owner,
            request=request,
            ttl_seconds=ttl_seconds,
        )
        return receipt.status, receipt.generation, receipt.result_ref

    def claim_idempotency_receipt(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        request: dict[str, Any],
        ttl_seconds: int = 60,
    ) -> IdempotencyClaimReceipt:
        if ttl_seconds < 1:
            raise ValueError("idempotency ttl_seconds must be positive")
        request_hash = canonical_sha256(request)
        expires_at = utcnow() + timedelta(seconds=ttl_seconds)
        tenant_id = self.current_tenant_id()
        self.connection.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:tenant_id || ':' || :scope || ':' || :key, 0))"),
            {"tenant_id": tenant_id, "scope": scope, "key": key},
        )
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_idempotency_claims(
                    tenant_id, scope, idempotency_key, owner, request_hash, status, generation, expires_at
                )
                VALUES (:tenant_id, :scope, :key, :owner, :request_hash, 'in_progress', 1, :expires_at)
                ON CONFLICT (tenant_id, scope, idempotency_key) DO NOTHING
                RETURNING owner, request_hash, status, generation, result_ref, true AS acquired
                """
            ),
            {
                "tenant_id": tenant_id,
                "scope": scope,
                "key": key,
                "owner": owner,
                "request_hash": request_hash,
                "expires_at": expires_at,
            },
        ).first()
        if row is None:
            row = self.connection.execute(
                text(
                    """
                    UPDATE infra_idempotency_claims
                    SET generation = infra_idempotency_claims.generation + 1,
                        owner = :owner,
                        status = 'in_progress',
                        result_ref = NULL,
                        expires_at = :expires_at
                    WHERE tenant_id = :tenant_id
                      AND scope = :scope
                      AND idempotency_key = :key
                      AND request_hash = :request_hash
                      AND status in ('in_progress','expired')
                      AND expires_at <= now()
                    RETURNING owner, request_hash, status, generation, result_ref, true AS acquired
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "scope": scope,
                    "key": key,
                    "owner": owner,
                    "request_hash": request_hash,
                    "expires_at": expires_at,
                },
            ).first()
        if row is None:
            row = self.connection.execute(
                text(
                    """
                    SELECT owner, request_hash, status, generation, result_ref, false AS acquired
                    FROM infra_idempotency_claims
                    WHERE tenant_id = :tenant_id AND scope = :scope AND idempotency_key = :key
                    """
                ),
                {"tenant_id": tenant_id, "scope": scope, "key": key},
            ).one()
        if row.request_hash != request_hash:
            raise InfrastructureConflictError("idempotency key was reused with a different request hash")
        return IdempotencyClaimReceipt(
            status=str(row.status),
            generation=int(row.generation),
            result_ref=str(row.result_ref or ""),
            owner=str(row.owner),
            acquired=bool(row.acquired),
        )

    def renew_idempotency(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        generation: int,
        ttl_seconds: int = 60,
    ) -> datetime:
        if ttl_seconds < 1:
            raise ValueError("idempotency ttl_seconds must be positive")
        expires_at = utcnow() + timedelta(seconds=ttl_seconds)
        tenant_id = self.current_tenant_id()
        row = self.connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET expires_at = :expires_at
                WHERE tenant_id = :tenant_id
                  AND scope = :scope
                  AND idempotency_key = :key
                  AND owner = :owner
                  AND generation = :generation
                  AND status = 'in_progress'
                  AND expires_at >= now()
                RETURNING expires_at
                """
            ),
            {
                "tenant_id": tenant_id,
                "scope": scope,
                "key": key,
                "owner": owner,
                "generation": generation,
                "expires_at": expires_at,
            },
        ).first()
        if row is None:
            raise FencingRejectedError("idempotency claim cannot be renewed by this owner/generation")
        return row.expires_at

    def expire_stale_idempotency_claims(self) -> list[str]:
        rows = self.connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET status = 'expired'
                WHERE status = 'in_progress' AND expires_at < now()
                RETURNING scope || ':' || idempotency_key AS claim_key
                """
            )
        ).all()
        return [str(row.claim_key) for row in rows]

    def complete_idempotency(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        generation: int,
        result_ref: str,
    ) -> None:
        if not result_ref:
            raise ValueError("idempotency result_ref must not be empty")
        tenant_id = self.current_tenant_id()
        result = self.connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET status = 'completed', result_ref = :result_ref, completed_at = now()
                WHERE tenant_id = :tenant_id
                  AND scope = :scope
                  AND idempotency_key = :key
                  AND owner = :owner
                  AND generation = :generation
                  AND status = 'in_progress'
                  AND expires_at >= now()
                """
            ),
            {
                "tenant_id": tenant_id,
                "scope": scope,
                "key": key,
                "owner": owner,
                "generation": generation,
                "result_ref": result_ref,
            },
        )
        if result.rowcount != 1:
            raise FencingRejectedError("idempotency owner/generation is stale or expired")

    def abort_idempotency(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        generation: int,
    ) -> None:
        tenant_id = self.current_tenant_id()
        result = self.connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET status = 'expired', expires_at = now(), result_ref = NULL
                WHERE tenant_id = :tenant_id
                  AND scope = :scope
                  AND idempotency_key = :key
                  AND owner = :owner
                  AND generation = :generation
                  AND status = 'in_progress'
                """
            ),
            {
                "tenant_id": tenant_id,
                "scope": scope,
                "key": key,
                "owner": owner,
                "generation": generation,
            },
        )
        if result.rowcount != 1:
            raise FencingRejectedError("idempotency claim cannot be aborted by this owner/generation")

    def configure_capacity(
        self,
        *,
        resource_id: str,
        capacity_limit: int,
        owner_id: str,
        drained: bool = False,
    ) -> int:
        if not resource_id.strip():
            raise ValueError("resource_id must not be empty")
        if capacity_limit < 1:
            raise ValueError("capacity_limit must be positive")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_capacity_admissions(
                    resource_id, capacity_limit, drained, generation, updated_by
                ) VALUES (
                    :resource_id, :capacity_limit, :drained, 1, :owner_id
                )
                ON CONFLICT (resource_id) DO UPDATE
                SET capacity_limit = EXCLUDED.capacity_limit,
                    drained = EXCLUDED.drained,
                    generation = infra_capacity_admissions.generation + 1,
                    updated_by = EXCLUDED.updated_by,
                    updated_at = now()
                RETURNING generation
                """
            ),
            {
                "resource_id": resource_id,
                "capacity_limit": capacity_limit,
                "drained": drained,
                "owner_id": owner_id,
            },
        ).one()
        return int(row.generation)

    def set_capacity_drain(self, *, resource_id: str, drained: bool, owner_id: str) -> int:
        if not resource_id.strip():
            raise ValueError("resource_id must not be empty")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        row = self.connection.execute(
            text(
                """
                UPDATE infra_capacity_admissions
                SET drained = :drained,
                    generation = generation + 1,
                    updated_by = :owner_id,
                    updated_at = now()
                WHERE resource_id = :resource_id
                RETURNING generation
                """
            ),
            {
                "resource_id": resource_id,
                "drained": drained,
                "owner_id": owner_id,
            },
        ).first()
        if row is None:
            raise CapacityBackpressureError("capacity admission resource is not configured")
        return int(row.generation)

    def reserve_capacity(
        self,
        *,
        resource_id: str,
        owner_id: str,
        amount: int = 1,
        ttl_seconds: int = 30,
    ) -> CapacityReservationReceipt:
        if not resource_id.strip():
            raise ValueError("resource_id must not be empty")
        if amount < 1:
            raise ValueError("reservation amount must be positive")
        if ttl_seconds < 1:
            raise ValueError("reservation ttl_seconds must be positive")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        reservation_id = f"capacity:{uuid4()}"
        admission = self.connection.execute(
            text(
                """
                SELECT resource_id, capacity_limit, drained, generation
                FROM infra_capacity_admissions
                WHERE resource_id = :resource_id
                FOR UPDATE
                """
            ),
            {"resource_id": resource_id},
        ).first()
        if admission is None or bool(admission.drained):
            raise CapacityBackpressureError("capacity admission is drained, missing, or exhausted")

        reserved_amount = int(
            self.connection.execute(
                text(
                    """
                    SELECT COALESCE(SUM(amount), 0)::integer
                    FROM infra_capacity_reservations
                    WHERE resource_id = :resource_id
                      AND status = 'active'
                      AND expires_at > now()
                    """
                ),
                {"resource_id": resource_id},
            ).scalar_one()
        )
        remaining_capacity = int(admission.capacity_limit) - reserved_amount - amount
        if remaining_capacity < 0:
            raise CapacityBackpressureError("capacity admission is drained, missing, or exhausted")

        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_capacity_reservations(
                    reservation_id, resource_id, owner_id, amount,
                    generation, status, expires_at
                ) VALUES (
                    :reservation_id, :resource_id, :owner_id, :amount,
                    :generation, 'active', now() + (:ttl_seconds * interval '1 second')
                )
                RETURNING reservation_id, resource_id, owner_id, amount,
                          generation, expires_at
                """
            ),
            {
                "resource_id": resource_id,
                "owner_id": owner_id,
                "amount": amount,
                "ttl_seconds": ttl_seconds,
                "reservation_id": reservation_id,
                "generation": int(admission.generation),
            },
        ).one()
        return CapacityReservationReceipt(
            reservation_id=str(row.reservation_id),
            resource_id=str(row.resource_id),
            owner_id=str(row.owner_id),
            amount=int(row.amount),
            generation=int(row.generation),
            remaining_capacity=remaining_capacity,
            expires_at=row.expires_at,
        )

    def release_capacity(self, *, reservation_id: str, owner_id: str) -> None:
        if not reservation_id.strip():
            raise ValueError("reservation_id must not be empty")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        result = self.connection.execute(
            text(
                """
                UPDATE infra_capacity_reservations
                SET status = 'released',
                    released_at = now()
                WHERE reservation_id = :reservation_id
                  AND owner_id = :owner_id
                  AND status = 'active'
                """
            ),
            {"reservation_id": reservation_id, "owner_id": owner_id},
        )
        if result.rowcount != 1:
            raise FencingRejectedError("capacity reservation cannot be released by this owner")

    def configure_audit_channel(
        self,
        *,
        channel_id: str,
        capacity_limit: int,
        owner_id: str,
        fail_mode: str = "fail_closed",
        drained: bool = False,
    ) -> int:
        if not channel_id.strip():
            raise ValueError("channel_id must not be empty")
        if capacity_limit < 1:
            raise ValueError("capacity_limit must be positive")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        if fail_mode not in {"fail_closed"}:
            raise ValueError("unsupported mandatory audit fail_mode")
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_audit_channels(
                    channel_id, capacity_limit, fail_mode, drained, generation, updated_by
                ) VALUES (
                    :channel_id, :capacity_limit, :fail_mode, :drained, 1, :owner_id
                )
                ON CONFLICT (channel_id) DO UPDATE
                SET capacity_limit = EXCLUDED.capacity_limit,
                    fail_mode = EXCLUDED.fail_mode,
                    drained = EXCLUDED.drained,
                    generation = infra_audit_channels.generation + 1,
                    updated_by = EXCLUDED.updated_by,
                    updated_at = now()
                RETURNING generation
                """
            ),
            {
                "channel_id": channel_id,
                "capacity_limit": capacity_limit,
                "fail_mode": fail_mode,
                "drained": drained,
                "owner_id": owner_id,
            },
        ).one()
        return int(row.generation)

    def record_mandatory_audit(
        self,
        *,
        channel_id: str,
        effect_id: str,
        owner_id: str,
        payload: dict[str, Any],
    ) -> AuditPersistenceReceipt:
        if not channel_id.strip():
            raise ValueError("channel_id must not be empty")
        if not effect_id.strip():
            raise ValueError("effect_id must not be empty")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        payload_hash = canonical_sha256(payload)
        channel = self.connection.execute(
            text(
                """
                SELECT channel_id, capacity_limit, fail_mode, drained, generation
                FROM infra_audit_channels
                WHERE channel_id = :channel_id
                FOR UPDATE
                """
            ),
            {"channel_id": channel_id},
        ).first()
        if channel is None or bool(channel.drained):
            raise AuditCapacityError("mandatory audit channel is missing or drained")

        in_flight = int(
            self.connection.execute(
                text(
                    """
                    SELECT COALESCE(COUNT(*), 0)::integer
                    FROM infra_mandatory_audit_events
                    WHERE channel_id = :channel_id
                      AND status = 'durable'
                    """
                ),
                {"channel_id": channel_id},
            ).scalar_one()
        )
        remaining_capacity = int(channel.capacity_limit) - in_flight - 1
        if remaining_capacity < 0:
            raise AuditCapacityError("mandatory audit capacity exhausted")

        audit_id = f"audit:{uuid4()}"
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_mandatory_audit_events(
                    audit_id, channel_id, effect_id, owner_id, payload_hash,
                    payload, status, generation
                ) VALUES (
                    :audit_id, :channel_id, :effect_id, :owner_id, :payload_hash,
                    CAST(:payload AS jsonb), 'durable', :generation
                )
                RETURNING audit_id, channel_id, effect_id, owner_id, payload_hash,
                          generation, created_at
                """
            ),
            {
                "audit_id": audit_id,
                "channel_id": channel_id,
                "effect_id": effect_id,
                "owner_id": owner_id,
                "payload_hash": payload_hash,
                "payload": _json(payload),
                "generation": int(channel.generation),
            },
        ).one()
        return AuditPersistenceReceipt(
            audit_id=str(row.audit_id),
            channel_id=str(row.channel_id),
            effect_id=str(row.effect_id),
            owner_id=str(row.owner_id),
            payload_hash=str(row.payload_hash),
            generation=int(row.generation),
            remaining_capacity=remaining_capacity,
            durable_at=row.created_at,
        )

    def assert_audit_durable_for_effect(
        self,
        *,
        audit_id: str,
        effect_id: str,
        owner_id: str,
    ) -> AuditPersistenceReceipt:
        if not audit_id.strip() or not effect_id.strip() or not owner_id.strip():
            raise ValueError("audit_id, effect_id and owner_id must not be empty")
        row = self.connection.execute(
            text(
                """
                SELECT audit_id, channel_id, effect_id, owner_id, payload_hash,
                       generation, created_at
                FROM infra_mandatory_audit_events
                WHERE audit_id = :audit_id
                  AND effect_id = :effect_id
                  AND owner_id = :owner_id
                  AND status = 'durable'
                FOR UPDATE
                """
            ),
            {"audit_id": audit_id, "effect_id": effect_id, "owner_id": owner_id},
        ).first()
        if row is None:
            raise FencingRejectedError("effect cannot run before durable mandatory audit")
        return AuditPersistenceReceipt(
            audit_id=str(row.audit_id),
            channel_id=str(row.channel_id),
            effect_id=str(row.effect_id),
            owner_id=str(row.owner_id),
            payload_hash=str(row.payload_hash),
            generation=int(row.generation),
            remaining_capacity=0,
            durable_at=row.created_at,
        )

    def mark_audited_effect_observed(
        self,
        *,
        audit_id: str,
        effect_id: str,
        owner_id: str,
    ) -> None:
        if not audit_id.strip() or not effect_id.strip() or not owner_id.strip():
            raise ValueError("audit_id, effect_id and owner_id must not be empty")
        result = self.connection.execute(
            text(
                """
                UPDATE infra_mandatory_audit_events
                SET status = 'effect_observed',
                    effect_observed_at = now()
                WHERE audit_id = :audit_id
                  AND effect_id = :effect_id
                  AND owner_id = :owner_id
                  AND status = 'durable'
                """
            ),
            {"audit_id": audit_id, "effect_id": effect_id, "owner_id": owner_id},
        )
        if result.rowcount != 1:
            raise FencingRejectedError("audited effect cannot be observed by this owner")

    def configure_cutover_target(
        self,
        *,
        target_id: str,
        owner_id: str,
    ) -> int:
        if not target_id.strip():
            raise ValueError("target_id must not be empty")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_cutover_targets(
                    target_id, active_generation, updated_by
                ) VALUES (
                    :target_id, 1, :owner_id
                )
                ON CONFLICT (target_id) DO UPDATE
                SET updated_by = EXCLUDED.updated_by,
                    updated_at = now()
                RETURNING active_generation
                """
            ),
            {"target_id": target_id, "owner_id": owner_id},
        ).one()
        return int(row.active_generation)

    def register_cutover_snapshot(
        self,
        *,
        target_id: str,
        snapshot_id: str,
        owner_id: str,
        payload: dict[str, Any],
    ) -> str:
        if not target_id.strip() or not snapshot_id.strip() or not owner_id.strip():
            raise ValueError("target_id, snapshot_id and owner_id must not be empty")
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO infra_cutover_snapshots(
                    snapshot_id, target_id, owner_id, payload_hash, payload, status
                ) VALUES (
                    :snapshot_id, :target_id, :owner_id, :payload_hash,
                    CAST(:payload AS jsonb), 'candidate'
                )
                """
            ),
            {
                "snapshot_id": snapshot_id,
                "target_id": target_id,
                "owner_id": owner_id,
                "payload_hash": payload_hash,
                "payload": _json(payload),
            },
        )
        return payload_hash

    def activate_cutover_snapshot(
        self,
        *,
        target_id: str,
        snapshot_id: str,
        expected_generation: int,
        owner_id: str,
    ) -> CutoverActivationReceipt:
        if expected_generation < 1:
            raise ValueError("expected_generation must be positive")
        if not target_id.strip() or not snapshot_id.strip() or not owner_id.strip():
            raise ValueError("target_id, snapshot_id and owner_id must not be empty")
        target = self.connection.execute(
            text(
                """
                SELECT target_id, active_snapshot_id, active_generation
                FROM infra_cutover_targets
                WHERE target_id = :target_id
                FOR UPDATE
                """
            ),
            {"target_id": target_id},
        ).first()
        if target is None:
            raise FencingRejectedError("cutover target is not configured")
        if int(target.active_generation) != expected_generation:
            raise FencingRejectedError("cutover generation CAS rejected stale writer")

        snapshot = self.connection.execute(
            text(
                """
                SELECT snapshot_id
                FROM infra_cutover_snapshots
                WHERE target_id = :target_id
                  AND snapshot_id = :snapshot_id
                  AND status = 'candidate'
                FOR UPDATE
                """
            ),
            {"target_id": target_id, "snapshot_id": snapshot_id},
        ).first()
        if snapshot is None:
            raise FencingRejectedError("cutover snapshot is not a candidate for this target")

        next_generation = expected_generation + 1
        if target.active_snapshot_id is not None:
            self.connection.execute(
                text(
                    """
                    UPDATE infra_cutover_snapshots
                    SET status = 'superseded',
                        superseded_at = now()
                    WHERE snapshot_id = :snapshot_id
                      AND status = 'active'
                    """
                ),
                {"snapshot_id": target.active_snapshot_id},
            )
        activated = self.connection.execute(
            text(
                """
                UPDATE infra_cutover_snapshots
                SET status = 'active',
                    activated_generation = :next_generation,
                    activated_at = now()
                WHERE snapshot_id = :snapshot_id
                  AND target_id = :target_id
                  AND status = 'candidate'
                RETURNING activated_at
                """
            ),
            {
                "target_id": target_id,
                "snapshot_id": snapshot_id,
                "next_generation": next_generation,
            },
        ).one()
        self.connection.execute(
            text(
                """
                UPDATE infra_cutover_targets
                SET active_snapshot_id = :snapshot_id,
                    active_generation = :next_generation,
                    updated_by = :owner_id,
                    updated_at = now()
                WHERE target_id = :target_id
                """
            ),
            {
                "target_id": target_id,
                "snapshot_id": snapshot_id,
                "next_generation": next_generation,
                "owner_id": owner_id,
            },
        )
        return CutoverActivationReceipt(
            target_id=target_id,
            snapshot_id=snapshot_id,
            previous_generation=expected_generation,
            active_generation=next_generation,
            activated_at=activated.activated_at,
        )

    def acquire_active_snapshot_ref(
        self,
        *,
        target_id: str,
        owner_id: str,
    ) -> ActiveSnapshotRefReceipt:
        if not target_id.strip() or not owner_id.strip():
            raise ValueError("target_id and owner_id must not be empty")
        target = self.connection.execute(
            text(
                """
                SELECT target_id, active_snapshot_id, active_generation
                FROM infra_cutover_targets
                WHERE target_id = :target_id
                FOR UPDATE
                """
            ),
            {"target_id": target_id},
        ).first()
        if target is None or target.active_snapshot_id is None:
            raise FencingRejectedError("cutover target has no active snapshot")
        ref_id = f"snapshot-ref:{uuid4()}"
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_active_snapshot_refs(
                    ref_id, target_id, snapshot_id, generation, owner_id, status
                ) VALUES (
                    :ref_id, :target_id, :snapshot_id, :generation, :owner_id, 'active'
                )
                RETURNING ref_id, target_id, snapshot_id, generation, owner_id
                """
            ),
            {
                "ref_id": ref_id,
                "target_id": target_id,
                "snapshot_id": target.active_snapshot_id,
                "generation": int(target.active_generation),
                "owner_id": owner_id,
            },
        ).one()
        return ActiveSnapshotRefReceipt(
            ref_id=str(row.ref_id),
            target_id=str(row.target_id),
            snapshot_id=str(row.snapshot_id),
            generation=int(row.generation),
            owner_id=str(row.owner_id),
        )

    def release_active_snapshot_ref(self, *, ref_id: str, owner_id: str) -> None:
        if not ref_id.strip() or not owner_id.strip():
            raise ValueError("ref_id and owner_id must not be empty")
        result = self.connection.execute(
            text(
                """
                UPDATE infra_active_snapshot_refs
                SET status = 'released',
                    released_at = now()
                WHERE ref_id = :ref_id
                  AND owner_id = :owner_id
                  AND status = 'active'
                """
            ),
            {"ref_id": ref_id, "owner_id": owner_id},
        )
        if result.rowcount != 1:
            raise FencingRejectedError("active snapshot ref cannot be released by this owner")

    def retire_cutover_snapshot(
        self,
        *,
        target_id: str,
        snapshot_id: str,
        owner_id: str,
    ) -> None:
        if not target_id.strip() or not snapshot_id.strip() or not owner_id.strip():
            raise ValueError("target_id, snapshot_id and owner_id must not be empty")
        target = self.connection.execute(
            text(
                """
                SELECT active_snapshot_id
                FROM infra_cutover_targets
                WHERE target_id = :target_id
                FOR UPDATE
                """
            ),
            {"target_id": target_id},
        ).first()
        if target is None:
            raise FencingRejectedError("cutover target is not configured")
        if target.active_snapshot_id == snapshot_id:
            raise FencingRejectedError("active cutover snapshot cannot be retired")
        active_refs = int(
            self.connection.execute(
                text(
                    """
                    SELECT COALESCE(COUNT(*), 0)::integer
                    FROM infra_active_snapshot_refs
                    WHERE target_id = :target_id
                      AND snapshot_id = :snapshot_id
                      AND status = 'active'
                    """
                ),
                {"target_id": target_id, "snapshot_id": snapshot_id},
            ).scalar_one()
        )
        if active_refs:
            raise FencingRejectedError("active snapshot references block retirement")
        result = self.connection.execute(
            text(
                """
                UPDATE infra_cutover_snapshots
                SET status = 'retired',
                    retired_at = now(),
                    retired_by = :owner_id
                WHERE target_id = :target_id
                  AND snapshot_id = :snapshot_id
                  AND status IN ('candidate', 'superseded')
                """
            ),
            {"target_id": target_id, "snapshot_id": snapshot_id, "owner_id": owner_id},
        )
        if result.rowcount != 1:
            raise FencingRejectedError("cutover snapshot is not eligible for retirement")

    def record_recovery_watermark(
        self,
        *,
        component_id: str,
        service_kind: str,
        authority: str,
        watermark: str,
        owner_id: str,
        payload: dict[str, Any],
    ) -> RecoveryWatermarkReceipt:
        if not component_id.strip() or not service_kind.strip() or not watermark.strip():
            raise ValueError("component_id, service_kind and watermark must not be empty")
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        if authority not in {"authoritative", "derived"}:
            raise ValueError("authority must be authoritative or derived")
        payload_hash = canonical_sha256(payload)
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_recovery_watermarks(
                    component_id, service_kind, authority, watermark, payload_hash,
                    payload, owner_id
                ) VALUES (
                    :component_id, :service_kind, :authority, :watermark, :payload_hash,
                    CAST(:payload AS jsonb), :owner_id
                )
                ON CONFLICT (component_id) DO UPDATE
                SET service_kind = EXCLUDED.service_kind,
                    authority = EXCLUDED.authority,
                    watermark = EXCLUDED.watermark,
                    payload_hash = EXCLUDED.payload_hash,
                    payload = EXCLUDED.payload,
                    owner_id = EXCLUDED.owner_id,
                    updated_at = now()
                RETURNING component_id, service_kind, authority, watermark, payload_hash
                """
            ),
            {
                "component_id": component_id,
                "service_kind": service_kind,
                "authority": authority,
                "watermark": watermark,
                "payload_hash": payload_hash,
                "payload": _json(payload),
                "owner_id": owner_id,
            },
        ).one()
        return RecoveryWatermarkReceipt(
            component_id=str(row.component_id),
            service_kind=str(row.service_kind),
            authority=str(row.authority),
            watermark=str(row.watermark),
            payload_hash=str(row.payload_hash),
        )

    def create_recovery_set(
        self,
        *,
        recovery_set_id: str,
        recovery_point: str,
        component_ids: tuple[str, ...],
        owner_id: str,
    ) -> RecoverySetReceipt:
        if not recovery_set_id.strip() or not recovery_point.strip() or not owner_id.strip():
            raise ValueError("recovery_set_id, recovery_point and owner_id must not be empty")
        if not component_ids:
            raise ValueError("component_ids must not be empty")
        normalized_components = tuple(dict.fromkeys(component_ids))
        if len(normalized_components) != len(component_ids) or any(
            not item.strip() for item in normalized_components
        ):
            raise ValueError("component_ids must be unique and non-empty")
        rows = self.connection.execute(
            text(
                """
                SELECT component_id, service_kind, authority, watermark, payload_hash
                FROM infra_recovery_watermarks
                WHERE component_id = ANY(:component_ids)
                FOR UPDATE
                """
            ),
            {"component_ids": list(normalized_components)},
        ).all()
        by_component = {str(row.component_id): row for row in rows}
        missing = [item for item in normalized_components if item not in by_component]
        if missing:
            raise InfrastructureConflictError(f"missing recovery watermarks: {missing!r}")
        mismatched = [
            item
            for item in normalized_components
            if str(by_component[item].watermark) != recovery_point
        ]
        if mismatched:
            raise InfrastructureConflictError(
                f"recovery watermark mismatch for recovery point {recovery_point}: {mismatched!r}"
            )
        authorities = {str(row.authority) for row in rows}
        if "authoritative" not in authorities or "derived" not in authorities:
            raise InfrastructureConflictError("recovery set must include authoritative and derived watermarks")
        verification_hash = canonical_sha256(
            {
                "recovery_point": recovery_point,
                "components": [
                    {
                        "component_id": item,
                        "service_kind": str(by_component[item].service_kind),
                        "authority": str(by_component[item].authority),
                        "watermark": str(by_component[item].watermark),
                        "payload_hash": str(by_component[item].payload_hash),
                    }
                    for item in normalized_components
                ],
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO infra_recovery_sets(
                    recovery_set_id, recovery_point, status, verification_hash, owner_id
                ) VALUES (
                    :recovery_set_id, :recovery_point, 'verified',
                    :verification_hash, :owner_id
                )
                """
            ),
            {
                "recovery_set_id": recovery_set_id,
                "recovery_point": recovery_point,
                "verification_hash": verification_hash,
                "owner_id": owner_id,
            },
        )
        for component_id in normalized_components:
            row = by_component[component_id]
            self.connection.execute(
                text(
                    """
                    INSERT INTO infra_recovery_set_members(
                        recovery_set_id, component_id, service_kind, authority,
                        watermark, payload_hash
                    ) VALUES (
                        :recovery_set_id, :component_id, :service_kind, :authority,
                        :watermark, :payload_hash
                    )
                    """
                ),
                {
                    "recovery_set_id": recovery_set_id,
                    "component_id": component_id,
                    "service_kind": str(row.service_kind),
                    "authority": str(row.authority),
                    "watermark": str(row.watermark),
                    "payload_hash": str(row.payload_hash),
                },
            )
        return RecoverySetReceipt(
            recovery_set_id=recovery_set_id,
            recovery_point=recovery_point,
            component_ids=normalized_components,
            verification_hash=verification_hash,
        )

    def register_secret_version(
        self,
        *,
        secret_ref: str,
        tenant_id: str,
        version: int,
        kms_key_ref: str,
        config_hash: str,
        owner_id: str,
        payload: dict[str, Any],
    ) -> SecretVersionReceipt:
        if (
            not secret_ref.strip()
            or not tenant_id.strip()
            or not kms_key_ref.strip()
            or not owner_id.strip()
        ):
            raise ValueError("secret_ref, tenant_id, kms_key_ref and owner_id must not be empty")
        if version < 1:
            raise ValueError("secret version must be positive")
        if len(config_hash) != 64:
            raise ValueError("config_hash must be a sha256 hex digest")
        if _contains_secret_material(payload):
            raise ValueError("secret rotation payload must not contain secret material")
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO infra_secret_versions(
                    secret_ref, version, tenant_id, kms_key_ref, config_hash,
                    payload_hash, payload, status, owner_id
                ) VALUES (
                    :secret_ref, :version, :tenant_id, :kms_key_ref, :config_hash,
                    :payload_hash, CAST(:payload AS jsonb), 'staged', :owner_id
                )
                ON CONFLICT (secret_ref, version) DO UPDATE
                SET tenant_id = EXCLUDED.tenant_id,
                    kms_key_ref = EXCLUDED.kms_key_ref,
                    config_hash = EXCLUDED.config_hash,
                    payload_hash = EXCLUDED.payload_hash,
                    payload = EXCLUDED.payload,
                    owner_id = EXCLUDED.owner_id
                WHERE infra_secret_versions.status <> 'active'
                """
            ),
            {
                "secret_ref": secret_ref,
                "version": version,
                "tenant_id": tenant_id,
                "kms_key_ref": kms_key_ref,
                "config_hash": config_hash,
                "payload_hash": payload_hash,
                "payload": _json(payload),
                "owner_id": owner_id,
            },
        )
        return SecretVersionReceipt(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            version=version,
            status="staged",
            generation=0,
        )

    def activate_secret_version(
        self,
        *,
        secret_ref: str,
        tenant_id: str,
        version: int,
        expected_generation: int,
        owner_id: str,
    ) -> SecretVersionReceipt:
        if expected_generation < 0:
            raise ValueError("expected_generation must be non-negative")
        version_row = self.connection.execute(
            text(
                """
                SELECT tenant_id
                FROM infra_secret_versions
                WHERE secret_ref = :secret_ref AND version = :version
                FOR UPDATE
                """
            ),
            {"secret_ref": secret_ref, "version": version},
        ).first()
        if version_row is None:
            raise InfrastructureConflictError("secret version is not registered")
        if str(version_row.tenant_id) != tenant_id:
            raise InfrastructureConflictError("secret version crossed the tenant boundary")

        head = self.connection.execute(
            text(
                """
                SELECT tenant_id, active_version, generation
                FROM infra_secret_rotation_heads
                WHERE secret_ref = :secret_ref
                FOR UPDATE
                """
            ),
            {"secret_ref": secret_ref},
        ).first()
        current_generation = 0 if head is None else int(head.generation)
        if current_generation != expected_generation:
            raise FencingRejectedError("secret rotation generation is stale")
        if head is not None and str(head.tenant_id) != tenant_id:
            raise InfrastructureConflictError("secret head crossed the tenant boundary")
        previous_version = None if head is None else int(head.active_version)
        next_generation = current_generation + 1

        self.connection.execute(
            text(
                """
                UPDATE infra_secret_versions
                SET status = CASE WHEN version = :version THEN 'active' ELSE 'retired' END,
                    activated_at = CASE WHEN version = :version THEN now() ELSE activated_at END,
                    retired_at = CASE WHEN version = :version THEN NULL ELSE now() END
                WHERE secret_ref = :secret_ref AND tenant_id = :tenant_id
                """
            ),
            {"secret_ref": secret_ref, "tenant_id": tenant_id, "version": version},
        )
        self.connection.execute(
            text(
                """
                INSERT INTO infra_secret_rotation_heads(
                    secret_ref, tenant_id, active_version, previous_version,
                    generation, status, owner_id
                ) VALUES (
                    :secret_ref, :tenant_id, :version, :previous_version,
                    :generation, 'active', :owner_id
                )
                ON CONFLICT (secret_ref) DO UPDATE
                SET tenant_id = EXCLUDED.tenant_id,
                    active_version = EXCLUDED.active_version,
                    previous_version = EXCLUDED.previous_version,
                    generation = EXCLUDED.generation,
                    status = 'active',
                    owner_id = EXCLUDED.owner_id,
                    updated_at = now()
                """
            ),
            {
                "secret_ref": secret_ref,
                "tenant_id": tenant_id,
                "version": version,
                "previous_version": previous_version,
                "generation": next_generation,
                "owner_id": owner_id,
            },
        )
        return SecretVersionReceipt(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            version=version,
            status="active",
            generation=next_generation,
        )

    def rollback_secret_version(
        self,
        *,
        secret_ref: str,
        tenant_id: str,
        target_version: int,
        expected_generation: int,
        owner_id: str,
    ) -> SecretVersionReceipt:
        head = self.connection.execute(
            text(
                """
                SELECT tenant_id, active_version, generation
                FROM infra_secret_rotation_heads
                WHERE secret_ref = :secret_ref
                FOR UPDATE
                """
            ),
            {"secret_ref": secret_ref},
        ).first()
        if head is None:
            raise InfrastructureConflictError("secret rotation head is missing")
        if str(head.tenant_id) != tenant_id:
            raise InfrastructureConflictError("secret rollback crossed the tenant boundary")
        if int(head.generation) != expected_generation:
            raise FencingRejectedError("secret rollback generation is stale")
        active_version = int(head.active_version)
        if target_version == active_version:
            raise InfrastructureConflictError("secret rollback target is already active")
        target = self.connection.execute(
            text(
                """
                SELECT tenant_id
                FROM infra_secret_versions
                WHERE secret_ref = :secret_ref AND version = :target_version
                FOR UPDATE
                """
            ),
            {"secret_ref": secret_ref, "target_version": target_version},
        ).first()
        if target is None:
            raise InfrastructureConflictError("secret rollback target is missing")
        if str(target.tenant_id) != tenant_id:
            raise InfrastructureConflictError("secret rollback target crossed the tenant boundary")
        next_generation = int(head.generation) + 1
        self.connection.execute(
            text(
                """
                UPDATE infra_secret_versions
                SET status = CASE WHEN version = :target_version THEN 'active' ELSE 'retired' END,
                    activated_at = CASE WHEN version = :target_version THEN now() ELSE activated_at END,
                    retired_at = CASE WHEN version = :target_version THEN NULL ELSE now() END
                WHERE secret_ref = :secret_ref AND tenant_id = :tenant_id
                """
            ),
            {
                "secret_ref": secret_ref,
                "tenant_id": tenant_id,
                "target_version": target_version,
            },
        )
        self.connection.execute(
            text(
                """
                UPDATE infra_secret_rotation_heads
                SET active_version = :target_version,
                    previous_version = :active_version,
                    generation = :generation,
                    status = 'rolled_back',
                    owner_id = :owner_id,
                    updated_at = now()
                WHERE secret_ref = :secret_ref
                """
            ),
            {
                "secret_ref": secret_ref,
                "target_version": target_version,
                "active_version": active_version,
                "generation": next_generation,
                "owner_id": owner_id,
            },
        )
        return SecretVersionReceipt(
            secret_ref=secret_ref,
            tenant_id=tenant_id,
            version=target_version,
            status="rolled_back",
            generation=next_generation,
        )

    def issue_secret_lease(
        self,
        *,
        secret_ref: str,
        tenant_id: str,
        owner_id: str,
        ttl_seconds: int,
    ) -> SecretLeaseReceipt:
        if ttl_seconds < 1:
            raise ValueError("secret lease ttl_seconds must be positive")
        row = self.connection.execute(
            text(
                """
                SELECT h.tenant_id, h.active_version, h.generation, v.payload_hash
                FROM infra_secret_rotation_heads h
                JOIN infra_secret_versions v
                  ON v.secret_ref = h.secret_ref
                 AND v.version = h.active_version
                WHERE h.secret_ref = :secret_ref
                  AND h.tenant_id = :tenant_id
                  AND v.status = 'active'
                FOR UPDATE
                """
            ),
            {"secret_ref": secret_ref, "tenant_id": tenant_id},
        ).first()
        if row is None:
            raise InfrastructureConflictError("active secret version is unavailable for tenant")
        lease_id = f"secret-lease:{uuid4()}"
        lease_row = self.connection.execute(
            text(
                """
                INSERT INTO infra_secret_leases(
                    lease_id, secret_ref, tenant_id, version, generation,
                    owner_id, payload_hash, expires_at
                ) VALUES (
                    :lease_id, :secret_ref, :tenant_id, :version, :generation,
                    :owner_id, :payload_hash, now() + (:ttl_seconds * interval '1 second')
                )
                RETURNING lease_id, secret_ref, tenant_id, version, generation,
                          payload_hash, expires_at
                """
            ),
            {
                "lease_id": lease_id,
                "secret_ref": secret_ref,
                "tenant_id": tenant_id,
                "version": int(row.active_version),
                "generation": int(row.generation),
                "owner_id": owner_id,
                "payload_hash": str(row.payload_hash),
                "ttl_seconds": ttl_seconds,
            },
        ).one()
        return SecretLeaseReceipt(
            lease_id=str(lease_row.lease_id),
            secret_ref=str(lease_row.secret_ref),
            tenant_id=str(lease_row.tenant_id),
            version=int(lease_row.version),
            generation=int(lease_row.generation),
            payload_hash=str(lease_row.payload_hash),
            expires_at=lease_row.expires_at,
        )

    def enforce_tenant_scope(
        self,
        *,
        service_kind: str,
        resource_ref: str,
        expected_tenant_id: str,
        observed_tenant_id: str,
        action: str,
        owner_id: str,
        payload: dict[str, Any],
    ) -> None:
        if expected_tenant_id == observed_tenant_id:
            return
        if action not in {"QUARANTINE", "FAIL_CLOSED", "MANDATORY_AUDIT"}:
            raise ValueError("cross-tenant action must fail closed")
        status = {
            "QUARANTINE": "quarantined",
            "FAIL_CLOSED": "blocked",
            "MANDATORY_AUDIT": "mandatory_audit",
        }[action]
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO infra_cross_tenant_hits(
                    hit_id, service_kind, resource_ref, expected_tenant_id,
                    observed_tenant_id, action, status, payload_hash, payload, owner_id
                ) VALUES (
                    :hit_id, :service_kind, :resource_ref, :expected_tenant_id,
                    :observed_tenant_id, :action, :status, :payload_hash,
                    CAST(:payload AS jsonb), :owner_id
                )
                """
            ),
            {
                "hit_id": f"tenant-hit:{uuid4()}",
                "service_kind": service_kind,
                "resource_ref": resource_ref,
                "expected_tenant_id": expected_tenant_id,
                "observed_tenant_id": observed_tenant_id,
                "action": action,
                "status": status,
                "payload_hash": payload_hash,
                "payload": _json(payload),
                "owner_id": owner_id,
            },
        )
        raise InfrastructureConflictError("cross-tenant hit was blocked")

    def acquire_lease(self, *, resource_id: str, owner_id: str, ttl_seconds: int = 30) -> FencingToken:
        if ttl_seconds < 1:
            raise ValueError("lease ttl_seconds must be positive")
        lease_id = f"lease:{uuid4()}"
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                VALUES (
                    :resource_id, :owner_id, :lease_id, 1,
                    now() + (:ttl_seconds * interval '1 second')
                )
                ON CONFLICT (resource_id) DO UPDATE
                SET owner_id = CASE
                        WHEN infra_worker_leases.expires_at <= now() THEN EXCLUDED.owner_id
                        ELSE infra_worker_leases.owner_id
                    END,
                    lease_id = CASE
                        WHEN infra_worker_leases.expires_at <= now() THEN EXCLUDED.lease_id
                        ELSE infra_worker_leases.lease_id
                    END,
                    epoch = CASE
                        WHEN infra_worker_leases.expires_at <= now() THEN infra_worker_leases.epoch + 1
                        ELSE infra_worker_leases.epoch
                    END,
                    expires_at = CASE
                        WHEN infra_worker_leases.expires_at <= now() THEN EXCLUDED.expires_at
                        ELSE GREATEST(infra_worker_leases.expires_at, EXCLUDED.expires_at)
                    END,
                    updated_at = now()
                WHERE infra_worker_leases.expires_at <= now()
                   OR infra_worker_leases.owner_id = EXCLUDED.owner_id
                RETURNING resource_id, owner_id, lease_id, epoch, expires_at
                """
            ),
            {
                "resource_id": resource_id,
                "owner_id": owner_id,
                "lease_id": lease_id,
                "ttl_seconds": ttl_seconds,
            },
        ).first()
        if row is None:
            raise FencingRejectedError("lease is held by another live owner")
        return FencingToken(
            resource_id=str(row.resource_id),
            owner_id=str(row.owner_id),
            lease_id=str(row.lease_id),
            epoch=int(row.epoch),
            expires_at=row.expires_at,
        )

    def assert_fence(self, token: FencingToken, *, clock_tolerance_seconds: float = 0) -> None:
        if not math.isfinite(clock_tolerance_seconds) or clock_tolerance_seconds < 0:
            raise ValueError("clock_tolerance_seconds must be finite and non-negative")
        row = self.connection.execute(
            text(
                """
                SELECT resource_id
                FROM infra_worker_leases
                WHERE resource_id = :resource_id
                  AND owner_id = :owner_id
                  AND lease_id = :lease_id
                  AND epoch = :epoch
                  AND expires_at >= now() + (:clock_tolerance_seconds * interval '1 second')
                FOR UPDATE
                """
            ),
            {
                "resource_id": token.resource_id,
                "owner_id": token.owner_id,
                "lease_id": token.lease_id,
                "epoch": token.epoch,
                "clock_tolerance_seconds": clock_tolerance_seconds,
            },
        ).first()
        if row is None:
            raise FencingRejectedError("fencing token is stale")

    def renew_lease(self, token: FencingToken, *, ttl_seconds: int = 30) -> FencingToken:
        if ttl_seconds < 1:
            raise ValueError("lease ttl_seconds must be positive")
        row = self.connection.execute(
            text(
                """
                UPDATE infra_worker_leases
                SET expires_at = GREATEST(
                        expires_at,
                        now() + (:ttl_seconds * interval '1 second')
                    ),
                    updated_at = now()
                WHERE resource_id = :resource_id
                  AND owner_id = :owner_id
                  AND lease_id = :lease_id
                  AND epoch = :epoch
                  AND expires_at >= now()
                RETURNING resource_id, owner_id, lease_id, epoch, expires_at
                """
            ),
            {
                "resource_id": token.resource_id,
                "owner_id": token.owner_id,
                "lease_id": token.lease_id,
                "epoch": token.epoch,
                "ttl_seconds": ttl_seconds,
            },
        ).first()
        if row is None:
            raise FencingRejectedError("lease cannot be renewed by this fencing token")
        return FencingToken(
            resource_id=str(row.resource_id),
            owner_id=str(row.owner_id),
            lease_id=str(row.lease_id),
            epoch=int(row.epoch),
            expires_at=row.expires_at,
        )

    def transfer_lease(
        self,
        token: FencingToken,
        *,
        new_owner_id: str,
        ttl_seconds: int = 30,
    ) -> FencingToken:
        if not new_owner_id or new_owner_id == token.owner_id:
            raise ValueError("new_owner_id must identify a different owner")
        if ttl_seconds < 1:
            raise ValueError("lease ttl_seconds must be positive")
        new_lease_id = f"lease:{uuid4()}"
        row = self.connection.execute(
            text(
                """
                UPDATE infra_worker_leases
                SET owner_id = :new_owner_id,
                    lease_id = :new_lease_id,
                    epoch = epoch + 1,
                    expires_at = now() + (:ttl_seconds * interval '1 second'),
                    updated_at = now()
                WHERE resource_id = :resource_id
                  AND owner_id = :owner_id
                  AND lease_id = :lease_id
                  AND epoch = :epoch
                  AND expires_at >= now()
                RETURNING resource_id, owner_id, lease_id, epoch, expires_at
                """
            ),
            {
                "resource_id": token.resource_id,
                "owner_id": token.owner_id,
                "lease_id": token.lease_id,
                "epoch": token.epoch,
                "new_owner_id": new_owner_id,
                "new_lease_id": new_lease_id,
                "ttl_seconds": ttl_seconds,
            },
        ).first()
        if row is None:
            raise FencingRejectedError("lease cannot be transferred by this fencing token")
        return FencingToken(
            resource_id=str(row.resource_id),
            owner_id=str(row.owner_id),
            lease_id=str(row.lease_id),
            epoch=int(row.epoch),
            expires_at=row.expires_at,
        )

    def cancel_lease(self, token: FencingToken) -> None:
        result = self.connection.execute(
            text(
                """
                UPDATE infra_worker_leases
                SET expires_at = now() - interval '1 day', updated_at = now()
                WHERE resource_id = :resource_id
                  AND owner_id = :owner_id
                  AND lease_id = :lease_id
                  AND epoch = :epoch
                  AND expires_at >= now()
                """
            ),
            {
                "resource_id": token.resource_id,
                "owner_id": token.owner_id,
                "lease_id": token.lease_id,
                "epoch": token.epoch,
            },
        )
        if result.rowcount != 1:
            raise FencingRejectedError("lease cannot be cancelled by this fencing token")

    def put_object_manifest(
        self,
        *,
        object_ref: str,
        content: bytes,
        owner: str,
        visibility: str = "staged",
    ) -> str:
        content_hash = canonical_sha256({"bytes": content.hex()})
        self.record_object_manifest(
            object_ref=object_ref,
            content_hash=content_hash,
            size_bytes=len(content),
            owner=owner,
            visibility=visibility,
        )
        return content_hash

    def record_object_manifest(
        self,
        *,
        object_ref: str,
        content_hash: str,
        size_bytes: int,
        owner: str,
        visibility: str = "staged",
    ) -> ObjectManifestRecord:
        if not object_ref.strip() or not owner.strip():
            raise ValueError("object_ref and owner must not be empty")
        if len(content_hash) != 64 or any(
            char not in "0123456789abcdef" for char in content_hash
        ):
            raise ValueError("content_hash must be a lowercase SHA-256 digest")
        if size_bytes < 0:
            raise ValueError("size_bytes must be non-negative")
        if visibility not in {"staged", "visible", "deleted", "restored"}:
            raise ValueError("unsupported object manifest visibility")
        self.connection.execute(
            text(
                """
                INSERT INTO infra_object_manifests(object_ref, owner, content_hash, size_bytes, visibility)
                VALUES (:object_ref, :owner, :content_hash, :size_bytes, :visibility)
                ON CONFLICT (object_ref) DO UPDATE
                SET conflict_hash = CASE
                    WHEN infra_object_manifests.visibility <> 'quarantined'
                     AND infra_object_manifests.owner = EXCLUDED.owner
                     AND infra_object_manifests.content_hash = EXCLUDED.content_hash
                     AND infra_object_manifests.size_bytes = EXCLUDED.size_bytes
                    THEN infra_object_manifests.conflict_hash
                    ELSE EXCLUDED.content_hash
                END,
                visibility = CASE
                    WHEN infra_object_manifests.visibility <> 'quarantined'
                     AND infra_object_manifests.owner = EXCLUDED.owner
                     AND infra_object_manifests.content_hash = EXCLUDED.content_hash
                     AND infra_object_manifests.size_bytes = EXCLUDED.size_bytes
                    THEN EXCLUDED.visibility
                    ELSE 'quarantined'
                END
                """
            ),
            {
                "object_ref": object_ref,
                "owner": owner,
                "content_hash": content_hash,
                "size_bytes": size_bytes,
                "visibility": visibility,
            },
        )
        manifest = self.object_manifest(object_ref=object_ref)
        if manifest is None:
            raise RuntimeError("object manifest was not persisted")
        if manifest.visibility == "quarantined":
            raise InfrastructureConflictError(
                "object ref reused across owner, hash, or size boundary"
            )
        return manifest

    def object_manifest(self, *, object_ref: str) -> ObjectManifestRecord | None:
        row = self.connection.execute(
            text(
                """
                SELECT object_ref, owner, content_hash, size_bytes, visibility, conflict_hash
                FROM infra_object_manifests
                WHERE object_ref = :object_ref
                """
            ),
            {"object_ref": object_ref},
        ).one_or_none()
        if row is None:
            return None
        return ObjectManifestRecord(
            object_ref=row.object_ref,
            owner=row.owner,
            content_hash=row.content_hash,
            size_bytes=int(row.size_bytes),
            visibility=row.visibility,
            conflict_hash=row.conflict_hash,
        )

    def save_checkpoint(
        self,
        *,
        thread_id: str,
        checkpoint_id: str,
        generation: int,
        state: dict[str, Any],
        owner: str,
    ) -> None:
        state_hash = canonical_sha256(state)
        result = self.connection.execute(
            text(
                """
                INSERT INTO infra_checkpoints(
                    thread_id, checkpoint_id, generation, owner, state_hash, state_payload
                ) VALUES (
                    :thread_id, :checkpoint_id, :generation, :owner, :state_hash, CAST(:state_payload AS jsonb)
                )
                ON CONFLICT (thread_id, generation) DO NOTHING
                """
            ),
            {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "generation": generation,
                "owner": owner,
                "state_hash": state_hash,
                "state_payload": _json(state),
            },
        )
        if result.rowcount != 1:
            raise InfrastructureConflictError("checkpoint generation already exists")

    def latest_checkpoint(self, *, thread_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            text(
                """
                SELECT checkpoint_id, generation, state_hash, state_payload
                FROM infra_checkpoints
                WHERE thread_id = :thread_id
                ORDER BY generation DESC
                LIMIT 1
                """
            ),
            {"thread_id": thread_id},
        ).first()
        if row is None:
            return None
        payload = dict(row.state_payload)
        if canonical_sha256(payload) != row.state_hash:
            raise InfrastructureConflictError("checkpoint state hash mismatch")
        return {
            "checkpoint_id": row.checkpoint_id,
            "generation": row.generation,
            "state": payload,
        }


def _contains_secret_material(payload: Any) -> bool:
    forbidden_keys = {"secret", "secret_material", "plaintext", "material", "value"}
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key).lower() in forbidden_keys:
                return True
            if _contains_secret_material(value):
                return True
    elif isinstance(payload, (list, tuple)):
        return any(_contains_secret_material(item) for item in payload)
    return False


def _json(payload: dict[str, Any]) -> str:
    return canonical_json(payload)


def _sqlstate(exc: DBAPIError) -> str:
    return str(getattr(exc.orig, "sqlstate", "") or getattr(exc.orig, "pgcode", ""))


__all__ = [
    "AuditCapacityError",
    "AuditPersistenceReceipt",
    "ActiveSnapshotRefReceipt",
    "CapacityBackpressureError",
    "CapacityReservationReceipt",
    "CrossTenantHitReceipt",
    "CutoverActivationReceipt",
    "DeliveryWatermarkReceipt",
    "FencingRejectedError",
    "FencingToken",
    "IdempotencyClaimReceipt",
    "InboxMessageRecord",
    "InboxReceipt",
    "InfrastructureConflictError",
    "InfrastructureRepository",
    "InfrastructureUnitOfWork",
    "ObjectManifestRecord",
    "OutboxBacklogReceipt",
    "OutboxEventRecord",
    "OutboxFailureReceipt",
    "OutboxReplayReceipt",
    "RecoverySetReceipt",
    "RecoveryWatermarkReceipt",
    "SecretLeaseReceipt",
    "SecretVersionReceipt",
    "TransactionRetryReceipt",
    "create_foundation_engine",
    "run_transaction_with_retry",
]
