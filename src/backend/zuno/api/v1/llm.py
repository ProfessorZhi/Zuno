from fastapi import APIRouter, Depends, HTTPException

from zuno.api.services.llm import LLMService, LLM_Types
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.llm import LLMActivateReq, LLMCreateReq, LLMDeleteReq, LLMSearchReq, LLMUpdateReq
from zuno.schema.schemas import resp_200, resp_500

router = APIRouter(tags=["LLM"], prefix="/llm")


@router.post("/create", summary="Create LLM")
async def create_llm(req: LLMCreateReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        await LLMService.create_llm(user_id=login_user.user_id, **req.model_dump())
        return resp_200()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.delete("/delete", summary="Delete LLM")
async def delete_llm(req: LLMDeleteReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        await LLMService.verify_user_permission(llm_id=req.llm_id, user_id=login_user.user_id, action="delete")
        await LLMService.delete_llm(req.llm_id)
        return resp_200()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.put("/update", summary="Update LLM")
async def update_llm(req: LLMUpdateReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        await LLMService.verify_user_permission(llm_id=req.llm_id, user_id=login_user.user_id, action="update")
        await LLMService.update_llm(**req.model_dump(exclude_unset=True))
        return resp_200()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/activate", summary="Activate model slot")
async def activate_llm(req: LLMActivateReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        await LLMService.verify_user_permission(llm_id=req.llm_id, user_id=login_user.user_id, action="activate")
        await LLMService.activate_model_slot(req.llm_id, req.model_slot)
        return resp_200()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/all", summary="List all LLMs")
async def get_all_llm(login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await LLMService.get_all_llm(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/personal", summary="List personal LLMs")
async def get_personal_llm(login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await LLMService.get_personal_llm(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/visible", summary="List visible LLMs")
async def get_visible_llm(login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await LLMService.get_visible_llm(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/agent/models", summary="List agent models")
async def get_all_agent_models(login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await LLMService.get_visible_llm(login_user.user_id)
        return resp_200(data=result.get("LLM", []))
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/search", summary="Search LLMs")
async def search_models(req: LLMSearchReq, login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await LLMService.search_llms_by_name(login_user.user_id, req.llm_name)
        return resp_200({"LLM": result})
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/schema", summary="Get LLM schema")
async def get_llm_type(login_user: UserPayload = Depends(get_login_user)):
    return resp_200(data=LLM_Types)


__all__ = [
    "activate_llm",
    "create_llm",
    "delete_llm",
    "get_all_agent_models",
    "get_all_llm",
    "get_llm_type",
    "get_personal_llm",
    "get_visible_llm",
    "router",
    "search_models",
    "update_llm",
]
