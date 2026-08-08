import logging

from mcp.types import CallToolResult

from zuno.platform.services.mcp_openai.mcp_client import MCPClient
from zuno.platform.services.mcp_openai.mcp_util import MCPUtil
from zuno.platform.services.mcp_openai.schema import FunctionTool


class MCPManager:
    def __init__(self, client: object):
        self.mcp_server_stack: list[str] = []
        self.chat_client = client
        self.mcp_clients: list[MCPClient] = []
        self.server_client_dict: dict[str, MCPClient] = {}
        self.server_path_env_dict: dict[str, str] = {}
        self.callable_mcp_tools: dict[str, FunctionTool] = {}

    async def enter_mcp_server(self, server_path, server_env):
        self.mcp_server_stack.append(server_path)
        mcp_client = MCPClient()

        self.server_path_env_dict[server_path] = server_env
        self.server_client_dict[server_path] = mcp_client

    async def connect_client(self):
        for mcp_server in self.mcp_server_stack:
            mcp_client = self.server_client_dict.get(mcp_server)
            server_env = self.server_path_env_dict[mcp_server]
            await mcp_client.connect_to_server(mcp_server, server_env)
            self.mcp_clients.append(mcp_client)

    async def list_all_server_tools(self) -> list[FunctionTool]:
        function_calls = await MCPUtil.get_all_function_tools(self.mcp_clients)
        for func in function_calls:
            self.callable_mcp_tools[func.name] = func
        return function_calls

    async def _chat_model(self, messages, available_tools):
        try:
            if hasattr(self.chat_client, "ainvoke"):
                return await self.chat_client.ainvoke(messages, available_tools)
            if hasattr(self.chat_client, "invoke"):
                return self.chat_client.invoke(messages, available_tools)
            client_type = type(self.chat_client)
            if "openai" in f"{client_type.__module__}.{client_type.__name__}".lower():
                raise NotImplementedError("OpenAI MCP chat client is not implemented yet")
            raise ValueError("Now MCP Server support Anthropic-compatible invoke clients")

        except Exception as err:
            logging.info(f"chat model appear error: {err}")
            raise

    async def process_query(self, messages):
        """Chat loop with direct MCP provider execution fails closed.

        PHASE22: the legacy chat loop executed MCP provider tools directly
        (``on_run_tool`` -> ``run_mcp_tool`` -> ``call_server_tool``) without
        the canonical ``ToolInvocationGateway``. Product execution must be
        routed through the canonical runtime; a raw chat loop is rejected
        before any provider call is made.
        """
        from zuno.platform.services.mcp_openai.mcp_client import (
            MCP_CANONICAL_RUNTIME_NOT_BOUND,
        )

        raise RuntimeError(MCP_CANONICAL_RUNTIME_NOT_BOUND)

    async def _get_tool_response(self, name, arguments) -> CallToolResult:
        from zuno.platform.services.mcp_openai.mcp_client import (
            MCP_CANONICAL_RUNTIME_NOT_BOUND,
        )

        raise RuntimeError(MCP_CANONICAL_RUNTIME_NOT_BOUND)


__all__ = ["MCPManager"]
