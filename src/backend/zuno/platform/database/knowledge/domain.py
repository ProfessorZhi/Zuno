from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, Engine, text

from zuno.platform.contracts import canonical_sha256


class KnowledgeCutoverConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class KnowledgeVersionDraft:
    knowledge_version_id: str
    tenant_id: str
    workspace_id: str
    knowledge_space_id: str
    version_no: int
    document_set: dict[str, Any]
    source_span_manifest: dict[str, Any]
    index_spec: dict[str, Any]
    security_epoch_ref: str


class KnowledgeUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "KnowledgeRepository":
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        return KnowledgeRepository(self._connection)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            self._connection.close()


class KnowledgeRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def active_snapshot_id(
        self,
        *,
        tenant_id: str,
        knowledge_space_id: str,
    ) -> str | None:
        row = self.connection.execute(
            text(
                """
                SELECT s.snapshot_id
                FROM knowledge_snapshots s
                JOIN knowledge_domain_versions v
                  ON v.knowledge_version_id = s.knowledge_version_id
                WHERE s.tenant_id = :tenant_id
                  AND v.knowledge_space_id = :knowledge_space_id
                  AND v.status = 'ACTIVE'
                ORDER BY s.created_at DESC, s.snapshot_id DESC
                LIMIT 1
                """
            ),
            {
                "tenant_id": tenant_id,
                "knowledge_space_id": knowledge_space_id,
            },
        ).first()
        return None if row is None else str(row.snapshot_id)

    def next_version_no(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_space_id: str,
    ) -> int:
        value = self.connection.execute(
            text(
                """
                SELECT coalesce(max(version_no), 0) + 1
                FROM knowledge_domain_versions
                WHERE tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND knowledge_space_id = :knowledge_space_id
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "knowledge_space_id": knowledge_space_id,
            },
        ).scalar_one()
        return int(value)

    def next_cutover_expected_generation(
        self,
        *,
        tenant_id: str,
        knowledge_space_id: str,
    ) -> int:
        value = self.connection.execute(
            text(
                """
                SELECT coalesce(max(committed_generation), 1)
                FROM knowledge_cutover_decisions
                WHERE tenant_id = :tenant_id
                  AND knowledge_space_id = :knowledge_space_id
                """
            ),
            {
                "tenant_id": tenant_id,
                "knowledge_space_id": knowledge_space_id,
            },
        ).scalar_one()
        return int(value)

    def create_version(self, draft: KnowledgeVersionDraft) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_domain_versions (
                    knowledge_version_id, tenant_id, workspace_id, knowledge_space_id,
                    version_no, document_set_hash, source_span_manifest_hash,
                    index_spec_hash, security_epoch_ref, status, generation
                )
                VALUES (
                    :knowledge_version_id, :tenant_id, :workspace_id, :knowledge_space_id,
                    :version_no, :document_set_hash, :source_span_manifest_hash,
                    :index_spec_hash, :security_epoch_ref, 'BUILDING', 1
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "knowledge_version_id": draft.knowledge_version_id,
                "tenant_id": draft.tenant_id,
                "workspace_id": draft.workspace_id,
                "knowledge_space_id": draft.knowledge_space_id,
                "version_no": draft.version_no,
                "document_set_hash": canonical_sha256(draft.document_set),
                "source_span_manifest_hash": canonical_sha256(draft.source_span_manifest),
                "index_spec_hash": canonical_sha256(draft.index_spec),
                "security_epoch_ref": draft.security_epoch_ref,
            },
        )

    def append_chunk(
        self,
        *,
        chunk_id: str,
        tenant_id: str,
        knowledge_version_id: str,
        document_version_id: str,
        source_span_ref: str,
        chunk_payload: dict[str, Any],
        acl_ref: str,
        authority_ref: str,
    ) -> None:
        if not source_span_ref:
            raise ValueError("Knowledge strict chunks require SourceSpan lineage")
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_chunks (
                    chunk_id, tenant_id, knowledge_version_id, document_version_id,
                    source_span_ref, chunk_hash, acl_ref, authority_ref
                )
                VALUES (
                    :chunk_id, :tenant_id, :knowledge_version_id, :document_version_id,
                    :source_span_ref, :chunk_hash, :acl_ref, :authority_ref
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "chunk_id": chunk_id,
                "tenant_id": tenant_id,
                "knowledge_version_id": knowledge_version_id,
                "document_version_id": document_version_id,
                "source_span_ref": source_span_ref,
                "chunk_hash": canonical_sha256(chunk_payload),
                "acl_ref": acl_ref,
                "authority_ref": authority_ref,
            },
        )

    def record_index_visibility(
        self,
        *,
        job_id: str,
        tenant_id: str,
        knowledge_version_id: str,
        index_kind: str,
        lease_ref: str,
        fencing_token: int,
        attempt_no: int,
        write_batch: dict[str, Any],
        visibility_receipt_ref: str,
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_index_build_jobs (
                    job_id, tenant_id, knowledge_version_id, index_kind, lease_ref,
                    fencing_token, attempt_no, status, write_batch_hash,
                    visibility_receipt_ref
                )
                VALUES (
                    :job_id, :tenant_id, :knowledge_version_id, :index_kind, :lease_ref,
                    :fencing_token, :attempt_no, 'VISIBLE', :write_batch_hash,
                    :visibility_receipt_ref
                )
                """
            ),
            {
                "job_id": job_id,
                "tenant_id": tenant_id,
                "knowledge_version_id": knowledge_version_id,
                "index_kind": index_kind,
                "lease_ref": lease_ref,
                "fencing_token": fencing_token,
                "attempt_no": attempt_no,
                "write_batch_hash": canonical_sha256(write_batch),
                "visibility_receipt_ref": visibility_receipt_ref,
            },
        )

    def mark_ready(self, *, knowledge_version_id: str) -> None:
        visible_count = self.connection.execute(
            text(
                """
                SELECT count(distinct index_kind)
                FROM knowledge_index_build_jobs
                WHERE knowledge_version_id = :knowledge_version_id
                  AND status = 'VISIBLE'
                """
            ),
            {"knowledge_version_id": knowledge_version_id},
        ).scalar_one()
        if int(visible_count) < 2:
            raise KnowledgeCutoverConflict("KnowledgeVersion needs visible BM25 and VECTOR indexes before READY")
        self.connection.execute(
            text(
                """
                UPDATE knowledge_domain_versions
                SET status = 'READY', generation = generation + 1
                WHERE knowledge_version_id = :knowledge_version_id
                  AND status in ('BUILDING','VERIFYING')
                """
            ),
            {"knowledge_version_id": knowledge_version_id},
        )

    def create_snapshot(
        self,
        *,
        snapshot_id: str,
        tenant_id: str,
        knowledge_version_id: str,
        snapshot_payload: dict[str, Any],
        serving_watermark_ref: str,
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_snapshots (
                    snapshot_id, tenant_id, knowledge_version_id,
                    snapshot_hash, serving_watermark_ref
                )
                VALUES (
                    :snapshot_id, :tenant_id, :knowledge_version_id,
                    :snapshot_hash, :serving_watermark_ref
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "snapshot_id": snapshot_id,
                "tenant_id": tenant_id,
                "knowledge_version_id": knowledge_version_id,
                "snapshot_hash": canonical_sha256(snapshot_payload),
                "serving_watermark_ref": serving_watermark_ref,
            },
        )

    def cutover(
        self,
        *,
        cutover_id: str,
        tenant_id: str,
        knowledge_space_id: str,
        to_version_id: str,
        expected_generation: int,
        decision_payload: dict[str, Any],
        from_version_id: str | None = None,
        rollback_of_cutover_id: str | None = None,
    ) -> None:
        status = self.connection.execute(
            text(
                """
                SELECT status
                FROM knowledge_domain_versions
                WHERE knowledge_version_id = :to_version_id
                FOR UPDATE
                """
            ),
            {"to_version_id": to_version_id},
        ).scalar_one()
        if status not in {"READY", "ACTIVE"}:
            raise KnowledgeCutoverConflict("Only READY KnowledgeVersion can cut over")
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_cutover_decisions (
                    cutover_id, tenant_id, knowledge_space_id, from_version_id,
                    to_version_id, expected_generation, committed_generation,
                    decision_hash, rollback_of_cutover_id
                )
                VALUES (
                    :cutover_id, :tenant_id, :knowledge_space_id, :from_version_id,
                    :to_version_id, :expected_generation, :committed_generation,
                    :decision_hash, :rollback_of_cutover_id
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "cutover_id": cutover_id,
                "tenant_id": tenant_id,
                "knowledge_space_id": knowledge_space_id,
                "from_version_id": from_version_id,
                "to_version_id": to_version_id,
                "expected_generation": expected_generation,
                "committed_generation": expected_generation + 1,
                "decision_hash": canonical_sha256(decision_payload),
                "rollback_of_cutover_id": rollback_of_cutover_id,
            },
        )
        self.connection.execute(
            text(
                """
                UPDATE knowledge_domain_versions
                SET status = 'SUPERSEDED'
                WHERE tenant_id = :tenant_id
                  AND knowledge_space_id = :knowledge_space_id
                  AND knowledge_version_id <> :to_version_id
                  AND status = 'ACTIVE'
                """
            ),
            {
                "tenant_id": tenant_id,
                "knowledge_space_id": knowledge_space_id,
                "to_version_id": to_version_id,
            },
        )
        self.connection.execute(
            text(
                """
                UPDATE knowledge_domain_versions
                SET status = 'ACTIVE', generation = :committed_generation
                WHERE knowledge_version_id = :to_version_id
                """
            ),
            {
                "to_version_id": to_version_id,
                "committed_generation": expected_generation + 1,
            },
        )

    def start_query_run(
        self,
        *,
        query_run_id: str,
        tenant_id: str,
        workspace_id: str,
        agent_core_decision_ref: str,
        snapshot_id: str,
        request_payload: dict[str, Any],
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_query_runs (
                    query_run_id, tenant_id, workspace_id, agent_core_decision_ref,
                    snapshot_id, request_hash, status
                )
                VALUES (
                    :query_run_id, :tenant_id, :workspace_id, :agent_core_decision_ref,
                    :snapshot_id, :request_hash, 'RUNNING'
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "query_run_id": query_run_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_core_decision_ref": agent_core_decision_ref,
                "snapshot_id": snapshot_id,
                "request_hash": canonical_sha256(request_payload),
            },
        )

    def start_retrieval_round(
        self,
        *,
        round_id: str,
        query_run_id: str,
        round_no: int,
        retriever_set: dict[str, Any],
        status: str = "RUNNING",
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_retrieval_rounds (
                    round_id, query_run_id, round_no, retriever_set_hash, status
                )
                VALUES (
                    :round_id, :query_run_id, :round_no, :retriever_set_hash, :status
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "round_id": round_id,
                "query_run_id": query_run_id,
                "round_no": round_no,
                "retriever_set_hash": canonical_sha256(retriever_set),
                "status": status,
            },
        )

    def mark_query_run_status(self, *, query_run_id: str, status: str) -> None:
        self.connection.execute(
            text(
                """
                UPDATE knowledge_query_runs
                SET status = :status
                WHERE query_run_id = :query_run_id
                """
            ),
            {
                "query_run_id": query_run_id,
                "status": status,
            },
        )

    def commit_evidence(
        self,
        *,
        evidence_id: str,
        query_run_id: str,
        round_id: str,
        chunk_id: str,
        source_span_ref: str,
        evidence_payload: dict[str, Any],
        authority_ref: str,
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO knowledge_evidence_records (
                    evidence_id, query_run_id, round_id, chunk_id, source_span_ref,
                    evidence_hash, citation_eligibility, selection_status, authority_ref
                )
                VALUES (
                    :evidence_id, :query_run_id, :round_id, :chunk_id, :source_span_ref,
                    :evidence_hash, 'STRICT', 'SELECTED', :authority_ref
                )
                """
            ),
            {
                "evidence_id": evidence_id,
                "query_run_id": query_run_id,
                "round_id": round_id,
                "chunk_id": chunk_id,
                "source_span_ref": source_span_ref,
                "evidence_hash": canonical_sha256(evidence_payload),
                "authority_ref": authority_ref,
            },
        )


__all__ = [
    "KnowledgeCutoverConflict",
    "KnowledgeRepository",
    "KnowledgeUnitOfWork",
    "KnowledgeVersionDraft",
]
