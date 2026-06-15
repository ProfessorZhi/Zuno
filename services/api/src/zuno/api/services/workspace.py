from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from fastapi import HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
from starlette.responses import StreamingResponse

from zuno.api.services.agent import AgentService
from zuno.api.services.llm import LLMService
from zuno.api.services.mcp_server import MCPService
from zuno.api.services.tool import ToolService
from zuno.api.services.user import UserPayload
from zuno.api.services.workspace_session import WorkSpaceSessionService
from zuno.database.models.workspace_session import WorkSpaceSessionCreate
from zuno.prompts.completion import SYSTEM_PROMPT
from zuno.schema.schemas import resp_200
from zuno.schema.usage_stats import UsageStatsAgentType
from zuno.schema.workspace import WorkSpaceSimpleTask
from zuno.services.execution_policy import (
    filter_tools_for_mode,
    get_execution_config_payload,
    normalize_access_scope,
    normalize_execution_mode,
    validate_tools_for_mode,
)
from zuno.services.workspace.attachment_service import (
    build_workspace_attachment_prompt,
    classify_attachment,
)
from zuno.tools.text2image.action import _text_to_image
from zuno.utils.contexts import set_agent_name_context, set_user_id_context
from zuno.utils.helpers import parse_imported_config
from zuno.utils.model_output import normalize_model_id_for_provider


class WorkspaceService:
    IMAGE_REGEN_KEYWORDS = [
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

    @staticmethod
    def create_workspace_session_payload(payload, user_id: str) -> WorkSpaceSessionCreate:
        return WorkSpaceSessionCreate(
            title=(payload.title or "New Session").strip() or "New Session",
            agent=payload.agent or "simple",
            user_id=user_id,
            session_id=payload.session_id,
            workspace_mode=payload.workspace_mode,
            contexts=payload.contexts or [],
        )

    @staticmethod
    async def get_workspace_plugins(*, execution_mode: str, access_scope: str, user_id: str):
        _ = normalize_access_scope(access_scope)
        results = await ToolService.get_visible_tool_by_user(user_id)
        return resp_200(data=filter_tools_for_mode(results, execution_mode))

    @staticmethod
    def get_workspace_execution_modes():
        return resp_200(data=get_execution_config_payload())

    @classmethod
    def pick_reference_image_url(cls, simple_task: WorkSpaceSimpleTask) -> str:
        for attachment in simple_task.attachments:
            if classify_attachment(attachment) == "image":
                return attachment.url
        return ""

    @classmethod
    def should_run_direct_image_generation(cls, simple_task: WorkSpaceSimpleTask) -> bool:
        if simple_task.execution_mode != "tool":
            return False
        reference_image_url = cls.pick_reference_image_url(simple_task)
        if not reference_image_url:
            return False
        normalized_query = (simple_task.query or "").lower()
        return any(keyword in normalized_query for keyword in cls.IMAGE_REGEN_KEYWORDS)

    @staticmethod
    async def resolve_workspace_usage_agent_name(
        simple_task: WorkSpaceSimpleTask,
        user_id: str,
        workspace_session: dict | None,
    ) -> str:
        if WorkSpaceSessionService.normalize_workspace_mode(simple_task.workspace_mode) != "agent":
            return UsageStatsAgentType.simple_agent.value

        for candidate in (simple_task.agent_name, (workspace_session or {}).get("agent")):
            agent_name = str(candidate or "").strip()
            if WorkSpaceSessionService.is_real_agent_name(agent_name):
                return agent_name

        agent_id = str(simple_task.agent_id or "").strip()
        if agent_id:
            agent = await AgentService.select_agent_by_id(agent_id)
            if agent and agent.get("user_id") == user_id:
                agent_name = str(agent.get("name") or "").strip()
                if WorkSpaceSessionService.is_real_agent_name(agent_name):
                    return agent_name

        return UsageStatsAgentType.simple_agent.value

    @staticmethod
    async def build_mcp_configs(simple_task: WorkSpaceSimpleTask):
        from zuno.services.workspace.simple_agent import MCPConfig

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
                    config_enabled=bool(mcp_server.get("config_enabled")),
                    config=mcp_server.get("config") or [],
                    headers=imported_info.headers if imported_info else None,
                    command=imported_info.command if imported_info else None,
                    args=(imported_info.args or []) if imported_info else [],
                    env=imported_info.env if imported_info else None,
                    env_passthrough=(imported_info.env_passthrough or []) if imported_info else [],
                    cwd=imported_info.cwd if imported_info else None,
                )
            )
        return servers_config, missing_mcp_ids

    @staticmethod
    async def build_simple_agent(
        *,
        simple_task: WorkSpaceSimpleTask,
        login_user: UserPayload,
        model_config: dict[str, Any],
        usage_agent_name: str,
        servers_config,
    ):
        from zuno.services.workspace.simple_agent import WorkSpaceSimpleAgent

        return WorkSpaceSimpleAgent(
            model_config={
                "model": normalize_model_id_for_provider(
                    model_config.get("model"),
                    provider=model_config.get("provider"),
                    base_url=model_config.get("base_url"),
                ),
                "base_url": model_config["base_url"],
                "api_key": model_config["api_key"],
                "provider": model_config.get("provider"),
                "user_id": login_user.user_id,
            },
            mcp_configs=servers_config,
            plugins=simple_task.plugins,
            knowledge_ids=simple_task.knowledge_ids,
            retrieval_mode=simple_task.retrieval_mode,
            agent_skill_ids=simple_task.agent_skill_ids,
            enable_web_search=simple_task.web_search,
            user_id=login_user.user_id,
            session_id=simple_task.session_id,
            execution_mode=normalize_execution_mode(simple_task.execution_mode).value,
            access_scope=normalize_access_scope(simple_task.access_scope).value,
            desktop_bridge_url=simple_task.desktop_bridge_url,
            desktop_bridge_token=simple_task.desktop_bridge_token,
            original_query=simple_task.query,
            usage_agent_name=usage_agent_name,
            multi_agent_enabled=simple_task.multi_agent_enabled,
        )

    @classmethod
    def build_direct_image_response(cls, simple_task: WorkSpaceSimpleTask) -> StreamingResponse:
        reference_image_url = cls.pick_reference_image_url(simple_task)

        async def direct_generate():
            status_event = {
                "event": "status",
                "timestamp": time.time(),
                "data": {
                    "phase": "start",
                    "status": "START",
                    "message": "Detected an image-regeneration task and routed it to image generation.",
                },
            }
            yield f"data: {json.dumps(status_event, ensure_ascii=False)}\n\n"

            tool_call_event = {
                "event": "tool_call",
                "timestamp": time.time(),
                "data": {
                    "tool_name": "text_to_image",
                    "tool_type": "builtin",
                    "tool_call_id": "workspace-direct-image-generation",
                    "arguments": {
                        "user_prompt": simple_task.query,
                        "reference_image_url": reference_image_url,
                    },
                    "message": "Generating a new image from the uploaded reference image.",
                },
            }
            yield f"data: {json.dumps(tool_call_event, ensure_ascii=False)}\n\n"

            try:
                result = await asyncio.to_thread(_text_to_image, simple_task.query, reference_image_url)
                tool_result_event = {
                    "event": "tool_result",
                    "timestamp": time.time(),
                    "data": {
                        "tool_name": "text_to_image",
                        "tool_type": "builtin",
                        "tool_call_id": "workspace-direct-image-generation",
                        "ok": True,
                        "result": result,
                        "message": "Image generation completed.",
                    },
                }
                yield f"data: {json.dumps(tool_result_event, ensure_ascii=False)}\n\n"
                final_event = {
                    "event": "final",
                    "timestamp": time.time(),
                    "data": {
                        "chunk": result,
                        "message": result,
                        "accumulated": result,
                        "done": True,
                    },
                }
                yield f"data: {json.dumps(final_event, ensure_ascii=False)}\n\n"
            except Exception as err:
                error_text = f"Image generation failed: {err}"
                tool_error_event = {
                    "event": "tool_result",
                    "timestamp": time.time(),
                    "data": {
                        "tool_name": "text_to_image",
                        "tool_type": "builtin",
                        "tool_call_id": "workspace-direct-image-generation",
                        "ok": False,
                        "error": str(err),
                        "result": error_text,
                        "message": "Image generation failed.",
                    },
                }
                yield f"data: {json.dumps(tool_error_event, ensure_ascii=False)}\n\n"
                final_error_event = {
                    "event": "final",
                    "timestamp": time.time(),
                    "data": {
                        "chunk": error_text,
                        "message": error_text,
                        "accumulated": error_text,
                        "done": True,
                    },
                }
                yield f"data: {json.dumps(final_error_event, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            direct_generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @classmethod
    async def workspace_simple_chat_response(
        cls,
        *,
        simple_task: WorkSpaceSimpleTask,
        login_user: UserPayload,
    ) -> StreamingResponse:
        set_user_id_context(login_user.user_id)

        execution_mode = normalize_execution_mode(simple_task.execution_mode)
        access_scope = normalize_access_scope(simple_task.access_scope)
        model_config = await LLMService.get_llm_by_id(simple_task.model_id)
        if not model_config:
            raise HTTPException(status_code=400, detail="Selected model does not exist. Refresh the model list and try again.")

        workspace_session = await WorkSpaceSessionService.get_workspace_session_from_id(
            simple_task.session_id,
            login_user.user_id,
        )
        usage_agent_name = await cls.resolve_workspace_usage_agent_name(
            simple_task,
            login_user.user_id,
            workspace_session,
        )
        set_agent_name_context(usage_agent_name)

        if cls.should_run_direct_image_generation(simple_task):
            return cls.build_direct_image_response(simple_task)

        servers_config, missing_mcp_ids = await cls.build_mcp_configs(simple_task)
        if missing_mcp_ids:
            logger.warning(f"Workspace request skipped missing MCP ids: {missing_mcp_ids}")
            if not servers_config and simple_task.mcp_servers:
                raise HTTPException(status_code=400, detail="Selected MCP servers are no longer available. Refresh and choose them again.")

        db_tools = await ToolService.get_tools_from_id(simple_task.plugins)
        validate_tools_for_mode([tool.to_dict() for tool in db_tools], execution_mode.value)

        simple_agent = await cls.build_simple_agent(
            simple_task=simple_task,
            login_user=login_user,
            model_config=model_config,
            usage_agent_name=usage_agent_name,
            servers_config=servers_config,
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
                start_event = {
                    "event": "status",
                    "timestamp": time.time(),
                    "data": {
                        "phase": "start",
                        "status": "START",
                        "message": "Preparing the workspace request.",
                        "retrieval_mode": simple_task.retrieval_mode,
                        "selected_knowledge_ids": simple_task.knowledge_ids or [],
                    },
                }
                yield f"data: {json.dumps(start_event, ensure_ascii=False)}\n\n"

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


__all__ = ["WorkspaceService"]
