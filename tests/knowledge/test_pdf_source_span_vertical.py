from __future__ import annotations

from pathlib import Path


PDF_FIXTURE = Path("tests/fixtures/documents/phase12_source_span.pdf")


def _parse_fixture():
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    return ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_phase12_pdf",
            source_id="source_phase12_pdf",
            workspace_id="workspace_phase12_pdf",
            source_uri=f"file:///{PDF_FIXTURE.resolve().as_posix()}",
            mime_type="application/pdf",
            source_bytes=PDF_FIXTURE.read_bytes(),
            parser_version="phase12-pymupdf-test",
        )
    )


def test_pymupdf_parse_gateway_extracts_real_pdf_source_spans() -> None:
    result = _parse_fixture()

    assert result.status == "succeeded"
    assert result.document is not None
    assert result.document.metadata.parser_id == "docling_pymupdf"
    assert result.document.metadata.target_blocked is False
    assert result.document.metadata.blocked_reason is None
    assert result.document.metadata.source_sha256
    assert result.document.metadata.document_version_id
    assert not any(diagnostic.code == "target_blocked_adapter" for diagnostic in result.diagnostics)

    first_block = result.document.blocks[0]
    assert first_block.text == "Release gate status is implementation complete but quality not yet proven."
    assert first_block.source_span.page == 1
    assert first_block.source_span.page_number == 1
    assert first_block.source_span.bbox and len(first_block.source_span.bbox) == 4
    assert first_block.source_span.char_start == 0
    assert first_block.source_span.char_end == len(first_block.text)
    assert first_block.source_span.normalized_text == first_block.text
    assert first_block.metadata["parser_adapter"] == "pymupdf"
    assert first_block.metadata["block_index"] >= 1

    assert result.index_handoff is not None
    citation = result.index_handoff.citation_items[0]
    citation_span = citation["source_span"]
    bm25_citation = result.index_handoff.bm25_documents[0]
    assert bm25_citation["metadata"]["chunk_role"] == "citation"
    assert bm25_citation["metadata"]["parent_chunk_id"]
    assert bm25_citation["metadata"]["parent_context"]
    assert citation_span["page_number"] == 1
    assert citation_span["bbox"]
    assert citation_span["block_id"] == first_block.block_id
    assert citation_span["document_version_id"] == result.document.metadata.document_version_id
    assert citation_span["chunk_id"] == citation["chunk_id"]


def test_pdf_source_spans_survive_index_handoff_and_retrieval() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    result = _parse_fixture()
    assert result.document is not None
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_phase12_pdf", "workspace_phase12_pdf")
    manifest = runtime.index_document(
        "ks_phase12_pdf",
        result.document,
        targets=["bm25", "vector", "graph"],
    )

    payload = runtime.to_retrieval_payload(
        "ks_phase12_pdf",
        "release gate status quality not yet proven",
    )
    top = payload["documents_by_source"]["bm25"][0]

    assert manifest.status == "succeeded"
    assert top["document_id"] == "doc_phase12_pdf"
    assert top["metadata"]["chunk_role"] == "citation"
    assert top["metadata"]["source_span"]["page_number"] == 1
    assert top["metadata"]["source_span"]["bbox"]
    assert top["metadata"]["citation_lineage"]["source_span"]["document_version_id"]
    assert top["metadata"]["parent_context"]


def test_corrupt_pdf_fails_without_fake_index() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_corrupt_pdf",
            workspace_id="workspace_phase12_pdf",
            source_uri="file:///corrupt.pdf",
            mime_type="application/pdf",
            source_bytes=b"%PDF-1.7\nthis is not a complete pdf",
            parser_version="phase12-pymupdf-test",
        )
    )

    assert result.status == "failed"
    assert result.document is None
    assert result.index_handoff is None
    assert result.failure is not None
    assert "PyMuPDF failed to open PDF" in result.failure.reason


def test_scanned_pdf_returns_needs_ocr_without_fake_blocks() -> None:
    import fitz

    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    document = fitz.open()
    document.new_page(width=595, height=842)
    pdf_bytes = document.tobytes()
    document.close()

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_scanned_pdf",
            workspace_id="workspace_phase12_pdf",
            source_uri="file:///scanned.pdf",
            mime_type="application/pdf",
            source_bytes=pdf_bytes,
            parser_version="phase12-pymupdf-test",
        )
    )

    assert result.status == "failed"
    assert result.document is None
    assert result.index_handoff is None
    assert result.failure is not None
    assert "needs_ocr" in result.failure.reason
