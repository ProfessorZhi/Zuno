from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from zuno.platform.services.application.context.contracts import (
    ContextItem,
    ContextPreparationInput,
    ContextPreparationResult,
    ContextSelectionReason,
    ContextSource,
    ContextTrace,
    ModelContextPacket,
)


class RecentWindowSelector:
    def __init__(self, estimate_tokens: Callable[[str], int] | None = None) -> None:
        self.estimate_tokens = estimate_tokens or _estimate_tokens

    def select(self, messages: tuple[Any, ...]) -> tuple[ContextItem, ...]:
        items: list[ContextItem] = []
        latest_user_index = self._latest_user_index(messages)
        tool_group_id: str | None = None
        tool_call_ids: set[str] = set()

        for index, message in enumerate(messages):
            content = _message_content(message)
            if isinstance(message, SystemMessage):
                continue
            if isinstance(message, HumanMessage):
                explicit_constraint = _looks_like_explicit_constraint(content)
                items.append(
                    ContextItem(
                        item_id=f"message_{index}",
                        source=ContextSource.RECENT_MESSAGE,
                        content=content,
                        token_estimate=self.estimate_tokens(content),
                        priority=100 if explicit_constraint else (90 if index == latest_user_index else 55),
                        reason=(
                            ContextSelectionReason.EXPLICIT_USER_CONSTRAINT
                            if explicit_constraint
                            else ContextSelectionReason.RECENT_USER_TURN
                        ),
                        metadata={"message_role": "user"},
                    )
                )
                continue
            if isinstance(message, AIMessage):
                calls = list(getattr(message, "tool_calls", None) or [])
                if calls:
                    tool_call_ids = {str(call.get("id") or call.get("name") or index) for call in calls}
                    tool_group_id = f"tool_group_{index}"
                    content = content or "; ".join(str(call.get("name") or "tool_call") for call in calls)
                    items.append(
                        ContextItem(
                            item_id=f"message_{index}",
                            source=ContextSource.TOOL_RESULT,
                            content=content,
                            token_estimate=self.estimate_tokens(content),
                            priority=80,
                            reason=ContextSelectionReason.TOOL_RESULT_REQUIRED,
                            metadata={"message_role": "assistant", "group_id": tool_group_id},
                        )
                    )
                    continue
                if content:
                    items.append(
                        ContextItem(
                            item_id=f"message_{index}",
                            source=ContextSource.RECENT_MESSAGE,
                            content=content,
                            token_estimate=self.estimate_tokens(content),
                            priority=45,
                            reason=ContextSelectionReason.RECENT_ASSISTANT_TURN,
                            metadata={"message_role": "assistant"},
                        )
                    )
                    continue
            if isinstance(message, ToolMessage):
                call_id = str(getattr(message, "tool_call_id", "") or index)
                group_id = tool_group_id if call_id in tool_call_ids else f"tool_group_{index}"
                items.append(
                    ContextItem(
                        item_id=f"message_{index}",
                        source=ContextSource.TOOL_RESULT,
                        content=content,
                        token_estimate=self.estimate_tokens(content),
                        priority=80,
                        reason=ContextSelectionReason.TOOL_RESULT_REQUIRED,
                        metadata={"message_role": "tool", "tool_call_id": call_id, "group_id": group_id},
                    )
                )

        return tuple(items)

    @staticmethod
    def _latest_user_index(messages: tuple[Any, ...]) -> int | None:
        for index in range(len(messages) - 1, -1, -1):
            if isinstance(messages[index], HumanMessage):
                return index
        return None


class ContextOrchestrator:
    def __init__(self, recent_window_selector: RecentWindowSelector | None = None) -> None:
        self.recent_window_selector = recent_window_selector or RecentWindowSelector()

    def prepare(self, preparation_input: ContextPreparationInput) -> ContextPreparationResult:
        candidates: list[ContextItem] = []
        system_instruction = preparation_input.system_instruction.strip()
        if system_instruction:
            candidates.append(
                ContextItem(
                    item_id="system_prompt",
                    source=ContextSource.SYSTEM_INSTRUCTION,
                    content=system_instruction,
                    token_estimate=_estimate_tokens(system_instruction),
                    priority=100,
                    reason=ContextSelectionReason.PINNED_INSTRUCTION,
                )
            )

        candidates.extend(self.recent_window_selector.select(preparation_input.messages))
        candidates.extend(preparation_input.memory_items)
        candidates.extend(preparation_input.knowledge_evidence_items)
        candidates.extend(preparation_input.capability_items)

        selected_items, dropped_items = preparation_input.token_budget.apply(tuple(candidates))
        trace = ContextTrace.from_items(
            trace_id=preparation_input.execution_context.trace_id,
            policy=preparation_input.token_budget,
            selected_items=selected_items,
            dropped_items=dropped_items,
        )
        packet = ModelContextPacket(
            execution_context=preparation_input.execution_context,
            items=selected_items,
            token_budget=preparation_input.token_budget,
            trace=trace,
        )
        return ContextPreparationResult(
            packet=packet,
            selected_items=selected_items,
            dropped_items=dropped_items,
        )


def _message_content(message: Any) -> str:
    content = getattr(message, "content", "") or ""
    if isinstance(content, list):
        return " ".join(str(part) for part in content)
    return str(content)


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _looks_like_explicit_constraint(text: str) -> bool:
    lowered = text.lower()
    markers = (
        "must",
        "always",
        "never",
        "requirement",
        "constraint",
        "必须",
        "不要",
        "不能",
        "约束",
        "要求",
    )
    return any(marker in lowered for marker in markers)


__all__ = ["ContextOrchestrator", "RecentWindowSelector"]
