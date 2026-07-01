from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import uuid4

from .adapters import get_parser_adapter
from .contracts import (
    CanonicalDocumentIR,
    DocumentBlock,
    DocumentFigure,
    DocumentMetadata,
    DocumentProvenance,
    DocumentTable,
    ParseDocumentRequest,
    ParseDocumentResult,
    ParseJobSnapshot,
    ParserDiagnostic,
    ParserFailure,
    ParserJobMetrics,
    SourceSpan,
)
from .router import PARSER_ADAPTER_CONTRACTS, build_index_handoff_payload, select_parser_for_format


class ParseGateway:
    """PHASE04 deterministic Parse Gateway runtime surface."""

    _jobs: dict[str, ParseDocumentResult] = {}
    _job_snapshots: dict[str, ParseJobSnapshot] = {}

    @classmethod
    def submit_parse_job(cls, request: ParseDocumentRequest) -> ParseDocumentResult:
        started = time.perf_counter()
        result = cls.parse_document(request)
        cls._jobs[result.job_id] = result
        cls._job_snapshots[result.job_id] = cls._build_job_snapshot(
            result=result,
            request=request,
            attempt=1,
            previous_job_id=None,
            duration_ms=(time.perf_counter() - started) * 1000,
        )
        return result

    @classmethod
    def get_job_status(cls, job_id: str) -> ParseDocumentResult:
        try:
            return cls._jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"parse job not found: {job_id}") from exc

    @classmethod
    def get_job_snapshot(cls, job_id: str) -> ParseJobSnapshot:
        try:
            return cls._job_snapshots[job_id]
        except KeyError as exc:
            raise KeyError(f"parse job snapshot not found: {job_id}") from exc

    @classmethod
    def retry_parse_job(cls, job_id: str, request: ParseDocumentRequest) -> ParseDocumentResult:
        previous = cls.get_job_snapshot(job_id)
        started = time.perf_counter()
        result = cls.parse_document(request)
        cls._jobs[result.job_id] = result
        cls._job_snapshots[result.job_id] = cls._build_job_snapshot(
            result=result,
            request=request,
            attempt=previous.attempt + 1,
            previous_job_id=previous.job_id,
            duration_ms=(time.perf_counter() - started) * 1000,
        )
        return result

    @classmethod
    def parse_document(cls, request: ParseDocumentRequest) -> ParseDocumentResult:
        capability = select_parser_for_format(request.source_uri or request.mime_type)
        parser_id = capability.default_parser
        diagnostics = [
            ParserDiagnostic(
                code="parser_selected",
                message=f"Selected {parser_id} for {capability.format}.",
                parser_id=parser_id,
                format=capability.format,
            )
        ]
        job_id = f"parse_{uuid4().hex[:12]}"

        try:
            source_text = cls._source_text(request)
            if not source_text.strip():
                raise ValueError("empty source content")

            adapter = get_parser_adapter(parser_id)
            blocks, tables, figures, warnings, confidence = adapter.parse(
                format_name=capability.format,
                text=source_text,
                request=request,
            )
            diagnostics.extend(
                ParserDiagnostic(
                    code="parser_warning",
                    message=warning,
                    severity="warning",
                    parser_id=parser_id,
                    format=capability.format,
                )
                for warning in warnings
            )
            metadata = DocumentMetadata(
                document_id=request.document_id,
                workspace_id=request.workspace_id,
                source_uri=request.source_uri,
                mime_type=request.mime_type,
                hash=request.hash or hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
                parser_id=parser_id,
                parser_version=request.parser_version,
                acl_scope=request.acl_scope,
                sensitivity_tags=list(request.sensitivity_tags),
            )
            document = CanonicalDocumentIR(
                metadata=metadata,
                blocks=blocks,
                tables=tables,
                figures=figures,
                provenance=DocumentProvenance(
                    parser_id=parser_id,
                    parser_version=request.parser_version,
                    source_uri=request.source_uri,
                    confidence=confidence,
                    warnings=warnings,
                ),
            )
            return ParseDocumentResult(
                job_id=job_id,
                status="succeeded",
                document=document,
                diagnostics=diagnostics,
                index_handoff=build_index_handoff_payload(document),
            )
        except Exception as exc:
            diagnostics.append(
                ParserDiagnostic(
                    code="parse_failed",
                    message=str(exc),
                    severity="error",
                    parser_id=parser_id,
                    format=capability.format,
                )
            )
            return ParseDocumentResult(
                job_id=job_id,
                status="failed",
                failure=ParserFailure(
                    parser_id=parser_id,
                    format=capability.format,
                    reason=str(exc),
                    fallback=capability.fallback,
                    retryable=False,
                ),
                diagnostics=diagnostics,
            )

    @classmethod
    def _build_job_snapshot(
        cls,
        *,
        result: ParseDocumentResult,
        request: ParseDocumentRequest,
        attempt: int,
        previous_job_id: str | None,
        duration_ms: float,
    ) -> ParseJobSnapshot:
        capability = select_parser_for_format(request.source_uri or request.mime_type)
        parser_id = cls._snapshot_parser_id(result, capability.default_parser)
        error_count = sum(1 for diagnostic in result.diagnostics if diagnostic.severity == "error")
        warning_count = sum(1 for diagnostic in result.diagnostics if diagnostic.severity == "warning")
        document = result.document
        adapter_contract = PARSER_ADAPTER_CONTRACTS.get(parser_id)
        metrics = ParserJobMetrics(
            block_count=len(document.blocks) if document else 0,
            table_count=len(document.tables) if document else 0,
            figure_count=len(document.figures) if document else 0,
            warning_count=warning_count,
            error_count=error_count,
            duration_ms=round(duration_ms, 3),
        )
        status_timeline = [
            {"status": "queued", "attempt": attempt},
            {"status": "running", "attempt": attempt, "parser_id": parser_id},
            {"status": result.status, "attempt": attempt},
        ]
        return ParseJobSnapshot(
            job_id=result.job_id,
            status=result.status,
            document_id=request.document_id,
            workspace_id=request.workspace_id,
            source_uri=request.source_uri,
            mime_type=request.mime_type,
            parser_id=parser_id,
            parser_format=capability.format,
            attempt=attempt,
            retryable=result.status == "failed",
            previous_job_id=previous_job_id,
            failure_reason=result.failure.reason if result.failure else None,
            metrics=metrics,
            source_provenance=cls._source_provenance(result, request, parser_id),
            adapter_boundary=adapter_contract.model_dump() if adapter_contract else {},
            status_timeline=status_timeline,
        )

    @staticmethod
    def _snapshot_parser_id(result: ParseDocumentResult, fallback_parser_id: str) -> str:
        if result.document is not None:
            return result.document.metadata.parser_id
        if result.failure is not None:
            return result.failure.parser_id
        return fallback_parser_id

    @staticmethod
    def _source_provenance(
        result: ParseDocumentResult,
        request: ParseDocumentRequest,
        parser_id: str,
    ) -> dict:
        if result.document is not None:
            metadata = result.document.metadata
            return {
                "document_id": metadata.document_id,
                "workspace_id": metadata.workspace_id,
                "source_uri": metadata.source_uri,
                "mime_type": metadata.mime_type,
                "hash": metadata.hash,
                "parser_id": metadata.parser_id,
                "parser_version": metadata.parser_version,
                "acl_scope": metadata.acl_scope,
                "sensitivity_tags": list(metadata.sensitivity_tags),
                "confidence": result.document.provenance.confidence,
            }
        return {
            "document_id": request.document_id,
            "workspace_id": request.workspace_id,
            "source_uri": request.source_uri,
            "mime_type": request.mime_type,
            "hash": request.hash,
            "parser_id": parser_id,
            "parser_version": request.parser_version,
            "acl_scope": request.acl_scope,
            "sensitivity_tags": list(request.sensitivity_tags),
        }

    @staticmethod
    def _source_text(request: ParseDocumentRequest) -> str:
        if request.source_text is not None:
            return request.source_text
        if request.source_bytes is not None:
            return request.source_bytes.decode("utf-8", errors="ignore")
        parsed = urlparse(request.source_uri)
        if parsed.scheme == "file":
            path_text = unquote(parsed.path)
            if re.match(r"^/[A-Za-z]:/", path_text):
                path_text = path_text[1:]
            return Path(path_text).read_text(encoding="utf-8", errors="ignore")
        return ""

    @classmethod
    def _parse_blocks(
        cls,
        *,
        format_name: str,
        text: str,
        request: ParseDocumentRequest,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        if format_name == "pdf":
            return cls._parse_pdf(text, request)
        if format_name in {"docx", "xlsx"}:
            return cls._parse_structured_markdown(text, request, table_cells=True)
        if format_name == "pptx":
            return cls._parse_pptx(text, request)
        if format_name == "image":
            return cls._parse_image_ocr(text, request)
        if format_name == "code":
            return cls._parse_code(text, request)
        return cls._parse_markdown_or_text(text, request, markdown=format_name in {"md", "html"})

    @classmethod
    def _parse_pdf(
        cls,
        text: str,
        request: ParseDocumentRequest,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        blocks: list[DocumentBlock] = []
        table_rows: list[list[str]] = []
        for line_number, line in enumerate(cls._lines(text), start=1):
            if "|" in line:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                table_rows.append(cells)
                blocks.append(
                    cls._block(
                        request,
                        block_id=f"block_table_{len(table_rows)}",
                        block_type="table",
                        text=line,
                        source_span=SourceSpan(page=1, bbox=[0.0, float(line_number), 600.0, float(line_number + 1)], table_cell=f"row:{len(table_rows)}"),
                    )
                )
            else:
                blocks.append(
                    cls._block(
                        request,
                        block_id=f"block_p{line_number}",
                        block_type="paragraph",
                        text=line,
                        source_span=SourceSpan(page=1, bbox=[0.0, float(line_number), 600.0, float(line_number + 1)]),
                    )
                )
        tables = [
            DocumentTable(
                table_id="table_1",
                rows=table_rows,
                source_span=SourceSpan(page=1, bbox=[0.0, 1.0, 600.0, float(len(table_rows) + 1)], table_cell="row:1"),
                caption="Extracted PDF table",
            )
        ] if table_rows else []
        return cls._ensure_blocks(blocks, text, request), tables, [], [], 0.94

    @classmethod
    def _parse_structured_markdown(
        cls,
        text: str,
        request: ParseDocumentRequest,
        *,
        table_cells: bool,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        blocks: list[DocumentBlock] = []
        table_rows: list[list[str]] = []
        current_section: list[str] = []
        for line_number, line in enumerate(cls._lines(text), start=1):
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                current_section = [title]
                blocks.append(
                    cls._block(request, block_id=f"block_heading_{line_number}", block_type="heading", text=title, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section)))
                )
            elif "|" in line:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                table_rows.append(cells)
                blocks.append(
                    cls._block(request, block_id=f"block_table_{line_number}", block_type="table", text=line, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section), table_cell=f"row:{len(table_rows)}" if table_cells else None))
                )
            else:
                blocks.append(
                    cls._block(request, block_id=f"block_paragraph_{line_number}", block_type="paragraph", text=line, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section)))
                )
        tables = [
            DocumentTable(
                table_id="table_1",
                rows=table_rows,
                source_span=SourceSpan(section_path=list(current_section), table_cell="row:1"),
            )
        ] if table_rows else []
        return cls._ensure_blocks(blocks, text, request), tables, [], [], 0.96

    @classmethod
    def _parse_pptx(
        cls,
        text: str,
        request: ParseDocumentRequest,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        blocks: list[DocumentBlock] = []
        figures: list[DocumentFigure] = []
        for line_number, line in enumerate(cls._lines(text), start=1):
            if line.startswith("#"):
                block_type = "slide_title"
                content = line.lstrip("#").strip()
            elif line.startswith("!") or line.startswith("!["):
                block_type = "figure"
                content = line
                figures.append(DocumentFigure(figure_id=f"figure_{line_number}", description=line, source_span=SourceSpan(slide=1, bbox=[10.0, 10.0, 300.0, 200.0])))
            else:
                block_type = "slide_body"
                content = line.lstrip("- ").strip()
            blocks.append(
                cls._block(request, block_id=f"block_slide_{line_number}", block_type=block_type, text=content, source_span=SourceSpan(slide=1, bbox=[10.0, float(line_number * 20), 500.0, float(line_number * 20 + 16)]))
            )
        return cls._ensure_blocks(blocks, text, request), [], figures, [], 0.91

    @classmethod
    def _parse_markdown_or_text(
        cls,
        text: str,
        request: ParseDocumentRequest,
        *,
        markdown: bool,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        blocks: list[DocumentBlock] = []
        current_section: list[str] = []
        for line_number, line in enumerate(cls._lines(text), start=1):
            if markdown and line.startswith("#"):
                title = line.lstrip("#").strip()
                current_section = [title]
                block_type = "heading"
                content = title
            elif markdown and re.search(r"\[[^\]]+\]\([^)]+\)", line):
                block_type = "link"
                content = line
            else:
                block_type = "paragraph"
                content = line
            blocks.append(
                cls._block(request, block_id=f"block_line_{line_number}", block_type=block_type, text=content, source_span=SourceSpan(line_range=[line_number, line_number], section_path=list(current_section)))
            )
        return cls._ensure_blocks(blocks, text, request), [], [], [], 1.0

    @classmethod
    def _parse_image_ocr(
        cls,
        text: str,
        request: ParseDocumentRequest,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        block = cls._block(
            request,
            block_id="block_ocr_1",
            block_type="ocr_text",
            text=text.strip(),
            source_span=SourceSpan(page=1, bbox=[0.0, 0.0, 1024.0, 768.0]),
            confidence=0.86,
        )
        figure = DocumentFigure(
            figure_id="figure_1",
            description="OCR source image",
            source_span=SourceSpan(page=1, bbox=[0.0, 0.0, 1024.0, 768.0]),
            uri=request.source_uri,
        )
        return [block], [], [figure], ["OCR confidence should be reviewed before high-risk use."], 0.86

    @classmethod
    def _parse_code(
        cls,
        text: str,
        request: ParseDocumentRequest,
    ) -> tuple[list[DocumentBlock], list[DocumentTable], list[DocumentFigure], list[str], float]:
        lines = cls._lines(text)
        return [
            cls._block(
                request,
                block_id="block_code_1",
                block_type="code_block",
                text="\n".join(lines),
                source_span=SourceSpan(line_range=[1, max(len(lines), 1)]),
            )
        ], [], [], [], 1.0

    @staticmethod
    def _lines(text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    @classmethod
    def _ensure_blocks(
        cls,
        blocks: list[DocumentBlock],
        text: str,
        request: ParseDocumentRequest,
    ) -> list[DocumentBlock]:
        if blocks:
            return blocks
        return [
            cls._block(
                request,
                block_id="block_1",
                block_type="paragraph",
                text=text.strip(),
                source_span=SourceSpan(line_range=[1, 1]),
            )
        ]

    @staticmethod
    def _block(
        request: ParseDocumentRequest,
        *,
        block_id: str,
        block_type: str,
        text: str,
        source_span: SourceSpan,
        confidence: float = 1.0,
    ) -> DocumentBlock:
        return DocumentBlock(
            block_id=block_id,
            type=block_type,
            text=text,
            source_span=source_span,
            acl_scope=request.acl_scope,
            sensitivity_tags=list(request.sensitivity_tags),
            confidence=confidence,
        )


__all__ = ["ParseGateway"]
