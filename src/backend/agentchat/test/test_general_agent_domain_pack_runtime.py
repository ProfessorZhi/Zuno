import asyncio
from types import SimpleNamespace


def test_general_agent_knowledge_tool_uses_domain_pack_runtime(monkeypatch):
    from agentchat.core.agents.general_agent import AgentConfig, GeneralAgent

    async def fake_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": "contract_review",
            "domain_pack": {"id": "contract_review"},
            "knowledge_config": {"retrieval_settings": {"default_mode": "graphrag"}},
        }

    async def fake_run_domain_qa(self, **kwargs):
        return {
            "final_answer": "结论\n合同包含违约责任条款。",
        }

    async def fail_if_called(*args, **kwargs):
        raise AssertionError("fallback RagHandler path should not be used when domain pack runtime is available")

    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )
    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.AgentRuntime.run_domain_qa",
        fake_run_domain_qa,
    )
    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.RagHandler.retrieve_ranked_documents",
        fail_if_called,
    )

    agent = GeneralAgent(
        AgentConfig(
            user_id="u_1",
            llm_id="",
            mcp_ids=[],
            knowledge_ids=["kb_1"],
            domain_pack_id="contract_review",
            tool_ids=[],
            agent_skill_ids=[],
            system_prompt="review contract",
            name="contract-agent",
        )
    )

    asyncio.run(agent.setup_knowledge_tool())

    result = asyncio.run(agent.tools[0].ainvoke({"query": "这份合同是否约定违约责任？"}))

    assert "违约责任条款" in result


def test_general_agent_astream_prefers_explicit_domain_graph_runtime(monkeypatch):
    from langchain_core.messages import HumanMessage

    from agentchat.core.agents.general_agent import AgentConfig, GeneralAgent

    async def fake_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": "contract_review",
            "domain_pack": {"id": "contract_review"},
            "knowledge_config": {"retrieval_settings": {"default_mode": "graphrag"}},
        }

    async def fake_run_domain_qa(self, **kwargs):
        return {
            "domain_pack_id": "contract_review",
            "final_answer": "结论\n合同包含违约责任条款。",
            "trace_metadata": {"nodes": [{"node": "resolve_domain_pack"}]},
            "cost_metadata": {"used_domain_pack": True},
        }

    class FailReactAgent:
        async def astream(self, *args, **kwargs):
            raise AssertionError("react agent path should be bypassed for explicit domain graph runtime")
            yield None

    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )
    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.AgentRuntime.run_domain_qa",
        fake_run_domain_qa,
    )

    agent = GeneralAgent(
        AgentConfig(
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
    )
    agent.react_agent = FailReactAgent()
    agent.conversation_model = SimpleNamespace()

    events = asyncio.run(_collect_events(agent, [HumanMessage(content="这份合同是否约定违约责任？")]))

    assert events[0]["type"] == "event"
    assert events[0]["data"]["phase"] == "domain_qa"
    assert events[-1]["type"] == "response_chunk"
    assert "违约责任条款" in events[-1]["data"]["accumulated"]


def test_general_agent_astream_exposes_domain_graph_failure(monkeypatch):
    from langchain_core.messages import HumanMessage

    from agentchat.core.agents.general_agent import AgentConfig, GeneralAgent

    async def fake_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": "contract_review",
            "domain_pack": {"id": "contract_review"},
        }

    async def fake_run_domain_qa(self, **kwargs):
        return {
            "domain_pack_id": "contract_review",
            "status": "failed",
            "failure_metadata": {"node": "retrieve_evidence", "error": "retrieval backend unavailable"},
            "trace_metadata": {"nodes": [{"node": "retrieve_evidence", "payload": {"status": "ERROR"}}]},
            "cost_metadata": {"status": "failed", "failed_node": "retrieve_evidence", "used_domain_pack": True},
            "final_answer": "领域问答流程在 `retrieve_evidence` 节点失败：retrieval backend unavailable",
        }

    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )
    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.AgentRuntime.run_domain_qa",
        fake_run_domain_qa,
    )

    agent = GeneralAgent(
        AgentConfig(
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
    )
    agent.conversation_model = SimpleNamespace()

    events = asyncio.run(_collect_events(agent, [HumanMessage(content="这份合同是否约定违约责任？")]))

    assert events[1]["type"] == "event"
    assert events[1]["data"]["status"] == "ERROR"
    assert events[1]["data"]["failure_metadata"]["node"] == "retrieve_evidence"
    assert "retrieve_evidence" in events[-1]["data"]["accumulated"]


async def _collect_events(agent, messages):
    return [event async for event in agent.astream(messages)]


def test_general_agent_astream_can_select_multi_agent_runtime(monkeypatch):
    from langchain_core.messages import HumanMessage

    from agentchat.core.agents.general_agent import AgentConfig, GeneralAgent

    async def fake_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": "contract_review",
            "domain_pack": {"id": "contract_review"},
            "knowledge_config": {"retrieval_settings": {"default_mode": "graphrag", "multi_agent_enabled": True}},
        }

    async def fake_run_domain_qa(self, **kwargs):
        assert kwargs["runtime_settings"]["knowledge_config"]["retrieval_settings"]["multi_agent_enabled"] is True
        return {
            "domain_pack_id": "contract_review",
            "status": "completed",
            "final_answer": "multi-agent supervisor produced a contract review answer",
            "trace_metadata": {
                "nodes": [
                    {"node": "plan_specialists"},
                    {"node": "domain_qa_specialist"},
                    {"node": "citation_verifier_specialist"},
                    {"node": "finalize"},
                ]
            },
            "cost_metadata": {"used_domain_pack": True, "specialist_count": 2},
        }

    class FailReactAgent:
        async def astream(self, *args, **kwargs):
            raise AssertionError("react agent path should be bypassed for multi-agent domain runtime")
            yield None

    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )
    monkeypatch.setattr(
        "agentchat.core.agents.general_agent.AgentRuntime.run_domain_qa",
        fake_run_domain_qa,
    )

    agent = GeneralAgent(
        AgentConfig(
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
    )
    agent.react_agent = FailReactAgent()
    agent.conversation_model = SimpleNamespace()

    events = asyncio.run(_collect_events(agent, [HumanMessage(content="请用多agent审查这份合同")]))

    assert events[0]["data"]["phase"] == "domain_qa"
    assert events[1]["data"]["trace_metadata"]["nodes"][0]["node"] == "plan_specialists"
    assert events[-1]["type"] == "response_chunk"
    assert "multi-agent supervisor produced" in events[-1]["data"]["accumulated"]
