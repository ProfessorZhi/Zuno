import functools
import json
import logging
from typing import Any

from mcp.types import Tool as MCPTool

from zuno.services.mcp_openai.mcp_client import MCPClient
from zuno.services.mcp_openai.schema import FunctionTool
from zuno.services.mcp_openai.strict_schema import ensure_strict_json_schema


class MCPUtil:
    """Utilities for interop between MCP servers and zuno chat runtimes."""

    @classmethod
    async def get_all_function_tools(
        cls,
        clients: list[MCPClient],
        convert_schemas_to_strict: bool = True,
    ) -> list[FunctionTool]:
        tools = []
        tool_names: set[str] = set()
        for client in clients:
            server_tools = await cls.get_function_tools(client, convert_schemas_to_strict)
            server_tool_names = {tool.name for tool in server_tools}
            if len(server_tool_names & tool_names) > 0:
                raise ValueError(
                    f"Duplicate tool names found across MCP servers: {server_tool_names & tool_names}"
                )
            tool_names.update(server_tool_names)
            tools.extend(server_tools)
        return tools

    @classmethod
    async def get_function_tools(
        cls,
        client: MCPClient,
        convert_schemas_to_strict: bool,
    ) -> list[FunctionTool]:
        tools = await client.list_server_tools()
        return [cls.to_function_tool(tool, client, convert_schemas_to_strict) for tool in tools]

    @classmethod
    def to_function_tool(
        cls,
        tool: MCPTool,
        client: MCPClient,
        convert_schemas_to_strict: bool,
    ) -> FunctionTool:
        invoke_func = functools.partial(cls.run_mcp_tool, client, tool)
        schema, is_strict = tool.inputSchema, False
        if "properties" not in schema:
            schema["properties"] = {}
        if convert_schemas_to_strict:
            try:
                schema = ensure_strict_json_schema(schema)
                is_strict = True
            except Exception as exc:
                logging.info(f"Error converting MCP schema to strict mode: {exc}")
        return FunctionTool(
            name=tool.name,
            description=tool.description or "",
            params_json_schema=schema,
            on_run_tool=invoke_func,
            strict_json_schema=is_strict,
        )

    @classmethod
    async def run_mcp_tool(
        cls,
        client: MCPClient,
        tool: MCPTool,
        input_json: str,
    ) -> str:
        try:
            json_data: dict[str, Any] = json.loads(input_json) if input_json else {}
        except Exception as exc:
            logging.debug(f"Invalid JSON input for tool {tool.name}: {input_json}")
            raise ValueError(f"Invalid JSON input for tool {tool.name}: {input_json}") from exc

        logging.debug(f"Invoking MCP tool {tool.name} with input {input_json}")
        try:
            result = await client.call_server_tool(tool.name, json_data)
        except Exception as exc:
            logging.error(f"Error invoking MCP tool {tool.name}: {exc}")
            raise ValueError(f"Error invoking MCP tool {tool.name}: {exc}") from exc

        logging.debug(f"MCP tool {tool.name} returned {result}")
        if len(result.content) == 1:
            return result.content[0].model_dump_json()
        if len(result.content) > 1:
            return json.dumps([item.model_dump() for item in result.content])
        logging.error(f"Error MCP tool result: {result}")
        return "Error running tool."


__all__ = ["MCPUtil"]
