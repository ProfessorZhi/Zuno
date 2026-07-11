from __future__ import annotations

from typing import Any, Protocol


class ModelGatewayProtocol(Protocol):
    def invoke(self, request: Any) -> Any:
        """Run one model request through the model gateway."""


class MemoryEngineProtocol(Protocol):
    def build_context_pack(self, **kwargs: Any) -> dict[str, Any]:
        """Build the runtime ContextPack view for one task."""

    def append_event(self, **kwargs: Any) -> Any:
        """Append a raw memory event."""

    def summarize_task(self, **kwargs: Any) -> Any:
        """Write or update a task summary."""


class KnowledgeRuntimeProtocol(Protocol):
    def retrieve(self, request: Any) -> Any:
        """Run corrective retrieval and return an EvidenceLedger-bearing result."""


class CapabilityRuntimeProtocol(Protocol):
    def select(self, request: Any) -> Any:
        """Select capabilities for a task."""


class ToolControlPlaneProtocol(Protocol):
    def execute(self, request: Any) -> Any:
        """Execute a governed tool request."""


class TraceSinkProtocol(Protocol):
    def append(self, event: dict[str, Any]) -> None:
        """Append a runtime trace event."""


__all__ = [
    "CapabilityRuntimeProtocol",
    "KnowledgeRuntimeProtocol",
    "MemoryEngineProtocol",
    "ModelGatewayProtocol",
    "ToolControlPlaneProtocol",
    "TraceSinkProtocol",
]
