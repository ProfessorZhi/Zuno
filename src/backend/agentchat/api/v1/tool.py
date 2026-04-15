from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from agentchat.api.services.tool import ToolService
from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.database import ToolTable
from agentchat.schema.schemas import UnifiedResponseModel, resp_200, resp_500
from agentchat.schema.tool import CLIToolPreviewReq, ToolCreateReq, ToolDeleteReq, ToolUpdateReq
from agentchat.services.cli_tool_discovery import CliToolDiscoveryService
from agentchat.services.user_defined_tool_runtime import build_stored_tool_auth_config
from agentchat.settings import app_settings
from agentchat.tools.cli_tool.adapter import CLIToolAdapter
from agentchat.tools.openapi_tool.adapter import OpenAPIToolAdapter

router = APIRouter(tags=["Tool"], prefix="/tool")


def _validate_tool_request(req: ToolCreateReq | ToolUpdateReq) -> str:
    runtime_type = req.runtime_type or "remote_api"
    if runtime_type not in {"remote_api", "cli"}:
        raise ValueError("Unsupported runtime_type")

    if runtime_type == "cli":
        CLIToolAdapter.validate_cli_config(req.cli_config)
        return runtime_type

    if not req.openapi_schema:
        raise ValueError("OpenAPI tools require openapi_schema")
    OpenAPIToolAdapter.validate_openapi_schema(req.openapi_schema)
    return runtime_type


@router.post("/create", response_model=UnifiedResponseModel)
async def create_tool(
    *,
    req: ToolCreateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        runtime_type = _validate_tool_request(req)
        tool = ToolTable(
            name=f"user_tool_{uuid4().hex[:8]}",
            display_name=req.display_name,
            description=req.description,
            logo_url=req.logo_url,
            openapi_schema=req.openapi_schema if runtime_type == "remote_api" else None,
            auth_config=build_stored_tool_auth_config(
                runtime_type,
                req.auth_config,
                req.cli_config,
            ),
            user_id=login_user.user_id,
            is_user_defined=True,
        )
        result = await ToolService.create_user_defined_tool(tool)
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"create tool failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/all", summary="获取当前用户可见的所有工具")
async def get_all_tools(
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await ToolService.get_all_tools(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"get visible tools failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/user_defined", summary="获取用户自定义工具")
async def get_user_defined_tools(
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await ToolService.get_user_defined_tools(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"get user defined tools failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/delete", response_model=UnifiedResponseModel)
async def delete_user_defined_tool(
    req: ToolDeleteReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await ToolService.verify_user_permission(req.tool_id, login_user.user_id)
        await ToolService.delete_user_defined_tool(tool_id=req.tool_id)
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/cli_preview", summary="Preview a local CLI tool directory")
@router.post("/cli/preview", summary="Preview a local CLI tool directory")
async def preview_cli_tool_directory(
    req: CLIToolPreviewReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = CliToolDiscoveryService.preview_tool_directory(req.tool_dir)
        return resp_200(data=result.model_dump())
    except ValueError as err:
        logger.warning(f"preview cli tool rejected: {err}")
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        logger.error(f"preview cli tool failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/update", summary="修改用户自定义工具")
async def update_user_defined_tool(
    req: ToolUpdateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        runtime_type = _validate_tool_request(req)
        await ToolService.verify_user_permission(req.tool_id, login_user.user_id)
        await ToolService.update_user_defined_tool(
            tool_id=req.tool_id,
            update_values={
                "display_name": req.display_name,
                "description": req.description,
                "logo_url": req.logo_url,
                "openapi_schema": req.openapi_schema if runtime_type == "remote_api" else None,
                "auth_config": build_stored_tool_auth_config(
                    runtime_type,
                    req.auth_config,
                    req.cli_config,
                ),
            },
        )
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/default_logo", summary="获取工具默认头像")
async def get_default_tol_logo(
    login_user: UserPayload = Depends(get_login_user),
):
    return resp_200(data={"logo_url": app_settings.default_config.get("tool_logo_url")})
