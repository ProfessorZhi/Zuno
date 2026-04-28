import os
from urllib.parse import urlparse

from fastapi import APIRouter, Body, Depends, Query

from agentchat.api.services.knowledge import KnowledgeService
from agentchat.api.services.knowledge_file import KnowledgeFileService
from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.schema.schemas import UnifiedResponseModel, resp_200, resp_500
from agentchat.services.storage import storage_client
from agentchat.utils.file_utils import get_object_key_from_public_url, get_save_tempfile

router = APIRouter(tags=["Knowledge-File"])


@router.post("/knowledge_file/create", response_model=UnifiedResponseModel)
async def upload_file(
    knowledge_id: str = Body(..., description="知识库 ID"),
    file_url: str = Body(..., description="文件上传后返回的 URL"),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        file_name = file_url.split("/")[-1]
        local_file_path = get_save_tempfile(file_name)
        parsed = urlparse(file_url)
        object_key = get_object_key_from_public_url(
            file_url,
            bucket_name=(parsed.path.lstrip("/").split("/", 1)[0] if parsed.path else ""),
        )
        storage_client.download_file(object_key, local_file_path)
        file_size_bytes = os.path.getsize(local_file_path)

        name_part, ext_part = file_name.rsplit(".", 1) if "." in file_name else (file_name, "")
        parts = name_part.split("_")
        file_name = "_".join(parts[:-1]) + f".{ext_part}"

        result = await KnowledgeFileService.create_knowledge_file(
            file_name=file_name,
            file_path=local_file_path,
            knowledge_id=knowledge_id,
            user_id=login_user.user_id,
            oss_url=file_url,
            file_size_bytes=file_size_bytes,
        )
        return resp_200(data=result)
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/knowledge_file/select", response_model=UnifiedResponseModel)
async def select_knowledge_file(
    knowledge_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        results = await KnowledgeFileService.get_knowledge_file(knowledge_id)
        return resp_200(data=results)
    except Exception as err:
        return resp_500(message=str(err))


@router.delete("/knowledge_file/delete", response_model=UnifiedResponseModel)
async def delete_knowledge_file(
    knowledge_file_id: str = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeFileService.verify_user_permission(knowledge_file_id, login_user.user_id)
        await KnowledgeFileService.delete_knowledge_file(knowledge_file_id)
        return resp_200()
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/knowledge_file/status", response_model=UnifiedResponseModel)
async def get_knowledge_file_status(
    knowledge_file_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeFileService.verify_user_permission(knowledge_file_id, login_user.user_id)
        knowledge_file = await KnowledgeFileService.select_knowledge_file_by_id(knowledge_file_id)
        return resp_200(data=knowledge_file.to_dict())
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/knowledge_file/task", response_model=UnifiedResponseModel)
async def get_knowledge_file_task(
    task_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await KnowledgeFileService.get_task_detail(task_id)
        task = result.get("task")
        if task:
            await KnowledgeFileService.verify_user_permission(task["knowledge_file_id"], login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/knowledge_file/tasks", response_model=UnifiedResponseModel)
async def list_knowledge_file_tasks(
    knowledge_file_id: str | None = Query(default=None),
    knowledge_id: str | None = Query(default=None),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        if knowledge_file_id:
            await KnowledgeFileService.verify_user_permission(knowledge_file_id, login_user.user_id)
        if knowledge_id:
            await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        result = await KnowledgeFileService.list_tasks(
            knowledge_file_id=knowledge_file_id,
            knowledge_id=knowledge_id,
        )
        return resp_200(data=result)
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/knowledge_file/task/retry", response_model=UnifiedResponseModel)
async def retry_knowledge_file_task(
    task_id: str = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        detail = await KnowledgeFileService.get_task_detail(task_id)
        task = detail.get("task")
        if not task:
            raise ValueError("knowledge task not found")
        await KnowledgeFileService.verify_user_permission(task["knowledge_file_id"], login_user.user_id)
        result = await KnowledgeFileService.retry_task(task_id)
        return resp_200(data=result)
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/knowledge_file/reindex", response_model=UnifiedResponseModel)
async def reindex_knowledge_files(
    knowledge_id: str = Body(..., embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await KnowledgeService.verify_user_permission(knowledge_id, login_user.user_id)
        result = await KnowledgeFileService.reindex_knowledge_files(knowledge_id)
        return resp_200(data=result)
    except Exception as err:
        return resp_500(message=str(err))
