from __future__ import annotations

from pathlib import Path
import re

from .contracts import (
    CanonicalDocumentIR,
    IndexHandoffPayload,
    ParserAdapterContract,
    ParserCapability,
    build_source_span_provenance,
)


DEFAULT_CITATION_CHUNK_CHAR_LIMIT = 240
DEFAULT_PARENT_CONTEXT_CHAR_LIMIT = 1200


def adapter_boundary_metadata(parser_id: str, *, fallback: str | None = None) -> dict:
    contract = PARSER_ADAPTER_CONTRACTS[parser_id]
    required_packages = contract.dependency_probe.get("required_packages", [])
    provider = contract.dependency_probe.get("provider")
    return {
        "parser_id": contract.parser_id,
        "capability_status": contract.capability_status,
        "external_dependency_status": contract.external_dependency_status,
        "dependency_status": contract.dependency_status,
        "provider": provider,
        "required_packages": required_packages,
        "dependency_probe": dict(contract.dependency_probe),
        "production_target": contract.production_target,
        "blocked_reason": contract.blocked_reason,
        "network_policy": contract.network_policy,
        "privacy_gate": dict(contract.privacy_gate),
        "budget_gate": dict(contract.budget_gate),
        "enrichment_role": contract.enrichment_role,
        "fallback": fallback,
    }


PARSER_ADAPTER_CONTRACTS = {
    "native": ParserAdapterContract(
        parser_id="native",
        family="native parser",
        supported_formats=["txt", "md", "csv", "json", "html", "code"],
        capabilities=["txt", "md", "csv", "json", "html", "code"],
        capability_status="current",
        timeout_seconds=20,
        resource_budget={"cpu": "low", "memory_mb": 256},
        sandbox_policy="read_only_workspace_file",
        fallback_reason="native parser failed or unsupported encoding",
        production_target="built-in deterministic parser",
        dependency_status="present",
        dependency_probe={
            "provider": "builtin",
            "required_packages": [],
            "status_reason": "implemented in repository with Python standard library helpers",
        },
        network_policy="local_only",
        privacy_gate={
            "sensitive_input_policy": "workspace_acl",
            "source_truth_policy": "deterministic_source_parser",
        },
        budget_gate={
            "max_pages": 0,
            "max_images": 0,
            "network_default": "deny",
            "review_required": False,
        },
    ),
    "docling_pymupdf": ParserAdapterContract(
        parser_id="docling_pymupdf",
        family="PDF and layout parser",
        supported_formats=["pdf"],
        capabilities=["pdf"],
        capability_status="fallback-current",
        timeout_seconds=90,
        resource_budget={"cpu": "medium", "memory_mb": 1024},
        sandbox_policy="isolated_parse_worker",
        fallback_reason="scanned content detected or layout extraction failed",
        production_target="Docling layout enrichment and OCR/VLM parser worker",
        external_dependency_status="not_required",
        blocked_reason=None,
        dependency_status="present",
        dependency_probe={
            "provider": "external_python_packages",
            "required_packages": ["pymupdf"],
            "status_reason": "local PyMuPDF text PDF parsing is available; Docling layout enrichment and OCR/VLM remain future targets",
        },
        network_policy="local_only",
        privacy_gate={
            "sensitive_input_policy": "deny_by_default",
            "source_truth_policy": "deterministic_layout_parser",
        },
        budget_gate={
            "max_pages": 50,
            "max_images": 0,
            "network_default": "deny",
            "review_required": False,
        },
    ),
    "mineru_ocr_vlm": ParserAdapterContract(
        parser_id="mineru_ocr_vlm",
        family="OCR and VLM parser",
        supported_formats=["image", "scanned"],
        capabilities=["image", "scanned"],
        capability_status="target-blocked",
        timeout_seconds=180,
        resource_budget={"cpu": "high", "memory_mb": 2048, "network": "deny"},
        sandbox_policy="ocr_vlm_sandbox_with_timeout",
        fallback_reason="OCR confidence below threshold or image unsupported",
        production_target="MinerU OCR / VLM parser worker",
        external_dependency_status="target_blocked",
        blocked_reason="production OCR / VLM parser service and model runtime are not deployed locally",
        dependency_status="missing",
        dependency_probe={
            "provider": "external_ocr_vlm_runtime",
            "required_packages": ["mineru", "paddleocr", "vlm_runtime"],
            "status_reason": "OCR / VLM service, model weights, and production worker are not deployed locally",
        },
        network_policy="deny_by_default",
        privacy_gate={
            "sensitive_input_policy": "deny_by_default",
            "source_truth_policy": "cannot_override_deterministic_source",
            "requires_human_review": True,
        },
        budget_gate={
            "max_pages": 0,
            "max_images": 0,
            "max_cost_usd": 0.0,
            "network_default": "deny",
            "review_required": True,
        },
        enrichment_role="derived_enrichment",
    ),
    "local_ocr_vlm": ParserAdapterContract(
        parser_id="local_ocr_vlm",
        family="local OCR and VLM fallback parser",
        supported_formats=["image", "scanned"],
        capabilities=["image", "scanned", "ocr_text", "figure_bbox", "review_required"],
        capability_status="current",
        timeout_seconds=30,
        resource_budget={"cpu": "low", "memory_mb": 256, "network": "deny"},
        sandbox_policy="read_only_workspace_file",
        fallback_reason="local OCR text extraction failed or review threshold not met",
        production_target="deterministic local OCR/VLM fallback before external MinerU deployment",
        external_dependency_status="not_required",
        blocked_reason=None,
        dependency_status="present",
        dependency_probe={
            "provider": "builtin",
            "required_packages": [],
            "status_reason": "deterministic repository adapter parses provided OCR text or decoded local bytes without network access",
            "live_provider": "mineru_ocr_vlm",
            "live_provider_status": "measurement_blocked",
        },
        network_policy="deny_by_default",
        privacy_gate={
            "sensitive_input_policy": "workspace_acl",
            "source_truth_policy": "local_ocr_requires_review_for_high_risk_use",
            "requires_human_review": True,
        },
        budget_gate={
            "max_pages": 0,
            "max_images": 1,
            "max_cost_usd": 0.0,
            "network_default": "deny",
            "review_required": True,
        },
        enrichment_role="derived_enrichment",
    ),
    "unstructured_markitdown": ParserAdapterContract(
        parser_id="unstructured_markitdown",
        family="office and long-tail parser",
        supported_formats=["docx", "pptx", "xlsx"],
        capabilities=["docx", "pptx", "xlsx", "unknown"],
        capability_status="target-blocked",
        timeout_seconds=120,
        resource_budget={"cpu": "medium", "memory_mb": 1024},
        sandbox_policy="office_parse_sandbox",
        fallback_reason="office parser failed or structure unsupported",
        production_target="Unstructured / MarkItDown parser worker",
        external_dependency_status="target_blocked",
        blocked_reason="production Unstructured / MarkItDown worker is not deployed in this repository runtime",
        dependency_status="missing",
        dependency_probe={
            "provider": "external_python_packages",
            "required_packages": ["unstructured", "markitdown"],
            "status_reason": "production office parser worker packages are not part of this repository runtime",
        },
        network_policy="local_only",
        privacy_gate={
            "sensitive_input_policy": "deny_by_default",
            "source_truth_policy": "deterministic_office_parser",
        },
        budget_gate={
            "max_pages": 50,
            "max_images": 0,
            "network_default": "deny",
            "review_required": False,
        },
    ),
    "local_office_archive": ParserAdapterContract(
        parser_id="local_office_archive",
        family="local office and archive fallback parser",
        supported_formats=["docx", "pptx", "xlsx", "archive"],
        capabilities=[
            "docx",
            "pptx",
            "xlsx",
            "archive",
            "headings",
            "tables",
            "slides",
            "archive_manifest",
        ],
        capability_status="current",
        timeout_seconds=30,
        resource_budget={"cpu": "low", "memory_mb": 256, "network": "deny"},
        sandbox_policy="read_only_workspace_file",
        fallback_reason="local office/archive text projection failed or unsupported container",
        production_target="deterministic local Office/Archive fallback before Unstructured / MarkItDown deployment",
        external_dependency_status="not_required",
        blocked_reason=None,
        dependency_status="present",
        dependency_probe={
            "provider": "builtin",
            "required_packages": [],
            "status_reason": "deterministic repository adapter parses supplied text projections and archive manifests without network access",
            "live_provider": "unstructured_markitdown",
            "live_provider_status": "measurement_blocked",
        },
        network_policy="local_only",
        privacy_gate={
            "sensitive_input_policy": "workspace_acl",
            "source_truth_policy": "local_projection_keeps_source_object_as_truth",
        },
        budget_gate={
            "max_pages": 50,
            "max_images": 0,
            "max_cost_usd": 0.0,
            "network_default": "deny",
            "review_required": False,
        },
    ),
}


PARSER_CAPABILITY_MATRIX = {
    "pdf": ParserCapability(
        format="pdf",
        default_parser="docling_pymupdf",
        fallback="mineru_ocr_vlm",
        structure_kept=["pages", "tables", "layout"],
        evidence_anchor=["page", "bbox", "section_path"],
        tests=["pdf_table"],
        timeout_seconds=90,
        resource_budget=PARSER_ADAPTER_CONTRACTS["docling_pymupdf"].resource_budget,
        sandbox_policy="isolated_parse_worker",
        fallback_reason="scanned PDF or layout parse failure",
    ),
    "docx": ParserCapability(
        format="docx",
        default_parser="local_office_archive",
        fallback="unstructured_markitdown",
        structure_kept=["headings", "tables"],
        evidence_anchor=["section_path", "table_cell"],
        tests=["docx_heading_table"],
        timeout_seconds=120,
        resource_budget=PARSER_ADAPTER_CONTRACTS["local_office_archive"].resource_budget,
        sandbox_policy="office_parse_sandbox",
        fallback_reason="office parser failure",
    ),
    "pptx": ParserCapability(
        format="pptx",
        default_parser="local_office_archive",
        fallback="unstructured_markitdown",
        structure_kept=["slides", "figures"],
        evidence_anchor=["slide", "bbox"],
        tests=["pptx_slide"],
        timeout_seconds=120,
        resource_budget=PARSER_ADAPTER_CONTRACTS["local_office_archive"].resource_budget,
        sandbox_policy="office_parse_sandbox",
        fallback_reason="slide layout or image extraction failure",
    ),
    "xlsx": ParserCapability(
        format="xlsx",
        default_parser="local_office_archive",
        fallback="unstructured_markitdown",
        structure_kept=["sheets", "tables"],
        evidence_anchor=["sheet", "table_cell"],
        tests=["xlsx_sheet"],
        timeout_seconds=120,
        resource_budget=PARSER_ADAPTER_CONTRACTS["local_office_archive"].resource_budget,
        sandbox_policy="office_parse_sandbox",
        fallback_reason="sheet conversion failure",
    ),
    "txt": ParserCapability(
        format="txt",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["plain_text"],
        evidence_anchor=["line_range"],
        tests=["plain_text"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="encoding detection failure",
    ),
    "md": ParserCapability(
        format="md",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["headings", "links", "code_fences", "tables"],
        evidence_anchor=["line_range", "section_path", "table_cell"],
        tests=["markdown_link", "markdown_structured"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="markdown parse failure",
    ),
    "csv": ParserCapability(
        format="csv",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["rows", "columns", "table_cells"],
        evidence_anchor=["line_range", "table_cell"],
        tests=["csv_table"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="delimiter or encoding failure",
    ),
    "json": ParserCapability(
        format="json",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["objects", "arrays", "values", "json_pointer"],
        evidence_anchor=["line_range", "section_path"],
        tests=["json_policy"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="invalid JSON or encoding failure",
    ),
    "html": ParserCapability(
        format="html",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["headings", "links", "tables"],
        evidence_anchor=["section_path", "line_range"],
        tests=["html_policy"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="HTML cleanup failure",
    ),
    "image": ParserCapability(
        format="image",
        default_parser="local_ocr_vlm",
        fallback="mineru_ocr_vlm",
        structure_kept=["figures", "ocr_text"],
        evidence_anchor=["bbox"],
        tests=["scanned_image"],
        timeout_seconds=180,
        resource_budget=PARSER_ADAPTER_CONTRACTS["local_ocr_vlm"].resource_budget,
        sandbox_policy="ocr_vlm_sandbox_with_timeout",
        fallback_reason="OCR/VLM parser failure",
    ),
    "scanned": ParserCapability(
        format="scanned",
        default_parser="local_ocr_vlm",
        fallback="mineru_ocr_vlm",
        structure_kept=["pages", "figures", "ocr_text"],
        evidence_anchor=["page", "bbox"],
        tests=["scanned_image"],
        timeout_seconds=180,
        resource_budget=PARSER_ADAPTER_CONTRACTS["local_ocr_vlm"].resource_budget,
        sandbox_policy="ocr_vlm_sandbox_with_timeout",
        fallback_reason="OCR confidence below threshold",
    ),
    "code": ParserCapability(
        format="code",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["line_numbers", "imports", "classes", "functions", "symbols"],
        evidence_anchor=["line_range"],
        tests=["code_file"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="encoding or language detection failure",
    ),
    "archive": ParserCapability(
        format="archive",
        default_parser="local_office_archive",
        fallback="unstructured_markitdown",
        structure_kept=["archive_entries", "manifest", "paths"],
        evidence_anchor=["source_uri", "line_range"],
        tests=["archive_manifest"],
        timeout_seconds=30,
        resource_budget=PARSER_ADAPTER_CONTRACTS["local_office_archive"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="archive manifest projection failure",
    ),
}

_EXTENSION_FORMATS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".pptx": "pptx",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
    ".txt": "txt",
    ".md": "md",
    ".mdx": "md",
    ".csv": "csv",
    ".json": "json",
    ".html": "html",
    ".htm": "html",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".bmp": "image",
    ".webp": "image",
    ".tiff": "image",
    ".zip": "archive",
    ".tar": "archive",
    ".tgz": "archive",
    ".gz": "archive",
    ".rar": "archive",
    ".py": "code",
    ".ts": "code",
    ".js": "code",
    ".java": "code",
    ".go": "code",
}


def select_parser_for_format(format_or_path: str) -> ParserCapability:
    normalized = format_or_path.strip().lower()
    suffix = Path(normalized).suffix
    format_name = _EXTENSION_FORMATS.get(suffix) or normalized.lstrip(".")
    return PARSER_CAPABILITY_MATRIX.get(
        format_name,
        ParserCapability(
            format=format_name or "unknown",
            default_parser="unstructured_markitdown",
            fallback="unstructured_markitdown",
            structure_kept=["best_effort_text"],
            evidence_anchor=["source_uri"],
            tests=["long_tail_fallback"],
            timeout_seconds=120,
            resource_budget=PARSER_ADAPTER_CONTRACTS["unstructured_markitdown"].resource_budget,
            sandbox_policy="office_parse_sandbox",
            fallback_reason="unknown format",
        ),
    )


def _base_metadata(document: CanonicalDocumentIR, block, chunk_id: str, source_span: dict) -> dict:
    return {
        "document_id": document.metadata.document_id,
        "source_object_id": document.metadata.source_id,
        "workspace_id": document.metadata.workspace_id,
        "source_uri": document.metadata.source_uri,
        "document_version_id": document.metadata.document_version_id,
        "content_hash": document.metadata.source_sha256 or document.metadata.hash,
        "parser_id": document.metadata.parser_id,
        "parser_name": document.metadata.parser_id,
        "parser_version": document.metadata.parser_version,
        "block_id": block.block_id,
        "chunk_id": chunk_id,
        "source_span": source_span,
        "acl_scope": block.acl_scope,
        "sensitivity_tags": list(block.sensitivity_tags),
    }


def _parent_chunk_payload(document: CanonicalDocumentIR, block, citation_chunk_ids: list[str]) -> dict:
    chunk_id = f"{document.metadata.document_id}::{block.block_id}"
    source_span = build_source_span_provenance(
        document=document,
        block=block,
        chunk_id=chunk_id,
        neighbor_chunk_ids=citation_chunk_ids,
    )
    metadata = _base_metadata(document, block, chunk_id, source_span)
    metadata.update(
        {
            "chunk_role": "parent_context",
            "citation_chunk_ids": list(citation_chunk_ids),
            "citation_chunking": _chunking_metadata(),
        }
    )
    return {
        "chunk_id": chunk_id,
        "content": block.text,
        "source_span": source_span,
        "metadata": metadata,
    }


def _citation_chunk_payloads(document: CanonicalDocumentIR, block) -> list[dict]:
    parent_chunk_id = f"{document.metadata.document_id}::{block.block_id}"
    units = _citation_units(block.text)
    chunk_ids = [f"{parent_chunk_id}::cite{index}" for index, _unit in enumerate(units, start=1)]
    payloads = []
    base_char_start = block.source_span.char_start or 0
    for index, unit in enumerate(units):
        chunk_id = chunk_ids[index]
        neighbor_chunk_ids = []
        if index > 0:
            neighbor_chunk_ids.append(chunk_ids[index - 1])
        if index + 1 < len(chunk_ids):
            neighbor_chunk_ids.append(chunk_ids[index + 1])
        span = block.source_span.model_copy(
            update={
                "char_start": base_char_start + unit["char_start"],
                "char_end": base_char_start + unit["char_end"],
                "raw_text": unit["text"],
                "normalized_text": _normalize_chunk_text(unit["text"]),
                "chunk_id": chunk_id,
                "parent_chunk_id": parent_chunk_id,
                "neighbor_chunk_ids": neighbor_chunk_ids,
            }
        )
        source_span = build_source_span_provenance(
            document=document,
            block=block.model_copy(update={"text": unit["text"], "source_span": span}),
            chunk_id=chunk_id,
            parent_chunk_id=parent_chunk_id,
            neighbor_chunk_ids=neighbor_chunk_ids,
        )
        metadata = _base_metadata(document, block, chunk_id, source_span)
        metadata.update(
            {
                "chunk_role": "citation",
                "parent_chunk_id": parent_chunk_id,
                "neighbor_chunk_ids": neighbor_chunk_ids,
                "parent_context": block.text[:DEFAULT_PARENT_CONTEXT_CHAR_LIMIT],
                "citation_chunking": _chunking_metadata(),
            }
        )
        payloads.append(
            {
                "chunk_id": chunk_id,
                "content": unit["text"],
                "source_span": source_span,
                "metadata": metadata,
            }
        )
    return payloads


def _chunk_payloads(document: CanonicalDocumentIR, block) -> list[dict]:
    citation_chunks = _citation_chunk_payloads(document, block)
    parent = _parent_chunk_payload(
        document,
        block,
        citation_chunk_ids=[chunk["chunk_id"] for chunk in citation_chunks],
    )
    return [parent, *citation_chunks]


def _citation_units(text: str) -> list[dict]:
    stripped = text.strip()
    if not stripped:
        return [{"text": "", "char_start": 0, "char_end": 0}]
    matches = list(re.finditer(r".+?(?:[.!?](?=\s|$)|$)", text, flags=re.DOTALL))
    units: list[dict] = []
    for match in matches or [re.match(r".*", text)]:
        if match is None:
            continue
        raw = match.group(0).strip()
        if not raw:
            continue
        start = text.find(raw, match.start(), match.end())
        units.extend(_split_long_unit(raw, start if start >= 0 else match.start()))
    return units or [{"text": stripped, "char_start": 0, "char_end": len(stripped)}]


def _split_long_unit(text: str, start: int) -> list[dict]:
    if len(text) <= DEFAULT_CITATION_CHUNK_CHAR_LIMIT:
        return [{"text": text, "char_start": start, "char_end": start + len(text)}]
    units = []
    offset = 0
    while offset < len(text):
        piece = text[offset : offset + DEFAULT_CITATION_CHUNK_CHAR_LIMIT].strip()
        if piece:
            piece_start = start + offset + (len(text[offset : offset + DEFAULT_CITATION_CHUNK_CHAR_LIMIT]) - len(text[offset : offset + DEFAULT_CITATION_CHUNK_CHAR_LIMIT].lstrip()))
            units.append(
                {
                    "text": piece,
                    "char_start": piece_start,
                    "char_end": piece_start + len(piece),
                }
            )
        offset += DEFAULT_CITATION_CHUNK_CHAR_LIMIT
    return units


def _normalize_chunk_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _chunking_metadata() -> dict:
    return {
        "strategy": "citation_sized_with_parent_context",
        "citation_chunk_char_limit": DEFAULT_CITATION_CHUNK_CHAR_LIMIT,
        "parent_context_char_limit": DEFAULT_PARENT_CONTEXT_CHAR_LIMIT,
        "boundary_priority": ["section", "paragraph", "sentence", "table_cell", "code_block", "character"],
    }


def build_index_handoff_payload(document: CanonicalDocumentIR) -> IndexHandoffPayload:
    chunks = [
        chunk
        for block in document.blocks
        for chunk in _chunk_payloads(document, block)
    ]
    citation_chunks = [chunk for chunk in chunks if chunk["metadata"]["chunk_role"] == "citation"]
    return IndexHandoffPayload(
        document_id=document.metadata.document_id,
        workspace_id=document.metadata.workspace_id,
        chunks=chunks,
        bm25_documents=[
            {"chunk_id": chunk["chunk_id"], "content": chunk["content"], "metadata": chunk["metadata"]}
            for chunk in citation_chunks
        ],
        vector_documents=[
            {"id": chunk["chunk_id"], "text": chunk["content"], "metadata": chunk["metadata"]}
            for chunk in citation_chunks
        ],
        graphrag_documents=[
            {
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "source_chunk_id": chunk["chunk_id"],
                **chunk["metadata"],
            }
            for chunk in citation_chunks
        ],
        evidence_items=[
            {
                "evidence_id": chunk["chunk_id"],
                "content": chunk["content"],
                "source_span": chunk["metadata"]["source_span"],
                "document_id": document.metadata.document_id,
                "block_id": chunk["metadata"]["block_id"],
                "chunk_id": chunk["chunk_id"],
                "document_version_id": document.metadata.document_version_id,
                "acl_scope": chunk["metadata"]["acl_scope"],
            }
            for chunk in citation_chunks
        ],
        citation_items=[
            {
                "citation_id": chunk["chunk_id"],
                "document_id": document.metadata.document_id,
                "block_id": chunk["chunk_id"].split("::", 1)[-1],
                "chunk_id": chunk["chunk_id"],
                "document_version_id": document.metadata.document_version_id,
                "source_span": chunk["metadata"]["source_span"],
            }
            for chunk in citation_chunks
        ],
    )


__all__ = [
    "PARSER_ADAPTER_CONTRACTS",
    "PARSER_CAPABILITY_MATRIX",
    "adapter_boundary_metadata",
    "build_index_handoff_payload",
    "select_parser_for_format",
]
