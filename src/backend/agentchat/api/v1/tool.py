from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from agentchat.api.services.tool import ToolService
from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.schema.schemas import UnifiedResponseModel, resp_200, resp_500
from agentchat.schema.tool import (
    CLIToolPreviewReq,
    RemoteApiAssistReq,
    ToolConnectivityReq,
    ToolCreateReq,
    ToolDeleteReq,
    ToolUpdateReq,
)
from agentchat.services.cli_tool_discovery import CliToolDiscoveryService
from agentchat.services.simple_api_tool import build_openapi_schema_from_simple_config, build_remote_api_assist_draft_agentic
from agentchat.services.tool_connectivity_service import ToolConnectivityService
from agentchat.services.tool_creation_service import ToolCreationService
from agentchat.services.user_defined_tool_runtime import build_stored_tool_auth_config
from agentchat.settings import app_settings
from agentchat.tools.cli_tool.adapter import CLIToolAdapter
from agentchat.tools.openapi_tool.adapter import OpenAPIToolAdapter

router = APIRouter(tags=["Tool"], prefix="/tool")


def _validate_tool_request(req: ToolCreateReq | ToolUpdateReq) -> tuple[str, dict | None]:
    runtime_type = req.runtime_type or "remote_api"
    if runtime_type not in {"remote_api", "cli"}:
        raise ValueError("Unsupported runtime_type")

    if runtime_type == "cli":
        CLIToolAdapter.validate_cli_config(req.cli_config)
        return runtime_type, None

    resolved_schema = req.openapi_schema
    if req.simple_api_config:
        resolved_schema = build_openapi_schema_from_simple_config(req.simple_api_config)

    if not resolved_schema:
        raise ValueError("OpenAPI tools require openapi_schema or simple_api_config")
    OpenAPIToolAdapter.validate_openapi_schema(resolved_schema)
    return runtime_type, resolved_schema


@router.post("/create", response_model=UnifiedResponseModel)
async def create_tool(
    *,
    req: ToolCreateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await ToolCreationService.create_user_defined_tool(
            display_name=req.display_name,
            description=req.description,
            logo_url=req.logo_url,
            runtime_type=req.runtime_type or "remote_api",
            user_id=login_user.user_id,
            auth_config=req.auth_config,
            cli_config=req.cli_config,
            openapi_schema=req.openapi_schema,
            simple_api_config=req.simple_api_config,
            source_metadata=req.source_metadata,
        )
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"create tool failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/all", summary="Get all tools visible to the current user")
async def get_all_tools(
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await ToolService.get_all_tools(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"get visible tools failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/user_defined", summary="Get custom tools created by the current user")
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
        result = CliToolDiscoveryService.preview(req)
        return resp_200(data=result.model_dump())
    except ValueError as err:
        logger.warning(f"preview cli tool rejected: {err}")
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        logger.error(f"preview cli tool failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/remote_api/assist", summary="Build a simple remote API draft from URL or curl")
async def assist_remote_api_tool(
    req: RemoteApiAssistReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await build_remote_api_assist_draft_agentic(req)
        return resp_200(data=result.model_dump(by_alias=True))
    except ValueError as err:
        logger.warning(f"remote api assist rejected: {err}")
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        logger.error(f"remote api assist failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/test_connectivity", summary="Test connectivity for the current tool draft")
async def test_tool_connectivity(
    req: ToolConnectivityReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await ToolConnectivityService.test(req)
        return resp_200(data=result.model_dump())
    except ValueError as err:
        logger.warning(f"tool connectivity rejected: {err}")
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        logger.error(f"tool connectivity failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/system/{tool_name}/test_connectivity", summary="Test connectivity for a system tool")
async def test_system_tool_connectivity(
    tool_name: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await ToolConnectivityService.test_system_tool(tool_name)
        return resp_200(data={
            **result.model_dump(),
            "status": ToolConnectivityService.to_runtime_status(result),
        })
    except ValueError as err:
        logger.warning(f"system tool connectivity rejected: {err}")
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        logger.error(f"system tool connectivity failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/{tool_id}/test_connectivity", summary="Test connectivity for a saved user defined tool")
async def test_saved_tool_connectivity(
    tool_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await ToolService.verify_user_permission(tool_id, login_user.user_id)
        tool = await ToolService.get_tool_by_id(tool_id)
        if not tool or not tool.is_user_defined:
            raise ValueError("Only user defined tools support saved connectivity checks")
        result = await ToolConnectivityService.test_saved_tool(tool)
        return resp_200(data={
            **result.model_dump(),
            "status": ToolConnectivityService.to_runtime_status(result),
        })
    except ValueError as err:
        logger.warning(f"saved tool connectivity rejected: {err}")
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        logger.error(f"saved tool connectivity failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/update", summary="Update a user defined tool")
async def update_user_defined_tool(
    req: ToolUpdateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        runtime_type, resolved_schema = _validate_tool_request(req)
        await ToolService.verify_user_permission(req.tool_id, login_user.user_id)
        await ToolService.update_user_defined_tool(
            tool_id=req.tool_id,
            update_values={
                "display_name": req.display_name,
                "description": req.description,
                "logo_url": req.logo_url,
                "openapi_schema": resolved_schema if runtime_type == "remote_api" else None,
                "auth_config": build_stored_tool_auth_config(
                    runtime_type,
                    req.auth_config,
                    req.cli_config,
                    req.simple_api_config.model_dump(by_alias=True) if req.simple_api_config else None,
                    req.source_metadata,
                ),
            },
        )
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/default_logo", summary="Get default tool logo")
async def get_default_tol_logo(
    login_user: UserPayload = Depends(get_login_user),
):
    return resp_200(data={"logo_url": app_settings.default_config.get("tool_logo_url")})
