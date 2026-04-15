from __future__ import annotations

import asyncio
import copy
import re
import time
import uuid
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
from agentchat.services.rag.handler import RagHandler
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

tool = lc_tool


class MCPConfig(BaseModel):
    url: str = ""
    type: str = "sse"
    tools: List[str] = []
    server_name: str
    mcp_server_id: str
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
        self.agent_skill_ids = agent_skill_ids or []
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

    @staticmethod
    def _norm(text: str | None) -> str:
        return (text or "").strip().lower()

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
        slash = re.match(r"^/([a-zA-Z_\-\u4e00-\u9fff]+)(?:\s+(.+))?$", text)
        if not slash:
            return text
        return (slash.group(2) or "").strip()


    def _find_route_tool(self, *tool_names: str) -> BaseTool | None:
        candidates = {name for name in tool_names if name}
        for tool in self._tools_for_route() or []:
            if tool.name in candidates:
                return tool
        return None


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
            "If the user explicitly asks to use a Skill, a knowledge base, MCP, terminal, or a specific tool, prefer the matching capability instead of a generic answer.",
            "If the user asks to search project资料、知识库、文档库、RAG, prefer search_knowledge_base when available.",
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
                if route_tools:
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

                if agent.is_mcp_tool(tool_name):
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
                    result_text = getattr(tool_result, "content", str(tool_result))
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
                    "type": "MCP工具",
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

            db_tools = await ToolService.get_tools_from_id(self.plugins)
            for db_tool in db_tools:
                if db_tool.is_user_defined:
                    runtime_type = get_user_defined_runtime_type(db_tool)
                    runtime_label = "CLI工具" if runtime_type == "cli" else "远程API工具"
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
            return await RagHandler.retrieve_ranked_documents(
                query,
                self.knowledge_ids,
                self.knowledge_ids,
            )

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
                "message": "Agent 已识别为带参考图的生成任务，直接调用生图能力",
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
                "message": "正在根据上传图片生成新图",
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

            results = await self.react_agent.ainvoke({"messages": normalized_messages})
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
        if session:
            return session.get("title")

        title_prompt = GenerateTitlePrompt.format(query=query)
        response = await self.model.ainvoke(
            title_prompt,
            config={"callbacks": [usage_metadata_callback]},
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

    async def _run_direct_routed_tool(
        self,
        tool: BaseTool,
        args: dict[str, Any],
        original_query: str,
    ) -> AsyncGenerator[WorkspaceAgentStreamEvent, None]:
        tool_type, display_name = self._tool_display_info(tool.name)
        tool_call_id = f"direct-{tool.name}-{uuid.uuid4().hex[:8]}"
        yield self._wrap_event(
            "status",
            {
                "phase": "route",
                "status": "START",
                "message": f"已按显式命令直达 {self.route_hint.kind} 能力",
                "route": self.route_hint.model_dump(),
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
        if self.is_mcp_tool(tool.name):
            mcp_config = await MCPUserConfigService.get_mcp_user_config(
                self.user_id,
                self.get_mcp_id_by_tool(tool.name),
            )
            call_args.update(mcp_config)
        result = await tool.ainvoke(call_args)
        result_text = result if isinstance(result, str) else str(result)
        yield self._wrap_event(
            "tool_result",
            {
                "tool_name": tool.name,
                "tool_type": tool_type,
                "tool_call_id": tool_call_id,
                "ok": True,
                "result": result_text,
                "message": f"{display_name} 已返回结果",
            },
        )
        title = await self._generate_title(original_query)
        await self._add_workspace_session(
            title,
            WorkSpaceSessionContext(query=original_query, answer=result_text),
        )
        yield self._wrap_event(
            "final",
            {
                "chunk": result_text,
                "message": result_text,
                "accumulated": result_text,
                "done": True,
            },
        )

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
                "所以我还不能真正访问你 Windows 本机的文件系统或执行本地命令。"
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
        route_tools = self._tools_for_route() or []
        logger.info(
            f"workspace direct route check: query={original_query!r} explicit={explicit_command} "
            f"route_hint={self.route_hint.model_dump()} "
            f"route_tools={[tool.name for tool in route_tools]} "
            f"cleaned={cleaned_route_query!r}"
        )
        if explicit_command and self.route_hint.kind == "knowledge" and route_tools:
            async for event in self._run_direct_routed_tool(
                route_tools[0],
                {"query": cleaned_route_query or original_query},
                original_query,
            ):
                yield event
            return
        if explicit_command and self.route_hint.kind == "skill" and route_tools:
            async for event in self._run_direct_routed_tool(
                route_tools[0],
                {"query": cleaned_route_query or original_query},
                original_query,
            ):
                yield event
            return
        if explicit_command and self.route_hint.kind == "mcp":
            direct_tool, direct_args = self._guess_direct_mcp_call(original_query)
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
            async for mode, payload in self.react_agent.astream(
                input={
                    "messages": user_messages,
                    "tool_call_count": 0,
                    "model_call_count": 0,
                    "user_id": self.user_id,
                },
                config={"callbacks": [usage_metadata_callback]},
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
                return self._canonical_mcp_target(server_name)
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
        slash = re.match(r"^/([a-zA-Z_\-一-鿿]+)(?:\s+(.+))?$", text)
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
                city = cleaned.replace("天气", "").strip(" ，。？?") or "杭州"
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
