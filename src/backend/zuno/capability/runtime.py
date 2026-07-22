from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field, replace
import hashlib
import json
import re
from typing import Any, Protocol
from uuid import uuid4

from zuno.capability.control_plane import (
    ApprovalGate,
    ExecutorAdapterContract,
    ExecutorRegistry,
    NormalizedToolResult,
    ToolApprovalPolicy,
    ToolCardManifest,
    ToolExecutionMode,
    ToolResultNormalizer,
    ToolSideEffectLevel,
    ToolTrustTier,
)
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
    ) -> None:
        self._manifests: dict[str, ToolCardManifest] = {}
        self._executor_registry = ExecutorRegistry()
        self._executors: dict[str, LegacyToolExecutor] = {}
        self._credential_broker = credential_broker or InMemoryCredentialBroker()
        self._sandbox_enforcer = sandbox_enforcer or SandboxPolicyEnforcer()
        self._security_approval_sink = security_approval_sink
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
        raw_result = self._executors[adapter.adapter_id](request.arguments, execution_context)
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
        return ToolRuntimeExecutionResult(
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
    runtime = ToolControlPlaneRuntime(security_approval_sink=security_approval_sink)

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
            "summary": "email send accepted by sandboxed adapter",
            "message_id": f"msg_{uuid4().hex[:12]}",
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
    "SecurityApprovalFactSink",
    "ToolControlPlaneRuntime",
    "ToolExecutionContext",
    "ToolRuntimeExecutionResult",
    "ToolRuntimeRequest",
    "ToolSandboxContext",
    "LEGACY_APPROVAL_BOOLEAN_ADAPTER_ID",
    "LEGACY_APPROVAL_BOOLEAN_ADAPTER_REMOVAL_PHASE",
    "WORKSPACE_APPROVAL_DECISION_REF_ADAPTER_ID",
    "build_default_tool_control_plane_runtime",
]
