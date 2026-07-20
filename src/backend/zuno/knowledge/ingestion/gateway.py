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
    TransformLedgerEntry,
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
        if result.status == "failed" and attempt >= MAX_PARSE_ATTEMPTS:
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
        if parser_id == "local_office_archive":
            diagnostics.append(
                ParserDiagnostic(
                    code="local_office_archive_fallback",
                    message="Local Office/Archive fallback is executable; live Unstructured / MarkItDown provider remains measurement blocked.",
                    severity="warning",
                    parser_id=parser_id,
                    format=capability.format,
                    metadata={
                        "live_provider": "unstructured_markitdown",
                        "live_provider_status": "measurement_blocked",
                        "network_policy": "local_only",
                        "archive_policy": "manifest_only_no_unpack",
                    },
                )
            )
        parser_config_hash = cls._parser_config_hash(request)
        job_id = cls._request_job_id(request)
        diagnostics.append(
            ParserDiagnostic(
                code="parser_contract_boundary",
                message="Parser request is bound to timeout, security policy, and source input contract.",
                parser_id=parser_id,
                format=capability.format,
                metadata={
                    "timeout_seconds": cls._effective_timeout_seconds(request, capability.timeout_seconds),
                    "sandbox_policy": capability.sandbox_policy,
                    "network_policy": adapter_contract.network_policy if adapter_contract else "unknown",
                    "security_policy_ref": request.security_policy_ref,
                    "security_epoch_ref": request.security_epoch_ref,
                    "source_input_mode": cls._source_input_mode(request),
                    "cancel_requested": request.cancel_requested,
                },
            )
        )
        if request.cancel_requested:
            return ParseDocumentResult(
                job_id=job_id,
                status="cancelled",
                failure=ParserFailure(
                    parser_id=parser_id,
                    format=capability.format,
                    reason="parse request cancelled before adapter execution",
                    fallback=capability.fallback,
                    retryable=False,
                    failure_classification="cancelled",
                ),
                diagnostics=[
                    *diagnostics,
                    ParserDiagnostic(
                        code="parse_cancelled",
                        message="parse request cancelled before adapter execution",
                        severity="warning",
                        parser_id=parser_id,
                        format=capability.format,
                    ),
                ],
            )
        policy_failure = cls._parser_policy_failure_result(
            request=request,
            parser_id=parser_id,
            format_name=capability.format,
            fallback=capability.fallback,
            job_id=job_id,
            diagnostics=diagnostics,
        )
        if policy_failure is not None:
            return policy_failure

        try:
            source_text = cls._source_text(request)
            if not source_text.strip():
                raise ValueError("empty source content")
            source_sha256 = cls._source_sha256(request, source_text)
            object_ref_metadata = cls._source_object_contract_metadata(
                request=request,
                source_sha256=source_sha256,
            )
            if object_ref_metadata:
                source_sha256 = object_ref_metadata["content_hash"]
                diagnostics.append(
                    ParserDiagnostic(
                        code="object_ref_input_bound",
                        message="Parser input is bound to PHASE04 SourceObject ObjectRef and manifest.",
                        parser_id=parser_id,
                        format=capability.format,
                        metadata=object_ref_metadata,
                    )
                )
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
                source_object_ref=request.source_object_ref,
                object_manifest_ref=object_ref_metadata.get("object_manifest_ref"),
                workspace_id=request.workspace_id,
                source_uri=request.source_uri,
                mime_type=request.mime_type,
                hash=object_ref_metadata.get("content_hash") or request.hash or source_sha256,
                source_sha256=source_sha256,
                parser_id=parser_id,
                parser_version=request.parser_version,
                parser_config_hash=parser_config_hash,
                document_version_id=request.document_version_id
                or cls._document_version_id(
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
                security_policy_ref=request.security_policy_ref,
                security_epoch_ref=request.security_epoch_ref,
            )
            document = CanonicalDocumentIR(
                metadata=metadata,
                blocks=blocks,
                tables=tables,
                figures=figures,
                transform_ledger=[
                    cls._transform_ledger_entry(
                        source_sha256=source_sha256,
                        parser_id=parser_id,
                        parser_version=request.parser_version,
                        parser_config_hash=parser_config_hash,
                        ir_schema_version=ir_schema_version,
                        blocks=blocks,
                        tables=tables,
                        figures=figures,
                    )
                ],
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
                    failure_classification=cls._failure_classification(str(exc)),
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
        source_sha256 = cls._source_identity_hash(request, cls._source_text(request))
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
            confidence=document.provenance.confidence if document else None,
            timeout_seconds=cls._effective_timeout_seconds(request, capability.timeout_seconds),
            source_input_mode=cls._source_input_mode(request),
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
            parse_plan_id=request.parse_plan_id or "",
            parse_attempt_id=request.parse_attempt_id or f"attempt_{result.job_id}_{attempt}",
            parse_idempotency_key=request.parse_idempotency_key or cls._parse_idempotency_key(
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
                "source_object_ref": metadata.source_object_ref,
                "object_manifest_ref": metadata.object_manifest_ref,
                "mime_type": metadata.mime_type,
                "hash": metadata.hash,
                "source_sha256": metadata.source_sha256,
                "parser_id": metadata.parser_id,
                "parser_version": metadata.parser_version,
                "parser_config_hash": metadata.parser_config_hash,
                "document_version_id": metadata.document_version_id,
                "parse_plan_id": request.parse_plan_id,
                "parse_job_id": request.parse_job_id or result.job_id,
                "parse_attempt_id": request.parse_attempt_id,
                "parse_idempotency_key": request.parse_idempotency_key,
                "schema_version": metadata.schema_version,
                "ir_schema_version": metadata.ir_schema_version,
                "acl_scope": metadata.acl_scope,
                "sensitivity_tags": list(metadata.sensitivity_tags),
                "security_policy_ref": metadata.security_policy_ref,
                "security_epoch_ref": metadata.security_epoch_ref,
                "confidence": result.document.provenance.confidence,
            }
        return {
            "document_id": request.document_id,
            "source_id": request.source_id or request.document_id,
            "workspace_id": request.workspace_id,
            "source_uri": request.source_uri,
            "source_object_ref": request.source_object_ref,
            "object_manifest_ref": request.source_object_manifest.get("object_manifest_ref"),
            "mime_type": request.mime_type,
            "hash": request.hash,
            "source_sha256": cls._source_identity_hash(request, cls._source_text(request)),
            "parser_id": parser_id,
            "parser_version": request.parser_version,
            "parser_config_hash": cls._parser_config_hash(request),
            "document_version_id": request.document_version_id,
            "parse_plan_id": request.parse_plan_id,
            "parse_job_id": request.parse_job_id or result.job_id,
            "parse_attempt_id": request.parse_attempt_id,
            "parse_idempotency_key": request.parse_idempotency_key,
            "schema_version": request.schema_version,
            "ir_schema_version": request.ir_schema_version,
            "acl_scope": request.acl_scope,
            "sensitivity_tags": list(request.sensitivity_tags),
            "security_policy_ref": request.security_policy_ref,
            "security_epoch_ref": request.security_epoch_ref,
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
            job_id=cls._request_job_id(request),
            status="blocked",
            failure=ParserFailure(
                parser_id=parser_id,
                format=capability.format,
                reason=reason,
                fallback=capability.fallback,
                retryable=False,
                failure_classification="dependency_blocked",
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

    @classmethod
    def _source_identity_hash(cls, request: ParseDocumentRequest, source_text: str) -> str:
        manifest_hash = request.source_object_manifest.get("content_hash")
        if request.source_object_ref and isinstance(manifest_hash, str) and manifest_hash:
            return manifest_hash
        return cls._source_sha256(request, source_text)

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
        if "source object" in reason.lower() or "objectref" in reason.lower():
            return "ObjectRefContractViolation"
        return "ParserError"

    @staticmethod
    def _failure_classification(reason: str | None) -> str:
        if not reason:
            return "parser_failure"
        lowered = reason.lower()
        if "oversized" in lowered:
            return "oversized_source"
        if "encrypted" in lowered:
            return "encrypted_source"
        if "corrupt" in lowered:
            return "corrupt_source"
        if "sandbox" in lowered:
            return "sandbox_denied"
        if "empty source content" in lowered:
            return "empty_source"
        if "source object" in lowered or "objectref" in lowered:
            return "object_ref_contract_violation"
        if "archive manifest" in lowered:
            return "unsafe_or_empty_archive"
        return "parser_failure"

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
            "failure_classification": result.failure.failure_classification if result.failure else None,
            "reason": result.failure.reason if result.failure else None,
            "blocked": result.status == "blocked",
            "dead_letter": result.status == "dead_letter",
        }

    @classmethod
    def _parser_policy_failure_result(
        cls,
        *,
        request: ParseDocumentRequest,
        parser_id: str,
        format_name: str,
        fallback: str | None,
        job_id: str,
        diagnostics: list[ParserDiagnostic],
    ) -> ParseDocumentResult | None:
        reason = cls._parser_policy_failure_reason(request)
        if reason is None:
            return None
        classification = cls._failure_classification(reason)
        return ParseDocumentResult(
            job_id=job_id,
            status="failed",
            failure=ParserFailure(
                parser_id=parser_id,
                format=format_name,
                reason=reason,
                fallback=fallback,
                retryable=False,
                failure_classification=classification,
            ),
            diagnostics=[
                *diagnostics,
                ParserDiagnostic(
                    code="parser_policy_denied",
                    message=reason,
                    severity="error",
                    parser_id=parser_id,
                    format=format_name,
                    metadata={
                        "failure_classification": classification,
                        "source_size_bytes": cls._source_size_bytes(request),
                        "max_size_bytes": request.parser_config.get("max_size_bytes"),
                        "sandbox_policy_ref": request.parser_config.get("sandbox_policy_ref"),
                    },
                ),
            ],
        )

    @staticmethod
    def _request_job_id(request: ParseDocumentRequest) -> str:
        return request.parse_job_id or f"parse_{uuid4().hex[:12]}"

    @classmethod
    def _parser_policy_failure_reason(cls, request: ParseDocumentRequest) -> str | None:
        if request.parser_config.get("encrypted") is True:
            return "encrypted source rejected by parser policy"
        if request.parser_config.get("corrupt") is True:
            return "corrupt source rejected by parser policy"
        if request.parser_config.get("sandbox_denied") is True:
            return "sandbox denied parser execution"
        max_size = request.parser_config.get("max_size_bytes")
        if max_size is not None and cls._source_size_bytes(request) > int(max_size):
            return "oversized source rejected by parser policy"
        return None

    @staticmethod
    def _source_size_bytes(request: ParseDocumentRequest) -> int:
        if request.source_bytes is not None:
            return len(request.source_bytes)
        if request.source_text is not None:
            return len(request.source_text.encode("utf-8"))
        manifest_size = request.source_object_manifest.get("size_bytes")
        if manifest_size is not None:
            return int(manifest_size)
        return 0

    @staticmethod
    def _transform_ledger_entry(
        *,
        source_sha256: str,
        parser_id: str,
        parser_version: str,
        parser_config_hash: str,
        ir_schema_version: str,
        blocks: list[DocumentBlock],
        tables: list[DocumentTable],
        figures: list[DocumentFigure],
    ) -> TransformLedgerEntry:
        payload = {
            "blocks": [block.model_dump() for block in blocks],
            "tables": [table.model_dump() for table in tables],
            "figures": [figure.model_dump() for figure in figures],
            "parser_id": parser_id,
            "parser_version": parser_version,
            "parser_config_hash": parser_config_hash,
            "ir_schema_version": ir_schema_version,
        }
        output_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()
        return TransformLedgerEntry(
            transform_id=hashlib.sha256(
                ":".join(
                    [
                        source_sha256,
                        parser_id,
                        parser_version,
                        parser_config_hash,
                        ir_schema_version,
                    ]
                ).encode("utf-8")
            ).hexdigest(),
            transform_type="extract",
            algorithm_version=f"{parser_id}:{parser_version}:{ir_schema_version}",
            input_hash=source_sha256,
            output_hash=output_hash,
            reversible=False,
            provenance={
                "parser_id": parser_id,
                "parser_version": parser_version,
                "parser_config_hash": parser_config_hash,
                "ir_schema_version": ir_schema_version,
                "block_count": len(blocks),
                "table_count": len(tables),
                "figure_count": len(figures),
            },
        )

    @staticmethod
    def _source_input_mode(request: ParseDocumentRequest) -> str:
        if request.source_object_ref:
            if request.source_bytes is not None:
                return "object_ref_with_bytes"
            if request.source_text is not None:
                return "object_ref_with_projection"
            return "object_ref_only"
        if request.source_bytes is not None:
            return "inline_bytes"
        if request.source_text is not None:
            return "inline_text"
        return "file_uri"

    @staticmethod
    def _effective_timeout_seconds(request: ParseDocumentRequest, capability_timeout: int) -> int:
        if request.parser_timeout_seconds is None:
            return capability_timeout
        return min(request.parser_timeout_seconds, capability_timeout)

    @staticmethod
    def _source_object_contract_metadata(
        *,
        request: ParseDocumentRequest,
        source_sha256: str,
    ) -> dict:
        if not request.source_object_ref:
            return {}
        if not request.source_object_ref.startswith("s3://"):
            raise ValueError("Source ObjectRef must use the PHASE04 s3:// object namespace")
        if request.source_uri != request.source_object_ref:
            raise ValueError("Source ObjectRef must match source_uri for parser input")
        manifest = request.source_object_manifest
        required_fields = {
            "object_manifest_ref",
            "content_hash",
            "size_bytes",
            "parser_policy_ref",
            "lineage_ref",
        }
        missing = sorted(field for field in required_fields if not manifest.get(field))
        if missing:
            raise ValueError(f"Source ObjectRef manifest missing required fields: {', '.join(missing)}")
        content_hash = str(manifest["content_hash"])
        if len(content_hash) != 64 or any(char not in "0123456789abcdef" for char in content_hash):
            raise ValueError("Source ObjectRef manifest content_hash must be a lowercase SHA-256 digest")
        expected_hash = request.hash
        if request.source_bytes is not None:
            expected_hash = source_sha256
        if expected_hash is not None and content_hash != expected_hash:
            raise ValueError("Source ObjectRef manifest content_hash does not match parser input bytes")
        size_bytes = int(manifest["size_bytes"])
        if size_bytes <= 0:
            raise ValueError("Source ObjectRef manifest size_bytes must be positive")
        if manifest.get("workspace_id") and manifest["workspace_id"] != request.workspace_id:
            raise ValueError("Source ObjectRef manifest workspace_id does not match parser request")
        return {
            "source_object_ref": request.source_object_ref,
            "object_manifest_ref": manifest["object_manifest_ref"],
            "content_hash": content_hash,
            "size_bytes": size_bytes,
            "parser_policy_ref": manifest["parser_policy_ref"],
            "lineage_ref": manifest["lineage_ref"],
            "classification_ref": manifest.get("classification_ref"),
            "security_epoch_ref": request.security_epoch_ref or manifest.get("security_epoch_ref"),
            "input_mode": ParseGateway._source_input_mode(request),
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

    @classmethod
    def _block(
        cls,
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
            order_index=cls._order_index_from_block_id(block_id),
            style=cls._style_for_block(block_type=block_type),
            acl_scope=request.acl_scope,
            sensitivity_tags=list(request.sensitivity_tags),
            confidence=confidence,
        )

    @staticmethod
    def _order_index_from_block_id(block_id: str) -> int | None:
        match = re.search(r"(\d+)$", block_id)
        return int(match.group(1)) if match else None

    @staticmethod
    def _style_for_block(*, block_type: str) -> dict:
        if block_type == "heading":
            return {"role": "heading"}
        if block_type in {"slide_title", "slide_body"}:
            return {"role": "slide", "layout": block_type}
        if block_type in {"table", "table_cell"}:
            return {"role": "structured_table"}
        if block_type == "code_block":
            return {"role": "code"}
        return {}


__all__ = ["ParseGateway"]
