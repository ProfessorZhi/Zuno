from __future__ import annotations

from collections.abc import Callable
import asyncio
import logging
from copy import deepcopy
from dataclasses import dataclass, field, replace
import hashlib
import json
import re
from threading import Thread
from typing import Any, Protocol
from uuid import uuid4

from zuno.capability.control_plane import (
    ApprovalGate,
    ExecutorAdapterContract,
    ExecutorRegistry,
    NormalizedToolResult,
    ToolApprovalDecision,
    ToolApprovalPolicy,
    ToolCardManifest,
    ToolExecutionMode,
    ToolResultNormalizer,
    ToolSideEffectLevel,
    ToolTrustTier,
)
from zuno.capability.tool_runtime.effect_policy import classify_tool_effect
from zuno.platform.security.governance import (
    SandboxAuditEvent,
    SecurityDecision,
    ToolSecurityGate,
    ToolSecurityProfile,
    redact_sensitive_payload,
    redact_sensitive_text,
)


ToolExecutor = Callable[["ToolExecutionContext"], Any]
LegacyToolExecutor = Callable[[dict[str, Any], "ToolExecutionContext"], Any]


class SecurityApprovalFactSink(Protocol):
    def record_tool_approval_fact(self, fact: dict[str, Any]) -> None:
        ...


LEGACY_APPROVAL_BOOLEAN_ADAPTER_ID = "temporary.adapter.tool_runtime.approved_bool"
LEGACY_APPROVAL_BOOLEAN_ADAPTER_REMOVAL_PHASE = "PHASE16"
WORKSPACE_APPROVAL_DECISION_REF_ADAPTER_ID = "workspace.approval_decision_ref"


@dataclass(frozen=True, slots=True)
class ToolRuntimeRequest:
    tool_id: str
    arguments: dict[str, Any]
    workspace_id: str
    user_id: str
    task_id: str
    trace_id: str
    model_intent: str
    approved: bool = False
    approval_decision_ref: str = ""
    approval_adapter_ref: str = ""
    approval_adapter_removal_phase: str = ""
    approval_comment: str = ""
    runtime_state: Any | None = None
    tool_request_id: str = field(default_factory=lambda: f"toolreq_{uuid4().hex[:12]}")
    approval_id: str = field(default_factory=lambda: f"approval_{uuid4().hex[:12]}")
    execution_id: str = ""


@dataclass(frozen=True, slots=True)
class CredentialGrant:
    policy: str
    credential_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "credential_refs": list(self.credential_refs),
        }


class InMemoryCredentialBroker:
    """Credential broker boundary for PHASE08.

    The broker returns references that an executor can resolve in its own
    sandbox. It never exposes raw secret values to trace or task events.
    """

    def __init__(self) -> None:
        self._secret_refs: dict[tuple[str, str, str], tuple[str, ...]] = {}

    def register_secret_ref(
        self,
        *,
        policy: str,
        workspace_id: str,
        user_id: str,
        secret_ref: str,
    ) -> None:
        if not _is_credential_ref(secret_ref):
            raise ValueError("credential broker only accepts credential reference URIs")
        key = (policy, workspace_id, user_id)
        self._secret_refs[key] = (*self._secret_refs.get(key, ()), secret_ref)

    def resolve(self, manifest: ToolCardManifest, request: ToolRuntimeRequest) -> CredentialGrant:
        policy = manifest.credential_policy
        if policy in {"", "none"}:
            return CredentialGrant(policy=policy)
        refs = self._secret_refs.get((policy, request.workspace_id, request.user_id))
        if refs is None:
            refs = (f"credref://{request.workspace_id}/{manifest.tool_id}",)
        return CredentialGrant(policy=policy, credential_refs=refs)


@dataclass(frozen=True, slots=True)
class NetworkPolicyDecision:
    policy: str
    allowed: bool
    reason: str
    requested_targets: tuple[str, ...] = ()
    allowed_targets: tuple[str, ...] = ()
    denied_targets: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "allowed": self.allowed,
            "reason": self.reason,
            "requested_targets": list(self.requested_targets),
            "allowed_targets": list(self.allowed_targets),
            "denied_targets": list(self.denied_targets),
        }


@dataclass(frozen=True, slots=True)
class ToolSandboxContext:
    tool_id: str
    adapter_id: str
    sandbox_profile: str
    network_policy: str
    credential_policy: str
    credential_refs: tuple[str, ...] = ()
    isolation_mode: str = "local_deterministic"
    real_isolation: bool = False
    target_isolation_profiles: tuple[str, ...] = ("rootless", "gvisor", "firecracker")
    network_policy_decision: NetworkPolicyDecision = field(
        default_factory=lambda: NetworkPolicyDecision(
            policy="deny",
            allowed=True,
            reason="no_network_requested",
        )
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "adapter_id": self.adapter_id,
            "sandbox_profile": self.sandbox_profile,
            "network_policy": self.network_policy,
            "credential_policy": self.credential_policy,
            "credential_refs": list(self.credential_refs),
            "isolation_mode": self.isolation_mode,
            "real_isolation": self.real_isolation,
            "target_isolation_profiles": list(self.target_isolation_profiles),
            "network_policy_decision": self.network_policy_decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class ToolExecutionContext:
    request: ToolRuntimeRequest
    manifest: ToolCardManifest
    adapter: ExecutorAdapterContract
    audit_ref: str
    sandbox_profile: str
    network_policy: str
    credential_policy: str
    credential_refs: tuple[str, ...] = ()


class SandboxPolicyEnforcer:
    def build_context(
        self,
        *,
        manifest: ToolCardManifest,
        adapter: ExecutorAdapterContract,
        credential_grant: CredentialGrant,
        request_arguments: dict[str, Any] | None = None,
    ) -> ToolSandboxContext:
        sandbox_profile = adapter.sandbox_profile or manifest.sandbox_profile
        network_policy = adapter.network_policy or manifest.network_policy
        credential_policy = adapter.credential_policy or manifest.credential_policy
        network_decision = self.evaluate_network_policy(
            policy=network_policy,
            arguments=request_arguments or {},
        )
        return ToolSandboxContext(
            tool_id=manifest.tool_id,
            adapter_id=adapter.adapter_id,
            sandbox_profile=sandbox_profile,
            network_policy=network_policy,
            credential_policy=credential_policy,
            credential_refs=credential_grant.credential_refs,
            network_policy_decision=network_decision,
        )

    def evaluate_network_policy(
        self,
        *,
        policy: str,
        arguments: dict[str, Any],
    ) -> NetworkPolicyDecision:
        targets = tuple(_network_targets(arguments))
        normalized_policy = str(policy or "deny").strip().lower()
        if not targets:
            return NetworkPolicyDecision(
                policy=normalized_policy,
                allowed=True,
                reason="no_network_requested",
            )
        if normalized_policy in {"deny", "deny_by_default"}:
            return NetworkPolicyDecision(
                policy=normalized_policy,
                allowed=False,
                reason="network_egress_denied",
                requested_targets=targets,
                denied_targets=targets,
            )
        if normalized_policy == "egress_mail_only":
            denied = tuple(target for target in targets if not _is_mail_target(target))
            return NetworkPolicyDecision(
                policy=normalized_policy,
                allowed=not denied,
                reason="network_policy_allowed" if not denied else "network_egress_denied",
                requested_targets=targets,
                allowed_targets=tuple(target for target in targets if target not in denied),
                denied_targets=denied,
            )
        return NetworkPolicyDecision(
            policy=normalized_policy,
            allowed=True,
            reason="network_policy_allowed",
            requested_targets=targets,
            allowed_targets=targets,
        )


@dataclass(frozen=True, slots=True)
class ToolRuntimeExecutionResult:
    tool_id: str
    status: str
    approval_required: bool
    security_decision: str
    approval_decision: dict[str, Any]
    audit_event: SandboxAuditEvent
    sandbox_context: ToolSandboxContext
    normalized_result: NormalizedToolResult | None = None
    task_events: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    tool_request_id: str = ""
    approval_id: str = ""
    tool_execution_id: str = ""
    tool_result_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "tool_request_id": self.tool_request_id,
            "approval_id": self.approval_id,
            "tool_execution_id": self.tool_execution_id,
            "tool_result_id": self.tool_result_id,
            "status": self.status,
            "approval_required": self.approval_required,
            "security_decision": self.security_decision,
            "approval_decision": dict(self.approval_decision),
            "audit_event": self.audit_event.to_trace_payload(),
            "sandbox_context": self.sandbox_context.to_dict(),
            "normalized_result": self.normalized_result.to_dict()
            if self.normalized_result is not None
            else None,
            "task_events": [dict(event) for event in self.task_events],
        }


class ToolControlPlaneRuntime:
    def __init__(
        self,
        *,
        credential_broker: InMemoryCredentialBroker | None = None,
        sandbox_enforcer: SandboxPolicyEnforcer | None = None,
        security_approval_sink: SecurityApprovalFactSink | None = None,
        tool_unit_of_work_factory: Callable[[], Any] | None = None,
        security_unit_of_work_factory: Callable[[], Any] | None = None,
        infrastructure_unit_of_work_factory: Callable[[str], Any] | None = None,
        readonly_cutover_only: bool = False,
    ) -> None:
        self._manifests: dict[str, ToolCardManifest] = {}
        self._executor_registry = ExecutorRegistry()
        self._executors: dict[str, LegacyToolExecutor] = {}
        self._credential_broker = credential_broker or InMemoryCredentialBroker()
        self._sandbox_enforcer = sandbox_enforcer or SandboxPolicyEnforcer()
        self._security_approval_sink = security_approval_sink
        self._tool_unit_of_work_factory = tool_unit_of_work_factory
        self._security_unit_of_work_factory = security_unit_of_work_factory
        self._infrastructure_unit_of_work_factory = infrastructure_unit_of_work_factory
        self._readonly_cutover_only = readonly_cutover_only
        self._approval_gate = ApprovalGate()
        self._tool_gate = ToolSecurityGate()
        self._approval_ledger: list[dict[str, Any]] = []

    def register_manifest(self, manifest: ToolCardManifest) -> None:
        self._manifests[manifest.tool_id] = manifest

    def get_manifest(self, tool_id: str) -> ToolCardManifest | None:
        return self._manifests.get(tool_id)

    def set_credential_broker(self, credential_broker: InMemoryCredentialBroker) -> None:
        self._credential_broker = credential_broker

    def approval_ledger(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(entry) for entry in self._approval_ledger)

    def register_executor_adapter(
        self,
        adapter: ExecutorAdapterContract,
        executor: LegacyToolExecutor | ToolExecutor,
    ) -> None:
        self._executor_registry.register(adapter)
        self._executors[adapter.adapter_id] = _normalize_executor(executor)

    def execute(self, request: ToolRuntimeRequest) -> ToolRuntimeExecutionResult:
        manifest = self._require_manifest(request.tool_id)
        adapter = self._executor_registry.select_executor(manifest)
        profile = ToolSecurityProfile.from_tool_card(
            tool_id=manifest.tool_id,
            side_effect_level=manifest.side_effect_level.value,
            execution_mode=manifest.execution_mode.value,
        )
        gate_result = self._tool_gate.evaluate(
            profile=profile,
            model_intent=request.model_intent,
            proposed_args=request.arguments,
            workspace_id=request.workspace_id,
            trace_id=request.trace_id,
            task_id=request.task_id,
        )
        approval_decision = self._approval_gate.evaluate(
            manifest,
            runtime_state=request.runtime_state,
        )
        credential_grant = self._credential_broker.resolve(manifest, request)
        sandbox_context = self._sandbox_enforcer.build_context(
            manifest=manifest,
            adapter=adapter,
            credential_grant=credential_grant,
            request_arguments=request.arguments,
        )

        if manifest.approval_policy is ToolApprovalPolicy.DISABLED:
            audit_event = replace(
                gate_result.audit_event,
                policy_decision=SecurityDecision.BLOCK,
                final_decision="blocked",
            )
            events = self._events_for_blocked(
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                reason=approval_decision.reason or "tool_disabled",
            )
            self._record_security_approval_fact(
                status="failed_closed_before_effect",
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                security_decision=SecurityDecision.BLOCK.value,
                approval_decision=approval_decision.to_dict(),
            )
            return ToolRuntimeExecutionResult(
                tool_id=manifest.tool_id,
                status="blocked",
                approval_required=False,
                security_decision=SecurityDecision.BLOCK.value,
                approval_decision=approval_decision.to_dict(),
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                task_events=events,
                tool_request_id=request.tool_request_id,
                approval_id=request.approval_id,
            )

        if not sandbox_context.network_policy_decision.allowed:
            audit_event = replace(
                gate_result.audit_event,
                policy_decision=SecurityDecision.BLOCK,
                final_decision="blocked",
                risk_reasons=[
                    *gate_result.audit_event.risk_reasons,
                    sandbox_context.network_policy_decision.reason,
                ],
            )
            events = self._events_for_blocked(
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                reason=sandbox_context.network_policy_decision.reason,
            )
            self._record_security_approval_fact(
                status="failed_closed_before_effect",
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                security_decision=SecurityDecision.BLOCK.value,
                approval_decision=approval_decision.to_dict(),
            )
            return ToolRuntimeExecutionResult(
                tool_id=manifest.tool_id,
                status="blocked",
                approval_required=False,
                security_decision=SecurityDecision.BLOCK.value,
                approval_decision=approval_decision.to_dict(),
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                task_events=events,
                tool_request_id=request.tool_request_id,
                approval_id=request.approval_id,
            )

        if self._readonly_cutover_only and manifest.side_effect_level not in {
            ToolSideEffectLevel.NONE,
            ToolSideEffectLevel.READ,
        }:
            audit_event = replace(
                gate_result.audit_event,
                policy_decision=SecurityDecision.BLOCK,
                final_decision="blocked",
                risk_reasons=[
                    *gate_result.audit_event.risk_reasons,
                    "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
                ],
            )
            events = self._events_for_blocked(
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                reason="PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
            )
            self._record_security_approval_fact(
                status="failed_closed_before_effect",
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                security_decision=SecurityDecision.BLOCK.value,
                approval_decision=approval_decision.to_dict(),
            )
            result = ToolRuntimeExecutionResult(
                tool_id=manifest.tool_id,
                status="blocked",
                approval_required=False,
                security_decision=SecurityDecision.BLOCK.value,
                approval_decision=approval_decision.to_dict(),
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                task_events=events,
                tool_request_id=request.tool_request_id,
                approval_id=request.approval_id,
            )
            self._record_tool_runtime_facts(
                request=request,
                manifest=manifest,
                adapter=adapter,
                result=result,
                attempt_status="FAILED",
                dispatch_certainty="NOT_DISPATCHED",
                effect_certainty="NO_EFFECT",
                observation_payload={"blocked": True, "reason": "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL"},
            )
            return result

        requires_approval = (
            gate_result.decision is SecurityDecision.REQUIRE_APPROVAL
            or approval_decision.approval_required
        )
        if requires_approval and not request.approved:
            audit_event = replace(gate_result.audit_event, final_decision="pending")
            events = self._events_for_pending_approval(
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                approval_decision=approval_decision.to_dict(),
            )
            self._record_approval_ledger(
                status="approval_waiting",
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
            )
            self._record_security_approval_fact(
                status="approval_waiting",
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                security_decision=gate_result.decision.value,
                approval_decision=approval_decision.to_dict(),
            )
            return ToolRuntimeExecutionResult(
                tool_id=manifest.tool_id,
                status="approval_required",
                approval_required=True,
                security_decision=gate_result.decision.value,
                approval_decision=approval_decision.to_dict(),
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                task_events=events,
                tool_request_id=request.tool_request_id,
                approval_id=request.approval_id,
            )

        audit_event = replace(
            gate_result.audit_event,
            final_decision="approved" if request.approved or requires_approval else "approved",
        )
        if request.approved or requires_approval:
            self._record_security_approval_fact(
                status="approved_before_effect",
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                security_decision=gate_result.decision.value,
                approval_decision=approval_decision.to_dict(),
            )
        execution_id = request.execution_id or f"toolexec_{uuid4().hex[:12]}"
        result_id = f"toolres_{execution_id.removeprefix('toolexec_')}"
        execution_context = ToolExecutionContext(
            request=request,
            manifest=manifest,
            adapter=adapter,
            audit_ref=audit_event.audit_id,
            sandbox_profile=sandbox_context.sandbox_profile,
            network_policy=sandbox_context.network_policy,
            credential_policy=sandbox_context.credential_policy,
            credential_refs=sandbox_context.credential_refs,
        )
        used_gateway = False
        if self._should_use_side_effect_gateway(manifest):
            raw_result, gateway_status, gateway_blocked_reason = self._invoke_side_effect_gateway(
                request=request,
                manifest=manifest,
                adapter=adapter,
                execution_context=execution_context,
                sandbox_context=sandbox_context,
            )
            used_gateway = True
            if gateway_status not in {"completed", "replayed"}:
                events = self._events_for_blocked(
                    request=request,
                    manifest=manifest,
                    audit_event=audit_event,
                    sandbox_context=sandbox_context,
                    reason=gateway_blocked_reason or gateway_status,
                )
                return ToolRuntimeExecutionResult(
                    tool_id=manifest.tool_id,
                    status=gateway_status,
                    approval_required=False,
                    security_decision=SecurityDecision.BLOCK.value,
                    approval_decision=approval_decision.to_dict(),
                    audit_event=audit_event,
                    sandbox_context=sandbox_context,
                    task_events=events,
                    tool_request_id=request.tool_request_id,
                    approval_id=request.approval_id,
                    tool_execution_id=execution_id,
                    tool_result_id=result_id,
                )
        else:
            try:
                raw_result = self._executors[adapter.adapter_id](request.arguments, execution_context)
            except Exception as exc:
                # A tool implementation failure must become a failed run
                # observation (retryable by plan), never a crash of the run
                # graph or a fallback to another runtime.
                logging.getLogger(__name__).warning(
                    f"tool executor failed for {manifest.tool_id}: {type(exc).__name__}: {exc}"
                )
                return self._build_failed_execution_result(
                    request=request,
                    manifest=manifest,
                    adapter=adapter,
                    audit_event=audit_event,
                    sandbox_context=sandbox_context,
                    approval_decision=approval_decision,
                    error=exc,
                )
        normalized = ToolResultNormalizer.normalize(
            tool_id=manifest.tool_id,
            raw_result=raw_result,
            trace_span_id=f"span_tool_{request.trace_id}_{execution_id}",
            audit_ref=audit_event.audit_id,
        )
        events = self._events_for_completed(
            request=request,
            manifest=manifest,
            audit_event=audit_event,
            sandbox_context=sandbox_context,
            normalized=normalized,
            execution_id=execution_id,
            result_id=result_id,
        )
        if request.approved or manifest.requires_approval:
            self._record_approval_ledger(
                status="approved_executed",
                request=request,
                manifest=manifest,
                audit_event=audit_event,
                sandbox_context=sandbox_context,
            )
        result = ToolRuntimeExecutionResult(
            tool_id=manifest.tool_id,
            status="completed",
            approval_required=False,
            security_decision=SecurityDecision.ALLOW.value,
            approval_decision=approval_decision.to_dict(),
            audit_event=audit_event,
            sandbox_context=sandbox_context,
            normalized_result=normalized,
            task_events=events,
            tool_request_id=request.tool_request_id,
            approval_id=request.approval_id,
            tool_execution_id=execution_id,
            tool_result_id=result_id,
        )
        if not used_gateway:
            self._record_tool_runtime_facts(
                request=request,
                manifest=manifest,
                adapter=adapter,
                result=result,
                attempt_status="SUCCEEDED",
                dispatch_certainty="DISPATCHED",
                effect_certainty=(
                    "NO_EFFECT"
                    if manifest.side_effect_level in {ToolSideEffectLevel.NONE, ToolSideEffectLevel.READ}
                    else "CONFIRMED_EFFECT"
                ),
                observation_payload=normalized.to_dict(),
            )
        return result

    def _should_use_side_effect_gateway(self, manifest: ToolCardManifest) -> bool:
        return (
            manifest.side_effect_level not in {ToolSideEffectLevel.NONE, ToolSideEffectLevel.READ}
            and self._tool_unit_of_work_factory is not None
            and self._security_unit_of_work_factory is not None
            and self._infrastructure_unit_of_work_factory is not None
        )

    def _invoke_side_effect_gateway(
        self,
        *,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        adapter: ExecutorAdapterContract,
        execution_context: ToolExecutionContext,
        sandbox_context: ToolSandboxContext,
    ) -> tuple[Any | None, str, str]:
        from zuno.capability.tool_runtime import ToolInvocationGateway

        gateway_args = dict(request.arguments)
        if sandbox_context.credential_refs and "secret_ref" not in gateway_args:
            gateway_args["secret_ref"] = sandbox_context.credential_refs[0]
        secret_ref = str(gateway_args.get("secret_ref") or "")
        if secret_ref:
            assert self._security_unit_of_work_factory is not None
            with self._security_unit_of_work_factory() as repo:
                repo.record_secret_ref(
                    secret_ref=secret_ref,
                    tenant_id=request.user_id,
                    credential_version_ref=f"credential-version:{manifest.tool_id}:default",
                    audience=f"tool:{manifest.tool_id}",
                    owner_principal_id=f"workspace-user:{request.workspace_id}",
                    scope={"tool": manifest.tool_id, "workspace_id": request.workspace_id},
                )

        gateway = ToolInvocationGateway(
            unit_of_work_factory=self._tool_unit_of_work_factory,
            security_unit_of_work_factory=self._security_unit_of_work_factory,
            infrastructure_unit_of_work_factory=self._infrastructure_unit_of_work_factory,
        )

        async def executor() -> Any:
            return self._executors[adapter.adapter_id](gateway_args, execution_context)

        result, receipt = _run_gateway_coroutine(
            gateway.invoke_readonly(
                tool_name=manifest.tool_id,
                args=gateway_args,
                tenant_id=request.user_id,
                workspace_id=request.workspace_id,
                trace_id=request.trace_id,
                call_id=request.execution_id or request.tool_request_id,
                adapter_kind=adapter.execution_mode.value.upper(),
                executor=executor,
                readonly=False,
                approved=request.approved,
            )
        )
        return result, receipt.status, receipt.blocked_reason

    def _record_tool_runtime_facts(
        self,
        *,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        adapter: ExecutorAdapterContract,
        result: ToolRuntimeExecutionResult,
        attempt_status: str,
        dispatch_certainty: str,
        effect_certainty: str,
        observation_payload: dict[str, Any],
    ) -> None:
        if self._tool_unit_of_work_factory is None:
            return
        from zuno.platform.database.tool_runtime import (
            PreparedToolActionInput,
            ToolAttemptInput,
            ToolExecutionReceiptInput,
            ToolObservationInput,
            ToolVersionInput,
        )

        tenant_id = request.user_id or "tenant:default"
        workspace_id = request.workspace_id or "workspace:default"
        tool_version_id = f"tool-version:{manifest.tool_id}:v1"
        tool_operation_id = f"{tool_version_id}:operation:default"
        prepared_id = f"prepared-tool-action:{request.execution_id or request.tool_request_id}"
        attempt_id = f"tool-attempt:{request.execution_id or request.tool_request_id}"
        receipt_id = f"tool-execution-receipt:{request.execution_id or request.tool_request_id}"
        observation_id = f"tool-observation:{request.execution_id or request.tool_request_id}"
        effect_policy = classify_tool_effect(
            tool_name=manifest.tool_id,
            args=request.arguments,
            side_effect_level=manifest.side_effect_level.value,
            adapter_kind=adapter.execution_mode.value,
        )
        with self._tool_unit_of_work_factory() as repo:
            repo.publish_tool_version(
                ToolVersionInput(
                    tool_definition_id=f"tool-definition:{manifest.tool_id}",
                    tool_version_id=tool_version_id,
                    tenant_id=tenant_id,
                    version_no=1,
                    input_schema=manifest.input_schema,
                    output_schema=manifest.output_schema,
                    adapter_kind=adapter.execution_mode.value,
                    effect_level=effect_policy.effect_level,
                )
            )
            repo.record_adapter_binding(
                adapter_binding_id=f"tool-adapter-binding:{adapter.adapter_id}:{tool_version_id}",
                tenant_id=tenant_id,
                tool_version_id=tool_version_id,
                adapter_kind=adapter.execution_mode.value,
                adapter_version=f"{adapter.adapter_id}:v1",
                conformance_payload={
                    "adapter_id": adapter.adapter_id,
                    "timeout_seconds": adapter.timeout_seconds,
                    "network_policy": adapter.network_policy,
                    "sandbox_profile": adapter.sandbox_profile,
                    "effect_policy_version": effect_policy.policy_version,
                    "effect_policy_hash": effect_policy.policy_hash,
                },
            )
            repo.install_tool(
                tool_installation_id=f"tool-installation:{workspace_id}:{manifest.tool_id}",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                tool_version_id=tool_version_id,
                policy_ref=f"tool-policy:{manifest.tool_id}:phase15",
            )
            repo.activate_tool(
                tool_activation_id=f"tool-activation:{workspace_id}:{manifest.tool_id}",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                tool_installation_id=f"tool-installation:{workspace_id}:{manifest.tool_id}",
                expected_generation=1,
                activation_payload={
                    "runtime": "ToolInvocationGateway",
                    "phase": "PHASE16",
                    "effect_policy_version": effect_policy.policy_version,
                    "effect_policy_hash": effect_policy.policy_hash,
                },
            )
            repo.prepare_action(
                PreparedToolActionInput(
                    prepared_tool_action_id=prepared_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    tool_operation_id=tool_operation_id,
                    canonical_args=redact_sensitive_payload(request.arguments),
                    target_resources=effect_policy.target_resource_set.resource_refs,
                    effect_level=effect_policy.effect_level,
                    approval_required=effect_policy.approval_required or result.approval_required,
                    idempotency_key=request.execution_id or request.tool_request_id,
                    security_epoch_ref=f"security-epoch:{request.trace_id}",
                    effect_policy_version=effect_policy.policy_version,
                    effect_policy_hash=effect_policy.policy_hash,
                    target_resource_set_ref=effect_policy.target_resource_set.resource_set_ref,
                    target_conflict_keys=effect_policy.target_resource_set.conflict_keys,
                    action_proposal_ref=f"action-proposal:{request.task_id}:{request.tool_request_id}",
                    status="READY" if result.status == "completed" else "OBSOLETE",
                )
            )
            repo.record_attempt(
                ToolAttemptInput(
                    attempt_id=attempt_id,
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    status=attempt_status,
                    dispatch_certainty=dispatch_certainty,
                    adapter_family=adapter.execution_mode.value.upper(),
                    hidden_retry_count=0,
                    state_history=("STARTED", attempt_status),
                )
            )
            repo.record_observation(
                ToolObservationInput(
                    observation_id=observation_id,
                    tenant_id=tenant_id,
                    attempt_id=attempt_id,
                    owner_module="08 Tool Runtime",
                    normalized_projection_owner="06 Agent Core / Planning & Control",
                    output_trusted=False,
                    schema_valid=result.status == "completed",
                    memory_write_allowed=False,
                    evidence_write_allowed=False,
                    payload=observation_payload,
                )
            )
            repo.record_execution_receipt(
                ToolExecutionReceiptInput(
                    receipt_id=receipt_id,
                    tenant_id=tenant_id,
                    prepared_tool_action_id=prepared_id,
                    attempt_id=attempt_id,
                    status=attempt_status,
                    dispatch_certainty=dispatch_certainty,
                    effect_certainty=effect_certainty,
                    append_only_generation=1,
                    receipt_payload={
                        "status": result.status,
                        "tool_request_id": result.tool_request_id,
                        "tool_execution_id": result.tool_execution_id,
                        "tool_result_id": result.tool_result_id,
                    },
                )
            )
            repo.record_bypass_guard(
                receipt_id=f"tool-bypass-guard:{request.execution_id or request.tool_request_id}",
                tenant_id=tenant_id,
                scope="default_readonly_tool_runtime",
                allowlist_count=0,
                guard_payload={"default_path": "ToolInvocationGateway", "direct_execution": False},
            )

    def _require_manifest(self, tool_id: str) -> ToolCardManifest:
        manifest = self._manifests.get(tool_id)
        if manifest is None:
            raise KeyError(f"unknown tool manifest: {tool_id}")
        return manifest

    @staticmethod
    def _tool_call_event(
        *,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        sandbox_context: ToolSandboxContext,
        status: str,
    ) -> dict[str, Any]:
        return {
            "type": "tool_call",
            "status": status,
            "payload": {
                "status": status,
                "tool_request_id": request.tool_request_id,
                "approval_id": request.approval_id,
                "tool_id": manifest.tool_id,
                "adapter_id": sandbox_context.adapter_id,
                "model_intent": request.model_intent,
                "arguments": redact_sensitive_payload(request.arguments),
                "side_effect_level": manifest.side_effect_level.value,
                "approval_required": manifest.requires_approval,
                "sandbox": sandbox_context.to_dict(),
            },
        }

    @staticmethod
    def _sandbox_audit_event(
        *,
        audit_event: SandboxAuditEvent,
        sandbox_context: ToolSandboxContext,
        status: str,
    ) -> dict[str, Any]:
        return {
            "type": "sandbox_audit",
            "status": status,
            "payload": {
                "status": status,
                "audit_ref": audit_event.audit_id,
                "audit": audit_event.to_trace_payload(),
                "sandbox": sandbox_context.to_dict(),
            },
        }

    def _events_for_pending_approval(
        self,
        *,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        audit_event: SandboxAuditEvent,
        sandbox_context: ToolSandboxContext,
        approval_decision: dict[str, Any],
    ) -> tuple[dict[str, Any], ...]:
        return (
            self._tool_call_event(
                request=request,
                manifest=manifest,
                sandbox_context=sandbox_context,
                status="approval_waiting",
            ),
            self._sandbox_audit_event(
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                status="approval_waiting",
            ),
            {
                "type": "approval_required",
                "status": "approval_waiting",
                "payload": {
                    "status": "approval_waiting",
                    "tool_request_id": request.tool_request_id,
                    "approval_id": request.approval_id,
                    "tool_id": manifest.tool_id,
                    "required_approval": f"tool:{manifest.tool_id}",
                    "approval_decision": approval_decision,
                    "audit_ref": audit_event.audit_id,
                },
            },
        )

    def _events_for_completed(
        self,
        *,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        audit_event: SandboxAuditEvent,
        sandbox_context: ToolSandboxContext,
        normalized: NormalizedToolResult,
        execution_id: str,
        result_id: str,
    ) -> tuple[dict[str, Any], ...]:
        return (
            self._tool_call_event(
                request=request,
                manifest=manifest,
                sandbox_context=sandbox_context,
                status="running",
            ),
            self._sandbox_audit_event(
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                status="running",
            ),
            {
                "type": "tool_result",
                "status": normalized.status,
                "payload": {
                    "status": normalized.status,
                    "tool_request_id": request.tool_request_id,
                    "approval_id": request.approval_id,
                    "tool_execution_id": execution_id,
                    "tool_result_id": result_id,
                    "tool_id": manifest.tool_id,
                    "result": normalized.to_dict(),
                    "audit_ref": audit_event.audit_id,
                    "credential_refs": list(sandbox_context.credential_refs),
                    "security_decision": SecurityDecision.ALLOW.value,
                },
            },
        )

    def _build_failed_execution_result(
        self,
        *,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        adapter: ExecutorAdapterContract,
        audit_event: SandboxAuditEvent,
        sandbox_context: ToolSandboxContext,
        approval_decision: ToolApprovalDecision,
        error: Exception,
    ) -> ToolRuntimeExecutionResult:
        """Convert a tool implementation exception into a failed observation.

        PHASE22 workspace-agent cutover: a failing tool marks the step failed
        (retryable by plan); it never crashes the run graph and never triggers
        a fallback to another runtime.
        """
        execution_id = f"exec_{request.trace_id}_{uuid4().hex[:8]}"
        result_id = f"tool_result_{execution_id}"
        failure_reason = f"{type(error).__name__}: {error}"
        events = (
            self._tool_call_event(
                request=request,
                manifest=manifest,
                sandbox_context=sandbox_context,
                status="failed",
            ),
            self._sandbox_audit_event(
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                status="failed",
            ),
            {
                "type": "tool_result",
                "status": "failed",
                "payload": {
                    "status": "failed",
                    "tool_request_id": request.tool_request_id,
                    "approval_id": request.approval_id,
                    "tool_execution_id": execution_id,
                    "tool_result_id": result_id,
                    "tool_id": manifest.tool_id,
                    "failure_reason": failure_reason,
                    "audit_ref": audit_event.audit_id,
                    "credential_refs": list(sandbox_context.credential_refs),
                    "security_decision": SecurityDecision.ALLOW.value,
                },
            },
        )
        try:
            self._record_tool_runtime_facts(
                request=request,
                manifest=manifest,
                adapter=adapter,
                result=ToolRuntimeExecutionResult(
                    tool_id=manifest.tool_id,
                    status="failed",
                    approval_required=False,
                    security_decision=SecurityDecision.ALLOW.value,
                    approval_decision=approval_decision.to_dict(),
                    audit_event=audit_event,
                    sandbox_context=sandbox_context,
                    task_events=events,
                    tool_request_id=request.tool_request_id,
                    approval_id=request.approval_id,
                    tool_execution_id=execution_id,
                    tool_result_id=result_id,
                ),
                attempt_status="FAILED",
                dispatch_certainty="DISPATCHED",
                effect_certainty="NO_EFFECT",
                observation_payload={"failure_reason": failure_reason},
            )
        except Exception as facts_exc:  # telemetry write must not mask the failure
            logging.getLogger(__name__).warning(
                f"tool failure facts recording skipped for {manifest.tool_id}: {type(facts_exc).__name__}"
            )
        return ToolRuntimeExecutionResult(
            tool_id=manifest.tool_id,
            status="failed",
            approval_required=False,
            security_decision=SecurityDecision.ALLOW.value,
            approval_decision=approval_decision.to_dict(),
            audit_event=audit_event,
            sandbox_context=sandbox_context,
            task_events=events,
            tool_request_id=request.tool_request_id,
            approval_id=request.approval_id,
            tool_execution_id=execution_id,
            tool_result_id=result_id,
        )

    def _events_for_blocked(
        self,
        *,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        audit_event: SandboxAuditEvent,
        sandbox_context: ToolSandboxContext,
        reason: str,
    ) -> tuple[dict[str, Any], ...]:
        return (
            self._tool_call_event(
                request=request,
                manifest=manifest,
                sandbox_context=sandbox_context,
                status="blocked",
            ),
            self._sandbox_audit_event(
                audit_event=audit_event,
                sandbox_context=sandbox_context,
                status="blocked",
            ),
            {
                "type": "tool_result",
                "status": "blocked",
                "payload": {
                    "status": "blocked",
                    "tool_request_id": request.tool_request_id,
                    "approval_id": request.approval_id,
                    "tool_id": manifest.tool_id,
                    "error": reason,
                    "audit_ref": audit_event.audit_id,
                    "security_decision": SecurityDecision.BLOCK.value,
                },
            },
        )

    def _record_approval_ledger(
        self,
        *,
        status: str,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        audit_event: SandboxAuditEvent,
        sandbox_context: ToolSandboxContext,
    ) -> None:
        self._approval_ledger.append(
            {
                "status": status,
                "tool_id": manifest.tool_id,
                "tool_request_id": request.tool_request_id,
                "approval_id": request.approval_id,
                "approval_decision_ref": _approval_decision_ref(request),
                "approval_adapter_ref": _approval_adapter_ref(request),
                "approval_adapter_removal_phase": _approval_adapter_removal_phase(request),
                "task_id": request.task_id,
                "trace_id": request.trace_id,
                "required_approval": f"tool:{manifest.tool_id}",
                "approval_comment": _redact_approval_comment(request.approval_comment),
                "audit_ref": audit_event.audit_id,
                "credential_refs": list(sandbox_context.credential_refs),
                "sandbox": sandbox_context.to_dict(),
            }
        )

    def _record_security_approval_fact(
        self,
        *,
        status: str,
        request: ToolRuntimeRequest,
        manifest: ToolCardManifest,
        audit_event: SandboxAuditEvent,
        sandbox_context: ToolSandboxContext,
        security_decision: str,
        approval_decision: dict[str, Any],
    ) -> None:
        if self._security_approval_sink is None:
            return
        redacted_arguments = redact_sensitive_payload(request.arguments)
        fact = {
            "status": status,
            "tool_id": manifest.tool_id,
            "tool_request_id": request.tool_request_id,
            "approval_id": request.approval_id,
            "approval_decision_ref": _approval_decision_ref(request),
            "approval_adapter_ref": _approval_adapter_ref(request),
            "approval_adapter_removal_phase": _approval_adapter_removal_phase(request),
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
            "task_id": request.task_id,
            "trace_id": request.trace_id,
            "required_approval": f"tool:{manifest.tool_id}",
            "prepared_action_hash": _hash_payload(
                {
                    "tool_id": manifest.tool_id,
                    "arguments": redacted_arguments,
                    "workspace_id": request.workspace_id,
                    "task_id": request.task_id,
                    "execution_id": request.execution_id,
                }
            ),
            "security_decision": security_decision,
            "approval_decision": approval_decision,
            "approval_comment": _redact_approval_comment(request.approval_comment),
            "audit_ref": audit_event.audit_id,
            "credential_refs": list(sandbox_context.credential_refs),
            "sandbox": sandbox_context.to_dict(),
        }
        self._security_approval_sink.record_tool_approval_fact(fact)


def build_default_tool_control_plane_runtime(
    *,
    security_approval_sink: SecurityApprovalFactSink | None = None,
) -> ToolControlPlaneRuntime:
    from zuno.platform.database import engine
    from zuno.platform.database.foundation import InfrastructureUnitOfWork
    from zuno.platform.database.tool_runtime import ToolUnitOfWork
    from zuno.platform.security import SecurityUnitOfWork

    runtime = ToolControlPlaneRuntime(
        security_approval_sink=security_approval_sink,
        tool_unit_of_work_factory=lambda: ToolUnitOfWork(engine),
        security_unit_of_work_factory=lambda: SecurityUnitOfWork(engine),
        infrastructure_unit_of_work_factory=lambda tenant: InfrastructureUnitOfWork(engine, tenant_id=tenant),
        readonly_cutover_only=False,
    )

    runtime.register_manifest(
        ToolCardManifest(
            tool_id="filesystem.read",
            owner="capability.tools.filesystem",
            capability_domain="filesystem",
            description_for_model="Read a workspace-scoped file.",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.READ,
            approval_policy=ToolApprovalPolicy.AUTO,
            sandbox_profile="workspace_ro",
            credential_policy="none",
            network_policy="deny",
            audit_policy="trace",
            budget={"timeout_seconds": 3},
            executor_adapter="local.filesystem.read",
        )
    )
    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="local.filesystem.read",
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            sandbox_profile="workspace_ro",
            network_policy="deny",
            credential_policy="none",
            timeout_seconds=3,
        ),
        lambda args, context: {
            "status": "success",
            "summary": "workspace file read",
            "path": args.get("path") or "workspace://current",
        },
    )

    runtime.register_manifest(
        ToolCardManifest(
            tool_id="filesystem.write",
            owner="capability.tools.filesystem",
            capability_domain="filesystem",
            description_for_model="Write a workspace artifact file after approval.",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.WRITE_LOCAL,
            approval_policy=ToolApprovalPolicy.APPROVAL_REQUIRED,
            sandbox_profile="workspace_rw_artifacts",
            credential_policy="none",
            network_policy="deny",
            audit_policy="trace_and_review",
            budget={"timeout_seconds": 3},
            executor_adapter="local.filesystem.write",
        )
    )
    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="local.filesystem.write",
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            sandbox_profile="workspace_rw_artifacts",
            network_policy="deny",
            credential_policy="none",
            timeout_seconds=3,
        ),
        lambda args, context: {
            "status": "success",
            "summary": "workspace artifact write prepared",
            "path": args.get("path") or "artifacts/tool-output.md",
        },
    )

    runtime.register_manifest(
        ToolCardManifest(
            tool_id="mail.send",
            owner="capability.tools.send_email",
            capability_domain="mail",
            description_for_model="Send an external email after approval.",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.API,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.WRITE_EXTERNAL,
            approval_policy=ToolApprovalPolicy.APPROVAL_REQUIRED,
            sandbox_profile="network_limited",
            credential_policy="brokered_secret",
            network_policy="egress_mail_only",
            audit_policy="trace_and_review",
            budget={"timeout_seconds": 10},
            executor_adapter="api.mail.send",
        )
    )
    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="api.mail.send",
            execution_mode=ToolExecutionMode.API,
            sandbox_profile="network_limited",
            network_policy="egress_mail_only",
            credential_policy="brokered_secret",
            timeout_seconds=10,
        ),
        lambda args, context: {
            "status": "success",
            "summary": "email sent",
            "message_id": "msg_123",
        },
    )

    return runtime


def _normalize_executor(executor: LegacyToolExecutor | ToolExecutor) -> LegacyToolExecutor:
    def invoke(args: dict[str, Any], context: ToolExecutionContext) -> Any:
        try:
            return executor(args, context)  # type: ignore[misc]
        except TypeError:
            return executor(context)  # type: ignore[misc]

    return invoke


def _run_gateway_coroutine(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    outcome: dict[str, Any] = {}

    def runner() -> None:
        try:
            outcome["result"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - re-raised on caller thread
            outcome["error"] = exc

    thread = Thread(target=runner, name="tool-invocation-gateway", daemon=False)
    thread.start()
    thread.join()
    if "error" in outcome:
        raise outcome["error"]
    return outcome["result"]


def _is_credential_ref(value: str) -> bool:
    return str(value).startswith(("credref://", "vaultref://", "oauthref://"))


def _network_targets(payload: Any) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()

    def add_target(target: str) -> None:
        if target in seen:
            return
        seen.add(target)
        targets.append(target)

    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                visit(child_value, str(child_key))
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                visit(item, key)
            return
        if not isinstance(value, str):
            return
        text = value.strip()
        key_l = key.lower()
        if text.startswith(("http://", "https://", "ws://", "wss://", "mailto:", "smtp://")):
            add_target(text)
            return
        if key_l in {"url", "endpoint", "host", "hostname", "base_url"} and text:
            add_target(text)

    visit(payload)
    return targets


def _is_mail_target(target: str) -> bool:
    return str(target).startswith(("mailto:", "smtp://"))


def _redact_approval_comment(comment: str) -> str:
    redacted = redact_sensitive_text(comment)
    return re.sub(r"\braw-secret\b", "[REDACTED_SECRET]", redacted, flags=re.I)


def _approval_decision_ref(request: ToolRuntimeRequest) -> str:
    if request.approval_decision_ref:
        return request.approval_decision_ref
    if request.approved:
        return f"{LEGACY_APPROVAL_BOOLEAN_ADAPTER_ID}:{request.approval_id}"
    return ""


def _approval_adapter_ref(request: ToolRuntimeRequest) -> str:
    if request.approval_adapter_ref:
        return request.approval_adapter_ref
    if request.approved:
        return LEGACY_APPROVAL_BOOLEAN_ADAPTER_ID
    return ""


def _approval_adapter_removal_phase(request: ToolRuntimeRequest) -> str:
    if request.approval_adapter_removal_phase:
        return request.approval_adapter_removal_phase
    if request.approved and not request.approval_decision_ref:
        return LEGACY_APPROVAL_BOOLEAN_ADAPTER_REMOVAL_PHASE
    return ""


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "CredentialGrant",
    "InMemoryCredentialBroker",
    "NetworkPolicyDecision",
    "SandboxPolicyEnforcer",
    "ToolControlPlaneRuntime",
    "ToolExecutionContext",
    "ToolRuntimeExecutionResult",
    "ToolRuntimeRequest",
    "ToolSandboxContext",
    "build_default_tool_control_plane_runtime",
]
