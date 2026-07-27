from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from zuno.platform.database.foundation import (
    FencingRejectedError,
    InfrastructureConflictError,
    InfrastructureUnitOfWork,
)
from zuno.platform.database.tool_runtime import (
    PreparedToolActionInput,
    ToolAttemptInput,
    ToolExecutionReceiptInput,
    ToolObservationInput,
    ToolUnitOfWork,
    ToolVersionInput,
)
from zuno.platform.contracts import canonical_sha256
from zuno.platform.security import (
    SecurityPersistenceError,
    SecurityUnitOfWork,
    redact_sensitive_payload,
)
from .effect_policy import classify_tool_effect


@dataclass(frozen=True, slots=True)
class ToolGatewayReceipt:
    status: str
    prepared_tool_action_id: str
    attempt_id: str
    receipt_id: str
    blocked_reason: str = ""


class ToolInvocationGateway:
    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], ToolUnitOfWork],
        security_unit_of_work_factory: Callable[[], SecurityUnitOfWork] | None = None,
        infrastructure_unit_of_work_factory: Callable[[str], InfrastructureUnitOfWork] | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._security_unit_of_work_factory = security_unit_of_work_factory
        self._infrastructure_unit_of_work_factory = infrastructure_unit_of_work_factory

    async def invoke_readonly(
        self,
        *,
        tool_name: str,
        args: dict[str, Any],
        tenant_id: str,
        workspace_id: str,
        trace_id: str,
        call_id: str,
        adapter_kind: str,
        executor: Callable[[], Awaitable[Any]],
        readonly: bool,
        approved: bool = False,
    ) -> tuple[Any | None, ToolGatewayReceipt]:
        prepared_id = f"prepared-tool-action:{call_id}"
        attempt_id = f"tool-attempt:{call_id}"
        receipt_id = f"tool-execution-receipt:{call_id}"
        tool_definition_id = f"tool-definition:{tool_name}"
        tool_version_id = f"tool-version:{tool_name}:v1"
        effect_policy = classify_tool_effect(
            tool_name=tool_name,
            args=args,
            readonly=readonly,
            adapter_kind=adapter_kind,
        )

        with self._unit_of_work_factory() as repo:
            repo.publish_tool_version(
                ToolVersionInput(
                    tool_definition_id=tool_definition_id,
                    tool_version_id=tool_version_id,
                    tenant_id=tenant_id,
                    version_no=1,
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    adapter_kind=adapter_kind,
                    effect_level=effect_policy.effect_level,
                )
            )
            repo.record_adapter_binding(
                adapter_binding_id=f"tool-adapter-binding:{adapter_kind}:{tool_version_id}",
                tenant_id=tenant_id,
                tool_version_id=tool_version_id,
                adapter_kind=adapter_kind,
                adapter_version=f"{adapter_kind}:phase15",
                conformance_payload={
                    "readonly": readonly,
                    "gateway": "ToolInvocationGateway",
                    "effect_policy_version": effect_policy.policy_version,
                    "effect_policy_hash": effect_policy.policy_hash,
                },
            )
            repo.install_tool(
                tool_installation_id=f"tool-installation:{workspace_id}:{tool_name}",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                tool_version_id=tool_version_id,
                policy_ref=f"tool-policy:{tool_name}:phase15",
            )
            repo.activate_tool(
                tool_activation_id=f"tool-activation:{workspace_id}:{tool_name}",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                tool_installation_id=f"tool-installation:{workspace_id}:{tool_name}",
                expected_generation=1,
                activation_payload={
                    "gateway": "ToolInvocationGateway",
                    "readonly": readonly,
                    "effect_policy_version": effect_policy.policy_version,
                    "effect_policy_hash": effect_policy.policy_hash,
                },
            )
            prepared_action_hash = repo.prepare_action(
                PreparedToolActionInput(
                    prepared_tool_action_id=prepared_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    tool_operation_id=f"{tool_version_id}:operation:default",
                    canonical_args=redact_sensitive_payload(args),
                    target_resources=effect_policy.target_resource_set.resource_refs,
                    effect_level=effect_policy.effect_level,
                    approval_required=effect_policy.approval_required,
                    idempotency_key=call_id,
                    security_epoch_ref=f"security-epoch:{trace_id}",
                    effect_policy_version=effect_policy.policy_version,
                    effect_policy_hash=effect_policy.policy_hash,
                    target_resource_set_ref=effect_policy.target_resource_set.resource_set_ref,
                    target_conflict_keys=effect_policy.target_resource_set.conflict_keys,
                    action_proposal_ref=f"action-proposal:{call_id}",
                    status="READY" if effect_policy.provider_dispatch_allowed else "OBSOLETE",
                )
            )
        security_blocked_reason = ""
        if self._security_unit_of_work_factory is not None:
            security_blocked_reason = self._record_security_prepare(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                trace_id=trace_id,
                call_id=call_id,
                tool_name=tool_name,
                prepared_action_hash=prepared_action_hash,
                approval_required=effect_policy.approval_required,
                target_resource_set_ref=effect_policy.target_resource_set.resource_set_ref,
                approved=approved,
                secret_ref=str(args.get("secret_ref") or ""),
            )

        if not effect_policy.provider_dispatch_allowed:
            blocked_reason = effect_policy.blocked_reason or "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL"
            payload = {
                "blocked": True,
                "reason": blocked_reason,
                "effect_class": effect_policy.effect_class.value,
                "target_resource_set_ref": effect_policy.target_resource_set.resource_set_ref,
                "target_conflict_keys": list(effect_policy.target_resource_set.conflict_keys),
            }
            if security_blocked_reason:
                payload["security_blocked_reason"] = security_blocked_reason
            elif self._infrastructure_unit_of_work_factory is not None and effect_policy.approval_required:
                infrastructure_blocked_reason = self._record_execute_prerequisites(
                    tenant_id=tenant_id,
                    call_id=call_id,
                    prepared_action_hash=prepared_action_hash,
                    target_resource_set_ref=effect_policy.target_resource_set.resource_set_ref,
                )
                if infrastructure_blocked_reason:
                    payload["infrastructure_blocked_reason"] = infrastructure_blocked_reason
            self._record_terminal(
                tenant_id=tenant_id,
                prepared_id=prepared_id,
                attempt_id=attempt_id,
                receipt_id=receipt_id,
                status="FAILED",
                dispatch_certainty="NOT_DISPATCHED",
                effect_certainty="NO_EFFECT",
                adapter_kind=adapter_kind,
                payload=payload,
            )
            return None, ToolGatewayReceipt("blocked", prepared_id, attempt_id, receipt_id, blocked_reason)

        try:
            result = await executor()
        except Exception as exc:
            self._record_terminal(
                tenant_id=tenant_id,
                prepared_id=prepared_id,
                attempt_id=attempt_id,
                receipt_id=receipt_id,
                status="FAILED",
                dispatch_certainty="DISPATCHED",
                effect_certainty="NO_EFFECT",
                adapter_kind=adapter_kind,
                payload={"error_type": type(exc).__name__, "error": str(exc)},
            )
            raise

        self._record_terminal(
            tenant_id=tenant_id,
            prepared_id=prepared_id,
            attempt_id=attempt_id,
            receipt_id=receipt_id,
            status="SUCCEEDED",
            dispatch_certainty="DISPATCHED",
            effect_certainty="NO_EFFECT",
            adapter_kind=adapter_kind,
            payload={"result": str(result)[:2000]},
        )
        return result, ToolGatewayReceipt("completed", prepared_id, attempt_id, receipt_id)

    def _record_security_prepare(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        trace_id: str,
        call_id: str,
        tool_name: str,
        prepared_action_hash: str,
        approval_required: bool,
        target_resource_set_ref: str,
        approved: bool,
        secret_ref: str,
    ) -> str:
        epoch_ref = f"security-epoch:{trace_id}"
        principal_context_id = f"principal-context:{workspace_id}:{call_id}"
        decision_id = f"authorization-decision:{call_id}"
        policy_bundle = {
            "phase": "PHASE16",
            "tool_name": tool_name,
            "target_resource_set_ref": target_resource_set_ref,
            "actions": ["tool.prepare", "tool.execute"],
        }
        decision = "REQUIRES_APPROVAL" if approval_required else "ALLOW"
        reason_code = "side_effect_requires_approval" if approval_required else "readonly_prepare_allowed"
        assert self._security_unit_of_work_factory is not None
        with self._security_unit_of_work_factory() as repo:
            repo.ensure_effective_epoch(
                epoch_ref=epoch_ref,
                tenant_id=tenant_id,
                policy_bundle_ref=f"security-policy-bundle:{tool_name}:phase16",
                policy_bundle=policy_bundle,
                action_set_version="tool-side-effect-actions:v1.phase16",
                principal_context_hash=canonical_sha256(
                    {"workspace_id": workspace_id, "trace_id": trace_id, "call_id": call_id}
                ),
                generation=1,
            )
            repo.ensure_principal_context(
                principal_context_id=principal_context_id,
                tenant_id=tenant_id,
                user_principal_id=f"workspace-user:{workspace_id}",
                agent_principal_id="agent:zuno-tool-runtime",
                task_principal_id=f"tool-call:{call_id}",
                session_principal_id=f"trace:{trace_id}",
                run_id=call_id,
                epoch_ref=epoch_ref,
            )
            repo.ensure_authorization_decision(
                decision_id=decision_id,
                tenant_id=tenant_id,
                principal_context_id=principal_context_id,
                epoch_ref=epoch_ref,
                resource_ref=target_resource_set_ref,
                action="tool.execute",
                decision=decision,
                reason_code=reason_code,
                prepared_action_hash=prepared_action_hash,
            )
            if approval_required:
                repo.ensure_approval_request(
                    approval_request_id=f"approval-request:{call_id}",
                    tenant_id=tenant_id,
                    decision_id=decision_id,
                    prepared_action_hash=prepared_action_hash,
                    requested_by_principal_id="agent:zuno-tool-runtime",
                    required_approver_policy_ref="approval-policy:tool-runtime:phase16",
                )
                if approved:
                    repo.ensure_approval_decision(
                        approval_decision_id=f"approval-decision:{call_id}",
                        tenant_id=tenant_id,
                        approval_request_id=f"approval-request:{call_id}",
                        approver_principal_id="workspace-user:approved",
                        decision="approved",
                    )
            repo.ensure_audit_requirement(
                audit_requirement_id=f"audit-requirement:{call_id}:tool-execute",
                tenant_id=tenant_id,
                decision_id=decision_id,
                audit_channel_id="audit-channel:tool-runtime:phase16",
            )
            try:
                repo.validate_pre_effect_authorization(
                    decision_id=decision_id,
                    tenant_id=tenant_id,
                    prepared_action_hash=prepared_action_hash,
                    require_approved_request=approval_required,
                )
            except SecurityPersistenceError as exc:
                return str(exc)
            if approval_required:
                if not secret_ref:
                    return "secret lease missing before effect"
                lease_id = f"security-secret-lease:{call_id}"
                repo.issue_secret_lease(
                    lease_id=lease_id,
                    tenant_id=tenant_id,
                    secret_ref=secret_ref,
                    workload_identity_ref=f"tool-runtime:{call_id}",
                    on_behalf_of_binding_ref=f"approval-request:{call_id}",
                    audience=f"tool:{tool_name}",
                    lease_generation=1,
                    expires_at=datetime.now(tz=UTC) + timedelta(minutes=5),
                )
                try:
                    repo.validate_secret_lease(
                        lease_id=lease_id,
                        tenant_id=tenant_id,
                        audience=f"tool:{tool_name}",
                    )
                except SecurityPersistenceError as exc:
                    return str(exc)
        return ""

    def _record_execute_prerequisites(
        self,
        *,
        tenant_id: str,
        call_id: str,
        prepared_action_hash: str,
        target_resource_set_ref: str,
    ) -> str:
        assert self._infrastructure_unit_of_work_factory is not None
        owner = f"tool-runtime:{call_id}"
        try:
            with self._infrastructure_unit_of_work_factory(tenant_id) as repo:
                claim = repo.claim_idempotency_receipt(
                    scope="tool-side-effect",
                    key=call_id,
                    owner=owner,
                    request={
                        "prepared_action_hash": prepared_action_hash,
                        "target_resource_set_ref": target_resource_set_ref,
                    },
                    ttl_seconds=60,
                )
                if not claim.acquired:
                    return "idempotency claim is already held or completed"
                fence = repo.acquire_lease(
                    resource_id=target_resource_set_ref,
                    owner_id=owner,
                    ttl_seconds=60,
                )
                repo.assert_fence(fence)
        except (InfrastructureConflictError, FencingRejectedError) as exc:
            return str(exc)
        return ""

    def _record_terminal(
        self,
        *,
        tenant_id: str,
        prepared_id: str,
        attempt_id: str,
        receipt_id: str,
        status: str,
        dispatch_certainty: str,
        effect_certainty: str,
        adapter_kind: str,
        payload: dict[str, Any],
    ) -> None:
        with self._unit_of_work_factory() as repo:
            repo.record_attempt(
                ToolAttemptInput(
                    attempt_id=attempt_id,
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    status=status,
                    dispatch_certainty=dispatch_certainty,
                    adapter_family=adapter_kind,
                    hidden_retry_count=0,
                    state_history=("STARTED", status),
                )
            )
            repo.record_observation(
                ToolObservationInput(
                    observation_id=f"tool-observation:{attempt_id}",
                    tenant_id=tenant_id,
                    attempt_id=attempt_id,
                    owner_module="08 Tool Runtime",
                    normalized_projection_owner="06 Agent Core / Planning & Control",
                    output_trusted=False,
                    schema_valid=status == "SUCCEEDED",
                    memory_write_allowed=False,
                    evidence_write_allowed=False,
                    payload=payload,
                )
            )
            repo.record_execution_receipt(
                ToolExecutionReceiptInput(
                    receipt_id=receipt_id,
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    attempt_id=attempt_id,
                    status=status,
                    dispatch_certainty=dispatch_certainty,
                    effect_certainty=effect_certainty,
                    append_only_generation=1,
                    receipt_payload=payload,
                )
            )
            repo.record_bypass_guard(
                receipt_id=f"tool-bypass-guard:{attempt_id}",
                tenant_id=tenant_id,
                scope="langchain_tool_gateway",
                allowlist_count=0,
                guard_payload={"gateway": "ToolInvocationGateway", "direct_handler_bypass": False},
            )

__all__ = ["ToolGatewayReceipt", "ToolInvocationGateway"]
