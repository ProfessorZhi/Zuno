import asyncio
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.retrieval.models import FusionResult, RetrievedDocument
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator
from zuno.services.retrieval.retrievers import QueryProcessor


def _doc(chunk_id: str, file_name: str, score: float, *, matched_by=None):
    return RetrievedDocument(
        chunk_id=chunk_id,
        knowledge_id="kb_1",
        file_id=file_name,
        file_name=file_name,
        content=file_name,
        summary="",
        score=score,
        normalized_score=None,
        source_type="vector",
        source_backend="milvus",
        retrieval_reason="vector",
        metadata={"matched_by": list(matched_by or ["vector"])},
    )


class _StaticExpander:
    def __init__(self, rewrites):
        self.rewrites = rewrites

    async def expand(self, query: str):
        return [query, *self.rewrites]


class _MappingRetriever:
    def __init__(self, mapping):
        self.mapping = mapping

    async def retrieve(self, query, knowledge_ids, options=None):
        docs = self.mapping.get(query, [])
        return {
            "content": "\n".join(doc.file_name for doc in docs),
            "raw_content": "\n".join(doc.file_name for doc in docs),
            "documents": [
                {
                    "chunk_id": doc.chunk_id,
                    "knowledge_id": doc.knowledge_id,
                    "file_id": doc.file_id,
                    "file_name": doc.file_name,
                    "content": doc.content,
                    "score": doc.score,
                    "metadata": dict(doc.metadata),
                }
                for doc in docs
            ],
            "document_count": len(docs),
        }


class _EmptyGraphRetriever:
    def _extract_query_seeds(self, query):
        return []

    def _is_graph_worthy_query(self, query, seed_entities):
        return False

    async def retrieve(self, query, knowledge_ids, options=None):
        return {"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}


class _RequeryAwareFusion:
    def __init__(self, *, use_requery_docs: bool):
        self.use_requery_docs = use_requery_docs

    def merge(self, *, query: str, documents_by_source, top_k=None):
        vector_docs = list(documents_by_source.get("vector") or [])
        requery_docs = list(documents_by_source.get("requery") or [])
        docs = list(vector_docs)
        if self.use_requery_docs and requery_docs:
            docs = [vector_docs[0], requery_docs[0], *vector_docs[1:]]
        if top_k is not None:
            docs = docs[:top_k]
        return FusionResult(
            documents=docs,
            dropped_documents=[],
            fusion_metadata={"strategy": "baseline_preserving"},
            rerank_metadata={},
        )


def test_hail_from_query_triggers_proactive_requery():
    query = "Hayden is a singer-songwriter from Canada, but where does Buck-Tick hail from?"
    rewrite = "Where does Buck-Tick hail from?"
    retriever = _MappingRetriever(
        {
            query: [_doc("v1", "Buck-Tick", 0.91), _doc("v2", "Atsushi Sakurai", 0.82)],
            rewrite: [_doc("r1", "Hayden (musician)", 0.88, matched_by=["requery"])],
        }
    )
    orchestrator = RetrievalOrchestrator(
        rag_retriever=retriever,
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_EmptyGraphRetriever(),
        query_expander=_StaticExpander([rewrite]),
        query_processor=QueryProcessor(),
        fusion=_RequeryAwareFusion(use_requery_docs=True),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "unavailable", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    assert result["metadata"]["requery_used"] is True
    assert result["metadata"]["requery_triggered_reason"] is not None
    assert result["metadata"]["requery_queries"] == [rewrite]
    assert result["metadata"]["requery_result_count"] == 1
    assert any(run["source"] == "requery" for run in result["metadata"]["retriever_runs"])


def test_located_in_what_city_query_triggers_proactive_requery():
    query = "Ralph Hefferline was a psychology professor at a university that is located in what city?"
    rewrite = "What city is Columbia University in?"
    retriever = _MappingRetriever(
        {
            query: [_doc("v1", "Ralph Hefferline", 0.95), _doc("v2", "Virginia Commonwealth University", 0.82)],
            rewrite: [_doc("r1", "Columbia University", 0.88, matched_by=["requery"])],
        }
    )
    orchestrator = RetrievalOrchestrator(
        rag_retriever=retriever,
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_EmptyGraphRetriever(),
        query_expander=_StaticExpander([rewrite]),
        query_processor=QueryProcessor(),
        fusion=_RequeryAwareFusion(use_requery_docs=True),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "unavailable", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    assert result["metadata"]["requery_used"] is True
    assert result["metadata"]["requery_triggered_reason"] is not None
    assert result["metadata"]["requery_result_count"] == 1


def test_simple_fact_query_does_not_trigger_proactive_requery():
    query = "What is Buck-Tick?"
    rewrite = "Explain Buck-Tick."
    retriever = _MappingRetriever({query: [_doc("v1", "Buck-Tick", 0.95), _doc("v2", "Atsushi Sakurai", 0.83)]})
    orchestrator = RetrievalOrchestrator(
        rag_retriever=retriever,
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_EmptyGraphRetriever(),
        query_expander=_StaticExpander([rewrite]),
        query_processor=QueryProcessor(),
        fusion=_RequeryAwareFusion(use_requery_docs=False),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "unavailable", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    assert result["metadata"]["requery_used"] is False
    assert result["metadata"]["requery_triggered_reason"] is None
    assert result["metadata"]["requery_queries"] == []


def test_low_confidence_requery_falls_back_to_standard_floor():
    query = "Ralph Hefferline was a psychology professor at a university that is located in what city?"
    rewrite = "What city is Columbia University in?"
    retriever = _MappingRetriever(
        {
            query: [_doc("v1", "Ralph Hefferline", 0.95), _doc("v2", "Virginia Commonwealth University", 0.82)],
            rewrite: [_doc("r1", "Columbia University", 0.81, matched_by=["requery"])],
        }
    )
    orchestrator = RetrievalOrchestrator(
        rag_retriever=retriever,
        keyword_retriever=_MappingRetriever({}),
        graph_retriever=_EmptyGraphRetriever(),
        query_expander=_StaticExpander([rewrite]),
        query_processor=QueryProcessor(),
        fusion=_RequeryAwareFusion(use_requery_docs=False),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query=query,
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "unavailable", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    assert [doc["file_name"] for doc in result["final_pass_result"]["documents"]] == [
        "Ralph Hefferline",
        "Virginia Commonwealth University",
    ]
    assert result["metadata"]["requery_used"] is True
    assert result["metadata"]["requery_fallback_to_floor"] is True
