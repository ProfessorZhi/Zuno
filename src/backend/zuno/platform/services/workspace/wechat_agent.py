import asyncio
import hashlib
import tempfile
from pathlib import Path
from typing import List, Any

from loguru import logger
from pydantic import BaseModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from zuno.api.services.knowledge import KnowledgeService
from zuno.api.services.mcp_user_config import MCPUserConfigService
from zuno.api.services.usage_stats import UsageStatsService
from zuno.api.services.workspace_session import WorkSpaceSessionService
from zuno.api.services.user import UserService
from zuno.platform.services.rag.handler import RagHandler
from zuno.capability.control_plane import ToolExecutionMode, ToolSideEffectLevel
from zuno.capability.tools import WeChatTools
from zuno.api.dto.usage_stats import UsageStatsAgentType
from zuno.api.dto.workspace import WorkSpaceAgents
from zuno.platform.services.mcp.manager import MCPManager
from zuno.platform.resources.prompts.completion import GenerateTitlePrompt
from zuno.platform.common.convert import convert_mcp_config
from zuno.agent.core.models.manager import ModelManager
from zuno.platform.database.models.workspace_session import WorkSpaceSessionCreate, WorkSpaceSessionContext
from zuno.platform.common.model_output import (
    extract_visible_text_from_stream,
    is_minimax_model,
    normalize_messages_for_model,
    strip_model_wrapper_from_user_input,
    strip_think_tags,
)
from zuno.platform.services.workspace.single_controller_runtime import (
    WorkspaceAgentRuntime,
    WorkspaceRunRequest,
    WorkspaceToolBinding,
)


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


class WeChatAgent:
    """WeChat product adapter over the canonical Single Controller Runtime.

    PHASE22 cutover: the previous independent langchain prebuilt-agent ReAct
    runtime and direct model answer generation are removed. Every request is
    planned and executed by the canonical runtime (security / approval /
    budget gates, tool control plane, run outcome); the adapter only converts
    the channel request to ``WorkspaceRunRequest`` and maps the run back to
    the WeChat message contract.
    """

    def __init__(self,
                 user_id: str,
                 session_id: str,
                 wechat_account_user: str = None,
                 plugins: List[str] = [],
                 mcp_configs: List[MCPConfig] = []):

        # The chat model is used by the canonical runtime's model steps via
        # the workspace model gateway; the adapter never answers directly.
        self.model = ModelManager.get_conversation_model()
        self.plugin_tools = []
        self.mcp_tools = []
        self.mcp_configs = mcp_configs
        self.tools = []
        self.mcp_manager = MCPManager(convert_mcp_config([mcp_config.model_dump() for mcp_config in mcp_configs]))
        self.plugins = plugins
        self.session_id = session_id
        self.wechat_account_user = wechat_account_user
        self.user_id = user_id
        self.server_dict: dict[str, Any] = {}
        self.bindings: list[WorkspaceToolBinding] = []
        self._runtime: WorkspaceAgentRuntime | None = None
        self._initialized = False

    async def init_wechat_agent(self):
        """Initialize the canonical composition root for this session."""
        try:
            if self._initialized:
                logger.info("WeChat Agent already initialized")
                return
            await self.setup_mcp_tools()
            await self.setup_plugin_tools()
            self.tools = self.plugin_tools + self.mcp_tools
            self.bindings = self._build_bindings()
            self._runtime = WorkspaceAgentRuntime(
                model=self.model,
                bindings=self.bindings,
                store_path=Path(tempfile.gettempdir())
                / f"zuno_wechat_agent_{self.user_id}_{self.session_id}.db",
            )
            self._initialized = True
            logger.info("WeChat Agent initialized with canonical runtime")
        except Exception as err:
            logger.error(f"Failed to initialize WeChat Agent: {err}")
            raise

    # -- governed bindings --------------------------------------------------

    def _build_bindings(self) -> List[WorkspaceToolBinding]:
        bindings: List[WorkspaceToolBinding] = []
        for tool in self.tools:
            bindings.append(
                WorkspaceToolBinding(
                    tool_id=f"tool.{tool.name}",
                    display_name=tool.name,
                    description=str(getattr(tool, "description", "") or ""),
                    input_schema=self._tool_input_schema(tool),
                    side_effect_level=self._classify_tool_effect(tool.name),
                    executor=lambda args, t=tool: self._execute_binding_tool(t, args),
                    execution_mode=self._tool_execution_mode(tool.name),
                    network_policy="allow" if self._tool_has_network(tool.name) else "deny",
                )
            )
        return bindings

    @staticmethod
    def _tool_input_schema(tool: Any) -> dict[str, Any]:
        args_schema = getattr(tool, "args_schema", None)
        if args_schema is not None:
            schema = getattr(args_schema, "model_json_schema", None)
            if schema is not None:
                try:
                    return dict(schema())
                except Exception:
                    pass
        return {"type": "object"}

    @staticmethod
    def _classify_tool_effect(tool_name: str) -> ToolSideEffectLevel:
        name = (tool_name or "").lower()
        if any(token in name for token in ("send_", "email", "text_to_image", "post_", "submit_")):
            return ToolSideEffectLevel.WRITE_EXTERNAL
        if name.startswith(("create_", "update_", "delete_", "write_", "convert_", "add_", "save_")):
            return ToolSideEffectLevel.WRITE_LOCAL
        return ToolSideEffectLevel.READ

    @staticmethod
    def _tool_execution_mode(tool_name: str) -> ToolExecutionMode:
        name = (tool_name or "").lower()
        if "mcp" in name:
            return ToolExecutionMode.MCP_LOCAL
        return ToolExecutionMode.LOCAL_FUNCTION

    @staticmethod
    def _tool_has_network(tool_name: str) -> bool:
        name = (tool_name or "").lower()
        return any(
            token in name
            for token in ("search", "weather", "web", "api", "remote", "send_", "text_to_image", "email")
        )

    async def _execute_binding_tool(self, tool: Any, args: dict[str, Any]) -> Any:
        call_args = dict(args)
        if self.is_mcp_tool(tool.name):
            mcp_config = await MCPUserConfigService.get_mcp_user_config(
                self.user_id,
                self.get_mcp_id_by_tool(tool.name),
            )
            call_args.update(mcp_config)
        return await tool.ainvoke(call_args)

    async def setup_mcp_tools(self):
        """Initialize MCP tools - with error handling"""
        if not self.mcp_configs:
            self.mcp_tools = []
            return

        try:
            # Establish connection with MCP Server
            self.mcp_tools = await self.mcp_manager.get_mcp_tools()

            mcp_servers_info = await self.mcp_manager.show_mcp_tools()
            self.server_dict = {server_name: [tool["name"] for tool in tools_info] for server_name, tools_info in
                                mcp_servers_info.items()}

            logger.info(f"Loaded {len(self.mcp_tools)} MCP tools from MCP servers")

        except Exception as err:
            logger.error(f"Failed to initialize MCP tools: {err}")
            self.mcp_tools = []

    async def setup_plugin_tools(self):
        """Initialize plugin tools - with error handling"""
        try:
            for tool_name, tool in WeChatTools.items():
                self.plugin_tools.append(tool)

            logger.info(f"Loaded {len(self.plugin_tools)} plugin tools")

        except Exception as err:
            logger.error(f"Failed to initialize plugin tools: {err}")
            self.plugin_tools = []

    async def retrival_knowledge_documents(self, query):
        wechat_account_user_id = UserService.get_user_id_by_name(self.wechat_account_user)
        knowledges = await KnowledgeService.select_knowledge(wechat_account_user_id)
        if not knowledges:
            return None
        collection_name = knowledges[0]["id"]  # 时间有限，只检索一个知识库
        document = await RagHandler.retrieve_ranked_documents(
            top_k=3,
            min_score=0.01,
            query=query,
            index_names=[collection_name],
            collection_names=[collection_name],
            needs_query_rewrite=False
        )

        return document

    # -- canonical run helpers ----------------------------------------------

    async def _run_request(self, goal: str) -> Any:
        if self._runtime is None:
            raise RuntimeError("wechat agent runtime not initialized")
        task_id = f"wechat:{hashlib.sha256(goal.encode('utf-8')).hexdigest()[:16]}"
        request = WorkspaceRunRequest(
            task_id=task_id,
            thread_id=self.session_id or task_id,
            workspace_id=f"workspace:{self.user_id}",
            user_id=self.user_id,
            trace_id=f"trace:{task_id}",
            goal=goal,
            plan_kind="simple",
        )
        return self._runtime.start(request)

    def _final_answer(self, snapshot: Any) -> str:
        response_content = ""
        for obs in snapshot.observations:
            if obs.kind == "model":
                if obs.metadata.get("grounded_synthesis"):
                    grounded = str(obs.metadata.get("final_answer") or "")
                    if grounded:
                        response_content = grounded
                    continue
                model_output = str(obs.metadata.get("model_output") or "")
                if model_output:
                    response_content = model_output
        return response_content

    async def ainvoke(self, messages: List[BaseMessage]):
        """Sub-agent tool execution through the canonical runtime.

        Returns the model answer (AIMessage) produced by the runtime; no
        tool executes outside the runtime and no answer bypasses the plan.
        """
        if not self._initialized:
            await self.init_wechat_agent()
        original_query = strip_model_wrapper_from_user_input(getattr(messages[-1], "content", ""))
        user_messages = list(messages)
        try:
            retrival_result = await self.retrival_knowledge_documents(query=original_query)
            if retrival_result:
                goal = f"{original_query}\n\n## 补充信息\n{retrival_result}"
            else:
                goal = original_query
            snapshot = await asyncio.to_thread(self._run_request, goal)
            if snapshot.finalization_status == "interrupted":
                raise ValueError(
                    "WeChat tool execution requires approval; no side effect was executed. "
                    "Please approve the pending run before continuing."
                )
            if snapshot.finalization_status in {"failed", "blocked", "abstained", "cancelled"}:
                raise ValueError(
                    f"WeChat run did not complete ({snapshot.finalization_status}); no side effect was executed."
                )
        except Exception as err:
            raise ValueError from err

        answer = self._final_answer(snapshot).strip() or "这次请求已经执行完成，但模型没有返回可见正文。"
        await self._add_workspace_session(
            title="微信对话",
            contexts=WorkSpaceSessionContext(
                query=original_query,
                answer=answer
            ))
        return AIMessage(content=answer)

    async def _generate_title(self, query):
        session = await WorkSpaceSessionService.get_workspace_session_from_id(self.session_id, self.wechat_account_user)
        if session:
            return session.get("title")
        title_prompt = GenerateTitlePrompt.format(query=query)
        response = await self.model.ainvoke(input=title_prompt)
        return WorkSpaceSessionService.normalize_session_title(response.content, fallback_query=query)

    async def _add_workspace_session(self, title, contexts: WorkSpaceSessionContext):
        normalized_title = WorkSpaceSessionService.normalize_session_title(title, fallback_query=contexts.query)
        session = await WorkSpaceSessionService.get_workspace_session_from_id(self.session_id, self.wechat_account_user)
        if session:
            await WorkSpaceSessionService.update_workspace_session_contexts(
                session_id=self.session_id,
                session_context=contexts.model_dump()
            )
        else:
            await WorkSpaceSessionService.create_workspace_session(
                WorkSpaceSessionCreate(
                    title=normalized_title,
                    user_id=self.user_id,
                    session_id=self.session_id,
                    contexts=[contexts.model_dump()],
                    agent=WorkSpaceAgents.WeChatAgent.value
                )
            )

    async def astream(self, messages: List[BaseMessage]):
        if not self._initialized:
            await self.init_wechat_agent()
        original_query = strip_model_wrapper_from_user_input(getattr(messages[-1], "content", ""))
        try:
            retrival_result = await self.retrival_knowledge_documents(query=original_query)
            goal = f"{original_query}\n\n## 补充信息\n{retrival_result}" if retrival_result else original_query
            snapshot = await asyncio.to_thread(self._run_request, goal)
        except Exception as err:
            raise ValueError from err

        if snapshot.finalization_status == "interrupted":
            yield {
                "event": "task_result",
                "data": {
                    "message": "该操作需要批准后才能执行。未批准前不会执行任何副作用。"
                },
            }
            return
        if snapshot.finalization_status in {"failed", "blocked", "abstained", "cancelled"}:
            yield {
                "event": "task_result",
                "data": {
                    "message": f"这次执行未完成（{snapshot.finalization_status}）。未产生副作用，可按原计划重试。"
                },
            }
            return

        final_answer = self._final_answer(snapshot).strip() or "这次请求已经执行完成，但模型没有返回可见正文。"
        yield {
            "event": "task_result",
            "data": {
                "message": final_answer
            },
        }

        await self._add_workspace_session(
            title="微信对话",
            contexts=WorkSpaceSessionContext(
                query=original_query,
                answer=final_answer
            ))

    async def _record_agent_token_usage(self, response: AIMessage | BaseMessage, model):
        if response.usage_metadata:
            await UsageStatsService.create_usage_stats(
                model=model,
                user_id=self.user_id,
                agent=UsageStatsAgentType.wechat_agent,
                input_tokens=response.usage_metadata.get("input_tokens"),
                output_tokens=response.usage_metadata.get("output_tokens")
            )

    def is_mcp_tool(self, tool_name: str):
        """Determine if it's an MCP tool and return the corresponding tool instance"""
        mcp_names = [tool.name for tool in self.mcp_tools]
        plugin_names = [tool.name for tool in self.plugin_tools]

        if tool_name in mcp_names:
            return True
        elif tool_name in plugin_names:
            return False
        else:
            raise ValueError(f"Tool '{tool_name}' not found in either MCP or plugin tools.")

    def get_mcp_id_by_tool(self, tool_name):
        for server_name, tools in self.server_dict.items():
            if tool_name in tools:
                for config in self.mcp_configs:
                    if server_name == config.server_name:
                        return config.mcp_server_id
        return None
