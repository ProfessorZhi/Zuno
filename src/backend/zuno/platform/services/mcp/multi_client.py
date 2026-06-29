"""Client for connecting to multiple MCP servers and loading LangChain tools/resources."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any

from langchain_core.documents.base import Blob
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from mcp import ClientSession

from zuno.services.mcp.load_mcp.prompts import load_mcp_prompt
from zuno.services.mcp.load_mcp.resources import load_mcp_resources
from zuno.services.mcp.load_mcp.tools import load_mcp_tools
from zuno.services.mcp.sessions import (
    Connection,
    McpHttpClientFactory,
    SSEConnection,
    StdioConnection,
    StreamableHttpConnection,
    WebsocketConnection,
    create_session,
)

ASYNC_CONTEXT_MANAGER_ERROR = (
    "context manager (e.g., async with MultiServerMCPClient(...)). "
    "Instead, you can do one of the following:\n"
    "1. client = MultiServerMCPClient(...)\n"
    "   tools = await client.get_tools()\n"
    "2. client = MultiServerMCPClient(...)\n"
    "   async with client.session(server_name) as session:\n"
    "       tools = await load_mcp_tools(session)"
)


class MultiServerMCPClient:
    """Client for connecting to multiple MCP servers."""

    def __init__(self, connections: dict[str, Connection] | None = None) -> None:
        self.connections: dict[str, Connection] = (
            connections if connections is not None else {}
        )

    @asynccontextmanager
    async def session(
        self,
        server_name: str,
        *,
        auto_initialize: bool = True,
    ) -> AsyncIterator[ClientSession]:
        if server_name not in self.connections:
            msg = (
                f"Couldn't find a server with name '{server_name}', "
                f"expected one of '{list(self.connections.keys())}'"
            )
            raise ValueError(msg)

        async with create_session(self.connections[server_name]) as session:
            if auto_initialize:
                await session.initialize()
            yield session

    async def get_tools(self, *, server_name: str | None = None) -> list[BaseTool]:
        if server_name is not None:
            if server_name not in self.connections:
                msg = (
                    f"Couldn't find a server with name '{server_name}', "
                    f"expected one of '{list(self.connections.keys())}'"
                )
                raise ValueError(msg)
            return await load_mcp_tools(None, connection=self.connections[server_name])

        all_tools: list[BaseTool] = []
        tasks = [
            asyncio.create_task(load_mcp_tools(None, connection=connection))
            for connection in self.connections.values()
        ]
        tools_list = await asyncio.gather(*tasks)
        for tools in tools_list:
            all_tools.extend(tools)
        return all_tools

    async def get_prompt(
        self,
        server_name: str,
        prompt_name: str,
        *,
        arguments: dict[str, Any] | None = None,
    ) -> list[HumanMessage | AIMessage]:
        async with self.session(server_name) as session:
            return await load_mcp_prompt(session, prompt_name, arguments=arguments)

    async def get_resources(
        self,
        server_name: str,
        *,
        uris: str | list[str] | None = None,
    ) -> list[Blob]:
        async with self.session(server_name) as session:
            return await load_mcp_resources(session, uris=uris)

    async def __aenter__(self) -> "MultiServerMCPClient":
        raise NotImplementedError(ASYNC_CONTEXT_MANAGER_ERROR)

    def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError(ASYNC_CONTEXT_MANAGER_ERROR)


__all__ = [
    "McpHttpClientFactory",
    "MultiServerMCPClient",
    "SSEConnection",
    "StdioConnection",
    "StreamableHttpConnection",
    "WebsocketConnection",
]
