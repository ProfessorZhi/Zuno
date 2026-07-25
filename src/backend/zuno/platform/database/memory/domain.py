from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, Engine, text

from zuno.platform.contracts import canonical_json, canonical_sha256


class MemoryGovernanceConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class MemoryVersionInput:
    memory_version_id: str
    tenant_id: str
    workspace_id: str
    memory_scope_ref: str
    memory_kind: str
    version_no: int
    content_ref: str
    source_refs: tuple[str, ...]
    confidence: float
    content_payload: dict[str, Any]
    status: str = "APPROVED"


@dataclass(frozen=True, slots=True)
class ContextPackInput:
    context_pack_id: str
    tenant_id: str
    workspace_id: str
    run_id: str
    step_run_id: str
    memory_version_id: str
    budget_tokens: int
    selection_payload: dict[str, Any]
    compression_payload: dict[str, Any]
    trace_payload: dict[str, Any]
    state: str = "PREPARED"


class MemoryUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "MemoryRepository":
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        return MemoryRepository(self._connection)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            self._connection.close()


class MemoryRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def publish_memory_version(self, version: MemoryVersionInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO memory_versions (
                    memory_version_id, tenant_id, workspace_id, memory_scope_ref,
                    memory_kind, version_no, content_ref, source_refs, confidence,
                    status, generation, content_hash
                )
                VALUES (
                    :memory_version_id, :tenant_id, :workspace_id, :memory_scope_ref,
                    :memory_kind, :version_no, :content_ref, CAST(:source_refs AS jsonb),
                    :confidence, :status, 1, :content_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "memory_version_id": version.memory_version_id,
                "tenant_id": version.tenant_id,
                "workspace_id": version.workspace_id,
                "memory_scope_ref": version.memory_scope_ref,
                "memory_kind": version.memory_kind,
                "version_no": version.version_no,
                "content_ref": version.content_ref,
                "source_refs": canonical_json(list(version.source_refs)),
                "confidence": version.confidence,
                "status": version.status,
                "content_hash": canonical_sha256(version.content_payload),
            },
        )

    def activate_memory_version(
        self,
        *,
        memory_version_id: str,
        expected_generation: int,
        snapshot_payload: dict[str, Any],
        serving_watermark_ref: str,
    ) -> None:
        status = self.connection.execute(
            text(
                """
                SELECT status
                FROM memory_versions
                WHERE memory_version_id = :memory_version_id
                FOR UPDATE
                """
            ),
            {"memory_version_id": memory_version_id},
        ).scalar_one()
        if status not in {"APPROVED", "ACTIVE"}:
            raise MemoryGovernanceConflict("only approved memory version can activate")
        snapshot_id = f"memory-snapshot:{memory_version_id}"
        self.connection.execute(
            text(
                """
                INSERT INTO memory_snapshots (
                    snapshot_id, tenant_id, workspace_id, memory_version_id,
                    snapshot_hash, serving_watermark_ref
                )
                SELECT
                    :snapshot_id, tenant_id, workspace_id, memory_version_id,
                    :snapshot_hash, :serving_watermark_ref
                FROM memory_versions
                WHERE memory_version_id = :memory_version_id
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "snapshot_id": snapshot_id,
                "memory_version_id": memory_version_id,
                "snapshot_hash": canonical_sha256(snapshot_payload),
                "serving_watermark_ref": serving_watermark_ref,
            },
        )
        result = self.connection.execute(
            text(
                """
                UPDATE memory_versions
                SET status = 'ACTIVE',
                    generation = :committed_generation,
                    current_snapshot_ref = :snapshot_id
                WHERE memory_version_id = :memory_version_id
                  AND generation = :expected_generation
                """
            ),
            {
                "memory_version_id": memory_version_id,
                "expected_generation": expected_generation,
                "committed_generation": expected_generation + 1,
                "snapshot_id": snapshot_id,
            },
        )
        if result.rowcount != 1:
            raise MemoryGovernanceConflict("memory activation CAS failed")

    def build_context_pack(
        self,
        *,
        pack: ContextPackInput,
    ) -> None:
        manifest_payload = {
            "context_pack_id": pack.context_pack_id,
            "memory_version_id": pack.memory_version_id,
            "selection_hash": canonical_sha256(pack.selection_payload),
            "compression_hash": canonical_sha256(pack.compression_payload),
            "trace_hash": canonical_sha256(pack.trace_payload),
            "budget_tokens": pack.budget_tokens,
            "state": pack.state,
        }
        self.connection.execute(
            text(
                """
                INSERT INTO context_pack_versions (
                    context_pack_id, tenant_id, workspace_id, run_id, step_run_id,
                    memory_version_id, budget_tokens, selection_hash,
                    compression_hash, trace_hash, state, generation
                )
                VALUES (
                    :context_pack_id, :tenant_id, :workspace_id, :run_id, :step_run_id,
                    :memory_version_id, :budget_tokens, :selection_hash,
                    :compression_hash, :trace_hash, :state, 1
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "context_pack_id": pack.context_pack_id,
                "tenant_id": pack.tenant_id,
                "workspace_id": pack.workspace_id,
                "run_id": pack.run_id,
                "step_run_id": pack.step_run_id,
                "memory_version_id": pack.memory_version_id,
                "budget_tokens": pack.budget_tokens,
                "selection_hash": canonical_sha256(pack.selection_payload),
                "compression_hash": canonical_sha256(pack.compression_payload),
                "trace_hash": canonical_sha256(pack.trace_payload),
                "state": pack.state,
            },
        )
        self.connection.execute(
            text(
                """
                INSERT INTO memory_manifest_snapshots (
                    manifest_snapshot_id, tenant_id, workspace_id, generation,
                    manifest_hash, snapshot_payload
                )
                VALUES (
                    :manifest_snapshot_id, :tenant_id, :workspace_id, :generation,
                    :manifest_hash, CAST(:snapshot_payload AS jsonb)
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "manifest_snapshot_id": f"memory-manifest:{pack.context_pack_id}",
                "tenant_id": pack.tenant_id,
                "workspace_id": pack.workspace_id,
                "generation": 1,
                "manifest_hash": canonical_sha256(manifest_payload),
                "snapshot_payload": canonical_json(manifest_payload),
            },
        )

    def request_delete(
        self,
        *,
        deletion_request_id: str,
        tenant_id: str,
        workspace_id: str,
        memory_scope_ref: str,
        requested_by: str,
        reason: str,
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO memory_deletion_requests (
                    deletion_request_id, tenant_id, workspace_id, memory_scope_ref,
                    requested_by, reason, state, generation
                )
                VALUES (
                    :deletion_request_id, :tenant_id, :workspace_id, :memory_scope_ref,
                    :requested_by, :reason, 'REQUESTED', 1
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "deletion_request_id": deletion_request_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "memory_scope_ref": memory_scope_ref,
                "requested_by": requested_by,
                "reason": reason,
            },
        )

    def complete_delete(
        self,
        *,
        deletion_receipt_id: str,
        deletion_request_id: str,
        tenant_id: str,
        workspace_id: str,
        deleted_payload: dict[str, Any],
        verification_payload: dict[str, Any],
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO memory_deletion_receipts (
                    deletion_receipt_id, deletion_request_id, tenant_id, workspace_id,
                    deleted_hash, verification_hash
                )
                VALUES (
                    :deletion_receipt_id, :deletion_request_id, :tenant_id, :workspace_id,
                    :deleted_hash, :verification_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "deletion_receipt_id": deletion_receipt_id,
                "deletion_request_id": deletion_request_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "deleted_hash": canonical_sha256(deleted_payload),
                "verification_hash": canonical_sha256(verification_payload),
            },
        )


__all__ = [
    "ContextPackInput",
    "MemoryGovernanceConflict",
    "MemoryRepository",
    "MemoryUnitOfWork",
    "MemoryVersionInput",
]
