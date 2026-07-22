from typing import List
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from loguru import logger

from zuno.api.services.agent import AgentService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.agent import AgentCreateReq, AgentDeleteReq, AgentSearchReq, AgentUpdateReq
from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500
from zuno.settings import app_settings

router = APIRouter(tags=["Agent"])


@router.post("/agent", response_model=UnifiedResponseModel)
async def create_agent(req: AgentCreateReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        if await AgentService.check_repeat_name(name=req.name, user_id=login_user.user_id):
            return resp_500(message="Agent name already exists")
        if not req.logo_url:
            req.logo_url = app_settings.default_config.get("agent_logo_url")

        result = await AgentService.create_agent(login_user, req)
        return resp_200(data=result)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/agent", response_model=UnifiedResponseModel)
async def get_agent(login_user: UserPayload = Depends(get_login_user)):
    try:
        results = await AgentService.get_all_agent_by_user_id(user_id=login_user.user_id)
        return resp_200(data=results)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.delete("/agent", response_model=UnifiedResponseModel)
async def delete_agent(req: AgentDeleteReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        await AgentService.verify_user_permission(req.agent_id, login_user.user_id, action="delete")
        await AgentService.delete_agent_by_id(req.agent_id)
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.put("/agent", response_model=UnifiedResponseModel)
async def update_agent(agent_request: AgentUpdateReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        await AgentService.verify_user_permission(agent_request.agent_id, login_user.user_id, action="update")

        update_values = agent_request.model_dump(exclude={"agent_id"}, exclude_none=True)

        await AgentService.update_agent(
            agent_id=agent_request.agent_id,
            update_values=update_values,
            user_id=login_user.user_id,
        )

        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/agent/search", response_model=UnifiedResponseModel)
async def search_agent(req: AgentSearchReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        results = await AgentService.search_agent_name(name=req.name, user_id=login_user.user_id)
        return resp_200(data=results)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/agent/upload", response_model=UnifiedResponseModel)
async def upload_agent_icon(
    files: List[UploadFile] = File(description="icon image"),
    user_id: str = Form(),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        _ = login_user
        image_urls = []
        for file in files:
            url = f"{app_settings.storage.active.base_url}/images/agent/{user_id}/{uuid4()}-{file.filename}"
            image_urls.append(url)
        return resp_200(data=image_urls)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/agent/custom", response_model=UnifiedResponseModel)
async def select_agent_by_custom(is_custom: bool = Body(description="whether agent is custom")):
    results = await AgentService.select_agent_by_custom(is_custom=is_custom)
    return resp_200(data=results)


@router.post("/agent/name", response_model=UnifiedResponseModel)
async def select_agent_by_name(name: str = Body(description="agent name")):
    results = await AgentService.select_agent_by_name(name=name)
    return resp_200(data=results)


@router.post("/agent/id", response_model=UnifiedResponseModel)
async def select_agent_by_id(agent_id: str = Body(description="agent id")):
    result = await AgentService.select_agent_by_id(agent_id=agent_id)
    return resp_200(data=result)


__all__ = [
    "create_agent",
    "delete_agent",
    "get_agent",
    "router",
    "search_agent",
    "select_agent_by_custom",
    "select_agent_by_id",
    "select_agent_by_name",
    "update_agent",
    "upload_agent_icon",
]
