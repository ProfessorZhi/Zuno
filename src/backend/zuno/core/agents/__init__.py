from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "AgentConfig": "general_agent",
    "EmitEventAgentMiddleware": "general_agent",
    "GeneralAgent": "general_agent",
    "StreamAgentState": "general_agent",
    "StructuredResponseAgent": "structured_response_agent",
}

__all__ = list(_EXPORT_TO_MODULE)


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
