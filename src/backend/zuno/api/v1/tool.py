from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from zuno.api.services.tool import ToolRuntimeService, ToolService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500
from zuno.schema.tool import (
    CLIToolPreviewReq,
    RemoteApiAssistReq,
    ToolConnectivityReq,
    ToolCreateReq,
    ToolDeleteReq,
    ToolUpdateReq,
)
from zuno.settings import app_settings

router = APIRouter(tags=["Tool"], prefix="/tool")


@router.post("/create", response_model=UnifiedResponseModel)
async def create_tool(*, req: ToolCreateReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await ToolRuntimeService.create_user_defined_tool(
            req,
            user_id=login_user.user_id,
        )
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"create tool failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/all", summary="Get all tools visible to the current user")
async def get_all_tools(login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await ToolService.get_all_tools(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"get visible tools failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/user_defined", summary="Get custom tools created by the current user")
async def get_user_defined_tools(login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await ToolService.get_user_defined_tools(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        logger.error(f"get user defined tools failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/delete", response_model=UnifiedResponseModel)
async def delete_user_defined_tool(req: ToolDeleteReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        await ToolService.verify_user_permission(req.tool_id, login_user.user_id, action="delete")
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
        _ = login_user
        result = ToolRuntimeService.preview_cli_tool_directory(req)
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
        _ = login_user
        result = await ToolRuntimeService.assist_remote_api_tool(req)
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
        _ = login_user
        result = await ToolRuntimeService.test_tool_connectivity(req)
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
        _ = login_user
        result = await ToolRuntimeService.test_system_tool_connectivity(tool_name)
        return resp_200(
            data={
                **result.model_dump(),
                "status": ToolRuntimeService.to_runtime_status(result),
            }
        )
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
        await ToolService.verify_user_permission(tool_id, login_user.user_id, action="test")
        tool = await ToolService.get_tool_by_id(tool_id)
        if not tool or not tool.is_user_defined:
            raise ValueError("Only user defined tools support saved connectivity checks")
        result = await ToolRuntimeService.test_saved_tool_connectivity(tool)
        return resp_200(
            data={
                **result.model_dump(),
                "status": ToolRuntimeService.to_runtime_status(result),
            }
        )
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
        await ToolService.verify_user_permission(req.tool_id, login_user.user_id, action="update")
        await ToolService.update_user_defined_tool(
            tool_id=req.tool_id,
            update_values=ToolRuntimeService.build_update_payload(req),
        )
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/default_logo", summary="Get default tool logo")
async def get_default_tol_logo(login_user: UserPayload = Depends(get_login_user)):
    _ = login_user
    return resp_200(data={"logo_url": app_settings.default_config.get("tool_logo_url")})


__all__ = [
    "assist_remote_api_tool",
    "create_tool",
    "delete_user_defined_tool",
    "get_all_tools",
    "get_default_tol_logo",
    "get_user_defined_tools",
    "preview_cli_tool_directory",
    "router",
    "test_saved_tool_connectivity",
    "test_system_tool_connectivity",
    "test_tool_connectivity",
    "update_user_defined_tool",
]
