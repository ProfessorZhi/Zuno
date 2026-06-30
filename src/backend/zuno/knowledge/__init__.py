from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.knowledge.agentic_graphrag import (
        AgenticGraphRAGTrace,
        AgenticRetrievalRuntime,
        AgenticRetrievalRuntimeRequest,
        AgenticRetrievalRuntimeResult,
        AgenticRetrievalRouter,
        Citation,
        CitationBuilder,
        EvidenceBundle,
        EvidenceItem,
        FusionStage,
        GraphRAGIndexPipelineContract,
        ProductMode,
        QueryMethod,
        RetrievalRouterDecision,
        RetrievalRouterInput,
        StagedFusionPlan,
        UnsupportedClaimCheck,
        UnsupportedClaimChecker,
    )
    from zuno.knowledge.contracts import (
        GraphRAGExtractorConfig,
        GraphRAGProjectContract,
        GraphRAGProjectLoader,
        GraphRAGSettingsValidator,
        LoadedGraphRAGProject,
        ProjectReadiness,
        normalize_retrieval_mode,
    )
    from zuno.knowledge.fusion import FusionResult, RetrievalFusion
    from zuno.knowledge.indexing import (
        IndexJobManifest,
        IndexQueryResult,
        KnowledgeIndexRuntime,
        KnowledgeSpaceManifest,
    )
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
    "AgenticGraphRAGTrace": "zuno.knowledge.agentic_graphrag",
    "AgenticRetrievalRuntime": "zuno.knowledge.agentic_graphrag",
    "AgenticRetrievalRuntimeRequest": "zuno.knowledge.agentic_graphrag",
    "AgenticRetrievalRuntimeResult": "zuno.knowledge.agentic_graphrag",
    "AgenticRetrievalRouter": "zuno.knowledge.agentic_graphrag",
    "Citation": "zuno.knowledge.agentic_graphrag",
    "CitationBuilder": "zuno.knowledge.agentic_graphrag",
    "EvidenceBundle": "zuno.knowledge.agentic_graphrag",
    "EvidenceChecker": "zuno.knowledge.trace",
    "EvidenceItem": "zuno.knowledge.agentic_graphrag",
    "EvidenceVerdict": "zuno.knowledge.trace",
    "FusionStage": "zuno.knowledge.agentic_graphrag",
    "FusionResult": "zuno.knowledge.fusion",
    "GraphRAGIndexPipelineContract": "zuno.knowledge.agentic_graphrag",
    "GraphRAGProjectContract": "zuno.knowledge.contracts",
    "GraphRAGExtractorConfig": "zuno.knowledge.contracts",
    "GraphRAGProjectLoader": "zuno.knowledge.contracts",
    "GraphRAGProjectSnapshot": "zuno.knowledge.query_service",
    "GraphRAGQueryService": "zuno.knowledge.query_service",
    "GraphRAGSettingsValidator": "zuno.knowledge.contracts",
    "HookPoint": "zuno.knowledge.trace",
    "IndexJobManifest": "zuno.knowledge.indexing",
    "IndexQueryResult": "zuno.knowledge.indexing",
    "KnowledgeQueryResult": "zuno.knowledge.query_service",
    "KnowledgeQueryService": "zuno.knowledge.query_service",
    "KnowledgeIndexRuntime": "zuno.knowledge.indexing",
    "KnowledgeSpaceManifest": "zuno.knowledge.indexing",
    "LoadedGraphRAGProject": "zuno.knowledge.contracts",
    "ProcessedQuery": "zuno.knowledge.retrieval",
    "ProductMode": "zuno.knowledge.agentic_graphrag",
    "ProjectReadiness": "zuno.knowledge.contracts",
    "QueryMethod": "zuno.knowledge.agentic_graphrag",
    "RetrievalFusion": "zuno.knowledge.fusion",
    "RetrievalOrchestrator": "zuno.knowledge.retrieval",
    "RetrievalPlan": "zuno.knowledge.retrieval",
    "RetrievalPlanner": "zuno.knowledge.retrieval",
    "RetrievalRequest": "zuno.knowledge.retrieval",
    "RetrievalRouterDecision": "zuno.knowledge.agentic_graphrag",
    "RetrievalRouterInput": "zuno.knowledge.agentic_graphrag",
    "RetrievedDocument": "zuno.knowledge.retrieval",
    "RuntimeTraceBuilder": "zuno.knowledge.trace",
    "RuntimeTraceEvent": "zuno.knowledge.trace",
    "StagedFusionPlan": "zuno.knowledge.agentic_graphrag",
    "TraceArtifactManifest": "zuno.knowledge.trace",
    "UnsupportedClaimCheck": "zuno.knowledge.agentic_graphrag",
    "UnsupportedClaimChecker": "zuno.knowledge.agentic_graphrag",
    "enrich_trace_metadata_with_artifacts": "zuno.knowledge.trace",
    "normalize_retrieval_mode": "zuno.knowledge.contracts",
}

__all__ = [
    "AgenticGraphRAGTrace",
    "AgenticRetrievalRuntime",
    "AgenticRetrievalRuntimeRequest",
    "AgenticRetrievalRuntimeResult",
    "AgenticRetrievalRouter",
    "Citation",
    "CitationBuilder",
    "EvidenceBundle",
    "EvidenceItem",
    "EvidenceChecker",
    "EvidenceVerdict",
    "FusionStage",
    "FusionResult",
    "GraphRAGIndexPipelineContract",
    "GraphRAGExtractorConfig",
    "GraphRAGProjectContract",
    "GraphRAGProjectLoader",
    "GraphRAGProjectSnapshot",
    "GraphRAGQueryService",
    "GraphRAGSettingsValidator",
    "HookPoint",
    "IndexJobManifest",
    "IndexQueryResult",
    "KnowledgeQueryResult",
    "KnowledgeQueryService",
    "KnowledgeIndexRuntime",
    "KnowledgeSpaceManifest",
    "LoadedGraphRAGProject",
    "ProductMode",
    "ProcessedQuery",
    "ProjectReadiness",
    "QueryMethod",
    "RetrievalFusion",
    "RetrievalOrchestrator",
    "RetrievalPlan",
    "RetrievalPlanner",
    "RetrievalRequest",
    "RetrievalRouterDecision",
    "RetrievalRouterInput",
    "RetrievedDocument",
    "RuntimeTraceBuilder",
    "RuntimeTraceEvent",
    "StagedFusionPlan",
    "TraceArtifactManifest",
    "UnsupportedClaimCheck",
    "UnsupportedClaimChecker",
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
