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
    workspace_id: str
    source_uri: str
    mime_type: str
    hash: str
    parser_id: str
    parser_version: str
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)


class DocumentBlock(BaseModel):
    block_id: str
    type: str
    text: str
    source_span: SourceSpan = Field(default_factory=SourceSpan)
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


class ParseDocumentRequest(BaseModel):
    document_id: str
    workspace_id: str
    source_uri: str
    mime_type: str
    source_text: str | None = None
    source_bytes: bytes | None = None
    hash: str | None = None
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)
    parser_version: str = "phase04-runtime-v1"


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
    status: Literal["succeeded", "failed"]
    document: CanonicalDocumentIR | None = None
    failure: ParserFailure | None = None
    diagnostics: list[ParserDiagnostic] = Field(default_factory=list)
    index_handoff: IndexHandoffPayload | None = None


class ParserJobMetrics(BaseModel):
    block_count: int = 0
    table_count: int = 0
    figure_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    duration_ms: float = 0.0


class ParseJobSnapshot(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    document_id: str
    workspace_id: str
    source_uri: str
    mime_type: str
    parser_id: str
    parser_format: str
    attempt: int = 1
    retryable: bool = False
    previous_job_id: str | None = None
    failure_reason: str | None = None
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
