import asyncio
import copy
import time
from typing import Any, AsyncGenerator, Callable, Dict, List, NotRequired

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool, tool
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime
from langgraph.types import Command
from loguru import logger
from pydantic import BaseModel

from zuno.api.services.agent_skill import AgentSkillService
from zuno.api.services.llm import LLMService
from zuno.api.services.mcp_server import MCPService
from zuno.api.services.mcp_user_config import MCPUserConfigService
from zuno.api.services.tool import ToolService
from zuno.core.callbacks import usage_metadata_callback
from zuno.core.models.manager import ModelManager
from zuno.database import AgentSkill
from zuno.services.application.capabilities import (
    CapabilityCost,
    CapabilityHealth,
    CapabilityPermissions,
    CapabilityRecord,
    CapabilityRegistry,
    CapabilitySelectionRequest,
    CapabilitySelectionResult,
    CapabilityType,
    DynamicCapabilitySelector,
)
from zuno.services.application.context import (
    AgentExecutionContext,
    ContextOrchestrator,
    ContextItem,
    ContextPreparationInput,
    ContextSelectionReason,
    ContextSource,
    ModelContextPacket,
    TokenBudgetPolicy,
)
from zuno.services.application.knowledge import KnowledgeQueryService
from zuno.services.memory import (
    InMemoryLayerStore,
    MemoryLayer,
    MemoryScope,
    RawMemoryEvent,
    TaskMemorySummary,
)
from zuno.services.mcp.manager import MCPManager
from zuno.services.user_defined_tool_runtime import build_user_defined_langchain_tools
from zuno.tools import AgentToolsWithName
from zuno.utils.convert import convert_mcp_config
from zuno.utils.helpers import parse_imported_config
from zuno.utils.model_output import (
    extract_visible_text_from_stream,
    is_minimax_model,
    normalize_messages_for_model,
)


class StreamAgentState(AgentState):
    tool_call_count: NotRequired[int]
    model_call_count: NotRequired[int]
    user_id: NotRequired[str]
    model_context_packet: NotRequired[dict[str, Any]]
    context_trace: NotRequired[dict[str, Any]]


class AgentConfig(BaseModel):
    user_id: str
    llm_id: str
    mcp_ids: List[str]
    knowledge_ids: List[str]
    domain_pack_id: str | None = None
    dialog_id: str | None = None
    tool_ids: List[str]
    agent_skill_ids: List[str]
    system_prompt: str
    enable_memory: bool = False
    name: str | None = None
    retrieval_profile: str | None = None
    eval_profile_id: str | None = None
    graph_capability: str | None = None
    multi_agent_enabled: bool = False


class EmitEventAgentMiddleware(AgentMiddleware):
    def __init__(
        self,
        name_resolver_func: Callable[[str], tuple[str, str]],
        mcp_checker: Callable[[str], bool],
        mcp_id_resolver: Callable[[str], str | None],
        user_id: str,
    ):
        super().__init__()
        self.name_resolver_func = name_resolver_func
        self.mcp_checker = mcp_checker
        self.mcp_id_resolver = mcp_id_resolver
        self.user_id = user_id

    async def aafter_model(
        self, state: StreamAgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return {"model_call_count": state.get("model_call_count", 0) + 1}
        return {"jump_to": "end"}

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        try:
            return await handler(request)
        except Exception as err:
            logger.error(f"Model call error: {err}")
            raise ValueError(err)

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        writer = get_stream_writer()
        tool_name = request.tool_call["name"]
        tool_type, display_name = self.name_resolver_func(tool_name)
        writer(
            {
                "status": "START",
                "title": f"执行{tool_type}: {display_name}",
                "message": f"正在调用 {display_name}...",
            }
        )

        if self.mcp_checker(tool_name):
            try:
                mcp_server_id = self.mcp_id_resolver(tool_name)
                if mcp_server_id:
                    mcp_config = await MCPUserConfigService.get_mcp_user_config(
                        self.user_id,
                        mcp_server_id,
                    )
                    request.tool_call["args"].update(mcp_config)
            except Exception as err:
                error_text = str(err)
                writer(
                    {
                        "status": "ERROR",
                        "title": f"执行{tool_type}: {display_name}",
                        "message": error_text,
                    }
                )
                return ToolMessage(
                    content=error_text,
                    name=tool_name,
                    tool_call_id=request.tool_call["id"],
                )

        try:
            tool_result = await handler(request)
            writer(
                {
                    "status": "END",
                    "title": f"执行{tool_type}: {display_name}",
                    "message": getattr(tool_result, "content", str(tool_result)),
                }
            )
            return tool_result
        except Exception as err:
            error_text = str(err)
            writer(
                {
                    "status": "ERROR",
                    "title": f"执行{tool_type}: {display_name}",
                    "message": error_text,
                }
            )
            return ToolMessage(
                content=error_text,
                name=tool_name,
                tool_call_id=request.tool_call["id"],
            )


class GeneralAgent:
    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.conversation_model = None
        self.react_agent = None

        self.tools: list[BaseTool] = []
        self.mcp_tools: list[BaseTool] = []
        self.skill_tools: list[BaseTool] = []
        self.middlewares: list[AgentMiddleware] = []
        self.tool_metadata_map: Dict[str, Dict[str, str]] = {}
        self.mcp_tool_server_map: Dict[str, str] = {}
        self.memory_layer_store = InMemoryLayerStore()
        self.last_model_context_packet: ModelContextPacket | None = None
        self.last_capability_selection: CapabilitySelectionResult | None = None

        self.event_queue = asyncio.Queue()
        self.stop_streaming = False

    def wrap_event(self, data: Dict[Any, Any]):
        return {
            "type": "event",
            "timestamp": time.time(),
            "data": data,
        }

    async def init_agent(self):
        self.mcp_tools = await self.setup_mcp_tools()
        self.tools = await self.setup_tools()
        self.skill_tools = await self.setup_skill_tools()
        await self.setup_knowledge_tool()
        await self.setup_language_model()
        self.middlewares = await self.setup_agent_middleware()
        self.react_agent = self.setup_react_agent()

    def prepare_context(self, messages: List[BaseMessage]) -> ModelContextPacket:
        task = self._extract_latest_user_query(messages)
        token_budget = TokenBudgetPolicy(max_tokens=4000, reserved_response_tokens=800)
        execution_context = AgentExecutionContext(
            trace_id=f"ga-{int(time.time() * 1000)}",
            user_id=self.agent_config.user_id,
            agent_id=self.agent_config.name or "general_agent",
            thread_id=self.agent_config.dialog_id or "",
            project_id=self.agent_config.knowledge_ids[0] if self.agent_config.knowledge_ids else None,
            task=task,
        )

        selected_capabilities = DynamicCapabilitySelector(
            CapabilityRegistry(self._available_capability_records())
        ).select(
            CapabilitySelectionRequest(
                task=task,
                max_capabilities=8,
            )
        )
        self.last_capability_selection = selected_capabilities

        capability_items: list[ContextItem] = []
        for capability in selected_capabilities.capabilities:
            capability_items.append(
                ContextItem(
                    item_id=capability.name,
                    source=ContextSource.CAPABILITY_SCHEMA,
                    content=str(capability.to_dict()),
                    token_estimate=self._estimate_tokens(str(capability.schema)) + 20,
                    priority=70,
                    reason=ContextSelectionReason.CAPABILITY_SELECTED,
                    metadata={"capability_type": capability.type.value},
                )
            )

        packet = ContextOrchestrator().prepare(
            ContextPreparationInput(
                execution_context=execution_context,
                messages=tuple(messages),
                system_instruction=self.agent_config.system_prompt,
                token_budget=token_budget,
                capability_items=tuple(capability_items),
            )
        ).packet
        self.last_model_context_packet = packet
        return packet

    def post_turn_commit(
        self,
        *,
        messages: List[BaseMessage],
        response: str,
        context_packet: ModelContextPacket,
    ) -> None:
        if not self.agent_config.enable_memory:
            return
        event = RawMemoryEvent(
            event_id=f"{context_packet.execution_context.trace_id}:turn",
            scope=self._memory_scope(),
            event_type="agent_turn",
            payload={
                "task": self._extract_latest_user_query(messages),
                "response": response,
                "context_trace": context_packet.trace.to_dict(),
            },
            layer=MemoryLayer.WORKING,
        )
        self.memory_layer_store.append_raw_event(event)
        self.memory_layer_store.save_task_summary(
            TaskMemorySummary(
                summary_id=f"{event.event_id}:summary",
                scope=event.scope,
                layer=MemoryLayer.TASK,
                content=response or event.payload["task"],
                source_event_ids=(event.event_id,),
                token_count=self._estimate_tokens(response or event.payload["task"]),
            )
        )

    def _available_capability_records(self) -> list[CapabilityRecord]:
        records: list[CapabilityRecord] = []
        for tool_item in self.tools:
            capability_type = (
                CapabilityType.KNOWLEDGE
                if getattr(tool_item, "name", "") == "search_knowledge_base"
                else CapabilityType.ACTION_TOOL
            )
            records.append(self._tool_capability_record(tool_item, capability_type))
        for tool_item in self.mcp_tools:
            records.append(self._tool_capability_record(tool_item, CapabilityType.MCP_TOOL))
        for tool_item in self.skill_tools:
            records.append(self._tool_capability_record(tool_item, CapabilityType.SKILL))
        return records

    def _tool_capability_record(self, tool_item: Any, capability_type: CapabilityType) -> CapabilityRecord:
        name = str(getattr(tool_item, "name", ""))
        description = str(getattr(tool_item, "description", ""))
        return CapabilityRecord(
            name=name,
            type=capability_type,
            description=description,
            schema=dict(getattr(tool_item, "args", {}) or {}),
            permissions=CapabilityPermissions(
                scopes=(f"{capability_type.value}:use",),
                side_effects=capability_type in {CapabilityType.ACTION_TOOL, CapabilityType.MCP_TOOL},
            ),
            cost=CapabilityCost(token_estimate=200),
            health=CapabilityHealth.READY,
            source="general_agent_runtime",
            owner="GeneralAgent",
            tags=tuple(part for part in [name.replace("_", " "), description] if part),
        )

    def _memory_scope(self) -> MemoryScope:
        return MemoryScope(
            user_id=self.agent_config.user_id,
            agent_id=self.agent_config.name or "general_agent",
            project_id=self.agent_config.knowledge_ids[0] if self.agent_config.knowledge_ids else None,
            thread_id=self.agent_config.dialog_id,
        )

    async def setup_agent_middleware(self):
        return [
            EmitEventAgentMiddleware(
                self.get_tool_display_name,
                self.is_mcp_tool,
                self.get_mcp_id_by_tool,
                self.agent_config.user_id,
            )
        ]

    async def setup_language_model(self):
        if self.agent_config.llm_id:
            model_config = await LLMService.get_llm_by_id(self.agent_config.llm_id)
            self.conversation_model = ModelManager.get_user_model(**model_config)
        else:
            self.conversation_model = ModelManager.get_conversation_model()

    def setup_react_agent(self):
        runtime_system_prompt = "\n".join(
            line
            for line in [
                self.agent_config.system_prompt.strip(),
                "Use available tools directly. Do not invent tool results.",
                "Skills are guidance assets. Read them when helpful, then continue solving the task in the same agent.",
                "MCP servers are available as direct tools. If a matching MCP tool exists, call it instead of only describing capabilities.",
                "When knowledge bases are enabled and the task asks for project资料、知识库、文档库或RAG信息, prefer search_knowledge_base.",
            ]
            if line
        )
        return create_agent(
            model=self.conversation_model,
            tools=self.tools + self.mcp_tools + self.skill_tools,
            middleware=self.middlewares,
            state_schema=StreamAgentState,
            system_prompt=runtime_system_prompt,
        )

    async def setup_tools(self) -> List[BaseTool]:
        tools: list[BaseTool] = []
        db_tools = await ToolService.get_tools_from_id(self.agent_config.tool_ids)
        for db_tool in db_tools:
            if db_tool.is_user_defined:
                tools.extend(
                    build_user_defined_langchain_tools(
                        db_tool,
                        self.tool_metadata_map,
                    )
                )
                continue

            agent_tool = AgentToolsWithName.get(db_tool.name)
            if agent_tool:
                tools.append(agent_tool)
            self.tool_metadata_map[db_tool.name] = {
                "name": db_tool.display_name,
                "type": "工具",
            }

        default_web_tools = {
            "web_search": "联网搜索",
            "read_webpage": "读取网页",
        }
        existing_tool_names = {tool.name for tool in tools}
        for tool_name, display_name in default_web_tools.items():
            default_tool = AgentToolsWithName.get(tool_name)
            if default_tool and default_tool.name not in existing_tool_names:
                tools.append(default_tool)
                self.tool_metadata_map[default_tool.name] = {
                    "name": display_name,
                    "type": "工具",
                }

        return tools

    async def setup_skill_tools(self) -> List[BaseTool]:
        skill_tools: list[BaseTool] = []
        agent_skills = await AgentSkillService.get_agent_skills_by_ids(self.agent_config.agent_skill_ids)

        def create_skill_tool(agent_skill: AgentSkill):
            @tool(agent_skill.as_tool_name, description=agent_skill.description)
            async def load_skill_context(query: str) -> str:
                """加载 Skill 内容，由当前主 Agent 直接使用。"""
                skill_context = AgentSkillService.build_skill_runtime_context(agent_skill, query=query)
                return (
                    f"You selected Skill '{agent_skill.name}'. Use the following skill package as guidance "
                    f"for the current task in this same conversation. Do not claim the skill has already "
                    f"executed unless you actually use other tools afterwards.\n\n{skill_context}"
                )

            return load_skill_context

        for agent_skill in agent_skills:
            self.tool_metadata_map[agent_skill.as_tool_name] = {
                "name": agent_skill.name,
                "type": "Skill",
            }
            skill_tools.append(create_skill_tool(agent_skill))

        return skill_tools

    async def setup_mcp_tools(self) -> List[BaseTool]:
        mcp_servers = []
        for mcp_id in self.agent_config.mcp_ids:
            mcp_server = await MCPService.get_mcp_server_from_id(mcp_id)
            if not mcp_server:
                continue

            if mcp_server.get("imported_config"):
                imported_info = parse_imported_config(mcp_server["imported_config"])
                server_info = {
                    "server_name": imported_info.name or mcp_server.get("server_name", ""),
                    "type": imported_info.type or mcp_server.get("type", "sse"),
                    "url": imported_info.url or "",
                    "headers": imported_info.headers,
                    "command": imported_info.command,
                    "args": imported_info.args or [],
                    "env": imported_info.env,
                    "env_passthrough": imported_info.env_passthrough or [],
                    "cwd": imported_info.cwd,
                }
            else:
                server_info = {
                    "server_name": mcp_server.get("server_name", ""),
                    "type": mcp_server.get("type", "sse"),
                    "url": mcp_server.get("url", "") or "",
                    "headers": None,
                    "command": None,
                    "args": [],
                    "env": None,
                    "env_passthrough": [],
                    "cwd": None,
                }

            for tool_name in mcp_server.get("tools") or []:
                self.mcp_tool_server_map[tool_name] = mcp_server.get("mcp_server_id", "")

            mcp_servers.append(server_info)

        if not mcp_servers:
            return []

        manager = MCPManager(convert_mcp_config(mcp_servers))
        mcp_tools = await manager.get_mcp_tools()
        for tool in mcp_tools:
            self.tool_metadata_map[tool.name] = {
                "name": tool.name,
                "type": "MCP",
            }
        return mcp_tools

    async def setup_knowledge_tool(self):
        @tool(parse_docstring=True)
        async def search_knowledge_base(query: str) -> str:
            """
            通过检索知识库来获取信息。

            Args:
                query: 用户问题
            """
            result = await KnowledgeQueryService().query(
                user_id=self.agent_config.user_id,
                knowledge_ids=self.agent_config.knowledge_ids,
                query=query,
            )
            return self._format_knowledge_query_result(result)

        if self.agent_config.knowledge_ids:
            self.tools.append(search_knowledge_base)
            self.tool_metadata_map[search_knowledge_base.name] = {
                "name": "检索知识库",
                "type": "工具",
            }

    @staticmethod
    def _format_knowledge_query_result(result) -> str:
        lines = [str(result.answer or "").strip()]
        if result.citations:
            lines.append(f"citations: {', '.join(result.citations)}")
        if result.resolved_query_method:
            lines.append(f"resolved_query_method: {result.resolved_query_method}")
        if result.retrievers_used:
            lines.append(f"retrievers_used: {', '.join(result.retrievers_used)}")
        return "\n".join(line for line in lines if line)

    @staticmethod
    def _extract_latest_user_query(messages: List[BaseMessage]) -> str:
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return str(message.content or "").strip()
        if messages:
            return str(getattr(messages[-1], "content", "") or "").strip()
        return ""

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    async def astream(self, messages: List[BaseMessage]) -> AsyncGenerator[Dict[str, Any], None]:
        response_content = ""
        context_packet = self.prepare_context(messages)
        visible_messages = copy.deepcopy(
            normalize_messages_for_model(messages, model=self.conversation_model)
        )
        inside_think = False
        try:
            async for token, metadata in self.react_agent.astream(
                input={
                    "messages": visible_messages,
                    "model_call_count": 0,
                    "user_id": self.agent_config.user_id,
                    "model_context_packet": context_packet.to_dict(),
                    "context_trace": context_packet.trace.to_dict(),
                },
                config={"callbacks": [usage_metadata_callback]},
                stream_mode=["messages", "custom"],
            ):
                if token == "custom":
                    yield self.wrap_event(metadata)
                elif isinstance(metadata[0], AIMessageChunk) and metadata[0].content:
                    visible_chunk = metadata[0].content
                    if is_minimax_model(model=self.conversation_model):
                        visible_chunk, inside_think = extract_visible_text_from_stream(
                            metadata[0].content, inside_think
                        )
                    if not visible_chunk:
                        continue

                    response_content += visible_chunk
                    yield {
                        "type": "response_chunk",
                        "timestamp": time.time(),
                        "data": {
                            "chunk": visible_chunk,
                            "accumulated": response_content,
                        },
                    }
        except Exception as err:
            logger.error(f"LLM Model Error: {err}")
            yield {
                "type": "response_chunk",
                "timestamp": time.time(),
                "data": {
                    "chunk": "对话生成失败，请稍后重试。",
                    "accumulated": response_content,
                },
            }
        finally:
            self.post_turn_commit(
                messages=messages,
                response=response_content,
                context_packet=context_packet,
            )

    def stop_streaming_callback(self):
        self.stop_streaming = True

    def get_tool_display_name(self, tool_name: str):
        metadata = self.tool_metadata_map.get(tool_name)
        if not metadata:
            return "工具", tool_name
        return metadata.get("type", "工具"), metadata.get("name", tool_name)

    def is_mcp_tool(self, tool_name: str) -> bool:
        return tool_name in self.mcp_tool_server_map

    def get_mcp_id_by_tool(self, tool_name: str) -> str | None:
        return self.mcp_tool_server_map.get(tool_name)
