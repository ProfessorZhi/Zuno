from __future__ import annotations

from agentchat.services.graphrag.models import normalize_retrieval_mode
from agentchat.services.retrieval.models import ProcessedQuery, RetrievalPlan, RetrievalRequest


class RetrievalPlanner:
    def __init__(self, *, enable_keyword_recall: bool = False):
        self.enable_keyword_recall = enable_keyword_recall

    @staticmethod
    def _resolve_profile(
        requested_profile: str,
        *,
        resolved_mode: str,
        relation_question: bool,
        knowledge_capability: str,
    ) -> str:
        normalized = str(requested_profile or "auto").strip().lower()
        if normalized and normalized not in {"auto", "default"}:
            return requested_profile
        if resolved_mode == "hybrid":
            return "relation_hybrid" if relation_question else "hybrid_balanced"
        if resolved_mode == "graphrag":
            return "graph_relation" if knowledge_capability == "rag_graph" else "graph_expanded"
        return "vector_rerank"

    def build_plan(
        self,
        request: RetrievalRequest,
        processed_query: ProcessedQuery,
        *,
        knowledge_capability: str = "rag",
    ) -> RetrievalPlan:
        requested_mode = normalize_retrieval_mode(request.mode)
        relation_question = bool(processed_query.query_features.get("relation_question"))
        scope_policy = dict(request.scope_policy or {})
        index_version = dict(request.index_version or {})
        index_health = dict(request.index_health or {})
        scope_status = str(scope_policy.get("status") or "active").strip().lower()
        graph_health = str(index_health.get("graph") or index_health.get("graph_status") or "ready").strip().lower()

        if requested_mode == "auto":
            resolved_mode = "hybrid" if relation_question and knowledge_capability == "rag_graph" else "rag"
        else:
            resolved_mode = requested_mode
        if scope_status != "active":
            resolved_mode = "rag"
        requested_profile = str(request.requested_profile or "auto").strip() or "auto"

        enabled_retrievers = [] if scope_status != "active" else ["vector"]
        if enabled_retrievers and self.enable_keyword_recall and resolved_mode in {"rag", "hybrid"}:
            enabled_retrievers.append("bm25")
        if (
            resolved_mode in {"graphrag", "hybrid"}
            and knowledge_capability == "rag_graph"
            and graph_health not in {"unavailable", "failed", "stale"}
        ):
            enabled_retrievers.append("graph")
        if resolved_mode == "graphrag" and "graph" not in enabled_retrievers:
            resolved_mode = "rag"
        resolved_profile = self._resolve_profile(
            requested_profile,
            resolved_mode=resolved_mode,
            relation_question=relation_question,
            knowledge_capability=knowledge_capability,
        )
        budget_policy = {
            "top_k": request.top_k,
            "rerank_top_k": request.rerank_top_k or request.top_k,
            "graph_hop_limit": request.graph_hop_limit,
            "max_paths_per_entity": request.max_paths_per_entity,
            "rewrite_enabled": request.needs_query_rewrite,
        }
        budget_policy.update(request.budget_policy or {})
        fallback_policy = {
            "allow_retry": True,
            "route_broadening": True,
            "query_rewrite_retry": True,
        }
        fallback_policy.update(request.fallback_policy or {})
        if scope_status != "active":
            fallback_policy["allow_retry"] = False
        if graph_health in {"unavailable", "failed", "stale"}:
            fallback_policy.setdefault("graph_degraded", True)
        trace_policy = {
            "enabled": request.trace_enabled,
            "include_processed_query": True,
            "include_retriever_runs": True,
            "include_rounds": True,
        }
        trace_policy.update(request.trace_policy or {})

        return RetrievalPlan(
            requested_mode=requested_mode,
            resolved_mode=resolved_mode,
            requested_profile=requested_profile,
            resolved_profile=resolved_profile,
            enabled_retrievers=enabled_retrievers,
            retriever_configs={
                name: {
                    "top_k": request.top_k,
                    "score_threshold": request.score_threshold,
                    "rerank_enabled": request.rerank_enabled,
                    "rerank_top_k": request.rerank_top_k,
                    "graph_hop_limit": request.graph_hop_limit,
                    "max_paths_per_entity": request.max_paths_per_entity,
                }
                for name in enabled_retrievers
            },
            fusion_policy={"name": "query_aware"},
            rerank_policy={"enabled": request.rerank_enabled, "top_k": request.rerank_top_k or request.top_k},
            budget_policy=budget_policy,
            fallback_policy=fallback_policy,
            trace_policy=trace_policy,
            scope_policy=scope_policy,
            index_version=index_version,
            index_health=index_health,
        )
