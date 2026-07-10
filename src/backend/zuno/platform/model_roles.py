from __future__ import annotations

from enum import StrEnum


class ModelRole(StrEnum):
    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    SYNTHESIS = "synthesis"
    TOOL_CALL = "tool_call"


ROLE_DEFAULT_SLOT = {
    ModelRole.PLANNER: "reasoning_model",
    ModelRole.EXECUTOR: "conversation_model",
    ModelRole.CRITIC: "reasoning_model",
    ModelRole.SYNTHESIS: "conversation_model",
    ModelRole.TOOL_CALL: "tool_call_model",
}


__all__ = ["ModelRole", "ROLE_DEFAULT_SLOT"]
