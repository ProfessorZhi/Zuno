import asyncio
from types import SimpleNamespace

from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_core.tools import tool as lc_tool


async def _collect_events(agent, query: str):
    return [event async for event in agent.astream([HumanMessage(content=query)])]


async def _collect_events_from_generator(generator):
    return [event async for event in generator]


def test_astream_direct_routes_non_explicit_mcp_query(monkeypatch):
    from agentchat.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    @lc_tool
    def maps_weather(city: str) -> str:
        """Return weather info for a city."""
        return f"weather:{city}"

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        mcp_configs=[
            MCPConfig(
                server_name="高德地图",
                mcp_server_id="mcp_1",
                url="http://example.com",
            )
        ],
        original_query="请用高德地图查询南京今天天气，并简短回答。",
    )
    agent._initialized = True
    agent.mcp_tools = [maps_weather]
    agent.server_dict = {"高德地图": ["maps_weather"]}

    captured = {}

    async def fake_run_direct_routed_tool(tool, args, original_query):
        captured["tool_name"] = tool.name
        captured["args"] = args
        captured["query"] = original_query
        yield {"event": "final", "data": {"done": True}}

    monkeypatch.setattr(agent, "_run_direct_routed_tool", fake_run_direct_routed_tool)

    asyncio.run(_collect_events(agent, agent.original_query))

    assert captured["tool_name"] == "maps_weather"
    assert captured["args"]["city"] == "南京"
    assert captured["query"] == "请用高德地图查询南京今天天气，并简短回答。"


def test_canonical_mcp_target_handles_custom_server_name_without_recursion(monkeypatch):
    from agentchat.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        mcp_configs=[
            MCPConfig(
                server_name="qa-mcp-461126",
                mcp_server_id="mcp_1",
                url="http://example.com",
            )
        ],
    )
    agent.server_dict = {"qa-mcp-461126": ["qa_mcp_ping"]}

    assert agent._canonical_mcp_target("qa-mcp-461126") == "qa-mcp-461126"


def test_normalize_weekday_labels_corrects_model_generated_weekdays():
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    text = (
        "| 日期 | 收盘 |\n"
        "| 2026-04-24（周四） | 208.27 |\n"
        "| 2026-04-25（周日） | 210.00 |\n"
        "| 2026-04-27（周一） | 216.61 |\n"
    )

    normalized = WorkSpaceSimpleAgent._normalize_weekday_labels(text)

    assert "2026-04-24（周五）" in normalized
    assert "2026-04-25（周六）" in normalized
    assert "2026-04-27（周一）" in normalized


def test_tool_result_for_model_enriches_market_ohlc_payload():
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    raw_result = {
        "data": [
            {
                "date": "2026-04-24T00:00:00+0000",
                "symbol": "NVDA",
                "open": 199.96,
                "high": 210.95,
                "low": 199.81,
                "close": 208.27,
                "volume": 213000000,
            },
            {
                "date": "2026-04-23T00:00:00+0000",
                "symbol": "NVDA",
                "open": 202.40,
                "high": 203.83,
                "low": 197.22,
                "close": 199.64,
                "volume": 109000000,
            },
        ]
    }

    formatted = WorkSpaceSimpleAgent._format_tool_result_for_model(raw_result)

    assert "结构化行情数据" in formatted
    assert "| 2026-04-24 | 周五 | NVDA |" in formatted
    assert "+4.32%" in formatted


def test_guess_direct_mcp_call_extracts_clean_weather_city(monkeypatch):
    from agentchat.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    @lc_tool
    def maps_weather(city: str) -> str:
        """Return weather info for a city."""
        return f"weather:{city}"

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        mcp_configs=[
            MCPConfig(
                server_name="高德地图",
                mcp_server_id="mcp_1",
                url="http://example.com",
            )
        ],
        original_query="请用高德地图查询南京今天天气，并简短回答。",
    )
    agent.mcp_tools = [maps_weather]
    agent.server_dict = {"高德地图": ["maps_weather"]}

    direct_tool, direct_args = agent._guess_direct_mcp_call(agent.original_query)

    assert direct_tool is not None
    assert direct_tool.name == "maps_weather"
    assert direct_args == {"city": "南京"}


def test_mcp_without_user_config_is_treated_as_platform_ready(monkeypatch):
    from agentchat.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        mcp_configs=[
            MCPConfig(
                server_name="高德地图",
                mcp_server_id="mcp_ready",
                url="http://example.com",
                tools=["maps_weather"],
                config_enabled=False,
                config=[],
            )
        ],
    )
    agent.mcp_tools = [SimpleNamespace(name="maps_weather")]
    agent.server_dict = {"高德地图": ["maps_weather"]}

    assert agent.mcp_requires_user_config("maps_weather") is False


def test_init_simple_agent_enables_explicit_slash_skill(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    skill_dict = {
        "id": "skill_1",
        "name": "verify-skill",
        "description": "验证 skill",
        "as_tool_name": "verify_skill_tool",
        "folder": {
            "folder": [
                {
                    "name": "SKILL.md",
                    "type": "file",
                    "path": "/verify-skill/SKILL.md",
                    "content": "---\nname: verify-skill\ndescription: 验证 skill\n---",
                }
            ]
        },
    }

    async def fake_catalog(_user_id):
        return [skill_dict]

    async def fake_skills_by_ids(_ids):
        return []

    async def noop(self):
        return None

    async def fake_middlewares(self):
        return []

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.AgentSkillService.get_agent_skills",
        fake_catalog,
    )
    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.AgentSkillService.get_agent_skills_by_ids",
        fake_skills_by_ids,
    )
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_terminal_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_mcp_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_plugin_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_knowledge_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_skill_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_middlewares", fake_middlewares)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_react_agent", lambda self: SimpleNamespace())

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        original_query="/verify-skill 请总结这个问题",
    )
    agent.plugin_tools = []
    agent.mcp_tools = []
    agent.knowledge_tools = []
    agent.skill_tools = []
    agent.terminal_tools = []

    asyncio.run(agent.init_simple_agent())

    assert agent.route_hint.kind == "skill"
    assert agent.route_hint.target == "verify-skill"
    assert "skill_1" in agent.agent_skill_ids


def test_init_simple_agent_enables_explicit_slash_skill_with_numeric_name(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    skill_dict = {
        "id": "skill_1",
        "name": "verify-skill-20260417",
        "description": "验证数字 skill",
        "as_tool_name": "verify_skill_tool_20260417",
        "folder": {
            "folder": [
                {
                    "name": "SKILL.md",
                    "type": "file",
                    "path": "/verify-skill-20260417/SKILL.md",
                    "content": "---\nname: verify-skill-20260417\ndescription: 验证数字 skill\n---",
                }
            ]
        },
    }

    async def fake_catalog(_user_id):
        return [skill_dict]

    async def fake_skills_by_ids(_ids):
        return []

    async def noop(self):
        return None

    async def fake_middlewares(self):
        return []

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.AgentSkillService.get_agent_skills",
        fake_catalog,
    )
    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.AgentSkillService.get_agent_skills_by_ids",
        fake_skills_by_ids,
    )
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_terminal_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_mcp_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_plugin_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_knowledge_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_skill_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_middlewares", fake_middlewares)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_react_agent", lambda self: SimpleNamespace())

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        original_query="/verify-skill-20260417 请总结这个问题",
    )
    agent.plugin_tools = []
    agent.mcp_tools = []
    agent.knowledge_tools = []
    agent.skill_tools = []
    agent.terminal_tools = []

    asyncio.run(agent.init_simple_agent())

    assert agent.route_hint.kind == "skill"
    assert agent.route_hint.target == "verify-skill-20260417"
    assert "skill_1" in agent.agent_skill_ids


def test_extract_api_tool_creation_payload_keeps_docs_urls_and_does_not_treat_them_as_endpoint(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
    )

    payload = agent._extract_api_tool_creation_payload(
        "文档地址：https://docs.apilayer.com/ipstack/docs/quickstart-guide?utm_source=dashboard&utm_medium=Referral\n"
        "https://docs.apilayer.com/ipstack/docs/getting-started?utm_source=dashboard&utm_medium=Referral\n"
        "https://docs.apilayer.com/ipstack/docs/ipstack-api-v-1-0-0?utm_source=dashboard&utm_medium=Referral"
    )

    assert payload["docs_url"].startswith("https://docs.apilayer.com/ipstack/docs/quickstart-guide")
    assert len(payload["docs_urls"]) == 3
    assert payload["endpoint_url"] == ""


def test_extract_api_tool_creation_payload_recognizes_access_key_label(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
    )

    payload = agent._extract_api_tool_creation_payload("access_key：test-ipstack-key")

    assert payload["api_key"] == "test-ipstack-key"


def test_extract_api_tool_creation_payload_merges_docs_urls_across_turns(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
    )

    base_payload = agent._extract_api_tool_creation_payload(
        "文档地址：https://docs.example.com/quickstart\nhttps://docs.example.com/reference"
    )
    merged = agent._extract_api_tool_creation_payload(
        "再补一条文档地址：https://docs.example.com/auth",
        base_payload=base_payload,
    )

    assert merged["docs_url"] == "https://docs.example.com/quickstart"
    assert merged["docs_urls"] == [
        "https://docs.example.com/quickstart",
        "https://docs.example.com/reference",
        "https://docs.example.com/auth",
    ]


def test_plan_tool_creation_flow_normalizes_none_sample_curl(monkeypatch):
    from agentchat.schema.tool import RemoteApiAssistResp, SimpleApiConfig
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
    )
    agent.plugin_tools = [SimpleNamespace(name="create_remote_api_tool")]

    async def fake_pending_state():
        return {
            "kind": "api",
            "payload": {
                "display_name": "ipstack-tool",
                "docs_url": "https://docs.example.com/ipstack",
                "docs_urls": ["https://docs.example.com/ipstack"],
                "sample_curl": None,
                "auth_type": "api_key_query",
                "api_key_name": "access_key",
            },
        }

    monkeypatch.setattr(agent, "_get_pending_tool_creation_state", fake_pending_state)

    def fake_assist(req):
        assert req.sample_curl == ""
        return RemoteApiAssistResp(
            display_name="ipstack-tool",
            description="lookup ip",
            simple_api_config=SimpleApiConfig(
                base_url="http://api.ipstack.com",
                path="/check",
                method="GET",
                operation_id="ipstack_tool",
                summary="ipstack-tool",
                description="lookup ip",
                params=[],
            ),
            auth_config={"auth_type": "APIKey", "in": "query", "name": "access_key", "data": ""},
            openapi_schema={"openapi": "3.1.0", "info": {"title": "ipstack-tool", "version": "1.0.0"}, "servers": [], "paths": {}},
            warnings=[],
        )

    monkeypatch.setattr("agentchat.services.workspace.simple_agent.build_remote_api_assist_draft", fake_assist)

    result = asyncio.run(agent._plan_tool_creation_flow("access_key：demo-key"))

    assert result is not None
    assert result["mode"] == "create"
    assert result["payload"]["api_key"] == "demo-key"


def test_prepare_explicit_skill_messages_injects_context(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    skill_dict = {
        "id": "skill_1",
        "name": "verify-skill",
        "description": "验证 skill",
        "as_tool_name": "verify_skill_tool",
        "folder": {
            "folder": [
                {
                    "name": "SKILL.md",
                    "type": "file",
                    "path": "/verify-skill/SKILL.md",
                    "content": "---\nname: verify-skill\ndescription: 验证 skill\n---\n请输出 SKILL_OK。",
                }
            ]
        },
    }

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        original_query="/verify-skill 请总结这个问题",
        agent_skill_ids=["skill_1"],
    )
    agent.available_skills = [skill_dict]
    agent.route_hint.kind = "skill"
    agent.route_hint.target = "verify-skill"

    messages = [HumanMessage(content="/verify-skill 请总结这个问题")]
    prepared = agent._prepare_explicit_skill_messages(messages, "请总结这个问题")

    assert isinstance(prepared[-1], HumanMessage)
    assert "Skill Name: verify-skill" in prepared[-1].content
    assert "Current User Task: 请总结这个问题" in prepared[-1].content
    assert "[User Task]\n请总结这个问题" in prepared[-1].content


def test_detect_route_hint_prefers_explicit_slash_skill_over_knowledge_keywords(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        original_query="/verify-skill-20260417 请简单说明什么是RAG。",
    )

    route = agent._detect_route_hint(agent.original_query)

    assert route.kind == "skill"
    assert route.target == "verify-skill-20260417"


def test_plan_tool_creation_flow_asks_for_api_key_when_docs_infer_query_auth(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent
    from agentchat.schema.tool import RemoteApiAssistResp, SimpleApiConfig

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )
    async def fake_get_session(*_args, **_kwargs):
        return None

    def fake_assist(_req):
        return RemoteApiAssistResp(
            display_name="IPStack",
            description="Lookup IP location",
            simple_api_config=SimpleApiConfig(
                base_url="https://api.ipstack.com",
                path="/check",
                method="GET",
                operation_id="lookupCurrentIp",
                summary="IPStack",
                description="Lookup IP location",
                params=[],
            ),
            auth_config={"auth_type": "APIKey", "in": "query", "name": "access_key"},
            openapi_schema={"openapi": "3.1.0", "info": {}, "servers": [], "paths": {}},
            warnings=[],
        )

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.WorkSpaceSessionService.get_workspace_session_from_id",
        fake_get_session,
    )
    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.build_remote_api_assist_draft",
        fake_assist,
    )

    agent = WorkSpaceSimpleAgent(model_config={}, user_id="u_1", session_id="s_1")

    plan = asyncio.run(agent._plan_tool_creation_flow("新增API工具 名称叫 ipstack 文档地址: https://ipstack.com/documentation"))

    assert plan["mode"] == "ask"
    assert plan["kind"] == "api"
    assert "access_key" in plan["reply"]
    assert plan["payload"]["api_key_name"] == "access_key"


def test_plan_tool_creation_flow_uses_pending_state_to_finish_creation(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent
    from agentchat.schema.tool import RemoteApiAssistResp, SimpleApiConfig

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    async def fake_get_session(*_args, **_kwargs):
        return {
            "contexts": [
                {
                    "query": "新增API工具 名称叫 ipstack",
                    "answer": "请继续提供 API Key",
                    "metadata": {
                        "tool_creation_state": {
                            "kind": "api",
                            "payload": {
                                "display_name": "ipstack",
                                "docs_url": "https://ipstack.com/documentation",
                                "auth_type": "api_key_query",
                                "api_key_name": "access_key",
                            },
                        }
                    },
                }
            ]
        }

    def fake_assist(_req):
        return RemoteApiAssistResp(
            display_name="IPStack",
            description="Lookup IP location",
            simple_api_config=SimpleApiConfig(
                base_url="https://api.ipstack.com",
                path="/check",
                method="GET",
                operation_id="lookupCurrentIp",
                summary="IPStack",
                description="Lookup IP location",
                params=[],
            ),
            auth_config={"auth_type": "APIKey", "in": "query", "name": "access_key"},
            openapi_schema={"openapi": "3.1.0", "info": {}, "servers": [], "paths": {}},
            warnings=[],
        )

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.WorkSpaceSessionService.get_workspace_session_from_id",
        fake_get_session,
    )
    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.build_remote_api_assist_draft",
        fake_assist,
    )

    agent = WorkSpaceSimpleAgent(model_config={}, user_id="u_1", session_id="s_1")
    agent.plugin_tools = [SimpleNamespace(name="create_remote_api_tool")]

    plan = asyncio.run(agent._plan_tool_creation_flow("API Key: demo-key-123"))

    assert plan["mode"] == "create"
    assert plan["kind"] == "api"
    assert plan["payload"]["api_key"] == "demo-key-123"


def test_astream_slash_skill_uses_injected_context_and_continues(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    skill_dict = {
        "id": "skill_1",
        "name": "verify-skill",
        "description": "验证 skill",
        "as_tool_name": "verify_skill_tool",
        "folder": {
            "folder": [
                {
                    "name": "SKILL.md",
                    "type": "file",
                    "path": "/verify-skill/SKILL.md",
                    "content": "---\nname: verify-skill\ndescription: 验证 skill\n---\n请输出 SKILL_OK。",
                }
            ]
        },
    }

    captured = {}

    class FakeReactAgent:
        async def astream(self, input, config=None, stream_mode=None):
            captured["messages"] = input["messages"]
            yield ("messages", (AIMessageChunk(content="SKILL_OK"), {}))

    async def fake_catalog(_user_id):
        return [skill_dict]

    async def fake_skills_by_ids(_ids):
        return []

    async def noop(self):
        return None

    async def fake_middlewares(self):
        return []

    async def fake_generate_title(self, query):
        return query

    async def fake_add_workspace_session(self, title, contexts):
        return None

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.AgentSkillService.get_agent_skills",
        fake_catalog,
    )
    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.AgentSkillService.get_agent_skills_by_ids",
        fake_skills_by_ids,
    )
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_terminal_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_mcp_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_plugin_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_knowledge_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_skill_tools", noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_middlewares", fake_middlewares)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "setup_react_agent", lambda self: FakeReactAgent())
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_generate_title", fake_generate_title)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_add_workspace_session", fake_add_workspace_session)

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        original_query="/verify-skill 请总结这个问题",
    )
    agent.plugin_tools = []
    agent.mcp_tools = []
    agent.knowledge_tools = []
    agent.skill_tools = []
    agent.terminal_tools = []

    events = asyncio.run(_collect_events(agent, agent.original_query))

    assert not any(event.get("event") == "tool_call" for event in events)
    assert any(event.get("event") == "final" for event in events)
    assert isinstance(captured["messages"][-1], HumanMessage)
    assert "Skill Name: verify-skill" in captured["messages"][-1].content
    assert "[User Task]\n请总结这个问题" in captured["messages"][-1].content


def test_astream_ignores_leading_blank_chunk_before_tool_events(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    class FakeReactAgent:
        async def astream(self, input, config=None, stream_mode=None):
            yield ("messages", (AIMessageChunk(content="\n"), {}))
            yield (
                "custom",
                {
                    "event": "tool_call",
                    "timestamp": 1.0,
                    "data": {
                        "tool_name": "echo_runner",
                        "tool_call_id": "tool_1",
                    },
                },
            )
            yield (
                "custom",
                {
                    "event": "tool_result",
                    "timestamp": 2.0,
                    "data": {
                        "tool_name": "echo_runner",
                        "tool_call_id": "tool_1",
                        "ok": True,
                        "result": "ZUNO_ECHO:hello",
                    },
                },
            )
            yield ("messages", (AIMessageChunk(content="工具调用完成"), {}))

    async def fake_generate_title(self, query):
        return query

    async def fake_add_workspace_session(self, title, contexts):
        return None

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        original_query="请调用 echo_runner",
    )
    agent._initialized = True
    agent.react_agent = FakeReactAgent()

    monkeypatch.setattr(WorkSpaceSimpleAgent, "_generate_title", fake_generate_title)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_add_workspace_session", fake_add_workspace_session)

    events = asyncio.run(_collect_events(agent, agent.original_query))

    assert [event["event"] for event in events] == [
        "status",
        "tool_call",
        "tool_result",
        "final",
        "status",
    ]
    assert events[3]["data"]["message"] == "工具调用完成"
    assert events[3]["data"]["done"] is False


def test_skill_route_does_not_over_restrict_request_tools(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )
    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.get_stream_writer",
        lambda: (lambda _payload: None),
    )

    @lc_tool
    def verify_skill_tool(query: str) -> str:
        """Load skill guidance."""
        return query

    @lc_tool
    def list_enabled_capabilities() -> str:
        """List enabled capabilities."""
        return "ok"

    @lc_tool
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base."""
        return query

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        original_query="/verify-skill 请总结这个问题",
    )
    agent.route_hint.kind = "skill"
    agent.route_hint.target = "verify-skill"
    agent.skill_tools = [verify_skill_tool]
    agent.plugin_tools = [list_enabled_capabilities]
    agent.knowledge_tools = [search_knowledge_base]
    agent.tools = [list_enabled_capabilities, search_knowledge_base, verify_skill_tool]

    middlewares = asyncio.run(agent.setup_middlewares())
    middleware = middlewares[1]

    request = SimpleNamespace(
        state={},
        tools=[list_enabled_capabilities, search_knowledge_base, verify_skill_tool],
    )
    captured = {}

    async def fake_handler(inner_request):
        captured["tool_names"] = [tool.name for tool in inner_request.tools]
        return SimpleNamespace(tool_calls=[])

    asyncio.run(middleware.awrap_model_call(request, fake_handler))

    assert captured["tool_names"] == [
        "list_enabled_capabilities",
        "search_knowledge_base",
        "verify_skill_tool",
    ]


def test_prefetched_knowledge_context_is_injected_into_messages(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    async def fake_retrieve(*args, **kwargs):
        return {
            "content": "Zuno -> Neo4j\nMCP -> Skill",
            "round_count": 1,
            "first_mode": "graphrag",
            "final_mode": "graphrag",
            "rounds": [],
        }

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.RagHandler.retrieve_ranked_documents_with_metadata",
        fake_retrieve,
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    context = asyncio.run(agent._prefetch_knowledge_context("Zuno 与 Neo4j 是什么关系？"))
    messages = agent._inject_prefetched_knowledge_context(
        [HumanMessage(content="Zuno 与 Neo4j 是什么关系？")],
        context["content"],
        "Zuno 与 Neo4j 是什么关系？",
    )

    assert context["content"] == "Zuno -> Neo4j\nMCP -> Skill"
    assert "[Knowledge Context]" in messages[-1].content
    assert "MCP -> Skill" in messages[-1].content
    assert "[User Task]\nZuno 与 Neo4j 是什么关系？" in messages[-1].content


def test_prefetched_knowledge_disables_web_search_for_non_realtime_query(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    @lc_tool
    def web_search(query: str) -> str:
        """Search the web."""
        return query

    @lc_tool
    def read_webpage(url: str) -> str:
        """Read a webpage."""
        return url

    @lc_tool
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base."""
        return query

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )
    agent.tools = [web_search, read_webpage, search_knowledge_base]

    filtered = agent._build_runtime_tools(
        "Zuno 与 Neo4j 是什么关系？",
        "Zuno -> Neo4j",
    )
    filtered_names = [tool.name for tool in filtered]

    assert "search_knowledge_base" in filtered_names
    assert "web_search" not in filtered_names
    assert "read_webpage" not in filtered_names


def test_prefetched_knowledge_keeps_web_search_for_realtime_query(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    @lc_tool
    def web_search(query: str) -> str:
        """Search the web."""
        return query

    @lc_tool
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base."""
        return query

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="rag",
    )
    agent.tools = [web_search, search_knowledge_base]

    filtered = agent._build_runtime_tools(
        "南京今天天气怎么样？",
        "已有知识上下文",
    )

    assert [tool.name for tool in filtered] == ["web_search", "search_knowledge_base"]


def test_direct_maps_weather_result_is_humanized_for_final_answer(monkeypatch):
    from agentchat.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    @lc_tool
    def maps_weather(city: str) -> str:
        """Return weather info for a city."""
        return (
            '{"status":"1","lives":[{"province":"江苏","city":"南京","weather":"晴","temperature":"26",'
            '"humidity":"58","winddirection":"东南","windpower":"3","reporttime":"2026-04-18 13:00:00"}]}'
        )

    stored = {}

    async def fake_generate_title(self, query):
        return query

    async def fake_add_workspace_session(self, title, contexts):
        stored["title"] = title
        stored["answer"] = contexts.answer

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        mcp_configs=[
            MCPConfig(
                server_name="高德地图",
                mcp_server_id="mcp_1",
                url="http://example.com",
                tools=["maps_weather"],
            )
        ],
    )
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_generate_title", fake_generate_title)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_add_workspace_session", fake_add_workspace_session)

    events = asyncio.run(
        _collect_events_from_generator(
            agent._run_direct_routed_tool(
                maps_weather,
                {"city": "南京"},
                "请用高德地图查询南京今天天气，并简短回答。",
            )
        )
    )

    tool_result_event = next(event for event in events if event.get("event") == "tool_result")
    final_event = next(event for event in events if event.get("event") == "final")

    assert '"lives"' in tool_result_event["data"]["result"]
    assert "南京当前晴" in final_event["data"]["message"]
    assert "气温 26°C" in final_event["data"]["message"]
    assert stored["answer"] == final_event["data"]["message"]


def test_setup_plugin_tools_registers_tool_creation_helpers(monkeypatch):
    from agentchat.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    async def fake_get_tools_from_id(_ids):
        return []

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ToolService.get_tools_from_id",
        fake_get_tools_from_id,
    )
    monkeypatch.setattr("agentchat.services.workspace.simple_agent.WorkSpacePlugins", {})

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
    )

    asyncio.run(agent.setup_plugin_tools())

    names = {tool.name for tool in agent.plugin_tools}
    assert "search_available_capabilities" in names
    assert "create_remote_api_tool" in names
    assert "create_cli_tool" in names


def test_direct_maps_weather_root_forecasts_are_humanized(monkeypatch):
    from agentchat.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "agentchat.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    @lc_tool
    def maps_weather(city: str) -> str:
        """Return weather info for a city."""
        return (
            '{"city":"南京市","forecasts":[{"date":"2026-04-18","dayweather":"晴","nightweather":"晴",'
            '"daytemp":"23","nighttemp":"12","daywind":"东","daypower":"1-3"}]}'
        )

    stored = {}

    async def fake_generate_title(self, query):
        return query

    async def fake_add_workspace_session(self, title, contexts):
        stored["answer"] = contexts.answer

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        mcp_configs=[
            MCPConfig(
                server_name="高德地图",
                mcp_server_id="mcp_1",
                url="http://example.com",
                tools=["maps_weather"],
            )
        ],
    )
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_generate_title", fake_generate_title)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_add_workspace_session", fake_add_workspace_session)

    events = asyncio.run(
        _collect_events_from_generator(
            agent._run_direct_routed_tool(
                maps_weather,
                {"city": "南京"},
                "请用高德地图查询南京今天天气，并简短回答。",
            )
        )
    )

    final_event = next(event for event in events if event.get("event") == "final")

    assert "南京市2026-04-18晴" in final_event["data"]["message"]
    assert "预计气温 12-23°C" in final_event["data"]["message"]
    assert stored["answer"] == final_event["data"]["message"]
