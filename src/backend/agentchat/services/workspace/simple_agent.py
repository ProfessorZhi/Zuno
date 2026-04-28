from __future__ import annotations

import ast
import asyncio
import copy
import json
import re
import time
import uuid
from datetime import date
from types import SimpleNamespace
from typing import Any, AsyncGenerator, Dict, List, NotRequired

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
    ToolCallLimitMiddleware,
)
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool, tool as lc_tool
from langgraph.config import get_stream_writer
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command
from loguru import logger
from pydantic import BaseModel

from agentchat.api.services.mcp_user_config import MCPUserConfigService
from agentchat.api.services.agent_skill import AgentSkillService
from agentchat.api.services.tool import ToolService
from agentchat.api.services.usage_stats import UsageStatsService
from agentchat.api.services.workspace_session import WorkSpaceSessionService
from agentchat.core.callbacks import usage_metadata_callback
from agentchat.core.models.manager import ModelManager
from agentchat.database import AgentSkill
from agentchat.schema.tool import (
    CLIToolPreviewReq,
    RemoteApiAssistReq,
    SimpleApiConfig,
    SimpleApiParamConfig,
)
from agentchat.database.models.workspace_session import (
    WorkSpaceSessionContext,
    WorkSpaceSessionCreate,
)
from agentchat.prompts.completion import GenerateTitlePrompt
from agentchat.schema.usage_stats import UsageStatsAgentType
from agentchat.schema.workspace import WorkSpaceAgents, WorkspaceAgentStreamEvent
from agentchat.services.execution_policy import (
    normalize_access_scope,
    normalize_execution_mode,
)
from agentchat.services.mcp.manager import MCPManager
from agentchat.services.cli_tool_discovery import CliToolDiscoveryService
from agentchat.services.capability_registry import CapabilityRegistryService
from agentchat.services.rag.handler import RagHandler
from agentchat.services.simple_api_tool import (
    build_openapi_schema_from_simple_config,
    build_remote_api_assist_draft,
)
from agentchat.services.structured_tool_result_formatter import format_structured_tool_result
from agentchat.services.tool_creation_service import ToolCreationService
from agentchat.services.user_defined_tool_runtime import (
    build_user_defined_langchain_tools,
    get_user_defined_runtime_type,
)
from agentchat.services.workspace.desktop_bridge_runtime import (
    DesktopBridgeConfig,
    build_terminal_langchain_tools,
)
from agentchat.tools import WorkSpacePlugins
from agentchat.tools.text2image.action import _text_to_image
from agentchat.utils.convert import convert_mcp_config
from agentchat.utils.model_output import (
    extract_visible_text_from_stream,
    is_minimax_model,
    normalize_messages_for_model,
    strip_model_wrapper_from_user_input,
)
from agentchat.utils.runtime_observability import (
    build_langchain_run_config,
    build_langsmith_metadata,
    get_active_trace_id,
)
from agentchat.settings import app_settings

tool = lc_tool


class MCPConfig(BaseModel):
    url: str = ""
    type: str = "sse"
    tools: List[str] = []
    server_name: str
    mcp_server_id: str
    config_enabled: bool = False
    config: List[dict] = []
    headers: dict[str, str] | None = None
    command: str | None = None
    args: List[str] | None = None
    env: dict[str, str] | None = None
    env_passthrough: List[str] | None = None
    cwd: str | None = None


class StreamAgentState(AgentState):
    tool_call_count: NotRequired[int]
    model_call_count: NotRequired[int]
    user_id: NotRequired[str]


class RouteHint(BaseModel):
    kind: str = ""
    target: str = ""
    reason: str = ""


class WorkSpaceSimpleAgent:
    """Workspace ReAct agent with streamed execution events."""

    def __init__(
        self,
        model_config,
        user_id: str,
        session_id: str,
        plugins: List[str] | None = None,
        mcp_configs: List[MCPConfig] | None = None,
        knowledge_ids: List[str] | None = None,
        retrieval_mode: str = "auto",
        agent_skill_ids: List[str] | None = None,
        enable_web_search: bool = True,
        execution_mode: str = "tool",
        access_scope: str = "workspace",
        desktop_bridge_url: str | None = None,
        desktop_bridge_token: str | None = None,
        original_query: str | None = None,
    ):
        self.model_name = model_config.get("model", "")
        self.base_url = model_config.get("base_url", "")
        self.model = ModelManager.get_user_model(**model_config)

        self.plugin_tools = []
        self.mcp_tools = []
        self.knowledge_tools = []
        self.skill_tools = []
        self.terminal_tools = []
        self.tools = []
        self.middlewares = []
        self.tool_metadata_map: Dict[str, Dict[str, str]] = {}

        self.mcp_configs = mcp_configs or []
        self.mcp_manager = MCPManager(
            convert_mcp_config([mcp_config.model_dump() for mcp_config in self.mcp_configs])
        )
        self.plugins = plugins or []
        self.enable_web_search = enable_web_search
        self.knowledge_ids = knowledge_ids or []
        self.retrieval_mode = retrieval_mode
        self.agent_skill_ids = agent_skill_ids or []
        self.available_skills: list[Any] = []
        self.session_id = session_id
        self.execution_mode = normalize_execution_mode(execution_mode).value
        self.access_scope = normalize_access_scope(access_scope).value
        self.user_id = user_id
        self.original_query = original_query
        self.desktop_bridge_config = (
            DesktopBridgeConfig(url=desktop_bridge_url, token=desktop_bridge_token)
            if desktop_bridge_url and desktop_bridge_token
            else None
        )

        self.server_dict: dict[str, Any] = {}
        self.route_hint = self._detect_route_hint(self.original_query)
        self._initialized = False

    def _wrap_event(self, event: str, data: Dict[str, Any]) -> WorkspaceAgentStreamEvent:
        return {
            "event": event,
            "timestamp": time.time(),
            "data": data,
        }

    def _build_run_metadata(self, **extra: Any) -> Dict[str, Any]:
        metadata = build_langsmith_metadata(
            trace_id=get_active_trace_id(),
            user_id=self.user_id,
            session_id=self.session_id,
            retrieval_mode=self.retrieval_mode,
            knowledge_ids=self.knowledge_ids,
            agent_name=UsageStatsAgentType.simple_agent.value,
            execution_mode=self.execution_mode,
            access_scope=self.access_scope,
            route_kind=self.route_hint.kind,
            route_target=self.route_hint.target,
        )
        if extra:
            metadata.update(build_langsmith_metadata(**extra))
        return metadata

    def _build_run_config(
        self,
        *,
        run_name: str,
        tags: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
        callbacks: List[Any] | None = None,
    ) -> Dict[str, Any]:
        return build_langchain_run_config(
            callbacks=callbacks or [usage_metadata_callback],
            run_name=run_name,
            tags=tags or ["workspace", "simple-agent"],
            metadata=self._build_run_metadata(**(metadata or {})),
        )

    @staticmethod
    def _summarize_retrieval_metadata(metadata: Dict[str, Any] | None) -> str:
        if not metadata:
            return "知识库检索已完成。"
        final_mode = str(metadata.get("final_mode") or metadata.get("first_mode") or "rag")
        round_count = int(metadata.get("round_count") or 1)
        fallback_reason = metadata.get("fallback_reason")
        second_pass_used = bool(metadata.get("second_pass_used"))
        rewritten_query_used = bool(metadata.get("rewritten_query_used"))
        parts = [f"知识库检索已完成，最终策略：{final_mode}，共 {round_count} 轮。"]
        if second_pass_used and fallback_reason:
            parts.append(f"首轮触发补检，原因：{fallback_reason}。")
        if rewritten_query_used:
            parts.append("本轮已启用改写后的问题再次补检。")
        return "".join(parts)

    def _build_retrieval_event_payload(self, result: Dict[str, Any], phase: str = "retrieval") -> Dict[str, Any]:
        metadata = result.get("metadata") or {}
        return {
            "phase": phase,
            "status": "END",
            "message": self._summarize_retrieval_metadata(metadata),
            "retrieval_mode": result.get("actual_mode") or metadata.get("final_mode") or self.retrieval_mode,
            "first_mode": result.get("first_mode") or metadata.get("first_mode"),
            "final_mode": result.get("final_mode") or metadata.get("final_mode"),
            "fallback_reason": result.get("fallback_reason") or metadata.get("fallback_reason"),
            "round_count": result.get("round_count") or metadata.get("round_count") or 1,
            "second_pass_used": result.get("second_pass_used") or metadata.get("second_pass_used") or False,
            "rewritten_query_used": metadata.get("rewritten_query_used") or False,
            "query_variants": metadata.get("query_variants") or [],
            "rounds": metadata.get("rounds") or [],
            "knowledge_ids": self.knowledge_ids,
        }

    @staticmethod
    def _norm(text: str | None) -> str:
        return (text or "").strip().lower()

    @staticmethod
    def _extract_labeled_value(query: str, labels: list[str]) -> str:
        for label in labels:
            pattern = rf"{label}\s*[:：]\s*(.+)"
            match = re.search(pattern, query, flags=re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                value = re.split(r"[\r\n]", value, maxsplit=1)[0].strip()
                return value.strip(" 。；;")
        return ""

    @staticmethod
    def _extract_tool_display_name(query: str) -> str:
        patterns = [
            r"(?:名称|名字)\s*(?:叫|是|为)?\s*([A-Za-z0-9_\-\u4e00-\u9fff]+)",
            r"新增(?:一个)?\s*(?:API|CLI)?\s*工具[，, ]*(?:名称)?(?:叫|是|为)\s*([A-Za-z0-9_\-\u4e00-\u9fff]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, query, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip(" 。；;,，")
        return ""

    @staticmethod
    def _parse_auth_type(raw: str) -> str:
        value = (raw or "").strip().lower()
        if not value or any(token in value for token in ["无认证", "none", "no auth", "noauth"]):
            return "none"
        if "bearer" in value:
            return "bearer"
        if "basic" in value:
            return "basic"
        if "query" in value or "参数" in value:
            return "api_key_query"
        if "header" in value or "请求头" in value:
            return "api_key_header"
        return "none"

    @staticmethod
    def _build_simple_api_schema_json(
        display_name: str,
        description: str,
        base_url: str,
        path: str,
        method: str,
        query: str,
    ) -> str:
        params: list[dict[str, Any]] = []
        path_tokens = re.findall(r"{([^{}]+)}", path or "")
        for token in path_tokens:
            name = token.strip()
            if name:
                params.append(
                    {
                        "name": name,
                        "in": "path",
                        "required": True,
                        "description": f"Path parameter: {name}",
                        "type": "string",
                    }
                )

        query_param_patterns = [
            r"必填\s*query\s*参数\s*([A-Za-z0-9_]+)",
            r"需要(?:一个)?必填\s*query\s*参数\s*([A-Za-z0-9_]+)",
            r"query\s*参数\s*([A-Za-z0-9_]+)",
            r"参数\s*([A-Za-z0-9_]+)",
        ]
        seen_query_params = set()
        for pattern in query_param_patterns:
            for match in re.finditer(pattern, query, flags=re.IGNORECASE):
                name = match.group(1).strip()
                if not name or name in seen_query_params:
                    continue
                seen_query_params.add(name)
                required = "必填" in query[max(0, match.start() - 8): match.end() + 8]
                params.append(
                    {
                        "name": name,
                        "in": "query",
                        "required": required,
                        "description": f"Query parameter: {name}",
                        "type": "string",
                    }
                )

        simple_api_config = SimpleApiConfig(
            base_url=base_url,
            path=path,
            method=method,
            operation_id=re.sub(r"[^a-zA-Z0-9_]+", "_", display_name).strip("_") or "call_api",
            summary=display_name,
            description=description or f"Call {path}",
            params=[
                SimpleApiParamConfig(
                    name=param["name"],
                    **{"in": param["in"]},
                    required=param["required"],
                    description=param["description"],
                    type=param["type"],
                )
                for param in params
            ],
            body_schema=None,
            response_schema=None,
        )
        return json.dumps(build_openapi_schema_from_simple_config(simple_api_config), ensure_ascii=False)

    @staticmethod
    def _extract_first_url(text: str) -> str:
        match = re.search(r"https?://[^\s'\"<>]+", text or "")
        return match.group(0).rstrip(".,);") if match else ""

    @staticmethod
    def _extract_all_urls(text: str) -> list[str]:
        urls: list[str] = []
        seen: set[str] = set()
        for candidate in re.findall(r"https?://[^\s'\"<>]+", text or ""):
            normalized = candidate.rstrip(".,);")
            if normalized and normalized not in seen:
                seen.add(normalized)
                urls.append(normalized)
        return urls

    @staticmethod
    def _extract_windows_path(text: str) -> str:
        match = re.search(r"[A-Za-z]:\\[^\r\n]+", text or "")
        return match.group(0).strip().rstrip("。；;,，") if match else ""

    @staticmethod
    def _merge_tool_creation_payload(base: dict[str, Any] | None, updates: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base or {})
        for key, value in updates.items():
            if value in (None, "", [], {}):
                continue
            if key == "docs_urls":
                existing = [str(item).strip() for item in (merged.get(key) or []) if str(item).strip()]
                incoming = [str(item).strip() for item in (value or []) if str(item).strip()]
                seen: set[str] = set()
                merged[key] = [item for item in [*existing, *incoming] if not (item in seen or seen.add(item))]
                continue
            if key == "docs_url" and str(merged.get("docs_url") or "").strip():
                continue
            merged[key] = value
        if merged.get("docs_urls") and not merged.get("docs_url"):
            merged["docs_url"] = merged["docs_urls"][0]
        return merged

    def _detect_tool_creation_kind(self, query: str, pending_kind: str = "") -> str:
        lowered = (query or "").lower()
        if any(token in lowered for token in ["api工具", "api 工具", "远程 api", "远程api", "openapi"]):
            return "api"
        if any(token in lowered for token in ["cli工具", "cli 工具", "命令行工具", "本地工具"]):
            return "cli"
        return pending_kind

    def _extract_api_tool_creation_payload(
        self,
        query: str,
        base_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = (query or "").strip()
        first_url = self._extract_first_url(text)
        all_urls = self._extract_all_urls(text)
        looks_like_docs = any(token in text.lower() for token in ["文档", "docs", "documentation", "swagger", "openapi", "postman"])
        sample_curl = self._extract_labeled_value(text, ["curl", "curl 示例", "curl命令", "curl command"]) or (
            text if "curl " in text.lower() else ""
        )
        labeled_docs = self._extract_labeled_value(text, ["文档地址", "docs", "docs url"])
        docs_urls = []
        if labeled_docs:
            docs_urls = self._extract_all_urls(labeled_docs)
        if looks_like_docs:
            for url in all_urls:
                if url not in docs_urls:
                    docs_urls.append(url)
        payload = {
            "display_name": self._extract_tool_display_name(text),
            "description": self._extract_labeled_value(text, ["用途", "描述", "说明"]) or "由 Agent 聊天创建的工具",
            "base_url": self._extract_labeled_value(text, ["Base URL", "base url", "base_url", "服务器地址"]),
            "endpoint_url": self._extract_labeled_value(text, ["Endpoint URL", "endpoint", "接口地址", "URL"]),
            "path": self._extract_labeled_value(text, ["Path", "路径"]),
            "method": (self._extract_labeled_value(text, ["Method", "请求方法"]) or "GET").upper(),
            "auth_type": self._parse_auth_type(self._extract_labeled_value(text, ["认证", "认证方式", "auth", "auth type"])),
            "api_key": self._extract_labeled_value(text, ["API Key", "api_key", "access_key", "token", "密钥"]),
            "api_key_name": self._extract_labeled_value(text, ["API Key Name", "api key name", "密钥字段", "参数名", "header 名"]),
            "docs_url": docs_urls[0] if docs_urls else labeled_docs,
            "docs_urls": docs_urls,
            "logo_url": self._extract_labeled_value(text, ["图标", "logo", "logo url", "icon"]),
            "sample_curl": sample_curl,
            "openapi_schema_json": "",
        }
        if first_url:
            if looks_like_docs and not payload["docs_url"]:
                payload["docs_url"] = first_url
                payload["docs_urls"] = [first_url]
            elif not payload["endpoint_url"]:
                payload["endpoint_url"] = first_url
        merged = self._merge_tool_creation_payload(base_payload, payload)
        if merged.get("endpoint_url") and merged.get("docs_urls") and merged["endpoint_url"] in set(merged["docs_urls"]):
            merged["endpoint_url"] = ""
        if not merged.get("endpoint_url") and merged.get("base_url") and merged.get("path"):
            merged["endpoint_url"] = f"{merged['base_url'].rstrip('/')}/{str(merged['path']).lstrip('/')}"
        if merged.get("base_url") and merged.get("path"):
            merged["openapi_schema_json"] = self._build_simple_api_schema_json(
                display_name=merged.get("display_name") or "call_api",
                description=merged.get("description") or "由 Agent 聊天创建的工具",
                base_url=merged["base_url"],
                path=merged["path"],
                method=merged.get("method") or "GET",
                query=text,
            )
        return merged

    def _extract_cli_tool_creation_payload(
        self,
        query: str,
        base_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = (query or "").strip()
        first_url = self._extract_first_url(text)
        first_path = self._extract_windows_path(text)
        payload = {
            "display_name": self._extract_tool_display_name(text),
            "description": self._extract_labeled_value(text, ["用途", "描述", "说明"]) or "由 Agent 聊天创建的工具",
            "command": self._extract_labeled_value(text, ["命令", "command", "运行命令", "启动命令"]),
            "tool_dir": self._extract_labeled_value(text, ["工具目录", "tool_dir", "tool dir"]),
            "source_type": self._extract_labeled_value(text, ["来源类型", "source_type"]) or "",
            "install_source": self._extract_labeled_value(text, ["安装来源", "install_source", "安装地址"]),
            "install_command": self._extract_labeled_value(text, ["安装命令", "install command"]),
            "healthcheck_command": self._extract_labeled_value(text, ["健康检查", "healthcheck", "healthcheck command"]),
            "cwd": self._extract_labeled_value(text, ["工作目录", "cwd"]),
            "local_path": self._extract_labeled_value(text, ["本地目录", "本地路径", "local path"]),
            "github_url": self._extract_labeled_value(text, ["GitHub", "github", "仓库地址"]),
            "docs_url": self._extract_labeled_value(text, ["文档地址", "docs", "docs url"]),
            "logo_url": self._extract_labeled_value(text, ["图标", "logo", "logo url", "icon"]),
            "args_template": "",
            "credential_mode": "none",
            "cwd_mode": "tool_dir",
            "timeout_ms": 30000,
            "notes": "",
        }
        if first_url:
            if "github.com" in first_url.lower() and not payload["github_url"]:
                payload["github_url"] = first_url
            elif not payload["docs_url"]:
                payload["docs_url"] = first_url
        if first_path and not payload["local_path"]:
            payload["local_path"] = first_path
        merged = self._merge_tool_creation_payload(base_payload, payload)
        if not merged.get("source_type"):
            if merged.get("github_url"):
                merged["source_type"] = "github_repo"
            elif merged.get("local_path") or merged.get("tool_dir"):
                merged["source_type"] = "local_directory"
            else:
                merged["source_type"] = "local_directory"
        return merged

    def _parse_direct_tool_creation_request(
        self,
        query: str,
        *,
        base_payload: dict[str, Any] | None = None,
        pending_kind: str = "",
    ) -> tuple[BaseTool | None, dict[str, Any], str]:
        text = (query or "").strip()
        kind = self._detect_tool_creation_kind(text, pending_kind=pending_kind)
        is_explicit_creation = ("新增" in text and "工具" in text) or ("创建" in text and "工具" in text)
        if not kind or (not is_explicit_creation and not pending_kind):
            return None, {}, ""

        if kind == "api":
            tool = next((tool for tool in self.plugin_tools if tool.name == "create_remote_api_tool"), None)
            return tool, self._extract_api_tool_creation_payload(text, base_payload=base_payload), kind

        if kind == "cli":
            tool = next((tool for tool in self.plugin_tools if tool.name == "create_cli_tool"), None)
            return tool, self._extract_cli_tool_creation_payload(text, base_payload=base_payload), kind
        return None, {}, ""

    def _parse_direct_named_tool_invocation(self, query: str) -> tuple[BaseTool | None, dict[str, Any]]:
        text = (query or "").strip()
        if "调用名为" not in text or "工具" not in text:
            return None, {}

        target = ""
        name_match = re.search(r"调用名为\s*([A-Za-z0-9_\-\u4e00-\u9fff]+)\s*的", text)
        if name_match:
            target = name_match.group(1).strip()
        if not target:
            return None, {}

        matched_tool = None
        for tool in self.plugin_tools:
            tool_type, display_name = self._tool_display_info(tool.name)
            if self._norm(display_name) == self._norm(target) or self._norm(tool.name) == self._norm(target):
                matched_tool = tool
                matched_tool_type = tool_type
                break
        if not matched_tool:
            return None, {}

        if "CLI" in text or matched_tool_type == "CLI 工具":
            input_value = self._extract_labeled_value(text, ["输入", "input", "参数"]) or ""
            if "=" in input_value:
                input_value = input_value.split("=", 1)[1].strip()
            input_value = input_value.strip(" 。；;,，")
            return matched_tool, {"input": input_value or text}

        args: dict[str, Any] = {}
        for match in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s，。；;]+)", text):
            args[match.group(1)] = match.group(2).strip()
        if not args:
            input_value = self._extract_labeled_value(text, ["参数", "query", "输入", "text"])
            if input_value:
                args["text"] = input_value.split("=", 1)[-1].strip(" 。；;,，")
        return matched_tool, args

    @staticmethod
    def _is_tool_creation_cancel(query: str) -> bool:
        lowered = (query or "").strip().lower()
        if not lowered:
            return False
        cancel_tokens = ["取消", "算了", "不用了", "不创建了", "放弃", "stop", "cancel", "never mind"]
        return any(token in lowered for token in cancel_tokens)

    async def _get_pending_tool_creation_state(self) -> dict[str, Any] | None:
        try:
            session = await WorkSpaceSessionService.get_workspace_session_from_id(self.session_id, self.user_id)
        except Exception as err:
            logger.warning(f"workspace tool creation state lookup failed: {err}")
            return None
        if not session:
            return None
        for context in reversed(session.get("contexts", []) or []):
            metadata = context.get("metadata") or {}
            if "tool_creation_state" in metadata:
                state = metadata.get("tool_creation_state")
                return state if isinstance(state, dict) else None
        return None

    def _build_tool_creation_missing_message(self, kind: str, payload: dict[str, Any]) -> str:
        if kind == "api":
            missing: list[str] = []
            if not payload.get("display_name"):
                missing.append("工具名称")
            if not any([payload.get("endpoint_url"), payload.get("docs_url"), payload.get("sample_curl")]):
                missing.append("接口地址、文档地址或 curl 示例")
            if missing:
                return "要继续创建 API 工具，我还缺这些信息：" + "、".join(missing) + "。"
            return (
                "我已经识别到这是一个 API 工具。"
                "如果你还有 API Key、认证字段名或图标，也可以继续补给我；"
                "如果没有，我会先按当前信息创建。"
            )

        missing = []
        if not payload.get("display_name"):
            missing.append("工具名称")
        if not any([
            payload.get("command"),
            payload.get("tool_dir"),
            payload.get("local_path"),
            payload.get("github_url"),
            payload.get("docs_url"),
            payload.get("install_source"),
        ]):
            missing.append("本地目录、GitHub 地址、文档地址、安装来源或启动命令")
        if missing:
            return "要继续创建 CLI 工具，我还缺这些信息：" + "、".join(missing) + "。"
        return (
            "我已经识别到这是一个 CLI 工具。"
            "如果你还有安装命令、健康检查命令、凭证或图标，也可以继续补给我；"
            "如果没有，我会先按当前信息创建。"
        )

    async def _plan_tool_creation_flow(self, query: str) -> dict[str, Any] | None:
        pending_state = await self._get_pending_tool_creation_state()
        pending_kind = str((pending_state or {}).get("kind") or "").strip()
        pending_payload = copy.deepcopy((pending_state or {}).get("payload") or {})
        tool, payload, kind = self._parse_direct_tool_creation_request(
            query,
            base_payload=pending_payload,
            pending_kind=pending_kind,
        )
        if not kind and any(token in (query or "") for token in ["新增工具", "新增 工具", "创建工具", "创建 工具"]):
            return {
                "mode": "ask",
                "kind": "",
                "payload": pending_payload,
                "reply": "我可以帮你接成 API 工具或 CLI 工具。先告诉我这是 API 还是 CLI；如果是 API，给我接口地址或文档地址；如果是 CLI，给我本地目录、GitHub 地址或启动命令。",
            }
        if not kind:
            return None

        if pending_state and self._is_tool_creation_cancel(query):
            return {
                "mode": "cancel",
                "reply": "好的，这次新增工具我先取消。后面你重新说“新增 API 工具”或“新增 CLI 工具”就会重新开始。",
            }

        if kind == "api":
            if not payload.get("display_name") or not any([payload.get("endpoint_url"), payload.get("docs_url"), payload.get("sample_curl")]):
                return {
                    "mode": "ask",
                    "kind": kind,
                    "payload": payload,
                    "reply": self._build_tool_creation_missing_message(kind, payload),
                }
            try:
                assist_result = build_remote_api_assist_draft(
                    RemoteApiAssistReq(
                        endpoint_url=payload.get("endpoint_url") or "",
                        docs_url=payload.get("docs_url") or "",
                        docs_urls=payload.get("docs_urls") or [],
                        sample_curl=payload.get("sample_curl") or "",
                        api_key=payload.get("api_key") or "",
                        api_key_name=payload.get("api_key_name") or "",
                        auth_type=payload.get("auth_type") or "none",
                        method=payload.get("method") or "GET",
                        display_name=payload.get("display_name") or "",
                        description=payload.get("description") or "",
                    )
                )
                payload["base_url"] = assist_result.simple_api_config.base_url
                payload["path"] = assist_result.simple_api_config.path
                payload["endpoint_url"] = (
                    f"{assist_result.simple_api_config.base_url.rstrip('/')}/{assist_result.simple_api_config.path.lstrip('/')}"
                    if assist_result.simple_api_config.base_url and assist_result.simple_api_config.path
                    else payload.get("endpoint_url", "")
                )
                payload["method"] = assist_result.simple_api_config.method
                payload["display_name"] = payload.get("display_name") or assist_result.display_name
                payload["description"] = payload.get("description") or assist_result.description
                payload["openapi_schema_json"] = json.dumps(assist_result.openapi_schema, ensure_ascii=False)
                if assist_result.auth_config.get("auth_type") == "APIKey":
                    payload["auth_type"] = (
                        "api_key_query" if assist_result.auth_config.get("in") == "query" else "api_key_header"
                    )
                    payload["api_key_name"] = assist_result.auth_config.get("name") or payload.get("api_key_name") or ""
                elif assist_result.auth_config.get("auth_type") == "Bearer":
                    payload["auth_type"] = "bearer"
                elif assist_result.auth_config.get("auth_type") == "Basic":
                    payload["auth_type"] = "basic"
                if assist_result.auth_config.get("auth_type") == "APIKey" and not payload.get("api_key"):
                    auth_name = assist_result.auth_config.get("name") or payload.get("api_key_name") or "API Key"
                    payload["api_key_name"] = auth_name
                    return {
                        "mode": "ask",
                        "kind": kind,
                        "payload": payload,
                        "reply": (
                            f"我已经根据文档识别出了 API 结构，下一步还缺凭证。"
                            f"请把 {auth_name} 发给我；如果还有图标，也可以一起给我。"
                        ),
                    }
            except Exception as err:
                return {
                    "mode": "ask",
                    "kind": kind,
                    "payload": payload,
                    "reply": f"我已经识别到这是 API 工具，但当前文档分析还不够完整：{err}。请继续补接口地址、curl 或更明确的文档链接。",
                }
        else:
            if not payload.get("display_name") or not any([
                payload.get("command"),
                payload.get("tool_dir"),
                payload.get("local_path"),
                payload.get("github_url"),
                payload.get("docs_url"),
                payload.get("install_source"),
            ]):
                return {
                    "mode": "ask",
                    "kind": kind,
                    "payload": payload,
                    "reply": self._build_tool_creation_missing_message(kind, payload),
                }

        if not tool:
            return None
        return {"mode": "create", "kind": kind, "tool": tool, "payload": payload}

    def _tools_for_route(self) -> list[BaseTool] | None:
        if not self.route_hint.kind:
            return None
        if self.route_hint.kind == "knowledge":
            return self.knowledge_tools or None
        if self.route_hint.kind == "skill":
            if not self.route_hint.target:
                return self.skill_tools or None
            matched = [
                tool for tool in self.skill_tools
                if self._matches_target(tool.name, self.route_hint.target)
                or self._matches_target(self._tool_display_info(tool.name)[1], self.route_hint.target)
            ]
            return matched or self.skill_tools or None
        if self.route_hint.kind == "terminal":
            return self.terminal_tools or None
        if self.route_hint.kind == "mcp":
            matched_tool_names: set[str] = set()
            for server_name, tool_names in self.server_dict.items():
                if self._matches_target(server_name, self.route_hint.target):
                    matched_tool_names.update(tool_names)
            matched = [
                tool for tool in self.mcp_tools
                if tool.name in matched_tool_names
                or self._matches_target(tool.name, self.route_hint.target)
                or self._matches_target(self._tool_display_info(tool.name)[1], self.route_hint.target)
            ]
            return matched or self.mcp_tools or None
        return None

    def _strip_route_command(self, query: str) -> str:
        text = (query or "").strip()
        slash = re.match(r"^/([a-zA-Z0-9_\-\u4e00-\u9fff]+)(?:\s+(.+))?$", text)
        if not slash:
            return text
        return (slash.group(2) or "").strip()


    def _find_route_tool(self, *tool_names: str) -> BaseTool | None:
        candidates = {name for name in tool_names if name}
        for tool in self._tools_for_route() or []:
            if tool.name in candidates:
                return tool
        return None

    @staticmethod
    def _skill_value(skill: Any, key: str, default: str = "") -> str:
        if isinstance(skill, dict):
            return str(skill.get(key) or default)
        return str(getattr(skill, key, default) or default)

    def _build_skill_catalog_text(self) -> str:
        if self.execution_mode == "terminal" or not self.available_skills:
            return ""

        selected_ids = set(self.agent_skill_ids)
        lines: list[str] = []
        for skill in self.available_skills:
            skill_id = self._skill_value(skill, "id")
            name = self._skill_value(skill, "name")
            description = self._skill_value(skill, "description", "暂无描述")
            tool_name = self._skill_value(skill, "as_tool_name")
            status = "已启用" if skill_id in selected_ids else "可按需启用"
            lines.append(f"- /{name} ({tool_name}) [{status}]: {description}")

        return (
            "当前可用 Skill 目录:\n"
            + "\n".join(lines)
            + "\n使用规则: Skill 是当前单 Agent 的方法包，不是子 Agent。"
            "未启用的 Skill 只作为目录供你推荐；用户输入 /SkillName 或已在设置中勾选后，"
            "你才能调用对应 Skill 工具加载完整说明。"
        )

    def _match_available_skill(self, raw_name: str | None) -> Any | None:
        target = self._norm(raw_name)
        if not target:
            return None
        for skill in self.available_skills:
            candidates = {
                self._norm(self._skill_value(skill, "id")),
                self._norm(self._skill_value(skill, "name")),
                self._norm(self._skill_value(skill, "as_tool_name")),
            }
            if target in candidates:
                return skill
        return None

    async def setup_available_skill_catalog(self):
        if self.execution_mode == "terminal":
            self.available_skills = []
            return
        try:
            self.available_skills = await AgentSkillService.get_agent_skills(self.user_id)
        except Exception as err:
            logger.error(f"Failed to load skill catalog: {err}")
            self.available_skills = []

    def _enable_explicit_slash_skill(self):
        text = (self.original_query or "").strip()
        slash = re.match(r"^/([a-zA-Z0-9_\-\u4e00-\u9fff]+)(?:\s+(.+))?$", text)
        if not slash:
            return

        skill = self._match_available_skill(slash.group(1))
        if not skill:
            return

        skill_id = self._skill_value(skill, "id")
        skill_name = self._skill_value(skill, "name")
        if skill_id and skill_id not in self.agent_skill_ids:
            self.agent_skill_ids.append(skill_id)
        self.route_hint = RouteHint(
            kind="skill",
            target=skill_name,
            reason=f"用户显式输入 /{slash.group(1)}",
        )

    def _build_enabled_capabilities_text(self) -> str:
        sections: list[str] = []

        if self.execution_mode == "terminal":
            terminal_lines = []
            for tool in self.terminal_tools:
                tool_type, display_name = self._tool_display_info(tool.name)
                terminal_lines.append(f"- {display_name} ({tool.name}, {tool_type})")
            if terminal_lines:
                sections.append("当前可用终端能力:\n" + "\n".join(terminal_lines))
        else:
            plugin_lines = []
            for tool in self.plugin_tools:
                tool_type, display_name = self._tool_display_info(tool.name)
                plugin_lines.append(f"- {display_name} ({tool.name}, {tool_type})")
            if plugin_lines:
                sections.append("当前可用内置能力:\n" + "\n".join(plugin_lines))

            mcp_lines = []
            for tool in self.mcp_tools:
                tool_type, display_name = self._tool_display_info(tool.name)
                mcp_lines.append(f"- {display_name} ({tool.name}, {tool_type})")
            if mcp_lines:
                sections.append("当前可用 MCP 能力:\n" + "\n".join(mcp_lines))

        if self.execution_mode != "terminal":
            knowledge_lines = []
            for tool in self.knowledge_tools:
                tool_type, display_name = self._tool_display_info(tool.name)
                knowledge_lines.append(f"- {display_name} ({tool.name}, {tool_type})")
            if knowledge_lines:
                sections.append("当前可用知识库能力:\n" + "\n".join(knowledge_lines))

            skill_lines = []
            for tool in self.skill_tools:
                tool_type, display_name = self._tool_display_info(tool.name)
                skill_lines.append(f"- {display_name} ({tool.name}, {tool_type})")
            if skill_lines:
                sections.append("当前可用 Skill:\n" + "\n".join(skill_lines))

        if self.server_dict:
            sections.append(
                "当前 MCP 服务映射:\n"
                + "\n".join(f"- {server}: {', '.join(tool_names)}" for server, tool_names in self.server_dict.items())
            )
        if self.route_hint.kind:
            sections.append(f"本轮显式路由: {self.route_hint.kind} / {self.route_hint.target or 'auto'}，原因：{self.route_hint.reason}")

        return "\n\n".join(sections)

    async def init_simple_agent(self):
        if self._initialized:
            return

        await self.setup_available_skill_catalog()
        self._enable_explicit_slash_skill()
        await self.setup_terminal_tools()
        await self.setup_mcp_tools()
        await self.setup_plugin_tools()
        await self.setup_knowledge_tools()
        await self.setup_skill_tools()
        logger.info(
            f"workspace agent capabilities initialized: execution_mode={self.execution_mode} "
            f"plugins={[tool.name for tool in self.plugin_tools]} "
            f"mcp_tools={[tool.name for tool in self.mcp_tools]} "
            f"knowledge_tools={[tool.name for tool in self.knowledge_tools]} "
            f"skill_tools={[tool.name for tool in self.skill_tools]} "
            f"route_hint={self.route_hint.model_dump()}"
        )
        self.middlewares = await self.setup_middlewares()
        if self.execution_mode == "terminal":
            self.tools = self.terminal_tools
        else:
            self.tools = self.plugin_tools + self.mcp_tools + self.knowledge_tools + self.skill_tools
        self.react_agent = self.setup_react_agent()
        self._initialized = True

    def _build_runtime_system_prompt(self) -> str:
        if self.execution_mode == "terminal":
            rules = [
                "You are working in Zuno Desktop terminal mode.",
                "When local files, folders, search, writing, or command execution are involved, use tools instead of pretending the work is done.",
                "Prefer safer tools first: search and read before write; execute commands only when needed.",
                "In the final answer, clearly state what you actually did, which tools you used, and which paths were affected.",
            ]
            if self.access_scope == "workspace":
                rules.append("Access is restricted to the workspace. Do not try to access paths outside it.")
            else:
                rules.append("Access scope is unrestricted, but still avoid unnecessary high-risk commands.")
            capability_text = self._build_enabled_capabilities_text()
            if capability_text:
                rules.append(capability_text)
            return "\n".join(rules)

        explicit_command = (self.original_query or "").strip().startswith("/")
        rules = [
            "You are working in Zuno Workspace Agent mode.",
            "Use enabled tools or MCP when external capability is needed. Never fake tool results.",
            "When the user asks for a capability that may exist but is not obviously enabled, call search_available_capabilities before saying it is unavailable.",
            "If the user explicitly asks to use a Skill, a knowledge base, MCP, terminal, or a specific tool, prefer the matching capability instead of a generic answer.",
            "If the user asks to search project materials, a knowledge base, a document library, or RAG content, prefer search_knowledge_base when available.",
            "Before sending email, if sender_slot is not specified, call list_email_accounts first.",
            "If a configuration cannot be found, say it cannot be found. Do not invent slot names or settings.",
            "If the user explicitly says to use Feishu, Lark, Amap, Gaode, Bing, or Bing MCP, prefer the matching enabled MCP tool instead of generic web search.",
            "When the user asks to generate an image, make a poster, cover, logo, visual mockup, or redraw a design, prefer calling text_to_image.",
            "When the user uploads an image and asks to understand it, use the attachment extraction result directly. Do not deny image understanding ability.",
            "When the user uploads an image and asks to recolor it, change background, restyle it, or regenerate a version of it, prefer calling text_to_image with reference_image_url.",
            "Do not answer with generic capability disclaimers when the required tool is available.",
            "Final answers must be grounded in actual tool results, not speculation.",
        ]
        if not explicit_command:
            rules.insert(2, "When the user asks what tools, MCPs, email slots, configurations, or accounts are available, call the relevant read-only tool first, then answer.")
            rules.insert(3, "Before claiming that a capability is unavailable, first call list_enabled_capabilities to verify the actual enabled tools and MCPs in this session.")
        route_tools = self._tools_for_route() or []
        if self.route_hint.kind:
            route_tool_names = ", ".join(tool.name for tool in route_tools) or "none"
            route_target = self.route_hint.target or self.route_hint.kind
            rules.extend(
                [
                    f"The user has explicitly routed this request to {self.route_hint.kind}: {route_target}.",
                    f"Allowed priority tools for this request: {route_tool_names}.",
                    "For this request, do not stop at describing available capabilities.",
                    "You must call a matching routed capability first when one is available, then answer from the real result.",
                ]
            )
        capability_text = self._build_enabled_capabilities_text()
        if capability_text:
            rules.append(capability_text)
        return "\n".join(rules)

    def setup_react_agent(self):
        return create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self._build_runtime_system_prompt(),
            middleware=self.middlewares,
            state_schema=StreamAgentState,
        )

    async def setup_middlewares(self):
        agent = self

        class WorkspaceReactMiddleware(AgentMiddleware):
            async def awrap_model_call(
                self,
                request: ModelRequest,
                handler: Any,
            ) -> ModelResponse:
                writer = get_stream_writer()
                model_call_count = request.state.get("model_call_count", 0) + 1
                route_tools = agent._tools_for_route()
                explicit_slash_skill = (
                    (agent.original_query or "").strip().startswith("/")
                    and agent.route_hint.kind == "skill"
                )
                if route_tools and not explicit_slash_skill:
                    allowed_names = {tool.name for tool in route_tools}
                    include_support_tool = not (agent.original_query or "").strip().startswith("/")
                    support_tools = [tool for tool in agent.tools if include_support_tool and tool.name in {"list_enabled_capabilities"}]
                    request.tools = support_tools + [tool for tool in request.tools if tool.name in allowed_names]
                    writer(
                        agent._wrap_event(
                            "status",
                            {
                                "phase": "route",
                                "status": "START",
                                "message": f"已按用户意图优先使用 {agent.route_hint.kind} 能力",
                                "route": agent.route_hint.model_dump(),
                                "tool_names": [tool.name for tool in request.tools],
                            },
                        )
                    )
                writer(
                    agent._wrap_event(
                        "status",
                        {
                            "phase": "model_call",
                            "status": "START",
                            "message": f"正在进行第 {model_call_count} 轮 ReAct 推理",
                        },
                    )
                )

                response = await handler(request)

                tool_call_names: list[str] = []
                if getattr(response, "tool_calls", None):
                    tool_call_names = sorted({tool_call["name"] for tool_call in response.tool_calls})
                    message = f"模型决定调用工具: {', '.join(tool_call_names)}"
                else:
                    message = "模型准备输出最终答案"

                writer(
                    agent._wrap_event(
                        "status",
                        {
                            "phase": "model_call",
                            "status": "END",
                            "message": message,
                            "tool_names": tool_call_names,
                        },
                    )
                )
                request.state["model_call_count"] = model_call_count
                return response

            async def awrap_tool_call(
                self,
                request: ToolCallRequest,
                handler,
            ) -> ToolMessage | Command:
                writer = get_stream_writer()
                tool_name = request.tool_call["name"]
                tool_type, display_name = agent._tool_display_info(tool_name)
                tool_call_id = request.tool_call["id"]
                tool_args = dict(request.tool_call.get("args") or {})

                writer(
                    agent._wrap_event(
                        "tool_call",
                        {
                            "tool_name": tool_name,
                            "tool_type": tool_type,
                            "tool_call_id": tool_call_id,
                            "arguments": tool_args,
                            "message": f"正在调用 {tool_type}: {display_name}",
                        },
                    )
                )

                if agent.is_mcp_tool(tool_name) and agent.mcp_requires_user_config(tool_name):
                    try:
                        mcp_config = await MCPUserConfigService.get_mcp_user_config(
                            agent.user_id,
                            agent.get_mcp_id_by_tool(tool_name),
                        )
                        request.tool_call["args"].update(mcp_config)
                    except Exception as err:
                        error_text = str(err)
                        writer(
                            agent._wrap_event(
                                "tool_result",
                                {
                                    "tool_name": tool_name,
                                    "tool_type": tool_type,
                                    "tool_call_id": tool_call_id,
                                    "ok": False,
                                    "error": error_text,
                                    "result": error_text,
                                    "message": f"{display_name} 配置读取失败",
                                },
                            )
                        )
                        return ToolMessage(
                            content=error_text,
                            name=tool_name,
                            tool_call_id=tool_call_id,
                        )

                try:
                    tool_result = await handler(request)
                    raw_result = getattr(tool_result, "content", tool_result)
                    result_text = agent._format_tool_result_for_model(raw_result)
                    if isinstance(tool_result, ToolMessage) and result_text != tool_result.content:
                        tool_result = tool_result.model_copy(update={"content": result_text})
                    writer(
                        agent._wrap_event(
                            "tool_result",
                            {
                                "tool_name": tool_name,
                                "tool_type": tool_type,
                                "tool_call_id": tool_call_id,
                                "ok": True,
                                "result": result_text,
                                "message": f"{display_name} 执行完成",
                            },
                        )
                    )
                    request.state["tool_call_count"] = request.state.get("tool_call_count", 0) + 1
                    return tool_result
                except Exception as err:
                    error_text = str(err)
                    writer(
                        agent._wrap_event(
                            "tool_result",
                            {
                                "tool_name": tool_name,
                                "tool_type": tool_type,
                                "tool_call_id": tool_call_id,
                                "ok": False,
                                "error": error_text,
                                "result": error_text,
                                "message": f"{display_name} 执行失败",
                            },
                        )
                    )
                    request.state["tool_call_count"] = request.state.get("tool_call_count", 0) + 1
                    return ToolMessage(
                        content=error_text,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                    )

        return [
            ToolCallLimitMiddleware(thread_limit=8),
            WorkspaceReactMiddleware(),
        ]

    async def setup_terminal_tools(self):
        if self.execution_mode != "terminal":
            self.terminal_tools = []
            return

        if not self.desktop_bridge_config:
            self.terminal_tools = []
            return

        self.terminal_tools, metadata_map = build_terminal_langchain_tools(
            bridge_config=self.desktop_bridge_config,
            access_scope=self.access_scope,
        )
        self.tool_metadata_map.update(metadata_map)

    async def setup_mcp_tools(self):
        if self.execution_mode == "terminal" or not self.mcp_configs:
            self.mcp_tools = []
            return

        try:
            self.mcp_tools = await self.mcp_manager.get_mcp_tools()
            mcp_servers_info = await self.mcp_manager.show_mcp_tools()
            self.server_dict = {
                server_name: [tool["name"] for tool in tools_info]
                for server_name, tools_info in mcp_servers_info.items()
            }
            for tool in self.mcp_tools:
                self.tool_metadata_map[tool.name] = {
                    "name": tool.name,
                    "type": "MCP 工具",
                }
        except Exception as err:
            logger.error(f"Failed to initialize MCP tools: {err}")
            self.mcp_tools = []

    async def setup_plugin_tools(self):
        if self.execution_mode == "terminal":
            self.plugin_tools = []
            return

        try:
            @tool(parse_docstring=True)
            def list_enabled_capabilities() -> str:
                """
                Return the actual enabled built-in tools and MCP tools for the current workspace session.

                Use this before claiming that a capability is unavailable, or when the user asks which
                tools, MCPs, or abilities are currently enabled.
                """
                sections: list[str] = []
                if self.plugin_tools:
                    sections.append(
                        "Built-in tools:\n" + "\n".join(
                            [
                                f"- {self._tool_display_info(enabled_tool.name)[1]} ({enabled_tool.name})"
                                for enabled_tool in self.plugin_tools
                                if enabled_tool.name != "list_enabled_capabilities"
                            ]
                        )
                    )
                if self.mcp_tools:
                    sections.append(
                        "MCP tools:\n" + "\n".join(
                            [
                                f"- {self._tool_display_info(enabled_tool.name)[1]} ({enabled_tool.name})"
                                for enabled_tool in self.mcp_tools
                            ]
                        )
                    )
                if self.knowledge_tools:
                    sections.append(
                        "Knowledge tools:\n" + "\n".join(
                            [
                                f"- {self._tool_display_info(enabled_tool.name)[1]} ({enabled_tool.name})"
                                for enabled_tool in self.knowledge_tools
                            ]
                        )
                    )
                if self.skill_tools:
                    sections.append(
                        "Skill tools:\n" + "\n".join(
                            [
                                f"- {self._tool_display_info(enabled_tool.name)[1]} ({enabled_tool.name})"
                                for enabled_tool in self.skill_tools
                            ]
                        )
                    )
                if self.server_dict:
                    sections.append(
                        "MCP servers:\n" + "\n".join(
                            [
                                f"- {server_name}: {', '.join(tool_names)}"
                                for server_name, tool_names in self.server_dict.items()
                            ]
                        )
                    )
                return "\n\n".join(sections) if sections else "No enabled tools or MCP tools found in this session."

            @tool(parse_docstring=True)
            async def search_available_capabilities(query: str, kind: str = "", limit: int = 8) -> str:
                """
                Search all available tools, skills, and MCP capabilities visible to the current user.

                Use this when the user mentions a tool, skill, MCP server, integration, or vague
                capability name that may exist but is not already obvious in the enabled session.

                Args:
                    query: Natural language capability query, such as "飞书发消息" or "PDF 转 Word".
                    kind: Optional capability kind filter: tool, skill, mcp_server, or mcp_tool.
                    limit: Maximum number of results to return.
                """
                results = await CapabilityRegistryService.search(
                    query,
                    user_id=self.user_id,
                    kind=kind,
                    limit=limit,
                )
                if not results:
                    return "没有找到匹配的能力。"
                return json.dumps(results, ensure_ascii=False, indent=2)

            @tool
            async def create_remote_api_tool(
                display_name: str,
                description: str,
                endpoint_url: str | None = None,
                base_url: str | None = None,
                path: str | None = None,
                method: str | None = "GET",
                auth_type: str | None = "none",
                api_key: str | None = None,
                api_key_name: str | None = None,
                docs_url: str | None = None,
                docs_urls: list[str] | None = None,
                sample_curl: str | None = None,
                logo_url: str | None = None,
                openapi_schema_json: str | None = None,
            ) -> str:
                """Create a remote API tool for the current user."""
                endpoint_url = (endpoint_url or "").strip()
                base_url = (base_url or "").strip()
                path = (path or "").strip()
                docs_url = (docs_url or "").strip()
                docs_urls = [str(item).strip() for item in (docs_urls or []) if str(item).strip()]
                sample_curl = (sample_curl or "").strip()
                api_key = (api_key or "").strip()
                api_key_name = (api_key_name or "").strip()
                openapi_schema_json = (openapi_schema_json or "").strip()
                method_value = (method or "GET").strip().upper() or "GET"
                auth_type_value = (auth_type or "none").strip().lower() or "none"
                logo = (logo_url or "").strip() or app_settings.default_config.get("tool_logo_url") or ""

                openapi_schema = None
                assist_source_available = bool(
                    endpoint_url
                    or docs_url
                    or sample_curl
                    or (base_url and path)
                )
                if openapi_schema_json and not assist_source_available:
                    try:
                        openapi_schema = json.loads(openapi_schema_json)
                    except Exception as err:
                        raise ValueError(f"openapi_schema_json is not valid JSON: {err}") from err

                simple_api_config = None
                normalized_auth = {}
                if not openapi_schema:
                    endpoint = endpoint_url or (f"{base_url.rstrip('/')}/{path.lstrip('/')}" if base_url and path else "")
                    assist_result = build_remote_api_assist_draft(
                        RemoteApiAssistReq(
                            endpoint_url=endpoint,
                            docs_url=docs_url,
                            docs_urls=docs_urls or [item for item in [docs_url] if item],
                            sample_curl=sample_curl,
                            api_key=api_key,
                            api_key_name=api_key_name,
                            auth_type=auth_type_value if auth_type_value in {"none", "bearer", "basic", "api_key_query", "api_key_header"} else "none",
                            method=method_value if method_value in {"GET", "POST", "PUT", "PATCH", "DELETE"} else "",
                            display_name=display_name,
                            description=description,
                        )
                    )
                    simple_api_config = assist_result.simple_api_config
                    normalized_auth = assist_result.auth_config

                created = await ToolCreationService.create_user_defined_tool(
                    display_name=display_name,
                    description=description,
                    logo_url=logo,
                    runtime_type="remote_api",
                    user_id=self.user_id,
                    auth_config=normalized_auth,
                    openapi_schema=openapi_schema,
                    simple_api_config=simple_api_config,
                    source_metadata={
                        "endpoint_url": endpoint or (
                            f"{str(simple_api_config.base_url).rstrip('/')}/{str(simple_api_config.path).lstrip('/')}"
                            if simple_api_config and simple_api_config.base_url and simple_api_config.path
                            else ""
                        ),
                        "docs_url": docs_url,
                        "docs_urls": docs_urls or [item for item in [docs_url] if item],
                        "sample_curl": sample_curl,
                    },
                )
                tool_id = created.get("tool_id") if isinstance(created, dict) else None
                return (
                    f"已创建 API 工具: {display_name}"
                    + (f" (tool_id={tool_id})" if tool_id else "")
                    + "。后续可以到工具页继续修改图标、参数或 OpenAPI 细节。"
                )

            @tool
            async def create_cli_tool(
                display_name: str,
                description: str,
                command: str | None = None,
                tool_dir: str | None = None,
                source_type: str | None = "local_directory",
                args_template: str | None = None,
                install_source: str | None = None,
                install_command: str | None = None,
                healthcheck_command: str | None = None,
                credential_mode: str | None = "none",
                cwd_mode: str | None = "tool_dir",
                cwd: str | None = None,
                timeout_ms: int = 30000,
                github_url: str | None = None,
                docs_url: str | None = None,
                local_path: str | None = None,
                notes: str | None = None,
                logo_url: str | None = None,
            ) -> str:
                """Create a CLI tool for the current user."""
                source_value = (source_type or "local_directory").strip()
                logo = (logo_url or "").strip() or app_settings.default_config.get("tool_logo_url") or ""
                cli_config = {
                    "source_type": source_value,
                    "tool_dir": (tool_dir or "").strip(),
                    "local_path": (local_path or "").strip(),
                    "command": (command or "").strip(),
                    "args_template": (args_template or "").strip(),
                    "cwd_mode": (cwd_mode or "tool_dir").strip() or "tool_dir",
                    "cwd": (cwd or "").strip(),
                    "timeout_ms": int(timeout_ms or 30000),
                    "install_command": (install_command or "").strip(),
                    "install_source": (install_source or "").strip(),
                    "install_notes": (notes or "").strip(),
                    "healthcheck_command": (healthcheck_command or "").strip(),
                    "credential_mode": (credential_mode or "none").strip() or "none",
                }

                preview_needed = not cli_config["command"] or github_url or docs_url or local_path
                if preview_needed:
                    preview = CliToolDiscoveryService.preview(
                        CLIToolPreviewReq(
                            tool_dir=cli_config["tool_dir"] or (local_path or ""),
                            source_type=source_value if source_value in {"local_directory", "executable", "npm_package", "python_package", "github_repo"} else "local_directory",
                            install_source=cli_config["install_source"],
                            command=cli_config["command"],
                            doc_url=docs_url,
                            docs_url=docs_url,
                            github_url=github_url,
                            local_path=local_path,
                            notes=notes,
                        )
                    )
                    if not cli_config["command"] and preview.recommended:
                        cli_config["command"] = preview.recommended.command
                        cli_config["args_template"] = " ".join(preview.recommended.args_template or [])
                        cli_config["cwd_mode"] = preview.recommended.cwd_mode or cli_config["cwd_mode"]
                        cli_config["cwd"] = preview.recommended.cwd or cli_config["cwd"]
                    if not cli_config["install_command"] and preview.suggested_install_command:
                        cli_config["install_command"] = preview.suggested_install_command
                    if not cli_config["healthcheck_command"] and preview.suggested_healthcheck_command:
                        cli_config["healthcheck_command"] = preview.suggested_healthcheck_command
                    if not cli_config["tool_dir"] and preview.tool_dir:
                        cli_config["tool_dir"] = preview.tool_dir

                created = await ToolCreationService.create_user_defined_tool(
                    display_name=display_name,
                    description=description,
                    logo_url=logo,
                    runtime_type="cli",
                    user_id=self.user_id,
                    cli_config=cli_config,
                    source_metadata={
                        "github_url": (github_url or "").strip(),
                        "docs_url": (docs_url or "").strip(),
                        "local_path": (local_path or "").strip(),
                        "notes": (notes or "").strip(),
                    },
                )
                tool_id = created.get("tool_id") if isinstance(created, dict) else None
                return (
                    f"已创建 CLI 工具: {display_name}"
                    + (f" (tool_id={tool_id})" if tool_id else "")
                    + "。后续可以到工具页继续修改图标、命令或凭证模式。"
                )

            db_tools = await ToolService.get_tools_from_id(self.plugins)
            for db_tool in db_tools:
                if db_tool.is_user_defined:
                    runtime_type = get_user_defined_runtime_type(db_tool)
                    runtime_label = "CLI 工具" if runtime_type == "cli" else "远程 API 工具"
                    langchain_tools = build_user_defined_langchain_tools(db_tool)
                    self.plugin_tools.extend(langchain_tools)
                    for langchain_tool in langchain_tools:
                        self.tool_metadata_map[langchain_tool.name] = {
                            "name": db_tool.display_name,
                            "type": runtime_label,
                        }
                    continue

                plugin_tool = WorkSpacePlugins.get(db_tool.name)
                if plugin_tool:
                    self.plugin_tools.append(plugin_tool)
                    self.tool_metadata_map[plugin_tool.name] = {
                        "name": db_tool.display_name,
                        "type": "系统工具",
                    }

            existing_names = {enabled_tool.name for enabled_tool in self.plugin_tools}

            if "send_email" in existing_names:
                email_list_tool = WorkSpacePlugins.get("list_email_accounts")
                if email_list_tool and email_list_tool.name not in existing_names:
                    self.plugin_tools.append(email_list_tool)
                    self.tool_metadata_map[email_list_tool.name] = {
                        "name": "邮箱槽位查询",
                        "type": "系统工具",
                    }
                    existing_names.add(email_list_tool.name)

            web_search_tool = WorkSpacePlugins.get("web_search")
            if self.enable_web_search and web_search_tool:
                if web_search_tool.name not in existing_names:
                    self.plugin_tools.append(web_search_tool)
                    self.tool_metadata_map[web_search_tool.name] = {
                        "name": "联网搜索",
                        "type": "系统工具",
                    }
                    existing_names.add(web_search_tool.name)

                read_webpage_tool = WorkSpacePlugins.get("read_webpage")
                if read_webpage_tool and read_webpage_tool.name not in existing_names:
                    self.plugin_tools.append(read_webpage_tool)
                    self.tool_metadata_map[read_webpage_tool.name] = {
                        "name": "网页读取",
                        "type": "系统工具",
                    }
                    existing_names.add(read_webpage_tool.name)

            default_image_tool = WorkSpacePlugins.get("text_to_image")
            if default_image_tool and default_image_tool.name not in existing_names:
                self.plugin_tools.append(default_image_tool)
                self.tool_metadata_map[default_image_tool.name] = {
                    "name": "文生图",
                    "type": "默认能力",
                }
                existing_names.add(default_image_tool.name)

            if "list_enabled_capabilities" not in existing_names:
                self.plugin_tools.append(list_enabled_capabilities)
                self.tool_metadata_map[list_enabled_capabilities.name] = {
                    "name": "能力清单查询",
                    "type": "只读工具",
                }
                existing_names.add(list_enabled_capabilities.name)
            if "search_available_capabilities" not in existing_names:
                self.plugin_tools.append(search_available_capabilities)
                self.tool_metadata_map[search_available_capabilities.name] = {
                    "name": "能力模糊搜索",
                    "type": "只读工具",
                }
                existing_names.add(search_available_capabilities.name)
            if "create_remote_api_tool" not in existing_names:
                self.plugin_tools.append(create_remote_api_tool)
                self.tool_metadata_map[create_remote_api_tool.name] = {
                    "name": "创建 API 工具",
                    "type": "默认能力",
                }
                existing_names.add(create_remote_api_tool.name)
            if "create_cli_tool" not in existing_names:
                self.plugin_tools.append(create_cli_tool)
                self.tool_metadata_map[create_cli_tool.name] = {
                    "name": "创建 CLI 工具",
                    "type": "默认能力",
                }
                existing_names.add(create_cli_tool.name)
        except Exception as err:
            logger.exception(f"Failed to initialize plugin tools: {err}")
            self.plugin_tools = []

    async def setup_knowledge_tools(self):
        if self.execution_mode == "terminal" or not self.knowledge_ids:
            self.knowledge_tools = []
            return

        @tool(parse_docstring=True)
        async def search_knowledge_base(query: str) -> str:
            """
            Search the selected knowledge bases and return relevant passages.

            Args:
                query: The question or keywords to retrieve from the selected knowledge bases.
            """
            result = await RagHandler.retrieve_ranked_documents_with_metadata(
                query,
                self.knowledge_ids,
                self.knowledge_ids,
                retrieval_mode=self.retrieval_mode,
            )
            try:
                writer = get_stream_writer()
                writer(self._wrap_event("status", self._build_retrieval_event_payload(result)))
            except Exception:
                logger.debug("knowledge retrieval trace writer unavailable in current execution context")
            return result["content"]

        self.knowledge_tools = [search_knowledge_base]
        self.tool_metadata_map[search_knowledge_base.name] = {
            "name": "知识库检索",
            "type": "知识库",
        }

    async def setup_skill_tools(self):
        if self.execution_mode == "terminal" or not self.agent_skill_ids:
            self.skill_tools = []
            return

        try:
            skills = await AgentSkillService.get_agent_skills_by_ids(self.agent_skill_ids)
        except Exception as err:
            logger.error(f"Failed to initialize skill tools: {err}")
            self.skill_tools = []
            return

        def create_skill_tool(skill: AgentSkill):
            @tool(skill.as_tool_name, description=skill.description or f"Use Skill: {skill.name}")
            async def load_skill_context(query: str) -> str:
                """Load the selected Skill package so the current agent can use it directly."""
                skill_context = AgentSkillService.build_skill_runtime_context(skill, query=query)
                return (
                    f"You selected Skill '{skill.name}'. Use the following skill package as guidance "
                    f"for the current task in this same conversation. Do not claim the skill has "
                    f"already executed unless you actually use other tools afterwards.\n\n{skill_context}"
                )

            return load_skill_context

        self.skill_tools = []
        for skill in skills:
            skill_tool = create_skill_tool(skill)
            self.skill_tools.append(skill_tool)
            self.tool_metadata_map[skill_tool.name] = {
                "name": skill.name,
                "type": "Skill",
            }

    @staticmethod
    def _extract_reference_image_url(content: Any) -> str:
        text = str(content or "")
        marker = "source_url:"
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith(marker):
                return stripped[len(marker):].strip()
        return ""

    @staticmethod
    def _looks_like_image_regeneration_request(query: str, reference_image_url: str) -> bool:
        if not reference_image_url:
            return False

        normalized_query = (query or "").lower()
        keywords = [
            "生成", "重生成", "重绘", "改背景", "换背景", "背景改", "改成", "变体", "海报", "封面", "logo",
            "poster", "cover", "regenerate", "redraw", "variant", "background", "recolor", "restyle",
        ]
        return any(keyword in normalized_query for keyword in keywords)

    async def _run_direct_image_generation(
        self,
        query: str,
        reference_image_url: str,
    ) -> AsyncGenerator[WorkspaceAgentStreamEvent, None]:
        yield self._wrap_event(
            "status",
            {
                "phase": "start",
                "status": "START",
                "message": "Agent 已识别为带参考图的生成任务，直接调用生图能力。",
                "execution_mode": self.execution_mode,
                "access_scope": self.access_scope,
            },
        )
        yield self._wrap_event(
            "tool_call",
            {
                "tool_name": "text_to_image",
                "tool_type": "默认能力",
                "tool_call_id": "direct-image-generation",
                "arguments": {
                    "user_prompt": query,
                    "reference_image_url": reference_image_url,
                },
                "message": "正在根据上传图片生成新图。",
            },
        )
        try:
            result = await asyncio.to_thread(_text_to_image, query, reference_image_url)
            yield self._wrap_event(
                "tool_result",
                {
                    "tool_name": "text_to_image",
                    "tool_type": "默认能力",
                    "tool_call_id": "direct-image-generation",
                    "ok": True,
                    "result": result,
                    "message": "图片已生成",
                },
            )
            yield self._wrap_event(
                "final",
                {
                    "chunk": result,
                    "message": result,
                    "accumulated": result,
                    "done": True,
                },
            )
        except Exception as err:
            error_text = f"图片生成失败：{err}"
            yield self._wrap_event(
                "tool_result",
                {
                    "tool_name": "text_to_image",
                    "tool_type": "默认能力",
                    "tool_call_id": "direct-image-generation",
                    "ok": False,
                    "error": str(err),
                    "result": error_text,
                    "message": "图片生成失败",
                },
            )
            yield self._wrap_event(
                "final",
                {
                    "chunk": error_text,
                    "message": error_text,
                    "accumulated": error_text,
                    "done": True,
                },
            )

    @staticmethod
    def _looks_like_image_regeneration_request_v2(query: str, reference_image_url: str) -> bool:
        if not reference_image_url:
            return False

        normalized_query = (query or "").lower()
        keywords = [
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
        return any(keyword in normalized_query for keyword in keywords)

    async def ainvoke(self, messages: List[BaseMessage]):
        if not self._initialized:
            await self.init_simple_agent()

        normalized_messages = normalize_messages_for_model(
            messages,
            model_name=self.model_name,
            base_url=self.base_url,
        )
        try:
            if not self.tools:
                return []

            results = await self.react_agent.ainvoke(
                {"messages": normalized_messages},
                config=self._build_run_config(
                    run_name="workspace_simple_agent_invoke",
                    metadata={"message_count": len(normalized_messages)},
                ),
            )
            result_messages = results["messages"][:-1]
            return [
                msg
                for msg in result_messages
                if isinstance(msg, ToolMessage) or (isinstance(msg, AIMessage) and msg.tool_calls)
            ]
        except Exception:
            return []

    async def _generate_title(self, query: str):
        session = await WorkSpaceSessionService.get_workspace_session_from_id(
            self.session_id,
            self.user_id,
        )
        if session and session.get("title") not in {"", "新对话", "未命名会话"}:
            return session.get("title")

        title_prompt = GenerateTitlePrompt.format(query=query)
        response = await self.model.ainvoke(
            title_prompt,
            config=self._build_run_config(
                run_name="workspace_generate_title",
                tags=["workspace", "title"],
                metadata={"query": query},
            ),
        )
        return WorkSpaceSessionService.normalize_session_title(
            response.content,
            fallback_query=query,
        )

    async def _add_workspace_session(self, title, contexts: WorkSpaceSessionContext):
        normalized_title = WorkSpaceSessionService.normalize_session_title(
            title,
            fallback_query=contexts.query,
        )
        session = await WorkSpaceSessionService.get_workspace_session_from_id(
            self.session_id,
            self.user_id,
        )
        if session:
            await WorkSpaceSessionService.update_workspace_session_contexts(
                session_id=self.session_id,
                session_context=contexts.model_dump(),
                title=normalized_title,
            )
            return

        await WorkSpaceSessionService.create_workspace_session(
            WorkSpaceSessionCreate(
                title=normalized_title,
                user_id=self.user_id,
                session_id=self.session_id,
                contexts=[contexts.model_dump()],
                agent=WorkSpaceAgents.SimpleAgent.value,
            )
        )

    @staticmethod
    def _safe_parse_structured_result(result: Any) -> Any | None:
        if isinstance(result, (dict, list)):
            return result
        if not isinstance(result, str):
            return None

        text = result.strip()
        if not text:
            return None

        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(text)
            except Exception:
                continue
            if isinstance(parsed, (dict, list)):
                return parsed
        return None

    @staticmethod
    def _format_weather_payload(payload: Any) -> str | None:
        if not isinstance(payload, dict):
            return None

        lives = payload.get("lives")
        if isinstance(lives, list) and lives:
            live = lives[0] if isinstance(lives[0], dict) else None
            if not live:
                return None

            city = live.get("city") or live.get("province") or "当前城市"
            weather = live.get("weather") or "天气未知"
            temperature = live.get("temperature")
            humidity = live.get("humidity")
            wind_direction = live.get("winddirection") or live.get("windDirection")
            wind_power = live.get("windpower") or live.get("windPower")
            report_time = live.get("reporttime") or live.get("reportTime")

            parts = [f"{city}当前{weather}"]
            if temperature:
                parts.append(f"气温 {temperature}°C")
            if humidity:
                parts.append(f"湿度 {humidity}%")
            if wind_direction or wind_power:
                wind_text = f"{wind_direction or ''}{wind_power or ''}".strip()
                if wind_text:
                    parts.append(f"风力 {wind_text}")
            summary = "，".join(parts) + "。"
            if report_time:
                summary += f" 数据时间：{report_time}。"
            return summary

        forecasts = payload.get("forecasts")
        if isinstance(forecasts, list) and forecasts:
            if all(isinstance(item, dict) and (item.get("dayweather") or item.get("nightweather")) for item in forecasts):
                today = forecasts[0]
                city = payload.get("city") or payload.get("province") or "当前城市"
                date = today.get("date") or "今天"
                day_weather = today.get("dayweather") or today.get("dayWeather") or "未知"
                night_weather = today.get("nightweather") or today.get("nightWeather")
                day_temp = today.get("daytemp") or today.get("dayTemp")
                night_temp = today.get("nighttemp") or today.get("nightTemp")
                day_wind = today.get("daywind") or today.get("dayWind")
                day_power = today.get("daypower") or today.get("dayPower")

                parts = [f"{city}{date}{day_weather}"]
                if day_temp or night_temp:
                    parts.append(f"预计气温 {night_temp or '?'}-{day_temp or '?'}°C")
                if night_weather:
                    parts.append(f"夜间 {night_weather}")
                if day_wind or day_power:
                    wind_text = f"{day_wind or ''}{day_power or ''}".strip()
                    if wind_text:
                        parts.append(f"白天风力 {wind_text}")
                return "，".join(parts) + "。"

            forecast = forecasts[0] if isinstance(forecasts[0], dict) else None
            if not forecast:
                return None

            city = forecast.get("city") or forecast.get("province") or "当前城市"
            casts = forecast.get("casts")
            if not isinstance(casts, list) or not casts:
                return None
            today = casts[0] if isinstance(casts[0], dict) else None
            if not today:
                return None

            date = today.get("date") or "今天"
            day_weather = today.get("dayweather") or today.get("dayWeather") or "未知"
            night_weather = today.get("nightweather") or today.get("nightWeather")
            day_temp = today.get("daytemp") or today.get("dayTemp")
            night_temp = today.get("nighttemp") or today.get("nightTemp")
            day_wind = today.get("daywind") or today.get("dayWind")
            day_power = today.get("daypower") or today.get("dayPower")

            parts = [f"{city}{date}{day_weather}"]
            if day_temp or night_temp:
                parts.append(f"预计气温 {night_temp or '?'}-{day_temp or '?'}°C")
            if night_weather:
                parts.append(f"夜间 {night_weather}")
            if day_wind or day_power:
                wind_text = f"{day_wind or ''}{day_power or ''}".strip()
                if wind_text:
                    parts.append(f"白天风力 {wind_text}")
            return "，".join(parts) + "。"

        return None

    def _format_direct_tool_final_answer(self, tool_name: str, result: Any, raw_text: str) -> str:
        if tool_name == "maps_weather":
            payload = self._safe_parse_structured_result(result)
            weather_summary = self._format_weather_payload(payload)
            if weather_summary:
                return weather_summary
        return self._normalize_weekday_labels(raw_text)

    @staticmethod
    def _format_tool_result_for_model(result: Any) -> str:
        structured_summary = format_structured_tool_result(result)
        if structured_summary:
            return structured_summary
        return result if isinstance(result, str) else str(result)

    @staticmethod
    def _normalize_weekday_labels(text: str) -> str:
        if not isinstance(text, str) or not text:
            return text

        weekday_names = ["一", "二", "三", "四", "五", "六", "日"]

        def replace(match: re.Match[str]) -> str:
            year = int(match.group("year"))
            month = int(match.group("month"))
            day = int(match.group("day"))
            try:
                weekday = weekday_names[date(year, month, day).weekday()]
            except ValueError:
                return match.group(0)
            return f"{year:04d}-{month:02d}-{day:02d}{match.group('open')}周{weekday}{match.group('close')}"

        return re.sub(
            r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})(?P<open>[（(])周[一二三四五六日天](?P<close>[）)])",
            replace,
            text,
        )

    async def _run_direct_routed_tool(
        self,
        tool: BaseTool,
        args: dict[str, Any],
        original_query: str,
        session_metadata: dict[str, Any] | None = None,
    ) -> AsyncGenerator[WorkspaceAgentStreamEvent, None]:
        tool_type, display_name = self._tool_display_info(tool.name)
        tool_call_id = f"direct-{tool.name}-{uuid.uuid4().hex[:8]}"
        route_kind = self.route_hint.kind or "tool_creation"
        yield self._wrap_event(
            "status",
            {
                "phase": "route",
                "status": "START",
                "message": f"已按显式意图直达 {route_kind} 能力",
                "route": {**self.route_hint.model_dump(), "kind": route_kind},
                "tool_names": [tool.name],
            },
        )
        yield self._wrap_event(
            "tool_call",
            {
                "tool_name": tool.name,
                "tool_type": tool_type,
                "tool_call_id": tool_call_id,
                "arguments": args,
                "message": f"正在调用 {tool_type}: {display_name}",
            },
        )
        call_args = dict(args)
        if self.is_mcp_tool(tool.name) and self.mcp_requires_user_config(tool.name):
            mcp_config = await MCPUserConfigService.get_mcp_user_config(
                self.user_id,
                self.get_mcp_id_by_tool(tool.name),
            )
            call_args.update(mcp_config)
        result = await tool.ainvoke(
            call_args,
            config=self._build_run_config(
                run_name="workspace_direct_tool_call",
                tags=["workspace", "tool"],
                metadata={
                    "tool_name": tool.name,
                    "tool_type": tool_type,
                },
            ),
        )
        raw_result_text = result if isinstance(result, str) else str(result)
        final_answer = self._format_direct_tool_final_answer(tool.name, result, raw_result_text)
        yield self._wrap_event(
            "tool_result",
            {
                "tool_name": tool.name,
                "tool_type": tool_type,
                "tool_call_id": tool_call_id,
                "ok": True,
                "result": raw_result_text,
                                    "message": f"{display_name} 已返回结果",
            },
        )
        title = await self._generate_title(original_query)
        await self._add_workspace_session(
            title,
            WorkSpaceSessionContext(
                query=original_query,
                answer=final_answer,
                metadata=session_metadata or {},
            ),
        )
        yield self._wrap_event(
            "final",
            {
                "chunk": final_answer,
                "message": final_answer,
                "accumulated": final_answer,
                "done": True,
            },
        )

    def _get_active_skill_for_route(self) -> Any | None:
        if self.route_hint.kind != "skill":
            return None

        target = self._norm(self.route_hint.target)
        for skill in self.available_skills:
            candidates = {
                self._norm(self._skill_value(skill, "id")),
                self._norm(self._skill_value(skill, "name")),
                self._norm(self._skill_value(skill, "as_tool_name")),
            }
            if target and target in candidates:
                return skill

        selected_ids = set(self.agent_skill_ids)
        for skill in self.available_skills:
            if self._skill_value(skill, "id") in selected_ids:
                return skill
        return None

    def _prepare_explicit_skill_messages(
        self,
        messages: List[BaseMessage],
        cleaned_query: str,
    ) -> List[BaseMessage]:
        if not ((self.original_query or "").strip().startswith("/") and self.route_hint.kind == "skill"):
            return messages

        skill = self._get_active_skill_for_route()
        if not skill:
            return messages

        runtime_skill = skill if not isinstance(skill, dict) else SimpleNamespace(**skill)
        effective_query = cleaned_query.strip() or self._strip_route_command(self.original_query or "").strip()
        skill_context = AgentSkillService.build_skill_runtime_context(runtime_skill, query=effective_query)
        normalized_messages = copy.deepcopy(messages)
        if normalized_messages and isinstance(normalized_messages[-1], HumanMessage):
            normalized_messages[-1] = HumanMessage(
                content=(
                    "The user explicitly selected a Skill for this turn.\n"
                    "Treat the following skill package as execution guidance for the current task.\n"
                    "Do not output the skill package verbatim.\n"
                    "Use it internally, then continue solving the user's task with normal tools and reasoning.\n\n"
                    f"{skill_context}\n\n"
                    f"[User Task]\n{effective_query}"
                )
            )
        return normalized_messages

    @staticmethod
    def _looks_like_external_freshness_query(query: str) -> bool:
        normalized = (query or "").lower()
        keywords = [
            "天气",
            "今天",
            "现在",
            "实时",
            "最新",
            "联网",
            "搜索",
            "查一个",
            "查一查",
            "新闻",
            "网页",
            "bing",
            "高德",
            "地图",
            "飞书",
            "邮件",
            "calendar",
            "weather",
            "today",
            "current",
            "latest",
            "news",
            "search",
            "web",
        ]
        return any(keyword in normalized for keyword in keywords)

    async def _prefetch_knowledge_context(self, query: str) -> Dict[str, Any] | None:
        if self.execution_mode == "terminal" or not self.knowledge_ids:
            return None
        normalized_query = (query or "").strip()
        if not normalized_query:
            return None
        try:
            result = await RagHandler.retrieve_ranked_documents_with_metadata(
                normalized_query,
                self.knowledge_ids,
                self.knowledge_ids,
                retrieval_mode=self.retrieval_mode,
            )
        except Exception as err:
            logger.warning(f"workspace knowledge prefetch failed: {err}")
            return None
        context = str(result.get("content") or "").strip()
        if not context:
            return None
        return {"content": context, "result": result}

    @staticmethod
    def _inject_prefetched_knowledge_context(
        messages: List[BaseMessage],
        knowledge_context: str,
        user_query: str,
    ) -> List[BaseMessage]:
        if not knowledge_context:
            return messages

        normalized_messages = copy.deepcopy(messages)
        injected_content = (
            "Use the following retrieved knowledge base context as your primary source for this turn.\n"
            "Prefer answering from this context before using generic web search.\n"
            "Only use external tools if the user explicitly requests real-time or external information, "
            "or if the retrieved context is clearly insufficient.\n\n"
            f"[Knowledge Context]\n{knowledge_context}\n\n"
            f"[User Task]\n{user_query}"
        )
        if normalized_messages and isinstance(normalized_messages[-1], HumanMessage):
            normalized_messages[-1] = HumanMessage(content=injected_content)
            return normalized_messages

        normalized_messages.append(HumanMessage(content=injected_content))
        return normalized_messages

    def _build_runtime_tools(
        self,
        query: str,
        prefetched_knowledge_context: str,
    ) -> List[BaseTool]:
        if not prefetched_knowledge_context:
            return self.tools
        if self._looks_like_external_freshness_query(query):
            return self.tools

        filtered_tools = [
            tool
            for tool in self.tools
            if tool.name not in {"web_search", "read_webpage"}
        ]
        return filtered_tools or self.tools

    async def astream(
        self,
        messages: List[BaseMessage],
    ) -> AsyncGenerator[WorkspaceAgentStreamEvent, None]:
        if not self._initialized:
            await self.init_simple_agent()

        original_query = self.original_query or strip_model_wrapper_from_user_input(
            getattr(messages[-1], "content", "")
        )
        reference_image_url = self._extract_reference_image_url(getattr(messages[-1], "content", ""))
        user_messages = copy.deepcopy(
            normalize_messages_for_model(
                messages,
                model_name=self.model_name,
                base_url=self.base_url,
            )
        )

        if self.execution_mode == "tool" and self._looks_like_image_regeneration_request_v2(
            original_query,
            reference_image_url,
        ):
            async for event in self._run_direct_image_generation(original_query, reference_image_url):
                yield event
            return

        if self.execution_mode == "terminal" and not self.desktop_bridge_config:
            terminal_notice = (
                "当前已切换到终端模式，但这次会话没有拿到桌面 bridge 配置。"
                "所以我还不能真正访问你的 Windows 本机文件系统或执行本地命令。"
                "请从桌面客户端发起终端模式对话，再让我执行本地文件或命令操作。"
            )
            yield self._wrap_event(
                "status",
                {
                    "phase": "unsupported",
                    "status": "ERROR",
                    "message": "当前终端模式缺少桌面 bridge，无法执行本机操作",
                    "error": terminal_notice,
                },
            )
            yield self._wrap_event(
                "final",
                {
                    "chunk": terminal_notice,
                    "message": terminal_notice,
                    "accumulated": terminal_notice,
                    "done": True,
                },
            )
            return

        explicit_command = original_query.strip().startswith("/")
        cleaned_route_query = self._strip_route_command(original_query)
        if explicit_command and self.route_hint.kind == "skill":
            user_messages = self._prepare_explicit_skill_messages(user_messages, cleaned_route_query)
        prefetched_knowledge_context = ""
        runtime_tools = self.tools
        runtime_system_prompt = self._build_runtime_system_prompt()
        if (
            self.execution_mode == "tool"
            and self.knowledge_ids
            and self.route_hint.kind not in {"mcp"}
        ):
            prefetched_query = cleaned_route_query.strip() or original_query
            prefetched_payload = await self._prefetch_knowledge_context(prefetched_query)
            if prefetched_payload:
                prefetched_knowledge_context = prefetched_payload["content"]
                user_messages = self._inject_prefetched_knowledge_context(
                    user_messages,
                    prefetched_knowledge_context,
                    prefetched_query,
                )
                runtime_tools = self._build_runtime_tools(
                    prefetched_query,
                    prefetched_knowledge_context,
                )
                runtime_system_prompt = (
                    f"{runtime_system_prompt}\n"
                    "Retrieved knowledge base context has already been injected for this turn. "
                    "Treat it as the primary source unless the user explicitly needs external real-time information."
                )
                yield self._wrap_event("status", self._build_retrieval_event_payload(prefetched_payload["result"]))
        route_tools = self._tools_for_route() or []
        direct_tool = None
        direct_args: dict[str, Any] = {}
        direct_creation_plan = await self._plan_tool_creation_flow(original_query)
        direct_named_tool, direct_named_args = self._parse_direct_named_tool_invocation(original_query)
        logger.info(
            f"workspace direct route check: query={original_query!r} explicit={explicit_command} "
            f"route_hint={self.route_hint.model_dump()} "
            f"route_tools={[tool.name for tool in route_tools]} "
            f"cleaned={cleaned_route_query!r}"
        )
        if direct_named_tool and direct_named_args:
            async for event in self._run_direct_routed_tool(
                direct_named_tool,
                direct_named_args,
                original_query,
            ):
                yield event
            return
        if direct_creation_plan and direct_creation_plan.get("mode") == "cancel":
            reply = direct_creation_plan["reply"]
            title = await self._generate_title(original_query)
            await self._add_workspace_session(
                title,
                WorkSpaceSessionContext(
                    query=original_query,
                    answer=reply,
                    metadata={"tool_creation_state": None},
                ),
            )
            yield self._wrap_event(
                "status",
                {
                    "phase": "tool_creation",
                    "status": "END",
                    "message": "已取消本轮工具创建",
                },
            )
            yield self._wrap_event(
                "final",
                {
                    "chunk": reply,
                    "message": reply,
                    "accumulated": reply,
                    "done": True,
                },
            )
            return
        if direct_creation_plan and direct_creation_plan.get("mode") == "ask":
            reply = direct_creation_plan["reply"]
            title = await self._generate_title(original_query)
            await self._add_workspace_session(
                title,
                WorkSpaceSessionContext(
                    query=original_query,
                    answer=reply,
                    metadata={
                        "tool_creation_state": {
                            "kind": direct_creation_plan.get("kind"),
                            "payload": direct_creation_plan.get("payload") or {},
                        }
                    },
                ),
            )
            yield self._wrap_event(
                "status",
                {
                    "phase": "tool_creation",
                    "status": "WAITING",
                    "message": "工具创建信息还不完整，已进入补参状态",
                },
            )
            yield self._wrap_event(
                "final",
                {
                    "chunk": reply,
                    "message": reply,
                    "accumulated": reply,
                    "done": True,
                },
            )
            return
        if direct_creation_plan and direct_creation_plan.get("mode") == "create":
            async for event in self._run_direct_routed_tool(
                direct_creation_plan["tool"],
                direct_creation_plan["payload"],
                original_query,
                session_metadata={"tool_creation_state": None},
            ):
                yield event
            return
        if explicit_command and self.route_hint.kind == "knowledge" and route_tools:
            async for event in self._run_direct_routed_tool(
                route_tools[0],
                {"query": cleaned_route_query or original_query},
                original_query,
            ):
                yield event
            return
        if self.route_hint.kind == "mcp":
            direct_tool, direct_args = self._guess_direct_mcp_call(original_query)
        if explicit_command and self.route_hint.kind == "mcp":
            if not direct_tool and route_tools:
                route_tool_names = {tool.name for tool in route_tools}
                route_query = cleaned_route_query or original_query
                gaode_route_match = re.search(
                    r"从(?P<origin>.+?)到(?P<destination>.+?)(?:怎么走|如何走|怎么去|路线|导航|开车|驾车|步行|骑行|公交|地铁|$)",
                    route_query,
                )
                if gaode_route_match and any(name.startswith("maps_") for name in route_tool_names):
                    origin = gaode_route_match.group("origin").strip(" ，。")
                    destination = gaode_route_match.group("destination").strip(" ，。")
                    if any(word in route_query for word in ["公交", "地铁"]):
                        direct_tool = self._find_route_tool("maps_direction_transit_integrated")
                        direct_args = {
                            "origin": origin,
                            "destination": destination,
                            "city": "杭州" if "杭州" in route_query else "杭州",
                            "cityd": "杭州" if "杭州" in route_query else "杭州",
                        }
                    elif "步行" in route_query:
                        direct_tool = self._find_route_tool("maps_direction_walking")
                        direct_args = {"origin": origin, "destination": destination}
                    elif "骑行" in route_query:
                        direct_tool = self._find_route_tool("maps_bicycling")
                        direct_args = {"origin": origin, "destination": destination}
                    else:
                        direct_tool = self._find_route_tool("maps_direction_driving")
                        direct_args = {"origin": origin, "destination": destination}
                elif "天气" in route_query and any(name.startswith("maps_") for name in route_tool_names):
                    city = route_query.replace("天气", "").strip(" ，。") or "杭州"
                    direct_tool = self._find_route_tool("maps_weather")
                    direct_args = {"city": city}
                elif "bing_search" in route_tool_names:
                    direct_tool = self._find_route_tool("bing_search")
                    direct_args = {"query": route_query}
            if direct_tool and direct_tool.name in {
                "maps_direction_driving",
                "maps_direction_walking",
                "maps_direction_transit_integrated",
                "maps_bicycling",
            }:
                origin = str(direct_args.get("origin", "")).strip()
                destination = str(direct_args.get("destination", "")).strip()
                coordinate_pattern = r"-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?"
                if not (
                    re.fullmatch(coordinate_pattern, origin)
                    and re.fullmatch(coordinate_pattern, destination)
                ):
                    logger.info(
                        "workspace explicit mcp route falls back to ReAct for multi-step gaode query: "
                        f"tool={direct_tool.name} origin={origin!r} destination={destination!r}"
                    )
                    direct_tool = None
                    direct_args = {}
        if direct_tool:
            async for event in self._run_direct_routed_tool(direct_tool, direct_args, original_query):
                yield event
            return

        generate_title_task = asyncio.create_task(self._generate_title(original_query))
        response_content = ""
        has_activity = False
        has_visible_output = False
        inside_think = False
        runtime_agent = self.react_agent
        if runtime_tools != self.tools or prefetched_knowledge_context:
            runtime_agent = create_agent(
                model=self.model,
                tools=runtime_tools,
                system_prompt=runtime_system_prompt,
                middleware=self.middlewares,
                state_schema=StreamAgentState,
            )

        yield self._wrap_event(
            "status",
            {
                "phase": "start",
                "status": "START",
                "message": "ReAct Agent 已启动",
                "execution_mode": self.execution_mode,
                "access_scope": self.access_scope,
            },
        )

        try:
            async for mode, payload in runtime_agent.astream(
                input={
                    "messages": user_messages,
                    "tool_call_count": 0,
                    "model_call_count": 0,
                    "user_id": self.user_id,
                },
                config=self._build_run_config(
                    run_name="workspace_simple_agent_stream",
                    metadata={
                        "query": original_query,
                        "knowledge_ids": self.knowledge_ids,
                    },
                ),
                stream_mode=["messages", "custom"],
            ):
                if mode == "custom":
                    has_activity = True
                    if isinstance(payload, dict):
                        yield payload
                    else:
                        yield self._wrap_event(
                            "status",
                            {
                                "phase": "custom",
                                "status": "END",
                                "message": str(payload),
                            },
                        )
                    continue

                if mode != "messages" or not isinstance(payload, tuple) or not payload:
                    continue

                chunk = payload[0]
                if not isinstance(chunk, (AIMessageChunk, AIMessage)):
                    continue

                visible_chunk = chunk.content or ""
                if is_minimax_model(model_name=self.model_name, base_url=self.base_url):
                    visible_chunk, inside_think = extract_visible_text_from_stream(
                        str(chunk.content or ""),
                        inside_think,
                    )

                if not visible_chunk:
                    continue
                if isinstance(visible_chunk, str) and not has_visible_output and not visible_chunk.strip():
                    continue

                has_activity = True
                has_visible_output = True
                response_content += visible_chunk
                yield self._wrap_event(
                    "final",
                    {
                        "chunk": visible_chunk,
                        "message": visible_chunk,
                        "accumulated": response_content,
                        "done": False,
                    },
                )
        except Exception as err:
            logger.error(f"Workspace Simple Agent streaming failed: {err}")
            if not generate_title_task.done():
                generate_title_task.cancel()
            error_text = (
                "这次执行没有成功完成。"
                f"后端返回的错误是：{err}。"
                "我已经停止当前任务，请稍后重试，或调整模式后继续。"
            )
            yield self._wrap_event(
                "status",
                {
                    "phase": "error",
                    "status": "ERROR",
                    "message": str(err),
                    "error": str(err),
                },
            )
            yield self._wrap_event(
                "final",
                {
                    "chunk": error_text,
                    "message": error_text,
                    "accumulated": error_text,
                    "done": True,
                },
            )
            return

        if not has_visible_output and not response_content:
            empty_text = (
                "这次请求已经执行完成，但模型没有返回可见正文。"
                "如果你是让它识别图片或分析附件，请直接重试一次；"
                "如果仍然没有正文，我会继续按这次的实际事件日志排查。"
            )
            yield self._wrap_event(
                "status",
                {
                    "phase": "empty",
                    "status": "END",
                    "message": "Agent 没有返回可见内容",
                },
            )
            yield self._wrap_event(
                "final",
                {
                    "chunk": empty_text,
                    "message": empty_text,
                    "accumulated": empty_text,
                    "done": True,
                },
            )
            response_content = empty_text

        normalized_response_content = self._normalize_weekday_labels(response_content)
        if normalized_response_content != response_content:
            response_content = normalized_response_content
            yield self._wrap_event(
                "final",
                {
                    "chunk": "",
                    "message": response_content,
                    "accumulated": response_content,
                    "done": True,
                },
            )

        try:
            title = await generate_title_task
        except Exception:
            title = original_query

        await self._add_workspace_session(
            title=title,
            contexts=WorkSpaceSessionContext(
                query=original_query,
                answer=response_content,
            ),
        )

        yield self._wrap_event(
            "status",
            {
                "phase": "complete",
                "status": "END",
                "message": "ReAct Agent 已完成",
                "answer_length": len(response_content),
            },
        )

    def _canonical_mcp_target(self, text: str | None) -> str:
        normalized = self._norm(text)
        aliases = {
            "bing": "bing",
            "必应": "bing",
            "gaode": "gaode",
            "高德": "gaode",
            "amap": "gaode",
            "feishu": "feishu",
            "飞书": "feishu",
            "lark": "feishu",
        }
        if normalized in aliases:
            return aliases[normalized]

        for server_name in self.server_dict.keys():
            server_norm = self._norm(server_name)
            if normalized and (normalized in server_norm or server_norm in normalized):
                # Custom MCP names are already normalized here. Recursing back into
                # _canonical_mcp_target(server_name) can loop forever when the
                # normalized query equals the normalized server name.
                return server_norm
        return normalized

    def _tool_display_info(self, tool_name: str) -> tuple[str, str]:
        metadata = self.tool_metadata_map.get(tool_name, {})
        return metadata.get("type", "工具"), metadata.get("name", tool_name)

    def _matches_target(self, text: str, target: str) -> bool:
        if not target:
            return True
        text_norm = self._norm(text)
        canonical = self._canonical_mcp_target(target)
        aliases = {
            "bing": ["bing", "必应", "search"],
            "gaode": ["高德", "gaode", "amap", "地图", "路线", "导航"],
            "feishu": ["飞书", "feishu", "lark"],
        }
        candidates = aliases.get(canonical, [self._norm(target)])
        return any(candidate in text_norm for candidate in candidates)

    def _detect_route_hint(self, query: str) -> RouteHint:
        text = (query or "").strip()
        if not text:
            return RouteHint()

        lowered = text.lower()
        slash = re.match(r"^/([a-zA-Z0-9_\-\u4e00-\u9fff]+)(?:\s+(.+))?$", text)
        if slash:
            raw_command = (slash.group(1) or "").strip()
            command = raw_command.lower()
            rest = (slash.group(2) or "").strip()
            command_map = {
                "kb": "knowledge",
                "知识库": "knowledge",
                "rag": "knowledge",
                "skill": "skill",
                "技能": "skill",
                "mcp": "mcp",
                "terminal": "terminal",
                "终端": "terminal",
                "bing": "mcp",
                "必应": "mcp",
                "gaode": "mcp",
                "amap": "mcp",
                "高德": "mcp",
                "feishu": "mcp",
                "lark": "mcp",
                "飞书": "mcp",
            }
            kind = command_map.get(command) or command_map.get(raw_command)
            if kind:
                target = ""
                direct_canonical = self._canonical_mcp_target(raw_command)
                if direct_canonical in {"bing", "gaode", "feishu"}:
                    target = direct_canonical
                elif kind == "skill":
                    target = rest.split(maxsplit=1)[0] if rest else ""
                elif kind == "mcp":
                    first_token = rest.split(maxsplit=1)[0] if rest else ""
                    target = self._canonical_mcp_target(first_token)
                    if not target and len(self.mcp_configs) == 1:
                        target = self._canonical_mcp_target(self.mcp_configs[0].server_name)
                return RouteHint(kind=kind, target=target, reason=f"显式命令 /{raw_command}")
            return RouteHint(kind="skill", target=raw_command, reason=f"显式 Skill /{raw_command}")

        if any(word in text for word in ["飞书", "Feishu", "Lark", "lark"]):
            return RouteHint(kind="mcp", target="feishu", reason="用户明确提到飞书")
        if any(word in text for word in ["高德", "Gaode", "gaode", "Amap", "amap", "地图", "路线", "导航"]):
            return RouteHint(kind="mcp", target="gaode", reason="用户明确提到高德地图能力")
        if any(word in text for word in ["必应", "Bing", "bing", "bing mcp"]):
            return RouteHint(kind="mcp", target="bing", reason="用户明确提到 Bing")
        if any(word in text for word in ["知识库", "根据资料", "根据文档", "查资料库", "查知识", "RAG", "rag"]):
            return RouteHint(kind="knowledge", reason="用户明确要求查知识库")
        if "skill" in lowered or "技能" in text:
            return RouteHint(kind="skill", reason="用户明确提到 Skill")
        if any(word in text for word in ["终端", "命令行", "执行命令", "本地文件", "文件系统"]):
            return RouteHint(kind="terminal", reason="用户明确提到终端/本地能力")
        return RouteHint()

    def _extract_route_payload_query(self, query: str) -> str:
        cleaned = self._strip_route_command(query)
        if not cleaned:
            return cleaned
        if self.route_hint.kind in {"skill", "mcp"} and self.route_hint.target:
            normalized_cleaned = self._norm(cleaned)
            candidates = [self.route_hint.target]
            if self.route_hint.kind == "mcp":
                alias_map = {
                    "bing": ["bing", "必应"],
                    "gaode": ["gaode", "amap", "高德"],
                    "feishu": ["feishu", "lark", "飞书"],
                }
                candidates.extend(alias_map.get(self._canonical_mcp_target(self.route_hint.target), []))
            for candidate in candidates:
                candidate_norm = self._norm(candidate)
                if normalized_cleaned == candidate_norm:
                    return ""
                if normalized_cleaned.startswith(candidate_norm + " "):
                    return cleaned[len(candidate):].strip()
        return cleaned

    def _extract_gaode_weather_city(self, query: str) -> str:
        cleaned = self._extract_route_payload_query(query)
        normalized = cleaned
        prefix_patterns = [
            r"^(?:请|麻烦|帮我|请帮我)?(?:用|通过)?(?:高德地图|高德|gaode|amap)?(?:查询|查一个|查一查|查看|搜索)?",
        ]
        suffix_patterns = [
            r"(?:并且).*$",
            r"(?:并).*$",
            r"(?:请|麻烦).*$",
        ]
        for pattern in prefix_patterns:
            normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE).strip()
        for pattern in suffix_patterns:
            normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE).strip()
        normalized = re.sub(
            r"(?:今天|今日)?天气(?:情况|怎么样|如何)?",
            "",
            normalized,
            flags=re.IGNORECASE,
        )
        normalized = re.sub(r"(今天|今日)$", "", normalized).strip(" ，。？!、")
        return normalized or "杭州"

    def _guess_direct_mcp_call(self, query: str) -> tuple[BaseTool | None, dict[str, Any]]:
        cleaned = self._extract_route_payload_query(query)
        target = self._canonical_mcp_target(self.route_hint.target)
        if not target or target not in {"bing", "gaode", "feishu"}:
            route_tool_names = {tool.name for tool in self._tools_for_route() or []}
            if any(name.startswith("maps_") for name in route_tool_names):
                target = "gaode"
            elif "bing_search" in route_tool_names or "crawl_webpage" in route_tool_names:
                target = "bing"
            elif len(self.server_dict) == 1:
                target = self._canonical_mcp_target(next(iter(self.server_dict.keys())))
        lowered = cleaned.lower()

        if target == "bing":
            return self._find_route_tool("bing_search"), {"query": cleaned}

        if target == "gaode":
            route_match = re.search(
                r"从(?P<origin>.+?)到(?P<destination>.+?)(?:怎么走|如何走|怎么去|路线|导航|开车|驾车|步行|骑行|公交|地铁|$)",
                cleaned,
            )
            if route_match:
                origin = route_match.group("origin").strip(" ，。？?")
                destination = route_match.group("destination").strip(" ，。？?")
                if any(word in lowered for word in ["公交", "地铁"]):
                    city = "杭州" if "杭州" in cleaned else "杭州"
                    return self._find_route_tool("maps_direction_transit_integrated"), {
                        "origin": origin,
                        "destination": destination,
                        "city": city,
                        "cityd": city,
                    }
                if "步行" in cleaned:
                    return self._find_route_tool("maps_direction_walking"), {"origin": origin, "destination": destination}
                if "骑行" in cleaned:
                    return self._find_route_tool("maps_bicycling"), {"origin": origin, "destination": destination}
                return self._find_route_tool("maps_direction_driving"), {"origin": origin, "destination": destination}

            if "天气" in cleaned:
                city = self._extract_gaode_weather_city(query)
                return self._find_route_tool("maps_weather"), {"city": city}

        return None, {}

    async def _record_agent_token_usage(
        self,
        response: AIMessage | AIMessageChunk | BaseMessage,
        model,
    ):
        if response.usage_metadata:
            await UsageStatsService.create_usage_stats(
                model=model,
                user_id=self.user_id,
                agent=UsageStatsAgentType.simple_agent,
                input_tokens=response.usage_metadata.get("input_tokens"),
                output_tokens=response.usage_metadata.get("output_tokens"),
            )

    def is_mcp_tool(self, tool_name: str):
        mcp_names = [tool.name for tool in self.mcp_tools]
        plugin_names = [tool.name for tool in self.plugin_tools]
        knowledge_names = [tool.name for tool in self.knowledge_tools]
        skill_names = [tool.name for tool in self.skill_tools]
        terminal_names = [tool.name for tool in self.terminal_tools]

        if tool_name in mcp_names:
            return True
        if tool_name in plugin_names or tool_name in terminal_names or tool_name in knowledge_names or tool_name in skill_names:
            return False
        logger.warning(f"Tool '{tool_name}' was not found in current workspace tool buckets; treating it as non-MCP.")
        return False

    def get_mcp_id_by_tool(self, tool_name):
        for server_name, tools in self.server_dict.items():
            if tool_name in tools:
                for config in self.mcp_configs:
                    if server_name == config.server_name:
                        return config.mcp_server_id
        return None

    def mcp_requires_user_config(self, tool_name: str) -> bool:
        mcp_server_id = self.get_mcp_id_by_tool(tool_name)
        if not mcp_server_id:
            return False

        for config in self.mcp_configs:
            if config.mcp_server_id != mcp_server_id:
                continue
            if config.config_enabled:
                return True
            if config.config:
                return True
            return False
        return False
