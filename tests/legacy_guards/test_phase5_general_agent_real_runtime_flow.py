import asyncio
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

from langchain_core.messages import AIMessageChunk, HumanMessage


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    runtime_root = str(BACKEND_ROOT)
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def _agent_config():
    AgentConfig = importlib.import_module("zuno.core.agents.general_agent").AgentConfig
    return AgentConfig(
        user_id="u_1",
        llm_id="",
        mcp_ids=[],
        knowledge_ids=["kb_contract"],
        domain_pack_id="contract_review",
        dialog_id="dialog_1",
        tool_ids=[],
        agent_skill_ids=[],
        system_prompt="review contract",
        name="contract-agent",
        multi_agent_enabled=True,
    )


def test_zuno_general_agent_knowledge_tool_uses_project_query_service(monkeypatch):
    _ensure_runtime_paths()

    ga = importlib.import_module("zuno.core.agents.general_agent")
    GeneralAgent = importlib.import_module("zuno.core.agents.general_agent").GeneralAgent
    KnowledgeQueryResult = importlib.import_module(
        "zuno.services.graphrag.query_service"
    ).KnowledgeQueryResult

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
            answer="第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
            requested_query_method="auto",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[{"chunk_id": "contract_chunk_1", "file_name": "loan_contract_001.md"}],
            evidence={"document_count": 1, "citation_coverage": 1.0},
            citations=["contract_chunk_1"],
            retrievers_used=["vector", "graph"],
            graph_paths=["第八条 违约责任 -> 违约责任"],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={"vector": "vector_v2", "graph": "graph_v2"},
            community_version="community-v0",
            trace_metadata={"resolved_query_method": "local"},
        )

    monkeypatch.setattr(ga.KnowledgeQueryService, "query", fake_query)

    agent = GeneralAgent(_agent_config())
    asyncio.run(agent.setup_knowledge_tool())
    result = asyncio.run(agent.tools[0].ainvoke({"query": "这份合同是否约定了违约责任？"}))

    assert agent.tools[0].name == "search_knowledge_base"
    assert captured["knowledge_ids"] == ["kb_contract"]
    assert captured["product_mode"] == "auto"
    assert "第八条 违约责任" in result
    assert "citations: contract_chunk_1" in result
    assert "resolved_query_method: local" in result


def test_zuno_general_agent_astream_keeps_single_react_runtime_with_project_bound():
    _ensure_runtime_paths()

    GeneralAgent = importlib.import_module("zuno.core.agents.general_agent").GeneralAgent

    class FakeReactAgent:
        async def astream(self, *args, **kwargs):
            yield "messages", [AIMessageChunk(content="single agent answer")]

    agent = GeneralAgent(_agent_config())
    assert not hasattr(agent, "domain_qa_runtime")
    agent.react_agent = FakeReactAgent()
    agent.conversation_model = SimpleNamespace()

    async def collect():
        return [
            event
            async for event in agent.astream([HumanMessage(content="请审查这份合同是否约定了违约责任？")])
        ]

    events = asyncio.run(collect())

    assert len(events) == 1
    assert events[0]["type"] == "response_chunk"
    assert events[0]["data"]["accumulated"] == "single agent answer"
