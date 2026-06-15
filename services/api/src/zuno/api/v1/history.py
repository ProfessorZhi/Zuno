from fastapi import APIRouter, Depends, Query
from loguru import logger

from zuno.api.services.history import HistoryService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500

router = APIRouter(tags=["History"])


@router.get("/history", response_model=UnifiedResponseModel)
async def get_dialog_history(
    dialog_id: str = Query(..., description="对话的ID", embed=True),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        _ = login_user
        results = await HistoryService.get_dialog_history(dialog_id=dialog_id)
        return resp_200(data=results)
    except Exception as err:
        logger.error(err)
        return resp_500(message=str(err))


__all__ = ["get_dialog_history", "router"]
