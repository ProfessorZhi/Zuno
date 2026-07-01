from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    ("source_uri", "mime_type", "source_text", "expected_parser", "expected_block"),
    [
        (
            "file://contracts/supplier.pdf",
            "application/pdf",
            "Supplier Contract\n| Term | Value |\n| Renewal | Annual |",
            "docling_pymupdf",
            "table",
        ),
        (
            "file://contracts/supplier.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "# Payment\nPayment is due in 30 days.\n| Fee | Amount |",
            "unstructured_markitdown",
            "heading",
        ),
        (
            "file://decks/risk-review.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "# Slide 1: Risk\n- Renewal risk\n![chart](chart.png)",
            "unstructured_markitdown",
            "slide_title",
        ),
        (
            "file://notes/review.md",
            "text/markdown",
            "# Review\nSee [contract](supplier.pdf).\nRisk is medium.",
            "native",
            "link",
        ),
        (
            "file://notes/plain.txt",
            "text/plain",
            "Line one\nLine two",
            "native",
            "paragraph",
        ),
        (
            "file://scans/page.png",
            "image/png",
            "OCR text: invoice number 42",
            "mineru_ocr_vlm",
            "ocr_text",
        ),
        (
            "file://src/app.py",
            "text/x-python",
            "def run():\n    return 42\n",
            "native",
            "code_block",
        ),
    ],
)
def test_parse_gateway_runtime_generates_canonical_ir_for_phase04_formats(
    source_uri: str,
    mime_type: str,
    source_text: str,
    expected_parser: str,
    expected_block: str,
) -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_phase04",
            workspace_id="workspace_phase04",
            source_uri=source_uri,
            mime_type=mime_type,
            source_text=source_text,
            acl_scope="workspace",
            sensitivity_tags=["internal"],
        )
    )

    assert result.status == "succeeded"
    assert result.failure is None
    assert result.document is not None
    assert result.index_handoff is not None
    assert result.document.metadata.parser_id == expected_parser
    assert result.document.metadata.acl_scope == "workspace"
    assert result.document.metadata.sensitivity_tags == ["internal"]
    assert result.document.provenance.parser_id == expected_parser
    assert any(block.type == expected_block for block in result.document.blocks)
    assert all(block.acl_scope == "workspace" for block in result.document.blocks)
    assert result.index_handoff.document_id == "doc_phase04"
    assert result.index_handoff.chunks
    assert {diagnostic.severity for diagnostic in result.diagnostics} <= {"info", "warning"}


def test_parse_gateway_preserves_source_anchors_for_runtime_blocks() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_pdf_table",
            workspace_id="workspace_phase04",
            source_uri="file://contracts/table.pdf",
            mime_type="application/pdf",
            source_text="Page heading\n| A | B |\n| 1 | 2 |",
        )
    )

    document = result.document
    assert document is not None
    table_block = next(block for block in document.blocks if block.type == "table")
    assert table_block.source_span.page == 1
    assert table_block.source_span.bbox is not None
    assert table_block.source_span.table_cell == "row:1"
    assert document.tables[0].source_span.table_cell == "row:1"


def test_parse_gateway_failure_is_traceable_and_does_not_swallow_errors() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_empty",
            workspace_id="workspace_phase04",
            source_uri="file://notes/empty.txt",
            mime_type="text/plain",
            source_text="",
        )
    )

    assert result.status == "failed"
    assert result.document is None
    assert result.index_handoff is None
    assert result.failure is not None
    assert result.failure.parser_id == "native"
    assert result.failure.format == "txt"
    assert result.failure.retryable is False
    assert "empty" in result.failure.reason.lower()
    assert result.diagnostics[-1].severity == "error"
    assert result.diagnostics[-1].code == "parse_failed"


def test_parse_gateway_records_parse_job_status_for_replay() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    submitted = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_job",
            workspace_id="workspace_phase04",
            source_uri="file://notes/job.md",
            mime_type="text/markdown",
            source_text="# Job\nReplay me.",
        )
    )
    replayed = ParseGateway.get_job_status(submitted.job_id)

    assert replayed.job_id == submitted.job_id
    assert replayed.status == "succeeded"
    assert replayed.document is not None
    assert replayed.document.metadata.document_id == "doc_job"


def test_parse_gateway_records_queue_snapshot_metrics_and_retry_lineage() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    failed = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_queue_empty",
            workspace_id="workspace_phase07",
            source_uri="file://notes/empty.md",
            mime_type="text/markdown",
            source_text="",
        )
    )
    failed_snapshot = ParseGateway.get_job_snapshot(failed.job_id)

    assert failed_snapshot.job_id == failed.job_id
    assert failed_snapshot.status == "failed"
    assert failed_snapshot.attempt == 1
    assert failed_snapshot.retryable is True
    assert failed_snapshot.failure_reason
    assert failed_snapshot.metrics.error_count == 1
    assert [entry["status"] for entry in failed_snapshot.status_timeline] == [
        "queued",
        "running",
        "failed",
    ]
    assert failed_snapshot.source_provenance["source_uri"] == "file://notes/empty.md"

    retried = ParseGateway.retry_parse_job(
        failed.job_id,
        ParseDocumentRequest(
            document_id="doc_queue_empty",
            workspace_id="workspace_phase07",
            source_uri="file://notes/empty.md",
            mime_type="text/markdown",
            source_text="# Repaired\nRetry me.",
        ),
    )
    retried_snapshot = ParseGateway.get_job_snapshot(retried.job_id)

    assert retried.job_id != failed.job_id
    assert retried_snapshot.previous_job_id == failed.job_id
    assert retried_snapshot.attempt == 2
    assert retried_snapshot.status == "succeeded"
    assert retried_snapshot.metrics.block_count >= 1
    assert retried_snapshot.metrics.warning_count == 0
    assert retried_snapshot.adapter_boundary["current_runtime"] == "deterministic_local"


def test_parse_gateway_reads_real_parser_golden_files() -> None:
    from pathlib import Path

    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    fixture_root = Path(__file__).resolve().parents[1] / "fixtures" / "parser_golden" / "inputs"
    cases = [
        ("pdf_table", "pdf_table.pdf", "application/pdf", "table"),
        ("docx_heading_table", "docx_heading_table.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "heading"),
        ("pptx_slide", "pptx_slide.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "slide_title"),
        ("xlsx_sheet", "xlsx_sheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "table"),
        ("scanned_image", "scanned_image.png", "image/png", "ocr_text"),
        ("code_file", "code_file.py", "text/x-python", "code_block"),
        ("markdown_link", "markdown_link.md", "text/markdown", "link"),
    ]

    for case_id, file_name, mime_type, expected_block in cases:
        source_path = fixture_root / file_name
        result = ParseGateway.parse_document(
            ParseDocumentRequest(
                document_id=f"doc_{case_id}",
                workspace_id="workspace_phase04",
                source_uri=source_path.as_uri(),
                mime_type=mime_type,
            )
        )

        assert result.status == "succeeded", case_id
        assert result.document is not None
        assert any(block.type == expected_block for block in result.document.blocks), case_id


def test_parse_gateway_uses_adapter_registry_for_runtime_dispatch() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway, get_parser_adapter

    adapter = get_parser_adapter("native")
    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_adapter",
            workspace_id="workspace_phase04",
            source_uri="file://notes/adapter.md",
            mime_type="text/markdown",
            source_text="# Adapter\nRegistry owned parse.",
        )
    )

    assert adapter.parser_id == "native"
    assert result.document is not None
    assert result.document.provenance.parser_id == adapter.parser_id


def test_legacy_chunks_normalize_to_ir_with_acl_source_span_provenance() -> None:
    from zuno.knowledge.ingestion import normalize_legacy_chunks_to_ir
    from zuno.schema.chunk import ChunkModel

    chunk = ChunkModel(
        chunk_id="legacy_chunk_1",
        content="Legacy parser content",
        file_id="file_legacy",
        file_name="legacy.md",
        update_time="2026-06-30T12:00:00",
        knowledge_id="knowledge_legacy",
        source_url="file://legacy.md",
    )

    document = normalize_legacy_chunks_to_ir(
        chunks=[chunk],
        document_id="doc_legacy",
        workspace_id="workspace_phase04",
        source_uri="file://legacy.md",
        mime_type="text/markdown",
        parser_id="legacy_doc_parser",
        parser_version="phase04-runtime-v1",
        acl_scope="workspace",
        sensitivity_tags=["internal"],
    )

    assert document.metadata.document_id == "doc_legacy"
    assert document.metadata.hash == chunk.document_hash
    assert document.blocks[0].block_id == "legacy_chunk_1"
    assert document.blocks[0].source_span.line_range == [1, 1]
    assert document.blocks[0].acl_scope == "workspace"
    assert document.blocks[0].sensitivity_tags == ["internal"]
    assert document.provenance.parser_id == "legacy_doc_parser"
