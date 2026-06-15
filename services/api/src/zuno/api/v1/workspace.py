from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.services.workspace import WorkspaceService
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


__all__ = [
    "WorkSpaceSessionCreateBody",
    "create_workspace_session",
    "delete_workspace_session",
    "get_workspace_execution_modes",
    "get_workspace_plugins",
    "get_workspace_sessions",
    "router",
    "workspace_session_info",
    "workspace_simple_chat",
]
