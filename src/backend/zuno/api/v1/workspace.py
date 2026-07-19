from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import PlainTextResponse, StreamingResponse

from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.services.workspace import WorkspaceService
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.api.services.workspace_session import WorkSpaceSessionService
from zuno.schema.schemas import resp_200
from zuno.schema.workspace import WorkSpaceSimpleTask

router = APIRouter(prefix="/workspace", tags=["WorkSpace"])


class WorkSpaceSessionCreateBody(BaseModel):
    title: str = ""
    session_id: str | None = None
    agent: str = Field(default="simple")
    workspace_mode: str = Field(default="normal")
    contexts: list[dict] = Field(default_factory=list)


class WorkspaceFeedbackBody(BaseModel):
    task_id: str
    rating: int | None = None
    label: str | None = None
    comment: str | None = None
    dataset_candidate: bool = False


class WorkspaceFileBody(BaseModel):
    workspace_id: str
    file_id: str | None = None
    name: str | None = None
    mime_type: str
    hash: str | None = None
    uri: str | None = None
    content: str | None = None
    trace_id: str | None = None
    security_label: str = "internal"


class WorkspaceIngestBody(BaseModel):
    workspace_id: str
    file_id: str
    knowledge_space_id: str
    session_id: str | None = None
    trace_id: str | None = None


class WorkspaceApprovalBody(BaseModel):
    decision: str
    comment: str | None = None
    approval_id: str | None = None
    tool_call_id: str | None = None
    required_approval: str | None = None


class WorkspaceCancelBody(BaseModel):
    reason: str | None = None


@router.get("/plugins", summary="Get workspace tools")
async def get_workspace_plugins(
    execution_mode: str = "tool",
    access_scope: str = "workspace",
    login_user: UserPayload = Depends(get_login_user),
):
    return await WorkspaceService.get_workspace_plugins(
        execution_mode=execution_mode,
        access_scope=access_scope,
        user_id=login_user.user_id,
    )


@router.get("/execution-modes", summary="Get workspace execution config")
async def get_workspace_execution_modes(
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return WorkspaceService.get_workspace_execution_modes()


@router.get("/session", summary="Get workspace session list")
async def get_workspace_sessions(
    workspace_mode: str | None = None,
    login_user: UserPayload = Depends(get_login_user),
):
    results = await WorkSpaceSessionService.get_workspace_sessions(
        login_user.user_id,
        workspace_mode=workspace_mode,
    )
    return resp_200(data=results)


@router.post("/session", summary="Create workspace session")
async def create_workspace_session(
    payload: WorkSpaceSessionCreateBody,
    login_user: UserPayload = Depends(get_login_user),
):
    session = await WorkSpaceSessionService.create_workspace_session(
        WorkspaceService.create_workspace_session_payload(payload, login_user.user_id)
    )
    return resp_200(data=WorkSpaceSessionService.serialize_session(session))


@router.post("/session/{session_id}", summary="Get workspace session info")
async def workspace_session_info(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await WorkSpaceSessionService.get_workspace_session_from_id(
            session_id,
            login_user.user_id,
        )
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.delete("/session", summary="Delete workspace session")
async def delete_workspace_session(
    session_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        await WorkSpaceSessionService.delete_workspace_session([session_id], login_user.user_id)
        return resp_200()
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/simple/chat", summary="Workspace simple chat")
async def workspace_simple_chat(
    simple_task: WorkSpaceSimpleTask,
    login_user: UserPayload = Depends(get_login_user),
):
    return await WorkspaceService.workspace_simple_chat_response(
        simple_task=simple_task,
        login_user=login_user,
    )


@router.post("/file", summary="Register workspace file")
async def register_workspace_file(
    payload: WorkspaceFileBody,
    login_user: UserPayload = Depends(get_login_user),
):
    return resp_200(
        data=WorkspaceTaskRuntimeService.register_file(
            workspace_id=payload.workspace_id,
            login_user=login_user,
            file_id=payload.file_id,
            mime_type=payload.mime_type,
            file_hash=payload.hash,
            name=payload.name,
            uri=payload.uri,
            trace_id=payload.trace_id,
            security_label=payload.security_label,
            content=payload.content,
        )
    )


@router.post("/ingest", summary="Create workspace ingest job")
async def create_workspace_ingest(
    payload: WorkspaceIngestBody,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(
        data=WorkspaceTaskRuntimeService.create_ingest_job(
            workspace_id=payload.workspace_id,
            file_id=payload.file_id,
            knowledge_space_id=payload.knowledge_space_id,
            session_id=payload.session_id,
            trace_id=payload.trace_id,
        )
    )


@router.post("/task", summary="Create workspace task")
async def create_workspace_task(
    simple_task: WorkSpaceSimpleTask,
    login_user: UserPayload = Depends(get_login_user),
):
    return resp_200(
        data=WorkspaceTaskRuntimeService.create_task(
            simple_task=simple_task,
            login_user=login_user,
        )
    )


@router.get("/task-lifecycle", summary="Get workspace task lifecycle contract")
async def get_workspace_task_lifecycle(
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(data=WorkspaceTaskRuntimeService.task_lifecycle_contract())


@router.get("/retrieval-observability", summary="Get agentic retrieval observability summary")
async def get_workspace_retrieval_observability(
    limit: int = 20,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(data=WorkspaceTaskRuntimeService.retrieval_observability_summary(limit=limit))


@router.get("/task/{task_id}", summary="Get workspace task")
async def get_workspace_task(
    task_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(data=WorkspaceTaskRuntimeService.get_task_snapshot(task_id))


@router.get("/task/{task_id}/events", summary="Get workspace task events")
async def get_workspace_task_events(
    task_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(data=WorkspaceTaskRuntimeService.list_task_events(task_id))


@router.post("/task/{task_id}/approve", summary="Approve workspace task")
async def approve_workspace_task(
    task_id: str,
    payload: WorkspaceApprovalBody,
    login_user: UserPayload = Depends(get_login_user),
):
    return resp_200(
        data=WorkspaceTaskRuntimeService.approve_task(
            task_id=task_id,
            decision=payload.decision,
            comment=payload.comment,
            principal_id=str(login_user.user_id or ""),
        )
    )


@router.post("/task/{task_id}/cancel", summary="Cancel workspace task")
async def cancel_workspace_task(
    task_id: str,
    payload: WorkspaceCancelBody,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(
        data=WorkspaceTaskRuntimeService.cancel_task(
            task_id=task_id,
            reason=payload.reason,
        )
    )


@router.get("/task/{task_id}/events/stream", summary="Stream workspace task events")
async def stream_workspace_task_events(
    task_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return StreamingResponse(
        WorkspaceTaskRuntimeService.stream_task_events(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/artifact/{artifact_id}", summary="Get workspace artifact")
async def get_workspace_artifact(
    artifact_id: str,
    login_user: UserPayload = Depends(get_login_user),
):
    return resp_200(
        data=WorkspaceTaskRuntimeService.get_artifact(
            artifact_id,
            principal_id=str(login_user.user_id or ""),
        )
    )


@router.get("/artifact/{artifact_id}/download", summary="Download workspace artifact")
async def download_workspace_artifact(
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


@router.post("/feedback", summary="Create workspace feedback")
async def create_workspace_feedback(
    payload: WorkspaceFeedbackBody,
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


__all__ = [
    "WorkSpaceSessionCreateBody",
    "WorkspaceApprovalBody",
    "WorkspaceCancelBody",
    "WorkspaceFeedbackBody",
    "WorkspaceFileBody",
    "WorkspaceIngestBody",
    "approve_workspace_task",
    "cancel_workspace_task",
    "create_workspace_ingest",
    "create_workspace_session",
    "create_workspace_feedback",
    "create_workspace_task",
    "delete_workspace_session",
    "download_workspace_artifact",
    "get_workspace_artifact",
    "get_workspace_execution_modes",
    "get_workspace_plugins",
    "get_workspace_retrieval_observability",
    "get_workspace_sessions",
    "get_workspace_task_lifecycle",
    "get_workspace_task",
    "get_workspace_task_events",
    "register_workspace_file",
    "router",
    "stream_workspace_task_events",
    "workspace_session_info",
    "workspace_simple_chat",
]
