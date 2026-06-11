import asyncio

from agentchat.api.services.history import HistoryService
from agentchat.api.services.llm import LLMService
from agentchat.api.services.mcp_stdio_server import MCPServerService
from agentchat.core.models.anthropic import DeepAsyncAnthropic
from agentchat.services.mcp_openai.mcp_manager import MCPManager
from agentchat.services.rag.handler import RagHandler


class MCPChatAgent:
    def __init__(self, **kwargs):
        self.mcp_servers_id = kwargs.get("mcp_servers_id")
        self.llm_id = kwargs.get("llm_id")
        self.enable_memory = kwargs.get("enable_memory")
        self.knowledges_id = kwargs.get("knowledges_id")

        self.deep_anthropic = self._init_Anthropic()
        self.mcp_manager = self._init_MCP_Manager()

    def _init_Anthropic(self) -> DeepAsyncAnthropic:
        llm_config = LLMService.get_llm_by_id(self.llm_id)
        return DeepAsyncAnthropic(**llm_config)

    def _init_MCP_Manager(self) -> MCPManager:
        return MCPManager(self.deep_anthropic)

    async def init_MCP_Server(self):
        for server_id in self.mcp_servers_id:
            mcp_server = MCPServerService.get_mcp_server_user(server_id)
            await self.mcp_manager.enter_mcp_server(
                mcp_server.mcp_server_path,
                mcp_server.mcp_server_env,
            )

        await self.mcp_manager.connect_client()

    async def ainvoke(self, user_input: str, dialog_id: str, stream: bool = False):
        history_messages, recall_knowledge_data = await asyncio.gather(
            self.get_history_message(user_input, dialog_id),
            self._get_knowledge_context(user_input),
        )
        mcp_tool_messages = history_messages.copy()
        mcp_response = await self.mcp_manager.process_query(mcp_tool_messages)

        mcp_response.append({"role": "user", "content": recall_knowledge_data})
        if stream:
            return self._stream_response(mcp_response)
        return await self._normal_response(mcp_response)

    async def get_history_message(self, user_input: str, dialog_id: str, top_k: int = 5):
        if self.enable_memory:
            return await self._retrieval_history(user_input, dialog_id, top_k)

        messages = await self._direct_history(dialog_id, top_k)
        return [message.to_json() for message in messages]

    async def _stream_response(self, messages):
        async for text in self.deep_anthropic.ainvoke_stream(messages):
            yield text

    async def _normal_response(self, messages):
        return await self.deep_anthropic.ainvoke(messages)

    async def _direct_history(self, dialog_id: str, top_k: int):
        return await HistoryService.select_history(dialog_id, top_k)

    async def _retrieval_history(self, user_input: str, dialog_id: str, top_k: int):
        # The old memory-RAG hook was removed from RagHandler.
        # Falling back to stored dialog history avoids runtime crashes.
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
