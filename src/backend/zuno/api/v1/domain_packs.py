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


@router.post("/domain-packs/draft", response_model=UnifiedResponseModel)
async def create_domain_pack_draft(payload: dict):
    try:
        return resp_200(data=await DomainPackService.create_draft(payload))
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/domain-packs/draft/from-knowledge", response_model=UnifiedResponseModel)
async def create_domain_pack_draft_from_knowledge(payload: dict):
    try:
        return resp_200(data=await DomainPackService.create_draft_from_knowledge(payload))
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/domain-packs/{pack_id}", response_model=UnifiedResponseModel)
async def get_domain_pack(pack_id: str):
    try:
        return resp_200(data=await DomainPackService.get_domain_pack(pack_id))
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.put("/domain-packs/{pack_id}", response_model=UnifiedResponseModel)
async def update_domain_pack(pack_id: str, payload: dict):
    try:
        return resp_200(data=await DomainPackService.update_domain_pack(pack_id, payload))
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


__all__ = [
    "create_domain_pack_draft",
    "create_domain_pack_draft_from_knowledge",
    "get_domain_pack",
    "list_domain_packs",
    "publish_domain_pack",
    "router",
    "update_domain_pack",
]
