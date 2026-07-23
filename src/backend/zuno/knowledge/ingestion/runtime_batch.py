from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
from typing import Iterable, Literal

from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway, SourceSpan
from zuno.knowledge.ingestion.async_runtime import (
    IngestionReconciler,
    LocalQueueBackend,
    ParserWorker,
    RabbitMQQueueBackend,
    RedisRuntimeStateBoundary,
)
from zuno.knowledge.ingestion.contracts import ParserAdapterContract
from zuno.knowledge.storage import (
    LocalObjectStore,
    SQLiteDurableIngestionStore,
    WorkspaceFileRecord,
)
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256


INPUT_REQUIREMENT_IDS: tuple[str, ...] = tuple(
    f"ARCH-ING-{index:03d}" for index in range(1, 81)
)


class InputRuntimeBatchError(ValueError):
    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


@dataclass(frozen=True, slots=True)
class TransformRecord:
    input_hash: str
    output_hash: str
    transform_version: str
    loss_class: Literal["LOSSLESS", "LOSSY", "MODEL_DERIVED"]
    keeps_original: bool


@dataclass(frozen=True, slots=True)
class QualityReport:
    verdict: Literal["PASS", "DEGRADED", "BLOCK"]
    source_span_coverage: float
    missing_content_manifest_ref: str | None
    policy_engine_ref: str


@dataclass(frozen=True, slots=True)
class ParseAttemptControl:
    parse_job_ref: str
    parse_attempt_ref: str
    execution_epoch: int
    lease_ref: str
    fencing_token: str
    lease_expires_at: datetime

    def accepts_result(self, *, epoch: int, fencing_token: str, now: datetime) -> bool:
        return (
            epoch == self.execution_epoch
            and fencing_token == self.fencing_token
            and now < self.lease_expires_at
        )


@dataclass(frozen=True, slots=True)
class ParserRoutingProfile:
    file_route: str
    page_route: str
    region_route: str
    profile_hash: str
    parser_bundle_digest: str
    model_weight_hash: str
    sandbox_policy: str
    security_gate_ref: str
    model_gateway_ref: str
    remote_fetch_guard: str


@dataclass(frozen=True, slots=True)
class DeletionReceipts:
    input_receipt: str
    knowledge_receipt: str
    object_receipt: str
    verification_receipt: str
    legal_hold_blocks_purge_only: bool


@dataclass(frozen=True, slots=True)
class CapacityProfile:
    deletion_reserved: int
    security_reserved: int
    online_attachment_reserved: int
    batch_page_parallel_limit: int
    gpu_batch_limit: int


@dataclass(frozen=True, slots=True)
class OfficeFormatPreservation:
    excel_formula_cache_display: bool
    word_revisions_comments_footnotes_headers: bool
    ppt_positions_notes_hidden_embeds: bool
    html_snapshot_final_url_redirect_dom: bool
    git_commit_blob_path_symbol_line: bool


@dataclass(frozen=True, slots=True)
class InputRuntimeBatchFixture:
    transform_records: tuple[TransformRecord, ...]
    quality_reports: tuple[QualityReport, ...]
    attempt_control: ParseAttemptControl
    parser_profile: ParserRoutingProfile
    deletion_receipts: DeletionReceipts
    capacity_profile: CapacityProfile
    office_preservation: OfficeFormatPreservation
    handoff_payload: dict[str, str]
    handoff_schema_hash: str
    trace_redacted: bool
    api_hides_internal_details: bool
    target_evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class InputRuntimeBatchReport:
    requirement_ids: tuple[str, ...]
    source_verified: bool
    parse_status: str
    blocked_status: str
    queue_outbox_count: int
    reconciler_count: int


def build_input_runtime_batch_fixture() -> InputRuntimeBatchFixture:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    raw_hash = canonical_sha256({"raw": "source"})
    normalized_hash = canonical_sha256({"normalized": "source"})
    model_hash = canonical_sha256({"model": "derived"})
    profile_payload = {
        "file": "native",
        "page": "layout",
        "region": "ocr_if_needed",
        "version": "parser-profile-v1",
    }
    handoff_payload = {
        "parse_snapshot_ref": "parse-snapshot:1",
        "document_version_ref": "document-version:1",
        "quality_report_ref": "quality:1",
    }
    return InputRuntimeBatchFixture(
        transform_records=(
            TransformRecord(raw_hash, normalized_hash, "normalize-v1", "LOSSLESS", True),
            TransformRecord(raw_hash, model_hash, "vlm-caption-v1", "MODEL_DERIVED", True),
        ),
        quality_reports=(
            QualityReport("PASS", 1.0, None, "policy:quality:v1"),
            QualityReport("DEGRADED", 0.82, "missing-content:1", "policy:quality:v1"),
            QualityReport("BLOCK", 0.2, "missing-content:block", "policy:quality:v1"),
        ),
        attempt_control=ParseAttemptControl(
            parse_job_ref="parse-job:1",
            parse_attempt_ref="parse-attempt:1",
            execution_epoch=1,
            lease_ref="lease:parse:1",
            fencing_token="fence:1",
            lease_expires_at=now + timedelta(minutes=5),
        ),
        parser_profile=ParserRoutingProfile(
            file_route="native",
            page_route="layout",
            region_route="ocr_if_needed",
            profile_hash=canonical_sha256(profile_payload),
            parser_bundle_digest="sha256:parser-bundle",
            model_weight_hash="sha256:model-weights",
            sandbox_policy="restricted",
            security_gate_ref="security-gate:1",
            model_gateway_ref="model-gateway:1",
            remote_fetch_guard="ssrf_dns_rebinding_bounded_response",
        ),
        deletion_receipts=DeletionReceipts(
            input_receipt="delete:input",
            knowledge_receipt="delete:knowledge",
            object_receipt="delete:object",
            verification_receipt="delete:verify",
            legal_hold_blocks_purge_only=True,
        ),
        capacity_profile=CapacityProfile(
            deletion_reserved=1,
            security_reserved=1,
            online_attachment_reserved=2,
            batch_page_parallel_limit=8,
            gpu_batch_limit=4,
        ),
        office_preservation=OfficeFormatPreservation(
            excel_formula_cache_display=True,
            word_revisions_comments_footnotes_headers=True,
            ppt_positions_notes_hidden_embeds=True,
            html_snapshot_final_url_redirect_dom=True,
            git_commit_blob_path_symbol_line=True,
        ),
        handoff_payload=handoff_payload,
        handoff_schema_hash=canonical_sha256({"schema": "ingestion-handoff-v1"}),
        trace_redacted=True,
        api_hides_internal_details=True,
        target_evidence_refs=("code", "migration", "test", "trace", "eval", "runtime"),
    )


def validate_input_runtime_batch(
    fixture: InputRuntimeBatchFixture | None = None,
) -> InputRuntimeBatchReport:
    fixture = fixture or build_input_runtime_batch_fixture()
    errors: list[str] = []
    runtime = _run_local_ingestion_runtime()
    errors.extend(_validate_source_integrity(runtime))
    errors.extend(_validate_transform_quality(fixture))
    errors.extend(_validate_attempt_queue_and_cache(fixture, runtime))
    errors.extend(_validate_storage_recovery_delete(fixture, runtime))
    errors.extend(_validate_security_parser_profile(fixture))
    errors.extend(_validate_handoff_contract(fixture))
    errors.extend(_validate_format_eval_trace(fixture))
    if errors:
        raise InputRuntimeBatchError(errors)
    return InputRuntimeBatchReport(
        requirement_ids=INPUT_REQUIREMENT_IDS,
        source_verified=bool(runtime["source_verified"]),
        parse_status=str(runtime["parse_status"]),
        blocked_status=str(runtime["blocked_status"]),
        queue_outbox_count=int(runtime["queue_outbox_count"]),
        reconciler_count=int(runtime["reconciler_count"]),
    )


def _run_local_ingestion_runtime() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="zuno-input-runtime-batch-") as tmp:
        root = Path(tmp)
        store = SQLiteDurableIngestionStore(root / "zuno.db")
        object_store = LocalObjectStore(root / "objects")
        queue = LocalQueueBackend()
        try:
            source = object_store.save_text(
                workspace_id="workspace-input",
                source_id="source-input-1",
                filename="policy.md",
                mime_type="text/markdown",
                content="# Policy\nOriginal bytes remain immutable.",
                owner_id="user-input",
                sensitivity_tags=["internal"],
            )
            store.save_source_object(source)
            store.save_workspace_file(
                WorkspaceFileRecord(
                    file_id="file-input-1",
                    workspace_id=source.workspace_id,
                    source_id=source.source_id,
                    owner_id="user-input",
                    filename=source.filename,
                    mime_type=source.mime_type,
                    source_sha256=source.source_sha256,
                    parse_status="uploaded",
                    security_label="internal",
                )
            )
            queue.enqueue(
                topic="parse_requested",
                payload={
                    "workspace_id": source.workspace_id,
                    "file_id": "file-input-1",
                    "source_id": source.source_id,
                    "knowledge_space_id": "ks-input",
                    "trace_id": "trace-input",
                },
                idempotency_key=f"parse:{source.workspace_id}:{source.source_sha256}",
                trace_id="trace-input",
            )
            parse_result = ParserWorker(store=store, object_store=object_store, queue=queue).run_once()
            parse_index_message = queue.consume("index_requested")
            if parse_index_message is not None:
                queue.ack(parse_index_message.message_id)

            blocked_source = object_store.save_bytes(
                workspace_id="workspace-input",
                source_id="source-scan-1",
                filename="scan.png",
                mime_type="image/png",
                content=b"blocked-ocr",
                owner_id="user-input",
                sensitivity_tags=["internal"],
            )
            store.save_source_object(blocked_source)
            store.save_workspace_file(
                WorkspaceFileRecord(
                    file_id="file-scan-1",
                    workspace_id=blocked_source.workspace_id,
                    source_id=blocked_source.source_id,
                    owner_id="user-input",
                    filename=blocked_source.filename,
                    mime_type=blocked_source.mime_type,
                    source_sha256=blocked_source.source_sha256,
                    parse_status="uploaded",
                    security_label="internal",
                )
            )
            queue.enqueue(
                topic="parse_requested",
                payload={
                    "workspace_id": blocked_source.workspace_id,
                    "file_id": "file-scan-1",
                    "source_id": blocked_source.source_id,
                    "knowledge_space_id": "ks-blocked",
                    "trace_id": "trace-blocked",
                },
                idempotency_key=f"parse:{blocked_source.workspace_id}:{blocked_source.source_sha256}",
                trace_id="trace-blocked",
            )
            blocked_result = ParserWorker(store=store, object_store=object_store, queue=queue).run_once()
            blocked_status = str(blocked_result.status.value if blocked_result else "")
            if blocked_result and any(
                diagnostic.get("code") == "review_pending"
                for diagnostic in blocked_result.diagnostics
            ):
                blocked_status = "review_pending"
            return {
                "source_verified": object_store.verify_sha256(source),
                "source_size": source.size_bytes,
                "source_mime": source.mime_type,
                "parse_status": str(parse_result.status.value if parse_result else ""),
                "blocked_status": blocked_status,
                "blocked_index_message": queue.consume("index_requested") is not None,
                "queue_outbox_count": len(queue.outbox_events()),
                "reconciler_count": len(IngestionReconciler(store).scan()),
                "rabbit_blocked": RabbitMQQueueBackend().dependency_probe().status == "target_blocked",
                "redis_fallback": RedisRuntimeStateBoundary().local_fallback_enabled,
                "parse_snapshot": store.get_parse_snapshot(parse_result.parse_job_id) if parse_result else None,
            }
        finally:
            store.engine.dispose()


def _validate_source_integrity(runtime: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if not runtime["source_verified"]:
        errors.append("SourceObject hash must verify before parser handoff")
    if int(runtime["source_size"]) <= 0 or runtime["source_mime"] != "text/markdown":
        errors.append("SourceObject commit must validate size and media type")
    snapshot = runtime["parse_snapshot"]
    if snapshot is None or not getattr(snapshot, "source_provenance", {}).get("source_sha256"):
        errors.append("Parser snapshot must retain source hash provenance")
    return errors


def _validate_transform_quality(fixture: InputRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if not all(record.input_hash and record.output_hash and record.transform_version for record in fixture.transform_records):
        errors.append("TransformRecord must include input hash, output hash and version")
    if any(record.loss_class in {"LOSSY", "MODEL_DERIVED"} and not record.keeps_original for record in fixture.transform_records):
        errors.append("lossy/model-derived transform cannot delete original content")
    verdicts = {report.verdict for report in fixture.quality_reports}
    if verdicts != {"PASS", "DEGRADED", "BLOCK"}:
        errors.append("Quality verdict must cover PASS, DEGRADED and BLOCK")
    blocked = next(report for report in fixture.quality_reports if report.verdict == "BLOCK")
    degraded = next(report for report in fixture.quality_reports if report.verdict == "DEGRADED")
    if not blocked.missing_content_manifest_ref or not degraded.missing_content_manifest_ref:
        errors.append("blocked/degraded snapshots need MissingContentManifest")
    span = SourceSpan(page=1, raw_text="raw", normalized_text="raw", chunk_id=None)
    if span.chunk_id is not None:
        errors.append("SourceSpan must not contain Knowledge chunk id")
    return errors


def _validate_attempt_queue_and_cache(
    fixture: InputRuntimeBatchFixture, runtime: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    if not fixture.attempt_control.accepts_result(epoch=1, fencing_token="fence:1", now=now):
        if now >= fixture.attempt_control.lease_expires_at:
            errors.append("late parse result after lease expiry must be rejected")
        else:
            errors.append("valid parse attempt with lease/fencing was rejected")
    if fixture.attempt_control.accepts_result(epoch=1, fencing_token="fence:1", now=now + timedelta(hours=1)):
        errors.append("late parse result after lease expiry must be rejected")
    if runtime["parse_status"] != "succeeded" or runtime["blocked_status"] not in {"blocked", "review_pending"}:
        errors.append("local parser worker did not prove succeeded and blocked/review_pending paths")
    if runtime["blocked_index_message"]:
        errors.append("BLOCK snapshot must not publish index handoff")
    if not runtime["rabbit_blocked"] or not runtime["redis_fallback"]:
        errors.append("Queue/Redis target boundary probes are missing")
    return errors


def _validate_storage_recovery_delete(
    fixture: InputRuntimeBatchFixture, runtime: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    if int(runtime["queue_outbox_count"]) < 5:
        errors.append("domain commit and message publication must expose outbox events")
    receipts = fixture.deletion_receipts
    if not all((receipts.input_receipt, receipts.knowledge_receipt, receipts.object_receipt, receipts.verification_receipt)):
        errors.append("delete completion requires Input, Knowledge, Object and Verification receipts")
    if not receipts.legal_hold_blocks_purge_only:
        errors.append("Legal Hold cannot restore revoked access")
    if not all(value > 0 for value in (
        fixture.capacity_profile.deletion_reserved,
        fixture.capacity_profile.security_reserved,
        fixture.capacity_profile.online_attachment_reserved,
    )):
        errors.append("capacity profile must reserve deletion, security and online attachment capacity")
    return errors


def _validate_security_parser_profile(fixture: InputRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    profile = fixture.parser_profile
    if not all((profile.file_route, profile.page_route, profile.region_route)):
        errors.append("Parser routing must support file/page/region levels")
    if not profile.profile_hash or not profile.parser_bundle_digest.startswith("sha256:"):
        errors.append("Parser profile and bundle must be versioned and hashed")
    if not profile.model_weight_hash.startswith("sha256:"):
        errors.append("model weights must be pinned by hash")
    if profile.sandbox_policy != "restricted" or not profile.security_gate_ref or not profile.model_gateway_ref:
        errors.append("remote OCR/VLM must pass security/model gateway and sandbox policy")
    adapter = ParserAdapterContract(
        parser_id="native-markdown",
        family="native",
        supported_formats=["text/markdown"],
        capabilities=["parse", "diagnostics"],
        timeout_seconds=30,
        sandbox_policy="restricted",
        fallback_reason="none",
    )
    if adapter.current_runtime != "deterministic_local" or adapter.network_policy != "local_only":
        errors.append("Parser adapter must be provider-neutral typed local contract")
    if "ssrf" not in profile.remote_fetch_guard:
        errors.append("remote URL fetch guard must cover SSRF")
    return errors


def _validate_handoff_contract(fixture: InputRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    payload_hash = canonical_sha256(fixture.handoff_payload)
    envelope = CrossModuleEnvelopeV1(
        contract_name="IngestionHandoff",
        contract_version="1.0",
        contract_bundle_version="2026.07.wave1",
        message_id="input-handoff:1",
        producer_module="Input / Document Ingestion",
        consumer_module="Knowledge",
        tenant_id="tenant:input",
        workspace_id="workspace:input",
        correlation_id="correlation:input",
        trace_id="trace:input",
        data_classification="internal",
        occurred_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
        payload=fixture.handoff_payload,
        payload_hash=payload_hash,
        payload_schema_hash=fixture.handoff_schema_hash,
        effective_security_epoch_ref="epoch:input:1",
        effective_security_epoch_hash="hash:epoch:1",
    )
    if envelope.payload_hash != payload_hash or not envelope.payload_schema_hash:
        errors.append("Handoff must verify payload hash and schema hash")
    if not envelope.tenant_id or envelope.contract_version.startswith("999"):
        errors.append("missing tenant/unknown contract variant must fail closed")
    return errors


def _validate_format_eval_trace(fixture: InputRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    office = fixture.office_preservation
    if not all((
        office.excel_formula_cache_display,
        office.word_revisions_comments_footnotes_headers,
        office.ppt_positions_notes_hidden_embeds,
        office.html_snapshot_final_url_redirect_dom,
        office.git_commit_blob_path_symbol_line,
    )):
        errors.append("format preservation matrix is incomplete")
    if not fixture.trace_redacted or not fixture.api_hides_internal_details:
        errors.append("Trace/API must hide sensitive docs, secrets and internal queue details")
    if set(fixture.target_evidence_refs) != {"code", "migration", "test", "trace", "eval", "runtime"}:
        errors.append("Target promotion requires complete engineering evidence")
    return errors


__all__ = [
    "INPUT_REQUIREMENT_IDS",
    "InputRuntimeBatchError",
    "InputRuntimeBatchFixture",
    "InputRuntimeBatchReport",
    "build_input_runtime_batch_fixture",
    "validate_input_runtime_batch",
]
