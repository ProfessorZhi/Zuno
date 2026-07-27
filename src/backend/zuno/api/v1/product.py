from __future__ import annotations

import json

from fastapi import APIRouter, Body, Depends, Header, Query
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field

from zuno.api.dto.schemas import UnifiedResponseModel, resp_200, resp_500
from zuno.api.services.product import ProductService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService


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


class ProductActionConsumeBody(BaseModel):
    tenant_id: str = Field(min_length=1)
    action_token_id: str = Field(min_length=1)
    client_request_id: str = Field(min_length=1)
    raw_intent_ref: str = Field(min_length=1)
    payload: dict = Field(default_factory=dict)


class ProductFeedbackBody(BaseModel):
    task_id: str = Field(min_length=1)
    rating: int | None = None
    label: str | None = None
    comment: str | None = None
    dataset_candidate: bool = False


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
                "projection": {
                    "projection_event_id": result.projection.projection_event_id,
                    "stream_cursor_id": result.projection.stream_cursor_id,
                    "stream_sequence_no": result.projection.stream_sequence_no,
                    "freshness": result.projection.freshness,
                    "redaction_decision_ref": result.projection.redaction_decision_ref,
                },
                "available_actions": [
                    {
                        "action": action.action,
                        "action_token_id": action.action_token_id,
                        "target_ref": action.target_ref,
                        "effective_security_epoch_ref": action.effective_security_epoch_ref,
                        "projection_version": action.projection_version,
                        "expires_at": action.expires_at,
                    }
                    for action in result.available_actions
                ],
            }
        )
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/actions/consume", response_model=UnifiedResponseModel)
async def consume_action_token(
    *,
    body: ProductActionConsumeBody = Body(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = ProductService.consume_action_token(
            tenant_id=body.tenant_id,
            principal_id=login_user.user_id,
            action_token_id=body.action_token_id,
            client_request_id=body.client_request_id,
            raw_intent_ref=body.raw_intent_ref,
            payload=body.payload,
        )
        return resp_200(
            data={
                "action_token_id": result.action_token_id,
                "command_id": result.command_id,
                "receipt_id": result.receipt_id,
                "status": result.status,
                "target_ref": result.target_ref,
                "used_at": result.used_at,
            }
        )
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/artifacts/{artifact_id}", response_model=UnifiedResponseModel)
async def get_product_artifact(
    *,
    artifact_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    return resp_200(
        data=WorkspaceTaskRuntimeService.get_artifact(
            artifact_id,
            principal_id=str(login_user.user_id or ""),
        )
    )


@router.get("/artifacts/{artifact_id}/download")
async def download_product_artifact(
    *,
    artifact_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    payload = WorkspaceTaskRuntimeService.download_artifact(
        artifact_id,
        principal_id=str(login_user.user_id or ""),
    )
    return PlainTextResponse(
        payload["content"],
        media_type=payload["media_type"],
        headers={
            "Content-Disposition": f'attachment; filename="{payload["filename"]}"',
            "Cache-Control": "no-store",
        },
    )


@router.post("/feedback", response_model=UnifiedResponseModel)
async def create_product_feedback(
    *,
    payload: ProductFeedbackBody,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(
        data=WorkspaceTaskRuntimeService.record_feedback(
            task_id=payload.task_id,
            rating=payload.rating,
            label=payload.label,
            comment=payload.comment,
            dataset_candidate=payload.dataset_candidate,
        )
    )


@router.get("/stream-events", response_model=UnifiedResponseModel)
async def list_stream_events(
    *,
    tenant_id: str = Query(min_length=1),
    workspace_id: str = Query(min_length=1),
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        events = ProductService.list_stream_events(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=login_user.user_id,
            last_event_id=last_event_id,
        )
        return resp_200(
            data={
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "sequence_no": event.sequence_no,
                        "redaction_decision_ref": event.redaction_decision_ref,
                        "resync_required": event.resync_required,
                    }
                    for event in events
                ]
            }
        )
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/stream")
async def stream_projection_events(
    *,
    tenant_id: str = Query(min_length=1),
    workspace_id: str = Query(min_length=1),
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    login_user: UserPayload = Depends(get_login_user),
):
    events = ProductService.list_stream_events(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        principal_id=login_user.user_id,
        last_event_id=last_event_id,
    )

    async def event_source():
        yield "retry: 1000\n\n"
        for event in events:
            payload = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "sequence_no": event.sequence_no,
                "redaction_decision_ref": event.redaction_decision_ref,
                "resync_required": event.resync_required,
            }
            yield (
                f"id: {event.event_id}\n"
                f"event: {event.event_type}\n"
                f"data: {json.dumps(payload, ensure_ascii=True, sort_keys=True)}\n\n"
            )
        yield (
            "event: HEARTBEAT\n"
            'data: {"event_id":"heartbeat","event_type":"HEARTBEAT","sequence_no":0,'
            '"redaction_decision_ref":"redaction:heartbeat","resync_required":false}\n\n'
        )

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


__all__ = [
    "router",
    "submit_runtime_request",
    "consume_action_token",
    "list_stream_events",
    "stream_projection_events",
    "ProductRuntimeRequestBody",
    "ProductActionConsumeBody",
    "ProductFeedbackBody",
    "get_product_artifact",
    "download_product_artifact",
    "create_product_feedback",
]
