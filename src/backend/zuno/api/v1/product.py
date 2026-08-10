from __future__ import annotations

import json

from datetime import datetime

from fastapi import APIRouter, Body, Depends, Header, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from zuno.api.dto.schemas import UnifiedResponseModel, resp_200, resp_500
from zuno.api.services.product import ProductService
from zuno.api.services.product import (
    ProductIngestionService,
    ProductObservabilityService,
)
from zuno.api.services.user import UserPayload, get_login_user


class ProductRuntimeRequestBody(BaseModel):
    tenant_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)
    client_request_id: str = Field(min_length=1)
    runtime_request_ref: str = Field(min_length=1)
    raw_intent_ref: str = Field(min_length=1)
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


class ProductAgentDraftBody(BaseModel):
    tenant_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    client_request_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    description: str = ""
    primary_agent_core_profile_ref: str = Field(default="agent-core-profile:product:default", min_length=1)
    configuration: dict = Field(default_factory=dict)


class ProductAgentPublicationBody(BaseModel):
    tenant_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    client_request_id: str = Field(min_length=1)
    agent_definition_id: str = Field(min_length=1)
    agent_version_id: str = Field(min_length=1)
    publication_scope: str = Field(default="WORKSPACE", min_length=1)
    primary_agent_core_profile_ref: str = Field(default="agent-core-profile:product:default", min_length=1)
    configuration: dict = Field(default_factory=dict)


class ProductAgentInstallationBody(BaseModel):
    tenant_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    client_request_id: str = Field(min_length=1)
    agent_version_id: str = Field(min_length=1)
    installation_scope: str = Field(default="USER", min_length=1)


class ProductFileBody(BaseModel):
    workspace_id: str = Field(min_length=1)
    file_id: str | None = None
    name: str | None = None
    mime_type: str = Field(min_length=1)
    hash: str | None = None
    uri: str | None = None
    content: str | None = None
    trace_id: str | None = None
    security_label: str = "internal"
    deadline_at: datetime | None = None


class ProductIngestionBody(BaseModel):
    workspace_id: str = Field(min_length=1)
    file_id: str = Field(min_length=1)
    knowledge_space_id: str = Field(min_length=1)
    session_id: str | None = None
    trace_id: str | None = None


router = APIRouter(tags=["Product"], prefix="/product")


def _agent_definition_payload(definition) -> dict:
    return {
        "agent_definition_id": definition.agent_definition_id,
        "tenant_id": definition.tenant_id,
        "workspace_id": definition.workspace_id,
        "owner_principal_ref": definition.owner_principal_ref,
        "display_name": definition.display_name,
        "description": definition.description,
        "status": definition.status,
    }


def _agent_draft_payload(draft) -> dict:
    return {
        "agent_draft_id": draft.agent_draft_id,
        "agent_definition_id": draft.agent_definition_id,
        "draft_version": draft.draft_version,
        "editor_principal_ref": draft.editor_principal_ref,
        "configuration_hash": draft.configuration_hash,
        "status": draft.status,
    }


def _agent_version_payload(version) -> dict:
    return {
        "agent_version_id": version.agent_version_id,
        "agent_definition_id": version.agent_definition_id,
        "version_no": version.version_no,
        "configuration_hash": version.configuration_hash,
        "primary_agent_core_profile_ref": version.primary_agent_core_profile_ref,
        "status": version.status,
    }


def _agent_publication_payload(publication) -> dict:
    return {
        "publication_id": publication.publication_id,
        "agent_version_id": publication.agent_version_id,
        "scope": publication.scope,
        "status": publication.status,
    }


def _agent_installation_payload(installation) -> dict:
    return {
        "installation_id": installation.installation_id,
        "agent_version_id": installation.agent_version_id,
        "workspace_id": installation.workspace_id,
        "principal_ref": installation.principal_ref,
        "status": installation.status,
    }


def _agent_catalog_entry_payload(entry) -> dict:
    return {
        "catalog_entry_id": entry.catalog_entry_id,
        "agent_version_id": entry.agent_version_id,
        "publication_ref": entry.publication_ref,
        "agent_definition_id": entry.agent_definition_id,
        "display_name": entry.display_name,
        "description": entry.description,
        "definition_status": entry.definition_status,
        "authorized": entry.authorized,
        "visibility_scope": entry.visibility_scope,
        "effective_permission_preview_ref": entry.effective_permission_preview_ref,
    }


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


@router.post("/files", response_model=UnifiedResponseModel)
async def register_product_file(
    *,
    body: ProductFileBody = Body(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        return resp_200(
            data=ProductIngestionService.register_file(
                workspace_id=body.workspace_id,
                login_user=login_user,
                file_id=body.file_id,
                mime_type=body.mime_type,
                file_hash=body.hash,
                name=body.name,
                uri=body.uri,
                trace_id=body.trace_id,
                security_label=body.security_label,
                content=body.content,
                deadline_at=body.deadline_at,
            )
        )
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/ingestions", response_model=UnifiedResponseModel)
async def create_product_ingestion(
    *,
    body: ProductIngestionBody = Body(...),
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    try:
        return resp_200(
            data=ProductIngestionService.create_ingest_job(
                workspace_id=body.workspace_id,
                file_id=body.file_id,
                knowledge_space_id=body.knowledge_space_id,
                session_id=body.session_id,
                trace_id=body.trace_id,
            )
        )
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/observability/retrieval", response_model=UnifiedResponseModel)
async def get_product_retrieval_observability(
    *,
    limit: int = Query(default=20, ge=1, le=200),
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(data=ProductObservabilityService.retrieval_observability_summary(limit=limit))


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


@router.post("/agent-drafts", response_model=UnifiedResponseModel)
async def create_agent_draft(
    *,
    body: ProductAgentDraftBody = Body(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        definition, draft = ProductService.create_agent_draft(
            tenant_id=body.tenant_id,
            workspace_id=body.workspace_id,
            principal_id=login_user.user_id,
            client_request_id=body.client_request_id,
            display_name=body.display_name,
            description=body.description,
            primary_agent_core_profile_ref=body.primary_agent_core_profile_ref,
            configuration=body.configuration,
        )
        return resp_200(
            data={
                "agent_definition": _agent_definition_payload(definition),
                "agent_draft": _agent_draft_payload(draft),
            }
        )
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/agent-publications", response_model=UnifiedResponseModel)
async def publish_agent_version(
    *,
    body: ProductAgentPublicationBody = Body(...),
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    try:
        publication, catalog_entry = ProductService.publish_agent_version(
            tenant_id=body.tenant_id,
            workspace_id=body.workspace_id,
            client_request_id=body.client_request_id,
            agent_definition_id=body.agent_definition_id,
            agent_version_id=body.agent_version_id,
            publication_scope=body.publication_scope,
            primary_agent_core_profile_ref=body.primary_agent_core_profile_ref,
            configuration=body.configuration,
        )
        return resp_200(
            data={
                "agent_publication": _agent_publication_payload(publication),
                "agent_catalog_entry": _agent_catalog_entry_payload(catalog_entry),
            }
        )
    except Exception as err:
        return resp_500(message=str(err))


@router.delete("/agent-publications/{publication_id}", response_model=UnifiedResponseModel)
async def revoke_agent_publication(
    *,
    publication_id: str,
    tenant_id: str = Query(min_length=1),
    workspace_id: str = Query(min_length=1),
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    try:
        publication = ProductService.revoke_agent_publication(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            publication_id=publication_id,
        )
        return resp_200(data={"agent_publication": _agent_publication_payload(publication)})
    except Exception as err:
        return resp_500(message=str(err))


@router.post("/agent-installations", response_model=UnifiedResponseModel)
async def install_agent_version(
    *,
    body: ProductAgentInstallationBody = Body(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        installation = ProductService.install_agent_version(
            tenant_id=body.tenant_id,
            workspace_id=body.workspace_id,
            principal_id=login_user.user_id,
            client_request_id=body.client_request_id,
            agent_version_id=body.agent_version_id,
            installation_scope=body.installation_scope,
        )
        return resp_200(data={"agent_installation": _agent_installation_payload(installation)})
    except Exception as err:
        return resp_500(message=str(err))


@router.delete("/agent-installations/{installation_id}", response_model=UnifiedResponseModel)
async def revoke_agent_installation(
    *,
    installation_id: str,
    tenant_id: str = Query(min_length=1),
    workspace_id: str = Query(min_length=1),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        installation = ProductService.revoke_agent_installation(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=login_user.user_id,
            installation_id=installation_id,
        )
        return resp_200(data={"agent_installation": _agent_installation_payload(installation)})
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/agent-catalog", response_model=UnifiedResponseModel)
async def list_agent_catalog(
    *,
    tenant_id: str = Query(min_length=1),
    workspace_id: str = Query(min_length=1),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        entries = ProductService.list_agent_catalog(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=login_user.user_id,
        )
        return resp_200(data={"agent_catalog_entries": [_agent_catalog_entry_payload(entry) for entry in entries]})
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/agent-studio/{agent_definition_id}", response_model=UnifiedResponseModel)
async def load_agent_studio_snapshot(
    *,
    agent_definition_id: str,
    tenant_id: str = Query(min_length=1),
    workspace_id: str = Query(min_length=1),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        snapshot = ProductService.load_agent_studio_snapshot(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=login_user.user_id,
            agent_definition_id=agent_definition_id,
        )
        payload = {
            "agent_definition": _agent_definition_payload(snapshot.agent_definition),
            "agent_draft": _agent_draft_payload(snapshot.agent_draft) if snapshot.agent_draft else None,
            "agent_version": _agent_version_payload(snapshot.agent_version) if snapshot.agent_version else None,
            "agent_catalog_entry": _agent_catalog_entry_payload(snapshot.agent_catalog_entry)
            if snapshot.agent_catalog_entry
            else None,
            "configuration": snapshot.configuration,
        }
        return resp_200(data=payload)
    except Exception as err:
        return resp_500(message=str(err))


@router.get("/artifacts/{artifact_id}", response_model=UnifiedResponseModel)
async def get_product_artifact(
    *,
    artifact_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    payload = ProductService.get_artifact(
        artifact_id,
        principal_id=str(login_user.user_id or ""),
    )
    artifact = dict(payload.get("artifact") or {})
    citation_refs = list(payload.get("citation_refs") or artifact.get("citation_refs") or [])
    citation_ids = [
        str(ref.get("citation_id") or ref.get("citation_ref") or ref.get("source_ref") or "")
        for ref in citation_refs
        if isinstance(ref, dict)
    ]
    citation_ids = [value for value in citation_ids if value]
    download = dict(payload.get("download") or {})
    quality_status = "RUNTIME_OBSERVED" if citation_refs else "UNMEASURED"
    enriched_payload = {
        **payload,
        "product_artifact": {
            "artifact_ref": artifact_id,
            "publication_ref": f"publication:{artifact_id}",
            "projection_version": 0,
            "downloadable": bool(download.get("url")),
            "citation_refs": citation_ids,
            "citation_count": len(citation_refs),
            "citation_authorized": bool(citation_refs),
            "download_policy": str(download.get("policy") or artifact.get("download_policy") or "unknown"),
        },
        "product_quality": {
            "quality_ref": f"quality:{artifact_id}:citation",
            "projection_version": 0,
            "status": quality_status,
            "blocked_reason": None,
            "metrics": {
                "citation_count": len(citation_refs),
            },
            "disclosure": (
                "Authorized citation refs returned by Product artifact endpoint."
                if citation_refs
                else "No citation refs were returned for this artifact."
            ),
        },
    }
    return resp_200(
        data=enriched_payload
    )


@router.get("/artifacts/{artifact_id}/download")
async def download_product_artifact(
    *,
    artifact_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    payload = ProductService.download_artifact(
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
        data=ProductService.record_feedback(
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
    "ProductFileBody",
    "ProductIngestionBody",
    "ProductRuntimeApprovalBody",
    "ProductRuntimeCancelBody",
    "ProductActionConsumeBody",
    "ProductFeedbackBody",
    "ProductAgentDraftBody",
    "ProductAgentPublicationBody",
    "ProductAgentInstallationBody",
    "create_agent_draft",
    "publish_agent_version",
    "revoke_agent_publication",
    "install_agent_version",
    "revoke_agent_installation",
    "list_agent_catalog",
    "get_product_artifact",
    "download_product_artifact",
    "create_product_feedback",
    "register_product_file",
    "create_product_ingestion",
    "get_product_runtime_lifecycle",
    "get_product_retrieval_observability",
    "get_product_runtime_snapshot",
    "list_product_runtime_events",
    "approve_product_runtime",
    "cancel_product_runtime",
    "stream_product_runtime_events",
]
