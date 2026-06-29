from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "GraphRAGProjectSnapshot": "zuno.platform.services.graphrag.query_service",
    "GraphRAGQueryService": "zuno.platform.services.graphrag.query_service",
    "KnowledgeQueryResult": "zuno.platform.services.graphrag.query_service",
    "KnowledgeQueryService": "zuno.platform.services.application.knowledge",
}

__all__ = [
    "GraphRAGProjectSnapshot",
    "GraphRAGQueryService",
    "KnowledgeQueryResult",
    "KnowledgeQueryService",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
