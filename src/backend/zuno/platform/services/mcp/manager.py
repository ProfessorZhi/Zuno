import asyncio
import logging
from typing import Any, Dict, List

from langchain_core.tools import BaseTool

from zuno.capability.tool_runtime.bypass_guard import ensure_legacy_direct_tool_allowed

from zuno.platform.services.mcp.multi_client import MultiServerMCPClient
from zuno.api.dto.mcp import MCPBaseConfig


logger = logging.getLogger(__name__)

HIDE_FIELDS = ["server_name", "personal_config"]


class MCPManager:
    def __init__(self, mcp_configs: List[MCPBaseConfig], timeout=10):
        connection_info = {
            mcp_config.server_name: mcp_config.model_dump(exclude={"server_name", "personal_config"})
            for mcp_config in mcp_configs
        }

        self.multi_server_client = MultiServerMCPClient(connection_info)
        self.mcp_configs = mcp_configs
        self.timeout = timeout

    async def get_mcp_tools(self) -> list[BaseTool]:
        tools = await asyncio.wait_for(
            self.multi_server_client.get_tools(),
            timeout=self.timeout,
        )
        return tools

    async def show_mcp_tools(self) -> dict:
        result = {}
        try:
            for mcp_config in self.mcp_configs:
                server_tools = await asyncio.wait_for(
                    self.multi_server_client.get_tools(server_name=mcp_config.server_name),
                    timeout=self.timeout,
                )
                tool_list = []
                for tool in server_tools:
                    input_schema = tool.args_schema
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": input_schema,
                    }
                    tool_list.append(tool_dict)
                result[mcp_config.server_name] = tool_list
            return result
        except asyncio.TimeoutError as err:
            logger.info("Timeout while getting MCP service tool list")
            raise TimeoutError(
                f"MCP service tool discovery timed out after {self.timeout}s"
            ) from err
        except Exception as err:
            logger.info(f"Error getting MCP service tool list: {err}")
            return {}

    async def call_mcp_tools(self, tools_info: List[Dict[str, Any]]):
        """Retired direct MCP execution surface.

        Tool discovery remains available to the MCP management/API surface,
        but executing a discovered tool must be proposed and dispatched by
        ``ToolInvocationGateway`` so security, approval, idempotency, and
        receipts cannot be bypassed by this compatibility manager.
        """
        del tools_info
        raise RuntimeError(
            "MCP_DIRECT_EXECUTION_RETIRED: use ToolInvocationGateway"
        )


__all__ = ["HIDE_FIELDS", "MCPManager"]
