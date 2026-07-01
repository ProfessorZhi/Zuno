from __future__ import annotations

from pathlib import Path

from .contracts import (
    CanonicalDocumentIR,
    IndexHandoffPayload,
    ParserAdapterContract,
    ParserCapability,
)


PARSER_ADAPTER_CONTRACTS = {
    "native": ParserAdapterContract(
        parser_id="native",
        family="native parser",
        supported_formats=["txt", "md", "csv", "json", "html", "code"],
        timeout_seconds=20,
        resource_budget={"cpu": "low", "memory_mb": 256},
        sandbox_policy="read_only_workspace_file",
        fallback_reason="native parser failed or unsupported encoding",
        production_target="built-in deterministic parser",
    ),
    "docling_pymupdf": ParserAdapterContract(
        parser_id="docling_pymupdf",
        family="PDF and layout parser",
        supported_formats=["pdf"],
        timeout_seconds=90,
        resource_budget={"cpu": "medium", "memory_mb": 1024},
        sandbox_policy="isolated_parse_worker",
        fallback_reason="layout parse failed or scanned content detected",
        production_target="Docling / PyMuPDF parser worker",
        external_dependency_status="target_blocked",
        blocked_reason="production Docling / PyMuPDF worker is not deployed in this repository runtime",
    ),
    "mineru_ocr_vlm": ParserAdapterContract(
        parser_id="mineru_ocr_vlm",
        family="OCR and VLM parser",
        supported_formats=["image", "scanned"],
        timeout_seconds=180,
        resource_budget={"cpu": "high", "memory_mb": 2048, "network": "deny"},
        sandbox_policy="ocr_vlm_sandbox_with_timeout",
        fallback_reason="OCR confidence below threshold or image unsupported",
        production_target="MinerU OCR / VLM parser worker",
        external_dependency_status="target_blocked",
        blocked_reason="production OCR / VLM parser service and model runtime are not deployed locally",
    ),
    "unstructured_markitdown": ParserAdapterContract(
        parser_id="unstructured_markitdown",
        family="office and long-tail parser",
        supported_formats=["docx", "pptx", "xlsx"],
        timeout_seconds=120,
        resource_budget={"cpu": "medium", "memory_mb": 1024},
        sandbox_policy="office_parse_sandbox",
        fallback_reason="office parser failed or structure unsupported",
        production_target="Unstructured / MarkItDown parser worker",
        external_dependency_status="target_blocked",
        blocked_reason="production Unstructured / MarkItDown worker is not deployed in this repository runtime",
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
        default_parser="unstructured_markitdown",
        fallback="native",
        structure_kept=["headings", "tables"],
        evidence_anchor=["section_path", "table_cell"],
        tests=["docx_heading_table"],
        timeout_seconds=120,
        resource_budget=PARSER_ADAPTER_CONTRACTS["unstructured_markitdown"].resource_budget,
        sandbox_policy="office_parse_sandbox",
        fallback_reason="office parser failure",
    ),
    "pptx": ParserCapability(
        format="pptx",
        default_parser="unstructured_markitdown",
        fallback="mineru_ocr_vlm",
        structure_kept=["slides", "figures"],
        evidence_anchor=["slide", "bbox"],
        tests=["pptx_slide"],
        timeout_seconds=120,
        resource_budget=PARSER_ADAPTER_CONTRACTS["unstructured_markitdown"].resource_budget,
        sandbox_policy="office_parse_sandbox",
        fallback_reason="slide layout or image extraction failure",
    ),
    "xlsx": ParserCapability(
        format="xlsx",
        default_parser="unstructured_markitdown",
        fallback="native",
        structure_kept=["sheets", "tables"],
        evidence_anchor=["sheet", "table_cell"],
        tests=["xlsx_sheet"],
        timeout_seconds=120,
        resource_budget=PARSER_ADAPTER_CONTRACTS["unstructured_markitdown"].resource_budget,
        sandbox_policy="office_parse_sandbox",
        fallback_reason="sheet conversion failure",
    ),
    "txt": ParserCapability(
        format="txt",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["plain_text"],
        evidence_anchor=["line_range"],
        tests=["code_file"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="encoding detection failure",
    ),
    "md": ParserCapability(
        format="md",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["headings", "links"],
        evidence_anchor=["line_range", "section_path"],
        tests=["markdown_link"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="markdown parse failure",
    ),
    "csv": ParserCapability(
        format="csv",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["rows", "columns"],
        evidence_anchor=["line_range", "table_cell"],
        tests=["xlsx_sheet"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="delimiter or encoding failure",
    ),
    "json": ParserCapability(
        format="json",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["keys", "paths"],
        evidence_anchor=["line_range", "section_path"],
        tests=["code_file"],
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
        tests=["markdown_link"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="HTML cleanup failure",
    ),
    "image": ParserCapability(
        format="image",
        default_parser="mineru_ocr_vlm",
        fallback="unstructured_markitdown",
        structure_kept=["figures", "ocr_text"],
        evidence_anchor=["bbox"],
        tests=["scanned_image"],
        timeout_seconds=180,
        resource_budget=PARSER_ADAPTER_CONTRACTS["mineru_ocr_vlm"].resource_budget,
        sandbox_policy="ocr_vlm_sandbox_with_timeout",
        fallback_reason="OCR/VLM parser failure",
    ),
    "scanned": ParserCapability(
        format="scanned",
        default_parser="mineru_ocr_vlm",
        fallback="docling_pymupdf",
        structure_kept=["pages", "figures", "ocr_text"],
        evidence_anchor=["page", "bbox"],
        tests=["scanned_image"],
        timeout_seconds=180,
        resource_budget=PARSER_ADAPTER_CONTRACTS["mineru_ocr_vlm"].resource_budget,
        sandbox_policy="ocr_vlm_sandbox_with_timeout",
        fallback_reason="OCR confidence below threshold",
    ),
    "code": ParserCapability(
        format="code",
        default_parser="native",
        fallback="unstructured_markitdown",
        structure_kept=["line_numbers", "symbols"],
        evidence_anchor=["line_range"],
        tests=["code_file"],
        timeout_seconds=20,
        resource_budget=PARSER_ADAPTER_CONTRACTS["native"].resource_budget,
        sandbox_policy="read_only_workspace_file",
        fallback_reason="encoding or language detection failure",
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


def _chunk_payload(document: CanonicalDocumentIR, block) -> dict:
    chunk_id = f"{document.metadata.document_id}::{block.block_id}"
    metadata = {
        "document_id": document.metadata.document_id,
        "workspace_id": document.metadata.workspace_id,
        "source_uri": document.metadata.source_uri,
        "parser_id": document.metadata.parser_id,
        "parser_version": document.metadata.parser_version,
        "source_span": block.source_span.model_dump(),
        "acl_scope": block.acl_scope,
        "sensitivity_tags": list(block.sensitivity_tags),
    }
    return {
        "chunk_id": chunk_id,
        "content": block.text,
        "metadata": metadata,
    }


def build_index_handoff_payload(document: CanonicalDocumentIR) -> IndexHandoffPayload:
    chunks = [_chunk_payload(document, block) for block in document.blocks]
    return IndexHandoffPayload(
        document_id=document.metadata.document_id,
        workspace_id=document.metadata.workspace_id,
        chunks=chunks,
        bm25_documents=[
            {"chunk_id": chunk["chunk_id"], "content": chunk["content"], "metadata": chunk["metadata"]}
            for chunk in chunks
        ],
        vector_documents=[
            {"id": chunk["chunk_id"], "text": chunk["content"], "metadata": chunk["metadata"]}
            for chunk in chunks
        ],
        graphrag_documents=[
            {
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "source_chunk_id": chunk["chunk_id"],
                **chunk["metadata"],
            }
            for chunk in chunks
        ],
        evidence_items=[
            {
                "evidence_id": chunk["chunk_id"],
                "content": chunk["content"],
                "source_span": chunk["metadata"]["source_span"],
                "acl_scope": chunk["metadata"]["acl_scope"],
            }
            for chunk in chunks
        ],
        citation_items=[
            {
                "citation_id": chunk["chunk_id"],
                "document_id": document.metadata.document_id,
                "block_id": chunk["chunk_id"].split("::", 1)[-1],
                "source_span": chunk["metadata"]["source_span"],
            }
            for chunk in chunks
        ],
    )


__all__ = [
    "PARSER_ADAPTER_CONTRACTS",
    "PARSER_CAPABILITY_MATRIX",
    "build_index_handoff_payload",
    "select_parser_for_format",
]
