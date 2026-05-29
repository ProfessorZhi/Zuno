from __future__ import annotations

from agentchat.services.graphrag.models import normalize_retrieval_mode
from agentchat.services.retrieval.models import ProcessedQuery, RetrievalPlan, RetrievalRequest


class RetrievalPlanner:
    def __init__(self, *, enable_keyword_recall: bool = False):
        self.enable_keyword_recall = enable_keyword_recall

    def build_plan(
        self,
        request: RetrievalRequest,
        processed_query: ProcessedQuery,
        *,
        knowledge_capability: str = "rag",
    ) -> RetrievalPlan:
        requested_mode = normalize_retrieval_mode(request.mode)
        relation_question = bool(processed_query.query_features.get("relation_question"))

        if requested_mode == "auto":
            resolved_mode = "hybrid" if relation_question and knowledge_capability == "rag_graph" else "rag"
        else:
            resolved_mode = requested_mode

        enabled_retrievers = ["vector"]
        if self.enable_keyword_recall and resolved_mode in {"rag", "hybrid"}:
            enabled_retrievers.append("bm25")
        if resolved_mode in {"graphrag", "hybrid"} and knowledge_capability == "rag_graph":
            enabled_retrievers.append("graph")

        return RetrievalPlan(
            requested_mode=requested_mode,
            resolved_mode=resolved_mode,
            enabled_retrievers=enabled_retrievers,
            retriever_configs={name: {} for name in enabled_retrievers},
            fusion_policy={"name": "query_aware"},
            rerank_policy={"enabled": request.rerank_enabled},
            fallback_policy={"allow_retry": True},
            trace_policy={"enabled": request.trace_enabled},
        )
