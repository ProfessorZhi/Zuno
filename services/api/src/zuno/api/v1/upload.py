from fastapi import APIRouter, Depends, File, UploadFile
from loguru import logger

from zuno.api.services.upload import UploadService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500

router = APIRouter(tags=["Upload"])


@router.post("/upload", description="Upload a file", response_model=UnifiedResponseModel)
async def upload_file(
    *,
    file: UploadFile = File(description="Supported file types include PDF, DOCX, TXT, and image files"),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        _ = login_user
        file_content = await file.read()
        sign_url = UploadService.upload_bytes(
            filename=file.filename,
            content=file_content,
            content_type=file.content_type or None,
        )
        return resp_200(sign_url)
    except Exception as err:
        logger.error(f"upload file failed for {file.filename}: {err}")
        return resp_500(message=str(err))


__all__ = ["router", "upload_file"]
