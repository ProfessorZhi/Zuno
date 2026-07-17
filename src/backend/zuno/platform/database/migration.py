from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Engine, text
from sqlalchemy.engine import Row

from zuno.platform.contracts import canonical_json, canonical_sha256
from zuno.platform.database.foundation import FencingRejectedError, InfrastructureConflictError


@dataclass(frozen=True, slots=True)
class BackfillSpec:
    backfill_id: str
    module_owner: str
    source_ref: str
    target_ref: str
    transform_version: str
    chunk_size: int
    forward_fix_of: str | None = None


@dataclass(frozen=True, slots=True)
class BackfillReceipt:
    backfill_id: str
    state: str
    generation: int
    lease_owner: str | None
    lease_expires_at: datetime | None
    cursor: dict[str, Any]
    cursor_hash: str
    source_watermark: str | None
    processed_count: int
    conflict_count: int
    verification_hash: str | None
    error_code: str | None
    forward_fix_of: str | None


@dataclass(frozen=True, slots=True)
class BackfillClaimReceipt:
    backfill: BackfillReceipt
    acquired: bool


@dataclass(frozen=True, slots=True)
class BackfillChunkReceipt:
    backfill_id: str
    chunk_id: str
    first_applied: bool
    end_cursor_hash: str
    processed_count: int
    source_watermark: str | None


class PostgresBackfillController:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def declare(self, spec: BackfillSpec) -> BackfillReceipt:
        self._validate_spec(spec)
        with self.engine.begin() as connection:
            existing = connection.execute(
                text("SELECT * FROM infra_migration_backfills WHERE backfill_id = :backfill_id FOR UPDATE"),
                {"backfill_id": spec.backfill_id},
            ).first()
            if existing is not None:
                self._assert_matching_spec(existing, spec)
                return self._receipt(existing)

            if spec.forward_fix_of is not None:
                prior = connection.execute(
                    text(
                        """
                        SELECT state
                        FROM infra_migration_backfills
                        WHERE backfill_id = :backfill_id
                        FOR UPDATE
                        """
                    ),
                    {"backfill_id": spec.forward_fix_of},
                ).first()
                if prior is None or prior.state != "failed":
                    raise InfrastructureConflictError("forward-fix source must be a failed backfill")
                connection.execute(
                    text(
                        """
                        UPDATE infra_migration_backfills
                        SET state = 'superseded', updated_at = now()
                        WHERE backfill_id = :backfill_id AND state = 'failed'
                        """
                    ),
                    {"backfill_id": spec.forward_fix_of},
                )

            row = connection.execute(
                text(
                    """
                    INSERT INTO infra_migration_backfills(
                        backfill_id, module_owner, source_ref, target_ref,
                        transform_version, state, cursor, cursor_hash,
                        chunk_size, forward_fix_of
                    ) VALUES (
                        :backfill_id, :module_owner, :source_ref, :target_ref,
                        :transform_version, 'declared', CAST(:cursor AS jsonb),
                        :cursor_hash, :chunk_size, :forward_fix_of
                    )
                    RETURNING *
                    """
                ),
                {
                    "backfill_id": spec.backfill_id,
                    "module_owner": spec.module_owner,
                    "source_ref": spec.source_ref,
                    "target_ref": spec.target_ref,
                    "transform_version": spec.transform_version,
                    "cursor": "{}",
                    "cursor_hash": canonical_sha256({}),
                    "chunk_size": spec.chunk_size,
                    "forward_fix_of": spec.forward_fix_of,
                },
            ).one()
            return self._receipt(row)

    def claim(self, *, backfill_id: str, owner: str, lease_seconds: float) -> BackfillClaimReceipt:
        normalized_owner = self._required_text("owner", owner, 128)
        self._validate_lease_seconds(lease_seconds)
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE infra_migration_backfills
                    SET state = 'running',
                        generation = generation + 1,
                        lease_owner = :owner,
                        lease_expires_at = now() + (:lease_seconds * interval '1 second'),
                        error_code = NULL,
                        updated_at = now()
                    WHERE backfill_id = :backfill_id
                      AND (
                        state IN ('declared', 'paused')
                        OR (state = 'running' AND lease_expires_at <= now())
                      )
                    RETURNING *
                    """
                ),
                {
                    "backfill_id": backfill_id,
                    "owner": normalized_owner,
                    "lease_seconds": lease_seconds,
                },
            ).first()
            if row is not None:
                return BackfillClaimReceipt(backfill=self._receipt(row), acquired=True)
            current = connection.execute(
                text("SELECT * FROM infra_migration_backfills WHERE backfill_id = :backfill_id"),
                {"backfill_id": backfill_id},
            ).first()
            if current is None:
                raise InfrastructureConflictError("backfill is not declared")
            return BackfillClaimReceipt(backfill=self._receipt(current), acquired=False)

    def renew(
        self,
        *,
        backfill_id: str,
        owner: str,
        generation: int,
        lease_seconds: float,
    ) -> BackfillReceipt:
        self._validate_lease_seconds(lease_seconds)
        normalized_owner = self._required_text("owner", owner, 128)
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE infra_migration_backfills
                    SET lease_expires_at = now() + (:lease_seconds * interval '1 second'),
                        updated_at = now()
                    WHERE backfill_id = :backfill_id
                      AND state = 'running'
                      AND lease_owner = :owner
                      AND generation = :generation
                      AND lease_expires_at > now()
                    RETURNING *
                    """
                ),
                {
                    "backfill_id": backfill_id,
                    "owner": normalized_owner,
                    "generation": generation,
                    "lease_seconds": lease_seconds,
                },
            ).first()
            if row is None:
                raise FencingRejectedError("backfill lease is not held by this generation")
            return self._receipt(row)

    def apply_chunk(
        self,
        *,
        backfill_id: str,
        owner: str,
        generation: int,
        chunk_id: str,
        start_cursor: dict[str, Any],
        end_cursor: dict[str, Any],
        payload_hash: str,
        row_count: int,
        source_watermark: str | None,
    ) -> BackfillChunkReceipt:
        normalized_chunk_id = self._required_text("chunk_id", chunk_id, 160)
        normalized_payload_hash = self._hash("payload_hash", payload_hash)
        normalized_owner = self._required_text("owner", owner, 128)
        normalized_watermark = (
            None
            if source_watermark is None
            else self._required_text("source_watermark", source_watermark, 256)
        )
        if row_count < 0:
            raise ValueError("row_count must not be negative")
        start_hash = canonical_sha256(start_cursor)
        end_hash = canonical_sha256(end_cursor)
        conflict: str | None = None
        receipt: BackfillChunkReceipt | None = None
        with self.engine.begin() as connection:
            backfill = self._lock_held_backfill(
                connection,
                backfill_id=backfill_id,
                owner=normalized_owner,
                generation=generation,
            )
            existing = connection.execute(
                text(
                    """
                    SELECT start_cursor_hash, end_cursor_hash, payload_hash,
                           source_watermark, row_count
                    FROM infra_migration_backfill_chunks
                    WHERE backfill_id = :backfill_id AND chunk_id = :chunk_id
                    """
                ),
                {"backfill_id": backfill_id, "chunk_id": normalized_chunk_id},
            ).first()
            if existing is not None:
                if (
                    existing.start_cursor_hash != start_hash
                    or existing.end_cursor_hash != end_hash
                    or existing.payload_hash != normalized_payload_hash
                    or existing.source_watermark != normalized_watermark
                    or int(existing.row_count) != row_count
                ):
                    conflict = "backfill chunk id was reused with different content"
                    self._increment_conflict(connection, backfill_id)
                else:
                    receipt = BackfillChunkReceipt(
                        backfill_id=backfill_id,
                        chunk_id=normalized_chunk_id,
                        first_applied=False,
                        end_cursor_hash=end_hash,
                        processed_count=int(backfill.processed_count),
                        source_watermark=backfill.source_watermark,
                    )
            elif backfill.cursor_hash != start_hash:
                conflict = "backfill chunk start cursor does not match the durable cursor"
                self._increment_conflict(connection, backfill_id)
            else:
                connection.execute(
                    text(
                        """
                        INSERT INTO infra_migration_backfill_chunks(
                            backfill_id, chunk_id, start_cursor, end_cursor,
                            start_cursor_hash, end_cursor_hash, payload_hash,
                            source_watermark, row_count, applied_generation
                        ) VALUES (
                            :backfill_id, :chunk_id, CAST(:start_cursor AS jsonb),
                            CAST(:end_cursor AS jsonb), :start_cursor_hash,
                            :end_cursor_hash, :payload_hash, :source_watermark,
                            :row_count, :generation
                        )
                        """
                    ),
                    {
                        "backfill_id": backfill_id,
                        "chunk_id": normalized_chunk_id,
                        "start_cursor": self._canonical_json(start_cursor),
                        "end_cursor": self._canonical_json(end_cursor),
                        "start_cursor_hash": start_hash,
                        "end_cursor_hash": end_hash,
                        "payload_hash": normalized_payload_hash,
                        "source_watermark": normalized_watermark,
                        "row_count": row_count,
                        "generation": generation,
                    },
                )
                updated = connection.execute(
                    text(
                        """
                        UPDATE infra_migration_backfills
                        SET cursor = CAST(:end_cursor AS jsonb),
                            cursor_hash = :end_cursor_hash,
                            source_watermark = :source_watermark,
                            processed_count = processed_count + :row_count,
                            updated_at = now()
                        WHERE backfill_id = :backfill_id
                          AND state = 'running'
                          AND lease_owner = :owner
                          AND generation = :generation
                        RETURNING processed_count, source_watermark
                        """
                    ),
                    {
                        "backfill_id": backfill_id,
                        "owner": normalized_owner,
                        "generation": generation,
                        "end_cursor": self._canonical_json(end_cursor),
                        "end_cursor_hash": end_hash,
                        "source_watermark": normalized_watermark,
                        "row_count": row_count,
                    },
                ).one()
                receipt = BackfillChunkReceipt(
                    backfill_id=backfill_id,
                    chunk_id=normalized_chunk_id,
                    first_applied=True,
                    end_cursor_hash=end_hash,
                    processed_count=int(updated.processed_count),
                    source_watermark=updated.source_watermark,
                )
        if conflict is not None:
            raise InfrastructureConflictError(conflict)
        if receipt is None:
            raise RuntimeError("backfill chunk transaction produced no receipt")
        return receipt

    def pause(self, *, backfill_id: str, owner: str, generation: int) -> BackfillReceipt:
        return self._release_with_state(
            backfill_id=backfill_id,
            owner=owner,
            generation=generation,
            state="paused",
        )

    def fail(
        self,
        *,
        backfill_id: str,
        owner: str,
        generation: int,
        error_code: str,
    ) -> BackfillReceipt:
        normalized_error = self._required_text("error_code", error_code, 128)
        normalized_owner = self._required_text("owner", owner, 128)
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE infra_migration_backfills
                    SET state = 'failed', error_code = :error_code,
                        lease_owner = NULL, lease_expires_at = NULL, updated_at = now()
                    WHERE backfill_id = :backfill_id
                      AND state = 'running'
                      AND lease_owner = :owner
                      AND generation = :generation
                      AND lease_expires_at > now()
                    RETURNING *
                    """
                ),
                {
                    "backfill_id": backfill_id,
                    "owner": normalized_owner,
                    "generation": generation,
                    "error_code": normalized_error,
                },
            ).first()
            if row is None:
                raise FencingRejectedError("backfill lease is not held by this generation")
            return self._receipt(row)

    def complete(
        self,
        *,
        backfill_id: str,
        owner: str,
        generation: int,
        verification_hash: str,
    ) -> BackfillReceipt:
        normalized_hash = self._hash("verification_hash", verification_hash)
        normalized_owner = self._required_text("owner", owner, 128)
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE infra_migration_backfills
                    SET state = 'completed', verification_hash = :verification_hash,
                        completed_at = now(), lease_owner = NULL,
                        lease_expires_at = NULL, updated_at = now()
                    WHERE backfill_id = :backfill_id
                      AND state = 'running'
                      AND lease_owner = :owner
                      AND generation = :generation
                      AND lease_expires_at > now()
                    RETURNING *
                    """
                ),
                {
                    "backfill_id": backfill_id,
                    "owner": normalized_owner,
                    "generation": generation,
                    "verification_hash": normalized_hash,
                },
            ).first()
            if row is None:
                raise FencingRejectedError("backfill lease is not held by this generation")
            return self._receipt(row)

    def get(self, backfill_id: str) -> BackfillReceipt:
        with self.engine.connect() as connection:
            row = connection.execute(
                text("SELECT * FROM infra_migration_backfills WHERE backfill_id = :backfill_id"),
                {"backfill_id": backfill_id},
            ).first()
        if row is None:
            raise InfrastructureConflictError("backfill is not declared")
        return self._receipt(row)

    def _release_with_state(
        self,
        *,
        backfill_id: str,
        owner: str,
        generation: int,
        state: str,
    ) -> BackfillReceipt:
        normalized_owner = self._required_text("owner", owner, 128)
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    UPDATE infra_migration_backfills
                    SET state = :state, lease_owner = NULL,
                        lease_expires_at = NULL, updated_at = now()
                    WHERE backfill_id = :backfill_id
                      AND state = 'running'
                      AND lease_owner = :owner
                      AND generation = :generation
                      AND lease_expires_at > now()
                    RETURNING *
                    """
                ),
                {
                    "backfill_id": backfill_id,
                    "owner": normalized_owner,
                    "generation": generation,
                    "state": state,
                },
            ).first()
            if row is None:
                raise FencingRejectedError("backfill lease is not held by this generation")
            return self._receipt(row)

    @staticmethod
    def _lock_held_backfill(connection, *, backfill_id: str, owner: str, generation: int) -> Row[Any]:
        row = connection.execute(
            text(
                """
                SELECT *
                FROM infra_migration_backfills
                WHERE backfill_id = :backfill_id
                FOR UPDATE
                """
            ),
            {"backfill_id": backfill_id},
        ).first()
        if (
            row is None
            or row.state != "running"
            or row.lease_owner != owner
            or int(row.generation) != generation
            or connection.execute(text("SELECT :expires_at > now()"), {"expires_at": row.lease_expires_at}).scalar_one()
            is not True
        ):
            raise FencingRejectedError("backfill lease is not held by this generation")
        return row

    @staticmethod
    def _increment_conflict(connection, backfill_id: str) -> None:
        connection.execute(
            text(
                """
                UPDATE infra_migration_backfills
                SET conflict_count = conflict_count + 1, updated_at = now()
                WHERE backfill_id = :backfill_id
                """
            ),
            {"backfill_id": backfill_id},
        )

    @staticmethod
    def _receipt(row: Row[Any]) -> BackfillReceipt:
        return BackfillReceipt(
            backfill_id=str(row.backfill_id),
            state=str(row.state),
            generation=int(row.generation),
            lease_owner=None if row.lease_owner is None else str(row.lease_owner),
            lease_expires_at=row.lease_expires_at,
            cursor=dict(row.cursor),
            cursor_hash=str(row.cursor_hash),
            source_watermark=None if row.source_watermark is None else str(row.source_watermark),
            processed_count=int(row.processed_count),
            conflict_count=int(row.conflict_count),
            verification_hash=None if row.verification_hash is None else str(row.verification_hash),
            error_code=None if row.error_code is None else str(row.error_code),
            forward_fix_of=None if row.forward_fix_of is None else str(row.forward_fix_of),
        )

    @classmethod
    def _validate_spec(cls, spec: BackfillSpec) -> None:
        cls._required_text("backfill_id", spec.backfill_id, 160)
        cls._required_text("module_owner", spec.module_owner, 128)
        cls._required_text("source_ref", spec.source_ref, 512)
        cls._required_text("target_ref", spec.target_ref, 512)
        cls._required_text("transform_version", spec.transform_version, 128)
        if spec.forward_fix_of is not None:
            cls._required_text("forward_fix_of", spec.forward_fix_of, 160)
            if spec.forward_fix_of == spec.backfill_id:
                raise ValueError("a backfill cannot be its own forward-fix source")
        if spec.chunk_size < 1:
            raise ValueError("chunk_size must be positive")

    @staticmethod
    def _assert_matching_spec(row: Row[Any], spec: BackfillSpec) -> None:
        actual = (
            str(row.module_owner),
            str(row.source_ref),
            str(row.target_ref),
            str(row.transform_version),
            int(row.chunk_size),
            None if row.forward_fix_of is None else str(row.forward_fix_of),
        )
        expected = (
            spec.module_owner,
            spec.source_ref,
            spec.target_ref,
            spec.transform_version,
            spec.chunk_size,
            spec.forward_fix_of,
        )
        if actual != expected:
            raise InfrastructureConflictError("backfill id was reused with a different immutable specification")

    @staticmethod
    def _validate_lease_seconds(value: float) -> None:
        if not math.isfinite(value) or value <= 0:
            raise ValueError("lease_seconds must be finite and positive")

    @staticmethod
    def _required_text(name: str, value: str, max_length: int) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > max_length:
            raise ValueError(f"{name} must contain between 1 and {max_length} characters")
        return normalized

    @staticmethod
    def _hash(name: str, value: str) -> str:
        normalized = value.strip().lower()
        if len(normalized) != 64 or any(character not in "0123456789abcdef" for character in normalized):
            raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")
        return normalized

    @staticmethod
    def _canonical_json(value: dict[str, Any]) -> str:
        return canonical_json(value)


__all__ = [
    "BackfillChunkReceipt",
    "BackfillClaimReceipt",
    "BackfillReceipt",
    "BackfillSpec",
    "PostgresBackfillController",
]
