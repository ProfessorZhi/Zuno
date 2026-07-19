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


def test_mcp_stdio_admin_delete_reauthorizes_through_security_guard(monkeypatch):
    from zuno.api.services.mcp_stdio_server import MCPServerService
    from zuno.database.models.user import AdminUser

    deleted = []

    monkeypatch.setattr(MCPServerService, "get_mcp_server_user", classmethod(lambda cls, server_id: "owner-1"))
    monkeypatch.setattr(
        "zuno.api.services.mcp_stdio_server.MCPServerStdioDao.delete_mcp_server",
        lambda server_id: deleted.append(server_id),
    )
    guard = RecordingProductActionGuard()
    MCPServerService.configure_security_product_action_guard(guard)

    try:
        MCPServerService.delete_mcp_server(AdminUser, "stdio-1")
    finally:
        MCPServerService.configure_security_product_action_guard(None)

    assert deleted == ["stdio-1"]
    assert [request.action for request in guard.requests] == ["admin.mcp_stdio.delete"]
    assert guard.requests[0].resource_ref == "mcp-stdio-server:stdio-1"


def test_mcp_stdio_admin_update_denial_blocks_dao_write(monkeypatch):
    from zuno.api.services.mcp_stdio_server import MCPServerService
    from zuno.database.models.user import AdminUser

    updated = []

    monkeypatch.setattr(MCPServerService, "get_mcp_server_user", classmethod(lambda cls, server_id: "owner-1"))
    monkeypatch.setattr(
        "zuno.api.services.mcp_stdio_server.MCPServerStdioDao.update_mcp_server",
        lambda *args: updated.append(args),
    )
    guard = RecordingProductActionGuard(deny_action="admin.mcp_stdio.update")
    MCPServerService.configure_security_product_action_guard(guard)

    try:
        with pytest.raises(ValueError, match="product action denied by Security"):
            MCPServerService.update_mcp_server(
                "stdio-1",
                "/tmp/server.py",
                "server",
                AdminUser,
                "python",
                "{}",
            )
    finally:
        MCPServerService.configure_security_product_action_guard(None)

    assert updated == []
    assert [request.action for request in guard.requests] == ["admin.mcp_stdio.update"]
