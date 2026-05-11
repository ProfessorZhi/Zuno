import asyncio

from agentchat.schema.workspace import WorkSpaceSimpleTask


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
    from agentchat.api.v1.workspace import _resolve_workspace_usage_agent_name

    result = asyncio.run(
        _resolve_workspace_usage_agent_name(
            _task(workspace_mode="normal", agent_name="小志"),
            "user_1",
            {"agent": "小志"},
        )
    )

    assert result == "Simple-Agent"


def test_agent_workspace_usage_prefers_session_agent_name():
    from agentchat.api.v1.workspace import _resolve_workspace_usage_agent_name

    result = asyncio.run(
        _resolve_workspace_usage_agent_name(
            _task(workspace_mode="agent"),
            "user_1",
            {"agent": "智智子"},
        )
    )

    assert result == "智智子"


def test_agent_workspace_usage_can_resolve_agent_id(monkeypatch):
    from agentchat.api.v1 import workspace

    async def fake_select_agent_by_id(agent_id):
        assert agent_id == "agent_1"
        return {"name": "小志", "user_id": "user_1"}

    monkeypatch.setattr(workspace.AgentService, "select_agent_by_id", fake_select_agent_by_id)

    result = asyncio.run(
        workspace._resolve_workspace_usage_agent_name(
            _task(workspace_mode="agent", agent_id="agent_1"),
            "user_1",
            {"agent": "agent"},
        )
    )

    assert result == "小志"
