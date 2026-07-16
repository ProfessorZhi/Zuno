from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import Connection

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


@dataclass(frozen=True, slots=True)
class IdempotencyClaimReceipt:
    status: str
    generation: int
    result_ref: str
    owner: str
    acquired: bool


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
    ) -> None:
        self.engine = engine
        self.tenant_id = tenant_id
        self.statement_timeout_ms = statement_timeout_ms
        self.lock_timeout_ms = lock_timeout_ms

    def __enter__(self) -> InfrastructureRepository:
        self._context = self.engine.begin()
        self.connection = self._context.__enter__()
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
        self._context.__exit__(exc_type, exc, tb)


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
    ) -> str:
        event_id = f"outbox:{uuid4()}"
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO infra_outbox_events(
                    event_id, aggregate_id, topic, payload, payload_hash, idempotency_key, status
                ) VALUES (
                    :event_id, :aggregate_id, :topic, CAST(:payload AS jsonb), :payload_hash,
                    :idempotency_key, 'pending'
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
                SELECT event_id, aggregate_id, topic, payload, payload_hash, idempotency_key, claim_owner
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
        )

    def record_inbox(self, *, consumer: str, message_id: str, payload: dict[str, Any]) -> str:
        payload_hash = canonical_sha256(payload)
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_inbox_messages(consumer, message_id, payload_hash, payload, status)
                VALUES (:consumer, :message_id, :payload_hash, CAST(:payload AS jsonb), 'received')
                ON CONFLICT (consumer, message_id) DO UPDATE
                SET conflict_hash = CASE
                    WHEN infra_inbox_messages.payload_hash = EXCLUDED.payload_hash
                    THEN infra_inbox_messages.conflict_hash
                    ELSE EXCLUDED.payload_hash
                END,
                status = CASE
                    WHEN infra_inbox_messages.payload_hash = EXCLUDED.payload_hash
                    THEN infra_inbox_messages.status
                    ELSE 'quarantined'
                END
                RETURNING status, payload_hash, conflict_hash
                """
            ),
            {
                "consumer": consumer,
                "message_id": message_id,
                "payload_hash": payload_hash,
                "payload": _json(payload),
            },
        ).one()
        if row.status == "quarantined":
            raise InfrastructureConflictError("same inbox message id received with a different payload hash")
        return str(row.payload_hash)

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
        self.connection.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:scope || ':' || :key, 0))"),
            {"scope": scope, "key": key},
        )
        row = self.connection.execute(
            text(
                """
                INSERT INTO infra_idempotency_claims(
                    scope, idempotency_key, owner, request_hash, status, generation, expires_at
                )
                VALUES (:scope, :key, :owner, :request_hash, 'in_progress', 1, :expires_at)
                ON CONFLICT (scope, idempotency_key) DO NOTHING
                RETURNING owner, request_hash, status, generation, result_ref, true AS acquired
                """
            ),
            {
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
                    WHERE scope = :scope
                      AND idempotency_key = :key
                      AND request_hash = :request_hash
                      AND status in ('in_progress','expired')
                      AND expires_at < now()
                    RETURNING owner, request_hash, status, generation, result_ref, true AS acquired
                    """
                ),
                {
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
                    WHERE scope = :scope AND idempotency_key = :key
                    """
                ),
                {"scope": scope, "key": key},
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
        row = self.connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET expires_at = :expires_at
                WHERE scope = :scope
                  AND idempotency_key = :key
                  AND owner = :owner
                  AND generation = :generation
                  AND status = 'in_progress'
                  AND expires_at >= now()
                RETURNING expires_at
                """
            ),
            {
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
        result = self.connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET status = 'completed', result_ref = :result_ref, completed_at = now()
                WHERE scope = :scope
                  AND idempotency_key = :key
                  AND generation = :generation
                  AND status = 'in_progress'
                """
            ),
            {"scope": scope, "key": key, "generation": generation, "result_ref": result_ref},
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


__all__ = [
    "FencingRejectedError",
    "FencingToken",
    "IdempotencyClaimReceipt",
    "InfrastructureConflictError",
    "InfrastructureRepository",
    "InfrastructureUnitOfWork",
    "OutboxEventRecord",
    "create_foundation_engine",
]
