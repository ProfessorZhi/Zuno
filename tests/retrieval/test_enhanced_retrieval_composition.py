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


class _FakeExpander:
    async def expand(self, query: str):
        return [query, f"{query} rewrite"]


class _RelationProcessor:
    async def process(self, query: str):
        return ProcessedQuery(
            original_query=query,
            normalized_query=query,
            rewritten_queries=[query],
            intent_labels=[],
            query_features={
                "relation_question": True,
                "global_question": False,
                "evidence_required": False,
            },
            route_hints=[],
        )


class _GlobalEvidenceProcessor:
    async def process(self, query: str):
        return ProcessedQuery(
            original_query=query,
            normalized_query=query,
            rewritten_queries=[query],
            intent_labels=[],
            query_features={
                "relation_question": False,
                "global_question": True,
                "evidence_required": True,
            },
            route_hints=[],
        )


class _FakeCommunityService:
    async def load_communities(self, knowledge_id, status="ready", community_version="v0"):
        return [{"community_id": "community-0"}]

    def search_reports(self, query, communities, limit=3):
        return {
            "used_communities": ["community-0"],
            "supporting_chunks": ["chunk-community"],
            "community_trace": {"selected": 1},
        }

    def build_global_answer(self, query, report_payload):
        return {
            "content": "global summary",
            "map_results": [{"community_id": "community-0"}],
            "reduce_trace": {"reduced": True},
        }

    def build_drift_plan(self, query, report_payload):
        return {
            "broad_answer": "broad summary",
            "follow_up_questions": ["Which clause supports the risk?"],
        }


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


def _graph_payload():
    return {
        "content": "graph evidence",
        "raw_content": "graph evidence",
        "documents": [
            {
                "chunk_id": "c3",
                "knowledge_id": "kb_1",
                "file_id": "f3",
                "file_name": "c.md",
                "content": "graph evidence",
                "score": 0.88,
            }
        ],
        "entities": [{"name": "终止条款"}],
        "paths": [{"source": "终止条款", "target": "通知期限"}],
    }


def test_enhanced_retrieval_alias_normalizes_to_deep_runtime():
    assert normalize_retrieval_mode("enhanced_retrieval") == "rag_graph_deep"


def _step_status(metadata, name: str) -> str:
    steps = {
        step["name"]: step["status"]
        for step in metadata["pipeline_trace"]["steps"]
    }
    return steps[name]


def test_enhanced_retrieval_uses_standard_floor_and_local_graph_route():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever(_vector_payload()),
        keyword_retriever=_FakeRetriever(_bm25_payload()),
        graph_retriever=_FakeRetriever(_graph_payload()),
        query_expander=_FakeExpander(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        query_processor=_RelationProcessor(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query="终止条款和通知期限是什么关系",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "trace_policy": {"enabled": True},
                "bm25_available": True,
                "rerank_available": True,
                "rerank_enabled": True,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["standard_floor_used"] is True
    assert metadata["graph_route_attempted"] is True
    assert metadata["graph_route_used"] is True
    assert metadata["requery_available"] is True
    assert metadata["community_available"] is False
    assert metadata["community_used"] is False
    assert metadata["drift_available"] is False
    assert metadata["drift_used"] is False
    assert metadata["confidence_gated_fusion_used"] is True
    assert metadata["final_rerank_used"] is True
    assert metadata["route_selection_reason"] == "relation_question"
    assert metadata["requested_query_method"] == "auto"
    assert metadata["resolved_query_method"] == "local"
    assert metadata["retrievers_used"] == ["vector", "bm25", "graph"]
    assert metadata["evidence_bundle"]["document_count"] >= 1
    assert metadata["citation_coverage"] == 1.0
    assert metadata["pipeline_trace"]["resolved_query_method"] == "local"
    assert _step_status(metadata, "query_method_router") == "used"
    assert _step_status(metadata, "multi_retriever_recall") == "used"
    assert _step_status(metadata, "fusion") == "used"
    assert _step_status(metadata, "rerank") == "used"
    assert _step_status(metadata, "evidence_check") == "used"
    assert _step_status(metadata, "citation_answer") == "used"


def test_enhanced_retrieval_reports_available_drift_route_when_ready():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever(_vector_payload()),
        keyword_retriever=_FakeRetriever(_bm25_payload()),
        graph_retriever=_FakeRetriever(_graph_payload()),
        query_expander=_FakeExpander(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        query_processor=_GlobalEvidenceProcessor(),
        community_service=_FakeCommunityService(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query="这批合同整体有哪些风险 并给出条款依据",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "ready"},
                "trace_policy": {"enabled": True},
                "bm25_available": True,
                "rerank_available": True,
                "rerank_enabled": True,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["standard_floor_used"] is True
    assert metadata["community_available"] is True
    assert metadata["community_used"] is True
    assert metadata["drift_available"] is True
    assert metadata["drift_used"] is True
    assert metadata["graph_route_attempted"] is True
    assert metadata["graph_route_used"] is True
    assert metadata["route_selection_reason"] == "global_question_with_evidence"
    assert metadata["resolved_query_method"] == "drift"
    assert "community" in metadata["retrievers_used"]
    assert metadata["pipeline_trace"]["resolved_query_method"] == "drift"
    assert _step_status(metadata, "citation_answer") == "used"


def test_explicit_basic_query_method_keeps_enhanced_mode_on_standard_pipeline():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever(_vector_payload()),
        keyword_retriever=_FakeRetriever(_bm25_payload()),
        graph_retriever=_FakeRetriever(_graph_payload()),
        query_expander=_FakeExpander(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        query_processor=_RelationProcessor(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="enhanced_retrieval",
            query="Which clause defines notice?",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "query_method": "basic",
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "ready"},
                "trace_policy": {"enabled": True},
                "bm25_available": True,
                "rerank_available": True,
                "rerank_enabled": True,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["requested_query_method"] == "basic"
    assert metadata["resolved_query_method"] == "basic"
    assert metadata["internal_route"] == "standard_rag"
    assert metadata["graph_route_attempted"] is False
    assert metadata["community_used"] is False
    assert metadata["retrievers_used"] == ["vector", "bm25"]
    assert metadata["pipeline_trace"]["requested_query_method"] == "basic"
