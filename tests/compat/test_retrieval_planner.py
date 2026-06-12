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
    assert plan.requested_profile == "auto"
    assert plan.resolved_profile == "relation_hybrid"
    assert plan.enabled_retrievers == ["vector", "bm25", "graph"]
    assert plan.budget_policy["rewrite_enabled"] is True
    assert plan.fallback_policy["allow_retry"] is True


def test_hybrid_mode_enables_keyword_when_elasticsearch_is_available():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="MILVUS FLUSH PARAM", knowledge_ids=["kb_1"], mode="hybrid"),
        _processed("MILVUS FLUSH PARAM", keyword=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "hybrid"
    assert plan.resolved_profile == "hybrid_balanced"
    assert plan.enabled_retrievers == ["vector", "bm25", "graph"]
    assert plan.rerank_policy["top_k"] is None


def test_rag_mode_defaults_to_vector_plus_bm25_when_elasticsearch_is_available():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(query="redis persistence mode", knowledge_ids=["kb_1"], mode="rag"),
        _processed("redis persistence mode"),
        knowledge_capability="rag",
    )

    assert plan.resolved_mode == "rag"
    assert plan.resolved_profile == "vector_rerank"
    assert plan.enabled_retrievers == ["vector", "bm25"]


def test_explicit_profile_is_preserved_and_budget_policy_is_merged():
    planner = RetrievalPlanner(enable_keyword_recall=False)

    plan = planner.build_plan(
        RetrievalRequest(
            query="review contract indemnity",
            knowledge_ids=["kb_1"],
            mode="rag",
            requested_profile="contract_review_strict",
            top_k=6,
            rerank_top_k=4,
            budget_policy={"max_context_chars": 4000},
            fallback_policy={"allow_retry": False},
            trace_policy={"include_rounds": False},
        ),
        _processed("review contract indemnity"),
        knowledge_capability="rag",
    )

    assert plan.requested_profile == "contract_review_strict"
    assert plan.resolved_profile == "contract_review_strict"
    assert plan.budget_policy["top_k"] == 6
    assert plan.budget_policy["rerank_top_k"] == 4
    assert plan.budget_policy["max_context_chars"] == 4000
    assert plan.fallback_policy["allow_retry"] is False
    assert plan.trace_policy["include_rounds"] is False


def test_planner_drops_graph_when_graph_index_health_is_unavailable():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="合同中的赔偿责任关系是什么",
            knowledge_ids=["kb_1"],
            mode="graphrag",
            scope_policy={"status": "active"},
            index_health={"graph": "unavailable"},
            index_version={"vector": "vector_v2", "graph": "graph_v2"},
        ),
        _processed("合同中的赔偿责任关系是什么", relation=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "rag"
    assert "graph" not in plan.enabled_retrievers
    assert plan.index_health["graph"] == "unavailable"
    assert plan.index_version["graph"] == "graph_v2"


def test_planner_disables_retrievers_for_inactive_scope():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="review archived knowledge",
            knowledge_ids=["kb_1"],
            mode="hybrid",
            scope_policy={"status": "archived", "knowledge_ids": ["kb_1"]},
        ),
        _processed("review archived knowledge"),
        knowledge_capability="rag_graph",
    )

    assert plan.enabled_retrievers == []
    assert plan.scope_policy["status"] == "archived"
    assert plan.fallback_policy["allow_retry"] is False
