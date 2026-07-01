from __future__ import annotations

from pathlib import Path

import pytest


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "parser_golden" / "inputs"


def _parse_fixture(case_id: str, file_name: str, mime_type: str):
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    source_path = FIXTURE_ROOT / file_name
    return ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id=f"doc_{case_id}",
            workspace_id="workspace_phase04",
            source_uri=source_path.as_uri(),
            mime_type=mime_type,
        )
    )


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


def test_parse_gateway_unknown_format_returns_stable_fallback_diagnostics() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_unknown",
            workspace_id="workspace_phase02",
            source_uri="file://uploads/archive.bin",
            mime_type="application/octet-stream",
            source_text="Long tail content that should use a deterministic fallback.",
        )
    )

    assert result.status == "succeeded"
    assert result.document is not None
    assert result.document.metadata.parser_id == "unstructured_markitdown"
    assert result.document.metadata.fallback_used is True
    assert result.document.metadata.fallback_reason == "unknown format"
    assert any(diagnostic.code == "unknown_format_fallback" for diagnostic in result.diagnostics)


def test_parse_gateway_target_blocked_adapter_emits_stable_diagnostic() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_scan",
            workspace_id="workspace_phase02",
            source_uri="file://scans/invoice.png",
            mime_type="image/png",
            source_text="OCR placeholder text",
        )
    )

    assert result.status == "succeeded"
    assert result.document is not None
    assert result.document.metadata.parser_id == "mineru_ocr_vlm"
    assert result.document.metadata.target_blocked is True
    assert result.document.metadata.blocked_reason
    blocked_diagnostic = next(
        diagnostic for diagnostic in result.diagnostics if diagnostic.code == "target_blocked_adapter"
    )
    assert blocked_diagnostic.severity == "warning"
    assert blocked_diagnostic.metadata["external_dependency_status"] == "target_blocked"


def test_parser_adapter_dependency_probe_reports_present_and_missing_dependencies() -> None:
    from zuno.knowledge.ingestion import get_parser_adapter

    native_probe = get_parser_adapter("native").dependency_probe()
    docling_probe = get_parser_adapter("docling_pymupdf").dependency_probe()

    assert native_probe.code == "adapter_dependency_probe"
    assert native_probe.severity == "info"
    assert native_probe.metadata["dependency_status"] == "present"
    assert native_probe.metadata["provider"] == "builtin"

    assert docling_probe.code == "adapter_dependency_probe"
    assert docling_probe.severity == "warning"
    assert docling_probe.metadata["dependency_status"] == "missing"
    assert "docling" in docling_probe.metadata["required_packages"]


@pytest.mark.parametrize(
    ("case_id", "file_name", "mime_type", "expected_parser", "expected_block"),
    [
        ("pdf_table", "pdf_table.pdf", "application/pdf", "docling_pymupdf", "table"),
        (
            "docx_heading_table",
            "docx_heading_table.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "unstructured_markitdown",
            "heading",
        ),
        (
            "pptx_slide",
            "pptx_slide.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "unstructured_markitdown",
            "slide_title",
        ),
        (
            "xlsx_sheet",
            "xlsx_sheet.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "unstructured_markitdown",
            "table",
        ),
    ],
)
def test_pdf_and_office_contract_parse_keeps_target_blocked_boundary(
    case_id: str,
    file_name: str,
    mime_type: str,
    expected_parser: str,
    expected_block: str,
) -> None:
    result = _parse_fixture(case_id, file_name, mime_type)

    assert result.status == "succeeded"
    assert result.document is not None
    assert result.document.metadata.parser_id == expected_parser
    assert result.document.metadata.target_blocked is True
    assert result.document.metadata.blocked_reason
    assert any(block.type == expected_block for block in result.document.blocks)
    blocked_diagnostic = next(
        diagnostic for diagnostic in result.diagnostics if diagnostic.code == "target_blocked_adapter"
    )
    assert blocked_diagnostic.metadata["dependency_status"] == "missing"
    assert blocked_diagnostic.metadata["capability_status"] == "target-blocked"
    assert blocked_diagnostic.metadata["fallback"] in {"native", "mineru_ocr_vlm"}


def test_ocr_vlm_blocked_result_keeps_derived_enrichment_gates() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    blocked = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_vlm_blocked",
            workspace_id="workspace_phase05",
            source_uri="file://scans/diagram.png",
            mime_type="image/png",
            source_text="OCR placeholder should not be source truth.",
        )
    )
    snapshot = ParseGateway.get_job_snapshot(blocked.job_id)
    diagnostic = blocked.diagnostics[0]

    assert blocked.status == "blocked"
    assert blocked.document is None
    assert diagnostic.code == "target_blocked_adapter"
    assert diagnostic.metadata["enrichment_role"] == "derived_enrichment"
    assert diagnostic.metadata["network_policy"] == "deny_by_default"
    assert diagnostic.metadata["privacy_gate"]["source_truth_policy"] == "cannot_override_deterministic_source"
    assert diagnostic.metadata["budget_gate"]["network_default"] == "deny"
    assert snapshot.adapter_boundary["enrichment_role"] == "derived_enrichment"
    assert snapshot.adapter_boundary["dependency_status"] == "missing"
    assert snapshot.adapter_boundary["budget_gate"]["review_required"] is True


def test_parse_gateway_records_parse_job_status_for_replay() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    request = ParseDocumentRequest(
        document_id="doc_job",
        workspace_id="workspace_phase04",
        source_uri="file://notes/job.md",
        mime_type="text/markdown",
        source_text="# Job\nReplay me.",
        parser_config={"chunking": "line"},
    )
    submitted = ParseGateway.submit_parse_job(request)
    replayed = ParseGateway.get_job_status(submitted.job_id)
    snapshot = ParseGateway.get_job_snapshot(submitted.job_id)
    resubmitted = ParseGateway.submit_parse_job(request)
    resubmitted_snapshot = ParseGateway.get_job_snapshot(resubmitted.job_id)

    assert replayed.job_id == submitted.job_id
    assert replayed.status == "succeeded"
    assert replayed.document is not None
    assert replayed.document.metadata.document_id == "doc_job"
    assert snapshot.parse_idempotency_key == resubmitted_snapshot.parse_idempotency_key
    assert snapshot.parse_attempt_id.startswith("attempt_")
    assert snapshot.attempt_count == 1
    assert [entry["status"] for entry in snapshot.status_timeline] == [
        "accepted",
        "running",
        "succeeded",
    ]
    assert snapshot.metrics.status == "succeeded"
    assert snapshot.metrics.parser_name == "native"
    assert snapshot.metrics.format == "md"


def test_parse_gateway_target_blocked_adapter_enters_blocked_job_state() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    blocked = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_blocked_ocr",
            workspace_id="workspace_phase03",
            source_uri="file://scans/invoice.png",
            mime_type="image/png",
            source_text="OCR placeholder should not make worker Current.",
        )
    )
    snapshot = ParseGateway.get_job_snapshot(blocked.job_id)

    assert blocked.status == "blocked"
    assert blocked.document is None
    assert blocked.failure is not None
    assert blocked.failure.reason == snapshot.blocked_reason
    assert snapshot.status == "blocked"
    assert snapshot.retryable is False
    assert snapshot.failure_snapshot["blocked"] is True
    assert snapshot.adapter_boundary["external_dependency_status"] == "target_blocked"
    assert [entry["status"] for entry in snapshot.status_timeline] == [
        "accepted",
        "blocked",
    ]


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
    assert failed_snapshot.attempt_count == 1
    assert failed_snapshot.retryable is True
    assert failed_snapshot.failure_reason
    assert failed_snapshot.last_error == failed_snapshot.failure_reason
    assert failed_snapshot.error_class == "ValueError"
    assert failed_snapshot.failure_snapshot["error_class"] == "ValueError"
    assert failed_snapshot.parser_diagnostics[-1]["code"] == "parse_failed"
    assert failed_snapshot.metrics.error_count == 1
    assert [entry["status"] for entry in failed_snapshot.status_timeline] == [
        "accepted",
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
    assert retried_snapshot.attempt_count == 2
    assert retried_snapshot.status == "succeeded"
    assert retried_snapshot.metrics.block_count >= 1
    assert retried_snapshot.metrics.warning_count == 0
    assert retried_snapshot.adapter_boundary["current_runtime"] == "deterministic_local"
    assert retried_snapshot.status_timeline[0]["status"] == "retrying"

    dead_letter = ParseGateway.retry_parse_job(
        retried.job_id,
        ParseDocumentRequest(
            document_id="doc_queue_empty",
            workspace_id="workspace_phase07",
            source_uri="file://notes/empty.md",
            mime_type="text/markdown",
            source_text="",
        ),
    )
    dead_letter_snapshot = ParseGateway.get_job_snapshot(dead_letter.job_id)

    assert dead_letter.status == "dead_letter"
    assert dead_letter_snapshot.status == "dead_letter"
    assert dead_letter_snapshot.retryable is False
    assert dead_letter_snapshot.status_timeline[-1]["status"] == "dead_letter"


def test_parse_gateway_cancelled_job_snapshot_is_distinct_from_failed() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    submitted = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_cancel",
            workspace_id="workspace_phase03",
            source_uri="file://notes/cancel.md",
            mime_type="text/markdown",
            source_text="# Cancel\nThis completed before cancellation request.",
        )
    )
    cancelled = ParseGateway.cancel_parse_job(submitted.job_id, reason="user_cancelled")
    snapshot = ParseGateway.get_job_snapshot(cancelled.job_id)

    assert cancelled.status == "cancelled"
    assert snapshot.status == "cancelled"
    assert snapshot.failure_reason == "user_cancelled"
    assert snapshot.retryable is False
    assert snapshot.status_timeline[-1]["status"] == "cancelled"


def test_native_markdown_fixture_keeps_sections_links_code_fence_and_table() -> None:
    result = _parse_fixture("markdown_structured", "markdown_structured.md", "text/markdown")

    assert result.status == "succeeded"
    assert result.document is not None
    document = result.document
    blocks = document.blocks

    heading = next(block for block in blocks if block.type == "heading" and block.text == "Supplier Policy")
    assert heading.source_span.section_path == ["Supplier Policy"]

    link = next(block for block in blocks if block.type == "link")
    assert link.metadata["href"] == "appendix.md"
    assert link.metadata["label"] == "contract appendix"
    assert link.source_span.section_path == ["Supplier Policy"]

    code = next(block for block in blocks if block.type == "code_block")
    assert code.language == "python"
    assert code.code_fence == "python"
    assert code.source_span.section_path == ["Supplier Policy", "Renewal"]

    table = next(block for block in blocks if block.type == "table")
    assert table.metadata["headers"] == ["Control", "Owner"]
    assert table.source_span.table_cell == "table:1"
    assert document.tables[0].rows[-1] == ["Notice", "Legal"]


def test_native_csv_fixture_keeps_table_cell_coordinates() -> None:
    result = _parse_fixture("csv_table", "csv_table.csv", "text/csv")

    assert result.status == "succeeded"
    assert result.document is not None
    document = result.document
    table = next(block for block in document.blocks if block.type == "table")
    cells = [block for block in document.blocks if block.type == "table_cell"]

    assert table.metadata["delimiter"] == ","
    assert table.metadata["headers"] == ["control", "owner", "status"]
    assert table.metadata["row_count"] == 2
    assert table.metadata["column_count"] == 3
    owner_cell = next(
        block
        for block in cells
        if block.metadata["row_index"] == 1 and block.metadata["column_name"] == "owner"
    )
    assert owner_cell.text == "Legal"
    assert owner_cell.source_span.table_cell == "row:1,col:owner"
    assert document.tables[0].rows[1] == ["Renewal Notice", "Legal", "ready"]


def test_native_json_fixture_keeps_pointer_paths_for_objects_arrays_and_values() -> None:
    result = _parse_fixture("json_policy", "json_policy.json", "application/json")

    assert result.status == "succeeded"
    assert result.document is not None
    blocks = result.document.blocks

    policy_object = next(block for block in blocks if block.metadata.get("json_pointer") == "/policy")
    owners_array = next(block for block in blocks if block.metadata.get("json_pointer") == "/policy/owners")
    policy_name = next(block for block in blocks if block.metadata.get("json_pointer") == "/policy/name")

    assert policy_object.type == "json_object"
    assert owners_array.type == "json_array"
    assert policy_name.type == "json_value"
    assert policy_name.text == "Renewal Review"
    assert policy_name.source_span.section_path == ["policy", "name"]


def test_native_html_fixture_filters_scripts_and_keeps_links_and_tables() -> None:
    result = _parse_fixture("html_policy", "html_policy.html", "text/html")

    assert result.status == "succeeded"
    assert result.document is not None
    document = result.document
    text = "\n".join(block.text for block in document.blocks)
    link = next(block for block in document.blocks if block.type == "link")
    table = next(block for block in document.blocks if block.type == "table")

    assert "window.secret" not in text
    assert "display: none" not in text
    assert any(block.type == "heading" and block.text == "Supplier Policy" for block in document.blocks)
    assert link.metadata["href"] == "appendix.html"
    assert link.metadata["label"] == "appendix"
    assert table.metadata["headers"] == ["Control", "Owner"]
    assert document.tables[0].rows[-1] == ["Renewal Notice", "Legal"]


def test_native_code_fixture_keeps_language_imports_and_symbol_metadata() -> None:
    result = _parse_fixture("code_file", "code_file.py", "text/x-python")

    assert result.status == "succeeded"
    assert result.document is not None
    code = next(block for block in result.document.blocks if block.type == "code_block")

    assert code.language == "python"
    assert code.metadata["imports"] == ["json", "pathlib.Path"]
    assert code.metadata["classes"] == ["PolicyParser"]
    assert code.metadata["functions"] == ["parse_policy", "helper"]
    assert code.metadata["language_detection"] == "extension"
    expected_line_count = len((FIXTURE_ROOT / "code_file.py").read_text(encoding="utf-8").splitlines())
    assert code.source_span.line_range == [1, expected_line_count]


@pytest.mark.parametrize(
    ("source_uri", "mime_type", "source_text", "expected_warning"),
    [
        (
            "file://fixtures/malformed.csv",
            "text/csv",
            "control,owner,status\nRenewal Notice,Legal\nSecurity Review,Platform,blocked,extra",
            "malformed_csv",
        ),
        (
            "file://fixtures/malformed.json",
            "application/json",
            '{"policy": {"name": "Broken", "owners": [}',
            "malformed_json",
        ),
        (
            "file://fixtures/malformed.html",
            "text/html",
            "<html><body><h1>Broken<p>Text<table><tr><td>A",
            "malformed_html",
        ),
    ],
)
def test_native_malformed_structured_inputs_emit_diagnostics_without_crashing(
    source_uri: str,
    mime_type: str,
    source_text: str,
    expected_warning: str,
) -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id=f"doc_{expected_warning}",
            workspace_id="workspace_phase04",
            source_uri=source_uri,
            mime_type=mime_type,
            source_text=source_text,
        )
    )

    assert result.status == "succeeded"
    assert result.document is not None
    assert any(expected_warning in diagnostic.message for diagnostic in result.diagnostics)
    assert any(block.metadata.get("malformed") for block in result.document.blocks)


def test_parse_gateway_reads_real_parser_golden_files() -> None:
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    cases = [
        ("pdf_table", "pdf_table.pdf", "application/pdf", "table"),
        ("docx_heading_table", "docx_heading_table.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "heading"),
        ("pptx_slide", "pptx_slide.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "slide_title"),
        ("xlsx_sheet", "xlsx_sheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "table"),
        ("scanned_image", "scanned_image.png", "image/png", "ocr_text"),
        ("plain_text", "plain_text.txt", "text/plain", "paragraph"),
        ("markdown_structured", "markdown_structured.md", "text/markdown", "code_block"),
        ("csv_table", "csv_table.csv", "text/csv", "table_cell"),
        ("json_policy", "json_policy.json", "application/json", "json_value"),
        ("html_policy", "html_policy.html", "text/html", "link"),
        ("code_file", "code_file.py", "text/x-python", "code_block"),
        ("markdown_link", "markdown_link.md", "text/markdown", "link"),
    ]

    for case_id, file_name, mime_type, expected_block in cases:
        source_path = FIXTURE_ROOT / file_name
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
