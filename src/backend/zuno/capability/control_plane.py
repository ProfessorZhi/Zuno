from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ToolExecutionMode(StrEnum):
    LOCAL_FUNCTION = "local_function"
    SDK = "sdk"
    API = "api"
    CLI = "cli"
    SSH = "ssh"
    MCP_LOCAL = "mcp_local"
    MCP_REMOTE = "mcp_remote"
    SANDBOX = "sandbox"


class ToolTrustTier(StrEnum):
    SYSTEM = "system"
    WORKSPACE = "workspace"
    USER = "user"
    UNTRUSTED = "untrusted"


class ToolSideEffectLevel(StrEnum):
    NONE = "none"
    READ = "read"
    WRITE_LOCAL = "write_local"
    WRITE_EXTERNAL = "write_external"
    DESTRUCTIVE = "destructive"


class ToolApprovalPolicy(StrEnum):
    AUTO = "auto"
    APPROVAL_REQUIRED = "approval_required"
    DISABLED = "disabled"


SIDE_EFFECT_RISK_MATRIX = {
    "none": {
        "default_approval_policy": "auto",
        "default_sandbox_profile": "read_only",
        "audit_required": False,
    },
    "read": {
        "default_approval_policy": "auto",
        "default_sandbox_profile": "read_scoped",
        "audit_required": True,
    },
    "write_local": {
        "default_approval_policy": "approval_required",
        "default_sandbox_profile": "workspace_write_scoped",
        "audit_required": True,
    },
    "write_external": {
        "default_approval_policy": "approval_required",
        "default_sandbox_profile": "network_limited",
        "audit_required": True,
    },
    "destructive": {
        "default_approval_policy": "approval_required",
        "default_sandbox_profile": "isolated",
        "audit_required": True,
    },
}


@dataclass(frozen=True, slots=True)
class ToolCardManifest:
    tool_id: str
    owner: str
    capability_domain: str
    description_for_model: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    execution_mode: ToolExecutionMode
    trust_tier: ToolTrustTier
    side_effect_level: ToolSideEffectLevel
    approval_policy: ToolApprovalPolicy
    sandbox_profile: str
    credential_policy: str
    network_policy: str
    audit_policy: str
    budget: dict[str, Any]
    failure_modes: tuple[str, ...] = ()
    executor_adapter: str = ""

    @property
    def requires_approval(self) -> bool:
        return self.approval_policy is ToolApprovalPolicy.APPROVAL_REQUIRED or self.side_effect_level in {
            ToolSideEffectLevel.WRITE_EXTERNAL,
            ToolSideEffectLevel.DESTRUCTIVE,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "owner": self.owner,
            "capability_domain": self.capability_domain,
            "description_for_model": self.description_for_model,
            "input_schema": deepcopy(self.input_schema),
            "output_schema": deepcopy(self.output_schema),
            "execution_mode": self.execution_mode.value,
            "trust_tier": self.trust_tier.value,
            "side_effect_level": self.side_effect_level.value,
            "approval_policy": self.approval_policy.value,
            "sandbox_profile": self.sandbox_profile,
            "credential_policy": self.credential_policy,
            "network_policy": self.network_policy,
            "audit_policy": self.audit_policy,
            "budget": deepcopy(self.budget),
            "failure_modes": list(self.failure_modes),
            "executor_adapter": self.executor_adapter,
            "requires_approval": self.requires_approval,
        }


@dataclass(frozen=True, slots=True)
class ExecutorAdapterContract:
    adapter_id: str
    execution_mode: ToolExecutionMode
    sandbox_profile: str
    network_policy: str
    credential_policy: str
    timeout_seconds: int
    result_normalizer: str = "default"

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "execution_mode": self.execution_mode.value,
            "sandbox_profile": self.sandbox_profile,
            "network_policy": self.network_policy,
            "credential_policy": self.credential_policy,
            "timeout_seconds": self.timeout_seconds,
            "result_normalizer": self.result_normalizer,
        }


@dataclass(slots=True)
class ExecutorRegistry:
    _adapters: dict[str, ExecutorAdapterContract] = field(default_factory=dict)

    def register(self, adapter: ExecutorAdapterContract) -> None:
        self._adapters[adapter.adapter_id] = adapter

    def get(self, adapter_id: str) -> ExecutorAdapterContract | None:
        return self._adapters.get(adapter_id)

    def list(self) -> tuple[ExecutorAdapterContract, ...]:
        return tuple(self._adapters.values())

    def select_executor(self, manifest: ToolCardManifest) -> ExecutorAdapterContract:
        if manifest.executor_adapter:
            adapter = self.get(manifest.executor_adapter)
            if adapter is None:
                raise KeyError(f"unknown executor adapter: {manifest.executor_adapter}")
            return adapter
        for adapter in self._adapters.values():
            if adapter.execution_mode is manifest.execution_mode:
                return adapter
        raise KeyError(f"no executor adapter for mode: {manifest.execution_mode.value}")


@dataclass(frozen=True, slots=True)
class ToolApprovalDecision:
    tool_id: str
    allowed: bool
    approval_required: bool
    reason: str
    interrupt: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "allowed": self.allowed,
            "approval_required": self.approval_required,
            "reason": self.reason,
            "interrupt": deepcopy(self.interrupt),
        }


class ApprovalGate:
    def evaluate(
        self,
        manifest: ToolCardManifest,
        *,
        runtime_state: Any | None = None,
        node: str = "act_react_loop",
    ) -> ToolApprovalDecision:
        if manifest.approval_policy is ToolApprovalPolicy.DISABLED:
            return ToolApprovalDecision(
                tool_id=manifest.tool_id,
                allowed=False,
                approval_required=False,
                reason="tool_disabled",
            )
        if not manifest.requires_approval:
            return ToolApprovalDecision(
                tool_id=manifest.tool_id,
                allowed=True,
                approval_required=False,
                reason="auto_allowed",
            )

        interrupt = None
        if runtime_state is not None:
            from zuno.agent.harness import build_single_controller_runtime_harness

            interrupt = build_single_controller_runtime_harness().request_interrupt(
                runtime_state,
                node=node,
                reason="tool_approval_required",
                required_approval=f"tool:{manifest.tool_id}",
                payload={
                    "tool_id": manifest.tool_id,
                    "side_effect_level": manifest.side_effect_level.value,
                    "approval_policy": manifest.approval_policy.value,
                },
            ).to_dict()
        return ToolApprovalDecision(
            tool_id=manifest.tool_id,
            allowed=False,
            approval_required=True,
            reason="approval_required",
            interrupt=interrupt,
        )


@dataclass(frozen=True, slots=True)
class MCPTrustContract:
    server_id: str
    transport: str
    trust_tier: ToolTrustTier
    auth_policy: str
    allowed_tools: tuple[str, ...]
    scope: str
    origin: str
    network_policy: str
    credential_policy: str
    untrusted_content_label: str = "mcp_untrusted_content"

    def allows_tool(self, tool_name: str) -> bool:
        return not self.allowed_tools or tool_name in self.allowed_tools

    def to_dict(self) -> dict[str, Any]:
        return {
            "server_id": self.server_id,
            "transport": self.transport,
            "trust_tier": self.trust_tier.value,
            "auth_policy": self.auth_policy,
            "allowed_tools": list(self.allowed_tools),
            "scope": self.scope,
            "origin": self.origin,
            "network_policy": self.network_policy,
            "credential_policy": self.credential_policy,
            "untrusted_content_label": self.untrusted_content_label,
        }


@dataclass(frozen=True, slots=True)
class NormalizedToolResult:
    tool_id: str
    status: str
    data: dict[str, Any]
    summary: str
    error: str
    audit_ref: str
    trace_span_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "status": self.status,
            "data": deepcopy(self.data),
            "summary": self.summary,
            "error": self.error,
            "audit_ref": self.audit_ref,
            "trace_span_id": self.trace_span_id,
        }


class ToolResultNormalizer:
    @staticmethod
    def normalize(
        *,
        tool_id: str,
        raw_result: Any,
        trace_span_id: str,
        audit_ref: str,
    ) -> NormalizedToolResult:
        if isinstance(raw_result, NormalizedToolResult):
            return raw_result
        if isinstance(raw_result, dict):
            status = str(raw_result.get("status") or "success")
            error = str(raw_result.get("error") or "")
            data = {
                key: deepcopy(value)
                for key, value in raw_result.items()
                if key not in {"status", "error", "summary"}
            }
            summary = str(raw_result.get("summary") or f"{tool_id} completed")
            return NormalizedToolResult(
                tool_id=tool_id,
                status=status,
                data=data,
                summary=summary,
                error=error,
                audit_ref=audit_ref,
                trace_span_id=trace_span_id,
            )
        return NormalizedToolResult(
            tool_id=tool_id,
            status="success",
            data={"value": raw_result},
            summary=f"{tool_id} completed",
            error="",
            audit_ref=audit_ref,
            trace_span_id=trace_span_id,
        )


__all__ = [
    "ApprovalGate",
    "ExecutorAdapterContract",
    "ExecutorRegistry",
    "MCPTrustContract",
    "NormalizedToolResult",
    "SIDE_EFFECT_RISK_MATRIX",
    "ToolApprovalDecision",
    "ToolApprovalPolicy",
    "ToolCardManifest",
    "ToolExecutionMode",
    "ToolResultNormalizer",
    "ToolSideEffectLevel",
    "ToolTrustTier",
]
