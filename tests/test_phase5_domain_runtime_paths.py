import asyncio
import importlib
import json
import subprocess
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_backend_path() -> None:
    backend_path = str(BACKEND_ROOT)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def test_zuno_agent_runtime_uses_single_agent_graph_by_default():
    _ensure_backend_path()

    AgentRuntime = importlib.import_module("zuno.core.runtime.agent_runtime").AgentRuntime

    class FakeDomainGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "single", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "single", "state": state}

    class FakeMultiGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "multi", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "multi", "state": state}

    runtime = AgentRuntime(graph=FakeDomainGraph(), multi_agent_graph=FakeMultiGraph())

    result = asyncio.run(
        runtime.run_domain_qa(
            user_id="u1",
            agent_id="a1",
            dialog_id="d1",
            query="review contract",
            knowledge_ids=["kb_1"],
            runtime_settings={"knowledge_config": {"retrieval_settings": {}}},
            domain_pack={"id": "contract_review"},
        )
    )

    assert result["mode"] == "single"


def test_zuno_agent_runtime_uses_multi_agent_graph_when_enabled_in_domain_pack():
    _ensure_backend_path()

    AgentRuntime = importlib.import_module("zuno.core.runtime.agent_runtime").AgentRuntime

    class FakeDomainGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "single", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "single", "state": state}

    class FakeMultiGraph:
        def build_initial_state(self, **kwargs):
            return {"mode": "multi", **kwargs}

        async def ainvoke(self, state):
            return {"status": "completed", "mode": "multi", "state": state}

    runtime = AgentRuntime(graph=FakeDomainGraph(), multi_agent_graph=FakeMultiGraph())

    result = asyncio.run(
        runtime.run_domain_qa(
            user_id="u1",
            agent_id="a1",
            dialog_id="d1",
            query="review contract",
            knowledge_ids=["kb_1"],
            runtime_settings={"knowledge_config": {"retrieval_settings": {}}},
            domain_pack={"id": "contract_review", "multi_agent_enabled": True},
        )
    )

    assert result["mode"] == "multi"


def test_zuno_general_agent_knowledge_tool_uses_domain_pack_runtime(monkeypatch):
    script = textwrap.dedent(
        f"""
        import asyncio
        import json
        import sys
        sys.path.insert(0, {str(BACKEND_ROOT)!r})
        from zuno.core.agents.general_agent import AgentConfig, GeneralAgent
        import agentchat.core.agents.general_agent as ga

        async def fake_runtime_settings(_knowledge_id):
            return {{
                "domain_pack_id": "contract_review",
                "domain_pack": {{"id": "contract_review"}},
                "knowledge_config": {{"retrieval_settings": {{"default_mode": "graphrag"}}}},
            }}

        async def fake_run_domain_qa(self, **kwargs):
            return {{
                "final_answer": "结论\\n合同包含违约责任条款。",
            }}

        async def fail_if_called(*args, **kwargs):
            raise AssertionError("fallback RagHandler path should not be used when domain pack runtime is available")

        ga.KnowledgeService.get_runtime_settings = fake_runtime_settings
        ga.AgentRuntime.run_domain_qa = fake_run_domain_qa
        ga.RagHandler.retrieve_ranked_documents = fail_if_called

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

        async def main():
            await agent.setup_knowledge_tool()
            result = await agent.tools[0].ainvoke({{"query": "这份合同是否约定违约责任？"}})
            print(json.dumps({{"result": result}}, ensure_ascii=False))

        asyncio.run(main())
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout.strip())
    assert "违约责任条款" in payload["result"]


def test_zuno_general_agent_astream_prefers_explicit_domain_graph_runtime(monkeypatch):
    script = textwrap.dedent(
        f"""
        import asyncio
        import json
        import sys
        from types import SimpleNamespace
        sys.path.insert(0, {str(BACKEND_ROOT)!r})
        from langchain_core.messages import HumanMessage
        from zuno.core.agents.general_agent import AgentConfig, GeneralAgent
        import agentchat.core.agents.general_agent as ga

        async def fake_runtime_settings(_knowledge_id):
            return {{
                "domain_pack_id": "contract_review",
                "domain_pack": {{"id": "contract_review"}},
                "knowledge_config": {{"retrieval_settings": {{"default_mode": "graphrag"}}}},
            }}

        async def fake_run_domain_qa(self, **kwargs):
            return {{
                "domain_pack_id": "contract_review",
                "final_answer": "结论\\n合同包含违约责任条款。",
                "trace_metadata": {{"nodes": [{{"node": "resolve_domain_pack"}}]}},
                "cost_metadata": {{"used_domain_pack": True}},
            }}

        class FailReactAgent:
            async def astream(self, *args, **kwargs):
                raise AssertionError("react agent path should be bypassed for explicit domain graph runtime")
                yield None

        ga.KnowledgeService.get_runtime_settings = fake_runtime_settings
        ga.AgentRuntime.run_domain_qa = fake_run_domain_qa

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

        async def collect():
            return [event async for event in agent.astream([HumanMessage(content="这份合同是否约定违约责任？")])]

        events = asyncio.run(collect())
        print(json.dumps(events, ensure_ascii=False))
        """
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
    )
    events = json.loads(completed.stdout.strip())
    assert events[0]["type"] == "event"
    assert events[0]["data"]["phase"] == "domain_qa"
    assert events[-1]["type"] == "response_chunk"
    assert "违约责任条款" in events[-1]["data"]["accumulated"]
