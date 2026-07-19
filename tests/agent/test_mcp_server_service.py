import asyncio
from types import SimpleNamespace

import pytest
from zuno.platform.security import SecurityProductActionDenied


class RecordingProductActionGuard:
    def __init__(self, deny_action: str | None = None) -> None:
        self.deny_action = deny_action
        self.requests = []

    def require_authorized_action(self, request):
        self.requests.append(request)
        if request.action == self.deny_action:
            raise SecurityProductActionDenied("product action denied by Security")


def test_ensure_tools_available_returns_server_tools():
    from zuno.api.services.mcp_server import MCPService

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
    from zuno.api.services.mcp_server import MCPService

    with pytest.raises(ValueError, match="no tools were discovered"):
        MCPService.ensure_tools_available("qa-server", {"qa-server": []})


def test_get_mcp_tools_info_tolerates_null_params(monkeypatch):
    from zuno.api.services.mcp_server import MCPService

    class FakeServer:
        def to_dict(self):
            return {"params": None}

    async def fake_get_server(server_id):
        assert server_id == "server-1"
        return FakeServer()

    monkeypatch.setattr(
        "zuno.api.services.mcp_server.MCPServerDao.get_mcp_server_from_id",
        fake_get_server,
    )

    result = asyncio.run(MCPService.get_mcp_tools_info("server-1"))

    assert result == []


def test_mcp_admin_override_reauthorizes_through_security_guard(monkeypatch):
    from zuno.api.services.mcp_server import MCPService
    from zuno.database.models.user import AdminUser

    class FakeServer:
        user_id = "ordinary-owner"

    async def fake_get_server(server_id):
        assert server_id == "server-1"
        return FakeServer()

    monkeypatch.setattr(
        "zuno.api.services.mcp_server.MCPServerDao.get_mcp_server_from_id",
        fake_get_server,
    )
    guard = RecordingProductActionGuard()
    MCPService.configure_security_product_action_guard(guard)

    try:
        asyncio.run(MCPService.verify_user_permission("server-1", AdminUser, action="delete"))
    finally:
        MCPService.configure_security_product_action_guard(None)

    assert [request.action for request in guard.requests] == ["admin.mcp.delete"]
    assert guard.requests[0].principal_id == AdminUser
    assert guard.requests[0].resource_ref == "mcp-server:server-1"


def test_mcp_admin_override_denial_blocks_before_permission_success(monkeypatch):
    from zuno.api.services.mcp_server import MCPService
    from zuno.database.models.user import AdminUser

    async def fake_get_server(server_id):
        return SimpleNamespace(user_id="ordinary-owner")

    monkeypatch.setattr(
        "zuno.api.services.mcp_server.MCPServerDao.get_mcp_server_from_id",
        fake_get_server,
    )
    guard = RecordingProductActionGuard(deny_action="admin.mcp.update")
    MCPService.configure_security_product_action_guard(guard)

    try:
        with pytest.raises(ValueError, match="product action denied by Security"):
            asyncio.run(MCPService.verify_user_permission("server-1", AdminUser, action="update"))
    finally:
        MCPService.configure_security_product_action_guard(None)

    assert [request.action for request in guard.requests] == ["admin.mcp.update"]


def test_mcp_owner_update_does_not_require_admin_override_security_guard(monkeypatch):
    from zuno.api.services.mcp_server import MCPService

    async def fake_get_server(server_id):
        return SimpleNamespace(user_id="owner-1")

    monkeypatch.setattr(
        "zuno.api.services.mcp_server.MCPServerDao.get_mcp_server_from_id",
        fake_get_server,
    )
    guard = RecordingProductActionGuard()
    MCPService.configure_security_product_action_guard(guard)

    try:
        asyncio.run(MCPService.verify_user_permission("server-1", "owner-1", action="update"))
    finally:
        MCPService.configure_security_product_action_guard(None)

    assert guard.requests == []
