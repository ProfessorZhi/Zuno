from __future__ import annotations

from zuno.services.graphrag.models import normalize_retrieval_mode
from zuno.services.retrieval.models import ProcessedQuery, RetrievalPlan, RetrievalRequest


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
        rerank_available: bool = True,
    ) -> RetrievalPlan:
        requested_mode = normalize_retrieval_mode(request.mode)
        relation_question = bool(processed_query.query_features.get("relation_question"))
        global_question = bool(processed_query.query_features.get("global_question"))
        evidence_required = bool(processed_query.query_features.get("evidence_required"))
        scope_policy = dict(request.scope_policy or {})
        index_version = dict(request.index_version or {})
        index_health = dict(request.index_health or {})
        scope_status = str(scope_policy.get("status") or "active").strip().lower()
        graph_health = str(index_health.get("graph") or index_health.get("graph_status") or "ready").strip().lower()
        community_health = str(
            index_health.get("community")
            or index_health.get("community_status")
            or "not_built"
        ).strip().lower()
        graph_available = knowledge_capability == "rag_graph" and graph_health not in {"unavailable", "failed", "stale"}
        community_ready = community_health in {"ready", "active"}

        if requested_mode == "auto":
            resolved_mode = "rag_graph_deep" if knowledge_capability == "rag_graph" else "rag"
        else:
            resolved_mode = requested_mode
        if scope_status != "active":
            resolved_mode = "rag"
        requested_profile = str(request.requested_profile or "auto").strip() or "auto"

        internal_route = "standard_rag"
        route_trace = {
            "requested_internal_route": "standard_rag",
            "degraded_from": None,
            "graph_required": False,
            "community_required": False,
            "local_graph_required": False,
        }
        if resolved_mode == "rag_graph_deep":
            if global_question and evidence_required:
                internal_route = "drift_like"
            elif global_question:
                internal_route = "community_global"
            elif relation_question:
                internal_route = "local_graphrag"
            else:
                internal_route = "standard_rag"
        elif resolved_mode == "local_graphrag":
            internal_route = "local_graphrag"
        elif resolved_mode == "community_global":
            internal_route = "community_global"
        elif resolved_mode == "drift_like":
            internal_route = "drift_like"

        route_trace["requested_internal_route"] = internal_route
        route_trace["graph_required"] = internal_route in {"local_graphrag", "drift_like"}
        route_trace["community_required"] = internal_route in {"community_global", "drift_like"}
        route_trace["local_graph_required"] = internal_route in {"local_graphrag", "drift_like"}

        if internal_route in {"community_global", "drift_like"} and not community_ready:
            route_trace["degraded_from"] = internal_route
            internal_route = "local_graphrag"

        if internal_route == "local_graphrag" and not graph_available:
            route_trace["degraded_from"] = route_trace["degraded_from"] or "local_graphrag"
            internal_route = "standard_rag"
            resolved_mode = "rag"

        enabled_retrievers = [] if scope_status != "active" else ["vector"]
        if enabled_retrievers and self.enable_keyword_recall and (
            internal_route in {"standard_rag", "local_graphrag"} or resolved_mode == "rag_graph_deep"
        ):
            enabled_retrievers.append("bm25")
        if internal_route == "local_graphrag" and graph_available:
            enabled_retrievers.append("graph")
        resolved_profile = self._resolve_profile(
            requested_profile,
            resolved_mode=(
                "graphrag"
                if internal_route == "local_graphrag"
                else ("hybrid" if internal_route == "standard_rag" and resolved_mode != "rag" else resolved_mode)
            ),
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
        if route_trace["degraded_from"] in {"community_global", "drift_like"}:
            fallback_policy["community_degraded"] = True
        if not graph_available and knowledge_capability == "rag_graph":
            fallback_policy["graph_degraded"] = True
        rerank_enabled = request.rerank_enabled is not False and rerank_available
        if request.rerank_enabled is not False and not rerank_available:
            fallback_policy["rerank_degraded"] = True
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
            internal_route=internal_route,
            route_trace=route_trace,
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
            rerank_policy={
                "enabled": rerank_enabled,
                "top_k": request.rerank_top_k or request.top_k,
                "strategy": "rerank" if rerank_enabled else "score_sort",
            },
            budget_policy=budget_policy,
            fallback_policy=fallback_policy,
            trace_policy=trace_policy,
            scope_policy=scope_policy,
            index_version=index_version,
            index_health=index_health,
        )
