from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zuno.platform.services.retrieval.trace_artifacts import enrich_trace_metadata_with_artifacts
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator
from zuno.services.retrieval.models import normalize_product_mode
from zuno.services.retrieval.planner import RetrievalPlanner


@dataclass(slots=True)
class GraphRAGProjectSnapshot:
    graphrag_project_id: str | None
    contract: dict[str, Any] = field(default_factory=dict)
    readiness: dict[str, Any] = field(default_factory=dict)
    prompt_categories: list[str] = field(default_factory=list)
    retrieval_settings: dict[str, Any] = field(default_factory=dict)
    index_version: dict[str, Any] = field(default_factory=dict)
    index_health: dict[str, Any] = field(default_factory=dict)
    knowledge_capability: str = "rag"
    query_policy: dict[str, Any] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)

    def default_query_method(self) -> str:
        method = str(self.contract.get("query_method") or "auto").strip().lower()
        return method if method in {"auto", "basic", "local", "global", "drift"} else "auto"

    def to_trace(self) -> dict[str, Any]:
        return {
            "graphrag_project_id": self.graphrag_project_id,
            "contract": dict(self.contract),
            "readiness": dict(self.readiness),
            "prompt_categories": list(self.prompt_categories),
            "index_version": dict(self.index_version),
            "index_health": dict(self.index_health),
        }


@dataclass(slots=True)
class KnowledgeQueryResult:
    graphrag_project_id: str | None
    answer: str
    requested_query_method: str
    resolved_query_method: str
    fallback_reason: str | None
    documents: list[dict[str, Any]]
    evidence: dict[str, Any]
    citations: list[str]
    retrievers_used: list[str]
    graph_paths: list[Any]
    communities: list[Any]
    prompt_version: str | None
    query_prompt_version: str | None
    index_version: dict[str, Any]
    community_version: str | None
    trace_metadata: dict[str, Any]
    raw_result: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "graphrag_project_id": self.graphrag_project_id,
            "answer": self.answer,
            "requested_query_method": self.requested_query_method,
            "resolved_query_method": self.resolved_query_method,
            "fallback_reason": self.fallback_reason,
            "documents": list(self.documents),
            "evidence": dict(self.evidence),
            "citations": list(self.citations),
            "retrievers_used": list(self.retrievers_used),
            "graph_paths": list(self.graph_paths),
            "communities": list(self.communities),
            "prompt_version": self.prompt_version,
            "query_prompt_version": self.query_prompt_version,
            "index_version": dict(self.index_version),
            "community_version": self.community_version,
            "trace_metadata": dict(self.trace_metadata),
        }


class GraphRAGQueryService:
    def __init__(self, orchestrator: RetrievalOrchestrator | None = None):
        self.orchestrator = orchestrator or RetrievalOrchestrator(
            planner=RetrievalPlanner(enable_keyword_recall=True)
        )

    async def query(
        self,
        *,
        query: str,
        knowledge_ids: list[str],
        snapshot: GraphRAGProjectSnapshot,
        product_mode: str | None = None,
        query_method: str | None = None,
        top_k: int | None = None,
    ) -> KnowledgeQueryResult:
        resolved_product_mode = normalize_product_mode(product_mode)
        requested_query_method = query_method or snapshot.default_query_method()
        if resolved_product_mode == "normal" and query_method is None:
            requested_query_method = "auto"
        retrieval_settings = dict(snapshot.retrieval_settings)
        if top_k is not None:
            retrieval_settings["top_k"] = top_k

        retrieval_options = {
            "product_mode": resolved_product_mode,
            "query_method": requested_query_method,
            "requested_profile": retrieval_settings.get("profile", "auto"),
            "top_k": retrieval_settings.get("top_k"),
            "rerank_enabled": retrieval_settings.get("rerank_enabled"),
            "rerank_top_k": retrieval_settings.get("rerank_top_k"),
            "score_threshold": retrieval_settings.get("score_threshold"),
            "graph_hop_limit": retrieval_settings.get("graph_hop_limit", 2),
            "max_paths_per_entity": retrieval_settings.get("max_paths_per_entity", 10),
            "knowledge_capability": snapshot.knowledge_capability,
            "graphrag_project": dict(snapshot.contract),
            "query_policy": dict(snapshot.query_policy),
            "budget_policy": {"product_mode": resolved_product_mode},
            "fallback_policy": {},
            "trace_policy": {"enabled": True},
            "scope_policy": {
                "knowledge_ids": list(knowledge_ids),
                "graphrag_project_id": snapshot.graphrag_project_id,
                "status": "active",
            },
            "index_version": dict(snapshot.index_version),
            "index_health": dict(snapshot.index_health),
        }
        mode = "enhanced_retrieval" if snapshot.knowledge_capability == "rag_graph" else "standard_retrieval"
        if resolved_product_mode == "normal":
            mode = "standard_retrieval"
        elif resolved_product_mode == "enhanced":
            mode = "enhanced_retrieval"
        raw_result = await self.orchestrator.run(
            mode,
            query,
            knowledge_ids,
            retrieval_options=retrieval_options,
        )
        return self._to_result(snapshot=snapshot, raw_result=raw_result, query=query)

    @staticmethod
    def _to_result(
        *,
        snapshot: GraphRAGProjectSnapshot,
        raw_result: dict[str, Any],
        query: str = "",
    ) -> KnowledgeQueryResult:
        metadata = dict(raw_result.get("metadata") or {})
        final_pass = dict(raw_result.get("final_pass_result") or {})
        evidence = dict(metadata.get("evidence_bundle") or {})
        citations = list(metadata.get("citation_chunks") or evidence.get("citation_chunks") or [])
        index_version = dict(metadata.get("index_version") or snapshot.index_version)
        contract = dict(snapshot.contract)
        fallback_reason = metadata.get("query_method_fallback_reason") or metadata.get("fallback_reason")
        trace_metadata = enrich_trace_metadata_with_artifacts(
            trace_metadata=metadata,
            query=query,
            answer=str(raw_result.get("content") or ""),
            documents=list(final_pass.get("documents") or []),
            evidence_bundle=evidence,
            citations=[str(item) for item in citations],
            fallback_reason=fallback_reason,
        )
        verdict_fallback_reason = (
            (trace_metadata.get("evidence_verdict") or {}).get("fallback_reason")
            if isinstance(trace_metadata.get("evidence_verdict"), dict)
            else None
        )
        return KnowledgeQueryResult(
            graphrag_project_id=snapshot.graphrag_project_id,
            answer=str(raw_result.get("content") or ""),
            requested_query_method=str(metadata.get("requested_query_method") or snapshot.default_query_method()),
            resolved_query_method=str(metadata.get("resolved_query_method") or snapshot.default_query_method()),
            fallback_reason=fallback_reason or verdict_fallback_reason or trace_metadata.get("fallback_reason"),
            documents=list(final_pass.get("documents") or []),
            evidence=evidence,
            citations=[str(item) for item in citations],
            retrievers_used=list(metadata.get("retrievers_used") or []),
            graph_paths=list(metadata.get("used_paths") or []),
            communities=list(metadata.get("used_communities") or []),
            prompt_version=metadata.get("prompt_version") or contract.get("prompt_version"),
            query_prompt_version=metadata.get("query_prompt_version") or contract.get("query_prompt_version"),
            index_version=index_version,
            community_version=contract.get("community_version"),
            trace_metadata=trace_metadata,
            raw_result=dict(raw_result),
        )


__all__ = [
    "GraphRAGProjectSnapshot",
    "GraphRAGQueryService",
    "KnowledgeQueryResult",
]
