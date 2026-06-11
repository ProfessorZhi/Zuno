from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, text
from sqlmodel import Field

from zuno.database.models.base import SQLModelSerializable
from zuno.settings import app_settings


class AgentTable(SQLModelSerializable, table=True):
    __tablename__ = "agent"
    __table_args__ = {"extend_existing": True}

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: str = Field(default="", description="Agent name")
    description: str = Field(default="", description="Agent description")
    logo_url: str = Field(default=app_settings.default_config.get("agent_logo_url"))
    user_id: Optional[str] = Field(default=None, index=True, description="Agent owner user ID")
    is_custom: bool = Field(default=True, description="Whether the agent is user-defined")
    system_prompt: str = Field(default="", description="Agent system prompt")
    llm_id: str = Field(default="", description="Bound LLM ID")
    enable_memory: bool = Field(default=True, description="Whether memory is enabled")
    mcp_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Bound MCP server IDs")
    tool_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Bound tool IDs")
    agent_skill_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Bound agent skill IDs")
    knowledge_ids: List[str] = Field(default=[], sa_column=Column(JSON), description="Bound knowledge IDs")
    domain_pack_id: Optional[str] = Field(default=None, description="Default Domain Pack ID")

    update_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
        ),
        description="Last update time",
    )
    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
        description="Creation time",
    )
