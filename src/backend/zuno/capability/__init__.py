from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.capability.contracts import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityRecord,
        CapabilityType,
        ToolCard,
    )
    from zuno.capability.control_plane import (
        ApprovalGate,
        ExecutorAdapterContract,
        ExecutorRegistry,
        MCPTrustContract,
        NormalizedToolResult,
        ToolApprovalDecision,
        ToolApprovalPolicy,
        ToolCardManifest,
        ToolExecutionMode,
        ToolResultNormalizer,
        ToolSideEffectLevel,
        ToolTrustTier,
    )
    from zuno.capability.layer import (
        CapabilityDecision,
        CapabilityLayerRegistry,
        CapabilityRouteDecision,
        CapabilityRouteRequest,
        CapabilityRouter,
        build_default_capability_layer_registry,
    )
    from zuno.capability.registry import CapabilityRegistry, ToolCardRegistry
    from zuno.capability.retrieval import NativeBM25Retriever, NativeBM25SearchResult
    from zuno.capability.runtime import (
        CredentialGrant,
        InMemoryCredentialBroker,
        SandboxPolicyEnforcer,
        ToolControlPlaneRuntime,
        ToolExecutionContext,
        ToolRuntimeExecutionResult,
        ToolRuntimeRequest,
        ToolSandboxContext,
        build_default_tool_control_plane_runtime,
    )
    from zuno.capability.runtime_batch import (
        CapabilityRuntimeBatch,
    )
    from zuno.capability.selector import (
        CapabilitySelectionRequest,
        CapabilitySelectionResult,
        DynamicCapabilitySelector,
    )
    from zuno.capability.trace import CapabilitySelectionTrace
    from zuno.capability.tool_runtime import ToolRuntimeBatch


_EXPORT_TO_MODULE = {
    "CapabilityCost": "zuno.capability.contracts",
    "CapabilityHealth": "zuno.capability.contracts",
    "CapabilityPermissions": "zuno.capability.contracts",
    "CapabilityRecord": "zuno.capability.contracts",
    "CapabilityRegistry": "zuno.capability.registry",
    "CapabilityDecision": "zuno.capability.layer",
    "CapabilityLayerRegistry": "zuno.capability.layer",
    "CapabilityRouteDecision": "zuno.capability.layer",
    "CapabilityRouteRequest": "zuno.capability.layer",
    "CapabilityRouter": "zuno.capability.layer",
    "CapabilitySelectionRequest": "zuno.capability.selector",
    "CapabilitySelectionResult": "zuno.capability.selector",
    "CapabilitySelectionTrace": "zuno.capability.trace",
    "CapabilityType": "zuno.capability.contracts",
    "CapabilityRuntimeBatch": "zuno.capability.runtime_batch",
    "CredentialGrant": "zuno.capability.runtime",
    "DynamicCapabilitySelector": "zuno.capability.selector",
    "ApprovalGate": "zuno.capability.control_plane",
    "ExecutorAdapterContract": "zuno.capability.control_plane",
    "ExecutorRegistry": "zuno.capability.control_plane",
    "InMemoryCredentialBroker": "zuno.capability.runtime",
    "MCPTrustContract": "zuno.capability.control_plane",
    "NativeBM25Retriever": "zuno.capability.retrieval",
    "NativeBM25SearchResult": "zuno.capability.retrieval",
    "NormalizedToolResult": "zuno.capability.control_plane",
    "SandboxPolicyEnforcer": "zuno.capability.runtime",
    "ToolApprovalDecision": "zuno.capability.control_plane",
    "ToolApprovalPolicy": "zuno.capability.control_plane",
    "ToolCard": "zuno.capability.contracts",
    "ToolCardManifest": "zuno.capability.control_plane",
    "ToolCardRegistry": "zuno.capability.registry",
    "ToolControlPlaneRuntime": "zuno.capability.runtime",
    "ToolExecutionMode": "zuno.capability.control_plane",
    "ToolExecutionContext": "zuno.capability.runtime",
    "ToolResultNormalizer": "zuno.capability.control_plane",
    "ToolRuntimeExecutionResult": "zuno.capability.runtime",
    "ToolRuntimeRequest": "zuno.capability.runtime",
    "ToolRuntimeBatch": "zuno.capability.tool_runtime",
    "ToolSandboxContext": "zuno.capability.runtime",
    "ToolSideEffectLevel": "zuno.capability.control_plane",
    "ToolTrustTier": "zuno.capability.control_plane",
    "build_default_tool_control_plane_runtime": "zuno.capability.runtime",
    "build_default_capability_layer_registry": "zuno.capability.layer",
}

__all__ = [
    "ApprovalGate",
    "CapabilityCost",
    "CapabilityHealth",
    "CapabilityPermissions",
    "CapabilityRecord",
    "CapabilityRegistry",
    "CapabilityDecision",
    "CapabilityLayerRegistry",
    "CapabilityRouteDecision",
    "CapabilityRouteRequest",
    "CapabilityRouter",
    "CapabilitySelectionRequest",
    "CapabilitySelectionResult",
    "CapabilitySelectionTrace",
    "CapabilityType",
    "CapabilityRuntimeBatch",
    "CredentialGrant",
    "DynamicCapabilitySelector",
    "ExecutorAdapterContract",
    "ExecutorRegistry",
    "InMemoryCredentialBroker",
    "MCPTrustContract",
    "NativeBM25Retriever",
    "NativeBM25SearchResult",
    "NormalizedToolResult",
    "SandboxPolicyEnforcer",
    "ToolApprovalDecision",
    "ToolApprovalPolicy",
    "ToolCard",
    "ToolCardManifest",
    "ToolCardRegistry",
    "ToolControlPlaneRuntime",
    "ToolExecutionMode",
    "ToolExecutionContext",
    "ToolResultNormalizer",
    "ToolRuntimeExecutionResult",
    "ToolRuntimeRequest",
    "ToolRuntimeBatch",
    "ToolSandboxContext",
    "ToolSideEffectLevel",
    "ToolTrustTier",
    "build_default_capability_layer_registry",
    "build_default_tool_control_plane_runtime",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
