from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SourceObjectRecord(BaseModel):
    source_id: str
    workspace_id: str
    owner_id: str | None = None
    source_uri: str
    storage_uri: str
    source_sha256: str
    mime_type: str
    filename: str
    size_bytes: int = 0
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)


class WorkspaceFileRecord(BaseModel):
    file_id: str
    workspace_id: str
    source_id: str
    owner_id: str | None = None
    filename: str
    mime_type: str
    source_sha256: str
    parse_status: str = "uploaded"
    latest_parse_job_id: str | None = None
    latest_document_version_id: str | None = None
    security_label: str = "internal"


class ParseJobRecord(BaseModel):
    parse_job_id: str
    workspace_id: str
    file_id: str
    source_id: str
    status: str
    parser_id: str
    parser_version: str
    parse_idempotency_key: str
    attempt_count: int = 1
    document_version_id: str | None = None
    blocked_reason: str | None = None
    failure_reason: str | None = None


class DocumentVersionRecord(BaseModel):
    document_version_id: str
    document_id: str
    workspace_id: str
    source_id: str | None = None
    source_sha256: str
    parser_id: str
    parser_version: str
    parser_config_hash: str
    ir_schema_version: str
    block_count: int = 0
    table_count: int = 0
    figure_count: int = 0
    status: str = "ready"
    ir_json: dict[str, Any] = Field(default_factory=dict)


class IndexChunkRecord(BaseModel):
    chunk_id: str
    index_job_id: str
    knowledge_space_id: str
    workspace_id: str
    document_id: str
    document_version_id: str
    block_id: str
    content: str
    source_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    citation_lineage: dict[str, Any] = Field(default_factory=dict)
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)


__all__ = [
    "DocumentVersionRecord",
    "IndexChunkRecord",
    "ParseJobRecord",
    "SourceObjectRecord",
    "WorkspaceFileRecord",
]
