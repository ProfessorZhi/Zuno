from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.agent.core.agents.general_agent import (
        AgentConfig,
        EmitEventAgentMiddleware,
        GeneralAgent,
        StreamAgentState,
    )
    from zuno.agent.core.agents.structured_response_agent import StructuredResponseAgent


_EXPORT_TO_MODULE = {
    "AgentConfig": "general_agent",
    "EmitEventAgentMiddleware": "general_agent",
    "GeneralAgent": "general_agent",
    "StreamAgentState": "general_agent",
    "StructuredResponseAgent": "structured_response_agent",
}

__all__ = [
    "AgentConfig",
    "EmitEventAgentMiddleware",
    "GeneralAgent",
    "StreamAgentState",
    "StructuredResponseAgent",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
