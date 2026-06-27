from __future__ import annotations

from importlib import import_module
from typing import Any

from zuno.services.graphrag import GraphRAGProjectContract, normalize_retrieval_mode
from zuno.services.graphrag.project import (
    GraphRAGProjectLoader,
    GraphRAGSettingsValidator,
    LoadedGraphRAGProject,
    ProjectReadiness,
)


_LAZY_EXPORT_TO_MODULE = {
    "FusionResult": "zuno.services.retrieval.models",
    "GraphRAGProjectSnapshot": "zuno.services.graphrag.query_service",
    "GraphRAGQueryService": "zuno.services.graphrag.query_service",
    "KnowledgeQueryResult": "zuno.services.graphrag.query_service",
    "KnowledgeQueryService": "zuno.services.application.knowledge",
    "ProcessedQuery": "zuno.services.retrieval.models",
    "RetrievalFusion": "zuno.services.retrieval.fusion",
    "RetrievalOrchestrator": "zuno.services.retrieval.orchestrator",
    "RetrievalPlan": "zuno.services.retrieval.models",
    "RetrievalPlanner": "zuno.services.retrieval.planner",
    "RetrievalRequest": "zuno.services.retrieval.models",
    "RetrievedDocument": "zuno.services.retrieval.models",
}

__all__ = [
    "FusionResult",
    "GraphRAGProjectContract",
    "GraphRAGProjectLoader",
    "GraphRAGProjectSnapshot",
    "GraphRAGQueryService",
    "GraphRAGSettingsValidator",
    "KnowledgeQueryResult",
    "KnowledgeQueryService",
    "LoadedGraphRAGProject",
    "ProcessedQuery",
    "ProjectReadiness",
    "RetrievalFusion",
    "RetrievalOrchestrator",
    "RetrievalPlan",
    "RetrievalPlanner",
    "RetrievalRequest",
    "RetrievedDocument",
    "normalize_retrieval_mode",
]


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
