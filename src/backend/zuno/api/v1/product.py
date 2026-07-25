from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, Field

from zuno.api.dto.schemas import UnifiedResponseModel, resp_200, resp_500
from zuno.api.services.product import ProductService
from zuno.api.services.user import UserPayload, get_login_user


class ProductRuntimeRequestBody(BaseModel):
    tenant_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)
    client_request_id: str = Field(min_length=1)
    runtime_request_ref: str = Field(min_length=1)
    raw_intent_ref: str = Field(min_length=1)
    command_kind: str = Field(min_length=1)
    active_agent_version_id: str = Field(min_length=1)
    payload: dict = Field(default_factory=dict)


router = APIRouter(tags=["Product"], prefix="/product")


@router.post("/runtime-requests", response_model=UnifiedResponseModel)
async def submit_runtime_request(
    *,
    body: ProductRuntimeRequestBody = Body(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = ProductService.submit_runtime_request(
            tenant_id=body.tenant_id,
            workspace_id=body.workspace_id,
            conversation_id=body.conversation_id,
            principal_id=login_user.user_id,
            active_agent_version_id=body.active_agent_version_id,
            client_request_id=body.client_request_id,
            runtime_request_ref=body.runtime_request_ref,
            raw_intent_ref=body.raw_intent_ref,
            command_kind=body.command_kind,
            payload=body.payload,
        )
        return resp_200(
            data={
                "command_id": result.command_id,
                "receipt_id": result.receipt_id,
                "status": result.status,
            }
        )
    except Exception as err:
        return resp_500(message=str(err))


__all__ = ["router", "submit_runtime_request", "ProductRuntimeRequestBody"]
