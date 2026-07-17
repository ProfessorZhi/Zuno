from __future__ import annotations

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

    def __enter__(self) -> InfrastructureRepository:
        if self.isolation_level is None:
            self._context = self.engine.begin()
            self.connection = self._context.__enter__()
            self._transaction = None
        else:
            self._context = self.engine.connect()
            self.connection = self._context.__enter__().execution_options(isolation_level=self.isolation_level)
            self._transaction = self.connection.begin()
        if self.tenant_id is not None:
            self.connection.execute(text("SELECT set_config('app.tenant_id', :tenant_id, true)"), {"tenant_id": self.tenant_id})
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

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._transaction is not None:
            try:
                self._transaction.__exit__(exc_type, exc, tb)
            finally:
                self._context.__exit__(exc_type, exc, tb)
            return
        self._context.__exit__(exc_type, exc, tb)


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
        tenant_id: str | None = None,
        ordering_key: str | None = None,
    ) -> str:
        event_id = f"outbox:{uuid4()}"
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
                WHERE event_id = :event_id AND status = 'pending'
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
                SET status = 'pending', claim_owner = NULL, claimed_at = NULL
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
                SET status = 'pending', claim_owner = NULL, claimed_at = NULL
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
                SET status = 'published', published_at = now()
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
                       claim_owner, tenant_id, ordering_key, ordering_sequence
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
                      AND expires_at < now()
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

    def complete_idempotency(self, *, scope: str, key: str, generation: int, result_ref: str) -> None:
        tenant_id = self.current_tenant_id()
        result = self.connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET status = 'completed', result_ref = :result_ref, completed_at = now()
                WHERE tenant_id = :tenant_id
                  AND scope = :scope
                  AND idempotency_key = :key
                  AND generation = :generation
                  AND status = 'in_progress'
                """
            ),
            {"tenant_id": tenant_id, "scope": scope, "key": key, "generation": generation, "result_ref": result_ref},
        )
        if result.rowcount != 1:
            raise FencingRejectedError("idempotency generation is stale")

    def acquire_lease(self, *, resource_id: str, owner_id: str, ttl_seconds: int = 30) -> FencingToken:
        lease_id = f"lease:{uuid4()}"
        expires_at = utcnow() + timedelta(seconds=ttl_seconds)
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                VALUES (:resource_id, :owner_id, :lease_id, 1, :expires_at)
                ON CONFLICT (resource_id) DO UPDATE
                SET owner_id = EXCLUDED.owner_id,
                    lease_id = EXCLUDED.lease_id,
                    epoch = infra_worker_leases.epoch + 1,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = now()
                WHERE infra_worker_leases.expires_at < now()
                   OR infra_worker_leases.owner_id = EXCLUDED.owner_id
                RETURNING resource_id, owner_id, lease_id, epoch, expires_at
                """
            ),
            {
                "resource_id": resource_id,
                "owner_id": owner_id,
                "lease_id": lease_id,
                "expires_at": expires_at,
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

    def assert_fence(self, token: FencingToken) -> None:
        row = self.connection.execute(
            text(
                """
                SELECT epoch, lease_id, expires_at
                FROM infra_worker_leases
                WHERE resource_id = :resource_id AND owner_id = :owner_id
                """
            ),
            {"resource_id": token.resource_id, "owner_id": token.owner_id},
        ).first()
        if row is None or int(row.epoch) != token.epoch or row.lease_id != token.lease_id or row.expires_at < utcnow():
            raise FencingRejectedError("fencing token is stale")

    def renew_lease(self, token: FencingToken, *, ttl_seconds: int = 30) -> FencingToken:
        expires_at = utcnow() + timedelta(seconds=ttl_seconds)
        row = self.connection.execute(
            text(
                """
                UPDATE infra_worker_leases
                SET expires_at = :expires_at, updated_at = now()
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
                "expires_at": expires_at,
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
        self.connection.execute(
            text(
                """
                INSERT INTO infra_object_manifests(object_ref, owner, content_hash, size_bytes, visibility)
                VALUES (:object_ref, :owner, :content_hash, :size_bytes, :visibility)
                ON CONFLICT (object_ref) DO UPDATE
                SET conflict_hash = CASE
                    WHEN infra_object_manifests.content_hash = EXCLUDED.content_hash
                    THEN infra_object_manifests.conflict_hash
                    ELSE EXCLUDED.content_hash
                END,
                visibility = CASE
                    WHEN infra_object_manifests.content_hash = EXCLUDED.content_hash
                    THEN EXCLUDED.visibility
                    ELSE 'quarantined'
                END
                """
            ),
            {
                "object_ref": object_ref,
                "owner": owner,
                "content_hash": content_hash,
                "size_bytes": len(content),
                "visibility": visibility,
            },
        )
        row = self.connection.execute(
            text("SELECT visibility FROM infra_object_manifests WHERE object_ref = :object_ref"),
            {"object_ref": object_ref},
        ).one()
        if row.visibility == "quarantined":
            raise InfrastructureConflictError("object ref reused with different content hash")
        return content_hash

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


def _json(payload: dict[str, Any]) -> str:
    return canonical_json(payload)


def _sqlstate(exc: DBAPIError) -> str:
    return str(getattr(exc.orig, "sqlstate", "") or getattr(exc.orig, "pgcode", ""))


__all__ = [
    "DeliveryWatermarkReceipt",
    "FencingRejectedError",
    "FencingToken",
    "IdempotencyClaimReceipt",
    "InboxMessageRecord",
    "InboxReceipt",
    "InfrastructureConflictError",
    "InfrastructureRepository",
    "InfrastructureUnitOfWork",
    "OutboxEventRecord",
    "TransactionRetryReceipt",
    "create_foundation_engine",
    "run_transaction_with_retry",
]
