from typing import List, Union

from fastapi import APIRouter, Body, Depends
from loguru import logger

from zuno.api.services.knowledge import KnowledgeService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.knowledge import (
    KnowledgeConfig,
    KnowledgeCreateRequest,
    KnowledgeUpdateRequest,
)
from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500

router = APIRouter(tags=["Knowledge"])


@router.post("/knowledge/create", response_model=UnifiedResponseModel)
async def upload_knowledge(
    *,
    knowledge_req: KnowledgeCreateRequest,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await KnowledgeService.create_knowledge(
            knowledge_name=knowledge_req.knowledge_name,
            knowledge_desc=knowledge_req.knowledge_desc,
            user_id=login_user.user_id,
            knowledge_config=(
                knowledge_req.knowledge_config.model_dump()
                if knowledge_req.knowledge_config is not None
                else None
            ),
        )
        return resp_200(data=result)
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/knowledge/select", response_model=UnifiedResponseModel)
async def select_knowledge(
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        results = await KnowledgeService.select_knowledge(login_user.user_id)
        return resp_200(data=results)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.put("/knowledge/update", response_model=UnifiedResponseModel)
async def update_knowledge(
    *,
    knowledge_req: KnowledgeUpdateRequest,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_req.knowledge_id, login_user.user_id)
        await KnowledgeService.update_knowledge(
            knowledge_req.knowledge_id,
            knowledge_req.knowledge_name,
            knowledge_req.knowledge_desc,
            (
                knowledge_req.knowledge_config.model_dump(exclude_unset=True)
                if knowledge_req.knowledge_config is not None
                else None
            ),
        )
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.delete("/knowledge/delete", response_model=UnifiedResponseModel)
async def delete_knowledge(
    knowledge_id: str = Body(embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        await KnowledgeService.delete_knowledge(knowledge_id)
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/knowledge/files", response_model=UnifiedResponseModel)
async def get_knowledge_files(
    knowledge_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        result = await KnowledgeService.select_knowledge_files(knowledge_id)
        return resp_200(data=result)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/knowledge/reindex", response_model=UnifiedResponseModel)
async def reindex_knowledge(
    knowledge_ids: Union[str, List[str]] = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        if isinstance(knowledge_ids, str):
            normalized_ids = [knowledge_ids]
        else:
            normalized_ids = list(knowledge_ids or [])

        for knowledge_id in normalized_ids:
            await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)

        for knowledge_id in normalized_ids:
            await KnowledgeService.reindex_knowledge(knowledge_id)
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/knowledge/{knowledge_id}/config/impact", response_model=UnifiedResponseModel)
async def analyze_knowledge_config_impact(
    *,
    knowledge_id: str,
    next_config: KnowledgeConfig | dict = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        previous_config = await KnowledgeService.get_knowledge_config(knowledge_id)
        normalized_next_config = (
            next_config.model_dump() if isinstance(next_config, KnowledgeConfig) else next_config
        )
        impact = KnowledgeService.analyze_config_impact(previous_config, normalized_next_config)
        return resp_200(data=impact)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/knowledge/{knowledge_id}/config", response_model=UnifiedResponseModel)
async def get_knowledge_config(
    *,
    knowledge_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        return resp_200(data=await KnowledgeService.get_knowledge_config(knowledge_id))
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.put("/knowledge/{knowledge_id}/config", response_model=UnifiedResponseModel)
async def update_knowledge_config(
    *,
    knowledge_id: str,
    next_config: KnowledgeConfig | dict = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        normalized_next_config = (
            next_config.model_dump() if isinstance(next_config, KnowledgeConfig) else next_config
        )
        await KnowledgeService.update_knowledge(
            knowledge_id,
            None,
            None,
            normalized_next_config,
        )
        return resp_200()
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/knowledge/{knowledge_id}/reindex/{action}", response_model=UnifiedResponseModel)
async def reindex_knowledge_action(
    *,
    knowledge_id: str,
    action: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        result = await KnowledgeService.run_reindex_action(knowledge_id, action)
        return resp_200(data=result)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.get("/knowledge/eval-profiles", response_model=UnifiedResponseModel)
async def list_eval_profiles():
    try:
        return resp_200(data=await KnowledgeService.list_eval_profiles())
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


@router.post("/knowledge/search", response_model=UnifiedResponseModel)
async def search_knowledge(
    *,
    knowledge_ids: List[str] = Body(...),
    query: str = Body(...),
    product_mode: str = Body(default="auto"),
    query_method: str | None = Body(default=None),
    top_k: int = Body(default=5),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        for knowledge_id in knowledge_ids:
            await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)

        result = await KnowledgeService.search_knowledge(
            user_id=login_user.user_id,
            knowledge_ids=knowledge_ids,
            query=query,
            product_mode=product_mode,
            query_method=query_method,
            top_k=top_k,
        )
        return resp_200(data=result)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


__all__ = [
    "analyze_knowledge_config_impact",
    "delete_knowledge",
    "get_knowledge_config",
    "get_knowledge_files",
    "list_eval_profiles",
    "reindex_knowledge",
    "reindex_knowledge_action",
    "router",
    "search_knowledge",
    "select_knowledge",
    "update_knowledge_config",
    "update_knowledge",
    "upload_knowledge",
]
