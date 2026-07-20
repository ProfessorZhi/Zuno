from __future__ import annotations

import hashlib
import json
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
from .router import (
    PARSER_ADAPTER_CONTRACTS,
    PARSER_CAPABILITY_MATRIX,
    adapter_boundary_metadata,
    build_index_handoff_payload,
    select_parser_for_format,
)


IR_SCHEMA_VERSION = "canonical-document-ir-v1"
MAX_PARSE_ATTEMPTS = 2


class ParseGateway:
    """PHASE04 deterministic Parse Gateway runtime surface."""

    _jobs: dict[str, ParseDocumentResult] = {}
    _job_snapshots: dict[str, ParseJobSnapshot] = {}

    @classmethod
    def submit_parse_job(cls, request: ParseDocumentRequest) -> ParseDocumentResult:
        started = time.perf_counter()
        result = cls._blocked_result(request) or cls.parse_document(request)
        cls._jobs[result.job_id] = result
        cls._job_snapshots[result.job_id] = cls._build_job_snapshot(
            result=result,
            request=request,
            attempt=1,
            previous_job_id=None,
            duration_ms=(time.perf_counter() - started) * 1000,
            lifecycle_start="accepted",
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
        attempt = previous.attempt + 1
        result = cls._blocked_result(request) or cls.parse_document(request)
        if result.status == "failed" and attempt > MAX_PARSE_ATTEMPTS:
            result = result.model_copy(
                update={
                    "status": "dead_letter",
                    "failure": result.failure.model_copy(update={"retryable": False})
                    if result.failure
                    else None,
                }
            )
        cls._jobs[result.job_id] = result
        cls._job_snapshots[result.job_id] = cls._build_job_snapshot(
            result=result,
            request=request,
            attempt=attempt,
            previous_job_id=previous.job_id,
            duration_ms=(time.perf_counter() - started) * 1000,
            lifecycle_start="retrying",
        )
        return result

    @classmethod
    def cancel_parse_job(cls, job_id: str, *, reason: str) -> ParseDocumentResult:
        previous = cls.get_job_snapshot(job_id)
        result = ParseDocumentResult(
            job_id=job_id,
            status="cancelled",
            failure=ParserFailure(
                parser_id=previous.parser_id,
                format=previous.parser_format,
                reason=reason,
                retryable=False,
            ),
            diagnostics=[
                ParserDiagnostic(
                    code="parse_cancelled",
                    message=reason,
                    severity="warning",
                    parser_id=previous.parser_id,
                    format=previous.parser_format,
                )
            ],
        )
        cls._jobs[job_id] = result
        cls._job_snapshots[job_id] = previous.model_copy(
            update={
                "status": "cancelled",
                "retryable": False,
                "failure_reason": reason,
                "last_error": reason,
                "failure_snapshot": {
                    **previous.failure_snapshot,
                    "cancelled": True,
                    "reason": reason,
                },
                "parser_diagnostics": [diagnostic.model_dump() for diagnostic in result.diagnostics],
                "metrics": previous.metrics.model_copy(update={"status": "cancelled"}),
                "status_timeline": [
                    *previous.status_timeline,
                    {"status": "cancelled", "attempt": previous.attempt, "reason": reason},
                ],
            }
        )
        return result

    @classmethod
    def parse_document(cls, request: ParseDocumentRequest) -> ParseDocumentResult:
        capability = select_parser_for_format(request.source_uri or request.mime_type)
        parser_id = capability.default_parser
        known_format = capability.format in PARSER_CAPABILITY_MATRIX
        adapter_contract = PARSER_ADAPTER_CONTRACTS.get(parser_id)
        diagnostics = [
            ParserDiagnostic(
                code="parser_selected",
                message=f"Selected {parser_id} for {capability.format}.",
                parser_id=parser_id,
                format=capability.format,
            )
        ]
        if not known_format:
            diagnostics.append(
                ParserDiagnostic(
                    code="unknown_format_fallback",
                    message=f"Unknown format {capability.format}; using deterministic fallback parser.",
                    severity="warning",
                    parser_id=parser_id,
                    format=capability.format,
                    metadata={
                        "fallback_used": True,
                        "fallback_reason": capability.fallback_reason,
                    },
                )
            )
        if adapter_contract and adapter_contract.external_dependency_status == "target_blocked":
            diagnostics.append(
                ParserDiagnostic(
                    code="target_blocked_adapter",
                    message=adapter_contract.blocked_reason or "External parser dependency is not available.",
                    severity="warning",
                    parser_id=parser_id,
                    format=capability.format,
                    metadata=adapter_boundary_metadata(parser_id, fallback=capability.fallback),
                )
            )
        if parser_id == "local_ocr_vlm":
            diagnostics.append(
                ParserDiagnostic(
                    code="local_ocr_vlm_fallback",
                    message="Local OCR/VLM fallback is executable; live MinerU provider remains measurement blocked.",
                    severity="warning",
                    parser_id=parser_id,
                    format=capability.format,
                    metadata={
                        "live_provider": "mineru_ocr_vlm",
                        "live_provider_status": "measurement_blocked",
                        "network_policy": "deny_by_default",
                        "requires_human_review": True,
                    },
                )
            )
        parser_config_hash = cls._parser_config_hash(request)
        job_id = f"parse_{uuid4().hex[:12]}"

        try:
            source_text = cls._source_text(request)
            if not source_text.strip():
                raise ValueError("empty source content")
            source_sha256 = cls._source_sha256(request, source_text)
            ir_schema_version = request.ir_schema_version or IR_SCHEMA_VERSION

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
                source_id=request.source_id or request.document_id,
                workspace_id=request.workspace_id,
                source_uri=request.source_uri,
                mime_type=request.mime_type,
                hash=request.hash or source_sha256,
                source_sha256=source_sha256,
                parser_id=parser_id,
                parser_version=request.parser_version,
                parser_config_hash=parser_config_hash,
                document_version_id=cls._document_version_id(
                    document_id=request.document_id,
                    source_sha256=source_sha256,
                    parser_id=parser_id,
                    parser_version=request.parser_version,
                    parser_config_hash=parser_config_hash,
                    ir_schema_version=ir_schema_version,
                ),
                schema_version=request.schema_version or ir_schema_version,
                ir_schema_version=ir_schema_version,
                parent_document_version_id=request.parent_document_version_id,
                derived_from=list(request.derived_from),
                asset_refs=list(request.asset_refs),
                redaction_status=request.redaction_status,
                retention_policy=request.retention_policy,
                fallback_used=not known_format,
                fallback_reason=capability.fallback_reason if not known_format else None,
                target_blocked=bool(
                    adapter_contract
                    and adapter_contract.external_dependency_status == "target_blocked"
                ),
                blocked_reason=(
                    adapter_contract.blocked_reason
                    if adapter_contract
                    and adapter_contract.external_dependency_status == "target_blocked"
                    else None
                ),
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
        lifecycle_start: str,
    ) -> ParseJobSnapshot:
        capability = select_parser_for_format(request.source_uri or request.mime_type)
        parser_id = cls._snapshot_parser_id(result, capability.default_parser)
        error_count = sum(1 for diagnostic in result.diagnostics if diagnostic.severity == "error")
        warning_count = sum(1 for diagnostic in result.diagnostics if diagnostic.severity == "warning")
        document = result.document
        adapter_contract = PARSER_ADAPTER_CONTRACTS.get(parser_id)
        failure_reason = result.failure.reason if result.failure else None
        error_class = cls._error_class(failure_reason)
        source_sha256 = cls._source_sha256(request, cls._source_text(request))
        parser_config_hash = cls._parser_config_hash(request)
        metrics = ParserJobMetrics(
            status=result.status,
            parser_name=parser_id,
            format=capability.format,
            block_count=len(document.blocks) if document else 0,
            table_count=len(document.tables) if document else 0,
            figure_count=len(document.figures) if document else 0,
            warning_count=warning_count,
            error_count=error_count,
            duration_ms=round(duration_ms, 3),
        )
        status_timeline = [{"status": lifecycle_start, "attempt": attempt}]
        if result.status == "blocked":
            status_timeline.append({"status": "blocked", "attempt": attempt, "parser_id": parser_id})
        else:
            status_timeline.extend(
                [
                    {"status": "running", "attempt": attempt, "parser_id": parser_id},
                    {"status": result.status, "attempt": attempt},
                ]
            )
        retryable = result.status == "failed" and attempt < MAX_PARSE_ATTEMPTS
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
            attempt_count=attempt,
            parse_attempt_id=f"attempt_{result.job_id}_{attempt}",
            parse_idempotency_key=cls._parse_idempotency_key(
                workspace_id=request.workspace_id,
                source_sha256=source_sha256,
                parser_id=parser_id,
                parser_version=request.parser_version,
                parser_config_hash=parser_config_hash,
            ),
            retryable=retryable,
            previous_job_id=previous_job_id,
            blocked_reason=result.failure.reason if result.status == "blocked" and result.failure else None,
            failure_reason=failure_reason,
            error_class=error_class,
            last_error=failure_reason,
            failure_snapshot=cls._failure_snapshot(
                result=result,
                error_class=error_class,
                attempt=attempt,
            ),
            parser_diagnostics=[diagnostic.model_dump() for diagnostic in result.diagnostics],
            retry_policy={
                "max_attempts": MAX_PARSE_ATTEMPTS,
                "next_status": "retrying" if retryable else None,
            },
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

    @classmethod
    def _source_provenance(
        cls,
        result: ParseDocumentResult,
        request: ParseDocumentRequest,
        parser_id: str,
    ) -> dict:
        if result.document is not None:
            metadata = result.document.metadata
            return {
                "document_id": metadata.document_id,
                "source_id": metadata.source_id,
                "workspace_id": metadata.workspace_id,
                "source_uri": metadata.source_uri,
                "mime_type": metadata.mime_type,
                "hash": metadata.hash,
                "source_sha256": metadata.source_sha256,
                "parser_id": metadata.parser_id,
                "parser_version": metadata.parser_version,
                "parser_config_hash": metadata.parser_config_hash,
                "document_version_id": metadata.document_version_id,
                "schema_version": metadata.schema_version,
                "ir_schema_version": metadata.ir_schema_version,
                "acl_scope": metadata.acl_scope,
                "sensitivity_tags": list(metadata.sensitivity_tags),
                "confidence": result.document.provenance.confidence,
            }
        return {
            "document_id": request.document_id,
            "source_id": request.source_id or request.document_id,
            "workspace_id": request.workspace_id,
            "source_uri": request.source_uri,
            "mime_type": request.mime_type,
            "hash": request.hash,
            "source_sha256": request.hash,
            "parser_id": parser_id,
            "parser_version": request.parser_version,
            "parser_config_hash": cls._parser_config_hash(request),
            "schema_version": request.schema_version,
            "ir_schema_version": request.ir_schema_version,
            "acl_scope": request.acl_scope,
            "sensitivity_tags": list(request.sensitivity_tags),
        }

    @classmethod
    def _blocked_result(cls, request: ParseDocumentRequest) -> ParseDocumentResult | None:
        capability = select_parser_for_format(request.source_uri or request.mime_type)
        parser_id = capability.default_parser
        adapter_contract = PARSER_ADAPTER_CONTRACTS.get(parser_id)
        if not adapter_contract or adapter_contract.external_dependency_status != "target_blocked":
            return None
        reason = adapter_contract.blocked_reason or "External parser dependency is not available."
        return ParseDocumentResult(
            job_id=f"parse_{uuid4().hex[:12]}",
            status="blocked",
            failure=ParserFailure(
                parser_id=parser_id,
                format=capability.format,
                reason=reason,
                fallback=capability.fallback,
                retryable=False,
            ),
            diagnostics=[
                ParserDiagnostic(
                    code="target_blocked_adapter",
                    message=reason,
                    severity="warning",
                    parser_id=parser_id,
                    format=capability.format,
                    metadata=adapter_boundary_metadata(parser_id, fallback=capability.fallback),
                )
            ],
        )

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

    @staticmethod
    def _parser_config_hash(request: ParseDocumentRequest) -> str:
        if request.parser_config_hash:
            return request.parser_config_hash
        payload = json.dumps(request.parser_config, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _source_sha256(request: ParseDocumentRequest, source_text: str) -> str:
        if request.source_bytes is not None:
            return hashlib.sha256(request.source_bytes).hexdigest()
        if source_text:
            return hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        return request.hash or ""

    @staticmethod
    def _document_version_id(
        *,
        document_id: str,
        source_sha256: str,
        parser_id: str,
        parser_version: str,
        parser_config_hash: str,
        ir_schema_version: str,
    ) -> str:
        return ":".join(
            [
                document_id,
                source_sha256,
                parser_id,
                parser_version,
                parser_config_hash,
                ir_schema_version,
            ]
        )

    @staticmethod
    def _parse_idempotency_key(
        *,
        workspace_id: str,
        source_sha256: str,
        parser_id: str,
        parser_version: str,
        parser_config_hash: str,
    ) -> str:
        payload = ":".join(
            [workspace_id, source_sha256, parser_id, parser_version, parser_config_hash]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _error_class(reason: str | None) -> str | None:
        if not reason:
            return None
        if "empty source content" in reason:
            return "ValueError"
        return "ParserError"

    @staticmethod
    def _failure_snapshot(
        *,
        result: ParseDocumentResult,
        error_class: str | None,
        attempt: int,
    ) -> dict:
        if result.status not in {"failed", "blocked", "dead_letter", "cancelled"}:
            return {}
        return {
            "status": result.status,
            "attempt": attempt,
            "error_class": error_class,
            "reason": result.failure.reason if result.failure else None,
            "blocked": result.status == "blocked",
            "dead_letter": result.status == "dead_letter",
        }

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
