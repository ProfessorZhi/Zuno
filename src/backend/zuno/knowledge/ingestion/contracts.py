from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ParserCapability(BaseModel):
    format: str
    default_parser: str
    fallback: str
    structure_kept: list[str] = Field(default_factory=list)
    evidence_anchor: list[str] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=list)
    timeout_seconds: int
    resource_budget: dict[str, Any] = Field(default_factory=dict)
    sandbox_policy: str
    fallback_reason: str


class ParserAdapterContract(BaseModel):
    parser_id: str
    family: str
    supported_formats: list[str] = Field(default_factory=list)
    operations: list[str] = Field(
        default_factory=lambda: ["supports", "parse", "diagnostics", "capabilities"]
    )
    capabilities: list[str] = Field(default_factory=list)
    capability_status: Literal[
        "current",
        "fallback-current",
        "target-blocked",
        "unknown-needs-test",
    ] = "current"
    timeout_seconds: int
    resource_budget: dict[str, Any] = Field(default_factory=dict)
    sandbox_policy: str
    fallback_reason: str
    current_runtime: Literal["deterministic_local", "external_service"] = "deterministic_local"
    production_target: str | None = None
    external_dependency_status: Literal["not_required", "target_blocked"] = "not_required"
    blocked_reason: str | None = None


class SourceSpan(BaseModel):
    page: int | None = None
    slide: int | None = None
    sheet: str | None = None
    line_range: list[int] | None = None
    bbox: list[float] | None = None
    section_path: list[str] = Field(default_factory=list)
    table_cell: str | None = None


class DocumentMetadata(BaseModel):
    document_id: str
    source_id: str | None = None
    workspace_id: str
    source_uri: str
    mime_type: str
    hash: str
    source_sha256: str = ""
    parser_id: str
    parser_version: str
    parser_config_hash: str = ""
    document_version_id: str = ""
    schema_version: str = "canonical-document-ir-v1"
    ir_schema_version: str = "canonical-document-ir-v1"
    parent_document_version_id: str | None = None
    derived_from: list[str] = Field(default_factory=list)
    asset_refs: list[str] = Field(default_factory=list)
    redaction_status: str = "raw"
    retention_policy: str | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None
    target_blocked: bool = False
    blocked_reason: str | None = None
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)


class DocumentBlock(BaseModel):
    block_id: str
    type: str
    text: str
    source_span: SourceSpan = Field(default_factory=SourceSpan)
    language: str | None = None
    code_fence: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)
    confidence: float = 1.0


class DocumentTable(BaseModel):
    table_id: str
    rows: list[list[str]] = Field(default_factory=list)
    source_span: SourceSpan = Field(default_factory=SourceSpan)
    caption: str | None = None


class DocumentFigure(BaseModel):
    figure_id: str
    description: str
    source_span: SourceSpan = Field(default_factory=SourceSpan)
    uri: str | None = None


class DocumentProvenance(BaseModel):
    parser_id: str
    parser_version: str
    source_uri: str
    confidence: float
    warnings: list[str] = Field(default_factory=list)


class CanonicalDocumentIR(BaseModel):
    metadata: DocumentMetadata
    blocks: list[DocumentBlock] = Field(default_factory=list)
    tables: list[DocumentTable] = Field(default_factory=list)
    figures: list[DocumentFigure] = Field(default_factory=list)
    provenance: DocumentProvenance


class ParserFailure(BaseModel):
    parser_id: str
    format: str
    reason: str
    fallback: str | None = None
    retryable: bool = False


class ParserDiagnostic(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "info"
    parser_id: str | None = None
    format: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParseDocumentRequest(BaseModel):
    document_id: str
    source_id: str | None = None
    workspace_id: str
    source_uri: str
    mime_type: str
    source_text: str | None = None
    source_bytes: bytes | None = None
    hash: str | None = None
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)
    parser_version: str = "phase04-runtime-v1"
    parser_config: dict[str, Any] = Field(default_factory=dict)
    parser_config_hash: str | None = None
    schema_version: str = "canonical-document-ir-v1"
    ir_schema_version: str = "canonical-document-ir-v1"
    parent_document_version_id: str | None = None
    derived_from: list[str] = Field(default_factory=list)
    asset_refs: list[str] = Field(default_factory=list)
    redaction_status: str = "raw"
    retention_policy: str | None = None


class IndexHandoffPayload(BaseModel):
    document_id: str
    workspace_id: str
    chunks: list[dict[str, Any]] = Field(default_factory=list)
    bm25_documents: list[dict[str, Any]] = Field(default_factory=list)
    vector_documents: list[dict[str, Any]] = Field(default_factory=list)
    graphrag_documents: list[dict[str, Any]] = Field(default_factory=list)
    evidence_items: list[dict[str, Any]] = Field(default_factory=list)
    citation_items: list[dict[str, Any]] = Field(default_factory=list)


class ParseDocumentResult(BaseModel):
    job_id: str
    status: Literal[
        "accepted",
        "running",
        "succeeded",
        "failed",
        "blocked",
        "retrying",
        "cancelled",
        "dead_letter",
    ]
    document: CanonicalDocumentIR | None = None
    failure: ParserFailure | None = None
    diagnostics: list[ParserDiagnostic] = Field(default_factory=list)
    index_handoff: IndexHandoffPayload | None = None


class ParserJobMetrics(BaseModel):
    status: str = "accepted"
    parser_name: str = ""
    format: str = ""
    block_count: int = 0
    table_count: int = 0
    figure_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    duration_ms: float = 0.0


class ParseJobSnapshot(BaseModel):
    job_id: str
    status: Literal[
        "accepted",
        "running",
        "succeeded",
        "failed",
        "blocked",
        "retrying",
        "cancelled",
        "dead_letter",
    ]
    document_id: str
    workspace_id: str
    source_uri: str
    mime_type: str
    parser_id: str
    parser_format: str
    attempt: int = 1
    attempt_count: int = 1
    parse_attempt_id: str = ""
    parse_idempotency_key: str = ""
    retryable: bool = False
    previous_job_id: str | None = None
    blocked_reason: str | None = None
    failure_reason: str | None = None
    error_class: str | None = None
    last_error: str | None = None
    failure_snapshot: dict[str, Any] = Field(default_factory=dict)
    parser_diagnostics: list[dict[str, Any]] = Field(default_factory=list)
    retry_policy: dict[str, Any] = Field(default_factory=dict)
    metrics: ParserJobMetrics = Field(default_factory=ParserJobMetrics)
    source_provenance: dict[str, Any] = Field(default_factory=dict)
    adapter_boundary: dict[str, Any] = Field(default_factory=dict)
    status_timeline: list[dict[str, Any]] = Field(default_factory=list)


__all__ = [
    "CanonicalDocumentIR",
    "DocumentBlock",
    "DocumentFigure",
    "DocumentMetadata",
    "DocumentProvenance",
    "DocumentTable",
    "IndexHandoffPayload",
    "ParseDocumentRequest",
    "ParseDocumentResult",
    "ParseJobSnapshot",
    "ParserAdapterContract",
    "ParserCapability",
    "ParserDiagnostic",
    "ParserFailure",
    "ParserJobMetrics",
    "SourceSpan",
]
