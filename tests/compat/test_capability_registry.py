import asyncio
from types import SimpleNamespace


def test_capability_registry_searches_tools_skills_and_mcp(monkeypatch):
    from agentchat.services.capability_registry import CapabilityRegistryService

    async def fake_tools(user_id):
        return [
            {
                "tool_id": "tool-email",
                "name": "send_email",
                "display_name": "发送邮件",
                "description": "通过 SMTP 发送邮件",
                "runtime_type": "cli",
                "is_user_defined": False,
                "user_id": "system",
            }
        ]

    async def fake_skills(user_id):
        return [
            {
                "id": "skill-paper",
                "name": "论文检索",
                "description": "去公开论文源检索文献",
                "as_tool_name": "paper_search_skill",
                "source": "user",
            }
        ]

    async def fake_mcps(user_id):
        return [
            {
                "mcp_server_id": "mcp-lark",
                "server_name": "飞书",
                "mcp_as_tool_name": "lark",
                "description": "飞书 MCP 服务",
                "type": "stdio",
                "tools": ["send_message"],
                "params": [
                    {
                        "name": "send_message",
                        "description": "给飞书联系人发送消息",
                        "input_schema": {"type": "object", "properties": {}},
                    }
                ],
                "test_status": {"success": True, "tools": ["send_message"]},
            }
        ]

    monkeypatch.setattr("agentchat.services.capability_registry.ToolService.get_visible_tool_by_user", fake_tools)
    monkeypatch.setattr("agentchat.services.capability_registry.AgentSkillService.get_agent_skills", fake_skills)
    monkeypatch.setattr("agentchat.services.capability_registry.MCPService.get_all_servers", fake_mcps)

    results = asyncio.run(CapabilityRegistryService.search("飞书 发消息", user_id="u1"))

    assert results
    assert results[0]["kind"] == "mcp_tool"
    assert results[0]["name"] == "send_message"
    assert results[0]["display_name"] == "飞书 / send_message"
    assert results[0]["status"] == "ready"
    assert results[0]["invoke_ref"] == {
        "mcp_server_id": "mcp-lark",
        "mcp_tool_name": "send_message",
    }

    skill_results = asyncio.run(CapabilityRegistryService.search("文献", user_id="u1", kind="skill"))
    assert [item["name"] for item in skill_results] == ["论文检索"]


def test_capability_registry_reports_unconfigured_mcp(monkeypatch):
    from agentchat.services.capability_registry import CapabilityRegistryService

    async def fake_tools(user_id):
        return []

    async def fake_skills(user_id):
        return []

    async def fake_mcps(user_id):
        return [
            {
                "mcp_server_id": "mcp-lark",
                "server_name": "飞书",
                "description": "飞书 MCP 服务",
                "tools": ["send_message"],
                "params": [{"name": "send_message", "description": "发送飞书消息"}],
                "test_status": {"success": False, "message": "缺少 App Secret"},
            }
        ]

    monkeypatch.setattr("agentchat.services.capability_registry.ToolService.get_visible_tool_by_user", fake_tools)
    monkeypatch.setattr("agentchat.services.capability_registry.AgentSkillService.get_agent_skills", fake_skills)
    monkeypatch.setattr("agentchat.services.capability_registry.MCPService.get_all_servers", fake_mcps)

    results = asyncio.run(CapabilityRegistryService.search("飞书", user_id="u1"))

    assert results[0]["status"] == "needs_config"
    assert results[0]["status_message"] == "缺少 App Secret"


def test_capability_search_route_uses_login_user(monkeypatch):
    from agentchat.api.v1.capability import search_capabilities
    from agentchat.schema.capability import CapabilitySearchReq

    captured = {}

    async def fake_search(query, *, user_id, kind=None, limit=8):
        captured.update({"query": query, "user_id": user_id, "kind": kind, "limit": limit})
        return [{"id": "tool:send_email", "name": "send_email"}]

    monkeypatch.setattr("agentchat.api.v1.capability.CapabilityRegistryService.search", fake_search)

    response = asyncio.run(
        search_capabilities(
            req=CapabilitySearchReq(query="邮件", kind="tool", limit=3),
            login_user=SimpleNamespace(user_id="u_route"),
        )
    )

    assert captured == {"query": "邮件", "user_id": "u_route", "kind": "tool", "limit": 3}
    assert response.data[0]["name"] == "send_email"
