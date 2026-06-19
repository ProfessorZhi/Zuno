import asyncio

from zuno.schema.workspace import WorkSpaceSimpleTask


def _task(**kwargs):
    return WorkSpaceSimpleTask(
        query="你好",
        model_id="model_1",
        session_id="session_1",
        plugins=[],
        mcp_servers=[],
        **kwargs,
    )


def test_normal_workspace_usage_keeps_internal_simple_agent():
    from zuno.api.v1.workspace import _resolve_workspace_usage_agent_name

    result = asyncio.run(
        _resolve_workspace_usage_agent_name(
            _task(workspace_mode="normal", agent_name="Demo Agent"),
            "user_1",
            {"agent": "Demo Agent"},
        )
    )

    assert result == "Simple-Agent"


def test_agent_workspace_usage_prefers_session_agent_name():
    from zuno.api.v1.workspace import _resolve_workspace_usage_agent_name

    result = asyncio.run(
        _resolve_workspace_usage_agent_name(
            _task(workspace_mode="agent"),
            "user_1",
            {"agent": "Agent Alpha"},
        )
    )

    assert result == "Agent Alpha"


def test_agent_workspace_usage_can_resolve_agent_id(monkeypatch):
    from zuno.api.v1 import workspace

    async def fake_select_agent_by_id(agent_id):
        assert agent_id == "agent_1"
        return {"name": "Agent Beta", "user_id": "user_1"}

    monkeypatch.setattr(workspace.AgentService, "select_agent_by_id", fake_select_agent_by_id)

    result = asyncio.run(
        workspace._resolve_workspace_usage_agent_name(
            _task(workspace_mode="agent", agent_id="agent_1"),
            "user_1",
            {"agent": "agent"},
        )
    )

    assert result == "Agent Beta"


def test_workspace_simple_chat_can_enable_multi_agent_runtime(monkeypatch):
    from zuno.api.v1.workspace import workspace_simple_chat
    from zuno.schema.workspace import WorkSpaceSimpleTask

    captured = {}

    class FakeSimpleAgent:
        def __init__(self, **kwargs):
            captured["multi_agent_enabled"] = kwargs["multi_agent_enabled"]

        async def astream(self, messages):
            yield {
                "event": "final",
                "timestamp": 0.0,
                "data": {"chunk": "ok", "message": "ok", "accumulated": "ok", "done": True},
            }

    async def fake_get_llm_by_id(model_id):
        assert model_id == "model_1"
        return {
            "model": "test-model",
            "base_url": "https://example.com",
            "api_key": "key",
            "provider": "openai",
        }

    async def fake_get_workspace_session_from_id(session_id, user_id):
        assert session_id == "session_1"
        assert user_id == "user_1"
        return {"agent": "simple", "contexts": []}

    async def fake_get_tools_from_id(_plugin_ids):
        return []

    async def fake_build_workspace_attachment_prompt(**kwargs):
        return kwargs["query"]

    monkeypatch.setattr("zuno.api.v1.workspace.LLMService.get_llm_by_id", fake_get_llm_by_id)
    monkeypatch.setattr(
        "zuno.api.v1.workspace.WorkSpaceSessionService.get_workspace_session_from_id",
        fake_get_workspace_session_from_id,
    )
    monkeypatch.setattr("zuno.api.v1.workspace.ToolService.get_tools_from_id", fake_get_tools_from_id)
    monkeypatch.setattr(
        "zuno.api.v1.workspace.build_workspace_attachment_prompt",
        fake_build_workspace_attachment_prompt,
    )
    monkeypatch.setattr(
        "zuno.api.v1.workspace.validate_tools_for_mode",
        lambda tools, execution_mode: None,
    )
    monkeypatch.setattr("zuno.api.v1.workspace.WorkSpaceSimpleAgent", FakeSimpleAgent)

    response = asyncio.run(
        workspace_simple_chat(
            simple_task=WorkSpaceSimpleTask(
                query="请用多 agent 审查这份合同",
                model_id="model_1",
                session_id="session_1",
                plugins=[],
                mcp_servers=[],
                knowledge_ids=["kb_1"],
                multi_agent_enabled=True,
            ),
            login_user=type("User", (), {"user_id": "user_1"})(),
        )
    )

    assert captured["multi_agent_enabled"] is True
    assert response.media_type == "text/event-stream"
