from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "ProcessedQuery": "zuno.platform.services.retrieval.models",
    "RetrievalOrchestrator": "zuno.platform.services.retrieval.orchestrator",
    "RetrievalPlan": "zuno.platform.services.retrieval.models",
    "RetrievalPlanner": "zuno.platform.services.retrieval.planner",
    "RetrievalRequest": "zuno.platform.services.retrieval.models",
    "RetrievedDocument": "zuno.platform.services.retrieval.models",
}

__all__ = [
    "ProcessedQuery",
    "RetrievalOrchestrator",
    "RetrievalPlan",
    "RetrievalPlanner",
    "RetrievalRequest",
    "RetrievedDocument",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
