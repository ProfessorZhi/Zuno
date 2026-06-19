from fastapi import APIRouter
from loguru import logger

from zuno.api.services.domain_pack import DomainPackService
from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500

router = APIRouter(tags=["Domain Packs"])


@router.get("/domain-packs", response_model=UnifiedResponseModel)
async def list_domain_packs():
    try:
        return resp_200(data=await DomainPackService.list_domain_packs())
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/domain-packs/{pack_id}/publish", response_model=UnifiedResponseModel)
async def publish_domain_pack(pack_id: str):
    try:
        return resp_200(data=await DomainPackService.publish_domain_pack(pack_id))
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


__all__ = ["list_domain_packs", "publish_domain_pack", "router"]
