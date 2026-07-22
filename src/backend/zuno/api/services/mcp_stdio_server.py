from loguru import logger

from zuno.database.dao.mcp_stdio_server import MCPServerStdioDao
from zuno.database.models.user import AdminUser
from zuno.platform.security import (
    SecurityProductActionDenied,
    SecurityProductActionGuard,
    SecurityProductActionRequest,
    build_product_action_hash,
)


class MCPServerService:
    _security_product_action_guard: SecurityProductActionGuard | None = None

    @classmethod
    def configure_security_product_action_guard(
        cls,
        guard: SecurityProductActionGuard | None,
    ) -> None:
        cls._security_product_action_guard = guard

    @classmethod
    def create_mcp_server(
        cls,
        name: str,
        mcp_server_path: str,
        user_id: str,
        mcp_server_command: str,
        mcp_server_env: str,
    ):
        if user_id == AdminUser:
            cls._require_admin_action_authorized(
                principal_id=user_id,
                action="admin.mcp_stdio.create",
                resource_ref=f"mcp-stdio-server:{name}",
            )
        return MCPServerStdioDao.create_mcp_server(
            mcp_server_path,
            mcp_server_command,
            user_id,
            name,
            mcp_server_env,
        )

    @classmethod
    def get_mcp_servers(cls, user_id: str):
        return list(MCPServerStdioDao.get_mcp_servers(user_id))

    @classmethod
    def delete_mcp_server(cls, user_id: str, mcp_server_id: str):
        mcp_server_user = cls.get_mcp_server_user(mcp_server_id)
        if user_id in (mcp_server_user, AdminUser):
            if user_id == AdminUser:
                cls._require_admin_action_authorized(
                    principal_id=user_id,
                    action="admin.mcp_stdio.delete",
                    resource_ref=f"mcp-stdio-server:{mcp_server_id}",
                )
            return MCPServerStdioDao.delete_mcp_server(mcp_server_id)
        logger.error("No Permission Exec Delete MCP Server")
        raise ValueError("No Permission Exec Delete MCP Server")

    @classmethod
    def update_mcp_server(
        cls,
        mcp_server_id: str,
        mcp_server_path: str,
        name: str,
        user_id: str,
        mcp_server_command: str,
        mcp_server_env: str,
    ):
        mcp_server_user = cls.get_mcp_server_user(mcp_server_id)
        if user_id in (mcp_server_user, AdminUser):
            if user_id == AdminUser:
                cls._require_admin_action_authorized(
                    principal_id=user_id,
                    action="admin.mcp_stdio.update",
                    resource_ref=f"mcp-stdio-server:{mcp_server_id}",
                )
            return MCPServerStdioDao.update_mcp_server(
                mcp_server_id,
                mcp_server_path,
                mcp_server_command,
                name,
                mcp_server_env,
            )
        logger.error("No Permission Exec Update MCP Server")
        raise ValueError("No Permission Exec Update MCP Server")

    @classmethod
    def get_mcp_server_user(cls, mcp_server_id: str):
        mcp_server = MCPServerStdioDao.get_mcp_server_by_id(mcp_server_id)
        return mcp_server.user_id

    @classmethod
    def get_mcp_server_from_id(cls, server_id: str):
        mcp_server = MCPServerStdioDao.get_mcp_server_by_id(server_id)
        return mcp_server.to_dict()

    @classmethod
    def _require_admin_action_authorized(
        cls,
        *,
        principal_id: str,
        action: str,
        resource_ref: str,
    ) -> None:
        if cls._security_product_action_guard is None:
            return
        tenant_id = "system"
        workspace_id = "system"
        request = SecurityProductActionRequest(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=principal_id,
            action=action,
            resource_ref=resource_ref,
            decision_id=f"authorization-decision:{action}:{principal_id}:{resource_ref}",
            prepared_action_hash=build_product_action_hash(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                principal_id=principal_id,
                action=action,
                resource_ref=resource_ref,
            ),
        )
        try:
            cls._security_product_action_guard.require_authorized_action(request)
        except SecurityProductActionDenied as exc:
            raise ValueError(str(exc) or "Security authorization denied") from exc


__all__ = ["MCPServerService"]
