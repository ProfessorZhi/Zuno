from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from zuno.platform.database.product import ProductCommandSubmission, ProductUnitOfWork


PRODUCT_DEFAULT_SECURITY_EPOCH_REF = "security-epoch:product:default"


@dataclass(frozen=True, slots=True)
class ProductAvailableActionResult:
    action: str
    action_token_id: str
    target_ref: str
    expires_at: str


@dataclass(frozen=True, slots=True)
class ProductProjectionResult:
    projection_event_id: str
    stream_cursor_id: str
    stream_sequence_no: int
    freshness: str


@dataclass(frozen=True, slots=True)
class ProductRuntimeRequestResult:
    command_id: str
    receipt_id: str
    status: str
    projection: ProductProjectionResult
    available_actions: tuple[ProductAvailableActionResult, ...]


@dataclass(frozen=True, slots=True)
class ProductStreamEventResult:
    event_id: str
    event_type: str
    sequence_no: int
    redaction_decision_ref: str
    resync_required: bool


class ProductService:
    @staticmethod
    def submit_runtime_request(
        *,
        tenant_id: str,
        workspace_id: str,
        conversation_id: str,
        principal_id: str,
        active_agent_version_id: str,
        client_request_id: str,
        runtime_request_ref: str,
        raw_intent_ref: str,
        command_kind: str,
        payload: dict[str, Any],
    ) -> ProductRuntimeRequestResult:
        submission = ProductCommandSubmission(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            principal_id=principal_id,
            active_agent_version_id=active_agent_version_id,
            submission_id=f"submission:{client_request_id}",
            client_request_id=client_request_id,
            raw_intent_ref=raw_intent_ref,
            command_id=f"command:{client_request_id}",
            command_kind=command_kind,
            owner_module="Agent Core",
            runtime_request_ref=runtime_request_ref,
            payload=payload,
            journal_sequence_no=1,
            outbox_message_id=f"outbox:{client_request_id}",
        )
        from zuno.database import engine

        with ProductUnitOfWork(engine) as repo:
            receipt = repo.submit_command(submission)
            now = datetime.now(timezone.utc)
            source_watermark = repo.next_projection_watermark(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
            projection = repo.record_projection_event(
                projection_event_id=f"projection:{receipt.command_id}:accepted",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                source_module="Product Surface",
                source_event_id=receipt.command_id,
                source_watermark=source_watermark,
                projection_payload={
                    "conversation_id": conversation_id,
                    "command_id": receipt.command_id,
                    "receipt_id": receipt.receipt_id,
                    "status": receipt.status,
                    "runtime_request_ref": runtime_request_ref,
                },
                redaction_decision_ref=f"redaction:{receipt.command_id}:server",
            )
            action = repo.issue_action_token(
                action_token_id=f"action-token:{receipt.command_id}:cancel",
                tenant_id=tenant_id,
                principal_id=principal_id,
                target_ref=runtime_request_ref,
                command_kind="CANCEL_RUNTIME_REQUEST",
                effective_security_epoch_ref=PRODUCT_DEFAULT_SECURITY_EPOCH_REF,
                nonce=f"nonce:{receipt.command_id}:cancel",
                expires_at=now + timedelta(minutes=5),
            )
            cursor = repo.open_stream_cursor(
                cursor_id=f"cursor:{receipt.command_id}:{projection.source_watermark}",
                tenant_id=tenant_id,
                principal_id=principal_id,
                projection_event_id=projection.projection_event_id,
                last_sequence_no=projection.source_watermark,
                effective_security_epoch_ref=PRODUCT_DEFAULT_SECURITY_EPOCH_REF,
                expires_at=now + timedelta(minutes=15),
                reauthorized_at=now,
            )
        return ProductRuntimeRequestResult(
            command_id=receipt.command_id,
            receipt_id=receipt.receipt_id,
            status=receipt.status,
            projection=ProductProjectionResult(
                projection_event_id=projection.projection_event_id,
                stream_cursor_id=cursor.cursor_id,
                stream_sequence_no=projection.source_watermark,
                freshness="gap" if projection.gap_detected else "current",
            ),
            available_actions=(
                ProductAvailableActionResult(
                    action="cancel",
                    action_token_id=action.action_token_id,
                    target_ref=action.target_ref,
                    expires_at=action.expires_at.isoformat(),
                ),
            ),
        )

    @staticmethod
    def list_stream_events(
        *,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
        last_event_id: str | None = None,
    ) -> tuple[ProductStreamEventResult, ...]:
        from zuno.database import engine

        with ProductUnitOfWork(engine) as repo:
            events = repo.list_projection_events(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                principal_id=principal_id,
                last_event_id=last_event_id,
            )
        return tuple(
            ProductStreamEventResult(
                event_id=event.projection_event_id,
                event_type="RESYNC_REQUIRED" if event.gap_detected else "DELTA",
                sequence_no=event.source_watermark,
                redaction_decision_ref=event.redaction_decision_ref,
                resync_required=event.gap_detected,
            )
            for event in events
        )


__all__ = [
    "ProductAvailableActionResult",
    "ProductProjectionResult",
    "ProductRuntimeRequestResult",
    "ProductService",
    "ProductStreamEventResult",
]
