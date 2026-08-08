import json
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.types import CallToolResult, Prompt, Resource, Tool


MCP_CANONICAL_RUNTIME_NOT_BOUND = (
    "MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND: MCP provider execution requires a "
    "canonical ToolInvocationGateway binding (Gateway -> registered "
    "MCPToolExecutorAdapter -> provider). A raw MCP client must never execute "
    "a provider tool on its own."
)


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_path: str, server_env: str):
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=json.loads(server_env),
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

    async def list_server_tools(self) -> list[Tool]:
        response = await self.session.list_tools()
        return response.tools

    async def list_server_prompts(self) -> list[Prompt]:
        response = await self.session.list_prompts()
        return response.prompts

    async def list_server_resources(self) -> list[Resource]:
        response = await self.session.list_resources()
        return response.resources

    async def call_server_tool(self, name, arguments) -> CallToolResult:
        """Provider execution without a canonical gateway binding fails closed.

        PHASE22: the MCP client performs admin / discovery (connect, list
        tools, prompts, resources) only. Executing a provider tool is the
        canonical executor's job (``ToolInvocationGateway`` -> registered
        ``MCPToolExecutorAdapter`` -> provider call). A direct call here
        bypasses Security / Budget / receipt / idempotency and is rejected
        before any provider call is made.
        """
        raise RuntimeError(MCP_CANONICAL_RUNTIME_NOT_BOUND)


__all__ = ["MCPClient"]
