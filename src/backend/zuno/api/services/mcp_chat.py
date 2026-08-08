from zuno.api.services.history import HistoryService
from zuno.platform.services.rag.handler import RagHandler


MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND = (
    "MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND: MCP Chat execution requires the "
    "canonical Product Runtime (tenant / workspace / principal / security / "
    "budget context + ToolInvocationGateway + MCPToolExecutorAdapter). The "
    "product context of this endpoint cannot provide them, so execution "
    "fails closed with zero provider calls and zero model calls."
)


class MCPChatCanonicalRuntimeNotBound(RuntimeError):
    """MCP Chat execution fail-closed marker.

    The legacy MCP Chat surface (``MCPChatAgent`` -> ``MCPManager.process_query``
    -> ``MCPUtil.run_mcp_tool`` -> ``MCPClient.call_server_tool``) executed MCP
    provider tools directly, bypassing ``ToolInvocationGateway`` (Security /
    Budget / receipt / idempotency) and held a provider model directly,
    bypassing the Model Gateway. The endpoint has no tenant / workspace /
    principal / security / budget product context, so PHASE22 fails closed:
    the canonical runtime is not bound and no provider or model call is made.
    """


class MCPChatAgent:
    def __init__(self, **kwargs):
        # Agent configuration is retained for contract compatibility; the
        # canonical product context (tenant / workspace / principal /
        # security decision / budget decision) is NOT derivable from it.
        self.mcp_servers_id = kwargs.get("mcp_servers_id")
        self.llm_id = kwargs.get("llm_id")
        self.enable_memory = kwargs.get("enable_memory")
        self.knowledges_id = kwargs.get("knowledges_id")

    async def init_MCP_Server(self):
        """Fail closed: no MCP server connection, no provider client.

        PHASE22: without a canonical runtime binding the agent must not
        connect MCP servers for execution. The endpoint returns
        ``MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND`` instead.
        """
        raise MCPChatCanonicalRuntimeNotBound(MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND)

    async def ainvoke(self, user_input: str, dialog_id: str, stream: bool = False):
        """Fail closed: zero provider calls, zero model calls.

        PHASE22: the legacy direct MCP execution loop is retired. A
        canonical integration would route through the Product Runtime
        (WorkspaceAgentRuntime -> ToolInvocationGateway ->
        MCPToolExecutorAdapter -> MCP provider); this endpoint cannot
        provide the required product context, so it fails closed.
        """
        raise MCPChatCanonicalRuntimeNotBound(MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND)

    async def get_history_message(self, user_input: str, dialog_id: str, top_k: int = 5):
        if self.enable_memory:
            return await self._retrieval_history(user_input, dialog_id, top_k)

        messages = await self._direct_history(dialog_id, top_k)
        return [message.to_json() for message in messages]

    async def _direct_history(self, dialog_id: str, top_k: int):
        return await HistoryService.select_history(dialog_id, top_k)

    async def _retrieval_history(self, user_input: str, dialog_id: str, top_k: int):
        _ = user_input
        return await self._direct_history(dialog_id, top_k)

    async def _get_knowledge_context(self, user_input: str):
        if not self.knowledges_id:
            return ""

        if isinstance(self.knowledges_id, str):
            collection_names = [self.knowledges_id]
        else:
            collection_names = list(self.knowledges_id)

        return await RagHandler.retrieve_ranked_documents(
            user_input,
            collection_names,
            collection_names,
        )


__all__ = ["MCPChatAgent", "MCPChatCanonicalRuntimeNotBound"]
