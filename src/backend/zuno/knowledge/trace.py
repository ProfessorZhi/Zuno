from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.platform.services.retrieval.trace_artifacts import (
        EvidenceChecker,
        EvidenceVerdict,
        HookPoint,
        RuntimeTraceBuilder,
        RuntimeTraceEvent,
        TraceArtifactManifest,
        enrich_trace_metadata_with_artifacts,
    )
    from zuno.platform.services.graphrag.query_service import (
        GraphRAGProjectSnapshot,
        KnowledgeQueryResult,
    )
    from zuno.platform.services.retrieval.models import ProcessedQuery, RetrievalPlan


_EXPORT_TO_MODULE = {
    "EvidenceChecker": "zuno.platform.services.retrieval.trace_artifacts",
    "EvidenceVerdict": "zuno.platform.services.retrieval.trace_artifacts",
    "GraphRAGProjectSnapshot": "zuno.platform.services.graphrag.query_service",
    "HookPoint": "zuno.platform.services.retrieval.trace_artifacts",
    "KnowledgeQueryResult": "zuno.platform.services.graphrag.query_service",
    "ProcessedQuery": "zuno.platform.services.retrieval.models",
    "RetrievalPlan": "zuno.platform.services.retrieval.models",
    "RuntimeTraceBuilder": "zuno.platform.services.retrieval.trace_artifacts",
    "RuntimeTraceEvent": "zuno.platform.services.retrieval.trace_artifacts",
    "TraceArtifactManifest": "zuno.platform.services.retrieval.trace_artifacts",
    "enrich_trace_metadata_with_artifacts": "zuno.platform.services.retrieval.trace_artifacts",
}

__all__ = [
    "EvidenceChecker",
    "EvidenceVerdict",
    "GraphRAGProjectSnapshot",
    "HookPoint",
    "KnowledgeQueryResult",
    "ProcessedQuery",
    "RetrievalPlan",
    "RuntimeTraceBuilder",
    "RuntimeTraceEvent",
    "TraceArtifactManifest",
    "enrich_trace_metadata_with_artifacts",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
