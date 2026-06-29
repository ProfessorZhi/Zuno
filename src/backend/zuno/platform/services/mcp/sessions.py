"""Session management for different MCP transport types."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Literal, Protocol

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from pathlib import Path

    import httpx

EncodingErrorHandler = Literal["strict", "ignore", "replace"]

DEFAULT_ENCODING = "utf-8"
DEFAULT_ENCODING_ERROR_HANDLER: EncodingErrorHandler = "strict"

DEFAULT_HTTP_TIMEOUT = 5
DEFAULT_SSE_READ_TIMEOUT = 60 * 5

DEFAULT_STREAMABLE_HTTP_TIMEOUT = timedelta(seconds=30)
DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT = timedelta(seconds=60 * 5)


class McpHttpClientFactory(Protocol):
    """Protocol for creating httpx.AsyncClient instances for MCP connections."""

    def __call__(
        self,
        headers: dict[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
        auth: httpx.Auth | None = None,
    ) -> httpx.AsyncClient:
        ...


class StdioConnection(TypedDict):
    transport: Literal["stdio"]
    command: str
    args: list[str]
    env: NotRequired[dict[str, str] | None]
    cwd: NotRequired[str | Path | None]
    encoding: NotRequired[str]
    encoding_error_handler: NotRequired[EncodingErrorHandler]
    session_kwargs: NotRequired[dict[str, Any] | None]


class SSEConnection(TypedDict):
    transport: Literal["sse"]
    url: str
    headers: NotRequired[dict[str, Any] | None]
    timeout: NotRequired[float]
    sse_read_timeout: NotRequired[float]
    session_kwargs: NotRequired[dict[str, Any] | None]
    httpx_client_factory: NotRequired[McpHttpClientFactory | None]
    auth: NotRequired[httpx.Auth]


class StreamableHttpConnection(TypedDict):
    transport: Literal["streamable_http"]
    url: str
    headers: NotRequired[dict[str, Any] | None]
    timeout: NotRequired[timedelta]
    sse_read_timeout: NotRequired[timedelta]
    terminate_on_close: NotRequired[bool]
    session_kwargs: NotRequired[dict[str, Any] | None]
    httpx_client_factory: NotRequired[McpHttpClientFactory | None]
    auth: NotRequired[httpx.Auth]


class WebsocketConnection(TypedDict):
    transport: Literal["websocket"]
    url: str
    session_kwargs: NotRequired[dict[str, Any] | None]


Connection = (
    StdioConnection | SSEConnection | StreamableHttpConnection | WebsocketConnection
)


@asynccontextmanager
async def _create_stdio_session(  # noqa: PLR0913
    *,
    command: str,
    args: list[str],
    env: dict[str, str] | None = None,
    cwd: str | Path | None = None,
    encoding: str = DEFAULT_ENCODING,
    encoding_error_handler: Literal[
        "strict", "ignore", "replace"
    ] = DEFAULT_ENCODING_ERROR_HANDLER,
    session_kwargs: dict[str, Any] | None = None,
) -> AsyncIterator[ClientSession]:
    env = env or {}
    if "PATH" not in env:
        env["PATH"] = os.environ.get("PATH", "")

    server_params = StdioServerParameters(
        command=command,
        args=args,
        env=env,
        cwd=cwd,
        encoding=encoding,
        encoding_error_handler=encoding_error_handler,
    )

    async with (
        stdio_client(server_params) as (read, write),
        ClientSession(read, write, **(session_kwargs or {})) as session,
    ):
        yield session


@asynccontextmanager
async def _create_sse_session(  # noqa: PLR0913
    *,
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: float = DEFAULT_HTTP_TIMEOUT,
    sse_read_timeout: float = DEFAULT_SSE_READ_TIMEOUT,
    session_kwargs: dict[str, Any] | None = None,
    httpx_client_factory: McpHttpClientFactory | None = None,
    auth: httpx.Auth | None = None,
) -> AsyncIterator[ClientSession]:
    kwargs = {}
    if httpx_client_factory is not None:
        kwargs["httpx_client_factory"] = httpx_client_factory

    async with (
        sse_client(url, headers, timeout, sse_read_timeout, auth=auth, **kwargs) as (
            read,
            write,
        ),
        ClientSession(read, write, **(session_kwargs or {})) as session,
    ):
        yield session


@asynccontextmanager
async def _create_streamable_http_session(  # noqa: PLR0913
    *,
    url: str,
    headers: dict[str, Any] | None = None,
    timeout: timedelta = DEFAULT_STREAMABLE_HTTP_TIMEOUT,
    sse_read_timeout: timedelta = DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT,
    terminate_on_close: bool = True,
    session_kwargs: dict[str, Any] | None = None,
    httpx_client_factory: McpHttpClientFactory | None = None,
    auth: httpx.Auth | None = None,
) -> AsyncIterator[ClientSession]:
    kwargs = {}
    if httpx_client_factory is not None:
        kwargs["httpx_client_factory"] = httpx_client_factory

    async with (
        streamablehttp_client(
            url,
            headers,
            timeout,
            sse_read_timeout,
            terminate_on_close,
            auth=auth,
            **kwargs,
        ) as (read, write, _),
        ClientSession(read, write, **(session_kwargs or {})) as session,
    ):
        yield session


@asynccontextmanager
async def _create_websocket_session(
    *,
    url: str,
    session_kwargs: dict[str, Any] | None = None,
) -> AsyncIterator[ClientSession]:
    try:
        from mcp.client.websocket import websocket_client
    except ImportError:
        msg = (
            "Could not import websocket_client. "
            "To use Websocket connections, please install the required dependency: "
            "'pip install mcp[ws]' or 'pip install websockets'"
        )
        raise ImportError(msg) from None

    async with (
        websocket_client(url) as (read, write),
        ClientSession(read, write, **(session_kwargs or {})) as session,
    ):
        yield session


@asynccontextmanager
async def create_session(connection: Connection) -> AsyncIterator[ClientSession]:  # noqa: C901
    if "transport" not in connection:
        msg = (
            "Configuration error: Missing 'transport' key in server configuration. "
            "Each server must include 'transport' with one of: "
            "'stdio', 'sse', 'websocket', 'streamable_http'. "
            "Please refer to the langchain-mcp-adapters documentation for more details."
        )
        raise ValueError(msg)

    transport = connection["transport"]
    params = {k: v for k, v in connection.items() if k != "transport"}

    if transport == "sse":
        if "url" not in params:
            raise ValueError("'url' parameter is required for SSE connection")
        async with _create_sse_session(**params) as session:
            yield session
    elif transport == "streamable_http":
        if "url" not in params:
            raise ValueError("'url' parameter is required for Streamable HTTP connection")
        async with _create_streamable_http_session(**params) as session:
            yield session
    elif transport == "stdio":
        if "command" not in params:
            raise ValueError("'command' parameter is required for stdio connection")
        if "args" not in params:
            raise ValueError("'args' parameter is required for stdio connection")
        async with _create_stdio_session(**params) as session:
            yield session
    elif transport == "websocket":
        if "url" not in params:
            raise ValueError("'url' parameter is required for Websocket connection")
        async with _create_websocket_session(**params) as session:
            yield session
    else:
        msg = (
            f"Unsupported transport: {transport}. "
            "Must be one of: 'stdio', 'sse', 'websocket', 'streamable_http'"
        )
        raise ValueError(msg)


__all__ = [
    "Connection",
    "McpHttpClientFactory",
    "SSEConnection",
    "StdioConnection",
    "StreamableHttpConnection",
    "WebsocketConnection",
    "create_session",
]
