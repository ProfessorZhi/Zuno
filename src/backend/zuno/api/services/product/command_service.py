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
PRODUCT_PROJECTION_REBUILD_TOPIC = "product.projection.rebuild.requested"
PRODUCT_PROJECTION_REBUILD_CONSUMER = "product-projection-rebuild-worker"


@dataclass(frozen=True, slots=True)
class ProductAvailableActionResult:
    action: str
    action_token_id: str
    target_ref: str
    effective_security_epoch_ref: str
    projection_version: int
    expires_at: str


@dataclass(frozen=True, slots=True)
class ProductActionConsumeResult:
    action_token_id: str
    command_id: str
    receipt_id: str
    status: str
    target_ref: str
    used_at: str


@dataclass(frozen=True, slots=True)
class ProductProjectionResult:
    projection_event_id: str
    stream_cursor_id: str
    stream_sequence_no: int
    freshness: str
    redaction_decision_ref: str


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
class ProductProjectionRebuildConsumeResult:
    event_id: str
    rebuild_id: str
    projection_event_id: str | None
    projection_status: str
    inbox_first_seen: bool
    outbox_status: str


@dataclass(frozen=True, slots=True)
class ProductStreamEventResult:
    event_id: str
    event_type: str
    sequence_no: int
    redaction_decision_ref: str
    resync_required: bool


@dataclass(frozen=True, slots=True)
class ProductAgentDefinitionResult:
    agent_definition_id: str
    tenant_id: str
    workspace_id: str
    owner_principal_ref: str
    display_name: str
    description: str
    status: str


@dataclass(frozen=True, slots=True)
class ProductAgentDraftResult:
    agent_draft_id: str
    agent_definition_id: str
    draft_version: int
    editor_principal_ref: str
    configuration_hash: str
    status: str


@dataclass(frozen=True, slots=True)
class ProductAgentPublicationResult:
    publication_id: str
    agent_version_id: str
    scope: str
    status: str


@dataclass(frozen=True, slots=True)
class ProductAgentInstallationResult:
    installation_id: str
    agent_version_id: str
    workspace_id: str
    principal_ref: str
    status: str


@dataclass(frozen=True, slots=True)
class ProductAgentCatalogEntryResult:
    catalog_entry_id: str
    agent_version_id: str
    authorized: bool
    visibility_scope: str
    effective_permission_preview_ref: str


class ProductService:
    @staticmethod
    def runtime_agent_version_id(*, surface: str, tenant_id: str, workspace_id: str) -> str:
        version_hash = canonical_sha256(
            {
                "surface": surface,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
            }
        )[:24]
        return f"agent-version:runtime:{surface}:{version_hash}"

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
        bootstrap_runtime_agent: bool = False,
        runtime_surface: str = "product",
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
            if bootstrap_runtime_agent:
                repo.ensure_runtime_agent_version(
                    agent_version_id=active_agent_version_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    owner_principal_id=principal_id,
                    display_name=f"{runtime_surface} unified runtime {active_agent_version_id[-8:]}",
                    primary_agent_core_profile_ref=f"agent-core-profile:{runtime_surface}:unified-runtime",
                )
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
                redaction_decision_ref=projection.redaction_decision_ref,
            ),
            available_actions=(
                ProductAvailableActionResult(
                    action="CANCEL",
                    action_token_id=action.action_token_id,
                    target_ref=action.target_ref,
                    effective_security_epoch_ref=action.effective_security_epoch_ref,
                    projection_version=projection.source_watermark,
                    expires_at=action.expires_at.isoformat(),
                ),
            ),
        )

    @staticmethod
    def consume_action_token(
        *,
        tenant_id: str,
        principal_id: str,
        action_token_id: str,
        client_request_id: str,
        raw_intent_ref: str,
        payload: dict[str, Any],
    ) -> ProductActionConsumeResult:
        from zuno.database import engine

        with ProductUnitOfWork(engine) as repo:
            consumed = repo.consume_action_token_as_command(
                action_token_id=action_token_id,
                tenant_id=tenant_id,
                principal_id=principal_id,
                client_request_id=client_request_id,
                raw_intent_ref=raw_intent_ref,
                payload=payload,
            )
        return ProductActionConsumeResult(
            action_token_id=consumed.action_token_id,
            command_id=consumed.command_id,
            receipt_id=consumed.receipt_id,
            status=consumed.status,
            target_ref=consumed.target_ref,
            used_at=consumed.used_at.isoformat(),
        )

    @staticmethod
    def create_agent_draft(
        *,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
        client_request_id: str,
        display_name: str,
        description: str,
        primary_agent_core_profile_ref: str,
        configuration: dict[str, Any],
    ) -> tuple[ProductAgentDefinitionResult, ProductAgentDraftResult]:
        from zuno.database import engine

        agent_definition_id = f"agent-definition:{client_request_id}"
        draft_id = f"agent-draft:{client_request_id}"
        draft_payload = {
            "display_name": display_name,
            "description": description,
            "primary_agent_core_profile_ref": primary_agent_core_profile_ref,
            "configuration": configuration,
        }
        with ProductUnitOfWork(engine) as repo:
            definition = repo.create_agent_definition(
                agent_definition_id=agent_definition_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                owner_principal_id=principal_id,
                display_name=display_name,
            )
            draft = repo.create_agent_draft(
                draft_id=draft_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                agent_definition_id=agent_definition_id,
                draft_payload=draft_payload,
            )
        return (
            ProductAgentDefinitionResult(
                agent_definition_id=definition.ref_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                owner_principal_ref=f"principal:{principal_id}",
                display_name=display_name,
                description=description,
                status=definition.status,
            ),
            ProductAgentDraftResult(
                agent_draft_id=draft.ref_id,
                agent_definition_id=agent_definition_id,
                draft_version=1,
                editor_principal_ref=f"principal:{principal_id}",
                configuration_hash=canonical_sha256(draft_payload),
                status=draft.status,
            ),
        )

    @staticmethod
    def publish_agent_version(
        *,
        tenant_id: str,
        workspace_id: str,
        client_request_id: str,
        agent_definition_id: str,
        agent_version_id: str,
        publication_scope: str,
        primary_agent_core_profile_ref: str,
        configuration: dict[str, Any],
    ) -> tuple[ProductAgentPublicationResult, ProductAgentCatalogEntryResult]:
        from zuno.database import engine

        publication_id = f"agent-publication:{client_request_id}"
        catalog_entry_id = f"agent-catalog:{tenant_id}:{workspace_id}:{agent_definition_id}"
        with ProductUnitOfWork(engine) as repo:
            repo.create_agent_version(
                agent_version_id=agent_version_id,
                tenant_id=tenant_id,
                agent_definition_id=agent_definition_id,
                version_no=1,
                configuration_payload=configuration,
                primary_agent_core_profile_ref=primary_agent_core_profile_ref,
                status="PUBLISHED",
            )
            publication = repo.publish_agent_version(
                publication_id=publication_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                agent_version_id=agent_version_id,
                publication_scope=publication_scope,
                publication_payload={
                    "publication_scope": publication_scope,
                    "agent_definition_id": agent_definition_id,
                    "agent_version_id": agent_version_id,
                    "configuration_hash": canonical_sha256(configuration),
                },
            )
            catalog = repo.upsert_catalog_entry(
                catalog_entry_id=catalog_entry_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                agent_definition_id=agent_definition_id,
                latest_version_id=agent_version_id,
                visibility_scope=publication_scope,
            )
        return (
            ProductAgentPublicationResult(
                publication_id=publication.ref_id,
                agent_version_id=agent_version_id,
                scope=publication_scope,
                status=publication.status,
            ),
            ProductAgentCatalogEntryResult(
                catalog_entry_id=catalog.ref_id,
                agent_version_id=agent_version_id,
                authorized=True,
                visibility_scope=publication_scope,
                effective_permission_preview_ref=f"permission-preview:{catalog.ref_id}",
            ),
        )

    @staticmethod
    def install_agent_version(
        *,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
        client_request_id: str,
        agent_version_id: str,
        installation_scope: str,
    ) -> ProductAgentInstallationResult:
        from zuno.database import engine

        installation_id = f"agent-installation:{client_request_id}"
        with ProductUnitOfWork(engine) as repo:
            installation = repo.install_agent_version(
                installation_id=installation_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                agent_version_id=agent_version_id,
                principal_id=principal_id,
                installation_scope=installation_scope,
                status="INSTALLED",
            )
        return ProductAgentInstallationResult(
            installation_id=installation.ref_id,
            agent_version_id=agent_version_id,
            workspace_id=workspace_id,
            principal_ref=f"principal:{principal_id}",
            status=installation.status,
        )

    @staticmethod
    def revoke_agent_installation(
        *,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
        installation_id: str,
    ) -> ProductAgentInstallationResult:
        from zuno.database import engine

        with ProductUnitOfWork(engine) as repo:
            revoked = repo.revoke_agent_installation(
                installation_id=installation_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                principal_id=principal_id,
            )
        return ProductAgentInstallationResult(
            installation_id=revoked.ref_id,
            agent_version_id="",
            workspace_id=workspace_id,
            principal_ref=f"principal:{principal_id}",
            status=revoked.status,
        )

    @staticmethod
    def revoke_agent_publication(
        *,
        tenant_id: str,
        workspace_id: str,
        publication_id: str,
    ) -> ProductAgentPublicationResult:
        from zuno.database import engine

        with ProductUnitOfWork(engine) as repo:
            revoked = repo.revoke_agent_publication(
                publication_id=publication_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            )
        return ProductAgentPublicationResult(
            publication_id=revoked.ref_id,
            agent_version_id="",
            scope="",
            status=revoked.status,
        )

    @staticmethod
    def list_agent_catalog(
        *,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
    ) -> tuple[ProductAgentCatalogEntryResult, ...]:
        _ = principal_id
        from zuno.database import engine

        with ProductUnitOfWork(engine) as repo:
            entries = repo.list_catalog_entries(tenant_id=tenant_id, workspace_id=workspace_id)
        return tuple(
            ProductAgentCatalogEntryResult(
                catalog_entry_id=entry.catalog_entry_id,
                agent_version_id=entry.latest_version_id,
                authorized=True,
                visibility_scope=entry.visibility_scope,
                effective_permission_preview_ref=f"permission-preview:{entry.catalog_entry_id}",
            )
            for entry in entries
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
            agent_run_id = f"agent-run:{runtime_request_ref}"
            owner_receipt_ref: str | None = None
            agent_run_status = "duplicate"
            inbox_first_seen = False
            try:
                owner_tx = conn.begin_nested()
                try:
                    receipt = infra_repo.record_inbox_receipt(
                        consumer=PRODUCT_RUNTIME_DISPATCH_CONSUMER,
                        message_id=record.event_id,
                        payload=payload,
                        tenant_id=tenant_id,
                        ordering_key=record.ordering_key,
                        ordering_sequence=record.ordering_sequence,
                    )
                    inbox_first_seen = receipt.first_seen
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
                    owner_tx.commit()
                except Exception:
                    owner_tx.rollback()
                    raise
            except Exception as exc:
                failure = infra_repo.record_outbox_publish_failure(
                    event_id=record.event_id,
                    worker_id=worker_id,
                    error_code=f"AgentCoreOwnerUnavailable:{type(exc).__name__}",
                    max_attempts=3,
                    base_backoff_seconds=0,
                    max_backoff_seconds=0,
                )
                return ProductRuntimeDispatchConsumeResult(
                    event_id=event_id,
                    command_id=command_id,
                    agent_run_id=agent_run_id,
                    agent_run_status="owner_unavailable",
                    owner_receipt_ref=None,
                    inbox_first_seen=False,
                    outbox_status=failure.status,
                )
            infra_repo.complete_outbox(event_id=record.event_id, worker_id=worker_id)
        return ProductRuntimeDispatchConsumeResult(
            event_id=event_id,
            command_id=command_id,
            agent_run_id=agent_run_id,
            agent_run_status=agent_run_status,
            owner_receipt_ref=owner_receipt_ref,
            inbox_first_seen=inbox_first_seen,
            outbox_status="published",
        )

    @staticmethod
    def consume_projection_rebuild_request(
        *,
        event_id: str,
        worker_id: str,
        engine: Any | None = None,
    ) -> ProductProjectionRebuildConsumeResult:
        if engine is None:
            from zuno.database import engine as default_engine

            engine = default_engine

        with engine.begin() as conn:
            infra_repo = InfrastructureRepository(conn)
            if not infra_repo.claim_outbox_event(event_id=event_id, worker_id=worker_id):
                return ProductProjectionRebuildConsumeResult(
                    event_id=event_id,
                    rebuild_id="",
                    projection_event_id=None,
                    projection_status="not_pending",
                    inbox_first_seen=False,
                    outbox_status="not_claimed",
                )
            record = infra_repo.load_claimed_outbox_event(event_id=event_id, worker_id=worker_id)
            payload = dict(record.payload)
            if (
                record.topic != PRODUCT_PROJECTION_REBUILD_TOPIC
                or payload.get("consumer_module") != "Product Surface"
            ):
                raise ValueError("outbox event is not a Product projection rebuild request")
            tenant_id = str(payload["tenant_id"])
            workspace_id = str(payload["workspace_id"])
            rebuild_id = str(payload["rebuild_id"])
            reason = str(payload.get("reason") or "owner_projection_rebuild")
            receipt = infra_repo.record_inbox_receipt(
                consumer=PRODUCT_PROJECTION_REBUILD_CONSUMER,
                message_id=record.event_id,
                payload=payload,
                tenant_id=tenant_id,
                ordering_key=record.ordering_key,
                ordering_sequence=record.ordering_sequence,
            )
            projection_event_id: str | None = None
            projection_status = "duplicate"
            if receipt.first_seen:
                rebuild = ProductRepository(conn).record_projection_rebuild(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    rebuild_id=rebuild_id,
                    reason=reason,
                )
                projection_event_id = rebuild.projection_event_id
                projection_status = "duplicate" if rebuild.duplicate else "recorded"
                infra_repo.mark_inbox_processed(
                    tenant_id=tenant_id,
                    consumer=PRODUCT_PROJECTION_REBUILD_CONSUMER,
                    message_id=record.event_id,
                )
            infra_repo.complete_outbox(event_id=record.event_id, worker_id=worker_id)
        return ProductProjectionRebuildConsumeResult(
            event_id=event_id,
            rebuild_id=rebuild_id,
            projection_event_id=projection_event_id,
            projection_status=projection_status,
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
    "ProductActionConsumeResult",
    "ProductAgentCatalogEntryResult",
    "ProductAgentDefinitionResult",
    "ProductAgentDraftResult",
    "ProductAgentInstallationResult",
    "ProductAgentPublicationResult",
    "ProductAvailableActionResult",
    "ProductProjectionResult",
    "ProductProjectionRebuildConsumeResult",
    "ProductRuntimeDispatchConsumeResult",
    "ProductRuntimeRequestResult",
    "ProductService",
    "ProductStreamEventResult",
]
