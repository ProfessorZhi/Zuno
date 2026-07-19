from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

from zuno.platform.contracts import canonical_json, canonical_sha256


class IngestionPersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class IngestionReceipt:
    ref: str
    tenant_id: str
    status: str
    payload_hash: str | None = None


class IngestionUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._active = False

    def __enter__(self) -> IngestionRepository:
        if self._active:
            raise RuntimeError("IngestionUnitOfWork cannot be nested")
        self._active = True
        self._context = self.engine.begin()
        try:
            self.connection = self._context.__enter__()
            return IngestionRepository(self.connection)
        except BaseException:
            self._active = False
            raise

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            self._context.__exit__(exc_type, exc, tb)
        finally:
            self._active = False


class IngestionRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def record_source_object(
        self,
        *,
        source_object_id: str,
        tenant_id: str,
        workspace_id: str,
        filename: str,
        mime_type: str,
        storage_uri: str,
        object_manifest_ref: str,
        source_sha256: str,
        size_bytes: int,
        classification_ref: str,
        security_epoch_ref: str,
        source_kind: str = "upload",
        declared_format: str = "unknown",
        status: str = "committed",
    ) -> IngestionReceipt:
        self._require_hash(source_sha256, "source_sha256")
        if size_bytes < 0:
            raise IngestionPersistenceError("source object size_bytes must be non-negative")
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_source_objects(
                    source_object_id, tenant_id, workspace_id, source_kind, filename,
                    mime_type, declared_format, storage_uri, object_manifest_ref,
                    source_sha256, size_bytes, classification_ref, security_epoch_ref, status
                ) VALUES (
                    :source_object_id, :tenant_id, :workspace_id, :source_kind, :filename,
                    :mime_type, :declared_format, :storage_uri, :object_manifest_ref,
                    :source_sha256, :size_bytes, :classification_ref, :security_epoch_ref, :status
                )
                """
            ),
            {
                "source_object_id": source_object_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "source_kind": source_kind,
                "filename": filename,
                "mime_type": mime_type,
                "declared_format": declared_format,
                "storage_uri": storage_uri,
                "object_manifest_ref": object_manifest_ref,
                "source_sha256": source_sha256,
                "size_bytes": size_bytes,
                "classification_ref": classification_ref,
                "security_epoch_ref": security_epoch_ref,
                "status": status,
            },
        )
        return IngestionReceipt(source_object_id, tenant_id, status, source_sha256)

    def record_document_version(
        self,
        *,
        document_version_id: str,
        tenant_id: str,
        workspace_id: str,
        source_object_id: str,
        version_no: int,
        content_hash: str,
        metadata: dict[str, Any],
        immutability_ref: str,
        status: str = "active",
    ) -> IngestionReceipt:
        self._require_hash(content_hash, "content_hash")
        if version_no <= 0:
            raise IngestionPersistenceError("document version_no must be positive")
        metadata_hash = canonical_sha256(metadata)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_document_versions(
                    document_version_id, tenant_id, workspace_id, source_object_id,
                    version_no, content_hash, metadata_hash, immutability_ref, status
                ) VALUES (
                    :document_version_id, :tenant_id, :workspace_id, :source_object_id,
                    :version_no, :content_hash, :metadata_hash, :immutability_ref, :status
                )
                """
            ),
            {
                "document_version_id": document_version_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "source_object_id": source_object_id,
                "version_no": version_no,
                "content_hash": content_hash,
                "metadata_hash": metadata_hash,
                "immutability_ref": immutability_ref,
                "status": status,
            },
        )
        return IngestionReceipt(document_version_id, tenant_id, status, metadata_hash)

    def record_parse_plan(
        self,
        *,
        parse_plan_id: str,
        tenant_id: str,
        document_version_id: str,
        parser_route: dict[str, Any],
        parser_policy_ref: str,
        parser_bundle: dict[str, Any],
        quality_policy_ref: str,
        security_decision_ref: str,
        status: str = "planned",
    ) -> IngestionReceipt:
        parser_bundle_hash = canonical_sha256(parser_bundle)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_plans(
                    parse_plan_id, tenant_id, document_version_id, parser_route,
                    parser_policy_ref, parser_bundle_hash, quality_policy_ref,
                    security_decision_ref, status
                ) VALUES (
                    :parse_plan_id, :tenant_id, :document_version_id, CAST(:parser_route AS jsonb),
                    :parser_policy_ref, :parser_bundle_hash, :quality_policy_ref,
                    :security_decision_ref, :status
                )
                """
            ),
            {
                "parse_plan_id": parse_plan_id,
                "tenant_id": tenant_id,
                "document_version_id": document_version_id,
                "parser_route": canonical_json(parser_route),
                "parser_policy_ref": parser_policy_ref,
                "parser_bundle_hash": parser_bundle_hash,
                "quality_policy_ref": quality_policy_ref,
                "security_decision_ref": security_decision_ref,
                "status": status,
            },
        )
        return IngestionReceipt(parse_plan_id, tenant_id, status, parser_bundle_hash)

    def record_parse_job(
        self,
        *,
        parse_job_id: str,
        tenant_id: str,
        parse_plan_id: str,
        document_version_id: str,
        idempotency_key: str,
        priority_class: str = "normal",
        status: str = "queued",
    ) -> IngestionReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_jobs(
                    parse_job_id, tenant_id, parse_plan_id, document_version_id,
                    idempotency_key, priority_class, status
                ) VALUES (
                    :parse_job_id, :tenant_id, :parse_plan_id, :document_version_id,
                    :idempotency_key, :priority_class, :status
                )
                """
            ),
            {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "parse_plan_id": parse_plan_id,
                "document_version_id": document_version_id,
                "idempotency_key": idempotency_key,
                "priority_class": priority_class,
                "status": status,
            },
        )
        return IngestionReceipt(parse_job_id, tenant_id, status)

    def record_parse_attempt(
        self,
        *,
        parse_attempt_id: str,
        tenant_id: str,
        parse_job_id: str,
        attempt_no: int,
        worker_id: str,
        lease_ref: str,
        fencing_token: int,
        status: str = "started",
    ) -> IngestionReceipt:
        if attempt_no <= 0 or fencing_token <= 0:
            raise IngestionPersistenceError("parse attempt_no and fencing_token must be positive")
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_attempts(
                    parse_attempt_id, tenant_id, parse_job_id, attempt_no,
                    worker_id, lease_ref, fencing_token, status
                ) VALUES (
                    :parse_attempt_id, :tenant_id, :parse_job_id, :attempt_no,
                    :worker_id, :lease_ref, :fencing_token, :status
                )
                """
            ),
            {
                "parse_attempt_id": parse_attempt_id,
                "tenant_id": tenant_id,
                "parse_job_id": parse_job_id,
                "attempt_no": attempt_no,
                "worker_id": worker_id,
                "lease_ref": lease_ref,
                "fencing_token": fencing_token,
                "status": status,
            },
        )
        return IngestionReceipt(parse_attempt_id, tenant_id, status)

    def record_parse_snapshot(
        self,
        *,
        parse_snapshot_id: str,
        tenant_id: str,
        parse_job_id: str,
        parse_attempt_id: str,
        document_version_id: str,
        canonical_ir: dict[str, Any],
        canonical_ir_ref: str,
        canonical_ir_schema_ref: str,
        parser_id: str,
        parser_version: str,
        status: str = "succeeded",
        diagnostics: list[dict[str, Any]] | None = None,
    ) -> IngestionReceipt:
        snapshot_hash = canonical_sha256(canonical_ir)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_snapshots(
                    parse_snapshot_id, tenant_id, parse_job_id, parse_attempt_id,
                    document_version_id, snapshot_hash, canonical_ir_ref,
                    canonical_ir_schema_ref, parser_id, parser_version, status, diagnostics
                ) VALUES (
                    :parse_snapshot_id, :tenant_id, :parse_job_id, :parse_attempt_id,
                    :document_version_id, :snapshot_hash, :canonical_ir_ref,
                    :canonical_ir_schema_ref, :parser_id, :parser_version, :status,
                    CAST(:diagnostics AS jsonb)
                )
                """
            ),
            {
                "parse_snapshot_id": parse_snapshot_id,
                "tenant_id": tenant_id,
                "parse_job_id": parse_job_id,
                "parse_attempt_id": parse_attempt_id,
                "document_version_id": document_version_id,
                "snapshot_hash": snapshot_hash,
                "canonical_ir_ref": canonical_ir_ref,
                "canonical_ir_schema_ref": canonical_ir_schema_ref,
                "parser_id": parser_id,
                "parser_version": parser_version,
                "status": status,
                "diagnostics": canonical_json(diagnostics or []),
            },
        )
        return IngestionReceipt(parse_snapshot_id, tenant_id, status, snapshot_hash)

    def record_source_span(
        self,
        *,
        source_span_id: str,
        tenant_id: str,
        parse_snapshot_id: str,
        document_version_id: str,
        block_id: str,
        coordinate_ref: dict[str, Any],
        page_no: int | None = None,
        region_ref: str | None = None,
    ) -> IngestionReceipt:
        span_hash = canonical_sha256(
            {
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "block_id": block_id,
                "page_no": page_no,
                "region_ref": region_ref,
                "coordinate_ref": coordinate_ref,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_source_spans(
                    source_span_id, tenant_id, parse_snapshot_id, document_version_id,
                    block_id, page_no, region_ref, coordinate_ref, span_hash
                ) VALUES (
                    :source_span_id, :tenant_id, :parse_snapshot_id, :document_version_id,
                    :block_id, :page_no, :region_ref, CAST(:coordinate_ref AS jsonb), :span_hash
                )
                """
            ),
            {
                "source_span_id": source_span_id,
                "tenant_id": tenant_id,
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "block_id": block_id,
                "page_no": page_no,
                "region_ref": region_ref,
                "coordinate_ref": canonical_json(coordinate_ref),
                "span_hash": span_hash,
            },
        )
        return IngestionReceipt(source_span_id, tenant_id, "recorded", span_hash)

    def record_quality_decision(
        self,
        *,
        quality_decision_id: str,
        tenant_id: str,
        parse_snapshot_id: str,
        coverage_score: float,
        confidence_score: float,
        decision: str,
        review_task_ref: str | None = None,
    ) -> IngestionReceipt:
        decision_hash = canonical_sha256(
            {
                "parse_snapshot_id": parse_snapshot_id,
                "coverage_score": coverage_score,
                "confidence_score": confidence_score,
                "decision": decision,
                "review_task_ref": review_task_ref,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_quality_gate_decisions(
                    quality_decision_id, tenant_id, parse_snapshot_id, coverage_score,
                    confidence_score, decision, review_task_ref, decision_hash
                ) VALUES (
                    :quality_decision_id, :tenant_id, :parse_snapshot_id, :coverage_score,
                    :confidence_score, :decision, :review_task_ref, :decision_hash
                )
                """
            ),
            {
                "quality_decision_id": quality_decision_id,
                "tenant_id": tenant_id,
                "parse_snapshot_id": parse_snapshot_id,
                "coverage_score": coverage_score,
                "confidence_score": confidence_score,
                "decision": decision,
                "review_task_ref": review_task_ref,
                "decision_hash": decision_hash,
            },
        )
        return IngestionReceipt(quality_decision_id, tenant_id, decision, decision_hash)

    def record_indexable_snapshot(
        self,
        *,
        indexable_snapshot_id: str,
        tenant_id: str,
        parse_snapshot_id: str,
        document_version_id: str,
        quality_decision_id: str,
        visibility_ref: str,
        payload: dict[str, Any],
        knowledge_handoff_status: str = "pending",
    ) -> IngestionReceipt:
        snapshot_hash = canonical_sha256(payload)
        handoff_hash = canonical_sha256(
            {
                "indexable_snapshot_id": indexable_snapshot_id,
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "quality_decision_id": quality_decision_id,
                "payload": payload,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_indexable_document_snapshots(
                    indexable_snapshot_id, tenant_id, parse_snapshot_id, document_version_id,
                    quality_decision_id, snapshot_hash, handoff_envelope_hash,
                    visibility_ref, knowledge_handoff_status
                ) VALUES (
                    :indexable_snapshot_id, :tenant_id, :parse_snapshot_id, :document_version_id,
                    :quality_decision_id, :snapshot_hash, :handoff_envelope_hash,
                    :visibility_ref, :knowledge_handoff_status
                )
                """
            ),
            {
                "indexable_snapshot_id": indexable_snapshot_id,
                "tenant_id": tenant_id,
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "quality_decision_id": quality_decision_id,
                "snapshot_hash": snapshot_hash,
                "handoff_envelope_hash": handoff_hash,
                "visibility_ref": visibility_ref,
                "knowledge_handoff_status": knowledge_handoff_status,
            },
        )
        return IngestionReceipt(indexable_snapshot_id, tenant_id, knowledge_handoff_status, handoff_hash)

    def enqueue_outbox_event(
        self,
        *,
        outbox_event_id: str,
        tenant_id: str,
        aggregate_ref: str,
        event_type: str,
        payload: dict[str, Any],
        publish_status: str = "pending",
    ) -> IngestionReceipt:
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_outbox_events(
                    outbox_event_id, tenant_id, aggregate_ref, event_type,
                    payload_hash, payload, publish_status
                ) VALUES (
                    :outbox_event_id, :tenant_id, :aggregate_ref, :event_type,
                    :payload_hash, CAST(:payload AS jsonb), :publish_status
                )
                """
            ),
            {
                "outbox_event_id": outbox_event_id,
                "tenant_id": tenant_id,
                "aggregate_ref": aggregate_ref,
                "event_type": event_type,
                "payload_hash": payload_hash,
                "payload": canonical_json(payload),
                "publish_status": publish_status,
            },
        )
        return IngestionReceipt(outbox_event_id, tenant_id, publish_status, payload_hash)

    def get_indexable_snapshot(self, indexable_snapshot_id: str) -> dict[str, Any]:
        row = self.connection.execute(
            text(
                """
                SELECT indexable_snapshot_id, parse_snapshot_id, document_version_id,
                       quality_decision_id, snapshot_hash, handoff_envelope_hash,
                       visibility_ref, knowledge_handoff_status
                FROM ingestion_indexable_document_snapshots
                WHERE indexable_snapshot_id = :indexable_snapshot_id
                """
            ),
            {"indexable_snapshot_id": indexable_snapshot_id},
        ).mappings().first()
        if row is None:
            raise IngestionPersistenceError(f"missing indexable snapshot: {indexable_snapshot_id}")
        return dict(row)

    @staticmethod
    def _require_hash(value: str, field_name: str) -> None:
        if len(value) != 64:
            raise IngestionPersistenceError(f"{field_name} must be a 64-character sha256 hash")
