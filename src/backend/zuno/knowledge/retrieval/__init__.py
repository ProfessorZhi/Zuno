from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.platform.services.retrieval.models import (
        ProcessedQuery,
        PRODUCT_MODES,
        QUERY_METHODS,
        QUERY_METHOD_ROUTER,
        RetrievalPlan,
        RetrievalRequest,
        RetrievedDocument,
        normalize_product_mode,
    )
    from zuno.platform.services.retrieval.orchestrator import RetrievalOrchestrator
    from zuno.platform.services.retrieval.planner import RetrievalPlanner


_EXPORT_TO_MODULE = {
    "ProcessedQuery": "zuno.platform.services.retrieval.models",
    "PRODUCT_MODES": "zuno.platform.services.retrieval.models",
    "QUERY_METHODS": "zuno.platform.services.retrieval.models",
    "QUERY_METHOD_ROUTER": "zuno.platform.services.retrieval.models",
    "RetrievalOrchestrator": "zuno.platform.services.retrieval.orchestrator",
    "RetrievalPlan": "zuno.platform.services.retrieval.models",
    "RetrievalPlanner": "zuno.platform.services.retrieval.planner",
    "RetrievalRequest": "zuno.platform.services.retrieval.models",
    "RetrievedDocument": "zuno.platform.services.retrieval.models",
    "normalize_product_mode": "zuno.platform.services.retrieval.models",
}

__all__ = [
    "ProcessedQuery",
    "PRODUCT_MODES",
    "QUERY_METHODS",
    "QUERY_METHOD_ROUTER",
    "RetrievalOrchestrator",
    "RetrievalPlan",
    "RetrievalPlanner",
    "RetrievalRequest",
    "RetrievedDocument",
    "normalize_product_mode",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
