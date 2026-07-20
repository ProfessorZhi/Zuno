from __future__ import annotations

from pathlib import PurePosixPath
import re
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
    dependency_status: Literal["present", "missing", "disabled", "unsupported"] = "present"
    dependency_probe: dict[str, Any] = Field(default_factory=dict)
    network_policy: str = "local_only"
    privacy_gate: dict[str, Any] = Field(default_factory=dict)
    budget_gate: dict[str, Any] = Field(default_factory=dict)
    enrichment_role: Literal["source_parser", "derived_enrichment", "none"] = "source_parser"


class SourceSpan(BaseModel):
    page: int | None = None
    page_number: int | None = None
    slide: int | None = None
    sheet: str | None = None
    line_range: list[int] | None = None
    bbox: list[float] | None = None
    region_id: str | None = None
    section_path: list[str] = Field(default_factory=list)
    table_cell: str | None = None
    char_start: int | None = None
    char_end: int | None = None
    normalized_text: str | None = None
    raw_text: str | None = None
    chunk_id: str | None = None
    parent_chunk_id: str | None = None
    neighbor_chunk_ids: list[str] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    document_id: str
    source_id: str | None = None
    source_object_ref: str | None = None
    object_manifest_ref: str | None = None
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
    security_policy_ref: str | None = None
    security_epoch_ref: str | None = None


class DocumentBlock(BaseModel):
    block_id: str
    type: str
    text: str
    source_span: SourceSpan = Field(default_factory=SourceSpan)
    order_index: int | None = None
    style: dict[str, Any] = Field(default_factory=dict)
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


class TransformLedgerEntry(BaseModel):
    transform_id: str
    transform_type: Literal["extract", "normalize", "project", "enrich", "redact"]
    algorithm_version: str
    input_hash: str
    output_hash: str
    source_block_id: str | None = None
    output_block_id: str | None = None
    reversible: bool = False
    provenance: dict[str, Any] = Field(default_factory=dict)


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
    transform_ledger: list[TransformLedgerEntry] = Field(default_factory=list)
    provenance: DocumentProvenance


class ParserFailure(BaseModel):
    parser_id: str
    format: str
    reason: str
    fallback: str | None = None
    retryable: bool = False
    failure_classification: str = "parser_failure"


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
    source_object_ref: str | None = None
    source_object_manifest: dict[str, Any] = Field(default_factory=dict)
    workspace_id: str
    source_uri: str
    mime_type: str
    source_text: str | None = None
    source_bytes: bytes | None = None
    hash: str | None = None
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)
    parser_version: str = "phase05-runtime-v1"
    parser_config: dict[str, Any] = Field(default_factory=dict)
    parser_config_hash: str | None = None
    schema_version: str = "canonical-document-ir-v1"
    ir_schema_version: str = "canonical-document-ir-v1"
    parent_document_version_id: str | None = None
    derived_from: list[str] = Field(default_factory=list)
    asset_refs: list[str] = Field(default_factory=list)
    redaction_status: str = "raw"
    retention_policy: str | None = None
    security_policy_ref: str | None = None
    security_epoch_ref: str | None = None
    parser_timeout_seconds: int | None = None
    cancel_requested: bool = False


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
    confidence: float | None = None
    timeout_seconds: int | None = None
    source_input_mode: str = "inline_or_file"


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


def build_source_span_provenance(
    *,
    document: CanonicalDocumentIR,
    block: DocumentBlock,
    chunk_id: str,
    parent_chunk_id: str | None = None,
    neighbor_chunk_ids: list[str] | None = None,
) -> dict[str, Any]:
    span = block.source_span.model_dump()
    page_number = span.get("page_number") if span.get("page_number") is not None else span.get("page")
    raw_text = span.get("raw_text") if span.get("raw_text") is not None else block.text
    normalized_text = (
        span.get("normalized_text")
        if span.get("normalized_text") is not None
        else _normalize_span_text(raw_text)
    )
    return {
        **span,
        "document_id": document.metadata.document_id,
        "source_object_id": document.metadata.source_id,
        "document_version_id": document.metadata.document_version_id,
        "page_number": page_number,
        "section_path": list(block.source_span.section_path),
        "block_id": block.block_id,
        "chunk_id": chunk_id,
        "char_start": span.get("char_start"),
        "char_end": span.get("char_end"),
        "normalized_text": normalized_text,
        "raw_text": raw_text,
        "parent_chunk_id": parent_chunk_id or span.get("parent_chunk_id"),
        "neighbor_chunk_ids": list(neighbor_chunk_ids or span.get("neighbor_chunk_ids") or []),
        "source_uri": document.metadata.source_uri,
        "file_name": _file_name_from_uri(document.metadata.source_uri),
        "content_hash": document.metadata.source_sha256 or document.metadata.hash,
        "parser_name": document.metadata.parser_id,
        "parser_version": document.metadata.parser_version,
    }


def round_trip_canonical_document_ir(document: CanonicalDocumentIR) -> CanonicalDocumentIR:
    return CanonicalDocumentIR.model_validate_json(document.model_dump_json())


def canonical_document_ir_contract_report(document: CanonicalDocumentIR) -> dict[str, Any]:
    round_tripped = round_trip_canonical_document_ir(document)
    span_payloads = [block.source_span.model_dump() for block in document.blocks]
    forbidden_ir_fields = {"chunk_id", "entity_id", "relation_id", "knowledge_version_id"}
    source_span_chunk_ids_absent = all(span.get("chunk_id") is None for span in span_payloads)
    transform_ledger_complete = all(
        entry.input_hash and entry.output_hash and entry.algorithm_version
        for entry in document.transform_ledger
    )
    return {
        "schema_round_trip": round_tripped.model_dump() == document.model_dump(),
        "block_count": len(document.blocks),
        "table_count": len(document.tables),
        "figure_count": len(document.figures),
        "source_span_chunk_ids_absent": source_span_chunk_ids_absent,
        "knowledge_artifacts_absent": not forbidden_ir_fields.intersection(
            set(document.metadata.model_dump())
        ),
        "transform_ledger_count": len(document.transform_ledger),
        "transform_ledger_complete": transform_ledger_complete,
        "source_span_shapes": [
            {
                "block_id": block.block_id,
                "page": block.source_span.page or block.source_span.page_number,
                "slide": block.source_span.slide,
                "sheet": block.source_span.sheet,
                "line_range": block.source_span.line_range,
                "bbox": block.source_span.bbox,
                "region_id": block.source_span.region_id,
                "table_cell": block.source_span.table_cell,
                "section_path": list(block.source_span.section_path),
                "order_index": block.order_index,
                "style_keys": sorted(block.style),
            }
            for block in document.blocks
        ],
    }


def _normalize_span_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _file_name_from_uri(source_uri: str) -> str | None:
    if not source_uri:
        return None
    name = PurePosixPath(source_uri.replace("\\", "/")).name
    return name or None


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
    "TransformLedgerEntry",
    "build_source_span_provenance",
    "canonical_document_ir_contract_report",
    "round_trip_canonical_document_ir",
]
