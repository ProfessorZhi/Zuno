from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from zuno.platform.security import SecurityProductActionDenied


class RecordingProductActionGuard:
    def __init__(self, *, deny_action: str | None = None) -> None:
        self.deny_action = deny_action
        self.requests = []

    def require_authorized_action(self, request) -> None:
        self.requests.append(request)
        if request.action == self.deny_action:
            raise SecurityProductActionDenied("product action denied by Security")


def test_agent_admin_override_reauthorizes_through_shared_security_guard(monkeypatch) -> None:
    from zuno.api.services.agent import AgentService
    from zuno.api.services.security_admin_actions import configure_security_admin_action_guard
    from zuno.database.models.user import AdminUser

    async def fake_owner(agent_id: str):
        assert agent_id == "agent-1"
        return SimpleNamespace(user_id="owner-1")

    monkeypatch.setattr("zuno.api.services.agent.AgentDao.get_agent_user_id", fake_owner)
    guard = RecordingProductActionGuard()
    configure_security_admin_action_guard(guard)

    try:
        asyncio.run(AgentService.verify_user_permission("agent-1", AdminUser, action="delete"))
    finally:
        configure_security_admin_action_guard(None)

    assert [request.action for request in guard.requests] == ["admin.agent.delete"]
    assert guard.requests[0].resource_ref == "agent:agent-1"


def test_llm_admin_override_denial_blocks_before_permission_success(monkeypatch) -> None:
    from zuno.api.services.llm import LLMService
    from zuno.api.services.security_admin_actions import configure_security_admin_action_guard
    from zuno.database.models.user import AdminUser

    async def fake_owner(llm_id: str):
        assert llm_id == "llm-1"
        return SimpleNamespace(user_id="owner-1")

    monkeypatch.setattr("zuno.api.services.llm.LLMDao.get_user_id_by_llm", fake_owner)
    guard = RecordingProductActionGuard(deny_action="admin.llm.update")
    configure_security_admin_action_guard(guard)

    try:
        with pytest.raises(ValueError, match="product action denied by Security"):
            asyncio.run(LLMService.verify_user_permission("llm-1", AdminUser, action="update"))
    finally:
        configure_security_admin_action_guard(None)

    assert [request.action for request in guard.requests] == ["admin.llm.update"]


def test_tool_owner_update_does_not_require_admin_override_security_guard(monkeypatch) -> None:
    from zuno.api.services.security_admin_actions import configure_security_admin_action_guard
    from zuno.api.services.tool import ToolService

    async def fake_tool(tool_id: str):
        assert tool_id == "tool-1"
        return SimpleNamespace(user_id="owner-1")

    monkeypatch.setattr("zuno.api.services.tool.ToolDao.get_tool_by_id", fake_tool)
    guard = RecordingProductActionGuard()
    configure_security_admin_action_guard(guard)

    try:
        asyncio.run(ToolService.verify_user_permission("tool-1", "owner-1", action="update"))
    finally:
        configure_security_admin_action_guard(None)

    assert guard.requests == []


def test_mcp_agent_admin_delete_denial_blocks_dao_delete(monkeypatch) -> None:
    from zuno.api.services.mcp_agent import MCPAgentService
    from zuno.api.services.security_admin_actions import configure_security_admin_action_guard
    from zuno.database.models.user import AdminUser

    deleted = []

    monkeypatch.setattr(MCPAgentService, "get_agent_user_id", classmethod(lambda cls, agent_id: "owner-1"))
    monkeypatch.setattr(
        "zuno.api.services.mcp_agent.MCPAgentDao.delete_mcp_agent_by_id",
        lambda id: deleted.append(id),
    )
    guard = RecordingProductActionGuard(deny_action="admin.mcp_agent.delete")
    configure_security_admin_action_guard(guard)

    try:
        result = MCPAgentService.delete_mcp_agent_by_id("agent-1", AdminUser)
    finally:
        configure_security_admin_action_guard(None)

    assert result is None
    assert deleted == []
    assert [request.action for request in guard.requests] == ["admin.mcp_agent.delete"]


def test_knowledge_file_admin_status_reauthorizes_through_shared_security_guard(monkeypatch) -> None:
    from zuno.api.services.knowledge_file import KnowledgeFileService
    from zuno.api.services.security_admin_actions import configure_security_admin_action_guard
    from zuno.database.models.user import AdminUser

    async def fake_file(file_id: str):
        assert file_id == "kf-1"
        return SimpleNamespace(user_id="owner-1")

    monkeypatch.setattr(KnowledgeFileService, "select_knowledge_file_by_id", classmethod(lambda cls, file_id: fake_file(file_id)))
    guard = RecordingProductActionGuard()
    configure_security_admin_action_guard(guard)

    try:
        asyncio.run(KnowledgeFileService.verify_user_permission("kf-1", AdminUser, action="status"))
    finally:
        configure_security_admin_action_guard(None)

    assert [request.action for request in guard.requests] == ["admin.knowledge_file.status"]
    assert guard.requests[0].resource_ref == "knowledge-file:kf-1"
