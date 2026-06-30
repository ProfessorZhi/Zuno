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
    from zuno.knowledge.fusion import FusionResult, RetrievalFusion
    from zuno.knowledge.query_service import (
        GraphRAGProjectSnapshot,
        GraphRAGQueryService,
        KnowledgeQueryResult,
        KnowledgeQueryService,
    )
    from zuno.knowledge.retrieval import (
        ProcessedQuery,
        RetrievalOrchestrator,
        RetrievalPlan,
        RetrievalPlanner,
        RetrievalRequest,
        RetrievedDocument,
    )
    from zuno.knowledge.trace import (
        EvidenceChecker,
        EvidenceVerdict,
        HookPoint,
        RuntimeTraceBuilder,
        RuntimeTraceEvent,
        TraceArtifactManifest,
        enrich_trace_metadata_with_artifacts,
    )


_LAZY_EXPORT_TO_MODULE = {
    "EvidenceChecker": "zuno.knowledge.trace",
    "EvidenceVerdict": "zuno.knowledge.trace",
    "FusionResult": "zuno.knowledge.fusion",
    "GraphRAGProjectContract": "zuno.knowledge.contracts",
    "GraphRAGProjectLoader": "zuno.knowledge.contracts",
    "GraphRAGProjectSnapshot": "zuno.knowledge.query_service",
    "GraphRAGQueryService": "zuno.knowledge.query_service",
    "GraphRAGSettingsValidator": "zuno.knowledge.contracts",
    "HookPoint": "zuno.knowledge.trace",
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
    "RuntimeTraceBuilder": "zuno.knowledge.trace",
    "RuntimeTraceEvent": "zuno.knowledge.trace",
    "TraceArtifactManifest": "zuno.knowledge.trace",
    "enrich_trace_metadata_with_artifacts": "zuno.knowledge.trace",
    "normalize_retrieval_mode": "zuno.knowledge.contracts",
}

__all__ = [
    "EvidenceChecker",
    "EvidenceVerdict",
    "FusionResult",
    "GraphRAGProjectContract",
    "GraphRAGProjectLoader",
    "GraphRAGProjectSnapshot",
    "GraphRAGQueryService",
    "GraphRAGSettingsValidator",
    "HookPoint",
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
    "RuntimeTraceBuilder",
    "RuntimeTraceEvent",
    "TraceArtifactManifest",
    "enrich_trace_metadata_with_artifacts",
    "normalize_retrieval_mode",
]


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
