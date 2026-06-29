import asyncio
from types import SimpleNamespace


def _agent_config(**overrides):
    from zuno.core.agents.general_agent import AgentConfig

    data = dict(
        user_id="u_1",
        llm_id="",
        mcp_ids=[],
        knowledge_ids=["kb_1"],
        domain_pack_id="contract_review",
        dialog_id="dialog_1",
        tool_ids=[],
        agent_skill_ids=[],
        system_prompt="review contract",
        name="contract-agent",
    )
    data.update(overrides)
    return AgentConfig(**data)


def test_general_agent_legacy_runtime_symbols_are_retired():
    from zuno.core.agents import general_agent as ga

    assert "AgentRuntime" not in vars(ga)
    assert "KnowledgeService" not in vars(ga)
    assert "RagHandler" not in vars(ga)


def test_general_agent_knowledge_tool_uses_project_query_runtime(monkeypatch):
    from zuno.core.agents import general_agent as ga
    from zuno.core.agents.general_agent import GeneralAgent
    from zuno.services.graphrag.query_service import KnowledgeQueryResult

    captured = {}

    async def fake_query(self, *, user_id, knowledge_ids, query, product_mode="auto", query_method=None, top_k=None):
        captured.update(
            {
                "user_id": user_id,
                "knowledge_ids": knowledge_ids,
                "query": query,
                "product_mode": product_mode,
                "query_method": query_method,
                "top_k": top_k,
            }
        )
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="第八条约定了违约责任。",
            requested_query_method="auto",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[{"chunk_id": "chunk-1", "file_name": "contract.md"}],
            evidence={"document_count": 1, "citation_coverage": 1.0},
            citations=["chunk-1"],
            retrievers_used=["vector", "graph"],
            graph_paths=[{"source": "第八条", "target": "违约责任"}],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={"vector": "v1", "graph": "g1"},
            community_version="c1",
            trace_metadata={"resolved_query_method": "local"},
        )

    monkeypatch.setattr(ga.KnowledgeQueryService, "query", fake_query)

    agent = GeneralAgent(_agent_config())
    asyncio.run(agent.setup_knowledge_tool())

    result = asyncio.run(agent.tools[0].ainvoke({"query": "这份合同是否约定违约责任？"}))

    assert captured["user_id"] == "u_1"
    assert captured["knowledge_ids"] == ["kb_1"]
    assert captured["query"] == "这份合同是否约定违约责任？"
    assert captured["product_mode"] == "auto"
    assert captured["query_method"] is None
    assert "第八条约定了违约责任" in result
    assert "citations: chunk-1" in result
    assert "resolved_query_method: local" in result


def test_general_agent_forwards_product_mode_and_query_method(monkeypatch):
    from zuno.core.agents import general_agent as ga
    from zuno.core.agents.general_agent import GeneralAgent
    from zuno.services.graphrag.query_service import KnowledgeQueryResult

    captured = {}

    async def fake_query(self, *, user_id, knowledge_ids, query, product_mode="auto", query_method=None, top_k=None):
        del self, top_k
        captured.update(
            {
                "user_id": user_id,
                "knowledge_ids": knowledge_ids,
                "query": query,
                "product_mode": product_mode,
                "query_method": query_method,
            }
        )
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="增强模式命中本地图谱。",
            requested_query_method="local",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[],
            evidence={"document_count": 0, "citation_coverage": 0.0},
            citations=[],
            retrievers_used=["vector", "graph"],
            graph_paths=[],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={},
            community_version=None,
            trace_metadata={"requested_product_mode": "enhanced", "resolved_query_method": "local"},
        )

    monkeypatch.setattr(ga.KnowledgeQueryService, "query", fake_query)

    agent = GeneralAgent(_agent_config(product_mode="enhanced", query_method="local"))
    asyncio.run(agent.setup_knowledge_tool())
    result = asyncio.run(agent.tools[0].ainvoke({"query": "用图谱解释合同关系"}))

    assert captured == {
        "user_id": "u_1",
        "knowledge_ids": ["kb_1"],
        "query": "用图谱解释合同关系",
        "product_mode": "enhanced",
        "query_method": "local",
    }
    assert "增强模式命中本地图谱" in result


def test_general_agent_knowledge_tool_emits_trace_artifact_event(monkeypatch):
    from zuno.core.agents import general_agent as ga
    from zuno.core.agents.general_agent import GeneralAgent
    from zuno.services.graphrag.query_service import KnowledgeQueryResult

    emitted = []

    async def fake_query(self, *, user_id, knowledge_ids, query, product_mode="auto", query_method=None, top_k=None):
        del self, user_id, knowledge_ids, query, product_mode, query_method, top_k
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="证据不足，无法高置信回答。",
            requested_query_method="local",
            resolved_query_method="local",
            fallback_reason="citation_coverage_below_threshold",
            documents=[{"chunk_id": "chunk-1"}],
            evidence={"document_count": 2, "citation_coverage": 0.5},
            citations=["chunk-1"],
            retrievers_used=["vector", "graph"],
            graph_paths=[],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={},
            community_version=None,
            trace_metadata={
                "runtime_trace_events": [
                    {"event_id": "trace-1:0001:pre_retrieval", "kind": "pre_retrieval"},
                    {"event_id": "trace-1:0003:post_answer", "kind": "post_answer"},
                ],
                "evidence_verdict": {
                    "status": "low_confidence",
                    "citation_coverage": 0.5,
                    "fallback_reason": "citation_coverage_below_threshold",
                },
                "artifact_manifest": {
                    "trace_id": "trace-1",
                    "retrieval_refs": ["chunk-1", "chunk-2"],
                    "evidence_refs": ["chunk-1"],
                },
            },
        )

    monkeypatch.setattr(ga.KnowledgeQueryService, "query", fake_query)
    monkeypatch.setattr(ga, "get_stream_writer", lambda: emitted.append)

    agent = GeneralAgent(_agent_config(product_mode="enhanced", query_method="local"))
    asyncio.run(agent.setup_knowledge_tool())
    result = asyncio.run(agent.tools[0].ainvoke({"query": "用证据回答合同风险"}))

    assert emitted == [
        {
            "status": "TRACE",
            "title": "知识库检索证据链",
            "message": "已生成知识库检索 trace、证据检查和 artifact manifest。",
            "runtime_trace_events": [
                {"event_id": "trace-1:0001:pre_retrieval", "kind": "pre_retrieval"},
                {"event_id": "trace-1:0003:post_answer", "kind": "post_answer"},
            ],
            "evidence_verdict": {
                "status": "low_confidence",
                "citation_coverage": 0.5,
                "fallback_reason": "citation_coverage_below_threshold",
            },
            "artifact_manifest": {
                "trace_id": "trace-1",
                "retrieval_refs": ["chunk-1", "chunk-2"],
                "evidence_refs": ["chunk-1"],
            },
        }
    ]
    assert "evidence_status: low_confidence" in result
    assert "citation_coverage: 0.5" in result
    assert "fallback_reason: citation_coverage_below_threshold" in result


def test_general_agent_astream_uses_single_react_loop_when_project_is_bound():
    from langchain_core.messages import AIMessageChunk, HumanMessage

    from zuno.core.agents.general_agent import GeneralAgent

    class FakeReactAgent:
        async def astream(self, *args, **kwargs):
            yield "messages", [AIMessageChunk(content="react-loop answer")]

    agent = GeneralAgent(_agent_config())
    agent.react_agent = FakeReactAgent()
    agent.conversation_model = SimpleNamespace()

    async def collect():
        return [
            event
            async for event in agent.astream([HumanMessage(content="这份合同是否约定违约责任？")])
        ]

    events = asyncio.run(collect())

    assert events == [
        {
            "type": "response_chunk",
            "timestamp": events[0]["timestamp"],
            "data": {
                "chunk": "react-loop answer",
                "accumulated": "react-loop answer",
            },
        }
    ]
