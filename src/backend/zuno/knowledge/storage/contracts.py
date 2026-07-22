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


class ParseAttemptLeaseRecord(BaseModel):
    parse_attempt_id: str
    parse_job_id: str
    worker_id: str
    attempt_no: int
    fencing_token: int
    state: str
    heartbeat_at: float
    lease_expires_at: float
    lease_lost_reason: str | None = None
    domain_commit_ref: str | None = None
    idempotency_key: str | None = None
    duplicate_commit: bool = False
    late_result_rejected: bool = False
    orphan_reconciled: bool = False
    receipt_hash: str
    history: list[str] = Field(default_factory=list)


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


class DocumentBlockRecord(BaseModel):
    document_version_id: str
    block_id: str
    workspace_id: str
    document_id: str
    block_type: str
    text: str
    source_span: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)


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


class QualityGateRecord(BaseModel):
    quality_decision_id: str
    parse_snapshot_id: str
    document_version_id: str
    workspace_id: str
    verdict: str
    decision_hash: str
    review_task_id: str | None = None
    metrics: list[dict[str, Any]] = Field(default_factory=list)


class ReviewTaskRecord(BaseModel):
    review_task_id: str
    parse_snapshot_id: str
    document_version_id: str
    workspace_id: str
    reviewer_scope: str
    security_epoch_ref: str
    status: str = "pending"
    expires_at: float
    reason: str
    decision_hash: str


class ReviewDecisionRecord(BaseModel):
    decision_id: str
    review_task_id: str
    status: str
    reviewer_id: str
    reviewer_scope: str
    security_epoch_ref: str
    decision_hash: str
    duplicate: bool = False
    reason: str = ""
    decided_at: float


class IndexableSnapshotRecord(BaseModel):
    indexable_snapshot_id: str
    document_version_id: str
    parse_snapshot_id: str
    quality_decision_id: str
    workspace_id: str
    document_id: str
    canonical_hash: str
    idempotency_key: str
    security_refs: dict[str, Any] = Field(default_factory=dict)
    delete_refs: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)


class IngestionOutboxRecord(BaseModel):
    outbox_event_id: str
    aggregate_ref: str
    event_type: str
    payload_hash: str
    idempotency_key: str
    publish_status: str = "pending"
    replay_count: int = 0


class DeleteLifecycleRecord(BaseModel):
    delete_ref: str
    snapshot_ref: str
    state: str
    visibility_ref: str
    cleanup_ref: str | None = None
    physical_delete_ref: str | None = None
    verification_ref: str | None = None
    legal_hold_ref: str | None = None
    restored_authorization: bool = False
    duplicate: bool = False
    late_worker_result_rejected: bool = False
    receipt_hash: str
    history: list[str] = Field(default_factory=list)


class WorkspaceTaskRecord(BaseModel):
    task_id: str
    workspace_id: str
    owner_id: str | None = None
    status: str
    trace_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskEventRecord(BaseModel):
    event_id: str
    task_id: str
    trace_id: str
    event_type: str
    timestamp: float
    payload: dict[str, Any] = Field(default_factory=dict)


class ArtifactRecord(BaseModel):
    artifact_id: str
    task_id: str
    workspace_id: str
    owner_id: str | None = None
    kind: str
    uri: str
    content: str
    content_sha256: str
    trace_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class FeedbackRecord(BaseModel):
    feedback_id: str
    task_id: str
    rating: int | None = None
    label: str | None = None
    comment: str | None = None
    dataset_candidate: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "ArtifactRecord",
    "DocumentBlockRecord",
    "DocumentVersionRecord",
    "DeleteLifecycleRecord",
    "FeedbackRecord",
    "IndexChunkRecord",
    "IndexableSnapshotRecord",
    "IngestionOutboxRecord",
    "ParseAttemptLeaseRecord",
    "ParseJobRecord",
    "QualityGateRecord",
    "ReviewDecisionRecord",
    "ReviewTaskRecord",
    "SourceObjectRecord",
    "TaskEventRecord",
    "WorkspaceFileRecord",
    "WorkspaceTaskRecord",
]
