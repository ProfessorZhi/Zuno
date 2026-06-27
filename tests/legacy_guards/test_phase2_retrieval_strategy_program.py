from zuno.services.retrieval.models import ProcessedQuery, RetrievalRequest
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator
from zuno.services.retrieval.planner import RetrievalPlanner


def _processed(
    query: str,
    *,
    relation: bool = False,
    global_question: bool = False,
    evidence_required: bool = False,
):
    return ProcessedQuery(
        original_query=query,
        normalized_query=query,
        rewritten_queries=[query],
        intent_labels=[],
        query_features={
            "relation_question": relation,
            "global_question": global_question,
            "evidence_required": evidence_required,
        },
        route_hints=[],
    )


def test_standard_retrieval_defaults_to_vector_bm25_fusion_rerank_contract():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="redis persistence mode", knowledge_ids=["kb_1"], mode="rag"),
        _processed("redis persistence mode"),
        knowledge_capability="rag",
    )

    assert plan.resolved_mode == "rag"
    assert plan.internal_route == "standard_rag"
    assert plan.enabled_retrievers == ["vector", "bm25"]
    assert plan.rerank_policy["enabled"] is True


def test_enhanced_retrieval_enters_rag_graph_deep_and_routes_relation_questions_to_local_graph():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="终止条款和通知期限是什么关系", knowledge_ids=["kb_1"], mode="rag_graph"),
        _processed("终止条款和通知期限是什么关系", relation=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "rag_graph_deep"
    assert plan.internal_route == "local_graphrag"
    assert plan.enabled_retrievers == ["vector", "bm25", "graph"]


def test_enhanced_retrieval_routes_global_questions_to_community_when_ready():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="这批合同整体有哪些高频风险",
            knowledge_ids=["kb_1"],
            mode="rag_graph",
            index_health={"graph": "ready", "community": "ready"},
        ),
        _processed("这批合同整体有哪些高频风险", global_question=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "rag_graph_deep"
    assert plan.internal_route == "community_global"
    assert plan.route_trace["community_required"] is True


def test_enhanced_retrieval_routes_global_plus_evidence_questions_to_drift_like_when_ready():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="这批合同整体有哪些风险 并给出条款依据",
            knowledge_ids=["kb_1"],
            mode="rag_graph",
            index_health={"graph": "ready", "community": "ready"},
        ),
        _processed(
            "这批合同整体有哪些风险 并给出条款依据",
            global_question=True,
            evidence_required=True,
        ),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "rag_graph_deep"
    assert plan.internal_route == "drift_like"
    assert plan.route_trace["community_required"] is True
    assert plan.route_trace["local_graph_required"] is True


def test_enhanced_retrieval_degrades_global_route_to_local_graph_when_community_not_ready():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="这批合同整体有哪些高频风险",
            knowledge_ids=["kb_1"],
            mode="rag_graph",
            index_health={"graph": "ready", "community": "stale"},
        ),
        _processed("这批合同整体有哪些高频风险", global_question=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "rag_graph_deep"
    assert plan.internal_route == "local_graphrag"
    assert plan.route_trace["degraded_from"] == "community_global"
    assert plan.fallback_policy["community_degraded"] is True


def test_enhanced_retrieval_degrades_to_standard_rag_when_graph_is_unavailable():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="赔偿责任链路",
            knowledge_ids=["kb_1"],
            mode="rag_graph",
            index_health={"graph": "unavailable", "community": "unavailable"},
        ),
        _processed("赔偿责任链路", relation=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "rag"
    assert plan.internal_route == "standard_rag"
    assert "graph" not in plan.enabled_retrievers
    assert plan.fallback_policy["graph_degraded"] is True


def test_planner_marks_rerank_unavailable_as_score_sort_fallback():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="redis persistence mode", knowledge_ids=["kb_1"], mode="rag"),
        _processed("redis persistence mode"),
        knowledge_capability="rag",
        rerank_available=False,
    )

    assert plan.rerank_policy["enabled"] is False
    assert plan.rerank_policy["strategy"] == "score_sort"
    assert plan.fallback_policy["rerank_degraded"] is True


class _FakeRetriever:
    def __init__(self, payload):
        self.payload = payload

    async def retrieve(self, query, knowledge_ids, options=None):
        return self.payload


class _FakeExpander:
    async def expand(self, query: str):
        return [query, f"{query} rewrite"]


class _FakeProcessor:
    async def process(self, query: str):
        return _processed(query, relation=True)


def test_orchestrator_trace_exposes_requested_mode_route_and_retriever_usage():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever(
            {
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
        ),
        keyword_retriever=_FakeRetriever(
            {
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
        ),
        graph_retriever=_FakeRetriever(
            {
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
        ),
        query_expander=_FakeExpander(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        query_processor=_FakeProcessor(),
    )

    result = __import__("asyncio").run(
        orchestrator.run(
            mode="rag_graph",
            query="终止条款和通知期限是什么关系",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "not_built"},
                "trace_policy": {"enabled": True},
                "rerank_enabled": True,
                "score_threshold": 0.2,
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["requested_mode"] == "rag_graph_deep"
    assert metadata["resolved_mode"] == "rag_graph_deep"
    assert metadata["internal_route"] == "local_graphrag"
    assert metadata["enabled_retrievers"] == ["vector", "bm25", "graph"]
    assert metadata["used_vector"] is True
    assert metadata["used_bm25"] is True
    assert metadata["used_graph"] is True
    assert metadata["used_communities"] == []
    assert "citation_chunks" in metadata
