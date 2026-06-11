from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, text
from sqlmodel import Field

from agentchat.database.models.base import SQLModelSerializable


class DialogTable(SQLModelSerializable, table=True):
    """单条对话记录。"""

    __tablename__ = "dialog"

    dialog_id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: str = Field(description='对话名称')
    agent_id: str = Field(description='绑定对象 ID')
    agent_type: str = Field(
        default="Agent",
        description="绑定对象类型，兼容 Agent 与历史 MCP 标记",
    )
    user_id: str = Field(description='所属用户 ID')
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
