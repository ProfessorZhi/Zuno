import asyncio

from zuno.services.graphrag.models import normalize_retrieval_mode
from zuno.services.retrieval.models import ProcessedQuery
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator
from zuno.services.retrieval.planner import RetrievalPlanner


class _FakeRetriever:
    def __init__(self, payload):
        self.payload = payload

    async def retrieve(self, query, knowledge_ids, options=None):
        return self.payload


class _FakeProcessor:
    async def process(self, query: str):
        return ProcessedQuery(
            original_query=query,
            normalized_query=query,
            rewritten_queries=[query],
            intent_labels=[],
            query_features={"relation_question": False, "keyword_heavy": False},
            route_hints=[],
        )


def _vector_payload():
    return {
        "content": "vector evidence",
        "raw_content": "vector evidence",
        "documents": [
            {
                "chunk_id": "c1",
                "knowledge_id": "kb_1",
                "file_id": "f1",
                "file_name": "a.md",
                "content": "vector evidence",
                "score": 0.91,
            }
        ],
        "document_count": 1,
        "requested_top_k": 5,
        "top_score": 0.91,
        "score_threshold": 0.2,
    }


def _bm25_payload():
    return {
        "content": "keyword evidence",
        "raw_content": "keyword evidence",
        "documents": [
            {
                "chunk_id": "c2",
                "knowledge_id": "kb_1",
                "file_id": "f2",
                "file_name": "b.md",
                "content": "keyword evidence",
                "score": 0.74,
            }
        ],
    }


def test_standard_retrieval_alias_normalizes_to_rag_runtime():
    assert normalize_retrieval_mode("standard_retrieval") == "rag"


def test_standard_retrieval_uses_vector_bm25_fusion_and_rerank_when_available():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever(_vector_payload()),
        keyword_retriever=_FakeRetriever(_bm25_payload()),
        graph_retriever=_FakeRetriever({"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        query_processor=_FakeProcessor(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="standard_retrieval",
            query="redis persistence mode",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag",
                "index_health": {"vector": "ready", "graph": "unavailable"},
                "trace_policy": {"enabled": True},
                "bm25_available": True,
                "rerank_available": True,
                "rerank_enabled": True,
                "score_threshold": 0.2,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["used_vector"] is True
    assert metadata["used_bm25"] is True
    assert metadata["fusion_used"] is True
    assert metadata["rerank_used"] is True
    assert metadata["bm25_available"] is True
    assert metadata["bm25_fallback_reason"] is None


def test_standard_retrieval_falls_back_to_vector_when_bm25_is_unavailable():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever(_vector_payload()),
        keyword_retriever=_FakeRetriever(_bm25_payload()),
        graph_retriever=_FakeRetriever({"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}),
        planner=RetrievalPlanner(enable_keyword_recall=False),
        query_processor=_FakeProcessor(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="standard_retrieval",
            query="redis persistence mode",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag",
                "index_health": {"vector": "ready", "graph": "unavailable"},
                "trace_policy": {"enabled": True},
                "bm25_available": False,
                "rerank_available": True,
                "rerank_enabled": True,
                "score_threshold": 0.2,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["used_vector"] is True
    assert metadata["used_bm25"] is False
    assert metadata["fusion_used"] is True
    assert metadata["rerank_used"] is True
    assert metadata["bm25_available"] is False
    assert metadata["bm25_fallback_reason"] == "bm25_backend_unavailable"
