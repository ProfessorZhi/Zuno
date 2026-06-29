from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "AgentConfig": "zuno.agent.runtime",
    "AgentExecutionContext": "zuno.agent.context",
    "ContextOrchestrator": "zuno.agent.context",
    "ContextTrace": "zuno.agent.context",
    "GeneralAgent": "zuno.agent.runtime",
    "ModelContextPacket": "zuno.agent.context",
    "StreamAgentState": "zuno.agent.state",
}

__all__ = [
    "AgentConfig",
    "AgentExecutionContext",
    "ContextOrchestrator",
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
