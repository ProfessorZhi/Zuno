from fastapi import APIRouter, Body, Depends, Query
from loguru import logger

from zuno.api.services.mcp_server import MCPService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.mcp import MCPServerImportedReq, MCPServerUpdateReq
from zuno.schema.schemas import resp_200, resp_500
from zuno.settings import app_settings

router = APIRouter(tags=["MCP-Server"])


@router.post("/mcp_server")
async def create_mcp_server(
    req: MCPServerImportedReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        create_payload = await MCPService.prepare_imported_server_create_payload(
            imported_config=req.imported_config,
            requested_server_name=req.server_name,
            logo_url=req.logo_url,
            user_id=login_user.user_id,
            user_name=login_user.user_name,
        )
        await MCPService.create_mcp_server(**create_payload)
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
    server_id: str = Body(..., embed=True, description="MCP server id"),
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
    server_id: str = Query(..., description="MCP server id"),
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
            update_data = await MCPService.prepare_imported_server_update_data(
                imported_config=req.imported_config,
                requested_name=req.name,
                logo_url=req.logo_url,
            )
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


@router.get("/mcp_server/logo", summary="Get default MCP logo")
async def get_mcp_default_logo(login_user: UserPayload = Depends(get_login_user)):
    _ = login_user
    return resp_200({"logo_url": app_settings.default_config.get("mcp_logo_url")})
