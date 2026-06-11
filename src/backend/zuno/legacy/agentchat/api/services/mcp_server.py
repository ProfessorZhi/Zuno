from datetime import datetime, timedelta
from typing import Dict, Any

import pytz

from agentchat.api.services.mcp_user_config import MCPUserConfigService
from agentchat.database.dao.mcp_server import MCPServerDao
from agentchat.database.models.user import AdminUser, SystemUser
from agentchat.services.mcp.manager import MCPManager
from agentchat.utils.convert import convert_mcp_config
from agentchat.utils.helpers import parse_imported_config


class MCPService:
    @classmethod
    def ensure_tools_available(cls, server_name: str, tools_params: dict | None):
        tool_defs = (tools_params or {}).get(server_name) or []
        if not tool_defs:
            raise ValueError(f"MCP `{server_name}` 连接成功，但没有获取到可用工具。")
        return tool_defs

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
        results = await MCPServerDao.get_server_from_tool_name(tool_name)
        return results.to_dict()

    @classmethod
    async def delete_server_from_id(cls, mcp_server_id):
        return await MCPServerDao.delete_mcp_server(mcp_server_id)

    @classmethod
    async def verify_user_permission(cls, server_id, user_id, action: str = "update"):
        mcp_server = await MCPServerDao.get_mcp_server_from_id(server_id)
        if not mcp_server:
            raise ValueError("MCP 服务不存在。")

        is_admin = user_id == AdminUser
        is_owner = user_id == mcp_server.user_id
        is_system_server = mcp_server.user_id == SystemUser

        if action in ("view", "config", "test"):
            if is_system_server or is_owner or is_admin:
                return
        else:
            if is_system_server:
                if is_admin:
                    return
            elif is_owner or is_admin:
                return

        raise ValueError("没有权限访问该 MCP 服务。")

    @classmethod
    async def get_all_servers(cls, user_id):
        if user_id in (AdminUser, SystemUser):
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
            message = f"缺少必填配置：{', '.join(missing_fields)}"
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
            message = "连接成功，但没有获取到可用工具。"
            await MCPUserConfigService.update_test_status(
                server_id,
                user_id,
                success=False,
                message=message,
                tools=[],
            )
            return {"success": False, "message": message, "tools": []}

        message = f"测试成功，已获取 {len(tools)} 个工具。"
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
            raise ValueError("缺少字段：mcpServers")

        mcp_servers = payload["mcpServers"]
        if not isinstance(mcp_servers, dict):
            raise ValueError("mcpServers 必须是一个对象。")
        if not mcp_servers:
            raise ValueError("mcpServers 不能为空。")

        for server_name, server_conf in mcp_servers.items():
            if not isinstance(server_name, str) or not server_name.strip():
                raise ValueError(f"非法的 MCP 名称：{server_name}")
            if not isinstance(server_conf, dict):
                raise ValueError(f"MCP `{server_name}` 的配置必须是对象。")

            if "type" not in server_conf or not server_conf.get("type"):
                raise ValueError(f"MCP `{server_name}` 缺少必填字段：type")

            transport = server_conf.get("type")
            if transport in ("sse", "streamable_http", "websocket"):
                if "url" not in server_conf or not server_conf.get("url"):
                    raise ValueError(f"MCP `{server_name}` 缺少必填字段：url")
            elif transport == "stdio":
                if "command" not in server_conf or not server_conf.get("command"):
                    raise ValueError(f"MCP `{server_name}` 缺少必填字段：command")
                if "args" not in server_conf or not isinstance(server_conf.get("args"), list):
                    raise ValueError(f"MCP `{server_name}` 缺少必填字段：args（必须为数组）")
            else:
                raise ValueError(f"MCP `{server_name}` 不支持该 transport：{transport}")

            if "headers" in server_conf and not isinstance(server_conf["headers"], dict):
                raise ValueError(f"MCP `{server_name}` 的 headers 必须是对象。")
            if "env" in server_conf and server_conf["env"] is not None and not isinstance(server_conf["env"], dict):
                raise ValueError(f"MCP `{server_name}` 的 env 必须是对象。")
            if "env_passthrough" in server_conf and server_conf["env_passthrough"] is not None:
                if not isinstance(server_conf["env_passthrough"], list):
                    raise ValueError(f"MCP `{server_name}` 的 env_passthrough 必须是数组。")
