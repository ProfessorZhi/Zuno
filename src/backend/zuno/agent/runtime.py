from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.agent.core.agents import AgentConfig, GeneralAgent


_EXPORT_TO_MODULE = {
    "AgentConfig": "zuno.agent.core.agents",
    "GeneralAgent": "zuno.agent.core.agents",
}

__all__ = [
    "AgentConfig",
    "GeneralAgent",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
