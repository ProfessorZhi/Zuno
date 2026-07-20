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


class DocumentBlockTable(SQLModel, table=True):
    __tablename__ = "zuno_document_blocks"

    block_row_id: str = Field(primary_key=True)
    document_version_id: str = Field(index=True)
    block_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    document_id: str = Field(index=True)
    block_type: str = Field(index=True)
    text: str
    source_span_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    metadata_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    acl_scope: str = "workspace"
    sensitivity_tags_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))


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


class QualityGateTable(SQLModel, table=True):
    __tablename__ = "zuno_quality_gates"

    quality_decision_id: str = Field(primary_key=True)
    parse_snapshot_id: str = Field(index=True)
    document_version_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    verdict: str = Field(index=True)
    decision_hash: str = Field(index=True)
    review_task_id: str | None = Field(default=None, index=True)
    metrics_json: list[dict] = Field(default_factory=list, sa_column=Column(JSON))


class ReviewTaskTable(SQLModel, table=True):
    __tablename__ = "zuno_review_tasks"

    review_task_id: str = Field(primary_key=True)
    parse_snapshot_id: str = Field(index=True)
    document_version_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    reviewer_scope: str = Field(index=True)
    security_epoch_ref: str = Field(index=True)
    status: str = Field(default="pending", index=True)
    expires_at: float = Field(index=True)
    reason: str
    decision_hash: str = Field(index=True)


class ReviewDecisionTable(SQLModel, table=True):
    __tablename__ = "zuno_review_decisions"

    decision_id: str = Field(primary_key=True)
    review_task_id: str = Field(index=True)
    status: str = Field(index=True)
    reviewer_id: str = Field(index=True)
    reviewer_scope: str = Field(index=True)
    security_epoch_ref: str = Field(index=True)
    decision_hash: str = Field(index=True)
    duplicate: bool = Field(default=False, index=True)
    reason: str = ""
    decided_at: float = Field(index=True)


class WorkspaceTaskTable(SQLModel, table=True):
    __tablename__ = "zuno_workspace_tasks"

    task_id: str = Field(primary_key=True)
    workspace_id: str = Field(index=True)
    owner_id: str | None = Field(default=None, index=True)
    status: str = Field(index=True)
    trace_id: str | None = Field(default=None, index=True)
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class TaskEventTable(SQLModel, table=True):
    __tablename__ = "zuno_task_events"

    event_id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    trace_id: str = Field(index=True)
    event_type: str = Field(index=True)
    timestamp: float = Field(index=True)
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class ArtifactTable(SQLModel, table=True):
    __tablename__ = "zuno_artifacts"

    artifact_id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    owner_id: str | None = Field(default=None, index=True)
    kind: str = Field(index=True)
    uri: str
    content: str
    content_sha256: str = Field(index=True)
    trace_id: str | None = Field(default=None, index=True)
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class FeedbackTable(SQLModel, table=True):
    __tablename__ = "zuno_feedback"

    feedback_id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    rating: int | None = Field(default=None, index=True)
    label: str | None = Field(default=None, index=True)
    comment: str | None = None
    dataset_candidate: bool = Field(default=False, index=True)
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


STORAGE_TABLES = [
    SourceObjectTable,
    WorkspaceFileTable,
    ParseJobTable,
    ParseSnapshotTable,
    DocumentVersionTable,
    DocumentBlockTable,
    IndexManifestTable,
    IndexChunkTable,
    QualityGateTable,
    ReviewTaskTable,
    ReviewDecisionTable,
    WorkspaceTaskTable,
    TaskEventTable,
    ArtifactTable,
    FeedbackTable,
]


__all__ = [
    "ArtifactTable",
    "DocumentBlockTable",
    "DocumentVersionTable",
    "FeedbackTable",
    "IndexChunkTable",
    "IndexManifestTable",
    "QualityGateTable",
    "ReviewDecisionTable",
    "ReviewTaskTable",
    "ParseJobTable",
    "ParseSnapshotTable",
    "STORAGE_TABLES",
    "SourceObjectTable",
    "TaskEventTable",
    "WorkspaceTaskTable",
    "WorkspaceFileTable",
]
