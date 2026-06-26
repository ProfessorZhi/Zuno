from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from zuno.services.graphrag.query_service import GraphRAGProjectSnapshot


class ContextSource(StrEnum):
    SYSTEM_INSTRUCTION = "system_instruction"
    RECENT_MESSAGE = "recent_message"
    TASK_SUMMARY = "task_summary"
    MEMORY = "memory"
    KNOWLEDGE_EVIDENCE = "knowledge_evidence"
    TOOL_RESULT = "tool_result"
    CAPABILITY_SCHEMA = "capability_schema"


class ContextSelectionReason(StrEnum):
    PINNED_INSTRUCTION = "pinned_instruction"
    RECENT_USER_TURN = "recent_user_turn"
    RELEVANT_MEMORY = "relevant_memory"
    KNOWLEDGE_RESULT = "knowledge_result"
    TOOL_RESULT_REQUIRED = "tool_result_required"
    CAPABILITY_SELECTED = "capability_selected"
    LOW_PRIORITY_EVICTED = "low_priority_evicted"


@dataclass(frozen=True, slots=True)
class ContextItem:
    item_id: str
    source: ContextSource
    content: str
    token_estimate: int
    priority: int
    reason: ContextSelectionReason
    source_event_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "source": self.source.value,
            "content": self.content,
            "token_estimate": self.token_estimate,
            "priority": self.priority,
            "reason": self.reason.value,
            "source_event_ids": list(self.source_event_ids),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class TokenBudgetPolicy:
    max_tokens: int
    reserved_response_tokens: int = 0
    hard_limit: bool = True

    def available_context_tokens(self) -> int:
        return max(0, self.max_tokens - self.reserved_response_tokens)

    def remaining_after(self, used_tokens: int) -> int:
        return max(0, self.available_context_tokens() - used_tokens)

    def to_dict(self, *, used_tokens: int = 0) -> dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "reserved_response_tokens": self.reserved_response_tokens,
            "available_context_tokens": self.available_context_tokens(),
            "used_tokens": used_tokens,
            "remaining_tokens": self.remaining_after(used_tokens),
            "hard_limit": self.hard_limit,
        }


@dataclass(frozen=True, slots=True)
class ContextTrace:
    trace_id: str
    selected_item_ids: tuple[str, ...]
    dropped_item_ids: tuple[str, ...]
    selection_reasons: dict[str, str]
    used_tokens: int
    remaining_tokens: int
    token_budget: TokenBudgetPolicy

    @classmethod
    def from_items(
        cls,
        *,
        trace_id: str,
        policy: TokenBudgetPolicy,
        selected_items: tuple[ContextItem, ...],
        dropped_items: tuple[ContextItem, ...],
    ) -> ContextTrace:
        used_tokens = sum(item.token_estimate for item in selected_items)
        reasons = {
            item.item_id: item.reason.value
            for item in (*selected_items, *dropped_items)
        }
        return cls(
            trace_id=trace_id,
            selected_item_ids=tuple(item.item_id for item in selected_items),
            dropped_item_ids=tuple(item.item_id for item in dropped_items),
            selection_reasons=reasons,
            used_tokens=used_tokens,
            remaining_tokens=policy.remaining_after(used_tokens),
            token_budget=policy,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "selected_item_ids": list(self.selected_item_ids),
            "dropped_item_ids": list(self.dropped_item_ids),
            "selection_reasons": dict(self.selection_reasons),
            "used_tokens": self.used_tokens,
            "remaining_tokens": self.remaining_tokens,
            "token_budget": self.token_budget.to_dict(used_tokens=self.used_tokens),
        }


@dataclass(frozen=True, slots=True)
class AgentExecutionContext:
    trace_id: str
    user_id: str
    agent_id: str
    thread_id: str
    project_id: str | None
    task: str
    graphrag_project: GraphRAGProjectSnapshot | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "thread_id": self.thread_id,
            "project_id": self.project_id,
            "task": self.task,
            "graphrag_project_id": (
                self.graphrag_project.graphrag_project_id
                if self.graphrag_project is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ModelContextPacket:
    execution_context: AgentExecutionContext
    items: tuple[ContextItem, ...]
    token_budget: TokenBudgetPolicy
    trace: ContextTrace

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_context": self.execution_context.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "token_budget": self.token_budget.to_dict(used_tokens=self.trace.used_tokens),
            "trace": self.trace.to_dict(),
        }


__all__ = [
    "AgentExecutionContext",
    "ContextItem",
    "ContextSelectionReason",
    "ContextSource",
    "ContextTrace",
    "ModelContextPacket",
    "TokenBudgetPolicy",
]
