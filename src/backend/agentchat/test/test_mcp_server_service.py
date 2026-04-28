import asyncio
import pytest


def test_ensure_tools_available_returns_server_tools():
    from agentchat.api.services.mcp_server import MCPService

    tools = MCPService.ensure_tools_available(
        "qa-server",
        {
            "qa-server": [
                {"name": "qa_ping", "description": "ping", "input_schema": {"properties": {}}},
            ]
        },
    )

    assert tools == [{"name": "qa_ping", "description": "ping", "input_schema": {"properties": {}}}]


def test_ensure_tools_available_rejects_empty_server_tools():
    from agentchat.api.services.mcp_server import MCPService

    with pytest.raises(ValueError, match="没有获取到可用工具"):
        MCPService.ensure_tools_available("qa-server", {"qa-server": []})


def test_get_mcp_tools_info_tolerates_null_params(monkeypatch):
    from agentchat.api.services.mcp_server import MCPService

    class FakeServer:
        def to_dict(self):
            return {"params": None}

    async def fake_get_server(server_id):
        assert server_id == "server-1"
        return FakeServer()

    monkeypatch.setattr(
        "agentchat.api.services.mcp_server.MCPServerDao.get_mcp_server_from_id",
        fake_get_server,
    )

    result = asyncio.run(MCPService.get_mcp_tools_info("server-1"))

    assert result == []
