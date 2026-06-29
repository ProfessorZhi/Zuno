from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.agent.context import (
        AgentExecutionContext,
        ContextOrchestrator,
        ContextPackPolicy,
        ContextTrace,
        ModelContextPacket,
    )
    from zuno.agent.runtime import AgentConfig, GeneralAgent
    from zuno.agent.state import StreamAgentState


_EXPORT_TO_MODULE = {
    "AgentConfig": "zuno.agent.runtime",
    "AgentExecutionContext": "zuno.agent.context",
    "ContextOrchestrator": "zuno.agent.context",
    "ContextPackPolicy": "zuno.agent.context",
    "ContextTrace": "zuno.agent.context",
    "GeneralAgent": "zuno.agent.runtime",
    "ModelContextPacket": "zuno.agent.context",
    "StreamAgentState": "zuno.agent.state",
}

__all__ = [
    "AgentConfig",
    "AgentExecutionContext",
    "ContextOrchestrator",
    "ContextPackPolicy",
    "ContextTrace",
    "GeneralAgent",
    "ModelContextPacket",
    "StreamAgentState",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
