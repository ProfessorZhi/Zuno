"""Tools adapter for converting MCP tools to LangChain tools."""

from typing import Any, cast, get_args

from langchain_core.tools import (
    BaseTool,
    InjectedToolArg,
    StructuredTool,
    ToolException,
)
from langchain_core.tools.base import get_all_basemodel_annotations
from mcp import ClientSession
from mcp.server.fastmcp.tools import Tool as FastMCPTool
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase, FuncMetadata
from mcp.types import CallToolResult, EmbeddedResource, ImageContent, TextContent
from mcp.types import Tool as MCPTool
from pydantic import BaseModel, create_model

from zuno.services.mcp.sessions import Connection, create_session

NonTextContent = ImageContent | EmbeddedResource
MAX_ITERATIONS = 1000


def _convert_call_tool_result(
    call_tool_result: CallToolResult,
) -> tuple[str | list[str], list[NonTextContent] | None]:
    text_contents: list[TextContent] = []
    non_text_contents = []
    for content in call_tool_result.content:
        if isinstance(content, TextContent):
            text_contents.append(content)
        else:
            non_text_contents.append(content)

    tool_content: str | list[str] = [content.text for content in text_contents]
    if not text_contents:
        tool_content = ""
    elif len(text_contents) == 1:
        tool_content = tool_content[0]

    if call_tool_result.isError:
        raise ToolException(tool_content)

    return tool_content, non_text_contents or None


async def _list_all_tools(session: ClientSession) -> list[MCPTool]:
    current_cursor: str | None = None
    all_tools: list[MCPTool] = []
    iterations = 0

    while True:
        iterations += 1
        if iterations > MAX_ITERATIONS:
            raise RuntimeError("Reached max of 1000 iterations while listing tools.")

        result = await session.list_tools(cursor=current_cursor)
        if result.tools:
            all_tools.extend(result.tools)
        if not result.nextCursor:
            break
        current_cursor = result.nextCursor
    return all_tools


def convert_mcp_tool_to_langchain_tool(
    session: ClientSession | None,
    tool: MCPTool,
    *,
    connection: Connection | None = None,
) -> BaseTool:
    if session is None and connection is None:
        raise ValueError("Either a session or a connection config must be provided")

    async def call_tool(
        **arguments: dict[str, Any],
    ) -> tuple[str | list[str], list[NonTextContent] | None]:
        if session is None:
            async with create_session(connection) as tool_session:
                await tool_session.initialize()
                result = await cast("ClientSession", tool_session).call_tool(
                    tool.name,
                    arguments,
                )
        else:
            result = await session.call_tool(tool.name, arguments)
        return _convert_call_tool_result(result)

    return StructuredTool(
        name=tool.name,
        description=tool.description or "",
        args_schema=tool.inputSchema,
        coroutine=call_tool,
        response_format="content_and_artifact",
        metadata=tool.annotations.model_dump() if tool.annotations else None,
    )


async def load_mcp_tools(
    session: ClientSession | None,
    *,
    connection: Connection | None = None,
) -> list[BaseTool]:
    if session is None and connection is None:
        raise ValueError("Either a session or a connection config must be provided")

    if session is None:
        async with create_session(connection) as tool_session:
            await tool_session.initialize()
            tools = await _list_all_tools(tool_session)
    else:
        tools = await _list_all_tools(session)

    return [
        convert_mcp_tool_to_langchain_tool(session, tool, connection=connection)
        for tool in tools
    ]


def _get_injected_args(tool: BaseTool) -> list[str]:
    def _is_injected_arg_type(type_: type) -> bool:
        return any(
            isinstance(arg, InjectedToolArg)
            or (isinstance(arg, type) and issubclass(arg, InjectedToolArg))
            for arg in get_args(type_)[1:]
        )

    return [
        field
        for field, field_info in get_all_basemodel_annotations(tool.args_schema).items()
        if _is_injected_arg_type(field_info)
    ]


def to_fastmcp(tool: BaseTool) -> FastMCPTool:
    if not issubclass(tool.args_schema, BaseModel):
        msg = (
            "Tool args_schema must be a subclass of pydantic.BaseModel. "
            "Tools with dict args schema are not supported."
        )
        raise TypeError(msg)

    parameters = tool.tool_call_schema.model_json_schema()
    field_definitions = {
        field: (field_info.annotation, field_info)
        for field, field_info in tool.tool_call_schema.model_fields.items()
    }
    arg_model = create_model(
        f"{tool.name}Arguments", **field_definitions, __base__=ArgModelBase
    )
    fn_metadata = FuncMetadata(arg_model=arg_model)

    async def fn(**arguments: dict[str, Any]) -> Any:
        return await tool.ainvoke(arguments)

    injected_args = _get_injected_args(tool)
    if injected_args:
        raise NotImplementedError("LangChain tools with injected arguments are not supported")

    return FastMCPTool(
        fn=fn,
        name=tool.name,
        description=tool.description,
        parameters=parameters,
        fn_metadata=fn_metadata,
        is_async=True,
    )
