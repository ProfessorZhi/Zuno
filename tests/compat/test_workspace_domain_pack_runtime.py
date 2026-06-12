import asyncio
from types import SimpleNamespace


def test_workspace_prefetch_uses_domain_pack_runtime_when_available(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    async def fake_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": "contract_review",
            "domain_pack": {"id": "contract_review"},
            "knowledge_config": {"retrieval_settings": {"default_mode": "graphrag"}},
        }

    async def fake_run_domain_qa(self, **kwargs):
        return {
            "domain_pack_id": "contract_review",
            "final_answer": "结论\n合同存在终止条款风险。",
            "report_markdown": "# report",
            "trace_metadata": {"nodes": [{"node": "resolve_domain_pack"}]},
            "cost_metadata": {"used_domain_pack": True},
            "retrieval_result": {
                "actual_mode": "graphrag",
                "first_mode": "graphrag",
                "final_mode": "graphrag",
                "round_count": 1,
                "metadata": {"round_count": 1},
                "final_pass_result": {"documents": [], "paths": []},
                "graph_result": {"paths": []},
            },
        }

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )
    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.AgentRuntime.run_domain_qa",
        fake_run_domain_qa,
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    context = asyncio.run(agent._prefetch_knowledge_context("请审查终止条款"))

    assert context is not None
    assert "终止条款风险" in context["content"]
    assert context["result"]["domain_pack_id"] == "contract_review"


def test_workspace_retrieval_event_payload_exposes_domain_pack_failure(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    payload = agent._build_retrieval_event_payload(
        {
            "domain_pack_id": "contract_review",
            "metadata": {
                "domain_pack_trace": {"nodes": [{"node": "retrieve_evidence"}]},
                "domain_pack_cost": {"status": "failed", "failed_node": "retrieve_evidence"},
                "domain_pack_failure": {"node": "retrieve_evidence", "error": "retrieval backend unavailable"},
            },
        }
    )

    assert payload["status"] == "ERROR"
    assert payload["domain_pack_failure"]["node"] == "retrieve_evidence"
    assert payload["domain_pack_cost"]["failed_node"] == "retrieve_evidence"


def test_workspace_domain_pack_query_can_select_multi_agent_runtime(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    async def fake_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": "contract_review",
            "domain_pack": {"id": "contract_review"},
            "knowledge_config": {
                "retrieval_settings": {
                    "default_mode": "graphrag",
                    "multi_agent_enabled": True,
                }
            },
        }

    async def fail_single_agent_ainvoke(self, state):
        raise AssertionError("single-agent DomainQAGraph should not be used when multi_agent_enabled is true")

    async def fake_multi_agent_ainvoke(self, state):
        return {
            "domain_pack_id": "contract_review",
            "status": "completed",
            "final_answer": "multi-agent workspace contract review answer",
            "report_markdown": "# report",
            "trace_metadata": {
                "nodes": [
                    {"node": "plan_specialists"},
                    {"node": "domain_qa_specialist"},
                    {"node": "citation_verifier_specialist"},
                    {"node": "finalize"},
                ]
            },
            "cost_metadata": {"used_domain_pack": True, "specialist_count": 2},
            "failure_metadata": None,
            "retrieval_result": {
                "actual_mode": "graphrag",
                "first_mode": "graphrag",
                "final_mode": "graphrag",
                "round_count": 1,
                "metadata": {"round_count": 1},
                "final_pass_result": {"documents": [], "paths": []},
                "graph_result": {"paths": []},
            },
        }

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )
    monkeypatch.setattr(
        "agentchat.core.runtime.agent_runtime.DomainQAGraph.ainvoke",
        fail_single_agent_ainvoke,
    )
    monkeypatch.setattr(
        "agentchat.core.runtime.agent_runtime.MultiAgentSupervisorGraph.ainvoke",
        fake_multi_agent_ainvoke,
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    result = asyncio.run(agent._run_domain_pack_query("请用多agent审查这份合同"))

    assert result is not None
    assert result["domain_pack_id"] == "contract_review"
    assert "multi-agent workspace" in result["content"]
    assert result["metadata"]["domain_pack_trace"]["nodes"][0]["node"] == "plan_specialists"
    assert result["metadata"]["domain_pack_cost"]["specialist_count"] == 2
