import json
import time
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from langchain_core.messages import HumanMessage, SystemMessage
from starlette.responses import StreamingResponse

from agentchat.api.services.llm import LLMService
from agentchat.api.services.mcp_server import MCPService
from agentchat.api.services.tool import ToolService
from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.api.services.workspace_session import WorkSpaceSessionService
from agentchat.prompts.completion import SYSTEM_PROMPT
from agentchat.schema.schemas import resp_200
from agentchat.schema.usage_stats import UsageStatsAgentType
from agentchat.schema.workspace import WorkSpaceSimpleTask
from agentchat.services.execution_policy import (
    filter_tools_for_mode,
    get_execution_config_payload,
    normalize_access_scope,
    normalize_execution_mode,
    validate_tools_for_mode,
)
from agentchat.services.workspace.attachment_service import build_workspace_attachment_prompt, classify_attachment
from agentchat.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent
from agentchat.tools.text2image.action import _text_to_image
from agentchat.utils.helpers import parse_imported_config
from agentchat.utils.contexts import set_agent_name_context, set_user_id_context

router = APIRouter(prefix="/workspace", tags=["WorkSpace"])


IMAGE_REGEN_KEYWORDS = [
    "\u751f\u6210",
    "\u91cd\u751f\u6210",
    "\u91cd\u7ed8",
    "\u6539\u80cc\u666f",
    "\u6362\u80cc\u666f",
    "\u80cc\u666f\u6539",
    "\u6539\u6210",
    "\u53d8\u4f53",
    "\u6d77\u62a5",
    "\u5c01\u9762",
    "logo",
    "poster",
    "cover",
    "regenerate",
    "redraw",
    "variant",
    "background",
    "recolor",
    "restyle",
]


def _pick_reference_image_url(simple_task: WorkSpaceSimpleTask) -> str:
    for attachment in simple_task.attachments:
        if classify_attachment(attachment) == "image":
            return attachment.url
    return ""


def _should_run_direct_image_generation(simple_task: WorkSpaceSimpleTask) -> bool:
    if simple_task.execution_mode != "tool":
        return False

    reference_image_url = _pick_reference_image_url(simple_task)
    if not reference_image_url:
        return False

    normalized_query = (simple_task.query or "").lower()
    return any(keyword in normalized_query for keyword in IMAGE_REGEN_KEYWORDS)


@router.get("/plugins", summary="Get workspace tools")
async def get_workspace_plugins(
    execution_mode: str = "tool",
    access_scope: str = "workspace",
    login_user: UserPayload = Depends(get_login_user),
):
    _ = normalize_access_scope(access_scope)
    results = await ToolService.get_visible_tool_by_user(login_user.user_id)
    return resp_200(data=filter_tools_for_mode(results, execution_mode))


@router.get("/execution-modes", summary="Get workspace execution config")
async def get_workspace_execution_modes(
    login_user: UserPayload = Depends(get_login_user),
):
    _ = login_user
    return resp_200(data=get_execution_config_payload())


@router.get("/session", summary="Get workspace session list")
async def get_workspace_sessions(login_user: UserPayload = Depends(get_login_user)):
    results = await WorkSpaceSessionService.get_workspace_sessions(login_user.user_id)
    return resp_200(data=results)


@router.post("/session", summary="Create workspace session")
async def create_workspace_session(
    *,
    title: str = "",
    contexts: dict = {},
    login_user: UserPayload = Depends(get_login_user),
):
    _ = title, contexts, login_user
    return resp_200()


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
    set_user_id_context(login_user.user_id)
    set_agent_name_context(UsageStatsAgentType.simple_agent)

    execution_mode = normalize_execution_mode(simple_task.execution_mode)
    access_scope = normalize_access_scope(simple_task.access_scope)
    model_config = await LLMService.get_llm_by_id(simple_task.model_id)

    if _should_run_direct_image_generation(simple_task):
        reference_image_url = _pick_reference_image_url(simple_task)

        async def direct_generate():
            yield f"data: {json.dumps({'event': 'status', 'timestamp': time.time(), 'data': {'phase': 'start', 'status': 'START', 'message': '已识别为参考图生成任务，直接调用生图能力'}}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'event': 'tool_call', 'timestamp': time.time(), 'data': {'tool_name': 'text_to_image', 'tool_type': '默认能力', 'tool_call_id': 'workspace-direct-image-generation', 'arguments': {'user_prompt': simple_task.query, 'reference_image_url': reference_image_url}, 'message': '正在根据上传图片生成新图'}}, ensure_ascii=False)}\n\n"
            try:
                result = await asyncio.to_thread(_text_to_image, simple_task.query, reference_image_url)
                yield f"data: {json.dumps({'event': 'tool_result', 'timestamp': time.time(), 'data': {'tool_name': 'text_to_image', 'tool_type': '默认能力', 'tool_call_id': 'workspace-direct-image-generation', 'ok': True, 'result': result, 'message': '图片已生成'}}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'event': 'final', 'timestamp': time.time(), 'data': {'chunk': result, 'message': result, 'accumulated': result, 'done': True}}, ensure_ascii=False)}\n\n"
            except Exception as err:
                error_text = f'图片生成失败：{err}'
                yield f"data: {json.dumps({'event': 'tool_result', 'timestamp': time.time(), 'data': {'tool_name': 'text_to_image', 'tool_type': '默认能力', 'tool_call_id': 'workspace-direct-image-generation', 'ok': False, 'error': str(err), 'result': error_text, 'message': '图片生成失败'}}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'event': 'final', 'timestamp': time.time(), 'data': {'chunk': error_text, 'message': error_text, 'accumulated': error_text, 'done': True}}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            direct_generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    servers_config = []
    missing_mcp_ids = []
    for mcp_id in simple_task.mcp_servers:
        mcp_server = await MCPService.get_mcp_server_from_id(mcp_id)
        if not mcp_server:
            missing_mcp_ids.append(mcp_id)
            continue
        imported_info = None
        if mcp_server.get("imported_config"):
            imported_info = parse_imported_config(mcp_server["imported_config"])
        servers_config.append(
            MCPConfig(
                server_name=mcp_server.get("server_name", ""),
                mcp_server_id=mcp_server.get("mcp_server_id", ""),
                type=(imported_info.type if imported_info else mcp_server.get("type", "sse")),
                url=(imported_info.url if imported_info else mcp_server.get("url", "")) or "",
                tools=mcp_server.get("tools") or [],
                headers=imported_info.headers if imported_info else None,
                command=imported_info.command if imported_info else None,
                args=(imported_info.args or []) if imported_info else [],
                env=imported_info.env if imported_info else None,
                env_passthrough=(imported_info.env_passthrough or []) if imported_info else [],
                cwd=imported_info.cwd if imported_info else None,
            )
        )

    if missing_mcp_ids:
        logger.warning(f"Workspace request skipped missing MCP ids: {missing_mcp_ids}")
        if not servers_config and simple_task.mcp_servers:
            raise HTTPException(status_code=400, detail="所选 MCP 已失效，请刷新页面后重新选择。")

    db_tools = await ToolService.get_tools_from_id(simple_task.plugins)
    validate_tools_for_mode([tool.to_dict() for tool in db_tools], execution_mode.value)

    simple_agent = WorkSpaceSimpleAgent(
        model_config={
            "model": model_config["model"],
            "base_url": model_config["base_url"],
            "api_key": model_config["api_key"],
            "user_id": login_user.user_id,
        },
        mcp_configs=servers_config,
        plugins=simple_task.plugins,
        knowledge_ids=simple_task.knowledge_ids,
        agent_skill_ids=simple_task.agent_skill_ids,
        enable_web_search=simple_task.web_search,
        user_id=login_user.user_id,
        session_id=simple_task.session_id,
        execution_mode=execution_mode.value,
        access_scope=access_scope.value,
        desktop_bridge_url=simple_task.desktop_bridge_url,
        desktop_bridge_token=simple_task.desktop_bridge_token,
        original_query=simple_task.query,
    )

    workspace_session = await WorkSpaceSessionService.get_workspace_session_from_id(
        simple_task.session_id,
        login_user.user_id,
    )
    if workspace_session:
        contexts = workspace_session.get("contexts", [])
        history_messages = [
            f"query: {message.get('query')}, answer: {message.get('answer')}\n"
            for message in contexts
        ]
    else:
        history_messages = []

    async def general_generate():
        system_message = SYSTEM_PROMPT.format(history=str(history_messages))
        message_query = await build_workspace_attachment_prompt(
            query=simple_task.query,
            attachments=simple_task.attachments,
            workspace_mode=simple_task.workspace_mode,
            session_id=simple_task.session_id,
        )
        try:
            async for chunk in simple_agent.astream(
                [
                    SystemMessage(content=system_message),
                    HumanMessage(content=message_query),
                ]
            ):
                if not isinstance(chunk, dict):
                    chunk = {
                        "event": "status",
                        "timestamp": time.time(),
                        "data": {
                            "status": "END",
                            "phase": "stream",
                            "message": str(chunk),
                        },
                    }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as err:
            error_event = {
                "event": "status",
                "timestamp": time.time(),
                "data": {
                    "status": "ERROR",
                    "phase": "stream",
                    "message": str(err),
                    "error": str(err),
                },
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        general_generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
