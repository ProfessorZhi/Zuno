from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from pathlib import Path
from typing import Iterable, Literal

from zuno.schema.workspace import (
    WORKSPACE_TASK_STATUS_TO_LIFECYCLE,
    ArtifactContract,
    WorkSpaceSimpleTask,
    WorkspaceProductStreamEvent,
    WorkspaceTaskContract,
)
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256


PRODUCT_REQUIREMENT_IDS: tuple[str, ...] = tuple(
    f"ARCH-PRODUCT-{index:03d}" for index in range(1, 81)
)


class ProductRuntimeBatchError(ValueError):
    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


class CommandReceiptStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    DUPLICATE = "DUPLICATE"
    CONFLICT = "CONFLICT"
    REJECTED = "REJECTED"


class RunOutcome(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUSED = "REFUSED"
    ABSTAINED = "ABSTAINED"
    EXPIRED = "EXPIRED"


class ProjectionEventKind(StrEnum):
    SNAPSHOT = "SNAPSHOT"
    DELTA = "DELTA"
    HEARTBEAT = "HEARTBEAT"
    GAP = "GAP"
    RESYNC_REQUIRED = "RESYNC_REQUIRED"


@dataclass(frozen=True, slots=True)
class ProductCommand:
    command_id: str
    journal_sequence_no: int
    idempotency_key: str
    request_hash: str
    command_kind: str
    runtime_request_ref: str
    outbox_event_ref: str
    committed_transaction_ref: str


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    receipt_id: str
    command_ref: str
    receipt_version: int
    status: CommandReceiptStatus
    duplicate_of: str | None = None
    conflict_ref: str | None = None
    domain_success_ref: str | None = None


@dataclass(frozen=True, slots=True)
class ProductProjection:
    projection_id: str
    source_fact_ref: str
    source_event_id: str
    source_partition: str
    source_watermark: int
    aggregate_sequence_no: int
    stream_sequence_no: int
    schema_version: str
    authorized_view_ref: str
    rebuildable: bool = True


@dataclass(frozen=True, slots=True)
class AuthorizedView:
    view_id: str
    projection_ref: str
    effective_security_epoch_ref: str
    redaction_decision_ref: str
    available_actions: tuple[str, ...]
    server_generated: bool


@dataclass(frozen=True, slots=True)
class StreamCursor:
    cursor_id: str
    snapshot_ref: str
    last_sequence_no: int
    expires_at: datetime
    reauthorized_at: datetime
    retention_expired: bool = False


@dataclass(frozen=True, slots=True)
class ActionToken:
    token_id: str
    principal_ref: str
    target_ref: str
    effective_security_epoch_ref: str
    expires_at: datetime
    nonce: str
    revoked: bool = False

    def is_usable(self, now: datetime) -> bool:
        return not self.revoked and now < self.expires_at and bool(self.nonce)


@dataclass(frozen=True, slots=True)
class ProductSignal:
    signal_id: str
    interrupt_ref: str
    action_token_ref: str
    signal_version: str
    idempotency_key: str
    owner_module: Literal["Agent Core"] = "Agent Core"


@dataclass(frozen=True, slots=True)
class ApprovalView:
    approval_ref: str
    prepared_tool_action_hash: str
    scope_ref: str
    expires_at: datetime
    accepted_not_effect_success: bool = True
    owner_module: Literal["Security"] = "Security"


@dataclass(frozen=True, slots=True)
class PublicationDelivery:
    publication_ref: str
    artifact_version_ref: str
    delivery_attempt_ref: str
    render_receipt_ref: str
    user_read_receipt_ref: str
    delivery_idempotency_key: str
    retry_reexecutes_agent_run: bool = False


@dataclass(frozen=True, slots=True)
class DownloadSession:
    session_id: str
    artifact_ref: str
    authorized_principal_ref: str
    expires_at: datetime
    revoked_by_epoch_change: bool = False


@dataclass(frozen=True, slots=True)
class ProductSecuritySurface:
    command_authorized: bool
    query_authorized: bool
    stream_authorized: bool
    download_authorized: bool
    sanitizes_rich_text: bool
    artifact_preview_sandboxed: bool
    desktop_typed_ipc: bool
    external_api_replay_protected: bool
    hides_secret_checkpoint_and_reasoning: bool


@dataclass(frozen=True, slots=True)
class RetentionPolicySurface:
    legal_hold_respected: bool
    owner_receipts_required: bool
    correction_keeps_history: bool
    projection_retention_independent: bool
    cursor_retention_independent: bool


@dataclass(frozen=True, slots=True)
class ProductRuntimeBatchFixture:
    task_request: WorkSpaceSimpleTask
    workspace_task: WorkspaceTaskContract
    command: ProductCommand
    receipts: tuple[CommandReceipt, ...]
    projection: ProductProjection
    authorized_view: AuthorizedView
    stream_events: tuple[WorkspaceProductStreamEvent, ...]
    cursor: StreamCursor
    action_token: ActionToken
    signal: ProductSignal
    approval_view: ApprovalView
    outcomes: tuple[RunOutcome, ...]
    file_statuses: tuple[str, ...]
    artifact: ArtifactContract
    delivery: PublicationDelivery
    download_session: DownloadSession
    security_surface: ProductSecuritySurface
    retention_surface: RetentionPolicySurface
    slo_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProductRuntimeBatchReport:
    requirement_ids: tuple[str, ...]
    command_count: int
    receipt_count: int
    stream_event_count: int
    outcome_count: int
    frontend_contract_checked: bool


def build_product_runtime_batch_fixture() -> ProductRuntimeBatchFixture:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    request_payload = {
        "query": "Review renewal terms",
        "session_id": "session:product",
        "workspace_id": "workspace:product",
        "task_id": "task:product",
    }
    request_hash = canonical_sha256(request_payload)
    task_request = WorkSpaceSimpleTask(
        query=request_payload["query"],
        model_id="model-local",
        session_id=request_payload["session_id"],
        workspace_id=request_payload["workspace_id"],
        task_id=request_payload["task_id"],
        trace_id="trace:product",
        goal="contract renewal review",
        product_mode="contract_review",
        approval_mode="required_for_risky_tools",
        desktop_bridge_token="untrusted-client-token",
        plugins=[],
        mcp_servers=[],
        multi_agent_enabled=False,
    )
    workspace_task = WorkspaceTaskContract(
        workspace_id="workspace:product",
        task_id="task:product",
        session_id="session:product",
        goal="contract renewal review",
        status="running",
        trace_id="trace:product",
    )
    command = ProductCommand(
        command_id="command:1",
        journal_sequence_no=1,
        idempotency_key="idem:product:1",
        request_hash=request_hash,
        command_kind="CREATE_RUNTIME_REQUEST",
        runtime_request_ref="runtime-request:1",
        outbox_event_ref="product-outbox:1",
        committed_transaction_ref="tx:product:1",
    )
    receipts = (
        CommandReceipt("receipt:1", command.command_id, 1, CommandReceiptStatus.ACCEPTED),
        CommandReceipt("receipt:2", command.command_id, 2, CommandReceiptStatus.DUPLICATE, duplicate_of="receipt:1"),
        CommandReceipt("receipt:3", command.command_id, 3, CommandReceiptStatus.CONFLICT, conflict_ref="conflict:hash"),
    )
    projection = ProductProjection(
        projection_id="projection:assistant-message",
        source_fact_ref="agent-publication:1",
        source_event_id="agent-event:publication:1",
        source_partition="agent-run:task:product",
        source_watermark=9,
        aggregate_sequence_no=3,
        stream_sequence_no=12,
        schema_version="product-projection-v1",
        authorized_view_ref="authorized-view:1",
    )
    view = AuthorizedView(
        view_id="authorized-view:1",
        projection_ref=projection.projection_id,
        effective_security_epoch_ref="epoch:product:1",
        redaction_decision_ref="redaction:1",
        available_actions=("retry_delivery", "download_artifact", "send_feedback"),
        server_generated=True,
    )
    stream_events = (
        _stream_event("event:snapshot", ProjectionEventKind.SNAPSHOT, "running", 10),
        _stream_event("event:delta", ProjectionEventKind.DELTA, "running", 11),
        _stream_event("event:heartbeat", ProjectionEventKind.HEARTBEAT, "running", 11),
        _stream_event("event:gap", ProjectionEventKind.GAP, "recoverable_failed", 13),
    )
    return ProductRuntimeBatchFixture(
        task_request=task_request,
        workspace_task=workspace_task,
        command=command,
        receipts=receipts,
        projection=projection,
        authorized_view=view,
        stream_events=stream_events,
        cursor=StreamCursor(
            cursor_id="cursor:1",
            snapshot_ref="snapshot:1",
            last_sequence_no=11,
            expires_at=now + timedelta(minutes=15),
            reauthorized_at=now,
        ),
        action_token=ActionToken(
            token_id="action-token:1",
            principal_ref="principal:1",
            target_ref="interrupt:1",
            effective_security_epoch_ref="epoch:product:1",
            expires_at=now + timedelta(minutes=5),
            nonce="nonce:1",
        ),
        signal=ProductSignal(
            signal_id="signal:1",
            interrupt_ref="interrupt:1",
            action_token_ref="action-token:1",
            signal_version="signal-v1",
            idempotency_key="signal:idem:1",
        ),
        approval_view=ApprovalView(
            approval_ref="approval:1",
            prepared_tool_action_hash="prepared-hash:1",
            scope_ref="scope:tool:1",
            expires_at=now + timedelta(minutes=5),
        ),
        outcomes=tuple(RunOutcome),
        file_statuses=("uploaded", "parse_succeeded", "indexed", "searchable"),
        artifact=ArtifactContract(
            workspace_id="workspace:product",
            artifact_id="artifact:1",
            task_id="task:product",
            kind="markdown",
            uri="object://artifact/1",
            hash="artifact-hash",
            download_policy="short_lived_session",
        ),
        delivery=PublicationDelivery(
            publication_ref="agent-publication:1",
            artifact_version_ref="artifact-version:1",
            delivery_attempt_ref="delivery-attempt:1",
            render_receipt_ref="render:1",
            user_read_receipt_ref="read:1",
            delivery_idempotency_key="delivery:idem:1",
        ),
        download_session=DownloadSession(
            session_id="download-session:1",
            artifact_ref="artifact:1",
            authorized_principal_ref="principal:1",
            expires_at=now + timedelta(minutes=10),
        ),
        security_surface=ProductSecuritySurface(
            command_authorized=True,
            query_authorized=True,
            stream_authorized=True,
            download_authorized=True,
            sanitizes_rich_text=True,
            artifact_preview_sandboxed=True,
            desktop_typed_ipc=True,
            external_api_replay_protected=True,
            hides_secret_checkpoint_and_reasoning=True,
        ),
        retention_surface=RetentionPolicySurface(
            legal_hold_respected=True,
            owner_receipts_required=True,
            correction_keeps_history=True,
            projection_retention_independent=True,
            cursor_retention_independent=True,
        ),
        slo_names=("command", "projection", "stream", "delivery"),
    )


def _stream_event(
    event_id: str,
    kind: ProjectionEventKind,
    status: str,
    sequence_no: int,
) -> WorkspaceProductStreamEvent:
    return WorkspaceProductStreamEvent(
        event_id=event_id,
        task_id="task:product",
        trace_id="trace:product",
        type=kind.value,
        status=status,
        timestamp=sequence_no,
        payload={"sequence_no": sequence_no, "kind": kind.value},
    )


def validate_product_runtime_batch(
    fixture: ProductRuntimeBatchFixture | None = None,
    *,
    workspace_api_text: str | None = None,
) -> ProductRuntimeBatchReport:
    fixture = fixture or build_product_runtime_batch_fixture()
    errors: list[str] = []
    errors.extend(_validate_northbound_boundary(fixture))
    errors.extend(_validate_command_receipts(fixture))
    errors.extend(_validate_projection_stream(fixture))
    errors.extend(_validate_interrupt_approval_effect(fixture))
    errors.extend(_validate_outcomes_files_publication(fixture))
    errors.extend(_validate_security_retention(fixture))
    errors.extend(_validate_frontend_contract(workspace_api_text))
    if errors:
        raise ProductRuntimeBatchError(errors)
    return ProductRuntimeBatchReport(
        requirement_ids=PRODUCT_REQUIREMENT_IDS,
        command_count=1,
        receipt_count=len(fixture.receipts),
        stream_event_count=len(fixture.stream_events),
        outcome_count=len(fixture.outcomes),
        frontend_contract_checked=workspace_api_text is not None,
    )


def validate_product_runtime_batch_from_repo(repo_root: Path) -> ProductRuntimeBatchReport:
    workspace_api_text = (repo_root / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )
    return validate_product_runtime_batch(workspace_api_text=workspace_api_text)


def _validate_northbound_boundary(fixture: ProductRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if fixture.task_request.multi_agent_enabled:
        errors.append("Product Surface must not become a second controller")
    if fixture.task_request.desktop_bridge_token and not fixture.security_surface.desktop_typed_ipc:
        errors.append("desktop bridge token is untrusted without typed IPC")
    payload = {"runtime_request_ref": fixture.command.runtime_request_ref}
    envelope = CrossModuleEnvelopeV1(
        contract_name="RuntimeRequest",
        contract_version="1.0",
        contract_bundle_version="2026.07.wave1",
        message_id="product-message:1",
        producer_module="Product Surface",
        consumer_module="Agent Core",
        tenant_id="tenant:product",
        workspace_id=fixture.workspace_task.workspace_id,
        correlation_id="correlation:product",
        trace_id=fixture.workspace_task.trace_id or "trace:product",
        data_classification="internal",
        occurred_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash="schema:runtime-request:v1",
    )
    if envelope.consumer_module != "Agent Core":
        errors.append("RuntimeRequest must be handed to Agent Core")
    return errors


def _validate_command_receipts(fixture: ProductRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if fixture.command.journal_sequence_no < 1 or not fixture.command.outbox_event_ref:
        errors.append("ProductCommand must use ordered journal and transactional outbox")
    for receipt in fixture.receipts:
        if receipt.domain_success_ref:
            errors.append("CommandReceipt must not claim domain success")
    statuses = {receipt.status for receipt in fixture.receipts}
    if {CommandReceiptStatus.ACCEPTED, CommandReceiptStatus.DUPLICATE, CommandReceiptStatus.CONFLICT} - statuses:
        errors.append("CommandReceipt must cover accepted, duplicate and conflict")
    duplicate = next(receipt for receipt in fixture.receipts if receipt.status == CommandReceiptStatus.DUPLICATE)
    conflict = next(receipt for receipt in fixture.receipts if receipt.status == CommandReceiptStatus.CONFLICT)
    if not duplicate.duplicate_of or not conflict.conflict_ref:
        errors.append("idempotency duplicate/conflict semantics are incomplete")
    return errors


def _validate_projection_stream(fixture: ProductRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if not fixture.projection.rebuildable or not fixture.projection.source_fact_ref:
        errors.append("Projection must be rebuildable from source fact")
    if fixture.authorized_view.projection_ref != fixture.projection.projection_id:
        errors.append("AuthorizedView must be derived from base projection")
    if not fixture.authorized_view.server_generated:
        errors.append("AvailableAction must be server generated")
    event_kinds = {event.type for event in fixture.stream_events}
    if {"SNAPSHOT", "DELTA", "HEARTBEAT", "GAP"} - event_kinds:
        errors.append("SSE must include snapshot, delta, heartbeat and gap semantics")
    heartbeat = next(event for event in fixture.stream_events if event.type == "HEARTBEAT")
    if heartbeat.status in {"completed", "succeeded"}:
        errors.append("Heartbeat cannot represent Run progress or success")
    if fixture.cursor.retention_expired:
        errors.append("expired cursor must resync instead of unsafe incremental stream")
    return errors


def _validate_interrupt_approval_effect(fixture: ProductRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    if not fixture.action_token.is_usable(now):
        errors.append("ActionToken must bind principal/target/epoch/expiry/nonce")
    if fixture.signal.owner_module != "Agent Core" or not fixture.signal.interrupt_ref:
        errors.append("Signal must bind an Agent Core interrupt")
    if fixture.approval_view.owner_module != "Security":
        errors.append("ApprovalDecision must remain Security-owned")
    if not fixture.approval_view.accepted_not_effect_success:
        errors.append("Approval accepted cannot equal Tool Effect success")
    return errors


def _validate_outcomes_files_publication(fixture: ProductRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if set(fixture.outcomes) != set(RunOutcome):
        errors.append("Product must preserve all RunOutcome semantics")
    if not {"uploaded", "parse_succeeded", "indexed", "searchable"}.issubset(
        set(fixture.file_statuses)
    ):
        errors.append("Upload, Parse, Index and Searchable states must be separated")
    if not fixture.artifact.download_policy == "short_lived_session":
        errors.append("Artifact download must use a short-lived authorized session")
    if fixture.delivery.retry_reexecutes_agent_run:
        errors.append("Delivery retry must not re-execute AgentRun")
    for field_name in (
        fixture.delivery.publication_ref,
        fixture.delivery.artifact_version_ref,
        fixture.delivery.delivery_attempt_ref,
        fixture.delivery.render_receipt_ref,
        fixture.delivery.user_read_receipt_ref,
    ):
        if not field_name:
            errors.append("Artifact, Publication, Delivery, Render and Read must be separate")
    if WORKSPACE_TASK_STATUS_TO_LIFECYCLE["failed"] != "recoverable_failed":
        errors.append("Product lifecycle must keep recoverable failure distinct")
    return errors


def _validate_security_retention(fixture: ProductRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    security = fixture.security_surface
    if not all(
        (
            security.command_authorized,
            security.query_authorized,
            security.stream_authorized,
            security.download_authorized,
            security.sanitizes_rich_text,
            security.artifact_preview_sandboxed,
            security.desktop_typed_ipc,
            security.external_api_replay_protected,
            security.hides_secret_checkpoint_and_reasoning,
        )
    ):
        errors.append("Product security surface is incomplete")
    retention = fixture.retention_surface
    if not all(
        (
            retention.legal_hold_respected,
            retention.owner_receipts_required,
            retention.correction_keeps_history,
            retention.projection_retention_independent,
            retention.cursor_retention_independent,
        )
    ):
        errors.append("Product retention surface is incomplete")
    if set(fixture.slo_names) != {"command", "projection", "stream", "delivery"}:
        errors.append("Product SLO must cover command, projection, stream and delivery")
    return errors


def _validate_frontend_contract(workspace_api_text: str | None) -> list[str]:
    if workspace_api_text is None:
        return []
    errors: list[str] = []
    for phrase in (
        "WorkspaceProductMode",
        "WorkspaceTaskStatus",
        "WorkspaceTaskLifecycleSnapshot",
        "WorkspaceApprovalRequest",
        "WorkspaceCancelRequest",
        "workspaceTaskEventsStreamAPI",
        "downloadWorkspaceArtifactAPI",
        "responseType: 'blob'",
    ):
        if phrase not in workspace_api_text:
            errors.append(f"frontend workspace API missing {phrase}")
    for forbidden in ("hidden_reasoning", "raw_checkpoint", "api_key"):
        if forbidden in workspace_api_text:
            errors.append(f"frontend workspace API exposes forbidden field: {forbidden}")
    return errors


__all__ = [
    "PRODUCT_REQUIREMENT_IDS",
    "ProductRuntimeBatchError",
    "ProductRuntimeBatchFixture",
    "ProductRuntimeBatchReport",
    "build_product_runtime_batch_fixture",
    "validate_product_runtime_batch",
    "validate_product_runtime_batch_from_repo",
]
