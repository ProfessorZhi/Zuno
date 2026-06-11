from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, text
from sqlmodel import Field

from agentchat.database.models.base import SQLModelSerializable


class MCPAgentTable(SQLModelSerializable, table=True):
    """历史兼容表：保存 MCP 服务集合配置。"""

    __tablename__ = "mcp_agent"

    mcp_agent_id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    mcp_server_id: str = Field(
        default=[],
        sa_column=Column(JSON),
        description='关联的 MCP 服务 ID 列表',
    )
    name: str = Field(default="", description="MCP 服务集合名称")
    description: str = Field(default='')
    logo_url: str = Field(default='img/mcp_openai/mcp_agent.png')
    user_id: Optional[str] = Field(index=True)
    update_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP'),
            onupdate=text('CURRENT_TIMESTAMP'),
        ),
        description="更新时间",
    )
    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP'),
        ),
        description="创建时间",
    )
