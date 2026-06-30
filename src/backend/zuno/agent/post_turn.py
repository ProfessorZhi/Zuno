from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zuno.memory.contracts import MemoryScope, RawMemoryEvent, TaskMemorySummary
from zuno.platform.services.memory.layers import InMemoryLayerStore


@dataclass(frozen=True, slots=True)
class RuntimeTurnLedger:
    trace_id: str = ""
    context_trace: dict[str, Any] = field(default_factory=dict)
    capability_trace: dict[str, Any] = field(default_factory=dict)
    knowledge_trace: dict[str, Any] = field(default_factory=dict)
    tool_trace_events: tuple[dict[str, Any], ...] = ()
    post_turn_memory_event_ids: tuple[str, ...] = ()
    response_present: bool = False
    stage_order: tuple[str, ...] = ()
    layers_touched: tuple[str, ...] = ()

    @classmethod
    def from_runtime(
        cls,
        *,
        context_packet: Any,
        capability_selection: Any,
        knowledge_trace: dict[str, Any] | None,
        tool_trace_events: tuple[dict[str, Any], ...] | list[dict[str, Any]],
        post_turn_memory_event_ids: tuple[str, ...] | list[str],
        response: str,
    ) -> "RuntimeTurnLedger":
        context_trace = context_packet.trace.to_dict() if context_packet is not None else {}
        capability_trace = (
            capability_selection.trace.to_dict()
            if capability_selection is not None and getattr(capability_selection, "trace", None) is not None
            else {}
        )
        knowledge_payload = dict(knowledge_trace or {})
        tool_events = tuple(dict(event) for event in tool_trace_events or ())
        memory_event_ids = tuple(str(event_id) for event_id in post_turn_memory_event_ids or ())

        stage_order = ["prepare_context"]
        if capability_trace:
            stage_order.append("capability_selection")
        stage_order.append("agent_loop")
        if knowledge_payload:
            stage_order.append("knowledge_retrieval_trace")
        if tool_events:
            stage_order.append("tool_trace")
        stage_order.append("post_turn_commit")

        layers_touched = ["agent", "context"]
        if capability_trace:
            layers_touched.append("capability")
        if knowledge_payload:
            layers_touched.append("knowledge")
        if knowledge_payload or tool_events:
            layers_touched.append("trace")
        if memory_event_ids:
            layers_touched.append("memory")

        return cls(
            trace_id=str(getattr(getattr(context_packet, "execution_context", None), "trace_id", "") or ""),
            context_trace=context_trace,
            capability_trace=capability_trace,
            knowledge_trace=knowledge_payload,
            tool_trace_events=tool_events,
            post_turn_memory_event_ids=memory_event_ids,
            response_present=bool(str(response or "").strip()),
            stage_order=tuple(stage_order),
            layers_touched=tuple(layers_touched),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "context_trace": dict(self.context_trace),
            "capability_trace": dict(self.capability_trace),
            "knowledge_trace": dict(self.knowledge_trace),
            "tool_trace_events": [dict(event) for event in self.tool_trace_events],
            "post_turn_memory_event_ids": list(self.post_turn_memory_event_ids),
            "response_present": self.response_present,
            "stage_order": list(self.stage_order),
            "layers_touched": list(self.layers_touched),
        }


__all__ = [
    "InMemoryLayerStore",
    "MemoryScope",
    "RawMemoryEvent",
    "RuntimeTurnLedger",
    "TaskMemorySummary",
]
