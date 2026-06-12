import asyncio

from agentchat.services.retrieval.models import FusionResult, ProcessedQuery, RetrievedDocument
from agentchat.services.retrieval.orchestrator import RetrievalOrchestrator


class _FakeQueryExpander:
    async def expand(self, query: str) -> list[str]:
        return [query, f"{query} rewritten"]


class _FakeQueryProcessor:
    async def process(self, query: str):
        return ProcessedQuery(
            original_query=query,
            normalized_query=query,
            rewritten_queries=[query],
            intent_labels=[],
            query_features={"relation_question": False, "keyword_heavy": False},
            route_hints=[],
        )


class _FakeVectorRetriever:
    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        if query.endswith("rewritten"):
            return {
                "content": "Indemnity clause survives termination.",
                "raw_content": "Indemnity clause survives termination.",
                "documents": [
                    {
                        "chunk_id": "chunk_1",
                        "knowledge_id": knowledge_ids[0],
                        "file_id": "file_1",
                        "file_name": "contract.md",
                        "content": "Indemnity clause survives termination.",
                        "score": 0.91,
                    }
                ],
                "document_count": 1,
            }
        return {
            "content": "",
            "raw_content": "",
            "documents": [],
            "document_count": 0,
        }


class _EmptyRetriever:
    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        return {"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}


class _FakeFusion:
    def merge(self, *, query: str, documents_by_source: dict[str, list[RetrievedDocument]], top_k: int | None = None):
        merged: list[RetrievedDocument] = []
        for source_docs in documents_by_source.values():
            merged.extend(source_docs)
        if top_k is not None:
            merged = merged[:top_k]
        return FusionResult(
            documents=merged,
            dropped_documents=[],
            fusion_metadata={"query": query},
            rerank_metadata={},
        )


def test_retrieval_orchestrator_preserves_governance_contract_across_fallback():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeVectorRetriever(),
        keyword_retriever=_EmptyRetriever(),
        graph_retriever=_EmptyRetriever(),
        query_expander=_FakeQueryExpander(),
        query_processor=_FakeQueryProcessor(),
        fusion=_FakeFusion(),
        max_rounds=2,
    )

    result = asyncio.run(
        orchestrator.run(
            mode="rag",
            query="review indemnity",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "top_k": 3,
                "requested_profile": "contract_review_strict",
                "budget_policy": {"max_context_chars": 4000},
                "scope_policy": {"status": "active", "knowledge_ids": ["kb_1"]},
                "index_version": {"vector": "vector_v2", "graph": "graph_v2"},
                "index_health": {"vector": "ready", "graph": "ready"},
                "fallback_policy": {
                    "allow_retry": True,
                    "route_broadening": False,
                    "query_rewrite_retry": True,
                    "max_rounds": 2,
                },
                "trace_policy": {"enabled": True, "include_rounds": False},
            },
        )
    )

    assert result["fallback_triggered"] is True
    assert result["content"] == "Indemnity clause survives termination."
    assert result["metadata"]["requested_mode"] == "rag"
    assert result["metadata"]["requested_profile"] == "contract_review_strict"
    assert result["metadata"]["resolved_profile"] == "contract_review_strict"
    assert result["metadata"]["budget_policy"]["max_context_chars"] == 4000
    assert result["metadata"]["fallback_policy"]["route_broadening"] is False
    assert result["metadata"]["trace_policy"]["include_rounds"] is False
    assert result["metadata"]["scope_policy"]["status"] == "active"
    assert result["metadata"]["index_version"]["graph"] == "graph_v2"
    assert result["metadata"]["index_health"]["graph"] == "ready"
    assert result["metadata"]["round_count"] == 2
    assert result["metadata"]["rounds"][1]["trigger"] == "query_rewrite_retry"
