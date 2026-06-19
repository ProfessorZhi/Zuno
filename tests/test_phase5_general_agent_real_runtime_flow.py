import asyncio
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

from langchain_core.messages import HumanMessage


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    for runtime_root in (str(BACKEND_ROOT),):
        if runtime_root not in sys.path:
            sys.path.insert(0, runtime_root)


def _build_fake_retrieval_result(*, answer_text: str) -> dict:
    return {
        "content": answer_text,
        "actual_mode": "hybrid",
        "domain_pack_id": "contract_review",
        "metadata": {
            "requested_mode": "graphrag",
            "requested_profile": "relation_hybrid",
            "resolved_profile": "relation_hybrid",
            "fallback_triggered": False,
            "scope_policy": {"status": "active"},
            "index_version": {"vector": "vector_v2", "graph": "graph_v2"},
            "index_health": {"vector": "ready", "graph": "ready"},
        },
        "graph_result": {
            "paths": ["第八条 违约责任 -> 违约责任"],
            "structured_paths": [
                {
                    "source": "第八条 违约责任",
                    "target": "违约责任",
                    "chunk_ids": ["contract_chunk_1"],
                }
            ],
        },
        "final_pass_result": {
            "documents": [
                {
                    "chunk_id": "contract_chunk_1",
                    "file_name": "loan_contract_001.md",
                    "knowledge_id": "kb_contract",
                    "content": answer_text,
                }
            ],
            "paths": ["第八条 违约责任 -> 违约责任"],
            "structured_paths": [
                {
                    "source": "第八条 违约责任",
                    "target": "违约责任",
                    "chunk_ids": ["contract_chunk_1"],
                }
            ],
        },
    }


def _runtime_settings(*, multi_agent_enabled: bool = False) -> dict:
    retrieval_settings = {
        "default_mode": "graphrag",
        "graph_hop_limit": 2,
    }
    if multi_agent_enabled:
        retrieval_settings["multi_agent_enabled"] = True
    return {
        "domain_pack_id": "contract_review",
        "domain_pack": {
            "id": "contract_review",
            "answer_template_text": "你是一名合同审查助手，请严格基于检索证据回答。",
        },
        "knowledge_config": {
            "retrieval_settings": retrieval_settings,
            "index_capability": "rag_graph",
            "index_settings": {"index_version": "vector_v2", "health_status": "ready"},
            "graph_index_settings": {"index_version": "graph_v2", "health_status": "ready"},
        },
    }


def test_zuno_general_agent_knowledge_tool_runs_real_domain_qa_graph(monkeypatch):
    _ensure_runtime_paths()

    ga = importlib.import_module("zuno.core.agents.general_agent")
    AgentConfig = importlib.import_module("zuno.core.agents.general_agent").AgentConfig
    GeneralAgent = importlib.import_module("zuno.core.agents.general_agent").GeneralAgent
    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph

    async def fake_runtime_settings(_knowledge_id):
        return _runtime_settings()

    async def fake_retrieval_runner(*, query, knowledge_ids, runtime_settings, domain_pack):
        assert "违约责任" in query
        assert knowledge_ids == ["kb_contract"]
        assert (domain_pack or {}).get("id") == "contract_review"
        return _build_fake_retrieval_result(
            answer_text="第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。"
        )

    async def fail_if_called(*args, **kwargs):
        raise AssertionError("fallback RagHandler path should not be used when real DomainQAGraph runtime is available")

    monkeypatch.setattr(ga.KnowledgeService, "get_runtime_settings", fake_runtime_settings)
    monkeypatch.setattr(ga.RagHandler, "retrieve_ranked_documents", fail_if_called)

    agent = GeneralAgent(
        AgentConfig(
            user_id="u_1",
            llm_id="",
            mcp_ids=[],
            knowledge_ids=["kb_contract"],
            domain_pack_id="contract_review",
            tool_ids=[],
            agent_skill_ids=[],
            system_prompt="review contract",
            name="contract-agent",
        )
    )
    agent.domain_qa_runtime.graph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)

    asyncio.run(agent.setup_knowledge_tool())
    result = asyncio.run(agent.tools[0].ainvoke({"query": "这份合同是否约定了违约责任？"}))

    assert result.startswith("你是一名合同审查助手")
    assert "第八条 违约责任" in result
    assert "loan_contract_001.md#contract_chunk_1" in result


def test_zuno_general_agent_astream_runs_real_multi_agent_runtime_chain(monkeypatch):
    _ensure_runtime_paths()

    ga = importlib.import_module("zuno.core.agents.general_agent")
    AgentConfig = importlib.import_module("zuno.core.agents.general_agent").AgentConfig
    GeneralAgent = importlib.import_module("zuno.core.agents.general_agent").GeneralAgent
    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph
    MultiAgentSupervisorGraph = importlib.import_module(
        "zuno.core.graphs.multi_agent_supervisor_graph"
    ).MultiAgentSupervisorGraph

    async def fake_runtime_settings(_knowledge_id):
        return _runtime_settings(multi_agent_enabled=True)

    async def fake_retrieval_runner(*, query, knowledge_ids, runtime_settings, domain_pack):
        assert "违约责任" in query
        assert knowledge_ids == ["kb_contract"]
        assert (runtime_settings or {}).get("knowledge_config", {}).get("retrieval_settings", {}).get(
            "multi_agent_enabled"
        ) is True
        return _build_fake_retrieval_result(
            answer_text="第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。"
        )

    async def actual_domain_qa_runner(state):
        subgraph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)
        sub_state = subgraph.build_initial_state(
            user_id=state["user_id"],
            agent_id=state["agent_id"],
            dialog_id=state["dialog_id"],
            query=state["query"],
            knowledge_ids=state.get("knowledge_ids") or [],
            domain_pack_id=state.get("domain_pack_id"),
            runtime_settings=state.get("runtime_settings"),
            domain_pack=state.get("domain_pack"),
        )
        return await subgraph.ainvoke(sub_state)

    class FailReactAgent:
        async def astream(self, *args, **kwargs):
            raise AssertionError("react agent path should be bypassed for explicit multi-agent domain runtime")
            yield None

    monkeypatch.setattr(ga.KnowledgeService, "get_runtime_settings", fake_runtime_settings)

    agent = GeneralAgent(
        AgentConfig(
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
    )
    agent.domain_qa_runtime.graph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)
    agent.domain_qa_runtime.multi_agent_graph = MultiAgentSupervisorGraph(
        domain_qa_runner=actual_domain_qa_runner
    )
    agent.react_agent = FailReactAgent()
    agent.conversation_model = SimpleNamespace()

    async def collect():
        return [
            event
            async for event in agent.astream([HumanMessage(content="请用多 agent 审查这份合同是否约定了违约责任？")])
        ]

    events = asyncio.run(collect())

    assert events[0]["type"] == "event"
    assert events[0]["data"]["phase"] == "domain_qa"
    assert events[1]["data"]["status"] == "END"
    assert [node["node"] for node in events[1]["data"]["trace_metadata"]["nodes"]] == [
        "plan_specialists",
        "domain_qa_specialist",
        "citation_verifier_specialist",
        "finalize",
    ]
    assert events[1]["data"]["cost_metadata"]["specialist_count"] == 2
    assert events[1]["data"]["support_verdict"]["status"] == "supported"
    assert events[1]["data"]["evidence_bundle"]["citation_count"] == 1
    assert events[-1]["type"] == "response_chunk"
    assert "第八条 违约责任" in events[-1]["data"]["accumulated"]
