from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "AgentConfig": ("agents", "AgentConfig"),
    "EmitEventAgentMiddleware": ("agents", "EmitEventAgentMiddleware"),
    "GeneralAgent": ("agents", "GeneralAgent"),
    "StreamAgentState": ("agents", "StreamAgentState"),
    "StructuredResponseAgent": ("agents", "StructuredResponseAgent"),
}

__all__ = list(_EXPORT_TO_MODULE)


def __getattr__(name: str) -> Any:
    target = _EXPORT_TO_MODULE.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    package_name, attr_name = target
    module = import_module(f"{__name__}.{package_name}")
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
