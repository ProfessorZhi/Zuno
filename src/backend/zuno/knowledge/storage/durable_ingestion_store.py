from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine, select

from zuno.knowledge.ingestion import CanonicalDocumentIR, ParseJobSnapshot
from zuno.knowledge.indexing import IndexJobManifest

from .contracts import (
    DocumentVersionRecord,
    IndexChunkRecord,
    ParseJobRecord,
    SourceObjectRecord,
    WorkspaceFileRecord,
)
from .sqlmodel_models import (
    DocumentVersionTable,
    IndexChunkTable,
    IndexManifestTable,
    ParseJobTable,
    ParseSnapshotTable,
    SourceObjectTable,
    WorkspaceFileTable,
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
