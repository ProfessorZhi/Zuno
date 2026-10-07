"""索引就绪状态在读取路径上必须 fail-closed（Round 020 · IMP-020-01）。

修复前：读取侧一律 `or "ready"`，缺配置 / 缺 `health_status` / 缺字段都被判定为
「就绪」。写入侧 `mark_ready` 有严格判定，读取侧却绕过了它 —— 未就绪的知识库
会被当作就绪使用，这不是崩溃，是静默地用不可信知识作答。

这里锁三件事：
1. 缺失即降级，且降级是**有记录的**（route_trace / fallback_policy 可查）。
2. 显式 ``ready`` 仍保持原路由 —— 防止把 fail-closed 做成"一律降级"。
3. 图索引可用性来自真实索引状态，而不是硬编码 ``True``。
"""

from __future__ import annotations

from types import SimpleNamespace

from zuno.platform.services.retrieval.models import ProcessedQuery, RetrievalRequest
from zuno.platform.services.retrieval.planner import RetrievalPlanner


def _processed(query: str, *, relation: bool = False, global_question: bool = False) -> ProcessedQuery:
    return ProcessedQuery(
        original_query=query,
        normalized_query=query,
        rewritten_queries=[query],
        intent_labels=[],
        query_features={
            "relation_question": relation,
            "keyword_heavy": False,
            "global_question": global_question,
            "evidence_required": False,
        },
        route_hints=[],
    )


def _plan(*, mode: str, index_health: dict | None = None, relation: bool = True):
    planner = RetrievalPlanner(enable_keyword_recall=True)
    kwargs = {"query": "Zuno 与 Neo4j 是什么关系？", "knowledge_ids": ["kb_1"], "mode": mode}
    if index_health is not None:
        kwargs["index_health"] = index_health
    return planner.build_plan(
        RetrievalRequest(**kwargs),
        _processed("Zuno 与 Neo4j 是什么关系？", relation=relation),
        knowledge_capability="rag_graph",
    )


def test_missing_graph_health_degrades_and_records_the_reason() -> None:
    plan = _plan(mode="auto")  # 不声明 index_health

    assert "graph" not in plan.enabled_retrievers
    assert plan.internal_route == "standard_rag"
    assert plan.route_trace["fallback_reason"] == "graph_not_ready"
    assert plan.fallback_policy["graph_degraded"] is True


def test_explicitly_unavailable_graph_health_degrades_the_same_way() -> None:
    plan = _plan(mode="auto", index_health={"graph": "unavailable"})

    assert "graph" not in plan.enabled_retrievers
    assert plan.route_trace["fallback_reason"] == "graph_not_ready"


def test_explicit_ready_graph_health_keeps_the_graph_route() -> None:
    plan = _plan(mode="auto", index_health={"graph": "ready"})

    assert "graph" in plan.enabled_retrievers
    assert plan.internal_route == "local_graphrag"
    assert plan.resolved_mode == "rag_graph_deep"
    assert "graph_degraded" not in plan.fallback_policy


def test_community_read_back_without_status_is_not_assumed_ready() -> None:
    from zuno.platform.services.graphrag.community.models import GraphCommunity

    restored = GraphCommunity.from_dict(
        {
            "community_id": "kb_1::community::0",
            "knowledge_id": "kb_1",
            "level": 0,
            "entities": [],
            "relation_count": 0,
            "supporting_chunks": [],
        }
    )

    assert restored.status == "unavailable"


def test_freshly_detected_community_still_defaults_to_ready() -> None:
    from zuno.platform.services.graphrag.community.models import GraphCommunity

    detected = GraphCommunity(
        community_id="kb_1::community::0",
        knowledge_id="kb_1",
        level=0,
        entities=[],
        relation_count=0,
        supporting_chunks=[],
    )

    assert detected.status == "ready"


class _FakeIndexRuntime:
    def __init__(self, payloads: dict) -> None:
        self._payloads = payloads

    def to_retrieval_payload(self, knowledge_space_id: str, query: str) -> dict:
        if knowledge_space_id not in self._payloads:
            raise KeyError(knowledge_space_id)
        return self._payloads[knowledge_space_id]


def _graph_available(monkeypatch, payloads: dict, knowledge_space_ids: list[str]) -> bool:
    from zuno.api.services.product.runtime_engine import ProductRuntimeMechanics

    monkeypatch.setattr(
        ProductRuntimeMechanics,
        "_knowledge_index_runtime",
        _FakeIndexRuntime(payloads),
    )
    return ProductRuntimeMechanics._graph_index_available(
        SimpleNamespace(knowledge_space_ids=knowledge_space_ids)
    )


def test_graph_available_requires_a_ready_graph_source(monkeypatch) -> None:
    assert _graph_available(
        monkeypatch,
        {"kb_1": {"retrievers_used": ["bm25", "vector", "graph"]}},
        ["kb_1"],
    ) is True

    assert _graph_available(
        monkeypatch,
        {"kb_1": {"retrievers_used": ["bm25", "vector"]}},
        ["kb_1"],
    ) is False


def test_graph_available_is_false_when_index_state_is_missing(monkeypatch) -> None:
    assert _graph_available(monkeypatch, {}, ["kb_missing"]) is False
    assert _graph_available(monkeypatch, {"kb_1": {"retrievers_used": ["graph"]}}, []) is False


def test_graph_available_holds_if_any_knowledge_space_can_serve_graph(monkeypatch) -> None:
    assert _graph_available(
        monkeypatch,
        {
            "kb_1": {"retrievers_used": ["bm25", "vector"]},
            "kb_2": {"retrievers_used": ["bm25", "vector", "graph"]},
        },
        ["kb_1", "kb_2"],
    ) is True
