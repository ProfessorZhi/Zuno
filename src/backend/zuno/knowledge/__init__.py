from __future__ import annotations

from importlib import import_module
from typing import Any


_LAZY_EXPORT_TO_MODULE = {
    "FusionResult": "zuno.knowledge.fusion",
    "GraphRAGProjectContract": "zuno.knowledge.contracts",
    "GraphRAGProjectLoader": "zuno.knowledge.contracts",
    "GraphRAGProjectSnapshot": "zuno.knowledge.query_service",
    "GraphRAGQueryService": "zuno.knowledge.query_service",
    "GraphRAGSettingsValidator": "zuno.knowledge.contracts",
    "KnowledgeQueryResult": "zuno.knowledge.query_service",
    "KnowledgeQueryService": "zuno.knowledge.query_service",
    "LoadedGraphRAGProject": "zuno.knowledge.contracts",
    "ProcessedQuery": "zuno.knowledge.retrieval",
    "ProjectReadiness": "zuno.knowledge.contracts",
    "RetrievalFusion": "zuno.knowledge.fusion",
    "RetrievalOrchestrator": "zuno.knowledge.retrieval",
    "RetrievalPlan": "zuno.knowledge.retrieval",
    "RetrievalPlanner": "zuno.knowledge.retrieval",
    "RetrievalRequest": "zuno.knowledge.retrieval",
    "RetrievedDocument": "zuno.knowledge.retrieval",
    "normalize_retrieval_mode": "zuno.knowledge.contracts",
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
