from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.platform.services.application.context import (
        AgentExecutionContext,
        ContextItem,
        ContextOrchestrator,
        ContextPackPolicy,
        ContextPreparationInput,
        ContextSelectionReason,
        ContextSource,
        ContextTrace,
        ModelContextPacket,
        TokenBudgetPolicy,
    )


_EXPORT_TO_MODULE = {
    "AgentExecutionContext": "zuno.platform.services.application.context",
    "ContextItem": "zuno.platform.services.application.context",
    "ContextOrchestrator": "zuno.platform.services.application.context",
    "ContextPackPolicy": "zuno.platform.services.application.context",
    "ContextPreparationInput": "zuno.platform.services.application.context",
    "ContextSelectionReason": "zuno.platform.services.application.context",
    "ContextSource": "zuno.platform.services.application.context",
    "ContextTrace": "zuno.platform.services.application.context",
    "ModelContextPacket": "zuno.platform.services.application.context",
    "TokenBudgetPolicy": "zuno.platform.services.application.context",
}

__all__ = [
    "AgentExecutionContext",
    "ContextItem",
    "ContextOrchestrator",
    "ContextPackPolicy",
    "ContextPreparationInput",
    "ContextSelectionReason",
    "ContextSource",
    "ContextTrace",
    "ModelContextPacket",
    "TokenBudgetPolicy",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
