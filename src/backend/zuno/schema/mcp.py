from pathlib import Path
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, model_validator


def _default_mcp_logo_url() -> str:
    from zuno.settings import app_settings

    return app_settings.default_config.get("mcp_logo_url", "")


class MCPBaseConfig(BaseModel):
    server_name: str
    transport: str
    personal_config: Optional[Dict[str, Any]] = None


class MCPSSEConfig(MCPBaseConfig):
    transport: Literal["sse"] = "sse"
    url: str
    headers: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = None
    sse_read_timeout: Optional[float] = None
    session_kwargs: Optional[Dict[str, Any]] = None


class MCPStdioConfig(MCPBaseConfig):
    transport: Literal["stdio"] = "stdio"
    command: str
    args: list[str]
    env: Optional[Dict[str, str]] = None
    cwd: Optional[Path] = None
    encoding: str = "utf-8"
    encoding_error_handler: Optional[str] = "ignore"
    session_kwargs: Optional[Dict[str, Any]] = None


class MCPStreamableHttpConfig(MCPBaseConfig):
    transport: Literal["streamable_http"] = "streamable_http"
    url: str
    headers: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = None
    sse_read_timeout: Optional[float] = None
    terminate_on_close: Optional[bool] = None
    session_kwargs: Optional[Dict[str, Any]] = None


class MCPWebsocketConfig(MCPBaseConfig):
    transport: Literal["websocket"] = "websocket"
    url: str
    session_kwargs: Optional[Dict[str, Any]] = None


class MCPServerImportedReq(BaseModel):
    server_name: str
    imported_config: dict
    logo_url: str = Field(default_factory=_default_mcp_logo_url)

    @model_validator(mode="after")
    def set_default_logo_url(self):
        if not self.logo_url:
            self.logo_url = _default_mcp_logo_url()
        return self


class MCPServerUpdateReq(BaseModel):
    server_id: str
    name: str = None
    logo_url: str = None
    imported_config: dict = None


class MCPResponseFormat(BaseModel):
    mcp_as_tool_name: str = Field(
        ...,
        description="根据 MCP 服务下提供的工具描述生成一个工具名称，要求是 2-4 个英文单词组成，用下划线分隔",
    )
    description: str = Field(
        ...,
        description="根据 MCP 服务下提供的工具描述生成一个子 Agent 描述，描述需要说明何时应调用它，并提示用户问题应尽量整合后一次提交。",
    )


__all__ = [
    "MCPBaseConfig",
    "MCPResponseFormat",
    "MCPSSEConfig",
    "MCPServerImportedReq",
    "MCPServerUpdateReq",
    "MCPStdioConfig",
    "MCPStreamableHttpConfig",
    "MCPWebsocketConfig",
]
