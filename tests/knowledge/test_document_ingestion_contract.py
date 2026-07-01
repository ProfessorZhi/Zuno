from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_parser_capability_matrix_covers_phase04_formats() -> None:
    from zuno.knowledge.ingestion import PARSER_CAPABILITY_MATRIX

    expected_formats = {
        "pdf",
        "docx",
        "pptx",
        "xlsx",
        "txt",
        "md",
        "csv",
        "json",
        "html",
        "image",
        "scanned",
        "code",
    }

    assert expected_formats.issubset(set(PARSER_CAPABILITY_MATRIX))
    for format_name in expected_formats:
        capability = PARSER_CAPABILITY_MATRIX[format_name]
        dumped = capability.model_dump()
        for field in [
            "format",
            "default_parser",
            "fallback",
            "structure_kept",
            "evidence_anchor",
            "tests",
            "timeout_seconds",
            "resource_budget",
            "sandbox_policy",
        ]:
            assert dumped[field], f"{format_name} missing {field}"


def test_parser_router_selects_default_and_fallback_contracts() -> None:
    from zuno.knowledge.ingestion import select_parser_for_format

    assert select_parser_for_format("contract.pdf").default_parser == "docling_pymupdf"
    assert select_parser_for_format("scan.png").default_parser == "mineru_ocr_vlm"
    assert select_parser_for_format("slides.pptx").default_parser == "unstructured_markitdown"
    assert select_parser_for_format("notes.md").default_parser == "native"
    assert select_parser_for_format("unknown.bin").fallback == "unstructured_markitdown"


def test_parser_adapter_contracts_mark_external_engines_as_target_boundary() -> None:
    from zuno.knowledge.ingestion import PARSER_ADAPTER_CONTRACTS

    assert PARSER_ADAPTER_CONTRACTS["native"].external_dependency_status == "not_required"
    for parser_id in ["docling_pymupdf", "mineru_ocr_vlm", "unstructured_markitdown"]:
        contract = PARSER_ADAPTER_CONTRACTS[parser_id]
        assert contract.current_runtime == "deterministic_local"
        assert contract.external_dependency_status == "target_blocked"
        assert contract.production_target
        assert contract.blocked_reason


def test_canonical_document_ir_keeps_provenance_acl_and_source_span() -> None:
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
    )

    ir = CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_1",
            workspace_id="workspace_1",
            source_uri="s3://bucket/contract.pdf",
            mime_type="application/pdf",
            hash="sha256:abc",
            parser_id="docling_pymupdf",
            parser_version="contract-v1",
            acl_scope="workspace",
            sensitivity_tags=["confidential"],
        ),
        blocks=[
            DocumentBlock(
                block_id="block_1",
                type="paragraph",
                text="Payment is due in 30 days.",
                source_span=SourceSpan(page=3, bbox=[10.0, 20.0, 300.0, 360.0]),
                acl_scope="workspace",
                sensitivity_tags=["confidential"],
                confidence=0.97,
            )
        ],
        provenance=DocumentProvenance(
            parser_id="docling_pymupdf",
            parser_version="contract-v1",
            source_uri="s3://bucket/contract.pdf",
            confidence=0.97,
        ),
    )

    dumped = ir.model_dump()
    assert dumped["metadata"]["document_id"] == "doc_1"
    assert dumped["blocks"][0]["source_span"]["page"] == 3
    assert dumped["blocks"][0]["source_span"]["bbox"] == [10.0, 20.0, 300.0, 360.0]
    assert dumped["blocks"][0]["acl_scope"] == "workspace"
    assert dumped["provenance"]["parser_id"] == "docling_pymupdf"


def test_index_handoff_payload_targets_retrieval_graphrag_and_citation() -> None:
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
        build_index_handoff_payload,
    )

    ir = CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_contract",
            workspace_id="workspace_1",
            source_uri="file://contract.md",
            mime_type="text/markdown",
            hash="sha256:def",
            parser_id="native",
            parser_version="contract-v1",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_payment",
                type="paragraph",
                text="The supplier must provide invoices monthly.",
                source_span=SourceSpan(line_range=[12, 14], section_path=["Payment"]),
            )
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="contract-v1",
            source_uri="file://contract.md",
            confidence=1.0,
        ),
    )

    handoff = build_index_handoff_payload(ir).model_dump()
    assert handoff["document_id"] == "doc_contract"
    assert handoff["bm25_documents"][0]["content"]
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["line_range"] == [12, 14]
    assert handoff["graphrag_documents"][0]["chunk_id"] == "doc_contract::block_payment"
    assert handoff["evidence_items"][0]["evidence_id"] == "doc_contract::block_payment"
    assert handoff["citation_items"][0]["source_span"]["section_path"] == ["Payment"]


def test_parser_golden_fixture_manifest_is_complete() -> None:
    manifest_path = REPO_ROOT / "tests/fixtures/parser_golden/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert {case["case_id"] for case in manifest["cases"]} == {
        "pdf_table",
        "scanned_image",
        "pptx_slide",
        "docx_heading_table",
        "xlsx_sheet",
        "code_file",
        "markdown_link",
    }
    for case in manifest["cases"]:
        for field in ["format", "input_path", "default_parser", "evidence_anchor", "expected_blocks"]:
            assert case[field], f"{case['case_id']} missing {field}"
        assert (manifest_path.parent / case["input_path"]).exists()
