from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "FusionResult": "zuno.platform.services.retrieval.models",
    "RetrievalFusion": "zuno.platform.services.retrieval.fusion",
    "RetrievedDocument": "zuno.platform.services.retrieval.models",
}

__all__ = [
    "FusionResult",
    "RetrievalFusion",
    "RetrievedDocument",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
