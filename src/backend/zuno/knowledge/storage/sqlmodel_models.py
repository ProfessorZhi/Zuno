from __future__ import annotations

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class SourceObjectTable(SQLModel, table=True):
    __tablename__ = "zuno_source_objects"

    source_id: str = Field(primary_key=True)
    workspace_id: str = Field(index=True)
    owner_id: str | None = Field(default=None, index=True)
    source_uri: str
    storage_uri: str
    source_sha256: str = Field(index=True)
    mime_type: str
    filename: str
    size_bytes: int = 0
    acl_scope: str = "workspace"
    sensitivity_tags_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class WorkspaceFileTable(SQLModel, table=True):
    __tablename__ = "zuno_workspace_files"

    file_id: str = Field(primary_key=True)
    workspace_id: str = Field(index=True)
    source_id: str = Field(index=True)
    owner_id: str | None = Field(default=None, index=True)
    filename: str
    mime_type: str
    source_sha256: str = Field(index=True)
    parse_status: str = Field(default="uploaded", index=True)
    latest_parse_job_id: str | None = Field(default=None, index=True)
    latest_document_version_id: str | None = Field(default=None, index=True)
    security_label: str = "internal"


class ParseJobTable(SQLModel, table=True):
    __tablename__ = "zuno_parse_jobs"

    parse_job_id: str = Field(primary_key=True)
    workspace_id: str = Field(index=True)
    file_id: str = Field(index=True)
    source_id: str = Field(index=True)
    status: str = Field(index=True)
    parser_id: str = Field(index=True)
    parser_version: str
    parse_idempotency_key: str = Field(index=True)
    attempt_count: int = 1
    document_version_id: str | None = Field(default=None, index=True)
    blocked_reason: str | None = None
    failure_reason: str | None = None


class ParseSnapshotTable(SQLModel, table=True):
    __tablename__ = "zuno_parse_snapshots"

    parse_job_id: str = Field(primary_key=True)
    status: str = Field(index=True)
    workspace_id: str = Field(index=True)
    document_id: str = Field(index=True)
    parse_attempt_id: str = Field(index=True)
    snapshot_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class DocumentVersionTable(SQLModel, table=True):
    __tablename__ = "zuno_document_versions"

    document_version_id: str = Field(primary_key=True)
    document_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    source_id: str | None = Field(default=None, index=True)
    source_sha256: str = Field(index=True)
    parser_id: str = Field(index=True)
    parser_version: str
    parser_config_hash: str
    ir_schema_version: str
    block_count: int = 0
    table_count: int = 0
    figure_count: int = 0
    status: str = "ready"
    ir_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class IndexManifestTable(SQLModel, table=True):
    __tablename__ = "zuno_index_manifests"

    index_job_id: str = Field(primary_key=True)
    knowledge_space_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    document_id: str = Field(index=True)
    document_version_id: str = Field(index=True)
    source_sha256: str = Field(index=True)
    status: str = Field(index=True)
    manifest_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class IndexChunkTable(SQLModel, table=True):
    __tablename__ = "zuno_index_chunks"

    chunk_id: str = Field(primary_key=True)
    index_job_id: str = Field(index=True)
    knowledge_space_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    document_id: str = Field(index=True)
    document_version_id: str = Field(index=True)
    block_id: str = Field(index=True)
    content: str
    source_type: str = Field(index=True)
    metadata_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    citation_lineage_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    acl_scope: str = "workspace"
    sensitivity_tags_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))


STORAGE_TABLES = [
    SourceObjectTable,
    WorkspaceFileTable,
    ParseJobTable,
    ParseSnapshotTable,
    DocumentVersionTable,
    IndexManifestTable,
    IndexChunkTable,
]


__all__ = [
    "DocumentVersionTable",
    "IndexChunkTable",
    "IndexManifestTable",
    "ParseJobTable",
    "ParseSnapshotTable",
    "STORAGE_TABLES",
    "SourceObjectTable",
    "WorkspaceFileTable",
]
