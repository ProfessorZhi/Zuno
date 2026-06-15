from __future__ import annotations

import re
from typing import Any

from zuno.api.services.knowledge import KnowledgeService
from zuno.services.graphrag.retriever import GraphRetriever
from zuno.services.rag.retrieval import MixRetrival
from zuno.settings import app_settings


def _guess_keyword_heavy(query: str) -> bool:
    tokens = re.findall(r"[A-Za-z0-9_]{3,}", str(query or ""))
    return len(tokens) >= 2 and any(token.isupper() for token in tokens)


class QueryProcessor:
    async def process(self, query: str) -> Any:
        normalized = str(query or "").strip()
        return {
            "original_query": query,
            "normalized_query": normalized,
            "rewritten_queries": [normalized] if normalized else [query],
            "intent_labels": [],
            "query_features": {
                "relation_question": "关系" in normalized
                or any(word in normalized.lower() for word in ["relation", "relationship", "graph"]),
                "keyword_heavy": _guess_keyword_heavy(normalized),
            },
            "route_hints": [],
        }


class VectorRetrieverAdapter:
    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        from zuno.services.rag.handler import RagHandler

        options = options or {}
        return await RagHandler._retrieve_ranked_documents_rag_detail(
            query,
            knowledge_ids,
            knowledge_ids,
            min_score=options.get("score_threshold"),
            top_k=options.get("top_k"),
            needs_query_rewrite=options.get("needs_query_rewrite", True),
            retrieval_options=options,
        )


class RagRetrieverAdapter(VectorRetrieverAdapter):
    pass


class BM25RetrieverAdapter:
    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        if not app_settings.rag.enable_elasticsearch:
            return {"content": "", "raw_content": "", "documents": []}

        options = options or {}
        _runtime_settings = await KnowledgeService.get_runtime_settings(knowledge_ids[0]) if knowledge_ids else {
            "knowledge_config": {"index_settings": {"image_indexing_mode": "dual"}},
            "text_embedding_config": None,
            "vl_embedding_config": None,
        }
        es_documents = await MixRetrival.retrival_es_documents(query, knowledge_ids, "content")
        documents = []
        for doc in es_documents[: options.get("top_k") or 5]:
            payload = doc.to_dict() if hasattr(doc, "to_dict") else dict(doc)
            documents.append(payload)
        content = "\n".join(str(item.get("content") or "") for item in documents if item.get("content"))
        return {"content": content, "raw_content": content, "documents": documents}


KeywordRetrieverAdapter = BM25RetrieverAdapter


class GraphRetrieverAdapter:
    def __init__(self, retriever: GraphRetriever | None = None):
        self.retriever = retriever or GraphRetriever()

    def __getattr__(self, item):
        return getattr(self.retriever, item)

    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        options = options or {}
        knowledge_id = knowledge_ids[0] if knowledge_ids else ""
        runtime_settings = await KnowledgeService.get_runtime_settings(knowledge_id) if knowledge_id else {
            "domain_pack_id": None,
        }
        scope_policy = dict(options.get("scope_policy") or {})
        index_version = dict(options.get("index_version") or {})
        local_graph_retriever = runtime_settings.get("graph_retriever")
        if local_graph_retriever:
            return await local_graph_retriever.retrieve(
                query,
                knowledge_id,
                graph_hop_limit=options.get("graph_hop_limit", 2),
                max_paths_per_entity=options.get("max_paths_per_entity", 10),
                domain_pack_id=options.get("domain_pack_id") or runtime_settings.get("domain_pack_id"),
                index_version=index_version.get("graph"),
                status=scope_policy.get("status"),
            )
        return await self.retriever.retrieve(
            query,
            knowledge_id,
            graph_hop_limit=options.get("graph_hop_limit", 2),
            max_paths_per_entity=options.get("max_paths_per_entity", 10),
            domain_pack_id=options.get("domain_pack_id") or runtime_settings.get("domain_pack_id"),
            index_version=index_version.get("graph"),
            status=scope_policy.get("status"),
        )
