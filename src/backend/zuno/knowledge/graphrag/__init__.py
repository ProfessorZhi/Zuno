from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.knowledge.contracts import (
        GraphRAGProjectContract,
        GraphRAGProjectLoader,
        GraphRAGSettingsValidator,
        LoadedGraphRAGProject,
        ProjectReadiness,
        normalize_retrieval_mode,
    )
    from zuno.platform.services.graphrag.query_service import (
        GraphRAGProjectSnapshot,
        GraphRAGQueryService,
    )


_EXPORT_TO_MODULE = {
    "GraphRAGProjectContract": "zuno.knowledge.contracts",
    "GraphRAGProjectLoader": "zuno.knowledge.contracts",
    "GraphRAGProjectSnapshot": "zuno.platform.services.graphrag.query_service",
    "GraphRAGQueryService": "zuno.platform.services.graphrag.query_service",
    "GraphRAGSettingsValidator": "zuno.knowledge.contracts",
    "LoadedGraphRAGProject": "zuno.knowledge.contracts",
    "ProjectReadiness": "zuno.knowledge.contracts",
    "normalize_retrieval_mode": "zuno.knowledge.contracts",
}

__all__ = [
    "GraphRAGProjectContract",
    "GraphRAGProjectLoader",
    "GraphRAGProjectSnapshot",
    "GraphRAGQueryService",
    "GraphRAGSettingsValidator",
    "LoadedGraphRAGProject",
    "ProjectReadiness",
    "normalize_retrieval_mode",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
