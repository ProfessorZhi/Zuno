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


class ParseAttemptLeaseTable(SQLModel, table=True):
    __tablename__ = "zuno_parse_attempt_leases"

    parse_attempt_id: str = Field(primary_key=True)
    parse_job_id: str = Field(index=True)
    worker_id: str = Field(index=True)
    attempt_no: int = Field(index=True)
    fencing_token: int = Field(index=True)
    state: str = Field(index=True)
    heartbeat_at: float = Field(index=True)
    lease_expires_at: float = Field(index=True)
    lease_lost_reason: str | None = Field(default=None, index=True)
    domain_commit_ref: str | None = Field(default=None, index=True)
    idempotency_key: str | None = Field(default=None, index=True)
    duplicate_commit: bool = Field(default=False, index=True)
    late_result_rejected: bool = Field(default=False, index=True)
    orphan_reconciled: bool = Field(default=False, index=True)
    receipt_hash: str = Field(index=True)
    history_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))


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


class IndexableSnapshotTable(SQLModel, table=True):
    __tablename__ = "zuno_indexable_snapshots"

    indexable_snapshot_id: str = Field(primary_key=True)
    document_version_id: str = Field(index=True)
    parse_snapshot_id: str = Field(index=True)
    quality_decision_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    document_id: str = Field(index=True)
    canonical_hash: str = Field(index=True)
    idempotency_key: str = Field(index=True)
    security_refs_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    delete_refs_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class IngestionOutboxTable(SQLModel, table=True):
    __tablename__ = "zuno_ingestion_outbox"

    outbox_event_id: str = Field(primary_key=True)
    aggregate_ref: str = Field(index=True)
    event_type: str = Field(index=True)
    payload_hash: str = Field(index=True)
    idempotency_key: str = Field(index=True)
    publish_status: str = Field(default="pending", index=True)
    replay_count: int = Field(default=0, index=True)


class DeleteLifecycleTable(SQLModel, table=True):
    __tablename__ = "zuno_delete_lifecycle"

    delete_ref: str = Field(primary_key=True)
    snapshot_ref: str = Field(index=True)
    state: str = Field(index=True)
    visibility_ref: str = Field(index=True)
    cleanup_ref: str | None = Field(default=None, index=True)
    physical_delete_ref: str | None = Field(default=None, index=True)
    verification_ref: str | None = Field(default=None, index=True)
    legal_hold_ref: str | None = Field(default=None, index=True)
    restored_authorization: bool = Field(default=False, index=True)
    duplicate: bool = Field(default=False, index=True)
    late_worker_result_rejected: bool = Field(default=False, index=True)
    receipt_hash: str = Field(index=True)
    history_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))


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
    ParseAttemptLeaseTable,
    DocumentVersionTable,
    DocumentBlockTable,
    IndexManifestTable,
    IndexChunkTable,
    QualityGateTable,
    ReviewTaskTable,
    ReviewDecisionTable,
    IndexableSnapshotTable,
    IngestionOutboxTable,
    DeleteLifecycleTable,
    WorkspaceTaskTable,
    TaskEventTable,
    ArtifactTable,
    FeedbackTable,
]


__all__ = [
    "ArtifactTable",
    "DocumentBlockTable",
    "DocumentVersionTable",
    "DeleteLifecycleTable",
    "FeedbackTable",
    "IndexChunkTable",
    "IndexManifestTable",
    "IndexableSnapshotTable",
    "IngestionOutboxTable",
    "QualityGateTable",
    "ReviewDecisionTable",
    "ReviewTaskTable",
    "ParseJobTable",
    "ParseAttemptLeaseTable",
    "ParseSnapshotTable",
    "STORAGE_TABLES",
    "SourceObjectTable",
    "TaskEventTable",
    "WorkspaceTaskTable",
    "WorkspaceFileTable",
]
