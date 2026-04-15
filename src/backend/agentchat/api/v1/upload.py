from loguru import logger
from fastapi import APIRouter, Body, UploadFile, File, Depends

from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.schema.schemas import UnifiedResponseModel, resp_200, resp_500
from agentchat.services.storage import storage_client
from agentchat.settings import app_settings
from agentchat.utils.file_utils import get_object_storage_base_path

router = APIRouter(tags=["Upload"])


def _build_storage_public_url(object_name: str) -> str:
    base_url = (app_settings.storage.active.base_url or "").rstrip("/")
    return f"{base_url}/{object_name.lstrip('/')}"

@router.post("/upload", description="上传文件的接口", response_model=UnifiedResponseModel)
async def upload_file(
    *,
    file: UploadFile = File(description="支持常见的Pdf、Docx、Txt、Jpg等文件"),
    login_user: UserPayload = Depends(get_login_user)
):
    try:
        file_content = await file.read()

        oss_object_name = get_object_storage_base_path(file.filename)
        sign_url = _build_storage_public_url(oss_object_name)

        storage_client.upload_file(
            oss_object_name,
            file_content,
            content_type=file.content_type or None,
        )

        return resp_200(sign_url)
    except Exception as err:
        logger.error(f"上传文件{file.filename}出错：{err}")
        return resp_500(message=str(err))
