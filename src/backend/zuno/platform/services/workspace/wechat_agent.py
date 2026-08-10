import asyncio
import hashlib
from typing import Any, Awaitable, Callable, Dict, List

from loguru import logger
from pydantic import BaseModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from zuno.api.services.knowledge import KnowledgeService
from zuno.api.services.mcp_user_config import MCPUserConfigService
from zuno.api.services.usage_stats import UsageStatsService
from zuno.api.services.workspace_session import WorkSpaceSessionService
from zuno.api.services.user import UserService
from zuno.platform.services.rag.handler import RagHandler
from zuno.capability.control_plane import ToolSideEffectLevel
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
    BlockedConfiguration,
    WorkspaceAgentRuntime,
    WorkspaceRunRequest,
    WorkspaceToolBinding,
    declared_policy_from_metadata,
    get_workspace_product_composition,
)
from zuno.agent.runtime import PROFILE_DEVELOPER_TEST, PROFILE_PRODUCT


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


async def generate_wechat_title(
    *,
    model: Any,
    session_id: Any,
    user_id: Any,
    query: str,
) -> str:
    """Module-level WeChat title generation helper.

    Lives outside the channel adapter and keeps title generation behind the
    configured model gateway.
    """
    session = await WorkSpaceSessionService.get_workspace_session_from_id(session_id, user_id)
    if session:
        return session.get("title")
    title_prompt = GenerateTitlePrompt.format(query=query)
    response = await model.ainvoke(input=title_prompt)
    return WorkSpaceSessionService.normalize_session_title(response.content, fallback_query=query)


async def execute_wechat_binding_tool(
    *,
    binding: Any,
    args: Dict[str, Any],
    user_id: Any,
    mcp_user_config_resolver: Callable[[str, str], Awaitable[Dict[str, Any]]] | None = None,
    is_mcp_tool: Callable[[str], bool] | None = None,
    mcp_tool_id_resolver: Callable[[str], str] | None = None,
    tool_adapter_registry: Any = None,
    tool_id: str | None = None,
    tenant_id: str = "",
    workspace_id: str = "",
    principal_id: str = "",
    run_id: str = "",
    step_run_id: str = "",
    trace_id: str = "",
    approved_artifact: Dict[str, Any] | None = None,
) -> Any:
    """Module-level WeChat binding execution helper.

    Every ``binding.ainvoke`` call routes
    through the registered ``MCPToolExecutorAdapter`` /
    ``ToolInvocationGateway``. A production call without a registered
    adapter fails closed BEFORE the LangChain tool is dispatched.
    Calls without a registered adapter fail closed.
    """
    from zuno.capability.mcp.mcp_tool_executor_adapter import (
        MCPToolAdapterNotBound,
    )
    from zuno.platform.services.workspace.simple_agent import (
        execute_binding_tool as _workspace_execute_binding_tool,
    )

    call_args = dict(args)
    if (
        is_mcp_tool is not None
        and mcp_user_config_resolver is not None
        and mcp_tool_id_resolver is not None
        and is_mcp_tool(binding.name)
    ):
        mcp_config = await mcp_user_config_resolver(
            user_id,
            mcp_tool_id_resolver(binding.name),
        )
        call_args.update(mcp_config)

    if tool_adapter_registry is None:
        raise MCPToolAdapterNotBound(
            f"execute_wechat_binding_tool requires tool_adapter_registry for tool={binding.name!r}"
        )

    # WeChat delegates to the workspace adapter so registry lookup and
    # gateway execution use one canonical path.
    return await _workspace_execute_binding_tool(
        binding=binding,
        args=call_args,
        user_id=user_id,
        mcp_user_config_resolver=mcp_user_config_resolver,
        is_mcp_tool=is_mcp_tool,
        mcp_tool_id_resolver=mcp_tool_id_resolver,
        mcp_requires_user_config=None,
        tool_adapter_registry=tool_adapter_registry,
        tool_id=tool_id or f"tool.{binding.name}",
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        principal_id=principal_id,
        run_id=run_id,
        step_run_id=step_run_id,
        trace_id=trace_id,
        approved_artifact=approved_artifact,
    )


class WeChatAgent:
    """WeChat product adapter over the canonical Single Controller Runtime.

    Every request is
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
                 mcp_configs: List[MCPConfig] = [],
                 runtime_profile: str = PROFILE_PRODUCT,
                 tenant_id: str = "",
                 workspace_id: str = "",
                 budget_limits: dict[str, Any] | None = None):

        # Reject unauthenticated channel requests before constructing model,
        # MCP, or runtime dependencies. The WeChat callback has no tenant /
        # workspace authority of its own, so failing closed must also avoid
        # external provider calls and tool discovery side effects.
        self._tenant_id = str(tenant_id or "").strip()
        self._workspace_id = str(workspace_id or "").strip()
        if not self._tenant_id or not self._workspace_id:
            raise BlockedConfiguration(
                "BLOCKED_CONFIGURATION: product runtime requires a real tenant_id and "
                "workspace_id from the product request/auth context; missing product "
                "context must not fall back to a synthetic identity"
            )

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
        # Composition profile + product submission identity.
        self.runtime_profile = runtime_profile
        self._submission_counter = 0
        # Real tenant / workspace identity from the product request / auth
        # context; no synthetic tenant:default and no workspace derived from
        # user_id. Missing identity fails closed with BLOCKED_CONFIGURATION.
        # Request-declared runtime limits flow into
        # the formal Budget Admission resolver (never self-attested).
        self._budget_limits = dict(budget_limits or {})
        # Tool gateway-bound runtime identity.
        from zuno.capability.mcp.mcp_tool_executor_adapter import (
            MCPToolExecutorAdapterRegistry,
        )

        self._tool_adapter_registry: MCPToolExecutorAdapterRegistry = (
            MCPToolExecutorAdapterRegistry()
        )
        self._runtime_run_id = (
            f"wechat-run:{session_id}:{user_id}"
        )
        self._step_run_id = ""
        self._trace_id = ""

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
            composition = get_workspace_product_composition()
            if composition is None:
                if self.runtime_profile != PROFILE_DEVELOPER_TEST:
                    raise BlockedConfiguration(
                        "BLOCKED_CONFIGURATION: workspace product composition not configured; "
                        "cannot initialize a product runtime"
                    )
                from zuno.platform.services.workspace.single_controller_runtime import (
                    WorkspaceRuntimeComposition,
                )

                composition = WorkspaceRuntimeComposition()
            if composition.store is None and self.runtime_profile != PROFILE_DEVELOPER_TEST:
                raise BlockedConfiguration(
                    "BLOCKED_CONFIGURATION: product composition has no durable AgentRunStore binding"
                )
            if not self._tenant_id or not self._workspace_id:
                raise BlockedConfiguration(
                    "BLOCKED_CONFIGURATION: product runtime requires a real tenant_id and "
                    "workspace_id from the product request/auth context; missing product "
                    "context must not fall back to a synthetic identity"
                )
            self._runtime = WorkspaceAgentRuntime(
                model=self.model,
                bindings=self.bindings,
                tenant_id=self._tenant_id,
                workspace_id=self._workspace_id,
                principal_id=self.user_id,
                profile=(
                    PROFILE_DEVELOPER_TEST
                    if self.runtime_profile == PROFILE_DEVELOPER_TEST
                    else PROFILE_PRODUCT
                ),
                store=composition.store,
                sqlite_store_path=None,
                security_approval_sink=composition.security_approval_sink,
                tool_unit_of_work_factory=composition.tool_unit_of_work_factory,
                security_unit_of_work_factory=composition.security_unit_of_work_factory,
                infrastructure_unit_of_work_factory=composition.infrastructure_unit_of_work_factory,
                security_epoch_ref=composition.security_epoch_ref,
                approval_flow=composition.approval_flow,
                security_decision_resolver=composition.security_decision_resolver,
                budget_decision_resolver=composition.budget_decision_resolver,
                dynamic_dag_planner=composition.dynamic_dag_planner,
            )
            self._initialized = True
            logger.info("WeChat Agent initialized with canonical runtime")
        except Exception as err:
            logger.error(f"Failed to initialize WeChat Agent: {err}")
            raise

    # -- governed bindings --------------------------------------------------

    def _build_bindings(self) -> List[WorkspaceToolBinding]:
        # Policy is declared by the tool owner at
        # registration time (structured tool metadata); never inferred from
        # the tool name. Undeclared tools fail closed with
        # UNRESOLVED_TOOL_POLICY at execution.
        bindings: List[WorkspaceToolBinding] = []
        for tool in self.tools:
            declared = declared_policy_from_metadata(getattr(tool, "metadata", None))
            if declared is None:
                bindings.append(
                    WorkspaceToolBinding(
                        tool_id=f"tool.{tool.name}",
                        display_name=tool.name,
                        description=str(getattr(tool, "description", "") or ""),
                        input_schema=self._tool_input_schema(tool),
                        side_effect_level=ToolSideEffectLevel.READ,
                        executor=lambda args, t=tool: self._execute_binding_tool(t, args),
                        policy_resolution="unresolved",
                    )
                )
                continue
            bindings.append(
                WorkspaceToolBinding(
                    tool_id=f"tool.{tool.name}",
                    display_name=tool.name,
                    description=str(getattr(tool, "description", "") or ""),
                    input_schema=self._tool_input_schema(tool),
                    side_effect_level=declared.side_effect_level,
                    executor=lambda args, t=tool: self._execute_binding_tool(t, args),
                    execution_mode=declared.execution_mode,
                    network_policy=declared.network_policy,
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

    async def _execute_binding_tool(self, tool: Any, args: dict[str, Any]) -> Any:
        """Route through the registered
        ``MCPToolExecutorAdapter`` / ``ToolInvocationGateway``.

        WeChat shares the workspace adapter registry so that the
        registry lookup / gateway path is identical to the workspace
        surface. The ``WeChatAgent`` only injects the binding call into
        the same gateway dispatch that ``WorkSpaceSimpleAgent`` uses.
        """
        return await execute_wechat_binding_tool(
            binding=tool,
            args=args,
            user_id=self.user_id,
            mcp_user_config_resolver=MCPUserConfigService.get_mcp_user_config,
            is_mcp_tool=self.is_mcp_tool,
            mcp_tool_id_resolver=self.get_mcp_id_by_tool,
            tool_adapter_registry=self._tool_adapter_registry,
            tool_id=f"tool.{tool.name}",
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
            principal_id=self.user_id,
            run_id=self._runtime_run_id,
            step_run_id=getattr(self, "_step_run_id", ""),
            trace_id=self._trace_id,
        )

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
        # Run identity is the product submission, never
        # the request text hash.
        self._submission_counter += 1
        client_request_id = f"req:{self.session_id or self.user_id}:{self._submission_counter}"
        submission_id = f"sub:{self.session_id or self.user_id}:{self._submission_counter}"
        task_id = f"wechat:{hashlib.sha256(f'{self._tenant_id}|{self._workspace_id}|{client_request_id}'.encode('utf-8')).hexdigest()[:16]}"
        request = WorkspaceRunRequest(
            task_id=task_id,
            thread_id=self.session_id or task_id,
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
            principal_id=self.user_id,
            submission_id=submission_id,
            client_request_id=client_request_id,
            user_id=self.user_id,
            trace_id=f"trace:{task_id}",
            goal=goal,
            conversation_id=self.session_id,
            agent_version="wechat-adapter-v1",
            content_fingerprint=f"content:{hashlib.sha256(goal.encode('utf-8')).hexdigest()[:16]}",
            plan_kind="simple",
            budget_limits=self._budget_limits or None,
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
        return await generate_wechat_title(
            model=self.model,
            session_id=self.session_id,
            user_id=self.wechat_account_user,
            query=query,
        )

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
