from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from zuno.platform.services.graphrag.query_service import GraphRAGProjectSnapshot


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
    RECENT_ASSISTANT_TURN = "recent_assistant_turn"
    EXPLICIT_USER_CONSTRAINT = "explicit_user_constraint"
    RELEVANT_MEMORY = "relevant_memory"
    KNOWLEDGE_RESULT = "knowledge_result"
    TOOL_RESULT_REQUIRED = "tool_result_required"
    CAPABILITY_SELECTED = "capability_selected"
    LOW_PRIORITY_EVICTED = "low_priority_evicted"


@dataclass(frozen=True, slots=True)
class ContextPackPolicy:
    compression_strategy: str = "summary_compression"
    extraction_strategy: str = "structured_extraction"
    require_source_event_ids: bool = True
    review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "compression_strategy": self.compression_strategy,
            "extraction_strategy": self.extraction_strategy,
            "require_source_event_ids": self.require_source_event_ids,
            "review_required": self.review_required,
        }


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

    def apply(
        self,
        items: tuple[ContextItem, ...] | list[ContextItem],
    ) -> tuple[tuple[ContextItem, ...], tuple[ContextItem, ...]]:
        available = self.available_context_tokens()
        selected: list[ContextItem] = []
        dropped: list[ContextItem] = []
        used_tokens = 0

        groups: dict[str, list[ContextItem]] = {}
        ungrouped: list[ContextItem] = []
        for item in items:
            group_id = item.metadata.get("group_id")
            if group_id:
                groups.setdefault(str(group_id), []).append(item)
            else:
                ungrouped.append(item)

        candidates: list[tuple[int, str, tuple[ContextItem, ...]]] = [
            (
                max(group_item.priority for group_item in group_items),
                group_id,
                tuple(group_items),
            )
            for group_id, group_items in groups.items()
        ]
        candidates.extend((item.priority, item.item_id, (item,)) for item in ungrouped)
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)

        for priority, _name, group_items in candidates:
            group_tokens = sum(item.token_estimate for item in group_items)
            protected = priority >= 90
            if protected or used_tokens + group_tokens <= available:
                selected.extend(group_items)
                used_tokens += group_tokens
            else:
                dropped.extend(
                    ContextItem(
                        item_id=item.item_id,
                        source=item.source,
                        content=item.content,
                        token_estimate=item.token_estimate,
                        priority=item.priority,
                        reason=ContextSelectionReason.LOW_PRIORITY_EVICTED,
                        source_event_ids=item.source_event_ids,
                        metadata=dict(item.metadata),
                    )
                    for item in group_items
                )

        selected_ids = {item.item_id for item in selected}
        ordered_selected = tuple(item for item in items if item.item_id in selected_ids)
        dropped_ids = {item.item_id for item in dropped}
        ordered_dropped = tuple(item for item in dropped if item.item_id in dropped_ids)
        return ordered_selected, ordered_dropped

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
    context_policy: ContextPackPolicy = field(default_factory=ContextPackPolicy)
    source_event_ids_by_item: dict[str, tuple[str, ...]] = field(default_factory=dict)
    missing_source_event_item_ids: tuple[str, ...] = ()

    @classmethod
    def from_items(
        cls,
        *,
        trace_id: str,
        policy: TokenBudgetPolicy,
        context_policy: ContextPackPolicy | None = None,
        selected_items: tuple[ContextItem, ...],
        dropped_items: tuple[ContextItem, ...],
    ) -> ContextTrace:
        used_tokens = sum(item.token_estimate for item in selected_items)
        all_items = (*selected_items, *dropped_items)
        reasons = {
            item.item_id: item.reason.value
            for item in all_items
        }
        source_event_ids_by_item = {
            item.item_id: tuple(item.source_event_ids)
            for item in all_items
            if item.source_event_ids
        }
        missing_source_event_item_ids = tuple(
            item.item_id
            for item in all_items
            if item.source in {ContextSource.MEMORY, ContextSource.TASK_SUMMARY, ContextSource.KNOWLEDGE_EVIDENCE}
            and not item.source_event_ids
        )
        return cls(
            trace_id=trace_id,
            selected_item_ids=tuple(item.item_id for item in selected_items),
            dropped_item_ids=tuple(item.item_id for item in dropped_items),
            selection_reasons=reasons,
            used_tokens=used_tokens,
            remaining_tokens=policy.remaining_after(used_tokens),
            token_budget=policy,
            context_policy=context_policy or ContextPackPolicy(),
            source_event_ids_by_item=source_event_ids_by_item,
            missing_source_event_item_ids=missing_source_event_item_ids,
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
            "context_policy": self.context_policy.to_dict(),
            "source_event_ids_by_item": {
                item_id: list(source_event_ids)
                for item_id, source_event_ids in self.source_event_ids_by_item.items()
            },
            "missing_source_event_item_ids": list(self.missing_source_event_item_ids),
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
    context_policy: ContextPackPolicy = field(default_factory=ContextPackPolicy)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_context": self.execution_context.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "token_budget": self.token_budget.to_dict(used_tokens=self.trace.used_tokens),
            "context_policy": self.context_policy.to_dict(),
            "trace": self.trace.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class ContextPreparationInput:
    execution_context: AgentExecutionContext
    messages: tuple[Any, ...] = ()
    system_instruction: str = ""
    token_budget: TokenBudgetPolicy = field(
        default_factory=lambda: TokenBudgetPolicy(
            max_tokens=4000,
            reserved_response_tokens=800,
        )
    )
    memory_items: tuple[ContextItem, ...] = ()
    knowledge_evidence_items: tuple[ContextItem, ...] = ()
    capability_items: tuple[ContextItem, ...] = ()
    context_policy: ContextPackPolicy = field(default_factory=ContextPackPolicy)


@dataclass(frozen=True, slots=True)
class ContextPreparationResult:
    packet: ModelContextPacket
    selected_items: tuple[ContextItem, ...]
    dropped_items: tuple[ContextItem, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet": self.packet.to_dict(),
            "selected_items": [item.to_dict() for item in self.selected_items],
            "dropped_items": [item.to_dict() for item in self.dropped_items],
        }


__all__ = [
    "AgentExecutionContext",
    "ContextItem",
    "ContextPackPolicy",
    "ContextPreparationInput",
    "ContextPreparationResult",
    "ContextSelectionReason",
    "ContextSource",
    "ContextTrace",
    "ModelContextPacket",
    "TokenBudgetPolicy",
]
