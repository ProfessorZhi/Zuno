from __future__ import annotations

import json
from pathlib import Path
import hashlib


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
    assert select_parser_for_format("scan.png").default_parser == "local_ocr_vlm"
    assert select_parser_for_format("slides.pptx").default_parser == "unstructured_markitdown"
    assert select_parser_for_format("notes.md").default_parser == "native"
    assert select_parser_for_format("unknown.bin").fallback == "unstructured_markitdown"


def test_parser_adapter_contracts_mark_external_engines_as_target_boundary() -> None:
    from zuno.knowledge.ingestion import PARSER_ADAPTER_CONTRACTS

    assert PARSER_ADAPTER_CONTRACTS["native"].external_dependency_status == "not_required"
    pdf_contract = PARSER_ADAPTER_CONTRACTS["docling_pymupdf"]
    assert pdf_contract.capability_status == "fallback-current"
    assert pdf_contract.external_dependency_status == "not_required"
    assert pdf_contract.dependency_status == "present"
    assert pdf_contract.blocked_reason is None
    assert "pymupdf" in pdf_contract.dependency_probe["required_packages"]

    for parser_id in ["mineru_ocr_vlm", "unstructured_markitdown"]:
        contract = PARSER_ADAPTER_CONTRACTS[parser_id]
        assert contract.current_runtime == "deterministic_local"
        assert contract.external_dependency_status == "target_blocked"
        assert contract.production_target
        assert contract.blocked_reason

    local_ocr_contract = PARSER_ADAPTER_CONTRACTS["local_ocr_vlm"]
    assert local_ocr_contract.current_runtime == "deterministic_local"
    assert local_ocr_contract.external_dependency_status == "not_required"
    assert local_ocr_contract.dependency_status == "present"
    assert local_ocr_contract.budget_gate["review_required"] is True


def test_parser_adapter_contract_exposes_runtime_operations_and_capabilities() -> None:
    from zuno.knowledge.ingestion import PARSER_ADAPTER_CONTRACTS, get_parser_adapter

    native_contract = PARSER_ADAPTER_CONTRACTS["native"]
    assert native_contract.operations == ["supports", "parse", "diagnostics", "capabilities"]
    assert native_contract.capability_status == "current"
    assert "md" in native_contract.capabilities

    native_adapter = get_parser_adapter("native")
    assert native_adapter.supports("md") is True
    assert native_adapter.supports("pdf") is False
    assert "code" in native_adapter.capabilities()

    blocked_contract = PARSER_ADAPTER_CONTRACTS["mineru_ocr_vlm"]
    assert blocked_contract.capability_status == "target-blocked"
    assert blocked_contract.blocked_reason

    local_ocr_contract = PARSER_ADAPTER_CONTRACTS["local_ocr_vlm"]
    assert local_ocr_contract.capability_status == "current"
    assert local_ocr_contract.blocked_reason is None
    assert get_parser_adapter("local_ocr_vlm").supports("image") is True


def test_external_parser_contracts_freeze_dependency_and_enrichment_boundaries() -> None:
    from zuno.knowledge.ingestion import PARSER_ADAPTER_CONTRACTS

    native_contract = PARSER_ADAPTER_CONTRACTS["native"]
    assert native_contract.dependency_status == "present"
    assert native_contract.dependency_probe["provider"] == "builtin"

    pdf_contract = PARSER_ADAPTER_CONTRACTS["docling_pymupdf"]
    assert pdf_contract.capability_status == "fallback-current"
    assert pdf_contract.external_dependency_status == "not_required"
    assert pdf_contract.dependency_status == "present"
    assert pdf_contract.network_policy == "local_only"
    assert pdf_contract.privacy_gate["sensitive_input_policy"] == "deny_by_default"

    for parser_id in ["unstructured_markitdown", "mineru_ocr_vlm"]:
        contract = PARSER_ADAPTER_CONTRACTS[parser_id]
        assert contract.capability_status == "target-blocked"
        assert contract.external_dependency_status == "target_blocked"
        assert contract.dependency_status == "missing"
        assert contract.dependency_probe["required_packages"]
        assert contract.network_policy in {"local_only", "deny_by_default"}
        assert contract.privacy_gate["sensitive_input_policy"] == "deny_by_default"
        assert contract.budget_gate["max_pages"] >= 0

    local_ocr_contract = PARSER_ADAPTER_CONTRACTS["local_ocr_vlm"]
    assert local_ocr_contract.capability_status == "current"
    assert local_ocr_contract.external_dependency_status == "not_required"
    assert local_ocr_contract.dependency_status == "present"
    assert local_ocr_contract.network_policy == "deny_by_default"
    assert local_ocr_contract.budget_gate["review_required"] is True

    ocr_contract = PARSER_ADAPTER_CONTRACTS["mineru_ocr_vlm"]
    assert ocr_contract.enrichment_role == "derived_enrichment"
    assert ocr_contract.privacy_gate["source_truth_policy"] == "cannot_override_deterministic_source"
    assert ocr_contract.budget_gate["network_default"] == "deny"


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


def test_parse_gateway_freezes_document_version_and_schema_fields() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    source_text = "# Policy\nRenewal notice is required."
    parser_config = {"chunking": "line", "normalizer": "deterministic"}
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    parser_config_hash = hashlib.sha256(
        json.dumps(parser_config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_policy",
            source_id="source_policy_md",
            workspace_id="workspace_contract",
            source_uri="file://policies/renewal.md",
            mime_type="text/markdown",
            source_text=source_text,
            parser_version="contract-v2",
            parser_config=parser_config,
            asset_refs=["file://policies/renewal.md"],
            retention_policy="workspace_default",
            redaction_status="raw",
        )
    )

    assert result.status == "succeeded"
    assert result.document is not None
    metadata = result.document.metadata
    assert metadata.source_id == "source_policy_md"
    assert metadata.source_sha256 == source_sha256
    assert metadata.parser_config_hash == parser_config_hash
    assert metadata.schema_version == "canonical-document-ir-v1"
    assert metadata.ir_schema_version == "canonical-document-ir-v1"
    assert metadata.document_version_id == (
        "doc_policy:"
        f"{source_sha256}:native:contract-v2:{parser_config_hash}:canonical-document-ir-v1"
    )
    assert metadata.parent_document_version_id is None
    assert metadata.derived_from == []
    assert metadata.asset_refs == ["file://policies/renewal.md"]
    assert metadata.redaction_status == "raw"
    assert metadata.retention_policy == "workspace_default"


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
            source_id="source_contract_md",
            workspace_id="workspace_1",
            source_uri="file://contract.md",
            mime_type="text/markdown",
            hash="sha256:def",
            source_sha256="sha256:def",
            parser_id="native",
            parser_version="contract-v1",
            document_version_id="doc_contract:v1",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_payment",
                type="paragraph",
                text="The supplier must provide invoices monthly.",
                source_span=SourceSpan(
                    page=5,
                    line_range=[12, 14],
                    section_path=["Payment"],
                    char_start=40,
                    char_end=84,
                ),
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
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["document_id"] == "doc_contract"
    assert (
        handoff["vector_documents"][0]["metadata"]["source_span"]["source_object_id"]
        == "source_contract_md"
    )
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["document_version_id"] == "doc_contract:v1"
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["page_number"] == 5
    assert (
        handoff["vector_documents"][0]["metadata"]["source_span"]["chunk_id"]
        == "doc_contract::block_payment::cite1"
    )
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["char_start"] == 40
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["char_end"] == (
        40 + len("The supplier must provide invoices monthly.")
    )
    assert (
        handoff["vector_documents"][0]["metadata"]["source_span"]["normalized_text"]
        == "The supplier must provide invoices monthly."
    )
    assert (
        handoff["vector_documents"][0]["metadata"]["source_span"]["raw_text"]
        == "The supplier must provide invoices monthly."
    )
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["content_hash"] == "sha256:def"
    assert handoff["vector_documents"][0]["metadata"]["source_span"]["parser_name"] == "native"
    assert handoff["graphrag_documents"][0]["chunk_id"] == "doc_contract::block_payment::cite1"
    assert handoff["evidence_items"][0]["evidence_id"] == "doc_contract::block_payment::cite1"
    assert handoff["evidence_items"][0]["chunk_id"] == "doc_contract::block_payment::cite1"
    assert handoff["citation_items"][0]["source_span"]["section_path"] == ["Payment"]
    assert handoff["citation_items"][0]["chunk_id"] == "doc_contract::block_payment::cite1"


def test_index_handoff_builds_citation_chunks_with_parent_context_and_neighbors() -> None:
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
        build_index_handoff_payload,
    )

    gold_sentence = "Critical supplier evidence survives sentence chunking."
    full_context = (
        "Introductory context should stay available for answer synthesis. "
        f"{gold_sentence} "
        "Neighbor context should be attached without replacing the citation span."
    )
    ir = CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_chunking",
            source_id="source_chunking",
            workspace_id="workspace_1",
            source_uri="file://chunking.md",
            mime_type="text/markdown",
            hash="sha256:chunking",
            parser_id="native",
            parser_version="chunking-v1",
            document_version_id="doc_chunking:v1",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_policy",
                type="paragraph",
                text=full_context,
                source_span=SourceSpan(line_range=[7, 7], section_path=["Policy"], char_start=100),
            )
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="chunking-v1",
            source_uri="file://chunking.md",
            confidence=1.0,
        ),
    )

    handoff = build_index_handoff_payload(ir).model_dump()
    parent_chunk = next(chunk for chunk in handoff["chunks"] if chunk["metadata"]["chunk_role"] == "parent_context")
    citation_chunks = [
        chunk for chunk in handoff["chunks"] if chunk["metadata"]["chunk_role"] == "citation"
    ]
    gold_chunk = next(chunk for chunk in citation_chunks if gold_sentence in chunk["content"])

    assert parent_chunk["chunk_id"] == "doc_chunking::block_policy"
    assert parent_chunk["content"] == full_context
    assert len(citation_chunks) == 3
    assert [item["chunk_id"] for item in handoff["bm25_documents"]] == [
        chunk["chunk_id"] for chunk in citation_chunks
    ]
    assert gold_chunk["metadata"]["parent_chunk_id"] == parent_chunk["chunk_id"]
    assert gold_chunk["metadata"]["parent_context"] == full_context
    assert gold_chunk["metadata"]["neighbor_chunk_ids"]
    assert gold_chunk["metadata"]["source_span"]["raw_text"] == gold_sentence
    assert gold_chunk["metadata"]["source_span"]["normalized_text"] == gold_sentence
    assert gold_chunk["metadata"]["source_span"]["char_start"] > 100
    assert gold_chunk["metadata"]["source_span"]["char_end"] > gold_chunk["metadata"]["source_span"]["char_start"]
    assert gold_chunk["metadata"]["citation_chunking"]["citation_chunk_char_limit"] == 240


def test_legacy_source_span_does_not_fake_page_or_character_offsets() -> None:
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
            document_id="doc_legacy",
            source_id="source_legacy",
            workspace_id="workspace_1",
            source_uri="file://legacy.txt",
            mime_type="text/plain",
            hash="sha256:legacy",
            parser_id="native",
            parser_version="legacy-v1",
            document_version_id="doc_legacy:v1",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_legacy",
                type="paragraph",
                text="Legacy text has no page or character offsets.",
                source_span=SourceSpan(),
            )
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="legacy-v1",
            source_uri="file://legacy.txt",
            confidence=1.0,
        ),
    )

    span = build_index_handoff_payload(ir).chunks[0]["metadata"]["source_span"]

    assert span["document_id"] == "doc_legacy"
    assert span["chunk_id"] == "doc_legacy::block_legacy"
    assert span["block_id"] == "block_legacy"
    assert span["page_number"] is None
    assert span["char_start"] is None
    assert span["char_end"] is None


def test_parser_golden_fixture_manifest_is_complete() -> None:
    manifest_path = REPO_ROOT / "tests/fixtures/parser_golden/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert {case["case_id"] for case in manifest["cases"]} == {
        "pdf_table",
        "scanned_image",
        "pptx_slide",
        "docx_heading_table",
        "xlsx_sheet",
        "plain_text",
        "markdown_structured",
        "csv_table",
        "json_policy",
        "html_policy",
        "code_file",
        "markdown_link",
    }
    expected_paths = {
        "docx_heading_table": "inputs/docx_heading_table.docx",
        "xlsx_sheet": "inputs/xlsx_sheet.xlsx",
        "plain_text": "inputs/plain_text.txt",
        "markdown_structured": "inputs/markdown_structured.md",
        "csv_table": "inputs/csv_table.csv",
        "json_policy": "inputs/json_policy.json",
        "html_policy": "inputs/html_policy.html",
        "code_file": "inputs/code_file.py",
        "markdown_link": "inputs/markdown_link.md",
    }
    for case in manifest["cases"]:
        for field in ["format", "input_path", "default_parser", "evidence_anchor", "expected_blocks"]:
            assert case[field], f"{case['case_id']} missing {field}"
        assert (manifest_path.parent / case["input_path"]).exists()
        if case["case_id"] in expected_paths:
            assert case["input_path"] == expected_paths[case["case_id"]]
