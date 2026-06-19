from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RetrievalRequest:
    query: str
    knowledge_ids: list[str]
    mode: str = "auto"
    requested_profile: str = "auto"
    top_k: int | None = None
    score_threshold: float | None = None
    rerank_enabled: bool | None = None
    rerank_top_k: int | None = None
    graph_hop_limit: int | None = None
    max_paths_per_entity: int | None = None
    needs_query_rewrite: bool = True
    trace_enabled: bool = True
    budget_policy: dict[str, Any] = field(default_factory=dict)
    fallback_policy: dict[str, Any] = field(default_factory=dict)
    trace_policy: dict[str, Any] = field(default_factory=dict)
    scope_policy: dict[str, Any] = field(default_factory=dict)
    index_version: dict[str, Any] = field(default_factory=dict)
    index_health: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProcessedQuery:
    original_query: str
    normalized_query: str
    rewritten_queries: list[str]
    intent_labels: list[str] = field(default_factory=list)
    query_features: dict[str, Any] = field(default_factory=dict)
    route_hints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetrievalPlan:
    requested_mode: str
    resolved_mode: str
    internal_route: str
    route_trace: dict[str, Any]
    requested_profile: str
    resolved_profile: str
    enabled_retrievers: list[str]
    retriever_configs: dict[str, dict[str, Any]]
    fusion_policy: dict[str, Any]
    rerank_policy: dict[str, Any]
    budget_policy: dict[str, Any]
    fallback_policy: dict[str, Any]
    trace_policy: dict[str, Any]
    scope_policy: dict[str, Any]
    index_version: dict[str, Any]
    index_health: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_mode": self.requested_mode,
            "resolved_mode": self.resolved_mode,
            "internal_route": self.internal_route,
            "route_trace": self.route_trace,
            "requested_profile": self.requested_profile,
            "resolved_profile": self.resolved_profile,
            "enabled_retrievers": list(self.enabled_retrievers),
            "retriever_configs": self.retriever_configs,
            "fusion_policy": self.fusion_policy,
            "rerank_policy": self.rerank_policy,
            "budget_policy": self.budget_policy,
            "fallback_policy": self.fallback_policy,
            "trace_policy": self.trace_policy,
            "scope_policy": self.scope_policy,
            "index_version": self.index_version,
            "index_health": self.index_health,
        }


@dataclass(slots=True)
class RetrievedDocument:
    chunk_id: str
    knowledge_id: str
    file_id: str
    file_name: str
    content: str
    summary: str
    score: float
    normalized_score: float | None
    source_type: str
    source_backend: str
    retrieval_reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "knowledge_id": self.knowledge_id,
            "file_id": self.file_id,
            "file_name": self.file_name,
            "content": self.content,
            "summary": self.summary,
            "score": self.score,
            "normalized_score": self.normalized_score,
            "source_type": self.source_type,
            "source_backend": self.source_backend,
            "retrieval_reason": self.retrieval_reason,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class FusionResult:
    documents: list[RetrievedDocument]
    dropped_documents: list[RetrievedDocument]
    fusion_metadata: dict[str, Any]
    rerank_metadata: dict[str, Any]
