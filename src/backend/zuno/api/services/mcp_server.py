import json
from datetime import datetime, timedelta
from typing import Any, Dict

import pytz
from loguru import logger

from zuno.api.services.mcp_user_config import MCPUserConfigService
from zuno.core.agents.structured_response_agent import StructuredResponseAgent
from zuno.database.dao.mcp_server import MCPServerDao
from zuno.database.models.user import AdminUser, SystemUser
from zuno.resources.prompts.mcp import McpAsToolPrompt
from zuno.schema.mcp import MCPResponseFormat
from zuno.services.mcp.manager import MCPManager
from zuno.platform.security import (
    SecurityProductActionDenied,
    SecurityProductActionGuard,
    SecurityProductActionRequest,
    build_product_action_hash,
)
from zuno.utils.convert import convert_mcp_config
from zuno.utils.helpers import parse_imported_config

ADMIN_MCP_ACTIONS = {
    "config": "admin.mcp.config",
    "create": "admin.mcp.create",
    "delete": "admin.mcp.delete",
    "list": "admin.mcp.list",
    "test": "admin.mcp.test",
    "update": "admin.mcp.update",
    "view": "admin.mcp.view",
}


class MCPService:
    _security_product_action_guard: SecurityProductActionGuard | None = None

    @classmethod
    def configure_security_product_action_guard(
        cls,
        guard: SecurityProductActionGuard | None,
    ) -> None:
        cls._security_product_action_guard = guard

    @staticmethod
    def build_mcp_summary(server_name: str, tools_params: dict) -> MCPResponseFormat:
        tool_defs = tools_params.get(server_name) or []
        tool_names = [tool.get("name", "") for tool in tool_defs if tool.get("name")]
        preview = ", ".join(tool_names[:3]) if tool_names else "MCP tool"
        description = (
            f"{server_name} MCP service with {len(tool_defs)} discovered tools. Primary tools: {preview}."
            if tool_defs
            else f"{server_name} MCP service."
        )
        return MCPResponseFormat(
            mcp_as_tool_name=server_name,
            description=description,
        )

    @classmethod
    def summarize_mcp_tools(cls, server_name: str, tools_params: dict) -> MCPResponseFormat:
        try:
            structured_agent = StructuredResponseAgent(MCPResponseFormat)
            return structured_agent.get_structured_response(
                McpAsToolPrompt.format(tools_info=json.dumps(tools_params, indent=4, ensure_ascii=False))
            )
        except Exception as err:
            logger.warning(f"build MCP summary via LLM failed, fallback to deterministic summary: {err}")
            return cls.build_mcp_summary(server_name, tools_params)

    @classmethod
    async def discover_tools_from_imported_server(cls, server_info: dict) -> dict:
        mcp_manager = MCPManager([convert_mcp_config(server_info)])
        return await mcp_manager.show_mcp_tools()

    @classmethod
    def ensure_tools_available(cls, server_name: str, tools_params: dict | None):
        tool_defs = (tools_params or {}).get(server_name) or []
        if not tool_defs:
            raise ValueError(f"MCP `{server_name}` connected, but no tools were discovered.")
        return tool_defs

    @classmethod
    async def prepare_imported_server_create_payload(
        cls,
        *,
        imported_config: dict,
        requested_server_name: str | None,
        logo_url: str,
        user_id: str,
        user_name: str,
    ) -> dict:
        cls.validate_imported_config(imported_config)
        name, info = next(iter(imported_config.get("mcpServers", {}).items()))
        server_name = requested_server_name or name
        server_info = {
            "server_name": server_name,
            "type": info.get("type", "sse"),
            "headers": info.get("headers"),
            "url": info.get("url"),
            "command": info.get("command"),
            "args": info.get("args"),
            "env": info.get("env"),
            "env_passthrough": info.get("env_passthrough"),
            "cwd": info.get("cwd"),
        }

        tools_params = await cls.discover_tools_from_imported_server(server_info)
        tool_defs = cls.ensure_tools_available(server_name, tools_params)
        structured_response = cls.summarize_mcp_tools(server_name, tools_params)
        return {
            "tools": [tool["name"] for tool in tool_defs],
            "url": info.get("url") or "",
            "config": {},
            "type": info.get("type", "sse"),
            "user_id": user_id,
            "server_name": server_name,
            "config_enabled": False,
            "logo_url": logo_url,
            "params": tools_params.get(server_name),
            "user_name": user_name,
            "description": structured_response.description,
            "mcp_as_tool_name": structured_response.mcp_as_tool_name,
            "imported_config": imported_config,
        }

    @classmethod
    async def prepare_imported_server_update_data(
        cls,
        *,
        imported_config: dict,
        requested_name: str | None,
        logo_url: str | None,
    ) -> dict:
        imported_info = parse_imported_config(imported_config)
        imported_info.name = requested_name or imported_info.name
        update_data = {
            "server_name": imported_info.name,
            "url": imported_info.url or "",
            "type": imported_info.type,
            "imported_config": imported_config,
            "logo_url": logo_url,
        }
        tools_params = await cls.discover_tools_from_imported_server(
            {
                "server_name": imported_info.name,
                "type": imported_info.type,
                "url": imported_info.url,
                "headers": imported_info.headers,
                "command": imported_info.command,
                "args": imported_info.args,
                "env": imported_info.env,
                "env_passthrough": imported_info.env_passthrough,
                "cwd": imported_info.cwd,
            }
        )
        tool_defs = cls.ensure_tools_available(imported_info.name, tools_params)
        structured_response = cls.summarize_mcp_tools(imported_info.name, tools_params)
        update_data["tools"] = [tool["name"] for tool in tool_defs]
        update_data["params"] = tool_defs
        update_data["mcp_as_tool_name"] = structured_response.mcp_as_tool_name
        update_data["description"] = structured_response.description
        return update_data

    @classmethod
    async def create_mcp_server(
        cls,
        url: str,
        type: str,
        tools: list,
        params: dict,
        server_name: str,
        user_id: str,
        user_name: str,
        logo_url: str,
        mcp_as_tool_name: str,
        description: str,
        config: dict = None,
        imported_config: dict = None,
        config_enabled: bool = False,
    ):
        if user_id == AdminUser:
            cls._require_admin_action_authorized(
                principal_id=user_id,
                action=ADMIN_MCP_ACTIONS["create"],
                resource_ref=f"mcp-server:{server_name}",
            )
        return await MCPServerDao.create_mcp_server(
            url=url,
            type=type,
            config=config,
            tools=tools,
            params=params,
            server_name=server_name,
            user_id=user_id,
            user_name=user_name,
            mcp_as_tool_name=mcp_as_tool_name,
            description=description,
            config_enabled=config_enabled,
            logo_url=logo_url,
            imported_config=imported_config,
        )

    @classmethod
    async def get_mcp_server_from_id(cls, mcp_server_id):
        result = await MCPServerDao.get_mcp_server_from_id(mcp_server_id)
        return result.to_dict() if result else None

    @classmethod
    async def update_mcp_server(cls, server_id: str, update_data: dict):
        if not update_data:
            return
        return await MCPServerDao.update_mcp_server(mcp_server_id=server_id, update_data=update_data)

    @classmethod
    async def get_server_from_tool_name(cls, tool_name):
        result = await MCPServerDao.get_server_from_tool_name(tool_name)
        return result.to_dict() if result else None

    @classmethod
    async def delete_server_from_id(cls, mcp_server_id):
        return await MCPServerDao.delete_mcp_server(mcp_server_id)

    @classmethod
    async def verify_user_permission(cls, server_id, user_id, action: str = "update"):
        mcp_server = await MCPServerDao.get_mcp_server_from_id(server_id)
        if not mcp_server:
            raise ValueError("MCP server does not exist.")

        is_admin = user_id == AdminUser
        is_owner = user_id == mcp_server.user_id
        is_system_server = mcp_server.user_id == SystemUser

        if action in ("view", "config", "test"):
            if is_system_server or is_owner or is_admin:
                if is_admin and not is_owner:
                    cls._require_admin_action_authorized(
                        principal_id=user_id,
                        action=ADMIN_MCP_ACTIONS[action],
                        resource_ref=f"mcp-server:{server_id}",
                    )
                return
        else:
            if is_system_server:
                if is_admin:
                    cls._require_admin_action_authorized(
                        principal_id=user_id,
                        action=ADMIN_MCP_ACTIONS[action],
                        resource_ref=f"mcp-server:{server_id}",
                    )
                    return
            elif is_owner or is_admin:
                if is_admin and not is_owner:
                    cls._require_admin_action_authorized(
                        principal_id=user_id,
                        action=ADMIN_MCP_ACTIONS[action],
                        resource_ref=f"mcp-server:{server_id}",
                    )
                return

        raise ValueError("No permission to access this MCP server.")

    @classmethod
    async def get_all_servers(cls, user_id):
        if user_id in (AdminUser, SystemUser):
            if user_id == AdminUser:
                cls._require_admin_action_authorized(
                    principal_id=user_id,
                    action=ADMIN_MCP_ACTIONS["list"],
                    resource_ref="mcp-server:*",
                )
            all_servers = await MCPServerDao.get_all_mcp_servers()
        else:
            personal_servers = await MCPServerDao.get_mcp_servers_from_user(user_id)
            admin_servers = await MCPServerDao.get_mcp_servers_from_user(SystemUser)
            all_servers = personal_servers + admin_servers

        all_servers = [server.to_dict() for server in all_servers]
        for server in all_servers:
            user_config = await MCPUserConfigService.show_mcp_user_config(user_id, server["mcp_server_id"])
            if user_config.get("config"):
                server["config"] = user_config.get("config")
            server["test_status"] = user_config.get("test_status")
        return all_servers

    @classmethod
    async def test_user_config(cls, server_id: str, user_id: str):
        server = await cls.get_mcp_server_from_id(server_id)
        user_config = await MCPUserConfigService.show_mcp_user_config(user_id, server_id)
        public_config = user_config.get("config") or []
        config_map = {item.get("key"): item.get("value") for item in public_config if item.get("key")}

        required_items = server.get("config") or []
        missing_fields = []
        for item in required_items:
            key = item.get("key")
            if key and not config_map.get(key):
                missing_fields.append(item.get("label") or key)

        if missing_fields:
            message = f"Missing required config: {', '.join(missing_fields)}"
            await MCPUserConfigService.update_test_status(
                server_id,
                user_id,
                success=False,
                message=message,
                tools=[],
            )
            return {"success": False, "message": message, "tools": []}

        headers = None
        imported_info = None
        imported_config = server.get("imported_config") or {}
        if imported_config:
            imported_info = parse_imported_config(imported_config)
            headers = imported_info.headers

        mcp_manager = MCPManager(
            [
                convert_mcp_config(
                    {
                        "server_name": server.get("server_name"),
                        "type": server.get("type"),
                        "url": server.get("url"),
                        "headers": headers,
                        "command": imported_info.command if imported_info else None,
                        "args": imported_info.args if imported_info else None,
                        "env": imported_info.env if imported_info else None,
                        "env_passthrough": imported_info.env_passthrough if imported_info else None,
                        "cwd": imported_info.cwd if imported_info else None,
                    }
                )
            ]
        )

        tools_params = await mcp_manager.show_mcp_tools()
        tools = [tool["name"] for tool in tools_params.get(server.get("server_name"), [])]
        if not tools:
            message = "Connected successfully, but no tools were discovered."
            await MCPUserConfigService.update_test_status(
                server_id,
                user_id,
                success=False,
                message=message,
                tools=[],
            )
            return {"success": False, "message": message, "tools": []}

        message = f"Test passed, discovered {len(tools)} tools."
        await MCPUserConfigService.update_test_status(
            server_id,
            user_id,
            success=True,
            message=message,
            tools=tools,
        )
        return {"success": True, "message": message, "tools": tools}

    @classmethod
    async def mcp_server_need_update(cls):
        server = await MCPServerDao.get_first_mcp_server()
        current_time = datetime.now(pytz.timezone("Asia/Shanghai"))
        time_difference = current_time - server.update_time.replace(tzinfo=pytz.timezone("Asia/Shanghai"))
        return time_difference > timedelta(days=7)

    @classmethod
    async def get_mcp_tools_info(cls, server_id):
        server = await MCPServerDao.get_mcp_server_from_id(server_id)
        server = server.to_dict()
        tools_info = []
        for param in server.get("params") or []:
            tool_schema = []
            properties = param["input_schema"]["properties"]
            required = param["input_schema"].get("required", [])
            for param_key, param_value in properties.items():
                tool_schema.append(
                    {
                        "name": param_key,
                        "description": param_value.get("description", ""),
                        "type": param_value.get("type"),
                        "required": param_key in required,
                    }
                )

            tools_info.append(
                {
                    "tool_name": param["name"],
                    "tool_description": param.get("description", ""),
                    "tool_schema": tool_schema,
                }
            )
        return tools_info

    @classmethod
    async def get_mcp_server_ids_from_name(cls, mcp_servers_name, user_id):
        mcp_servers = await MCPServerDao.get_mcp_server_ids_from_name(mcp_servers_name, user_id)
        mcp_servers.extend(await MCPServerDao.get_mcp_server_ids_from_name(mcp_servers_name, SystemUser))
        return [mcp_server.mcp_server_id for mcp_server in mcp_servers]

    @classmethod
    def validate_imported_config(cls, payload: Dict[str, Any]):
        if "mcpServers" not in payload:
            raise ValueError("Missing field: mcpServers")

        mcp_servers = payload["mcpServers"]
        if not isinstance(mcp_servers, dict):
            raise ValueError("mcpServers must be an object.")
        if not mcp_servers:
            raise ValueError("mcpServers cannot be empty.")

        for server_name, server_conf in mcp_servers.items():
            if not isinstance(server_name, str) or not server_name.strip():
                raise ValueError(f"Invalid MCP server name: {server_name}")
            if not isinstance(server_conf, dict):
                raise ValueError(f"MCP `{server_name}` config must be an object.")

            if "type" not in server_conf or not server_conf.get("type"):
                raise ValueError(f"MCP `{server_name}` is missing required field: type")

            transport = server_conf.get("type")
            if transport in ("sse", "streamable_http", "websocket"):
                if "url" not in server_conf or not server_conf.get("url"):
                    raise ValueError(f"MCP `{server_name}` is missing required field: url")
            elif transport == "stdio":
                if "command" not in server_conf or not server_conf.get("command"):
                    raise ValueError(f"MCP `{server_name}` is missing required field: command")
                if "args" not in server_conf or not isinstance(server_conf.get("args"), list):
                    raise ValueError(f"MCP `{server_name}` is missing required field: args (must be a list)")
            else:
                raise ValueError(f"MCP `{server_name}` uses unsupported transport: {transport}")

            if "headers" in server_conf and not isinstance(server_conf["headers"], dict):
                raise ValueError(f"MCP `{server_name}` headers must be an object.")
            if "env" in server_conf and server_conf["env"] is not None and not isinstance(server_conf["env"], dict):
                raise ValueError(f"MCP `{server_name}` env must be an object.")
            if "env_passthrough" in server_conf and server_conf["env_passthrough"] is not None:
                if not isinstance(server_conf["env_passthrough"], list):
                    raise ValueError(f"MCP `{server_name}` env_passthrough must be a list.")

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


__all__ = ["MCPService"]
