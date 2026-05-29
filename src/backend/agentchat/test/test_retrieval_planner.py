from agentchat.services.retrieval.models import ProcessedQuery, RetrievalRequest
from agentchat.services.retrieval.planner import RetrievalPlanner


def _processed(query: str, *, relation: bool = False, keyword: bool = False):
    return ProcessedQuery(
        original_query=query,
        normalized_query=query,
        rewritten_queries=[query],
        intent_labels=[],
        query_features={
            "relation_question": relation,
            "keyword_heavy": keyword,
        },
        route_hints=[],
    )


def test_auto_mode_prefers_graphrag_for_relation_question():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="Zuno 与 Neo4j 是什么关系？", knowledge_ids=["kb_1"], mode="auto"),
        _processed("Zuno 与 Neo4j 是什么关系？", relation=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "hybrid"
    assert plan.enabled_retrievers == ["vector", "bm25", "graph"]


def test_hybrid_mode_enables_keyword_when_elasticsearch_is_available():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="MILVUS FLUSH PARAM", knowledge_ids=["kb_1"], mode="hybrid"),
        _processed("MILVUS FLUSH PARAM", keyword=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "hybrid"
    assert plan.enabled_retrievers == ["vector", "bm25", "graph"]


def test_rag_mode_defaults_to_vector_plus_bm25_when_elasticsearch_is_available():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="redis persistence mode", knowledge_ids=["kb_1"], mode="rag"),
        _processed("redis persistence mode"),
        knowledge_capability="rag",
    )

    assert plan.resolved_mode == "rag"
    assert plan.enabled_retrievers == ["vector", "bm25"]
