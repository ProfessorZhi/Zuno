# Zuno Retrieval Orchestrator Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 Zuno 当前分散的 RAG / GraphRAG / hybrid 检索逻辑收敛到统一 retrieval orchestrator 主线，并让 workspace 主入口、trace、回归测试都走新主线。

**Architecture:** 新增 `services/retrieval/` 作为统一检索编排层，拆出数据模型、planner、retriever 适配器、fusion、trace，再让现有 `services/graphrag/orchestrator.py` 成为兼容薄封装，保留对外接口不变。现有 Milvus、Elasticsearch、Neo4j 能力继续复用，只上提控制面与结果模型。

**Tech Stack:** Python 3.12, FastAPI backend, pytest, existing Milvus / Elasticsearch / Neo4j integrations

---

### Task 1: 建立统一 retrieval 数据模型与 planner

**Files:**
- Create: `src/backend/agentchat/services/retrieval/models.py`
- Create: `src/backend/agentchat/services/retrieval/planner.py`
- Test: `src/backend/agentchat/test/test_retrieval_planner.py`

- [ ] **Step 1: Write the failing planner tests**

```python
from agentchat.services.retrieval.planner import RetrievalPlanner
from agentchat.services.retrieval.models import ProcessedQuery, RetrievalRequest


def _processed(query: str, *, relation=False, keyword=False):
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
    planner = RetrievalPlanner()
    plan = planner.build_plan(
        RetrievalRequest(query="Zuno 与 Neo4j 是什么关系？", knowledge_ids=["kb_1"], mode="auto"),
        _processed("Zuno 与 Neo4j 是什么关系？", relation=True),
        knowledge_capability="rag_graph",
    )
    assert plan.resolved_mode == "graphrag"
    assert plan.enabled_retrievers == ["vector", "graph"]


def test_hybrid_mode_enables_keyword_when_elasticsearch_is_available():
    planner = RetrievalPlanner(enable_keyword_recall=True)
    plan = planner.build_plan(
        RetrievalRequest(query="MILVUS FLUSH PARAM", knowledge_ids=["kb_1"], mode="hybrid"),
        _processed("MILVUS FLUSH PARAM", keyword=True),
        knowledge_capability="rag_graph",
    )
    assert plan.resolved_mode == "hybrid"
    assert plan.enabled_retrievers == ["vector", "keyword", "graph"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest src/backend/agentchat/test/test_retrieval_planner.py -v`
Expected: FAIL with import errors for `agentchat.services.retrieval`

- [ ] **Step 3: Write minimal models and planner**

```python
from dataclasses import dataclass, field


@dataclass(slots=True)
class RetrievalRequest:
    query: str
    knowledge_ids: list[str]
    mode: str = "auto"
    top_k: int | None = None
    score_threshold: float | None = None
    rerank_enabled: bool | None = None
    rerank_top_k: int | None = None
    graph_hop_limit: int | None = None
    max_paths_per_entity: int | None = None
    needs_query_rewrite: bool = True
    trace_enabled: bool = True


@dataclass(slots=True)
class ProcessedQuery:
    original_query: str
    normalized_query: str
    rewritten_queries: list[str]
    intent_labels: list[str] = field(default_factory=list)
    query_features: dict[str, bool] = field(default_factory=dict)
    route_hints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetrievalPlan:
    requested_mode: str
    resolved_mode: str
    enabled_retrievers: list[str]
    retriever_configs: dict[str, dict]
    fusion_policy: dict
    rerank_policy: dict
    fallback_policy: dict
    trace_policy: dict
```

```python
class RetrievalPlanner:
    def __init__(self, *, enable_keyword_recall: bool = False):
        self.enable_keyword_recall = enable_keyword_recall

    def build_plan(self, request, processed_query, *, knowledge_capability: str = "rag") -> RetrievalPlan:
        requested_mode = (request.mode or "auto").strip().lower()
        relation_question = bool(processed_query.query_features.get("relation_question"))
        keyword_heavy = bool(processed_query.query_features.get("keyword_heavy"))

        if requested_mode == "auto":
            resolved_mode = "graphrag" if relation_question and knowledge_capability == "rag_graph" else "hybrid"
        elif requested_mode == "rag_graph":
            resolved_mode = "hybrid"
        else:
            resolved_mode = requested_mode

        enabled = ["vector"]
        if resolved_mode in {"graphrag", "hybrid"} and knowledge_capability == "rag_graph":
            enabled.append("graph")
        if self.enable_keyword_recall and resolved_mode == "hybrid":
            enabled.insert(1, "keyword")
        elif self.enable_keyword_recall and resolved_mode == "rag" and keyword_heavy:
            enabled.append("keyword")

        return RetrievalPlan(
            requested_mode=requested_mode,
            resolved_mode=resolved_mode,
            enabled_retrievers=enabled,
            retriever_configs={name: {} for name in enabled},
            fusion_policy={"name": "query_aware"},
            rerank_policy={"enabled": request.rerank_enabled},
            fallback_policy={"allow_retry": True},
            trace_policy={"enabled": request.trace_enabled},
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest src/backend/agentchat/test/test_retrieval_planner.py -v`
Expected: PASS

### Task 2: 抽统一 retriever 适配器与 fusion 层

**Files:**
- Create: `src/backend/agentchat/services/retrieval/retrievers.py`
- Create: `src/backend/agentchat/services/retrieval/fusion.py`
- Test: `src/backend/agentchat/test/test_retrieval_fusion.py`

- [ ] **Step 1: Write the failing fusion tests**

```python
from agentchat.services.retrieval.fusion import RetrievalFusion
from agentchat.services.retrieval.models import RetrievedDocument


def _doc(chunk_id: str, source_type: str, score: float, content: str):
    return RetrievedDocument(
        chunk_id=chunk_id,
        knowledge_id="kb_1",
        file_id="f_1",
        file_name="doc.md",
        content=content,
        summary="",
        score=score,
        normalized_score=None,
        source_type=source_type,
        source_backend=source_type,
        retrieval_reason=source_type,
        metadata={},
    )


def test_fusion_merges_same_chunk_and_tracks_matched_sources():
    fusion = RetrievalFusion()
    results = fusion.merge(
        query="redis persistence",
        documents_by_source={
            "vector": [_doc("c1", "vector", 0.8, "redis content")],
            "keyword": [_doc("c1", "keyword", 12.0, "redis content")],
        },
        top_k=5,
    )
    assert len(results.documents) == 1
    assert results.documents[0].metadata["matched_by"] == ["vector", "keyword"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest src/backend/agentchat/test/test_retrieval_fusion.py -v`
Expected: FAIL with import errors for `RetrievalFusion`

- [ ] **Step 3: Write minimal retriever adapters and fusion**

```python
class VectorRetrieverAdapter:
    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        ...


class KeywordRetrieverAdapter:
    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        ...


class GraphRetrieverAdapter:
    async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
        ...
```

```python
class RetrievalFusion:
    def merge(self, *, query: str, documents_by_source: dict[str, list[RetrievedDocument]], top_k: int | None):
        merged = {}
        for source_name, docs in documents_by_source.items():
            for doc in docs:
                current = merged.setdefault(doc.chunk_id or f"{source_name}:{len(merged)}", doc)
                matched = current.metadata.setdefault("matched_by", [])
                if source_name not in matched:
                    matched.append(source_name)
                if doc.score > current.score:
                    current.score = doc.score
        ordered = sorted(
            merged.values(),
            key=lambda item: (len(item.metadata.get("matched_by", [])), item.score),
            reverse=True,
        )
        return FusionResult(documents=ordered[:top_k] if top_k else ordered, dropped_documents=[], fusion_metadata={}, rerank_metadata={})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest src/backend/agentchat/test/test_retrieval_fusion.py -v`
Expected: PASS

### Task 3: 把统一 orchestrator 主线落到新目录并保留兼容入口

**Files:**
- Create: `src/backend/agentchat/services/retrieval/orchestrator.py`
- Modify: `src/backend/agentchat/services/graphrag/orchestrator.py`
- Test: `src/backend/agentchat/test/test_graphrag.py`

- [ ] **Step 1: Write the failing orchestrator test for plan metadata**

```python
def test_retrieval_orchestrator_returns_plan_and_trace_metadata():
    from agentchat.services.retrieval.orchestrator import RetrievalOrchestrator

    orchestrator = RetrievalOrchestrator(
        planner=FakePlanner(),
        query_processor=FakeQueryProcessor(),
        retrievers={"vector": FakeVectorRetriever()},
        fusion=FakeFusion(),
    )
    result = asyncio.run(orchestrator.run("rag", "what is redis", ["kb_1"]))
    assert result["metadata"]["plan"]["resolved_mode"] == "rag"
    assert result["metadata"]["retriever_runs"][0]["source"] == "vector"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest src/backend/agentchat/test/test_graphrag.py -k plan -v`
Expected: FAIL with missing orchestrator implementation

- [ ] **Step 3: Implement the new orchestrator and thin compatibility wrapper**

```python
class RetrievalOrchestrator:
    async def run(self, mode: str, query: str, knowledge_ids: list[str], retrieval_options: dict | None = None) -> dict:
        request = RetrievalRequest(...)
        processed = await self.query_processor.process(request.query)
        plan = self.planner.build_plan(request, processed, knowledge_capability=...)
        runs = await self._run_retrievers(plan, processed, request)
        fusion_result = self.fusion.merge(...)
        return {
            "actual_mode": plan.resolved_mode,
            "first_mode": plan.resolved_mode,
            "final_mode": plan.resolved_mode,
            "content": ...,
            "metadata": {
                "plan": ...,
                "retriever_runs": ...,
                "rounds": ...,
            },
        }
```

```python
from agentchat.services.retrieval.orchestrator import RetrievalOrchestrator

__all__ = ["RetrievalOrchestrator", "RagRetrieverAdapter", "QueryExpanderAdapter"]
```

- [ ] **Step 4: Run orchestrator regression tests**

Run: `pytest src/backend/agentchat/test/test_graphrag.py -v`
Expected: PASS

### Task 4: 接入 RagHandler 与 workspace 主路径

**Files:**
- Modify: `src/backend/agentchat/services/rag/handler.py`
- Modify: `src/backend/agentchat/services/workspace/simple_agent.py`
- Test: `src/backend/agentchat/test/test_workspace_retrieval_trace.py`

- [ ] **Step 1: Write the failing workspace trace test for planner metadata passthrough**

```python
def test_build_retrieval_event_payload_includes_plan_summary():
    payload = agent._build_retrieval_event_payload(
        {
            "actual_mode": "hybrid",
            "metadata": {
                "plan": {"resolved_mode": "hybrid", "enabled_retrievers": ["vector", "keyword", "graph"]},
                "retriever_runs": [{"source": "vector", "result_count": 2}],
            },
        }
    )
    assert payload["plan"]["enabled_retrievers"] == ["vector", "keyword", "graph"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest src/backend/agentchat/test/test_workspace_retrieval_trace.py -v`
Expected: FAIL because payload lacks plan metadata

- [ ] **Step 3: Switch handler/workspace to the new metadata shape**

```python
return await orchestrator.run(
    mode=normalized_mode,
    query=query,
    knowledge_ids=collection_names,
    retrieval_options=effective_options,
)
```

```python
return {
    ...
    "plan": metadata.get("plan") or {},
    "retriever_runs": metadata.get("retriever_runs") or [],
}
```

- [ ] **Step 4: Run trace test to verify it passes**

Run: `pytest src/backend/agentchat/test/test_workspace_retrieval_trace.py -v`
Expected: PASS

### Task 5: 做完整后端回归验证

**Files:**
- Verify only

- [ ] **Step 1: Run focused retrieval tests**

Run: `pytest src/backend/agentchat/test/test_retrieval_planner.py src/backend/agentchat/test/test_retrieval_fusion.py src/backend/agentchat/test/test_graphrag.py src/backend/agentchat/test/test_workspace_retrieval_trace.py -v`
Expected: PASS

- [ ] **Step 2: Run broader workspace / knowledge contract regressions**

Run: `pytest src/backend/agentchat/test/test_workspace_simple_agent.py src/backend/agentchat/test/test_knowledge_api_contract.py -v`
Expected: PASS

- [ ] **Step 3: Inspect git diff for unintended files**

Run: `git -C F:\\resume project\\02_projects\\Zuno diff -- src/backend/agentchat/services src/backend/agentchat/test docs/superpowers`
Expected: only retrieval refactor files and touched tests / docs
