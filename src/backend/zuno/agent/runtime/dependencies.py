from __future__ import annotations

from dataclasses import dataclass

from zuno.agent.runtime.protocols import (
    CapabilityRuntimeProtocol,
    KnowledgeRuntimeProtocol,
    MemoryEngineProtocol,
    ModelGatewayProtocol,
    ToolControlPlaneProtocol,
    TraceSinkProtocol,
)


@dataclass(frozen=True, slots=True)
class RuntimeDependencies:
    model_gateway: ModelGatewayProtocol | None = None
    memory_engine: MemoryEngineProtocol | None = None
    knowledge_runtime: KnowledgeRuntimeProtocol | None = None
    capability_runtime: CapabilityRuntimeProtocol | None = None
    tool_control_plane: ToolControlPlaneProtocol | None = None
    trace_sink: TraceSinkProtocol | None = None


__all__ = ["RuntimeDependencies"]
