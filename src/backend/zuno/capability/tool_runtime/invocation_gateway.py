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
    ToolEffectReceiptInput,
    ToolEffectReconciliationInput,
    ToolAsyncJobInput,
    ToolAsyncCallbackInput,
    ToolCancellationReceiptInput,
    ToolManualEffectAssessmentInput,
    ToolCompensationAttemptInput,
    ToolCompensationDefinitionInput,
    ToolExecutionReceiptInput,
    ToolObservationInput,
    ToolSandboxReceiptInput,
    ToolSandboxSessionInput,
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
from .sandbox import SandboxAdapterRegistry, SandboxExecutionResult, SandboxPolicyViolation, SandboxSessionRecord, SandboxSessionStore


class ToolEffectUnknownError(RuntimeError):
    def __init__(
        self,
        *,
        provider_effect_id: str,
        reconciliation_query: dict[str, Any],
        message: str = "tool effect outcome is unknown",
    ) -> None:
        super().__init__(message)
        self.provider_effect_id = provider_effect_id
        self.reconciliation_query = reconciliation_query

@dataclass(frozen=True, slots=True)
class ToolGatewayReceipt:
    status: str
    prepared_tool_action_id: str
    attempt_id: str
    receipt_id: str
    blocked_reason: str = ""
    result_ref: str = ""



@dataclass(frozen=True, slots=True)
class _SecurityPrepareResult:
    blocked_reason: str = ""


@dataclass(frozen=True, slots=True)
class _ExecutePrerequisiteResult:
    blocked_reason: str = ""
    replay_result_ref: str = ""
    idempotency_scope: str = ""
    idempotency_key: str = ""
    idempotency_generation: int = 0
    fencing_resource_id: str = ""
    fencing_lease_id: str = ""
    fencing_epoch: int = 0


class _ToolRuntimeSandboxSessionStore(SandboxSessionStore):
    def __init__(self, unit_of_work_factory: Callable[[], ToolUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def put(self, record: SandboxSessionRecord) -> None:
        with self._unit_of_work_factory() as repo:
            repo.record_sandbox_session(
                ToolSandboxSessionInput(
                    session_ref=record.session_ref,
                    tenant_id=record.tenant_id,
                    workspace_id=record.workspace_id,
                    run_id=record.run_id,
                    thread_id=record.thread_id,
                    call_id=record.call_id,
                    sandbox_profile_id=record.sandbox_profile_id,
                    adapter_tier=record.adapter_tier,
                    session_version=record.session_version,
                    profile_hash=record.profile_hash,
                    limits_hash=record.limits_hash,
                    session_hash=record.session_hash,
                    state_integrity_hash=canonical_sha256(
                        {
                            "session_hash": record.session_hash,
                            "profile_hash": record.profile_hash,
                            "limits_hash": record.limits_hash,
                        }
                    ),
                    session_size_bytes=record.session_size_bytes,
                    expires_at=record.expires_at,
                )
            )

    def get(self, session_ref: str) -> SandboxSessionRecord | None:
        with self._unit_of_work_factory() as repo:
            row = repo.get_sandbox_session(session_ref=session_ref)
        if row is None:
            return None
        return SandboxSessionRecord(
            session_ref=str(row["session_ref"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            run_id=str(row["run_id"]),
            thread_id=str(row["thread_id"]),
            call_id=str(row["call_id"]),
            sandbox_profile_id=str(row["sandbox_profile_id"]),
            adapter_tier=str(row["adapter_tier"]),
            session_version=int(row["session_version"]),
            profile_hash=str(row["profile_hash"]),
            limits_hash=str(row["limits_hash"]),
            session_hash=str(row["session_hash"]),
            expires_at=row["expires_at"],
            session_size_bytes=int(row["session_size_bytes"]),
        )


class ToolInvocationGateway:
    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], ToolUnitOfWork],
        security_unit_of_work_factory: Callable[[], SecurityUnitOfWork] | None = None,
        infrastructure_unit_of_work_factory: Callable[[str], InfrastructureUnitOfWork] | None = None,
        sandbox_registry: SandboxAdapterRegistry | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._security_unit_of_work_factory = security_unit_of_work_factory
        self._infrastructure_unit_of_work_factory = infrastructure_unit_of_work_factory
        self._sandbox_registry = sandbox_registry or SandboxAdapterRegistry(
            session_store=_ToolRuntimeSandboxSessionStore(unit_of_work_factory)
        )

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
        security_prepare = _SecurityPrepareResult()
        if self._security_unit_of_work_factory is not None:
            security_prepare = self._record_security_prepare(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                trace_id=trace_id,
                call_id=call_id,
                tool_name=tool_name,
                prepared_action_hash=prepared_action_hash,
                approval_required=effect_policy.approval_required,
                target_resource_set_ref=effect_policy.target_resource_set.resource_set_ref,
                approved=approved,
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
            if security_prepare.blocked_reason:
                payload["security_blocked_reason"] = security_prepare.blocked_reason
            elif self._infrastructure_unit_of_work_factory is not None and effect_policy.approval_required:
                if approved and not str(args.get("secret_ref") or ""):
                    payload["security_blocked_reason"] = "secret lease missing before effect"
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
                execute_prerequisites = self._record_execute_prerequisites(
                    tenant_id=tenant_id,
                    call_id=call_id,
                    prepared_action_hash=prepared_action_hash,
                    target_resource_set_ref=effect_policy.target_resource_set.resource_set_ref,
                )
                if execute_prerequisites.replay_result_ref:
                    replay_payload = {
                        "idempotency_replay": True,
                        "result_ref": execute_prerequisites.replay_result_ref,
                        "idempotency_scope": "tool-side-effect",
                        "idempotency_key": call_id,
                    }
                    return replay_payload, ToolGatewayReceipt(
                        "replayed",
                        prepared_id,
                        attempt_id,
                        receipt_id,
                        "IDEMPOTENT_SIDE_EFFECT_REPLAY",
                        execute_prerequisites.replay_result_ref,
                    )
                if execute_prerequisites.blocked_reason:
                    blocked_reason = execute_prerequisites.blocked_reason
                    payload["reason"] = blocked_reason
                    payload["infrastructure_blocked_reason"] = execute_prerequisites.blocked_reason
                elif approved:
                    try:
                        self._reauthorize_execute_epoch(
                            tenant_id=tenant_id,
                            call_id=call_id,
                            prepared_action_hash=prepared_action_hash,
                            approval_required=effect_policy.approval_required,
                        )
                    except SecurityPersistenceError as exc:
                        payload["security_blocked_reason"] = str(exc)
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
                        return None, ToolGatewayReceipt("blocked", prepared_id, attempt_id, receipt_id, str(exc))
                    try:
                        secret_lease_id = self._issue_secret_lease(
                            tenant_id=tenant_id,
                            call_id=call_id,
                            tool_name=tool_name,
                            secret_ref=str(args.get("secret_ref") or ""),
                        )
                    except SecurityPersistenceError as exc:
                        payload["security_blocked_reason"] = str(exc)
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
                        return None, ToolGatewayReceipt("blocked", prepared_id, attempt_id, receipt_id, str(exc))
                    sandbox_blocked_reason, sandbox_result = self._prepare_sandbox_or_block(
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        trace_id=trace_id,
                        call_id=call_id,
                        tool_name=tool_name,
                        adapter_kind=adapter_kind,
                        args=args,
                        prepared_id=prepared_id,
                        attempt_id=attempt_id,
                        receipt_id=receipt_id,
                    )
                    if sandbox_blocked_reason:
                        payload["sandbox_blocked_reason"] = sandbox_blocked_reason
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
                        return None, ToolGatewayReceipt("blocked", prepared_id, attempt_id, receipt_id, sandbox_blocked_reason)
                    if sandbox_result is not None:
                        sandbox_reconciliation_payload = _sandbox_observation_reconciliation_payload(
                            sandbox_result=sandbox_result,
                            call_id=call_id,
                        )
                        self._record_terminal(
                            tenant_id=tenant_id,
                            prepared_id=prepared_id,
                            attempt_id=attempt_id,
                            receipt_id=receipt_id,
                            status="UNKNOWN",
                            dispatch_certainty="DISPATCHED",
                            effect_certainty="UNKNOWN_EFFECT",
                            adapter_kind=adapter_kind,
                            payload=sandbox_reconciliation_payload,
                        )
                        reconciliation_id = f"tool-effect-reconciliation:{call_id}"
                        with self._unit_of_work_factory() as repo:
                            repo.record_effect_reconciliation(
                                ToolEffectReconciliationInput(
                                    reconciliation_id=reconciliation_id,
                                    tenant_id=tenant_id,
                                    prepared_tool_action_id=prepared_id,
                                    attempt_id=attempt_id,
                                    execution_receipt_id=receipt_id,
                                    provider_effect_id=str(sandbox_reconciliation_payload["provider_effect_id"]),
                                    status="OPEN",
                                    next_action="RECONCILE",
                                    reconciliation_query=sandbox_reconciliation_payload["reconciliation_query"],
                                    manual_assessment_required=False,
                                    age_escalation_after_seconds=900,
                                    idempotency_scope=execute_prerequisites.idempotency_scope,
                                    idempotency_key=execute_prerequisites.idempotency_key,
                                    idempotency_generation=execute_prerequisites.idempotency_generation,
                                    fencing_resource_id=execute_prerequisites.fencing_resource_id,
                                    fencing_lease_id=execute_prerequisites.fencing_lease_id,
                                    fencing_epoch=execute_prerequisites.fencing_epoch,
                                    secret_lease_id=secret_lease_id,
                                    reconciliation_payload=sandbox_reconciliation_payload,
                                )
                            )
                        self._complete_execute_prerequisites(
                            tenant_id=tenant_id,
                            owner=f"tool-runtime:{call_id}",
                            prerequisites=execute_prerequisites,
                            result_ref=reconciliation_id,
                        )
                        return None, ToolGatewayReceipt(
                            "reconcile_required",
                            prepared_id,
                            attempt_id,
                            receipt_id,
                            "SANDBOX_OBSERVATION_REQUIRES_EFFECT_RECONCILIATION",
                        )
                    try:
                        result = await executor()
                    except ToolEffectUnknownError as exc:
                        unknown_payload = _unknown_effect_payload(exc=exc, call_id=call_id)
                        self._record_terminal(
                            tenant_id=tenant_id,
                            prepared_id=prepared_id,
                            attempt_id=attempt_id,
                            receipt_id=receipt_id,
                            status="UNKNOWN",
                            dispatch_certainty="DISPATCHED",
                            effect_certainty="UNKNOWN_EFFECT",
                            adapter_kind=adapter_kind,
                            payload=unknown_payload,
                        )
                        reconciliation_id = f"tool-effect-reconciliation:{call_id}"
                        with self._unit_of_work_factory() as repo:
                            repo.record_effect_reconciliation(
                                ToolEffectReconciliationInput(
                                    reconciliation_id=reconciliation_id,
                                    tenant_id=tenant_id,
                                    prepared_tool_action_id=prepared_id,
                                    attempt_id=attempt_id,
                                    execution_receipt_id=receipt_id,
                                    provider_effect_id=exc.provider_effect_id,
                                    status="OPEN",
                                    next_action="RECONCILE",
                                    reconciliation_query=exc.reconciliation_query,
                                    manual_assessment_required=False,
                                    age_escalation_after_seconds=900,
                                    idempotency_scope=execute_prerequisites.idempotency_scope,
                                    idempotency_key=execute_prerequisites.idempotency_key,
                                    idempotency_generation=execute_prerequisites.idempotency_generation,
                                    fencing_resource_id=execute_prerequisites.fencing_resource_id,
                                    fencing_lease_id=execute_prerequisites.fencing_lease_id,
                                    fencing_epoch=execute_prerequisites.fencing_epoch,
                                    secret_lease_id=secret_lease_id,
                                    reconciliation_payload=unknown_payload,
                                )
                            )
                        self._complete_execute_prerequisites(
                            tenant_id=tenant_id,
                            owner=f"tool-runtime:{call_id}",
                            prerequisites=execute_prerequisites,
                            result_ref=reconciliation_id,
                        )
                        return None, ToolGatewayReceipt(
                            "reconcile_required",
                            prepared_id,
                            attempt_id,
                            receipt_id,
                            "UNKNOWN_EFFECT_RECONCILIATION_REQUIRED",
                        )
                    except Exception as exc:
                        unknown_payload = _unknown_effect_payload_from_exception(exc=exc, call_id=call_id)
                        self._record_terminal(
                            tenant_id=tenant_id,
                            prepared_id=prepared_id,
                            attempt_id=attempt_id,
                            receipt_id=receipt_id,
                            status="UNKNOWN",
                            dispatch_certainty="DISPATCHED",
                            effect_certainty="UNKNOWN_EFFECT",
                            adapter_kind=adapter_kind,
                            payload=unknown_payload,
                        )
                        reconciliation_id = f"tool-effect-reconciliation:{call_id}"
                        with self._unit_of_work_factory() as repo:
                            repo.record_effect_reconciliation(
                                ToolEffectReconciliationInput(
                                    reconciliation_id=reconciliation_id,
                                    tenant_id=tenant_id,
                                    prepared_tool_action_id=prepared_id,
                                    attempt_id=attempt_id,
                                    execution_receipt_id=receipt_id,
                                    provider_effect_id=str(unknown_payload["provider_effect_id"]),
                                    status="OPEN",
                                    next_action="RECONCILE",
                                    reconciliation_query=unknown_payload["reconciliation_query"],
                                    manual_assessment_required=False,
                                    age_escalation_after_seconds=900,
                                    idempotency_scope=execute_prerequisites.idempotency_scope,
                                    idempotency_key=execute_prerequisites.idempotency_key,
                                    idempotency_generation=execute_prerequisites.idempotency_generation,
                                    fencing_resource_id=execute_prerequisites.fencing_resource_id,
                                    fencing_lease_id=execute_prerequisites.fencing_lease_id,
                                    fencing_epoch=execute_prerequisites.fencing_epoch,
                                    secret_lease_id=secret_lease_id,
                                    reconciliation_payload=unknown_payload,
                                )
                            )
                        self._complete_execute_prerequisites(
                            tenant_id=tenant_id,
                            owner=f"tool-runtime:{call_id}",
                            prerequisites=execute_prerequisites,
                            result_ref=reconciliation_id,
                        )
                        return None, ToolGatewayReceipt(
                            "reconcile_required",
                            prepared_id,
                            attempt_id,
                            receipt_id,
                            "UNKNOWN_EFFECT_RECONCILIATION_REQUIRED",
                        )
                    if effect_policy.effect_class.value == "ASYNC_EXTERNAL":
                        async_payload = _async_job_payload_from_result(result=result, call_id=call_id)
                        provider_job_id = str(async_payload["provider_job_id"])
                        self._record_terminal(
                            tenant_id=tenant_id,
                            prepared_id=prepared_id,
                            attempt_id=attempt_id,
                            receipt_id=receipt_id,
                            status="DISPATCHED",
                            dispatch_certainty="DISPATCHED",
                            effect_certainty="UNKNOWN_EFFECT",
                            adapter_kind=adapter_kind,
                            payload=async_payload,
                        )
                        async_job_id = f"tool-async-job:{call_id}"
                        try:
                            with self._unit_of_work_factory() as repo:
                                repo.record_async_job(
                                    ToolAsyncJobInput(
                                        async_job_id=async_job_id,
                                        tenant_id=tenant_id,
                                        prepared_tool_action_id=prepared_id,
                                        attempt_id=attempt_id,
                                        execution_receipt_id=receipt_id,
                                        provider_job_id=provider_job_id,
                                        status="WAITING_CALLBACK",
                                        callback_binding_ref=f"callback-binding:{call_id}",
                                        callback_order=0,
                                        deadline_at=datetime.now(tz=UTC) + timedelta(minutes=15),
                                        idempotency_scope=execute_prerequisites.idempotency_scope,
                                        idempotency_key=execute_prerequisites.idempotency_key,
                                        idempotency_generation=execute_prerequisites.idempotency_generation,
                                        fencing_resource_id=execute_prerequisites.fencing_resource_id,
                                        fencing_lease_id=execute_prerequisites.fencing_lease_id,
                                        fencing_epoch=execute_prerequisites.fencing_epoch,
                                        secret_lease_id=secret_lease_id,
                                        job_payload=async_payload,
                                    )
                                )
                            self._complete_execute_prerequisites(
                                tenant_id=tenant_id,
                                owner=f"tool-runtime:{call_id}",
                                prerequisites=execute_prerequisites,
                                result_ref=async_job_id,
                            )
                            with self._unit_of_work_factory() as repo:
                                repo.update_execution_receipt(
                                    ToolExecutionReceiptInput(
                                        receipt_id=receipt_id,
                                        tenant_id=tenant_id,
                                        prepared_tool_action_id=prepared_id,
                                        attempt_id=attempt_id,
                                        status="DISPATCHED",
                                        dispatch_certainty="DISPATCHED",
                                        effect_certainty="UNKNOWN_EFFECT",
                                        append_only_generation=1,
                                        receipt_payload=async_payload,
                                    )
                                )
                            return result, ToolGatewayReceipt("async_waiting", prepared_id, attempt_id, receipt_id)
                        except Exception as exc:
                            recovery_payload = _recovery_unknown_effect_payload_from_result(
                                result=result,
                                effect_payload=async_payload,
                                call_id=call_id,
                                exc=exc,
                            )
                            self._record_terminal(
                                tenant_id=tenant_id,
                                prepared_id=prepared_id,
                                attempt_id=attempt_id,
                                receipt_id=receipt_id,
                                status="UNKNOWN",
                                dispatch_certainty="DISPATCHED",
                                effect_certainty="UNKNOWN_EFFECT",
                                adapter_kind=adapter_kind,
                                payload=recovery_payload,
                            )
                            reconciliation_id = f"tool-effect-reconciliation:{call_id}"
                            with self._unit_of_work_factory() as repo:
                                repo.record_effect_reconciliation(
                                    ToolEffectReconciliationInput(
                                        reconciliation_id=reconciliation_id,
                                        tenant_id=tenant_id,
                                        prepared_tool_action_id=prepared_id,
                                        attempt_id=attempt_id,
                                        execution_receipt_id=receipt_id,
                                        provider_effect_id=provider_job_id,
                                        status="OPEN",
                                        next_action="RECONCILE",
                                        reconciliation_query=recovery_payload["reconciliation_query"],
                                        manual_assessment_required=False,
                                        age_escalation_after_seconds=900,
                                        idempotency_scope=execute_prerequisites.idempotency_scope,
                                        idempotency_key=execute_prerequisites.idempotency_key,
                                        idempotency_generation=execute_prerequisites.idempotency_generation,
                                        fencing_resource_id=execute_prerequisites.fencing_resource_id,
                                        fencing_lease_id=execute_prerequisites.fencing_lease_id,
                                        fencing_epoch=execute_prerequisites.fencing_epoch,
                                        secret_lease_id=secret_lease_id,
                                        reconciliation_payload=recovery_payload,
                                    )
                                )
                                repo.update_execution_receipt(
                                    ToolExecutionReceiptInput(
                                        receipt_id=receipt_id,
                                        tenant_id=tenant_id,
                                        prepared_tool_action_id=prepared_id,
                                        attempt_id=attempt_id,
                                        status="UNKNOWN",
                                        dispatch_certainty="DISPATCHED",
                                        effect_certainty="UNKNOWN_EFFECT",
                                        append_only_generation=1,
                                        receipt_payload=recovery_payload,
                                    )
                                )
                            try:
                                self._complete_execute_prerequisites(
                                    tenant_id=tenant_id,
                                    owner=f"tool-runtime:{call_id}",
                                    prerequisites=execute_prerequisites,
                                    result_ref=reconciliation_id,
                                )
                            except FencingRejectedError:
                                pass
                            return None, ToolGatewayReceipt(
                                "reconcile_required",
                                prepared_id,
                                attempt_id,
                                receipt_id,
                                "UNKNOWN_EFFECT_RECONCILIATION_REQUIRED",
                            )
                    effect_payload = _effect_payload_from_result(result=result, call_id=call_id)
                    provider_effect_id = str(effect_payload["provider_effect_id"])
                    self._record_terminal(
                        tenant_id=tenant_id,
                        prepared_id=prepared_id,
                        attempt_id=attempt_id,
                        receipt_id=receipt_id,
                        status="DISPATCHED",
                        dispatch_certainty="DISPATCHED",
                        effect_certainty="UNKNOWN_EFFECT",
                        adapter_kind=adapter_kind,
                        payload=effect_payload,
                    )
                    try:
                        effect_receipt_id = f"tool-effect-receipt:{call_id}"
                        with self._unit_of_work_factory() as repo:
                            repo.record_effect_receipt(
                                ToolEffectReceiptInput(
                                    effect_receipt_id=effect_receipt_id,
                                    tenant_id=tenant_id,
                                    prepared_tool_action_id=prepared_id,
                                    attempt_id=attempt_id,
                                    execution_receipt_id=receipt_id,
                                    provider_effect_id=provider_effect_id,
                                    effect_status="CONFIRMED",
                                    effect_certainty="CONFIRMED_EFFECT",
                                    idempotency_scope=execute_prerequisites.idempotency_scope,
                                    idempotency_key=execute_prerequisites.idempotency_key,
                                    idempotency_generation=execute_prerequisites.idempotency_generation,
                                    fencing_resource_id=execute_prerequisites.fencing_resource_id,
                                    fencing_lease_id=execute_prerequisites.fencing_lease_id,
                                    fencing_epoch=execute_prerequisites.fencing_epoch,
                                    secret_lease_id=secret_lease_id,
                                    native_result={"result": redact_sensitive_payload(result)},
                                    effect_payload=effect_payload,
                                    append_only_generation=1,
                                )
                            )
                        self._complete_execute_prerequisites(
                            tenant_id=tenant_id,
                            owner=f"tool-runtime:{call_id}",
                            prerequisites=execute_prerequisites,
                            result_ref=effect_receipt_id,
                        )
                        with self._unit_of_work_factory() as repo:
                            repo.update_execution_receipt(
                                ToolExecutionReceiptInput(
                                    receipt_id=receipt_id,
                                    tenant_id=tenant_id,
                                    prepared_tool_action_id=prepared_id,
                                    attempt_id=attempt_id,
                                    status="SUCCEEDED",
                                    dispatch_certainty="DISPATCHED",
                                    effect_certainty="CONFIRMED_EFFECT",
                                    append_only_generation=1,
                                    receipt_payload=effect_payload,
                                )
                            )
                        return result, ToolGatewayReceipt("completed", prepared_id, attempt_id, receipt_id)
                    except Exception as exc:
                        recovery_payload = _recovery_unknown_effect_payload_from_result(
                            result=result,
                            effect_payload=effect_payload,
                            call_id=call_id,
                            exc=exc,
                        )
                        self._record_terminal(
                            tenant_id=tenant_id,
                            prepared_id=prepared_id,
                            attempt_id=attempt_id,
                            receipt_id=receipt_id,
                            status="UNKNOWN",
                            dispatch_certainty="DISPATCHED",
                            effect_certainty="UNKNOWN_EFFECT",
                            adapter_kind=adapter_kind,
                            payload=recovery_payload,
                        )
                        reconciliation_id = f"tool-effect-reconciliation:{call_id}"
                        with self._unit_of_work_factory() as repo:
                            repo.record_effect_reconciliation(
                                ToolEffectReconciliationInput(
                                    reconciliation_id=reconciliation_id,
                                    tenant_id=tenant_id,
                                    prepared_tool_action_id=prepared_id,
                                    attempt_id=attempt_id,
                                    execution_receipt_id=receipt_id,
                                    provider_effect_id=provider_effect_id,
                                    status="OPEN",
                                    next_action="RECONCILE",
                                    reconciliation_query=recovery_payload["reconciliation_query"],
                                    manual_assessment_required=False,
                                    age_escalation_after_seconds=900,
                                    idempotency_scope=execute_prerequisites.idempotency_scope,
                                    idempotency_key=execute_prerequisites.idempotency_key,
                                    idempotency_generation=execute_prerequisites.idempotency_generation,
                                    fencing_resource_id=execute_prerequisites.fencing_resource_id,
                                    fencing_lease_id=execute_prerequisites.fencing_lease_id,
                                    fencing_epoch=execute_prerequisites.fencing_epoch,
                                    secret_lease_id=secret_lease_id,
                                    reconciliation_payload=recovery_payload,
                                )
                            )
                            repo.update_execution_receipt(
                                ToolExecutionReceiptInput(
                                    receipt_id=receipt_id,
                                    tenant_id=tenant_id,
                                    prepared_tool_action_id=prepared_id,
                                    attempt_id=attempt_id,
                                    status="UNKNOWN",
                                    dispatch_certainty="DISPATCHED",
                                    effect_certainty="UNKNOWN_EFFECT",
                                    append_only_generation=1,
                                    receipt_payload=recovery_payload,
                                )
                            )
                        try:
                            self._complete_execute_prerequisites(
                                tenant_id=tenant_id,
                                owner=f"tool-runtime:{call_id}",
                                prerequisites=execute_prerequisites,
                                result_ref=reconciliation_id,
                            )
                        except FencingRejectedError:
                            pass
                        return None, ToolGatewayReceipt(
                            "reconcile_required",
                            prepared_id,
                            attempt_id,
                            receipt_id,
                            "UNKNOWN_EFFECT_RECONCILIATION_REQUIRED",
                        )
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
            sandbox_blocked_reason, sandbox_result = self._prepare_sandbox_or_block(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                trace_id=trace_id,
                call_id=call_id,
                tool_name=tool_name,
                adapter_kind=adapter_kind,
                args=args,
                prepared_id=prepared_id,
                attempt_id=attempt_id,
                receipt_id=receipt_id,
            )
            if sandbox_blocked_reason:
                self._record_terminal(
                    tenant_id=tenant_id,
                    prepared_id=prepared_id,
                    attempt_id=attempt_id,
                    receipt_id=receipt_id,
                    status="FAILED",
                    dispatch_certainty="NOT_DISPATCHED",
                    effect_certainty="NO_EFFECT",
                    adapter_kind=adapter_kind,
                    payload={"blocked": True, "reason": sandbox_blocked_reason},
                )
                return None, ToolGatewayReceipt("blocked", prepared_id, attempt_id, receipt_id, sandbox_blocked_reason)
            result = sandbox_result.output_payload if sandbox_result is not None else await executor()
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
    ) -> _SecurityPrepareResult:
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
                return _SecurityPrepareResult(blocked_reason=str(exc))
        return _SecurityPrepareResult()

    def _prepare_sandbox_or_block(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        trace_id: str,
        call_id: str,
        tool_name: str,
        adapter_kind: str,
        args: dict[str, Any],
        prepared_id: str,
        attempt_id: str,
        receipt_id: str,
    ) -> tuple[str, SandboxExecutionResult | None]:
        try:
            sandbox = self._sandbox_registry.prepare(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                run_id=call_id,
                thread_id=trace_id,
                call_id=call_id,
                tool_name=tool_name,
                adapter_kind=adapter_kind,
                args=redact_sensitive_payload(args),
            )
        except SandboxPolicyViolation as exc:
            return str(exc), None
        try:
            sandbox_result = self._sandbox_registry.execute(dispatch=sandbox, args=redact_sensitive_payload(args))
        except SandboxPolicyViolation as exc:
            self._record_sandbox_receipt(
                tenant_id=tenant_id,
                call_id=call_id,
                prepared_id=prepared_id,
                attempt_id=attempt_id,
                receipt_id=receipt_id,
                adapter_kind=adapter_kind,
                sandbox=sandbox,
                sandbox_result=SandboxExecutionResult(
                    status="BLOCKED",
                    stdout="",
                    stderr=str(exc),
                    exit_code=126,
                    output_payload={"sandbox_blocked_reason": str(exc), "session_ref": sandbox.session_ref},
                ),
            )
            return str(exc), None
        sandbox_result = _redact_sandbox_execution_result(sandbox_result)
        self._record_sandbox_receipt(
            tenant_id=tenant_id,
            call_id=call_id,
            prepared_id=prepared_id,
            attempt_id=attempt_id,
            receipt_id=receipt_id,
            adapter_kind=adapter_kind,
            sandbox=sandbox,
            sandbox_result=sandbox_result,
        )
        if sandbox_result.status != "SUCCEEDED":
            return "sandbox execution failed", None
        return "", sandbox_result

    def _record_sandbox_receipt(
        self,
        *,
        tenant_id: str,
        call_id: str,
        prepared_id: str,
        attempt_id: str,
        receipt_id: str,
        adapter_kind: str,
        sandbox: Any,
        sandbox_result: SandboxExecutionResult,
    ) -> None:
        payload = dict(sandbox.dispatch_payload)
        payload["prepared_tool_action_id"] = prepared_id
        payload["attempt_id"] = attempt_id
        payload["execution_receipt_id"] = receipt_id
        payload["sandbox_execution"] = sandbox_result.output_payload
        payload["sandbox_execution_status"] = sandbox_result.status
        with self._unit_of_work_factory() as repo:
            repo.record_attempt(
                ToolAttemptInput(
                    attempt_id=attempt_id,
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    status="STARTED",
                    dispatch_certainty="NOT_DISPATCHED",
                    adapter_family=adapter_kind,
                    hidden_retry_count=0,
                    state_history=("STARTED",),
                )
            )
            repo.record_sandbox_receipt(
                ToolSandboxReceiptInput(
                    sandbox_receipt_id=f"tool-sandbox-receipt:{call_id}",
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    attempt_id=attempt_id,
                    sandbox_profile_id=sandbox.sandbox_profile_id,
                    adapter_tier=sandbox.adapter_tier,
                    session_ref=sandbox.session_ref,
                    session_version=sandbox.session_version,
                    profile_hash=sandbox.profile_hash,
                    limits_hash=sandbox.limits_hash,
                    session_hash=sandbox.session_hash,
                    state_integrity_hash=canonical_sha256(
                        {
                            "session_hash": sandbox.session_hash,
                            "profile_hash": sandbox.profile_hash,
                            "limits_hash": sandbox.limits_hash,
                        }
                    ),
                    isolation_verified=True,
                    allowlist_enforced=True,
                    receipt_payload=payload,
                )
            )

    def _issue_secret_lease(
        self,
        *,
        tenant_id: str,
        call_id: str,
        tool_name: str,
        secret_ref: str,
    ) -> str:
        assert self._security_unit_of_work_factory is not None
        lease_id = f"security-secret-lease:{call_id}"
        with self._security_unit_of_work_factory() as repo:
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
            repo.validate_secret_lease(
                lease_id=lease_id,
                tenant_id=tenant_id,
                audience=f"tool:{tool_name}",
            )
        return lease_id

    def _reauthorize_execute_epoch(
        self,
        *,
        tenant_id: str,
        call_id: str,
        prepared_action_hash: str,
        approval_required: bool,
    ) -> None:
        assert self._security_unit_of_work_factory is not None
        decision_id = f"authorization-decision:{call_id}"
        with self._security_unit_of_work_factory() as repo:
            repo.validate_pre_effect_authorization(
                decision_id=decision_id,
                tenant_id=tenant_id,
                prepared_action_hash=prepared_action_hash,
                require_approved_request=approval_required,
            )

    def _record_execute_prerequisites(
        self,
        *,
        tenant_id: str,
        call_id: str,
        prepared_action_hash: str,
        target_resource_set_ref: str,
    ) -> _ExecutePrerequisiteResult:
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
                    if claim.status == "completed" and claim.result_ref:
                        return _ExecutePrerequisiteResult(replay_result_ref=claim.result_ref)
                    recovered_result_ref = self._existing_side_effect_result_ref(tenant_id=tenant_id, call_id=call_id)
                    if recovered_result_ref:
                        if claim.status == "in_progress" and claim.owner == owner:
                            try:
                                repo.complete_idempotency(
                                    scope="tool-side-effect",
                                    key=call_id,
                                    owner=owner,
                                    generation=claim.generation,
                                    result_ref=recovered_result_ref,
                                )
                            except FencingRejectedError:
                                pass
                        return _ExecutePrerequisiteResult(replay_result_ref=recovered_result_ref)
                    return _ExecutePrerequisiteResult(blocked_reason="idempotency claim is already held or completed")
                fence = repo.acquire_lease(
                    resource_id=target_resource_set_ref,
                    owner_id=owner,
                    ttl_seconds=60,
                )
                repo.assert_fence(fence)
        except (InfrastructureConflictError, FencingRejectedError) as exc:
            return _ExecutePrerequisiteResult(blocked_reason=str(exc))
        return _ExecutePrerequisiteResult(
            idempotency_scope="tool-side-effect",
            idempotency_key=call_id,
            idempotency_generation=claim.generation,
            fencing_resource_id=fence.resource_id,
            fencing_lease_id=fence.lease_id,
            fencing_epoch=fence.epoch,
        )

    def _existing_side_effect_result_ref(self, *, tenant_id: str, call_id: str) -> str:
        with self._unit_of_work_factory() as repo:
            return repo.existing_side_effect_result_ref(tenant_id=tenant_id, call_id=call_id)

    def _complete_execute_prerequisites(
        self,
        *,
        tenant_id: str,
        owner: str,
        prerequisites: _ExecutePrerequisiteResult,
        result_ref: str,
    ) -> None:
        assert self._infrastructure_unit_of_work_factory is not None
        with self._infrastructure_unit_of_work_factory(tenant_id) as repo:
            repo.complete_idempotency(
                scope=prerequisites.idempotency_scope,
                key=prerequisites.idempotency_key,
                owner=owner,
                generation=prerequisites.idempotency_generation,
                result_ref=result_ref,
            )



    def escalate_due_reconciliations(self, *, tenant_id: str, now: datetime | None = None) -> int:
        with self._unit_of_work_factory() as repo:
            return repo.escalate_due_reconciliations(
                tenant_id=tenant_id,
                now=now or datetime.now(tz=UTC),
            )

    def timeout_due_async_jobs(self, *, tenant_id: str, now: datetime | None = None) -> int:
        with self._unit_of_work_factory() as repo:
            return repo.timeout_due_async_jobs(
                tenant_id=tenant_id,
                now=now or datetime.now(tz=UTC),
            )

    def record_async_callback(
        self,
        *,
        tenant_id: str,
        async_job_id: str,
        provider_job_id: str,
        callback_order: int,
        callback_payload: dict[str, Any],
        expected_binding_ref: str,
        provided_binding_ref: str,
    ) -> None:
        with self._unit_of_work_factory() as repo:
            latest_order = repo.latest_async_callback_order(async_job_id=async_job_id)
            if expected_binding_ref != provided_binding_ref:
                authenticity_status = "FORGED"
            elif callback_order <= latest_order:
                authenticity_status = "REPLAY"
            elif callback_order != latest_order + 1:
                authenticity_status = "OUT_OF_ORDER"
            else:
                authenticity_status = "VERIFIED"
            accepted = authenticity_status == "VERIFIED"
            accepted = repo.record_async_callback(
                ToolAsyncCallbackInput(
                    callback_id=f"tool-async-callback:{provider_job_id}:{callback_order}",
                    tenant_id=tenant_id,
                    async_job_id=async_job_id,
                    provider_job_id=provider_job_id,
                    callback_order=callback_order,
                    authenticity_status=authenticity_status,
                    accepted=accepted,
                    callback_payload=callback_payload,
                )
            )
            if accepted:
                state = str(callback_payload.get("state") or callback_payload.get("status") or "").lower()
                repo.advance_async_job_after_callback(
                    async_job_id=async_job_id,
                    callback_order=callback_order,
                    completed=state in {"done", "completed", "succeeded", "success"},
                )

    def record_cancellation_request(
        self,
        *,
        tenant_id: str,
        prepared_id: str,
        attempt_id: str,
        async_job_id: str | None,
        provider_job_id: str,
        requested_by_principal_id: str,
        audit_requirement_id: str,
    ) -> None:
        payload = {
            "provider_job_id": provider_job_id,
            "status": "NOT_GUARANTEED",
            "external_effect_revoked": False,
            "requested_by_principal_id": requested_by_principal_id,
            "audit_requirement_id": audit_requirement_id,
        }
        with self._unit_of_work_factory() as repo:
            repo.record_cancellation_receipt(
                ToolCancellationReceiptInput(
                    cancellation_receipt_id=f"tool-cancellation-receipt:{provider_job_id}",
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    attempt_id=attempt_id,
                    async_job_id=async_job_id,
                    provider_job_id=provider_job_id,
                    status="NOT_GUARANTEED",
                    external_effect_revoked=False,
                    requested_by_principal_id=requested_by_principal_id,
                    audit_requirement_id=audit_requirement_id,
                    cancellation_payload=payload,
                )
            )
    def record_compensation_attempt(
        self,
        *,
        tenant_id: str,
        compensation_definition_id: str,
        compensation_attempt_id: str,
        source_effect_receipt_id: str | None,
        source_reconciliation_id: str | None,
        compensation_call_id: str,
        new_action_proposal_ref: str,
        operation_ref: str,
        compensation_capability: str,
        residual_impact: str,
        audit_requirement_id: str,
        idempotency_generation: int = 1,
    ) -> None:
        definition_payload = {
            "source_effect_receipt_id": source_effect_receipt_id,
            "source_reconciliation_id": source_reconciliation_id,
            "compensation_capability": compensation_capability,
            "operation_ref": operation_ref,
            "new_action_proposal_ref": new_action_proposal_ref,
            "requires_approval": True,
            "residual_impact": residual_impact,
            "hidden_rollback": False,
        }
        attempt_payload = {
            "compensation_definition_id": compensation_definition_id,
            "prepared_tool_action_id": f"prepared-tool-action:{compensation_call_id}",
            "attempt_id": f"tool-attempt:{compensation_call_id}",
            "execution_receipt_id": f"tool-execution-receipt:{compensation_call_id}",
            "status": "CONFIRMED",
            "hidden_rollback": False,
            "idempotency_scope": "tool-side-effect",
            "idempotency_key": compensation_call_id,
            "idempotency_generation": idempotency_generation,
            "audit_requirement_id": audit_requirement_id,
        }
        with self._unit_of_work_factory() as repo:
            repo.record_compensation_definition(
                ToolCompensationDefinitionInput(
                    compensation_definition_id=compensation_definition_id,
                    tenant_id=tenant_id,
                    source_effect_receipt_id=source_effect_receipt_id,
                    source_reconciliation_id=source_reconciliation_id,
                    compensation_capability=compensation_capability,
                    operation_ref=operation_ref,
                    new_action_proposal_ref=new_action_proposal_ref,
                    requires_approval=True,
                    window_deadline_at=datetime.now(tz=UTC) + timedelta(hours=24),
                    residual_impact=residual_impact,
                    policy_ref="compensation-policy:tool-runtime:phase16",
                    definition_payload=definition_payload,
                )
            )
            repo.record_compensation_attempt(
                ToolCompensationAttemptInput(
                    compensation_attempt_id=compensation_attempt_id,
                    tenant_id=tenant_id,
                    compensation_definition_id=compensation_definition_id,
                    prepared_tool_action_id=f"prepared-tool-action:{compensation_call_id}",
                    attempt_id=f"tool-attempt:{compensation_call_id}",
                    execution_receipt_id=f"tool-execution-receipt:{compensation_call_id}",
                    status="CONFIRMED",
                    hidden_rollback=False,
                    idempotency_scope="tool-side-effect",
                    idempotency_key=compensation_call_id,
                    idempotency_generation=idempotency_generation,
                    audit_requirement_id=audit_requirement_id,
                    attempt_payload=attempt_payload,
                )
            )

    def record_manual_effect_assessment(
        self,
        *,
        tenant_id: str,
        manual_assessment_id: str,
        reconciliation_id: str,
        provider_effect_id: str,
        conclusion: str,
        confidence: float,
        assessor_principal_id: str,
        residual_uncertainty: str,
        evidence_payload: dict[str, Any],
    ) -> None:
        with self._unit_of_work_factory() as repo:
            repo.record_manual_effect_assessment(
                ToolManualEffectAssessmentInput(
                    manual_assessment_id=manual_assessment_id,
                    tenant_id=tenant_id,
                    reconciliation_id=reconciliation_id,
                    provider_effect_id=provider_effect_id,
                    conclusion=conclusion,
                    confidence=confidence,
                    assessor_principal_id=assessor_principal_id,
                    residual_uncertainty=residual_uncertainty,
                    evidence_payload=evidence_payload,
                )
            )
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


def _effect_payload_from_result(*, result: Any, call_id: str) -> dict[str, Any]:
    native = result if isinstance(result, dict) else {"value": str(result)}
    provider_effect_id = str(native.get("provider_effect_id") or native.get("effect_id") or f"provider-effect:{call_id}")
    return {
        "provider_effect_id": provider_effect_id,
        "effect_status": "CONFIRMED",
        "effect_certainty": "CONFIRMED_EFFECT",
        "native_result": redact_sensitive_payload(native),
    }


def _async_job_payload_from_result(*, result: Any, call_id: str) -> dict[str, Any]:
    native = result if isinstance(result, dict) else {"value": str(result)}
    provider_job_id = str(native.get("provider_job_id") or native.get("job_id") or f"provider-job:{call_id}")
    return {
        "provider_job_id": provider_job_id,
        "async_status": "WAITING_CALLBACK",
        "effect_certainty": "UNKNOWN_EFFECT",
        "native_result": redact_sensitive_payload(native),
    }


def _sandbox_observation_reconciliation_payload(
    *,
    sandbox_result: SandboxExecutionResult,
    call_id: str,
) -> dict[str, Any]:
    return {
        "provider_effect_id": f"sandbox-observation:{call_id}",
        "effect_status": "UNKNOWN",
        "effect_certainty": "UNKNOWN_EFFECT",
        "reconciliation_id": f"tool-effect-reconciliation:{call_id}",
        "next_action": "RECONCILE",
        "reconciliation_query": redact_sensitive_payload(
            {
                "reason": "sandbox_observation_requires_effect_reconciliation",
                "sandbox_adapter_tier": sandbox_result.output_payload.get("sandbox_adapter_tier"),
                "session_ref": sandbox_result.output_payload.get("session_ref"),
                "exit_code": sandbox_result.exit_code,
                "stdout": sandbox_result.stdout,
                "stderr": sandbox_result.stderr,
                "output_payload": sandbox_result.output_payload,
            }
        ),
    }


def _redact_sandbox_execution_result(result: SandboxExecutionResult) -> SandboxExecutionResult:
    return SandboxExecutionResult(
        status=result.status,
        stdout=str(redact_sensitive_payload(result.stdout)),
        stderr=str(redact_sensitive_payload(result.stderr)),
        exit_code=result.exit_code,
        output_payload=redact_sensitive_payload(result.output_payload),
    )


def _unknown_effect_payload(*, exc: ToolEffectUnknownError, call_id: str) -> dict[str, Any]:
    return {
        "provider_effect_id": exc.provider_effect_id,
        "effect_status": "UNKNOWN",
        "effect_certainty": "UNKNOWN_EFFECT",
        "reconciliation_id": f"tool-effect-reconciliation:{call_id}",
        "next_action": "RECONCILE",
        "reconciliation_query": redact_sensitive_payload(exc.reconciliation_query),
    }


def _recovery_unknown_effect_payload_from_result(
    *,
    result: Any,
    effect_payload: dict[str, Any],
    call_id: str,
    exc: Exception,
) -> dict[str, Any]:
    provider_effect_id = str(
        effect_payload.get("provider_effect_id")
        or effect_payload.get("provider_job_id")
        or f"provider-effect:{call_id}"
    )
    recovery_query = {
        "reason": "post_dispatch_persistence_failure",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "result": redact_sensitive_payload(result if isinstance(result, dict) else {"value": str(result)}),
        "call_id": call_id,
    }
    return {
        "provider_effect_id": provider_effect_id,
        "effect_status": "UNKNOWN",
        "effect_certainty": "UNKNOWN_EFFECT",
        "reconciliation_id": f"tool-effect-reconciliation:{call_id}",
        "next_action": "RECONCILE",
        "reconciliation_query": redact_sensitive_payload(recovery_query),
    }


def _unknown_effect_payload_from_exception(*, exc: Exception, call_id: str) -> dict[str, Any]:
    reconciliation_query = {
        "reason": "provider_exception_after_dispatch_boundary",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "call_id": call_id,
    }
    return {
        "provider_effect_id": f"provider-effect:{call_id}:unknown",
        "effect_status": "UNKNOWN",
        "effect_certainty": "UNKNOWN_EFFECT",
        "reconciliation_id": f"tool-effect-reconciliation:{call_id}",
        "next_action": "RECONCILE",
        "reconciliation_query": redact_sensitive_payload(reconciliation_query),
    }
__all__ = ["ToolEffectUnknownError", "ToolGatewayReceipt", "ToolInvocationGateway"]
