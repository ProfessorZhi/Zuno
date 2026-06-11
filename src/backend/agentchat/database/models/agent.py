from sqlmodel import Field, SQLModel
from typing import Literal, Optional, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy import JSON, Column, text, DateTime

from agentchat.settings import app_settings
from agentchat.database.models.base import SQLModelSerializable


class AgentTable(SQLModelSerializable, table=True):
    __tablename__ = "agent"
    __table_args__ = {"extend_existing": True}

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: str = Field(default="", description="Agent 的名称")
    description: str = Field(default="", description="Agent 的描述")
    logo_url: str = Field(default=app_settings.default_config.get("agent_logo_url"))
    user_id: Optional[str] = Field(index=True, description="Agent绑定的用户ID")
    is_custom: bool = Field(default=True, description="Agent是否为用户自定义")
    system_prompt: str = Field(default="", description="Agent设定的系统提示词")
    llm_id: str = Field(default="", description="Agent绑定的LLM模型")
    enable_memory: bool = Field(default=True, description="是否开启记忆功能")
    mcp_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Agent绑定的MCP Server")
    tool_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Agent绑定的工具列表")
    agent_skill_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Agent绑定的技能")
    knowledge_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Agent 绑定的知识库")
    domain_pack_id: Optional[str] = Field(default=None, description="Agent绑定的领域包")

    # 修改时间，默认为当前时间戳，自动更新
    update_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP'),
            onupdate=text('CURRENT_TIMESTAMP')
        ),
        description="修改时间"
    )

    # 创建时间，默认为当前时间戳
    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text('CURRENT_TIMESTAMP')
        ),
        description="创建时间"
    )
