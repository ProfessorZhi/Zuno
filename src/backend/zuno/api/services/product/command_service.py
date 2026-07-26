from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from zuno.agent.domain import AgentRun, GoalInputClassification, GoalVersion, TaskContract
from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.agent import AgentDomainRepository
from zuno.platform.database.foundation import InfrastructureRepository
from zuno.platform.database.product import ProductCommandSubmission, ProductRepository, ProductUnitOfWork


PRODUCT_DEFAULT_SECURITY_EPOCH_REF = "security-epoch:product:default"
PRODUCT_RUNTIME_DISPATCH_TOPIC = "product.runtime_request.dispatch"
PRODUCT_RUNTIME_DISPATCH_CONSUMER = "agent-core-product-runtime-dispatch"


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
class ProductRuntimeDispatchConsumeResult:
    event_id: str
    command_id: str
    agent_run_id: str | None
    agent_run_status: str
    owner_receipt_ref: str | None
    inbox_first_seen: bool
    outbox_status: str


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
    def consume_runtime_request_dispatch(
        *,
        event_id: str,
        worker_id: str,
        engine: Any | None = None,
    ) -> ProductRuntimeDispatchConsumeResult:
        if engine is None:
            from zuno.database import engine as default_engine

            engine = default_engine

        with engine.begin() as conn:
            infra_repo = InfrastructureRepository(conn)
            if not infra_repo.claim_outbox_event(event_id=event_id, worker_id=worker_id):
                return ProductRuntimeDispatchConsumeResult(
                    event_id=event_id,
                    command_id="",
                    agent_run_id=None,
                    agent_run_status="not_pending",
                    owner_receipt_ref=None,
                    inbox_first_seen=False,
                    outbox_status="not_claimed",
                )
            record = infra_repo.load_claimed_outbox_event(event_id=event_id, worker_id=worker_id)
            payload = dict(record.payload)
            if record.topic != PRODUCT_RUNTIME_DISPATCH_TOPIC or payload.get("consumer_module") != "Agent Core":
                raise ValueError("outbox event is not a Product RuntimeRequest dispatch for Agent Core")
            tenant_id = str(payload["tenant_id"])
            workspace_id = str(payload["workspace_id"])
            principal_id = str(payload["principal_id"])
            command_id = str(payload["command_id"])
            runtime_request_ref = str(payload["runtime_request_ref"])
            receipt = infra_repo.record_inbox_receipt(
                consumer=PRODUCT_RUNTIME_DISPATCH_CONSUMER,
                message_id=record.event_id,
                payload=payload,
                tenant_id=tenant_id,
                ordering_key=record.ordering_key,
                ordering_sequence=record.ordering_sequence,
            )
            agent_run_id = f"agent-run:{runtime_request_ref}"
            owner_receipt_ref: str | None = None
            agent_run_status = "duplicate"
            if receipt.first_seen:
                agent_repo = AgentDomainRepository(conn)
                now = datetime.now(timezone.utc)
                task_contract_id = f"task-contract:{runtime_request_ref}"
                goal_version_id = f"goal:{runtime_request_ref}"
                agent_repo.record_goal_version(
                    GoalVersion(
                        goal_version_id=goal_version_id,
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        principal_id=principal_id,
                        goal_sequence=int(record.ordering_sequence or 1),
                        input_classification=GoalInputClassification.NEW_TASK,
                        objective_hash=str(payload["payload_hash"]),
                        output_contract_ref=f"output-contract:{runtime_request_ref}",
                        constraints_hash=canonical_sha256(
                            {
                                "active_agent_version_id": payload.get("active_agent_version_id"),
                                "command_id": command_id,
                            }
                        ),
                    )
                )
                agent_repo.record_task_contract(
                    TaskContract(
                        task_contract_id=task_contract_id,
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        principal_id=principal_id,
                        goal_version_id=goal_version_id,
                        idempotency_key=record.idempotency_key,
                        security_context_ref=f"security-context:{runtime_request_ref}",
                        security_epoch_ref=PRODUCT_DEFAULT_SECURITY_EPOCH_REF,
                        deadline_at=now + timedelta(hours=1),
                        budget_ref=f"budget:{runtime_request_ref}",
                    )
                )
                run_receipt = agent_repo.record_agent_run(
                    AgentRun(
                        run_id=agent_run_id,
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        principal_id=principal_id,
                        task_contract_id=task_contract_id,
                        trace_id=f"trace:{runtime_request_ref}",
                    )
                )
                owner_receipt_ref = f"owner-receipt:{record.event_id}:agent-run-created"
                ProductRepository(conn).append_owner_receipt(
                    tenant_id=tenant_id,
                    command_id=command_id,
                    status="ACCEPTED",
                    owner_receipt_ref=owner_receipt_ref,
                    payload={
                        "runtime_request_ref": runtime_request_ref,
                        "agent_run_ref": run_receipt.ref,
                        "task_contract_ref": task_contract_id,
                        "outbox_event_id": record.event_id,
                    },
                )
                infra_repo.mark_inbox_processed(
                    tenant_id=tenant_id,
                    consumer=PRODUCT_RUNTIME_DISPATCH_CONSUMER,
                    message_id=record.event_id,
                )
                agent_run_status = run_receipt.status
            infra_repo.complete_outbox(event_id=record.event_id, worker_id=worker_id)
        return ProductRuntimeDispatchConsumeResult(
            event_id=event_id,
            command_id=command_id,
            agent_run_id=agent_run_id,
            agent_run_status=agent_run_status,
            owner_receipt_ref=owner_receipt_ref,
            inbox_first_seen=receipt.first_seen,
            outbox_status="published",
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
    "ProductRuntimeDispatchConsumeResult",
    "ProductRuntimeRequestResult",
    "ProductService",
    "ProductStreamEventResult",
]
