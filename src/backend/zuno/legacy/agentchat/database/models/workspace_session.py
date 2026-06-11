from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, text
from sqlmodel import Field

from agentchat.database.models.base import SQLModelSerializable


class WorkSpaceSessionBase(SQLModelSerializable):
    title: str = Field(..., description="工作台会话标题")
    agent: str = Field(..., description="工作台使用的智能体")
    user_id: str = Field(..., description="所属用户 ID")
    contexts: List[dict] = Field(
        [],
        sa_column=Column(JSON),
        description="结构化上下文列表",
    )


class WorkSpaceSession(WorkSpaceSessionBase, table=True):
    __tablename__ = "workspace_session"

    session_id: str = Field(
        default_factory=lambda: uuid4().hex,
        primary_key=True,
        description="工作台会话 ID",
    )

    update_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
        ),
        description="修改时间",
    )
    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
        description="创建时间",
    )


class WorkSpaceSessionCreate(BaseModel):
    title: str
    agent: str
    user_id: str
    session_id: Optional[str] = None
    workspace_mode: str = "normal"
    contexts: list[dict] = []


class WorkSpaceSessionContext(BaseModel):
    query: str
    guide_prompt: str = ""
    task: list[dict] = []
    answer: str
    metadata: dict = {}
