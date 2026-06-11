from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.schema.capability import CapabilitySearchReq
from agentchat.schema.schemas import UnifiedResponseModel, resp_200
from agentchat.services.capability_registry import CapabilityRegistryService

router = APIRouter(tags=["Capability"], prefix="/capability")


@router.post("/search", response_model=UnifiedResponseModel)
async def search_capabilities(
    *,
    req: CapabilitySearchReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        results = await CapabilityRegistryService.search(
            req.query,
            user_id=login_user.user_id,
            kind=req.kind,
            limit=req.limit,
        )
        return resp_200(data=results)
    except Exception as err:
        logger.error(f"search capabilities failed: {err}")
        raise HTTPException(status_code=500, detail=str(err)) from err
