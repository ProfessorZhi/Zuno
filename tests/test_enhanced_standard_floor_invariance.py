import asyncio
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.retrieval.models import FusionResult, ProcessedQuery, RetrievedDocument
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator


def _doc(chunk_id: str, file_name: str, source_type: str, score: float, *, matched_by=None):
    return RetrievedDocument(
        chunk_id=chunk_id,
        knowledge_id="kb_1",
        file_id=file_name,
        file_name=file_name,
        content=file_name,
        summary="",
        score=score,
        normalized_score=None,
        source_type=source_type,
        source_backend=source_type,
        retrieval_reason=source_type,
        metadata={"matched_by": list(matched_by or [source_type])},
    )


class _StaticRetriever:
    def __init__(self, payload):
        self.payload = payload

    async def retrieve(self, query, knowledge_ids, options=None):
        return self.payload


class _EnhancedFloorProcessor:
    def __init__(self, *, relation_question: bool):
        self.relation_question = relation_question

    async def process(self, query: str):
        return ProcessedQuery(
            original_query=query,
            normalized_query=query,
            rewritten_queries=[query],
            intent_labels=[],
            query_features={
                "relation_question": self.relation_question,
                "global_question": False,
                "evidence_required": False,
            },
            route_hints=[],
        )


class _NoRewriteExpander:
    async def expand(self, query: str):
        return [query]


class _InvarianceFusion:
    def __init__(self, *, final_documents, floor_documents):
        self.final_documents = list(final_documents)
        self.floor_documents = list(floor_documents)

    def merge(self, *, query: str, documents_by_source: dict[str, list[RetrievedDocument]], top_k: int | None = None):
        has_graph = bool(documents_by_source.get("graph"))
        docs = self.final_documents if has_graph else self.floor_documents
        if top_k is not None:
            docs = docs[:top_k]
        return FusionResult(
            documents=list(docs),
            dropped_documents=[],
            fusion_metadata={"strategy": "baseline_preserving"},
            rerank_metadata={},
        )


def _vector_payload(*docs):
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
    }


def _graph_payload(*docs):
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
        "entities": [{"name": "entity"}] if docs else [],
        "paths": [{"source": "a", "target": "b"}] if docs else [],
    }


def test_enhanced_reuses_standard_floor_when_no_enhancement_channel_is_used():
    floor_docs = [_doc("v1", "alpha.md", "vector", 0.91), _doc("v2", "beta.md", "vector", 0.85)]
    drift_docs = [_doc("v1", "alpha.md", "vector", 0.91), _doc("v3", "gamma.md", "vector", 0.84)]
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_StaticRetriever(_vector_payload(*floor_docs)),
        keyword_retriever=_StaticRetriever({"content": "", "raw_content": "", "documents": []}),
        graph_retriever=_StaticRetriever(_graph_payload()),
        query_expander=_NoRewriteExpander(),
        query_processor=_EnhancedFloorProcessor(relation_question=False),
        fusion=_InvarianceFusion(final_documents=drift_docs, floor_documents=floor_docs),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query="where is alpha located",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    assert [doc["file_name"] for doc in result["final_pass_result"]["documents"]] == ["alpha.md", "beta.md"]
    assert result["metadata"]["standard_floor_reused"] is True
    assert result["metadata"]["enhanced_noop"] is True
    assert result["metadata"]["enhanced_noop_reason"] == "no_enhancement_channel_used"


def test_enhanced_can_change_ranking_when_graph_confidently_contributes():
    floor_docs = [_doc("v1", "alpha.md", "vector", 0.91), _doc("v2", "beta.md", "vector", 0.85)]
    graph_doc = _doc("g1", "bridge.md", "graph", 0.95, matched_by=["graph"])
    merged_docs = [graph_doc, floor_docs[0], floor_docs[1]]
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_StaticRetriever(_vector_payload(*floor_docs)),
        keyword_retriever=_StaticRetriever({"content": "", "raw_content": "", "documents": []}),
        graph_retriever=_StaticRetriever(_graph_payload(graph_doc)),
        query_expander=_NoRewriteExpander(),
        query_processor=_EnhancedFloorProcessor(relation_question=True),
        fusion=_InvarianceFusion(final_documents=merged_docs, floor_documents=floor_docs),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query="who founded alpha and where is it based",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    assert [doc["file_name"] for doc in result["final_pass_result"]["documents"]][:2] == ["bridge.md", "alpha.md"]
    assert result["metadata"]["standard_floor_reused"] is False
    assert result["metadata"]["enhanced_noop"] is False
    assert result["metadata"]["enhanced_fallback_to_floor"] is False


def test_low_confidence_graph_falls_back_to_standard_floor():
    floor_docs = [_doc("v1", "alpha.md", "vector", 0.91), _doc("v2", "beta.md", "vector", 0.85)]
    graph_doc = _doc("g1", "noise.md", "graph", 0.55, matched_by=["graph"])
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_StaticRetriever(_vector_payload(*floor_docs)),
        keyword_retriever=_StaticRetriever({"content": "", "raw_content": "", "documents": []}),
        graph_retriever=_StaticRetriever(_graph_payload(graph_doc)),
        query_expander=_NoRewriteExpander(),
        query_processor=_EnhancedFloorProcessor(relation_question=True),
        fusion=_InvarianceFusion(final_documents=floor_docs, floor_documents=floor_docs),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query="who founded alpha and where is it based",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "bm25_available": False,
                "rerank_available": True,
                "top_k": 5,
            },
        )
    )

    assert [doc["file_name"] for doc in result["final_pass_result"]["documents"]] == ["alpha.md", "beta.md"]
    assert result["metadata"]["standard_floor_reused"] is True
    assert result["metadata"]["enhanced_fallback_to_floor"] is True
    assert result["metadata"]["enhanced_noop_reason"] == "enhancement_channel_low_confidence"
