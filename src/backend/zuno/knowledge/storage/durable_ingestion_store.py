from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine, select

from zuno.knowledge.ingestion import CanonicalDocumentIR, ParseJobSnapshot
from zuno.knowledge.indexing import IndexJobManifest

from .contracts import (
    ArtifactRecord,
    DocumentBlockRecord,
    DocumentVersionRecord,
    FeedbackRecord,
    IndexChunkRecord,
    ParseJobRecord,
    SourceObjectRecord,
    TaskEventRecord,
    WorkspaceFileRecord,
    WorkspaceTaskRecord,
)
from .sqlmodel_models import (
    ArtifactTable,
    DocumentBlockTable,
    DocumentVersionTable,
    FeedbackTable,
    IndexChunkTable,
    IndexManifestTable,
    ParseJobTable,
    ParseSnapshotTable,
    SourceObjectTable,
    TaskEventTable,
    WorkspaceFileTable,
    WorkspaceTaskTable,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


class SQLiteDurableIngestionStore:
    """SQLite-backed Product V1 durable store for ingestion/index contracts."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}", connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(self.engine)

    def save_source_object(self, record: SourceObjectRecord) -> SourceObjectRecord:
        self._merge(
            SourceObjectTable(
                source_id=record.source_id,
                workspace_id=record.workspace_id,
                owner_id=record.owner_id,
                source_uri=record.source_uri,
                storage_uri=record.storage_uri,
                source_sha256=record.source_sha256,
                mime_type=record.mime_type,
                filename=record.filename,
                size_bytes=record.size_bytes,
                acl_scope=record.acl_scope,
                sensitivity_tags_json=list(record.sensitivity_tags),
            )
        )
        return record

    def save_workspace_file(self, record: WorkspaceFileRecord) -> WorkspaceFileRecord:
        self._merge(
            WorkspaceFileTable(
                file_id=record.file_id,
                workspace_id=record.workspace_id,
                source_id=record.source_id,
                owner_id=record.owner_id,
                filename=record.filename,
                mime_type=record.mime_type,
                source_sha256=record.source_sha256,
                parse_status=record.parse_status,
                latest_parse_job_id=record.latest_parse_job_id,
                latest_document_version_id=record.latest_document_version_id,
                security_label=record.security_label,
            )
        )
        return record

    def create_parse_job(self, record: ParseJobRecord) -> ParseJobRecord:
        self._merge(
            ParseJobTable(
                parse_job_id=record.parse_job_id,
                workspace_id=record.workspace_id,
                file_id=record.file_id,
                source_id=record.source_id,
                status=record.status,
                parser_id=record.parser_id,
                parser_version=record.parser_version,
                parse_idempotency_key=record.parse_idempotency_key,
                attempt_count=record.attempt_count,
                document_version_id=record.document_version_id,
                blocked_reason=record.blocked_reason,
                failure_reason=record.failure_reason,
            )
        )
        return record

    def save_parse_snapshot(self, snapshot: ParseJobSnapshot) -> ParseJobSnapshot:
        payload = _model_payload(snapshot)
        self._merge(
            ParseSnapshotTable(
                parse_job_id=snapshot.job_id,
                status=snapshot.status,
                workspace_id=snapshot.workspace_id,
                document_id=snapshot.document_id,
                parse_attempt_id=snapshot.parse_attempt_id,
                snapshot_json=payload,
            )
        )
        return snapshot

    def save_document_version(self, document: CanonicalDocumentIR) -> DocumentVersionRecord:
        metadata = document.metadata
        record = DocumentVersionRecord(
            document_version_id=metadata.document_version_id,
            document_id=metadata.document_id,
            workspace_id=metadata.workspace_id,
            source_id=metadata.source_id,
            source_sha256=metadata.source_sha256 or metadata.hash,
            parser_id=metadata.parser_id,
            parser_version=metadata.parser_version,
            parser_config_hash=metadata.parser_config_hash,
            ir_schema_version=metadata.ir_schema_version,
            block_count=len(document.blocks),
            table_count=len(document.tables),
            figure_count=len(document.figures),
            ir_json=_model_payload(document),
        )
        self._merge(
            DocumentVersionTable(
                document_version_id=record.document_version_id,
                document_id=record.document_id,
                workspace_id=record.workspace_id,
                source_id=record.source_id,
                source_sha256=record.source_sha256,
                parser_id=record.parser_id,
                parser_version=record.parser_version,
                parser_config_hash=record.parser_config_hash,
                ir_schema_version=record.ir_schema_version,
                block_count=record.block_count,
                table_count=record.table_count,
                figure_count=record.figure_count,
                status=record.status,
                ir_json=record.ir_json,
            )
        )
        for block in document.blocks:
            self._merge(
                DocumentBlockTable(
                    block_row_id=f"{record.document_version_id}:{block.block_id}",
                    document_version_id=record.document_version_id,
                    block_id=block.block_id,
                    workspace_id=record.workspace_id,
                    document_id=record.document_id,
                    block_type=block.type,
                    text=block.text,
                    source_span_json=_model_payload(block.source_span),
                    metadata_json=block.metadata,
                    acl_scope=block.acl_scope,
                    sensitivity_tags_json=list(block.sensitivity_tags),
                )
            )
        return record

    def save_index_manifest(self, manifest: IndexJobManifest) -> IndexJobManifest:
        self._merge(
            IndexManifestTable(
                index_job_id=manifest.job_id,
                knowledge_space_id=manifest.knowledge_space_id,
                workspace_id=manifest.workspace_id,
                document_id=manifest.document_id,
                document_version_id=manifest.document_version_id,
                source_sha256=manifest.source_sha256,
                status=manifest.status,
                manifest_json=_model_payload(manifest),
            )
        )
        return manifest

    def save_index_chunk(self, record: IndexChunkRecord) -> IndexChunkRecord:
        self._merge(
            IndexChunkTable(
                chunk_id=record.chunk_id,
                index_job_id=record.index_job_id,
                knowledge_space_id=record.knowledge_space_id,
                workspace_id=record.workspace_id,
                document_id=record.document_id,
                document_version_id=record.document_version_id,
                block_id=record.block_id,
                content=record.content,
                source_type=record.source_type,
                metadata_json=record.metadata,
                citation_lineage_json=record.citation_lineage,
                acl_scope=record.acl_scope,
                sensitivity_tags_json=list(record.sensitivity_tags),
            )
        )
        return record

    def get_source_object(self, source_id: str) -> SourceObjectRecord:
        row = self._get(SourceObjectTable, source_id, "source object")
        return SourceObjectRecord(
            source_id=row.source_id,
            workspace_id=row.workspace_id,
            owner_id=row.owner_id,
            source_uri=row.source_uri,
            storage_uri=row.storage_uri,
            source_sha256=row.source_sha256,
            mime_type=row.mime_type,
            filename=row.filename,
            size_bytes=row.size_bytes,
            acl_scope=row.acl_scope,
            sensitivity_tags=list(row.sensitivity_tags_json or []),
        )

    def get_workspace_file(self, file_id: str) -> WorkspaceFileRecord:
        row = self._get(WorkspaceFileTable, file_id, "workspace file")
        return WorkspaceFileRecord(
            file_id=row.file_id,
            workspace_id=row.workspace_id,
            source_id=row.source_id,
            owner_id=row.owner_id,
            filename=row.filename,
            mime_type=row.mime_type,
            source_sha256=row.source_sha256,
            parse_status=row.parse_status,
            latest_parse_job_id=row.latest_parse_job_id,
            latest_document_version_id=row.latest_document_version_id,
            security_label=row.security_label,
        )

    def list_workspace_files(self) -> list[WorkspaceFileRecord]:
        with Session(self.engine) as session:
            rows = session.exec(select(WorkspaceFileTable)).all()
        return [
            WorkspaceFileRecord(
                file_id=row.file_id,
                workspace_id=row.workspace_id,
                source_id=row.source_id,
                owner_id=row.owner_id,
                filename=row.filename,
                mime_type=row.mime_type,
                source_sha256=row.source_sha256,
                parse_status=row.parse_status,
                latest_parse_job_id=row.latest_parse_job_id,
                latest_document_version_id=row.latest_document_version_id,
                security_label=row.security_label,
            )
            for row in rows
        ]

    def get_parse_job(self, parse_job_id: str) -> ParseJobRecord:
        row = self._get(ParseJobTable, parse_job_id, "parse job")
        return ParseJobRecord(
            parse_job_id=row.parse_job_id,
            workspace_id=row.workspace_id,
            file_id=row.file_id,
            source_id=row.source_id,
            status=row.status,
            parser_id=row.parser_id,
            parser_version=row.parser_version,
            parse_idempotency_key=row.parse_idempotency_key,
            attempt_count=row.attempt_count,
            document_version_id=row.document_version_id,
            blocked_reason=row.blocked_reason,
            failure_reason=row.failure_reason,
        )

    def get_parse_snapshot(self, parse_job_id: str) -> ParseJobSnapshot:
        row = self._get(ParseSnapshotTable, parse_job_id, "parse snapshot")
        return ParseJobSnapshot.model_validate(row.snapshot_json)

    def get_document_version(self, document_version_id: str) -> DocumentVersionRecord:
        row = self._get(DocumentVersionTable, document_version_id, "document version")
        return DocumentVersionRecord(
            document_version_id=row.document_version_id,
            document_id=row.document_id,
            workspace_id=row.workspace_id,
            source_id=row.source_id,
            source_sha256=row.source_sha256,
            parser_id=row.parser_id,
            parser_version=row.parser_version,
            parser_config_hash=row.parser_config_hash,
            ir_schema_version=row.ir_schema_version,
            block_count=row.block_count,
            table_count=row.table_count,
            figure_count=row.figure_count,
            status=row.status,
            ir_json=row.ir_json,
        )

    def list_document_blocks(self, document_version_id: str) -> list[DocumentBlockRecord]:
        with Session(self.engine) as session:
            rows = session.exec(
                select(DocumentBlockTable).where(
                    DocumentBlockTable.document_version_id == document_version_id
                )
            ).all()
        return [
            DocumentBlockRecord(
                document_version_id=row.document_version_id,
                block_id=row.block_id,
                workspace_id=row.workspace_id,
                document_id=row.document_id,
                block_type=row.block_type,
                text=row.text,
                source_span=row.source_span_json,
                metadata=row.metadata_json,
                acl_scope=row.acl_scope,
                sensitivity_tags=list(row.sensitivity_tags_json or []),
            )
            for row in rows
        ]

    def get_index_manifest(self, index_job_id: str) -> IndexJobManifest:
        row = self._get(IndexManifestTable, index_job_id, "index manifest")
        return IndexJobManifest.model_validate(row.manifest_json)

    def list_index_chunks(self, index_job_id: str) -> list[IndexChunkRecord]:
        with Session(self.engine) as session:
            rows = session.exec(
                select(IndexChunkTable).where(IndexChunkTable.index_job_id == index_job_id)
            ).all()
        return [
            IndexChunkRecord(
                chunk_id=row.chunk_id,
                index_job_id=row.index_job_id,
                knowledge_space_id=row.knowledge_space_id,
                workspace_id=row.workspace_id,
                document_id=row.document_id,
                document_version_id=row.document_version_id,
                block_id=row.block_id,
                content=row.content,
                source_type=row.source_type,
                metadata=row.metadata_json,
                citation_lineage=row.citation_lineage_json,
                acl_scope=row.acl_scope,
                sensitivity_tags=list(row.sensitivity_tags_json or []),
            )
            for row in rows
        ]

    def list_index_manifests(self) -> list[IndexJobManifest]:
        with Session(self.engine) as session:
            rows = session.exec(select(IndexManifestTable)).all()
        return [IndexJobManifest.model_validate(row.manifest_json) for row in rows]

    def save_workspace_task(self, record: WorkspaceTaskRecord) -> WorkspaceTaskRecord:
        self._merge(
            WorkspaceTaskTable(
                task_id=record.task_id,
                workspace_id=record.workspace_id,
                owner_id=record.owner_id,
                status=record.status,
                trace_id=record.trace_id,
                payload_json=record.payload,
            )
        )
        return record

    def get_workspace_task(self, task_id: str) -> WorkspaceTaskRecord:
        row = self._get(WorkspaceTaskTable, task_id, "workspace task")
        return WorkspaceTaskRecord(
            task_id=row.task_id,
            workspace_id=row.workspace_id,
            owner_id=row.owner_id,
            status=row.status,
            trace_id=row.trace_id,
            payload=row.payload_json,
        )

    def list_workspace_tasks(self) -> list[WorkspaceTaskRecord]:
        with Session(self.engine) as session:
            rows = session.exec(select(WorkspaceTaskTable)).all()
        return [
            WorkspaceTaskRecord(
                task_id=row.task_id,
                workspace_id=row.workspace_id,
                owner_id=row.owner_id,
                status=row.status,
                trace_id=row.trace_id,
                payload=row.payload_json,
            )
            for row in rows
        ]

    def save_task_event(self, record: TaskEventRecord) -> TaskEventRecord:
        self._merge(
            TaskEventTable(
                event_id=record.event_id,
                task_id=record.task_id,
                trace_id=record.trace_id,
                event_type=record.event_type,
                timestamp=record.timestamp,
                payload_json=record.payload,
            )
        )
        return record

    def list_task_events(self, task_id: str) -> list[TaskEventRecord]:
        with Session(self.engine) as session:
            rows = session.exec(
                select(TaskEventTable).where(TaskEventTable.task_id == task_id)
            ).all()
        rows = sorted(rows, key=lambda row: row.timestamp)
        return [
            TaskEventRecord(
                event_id=row.event_id,
                task_id=row.task_id,
                trace_id=row.trace_id,
                event_type=row.event_type,
                timestamp=row.timestamp,
                payload=row.payload_json,
            )
            for row in rows
        ]

    def save_artifact(self, record: ArtifactRecord) -> ArtifactRecord:
        self._merge(
            ArtifactTable(
                artifact_id=record.artifact_id,
                task_id=record.task_id,
                workspace_id=record.workspace_id,
                owner_id=record.owner_id,
                kind=record.kind,
                uri=record.uri,
                content=record.content,
                content_sha256=record.content_sha256,
                trace_id=record.trace_id,
                payload_json=record.payload,
            )
        )
        return record

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        row = self._get(ArtifactTable, artifact_id, "artifact")
        return ArtifactRecord(
            artifact_id=row.artifact_id,
            task_id=row.task_id,
            workspace_id=row.workspace_id,
            owner_id=row.owner_id,
            kind=row.kind,
            uri=row.uri,
            content=row.content,
            content_sha256=row.content_sha256,
            trace_id=row.trace_id,
            payload=row.payload_json,
        )

    def list_artifacts_for_task(self, task_id: str) -> list[ArtifactRecord]:
        with Session(self.engine) as session:
            rows = session.exec(
                select(ArtifactTable).where(ArtifactTable.task_id == task_id)
            ).all()
        return [
            ArtifactRecord(
                artifact_id=row.artifact_id,
                task_id=row.task_id,
                workspace_id=row.workspace_id,
                owner_id=row.owner_id,
                kind=row.kind,
                uri=row.uri,
                content=row.content,
                content_sha256=row.content_sha256,
                trace_id=row.trace_id,
                payload=row.payload_json,
            )
            for row in rows
        ]

    def save_feedback(self, record: FeedbackRecord) -> FeedbackRecord:
        self._merge(
            FeedbackTable(
                feedback_id=record.feedback_id,
                task_id=record.task_id,
                rating=record.rating,
                label=record.label,
                comment=record.comment,
                dataset_candidate=record.dataset_candidate,
                payload_json=record.payload,
            )
        )
        return record

    def list_feedback_for_task(self, task_id: str) -> list[FeedbackRecord]:
        with Session(self.engine) as session:
            rows = session.exec(
                select(FeedbackTable).where(FeedbackTable.task_id == task_id)
            ).all()
        return [
            FeedbackRecord(
                feedback_id=row.feedback_id,
                task_id=row.task_id,
                rating=row.rating,
                label=row.label,
                comment=row.comment,
                dataset_candidate=row.dataset_candidate,
                payload=row.payload_json,
            )
            for row in rows
        ]

    def _merge(self, row: SQLModel) -> None:
        with Session(self.engine) as session:
            session.merge(row)
            session.commit()

    def _get(self, table: type[SQLModel], key: str, label: str) -> Any:
        with Session(self.engine) as session:
            row = session.get(table, key)
        if row is None:
            raise KeyError(f"{label} not found: {key}")
        return row


def _model_payload(model: BaseModel) -> dict[str, Any]:
    return json.loads(model.model_dump_json())


__all__ = ["SQLiteDurableIngestionStore"]
