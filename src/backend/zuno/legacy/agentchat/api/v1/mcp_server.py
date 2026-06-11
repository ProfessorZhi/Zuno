import json

from fastapi import APIRouter, Body, Depends, Query
from loguru import logger

from agentchat.api.services.mcp_server import MCPService
from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.core.agents.structured_response_agent import StructuredResponseAgent
from agentchat.prompts.mcp import McpAsToolPrompt
from agentchat.schema.mcp import MCPResponseFormat, MCPServerImportedReq, MCPServerUpdateReq
from agentchat.schema.schemas import resp_200, resp_500
from agentchat.services.mcp.manager import MCPManager
from agentchat.settings import app_settings
from agentchat.utils.convert import convert_mcp_config
from agentchat.utils.helpers import parse_imported_config

router = APIRouter(tags=["MCP-Server"])


def _build_mcp_summary(server_name: str, tools_params: dict) -> MCPResponseFormat:
    tool_defs = tools_params.get(server_name) or []
    tool_names = [tool.get("name", "") for tool in tool_defs if tool.get("name")]
    preview = "、".join(tool_names[:3]) if tool_names else "MCP tool"
    description = (
        f"{server_name} MCP 服务，当前提供 {len(tool_defs)} 个工具。优先可用工具：{preview}。"
        if tool_defs
        else f"{server_name} MCP 服务。"
    )
    return MCPResponseFormat(
        mcp_as_tool_name=server_name,
        description=description,
    )


@router.post("/mcp_server")
async def create_mcp_server(
    req: MCPServerImportedReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        MCPService.validate_imported_config(req.imported_config)
        name, info = next(iter(req.imported_config.get("mcpServers", {}).items()))
        server_name = req.server_name or name
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

        mcp_manager = MCPManager([convert_mcp_config(server_info)])
        tools_params = await mcp_manager.show_mcp_tools()
        tool_defs = MCPService.ensure_tools_available(server_name, tools_params)
        tool_names = [tool["name"] for tool in tool_defs]

        try:
            structured_agent = StructuredResponseAgent(MCPResponseFormat)
            structured_response = structured_agent.get_structured_response(
                McpAsToolPrompt.format(tools_info=json.dumps(tools_params, indent=4, ensure_ascii=False))
            )
        except Exception as err:
            logger.warning(f"build MCP summary via LLM failed, fallback to deterministic summary: {err}")
            structured_response = _build_mcp_summary(server_name, tools_params)

        await MCPService.create_mcp_server(
            tools=tool_names,
            url=info.get("url") or "",
            config={},
            type=info.get("type", "sse"),
            user_id=login_user.user_id,
            server_name=server_name,
            config_enabled=False,
            logo_url=req.logo_url,
            params=tools_params.get(server_name),
            user_name=login_user.user_name,
            description=structured_response.description,
            mcp_as_tool_name=structured_response.mcp_as_tool_name,
            imported_config=req.imported_config,
        )
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/mcp_server")
async def get_mcp_servers(login_user: UserPayload = Depends(get_login_user)):
    try:
        mcp_servers = await MCPService.get_all_servers(login_user.user_id)
        return resp_200(data=mcp_servers)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.delete("/mcp_server")
async def delete_mcp_server(
    server_id: str = Body(..., embed=True, description="MCP Server 的 ID"),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await MCPService.verify_user_permission(server_id, login_user.user_id, action="delete")
        await MCPService.delete_server_from_id(server_id)
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/mcp_tools")
async def get_mcp_tools(
    server_id: str = Query(..., description="MCP Server 的 ID"),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await MCPService.verify_user_permission(server_id, login_user.user_id, action="view")
        results = await MCPService.get_mcp_tools_info(server_id)
        return resp_200(data=results)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.put("/mcp_server")
async def update_mcp_server(
    req: MCPServerUpdateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await MCPService.verify_user_permission(req.server_id, login_user.user_id, action="update")
        mcp_server = await MCPService.get_mcp_server_from_id(req.server_id)
        update_data = {}

        if req.imported_config and req.imported_config != mcp_server["imported_config"]:
            imported_info = parse_imported_config(req.imported_config)
            imported_info.name = req.name or imported_info.name

            update_data.update(
                {
                    "server_name": imported_info.name,
                    "url": imported_info.url or "",
                    "type": imported_info.type,
                    "imported_config": req.imported_config,
                    "logo_url": req.logo_url,
                }
            )

            mcp_manager = MCPManager(
                [
                    convert_mcp_config(
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
                ]
            )
            tools_params = await mcp_manager.show_mcp_tools()
            tool_defs = MCPService.ensure_tools_available(imported_info.name, tools_params)
            update_data["tools"] = [tool["name"] for tool in tool_defs]
            update_data["params"] = tool_defs

            try:
                structured_agent = StructuredResponseAgent(MCPResponseFormat)
                structured_response = structured_agent.get_structured_response(
                    McpAsToolPrompt.format(tools_info=json.dumps(tools_params, indent=4, ensure_ascii=False))
                )
            except Exception as err:
                logger.warning(f"build MCP summary via LLM failed, fallback to deterministic summary: {err}")
                structured_response = _build_mcp_summary(imported_info.name, tools_params)
            update_data["mcp_as_tool_name"] = structured_response.mcp_as_tool_name
            update_data["description"] = structured_response.description
        else:
            if req.name is not None:
                update_data["server_name"] = req.name
            if req.logo_url is not None:
                update_data["logo_url"] = req.logo_url

        await MCPService.update_mcp_server(server_id=req.server_id, update_data=update_data)
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/mcp_server/logo", summary="获取 MCP 服务默认图标")
async def get_mcp_default_logo(login_user: UserPayload = Depends(get_login_user)):
    return resp_200({"logo_url": app_settings.default_config.get("mcp_logo_url")})
