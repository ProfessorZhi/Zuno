from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, text
from sqlmodel import Field

from agentchat.database.models.base import SQLModelSerializable


class Status:
    fail = "fail"
    process = "process"
    success = "success"


class KnowledgeFileTable(SQLModelSerializable, table=True):
    __tablename__ = "knowledge_file"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    file_name: str = Field(index=True)
    knowledge_id: str = Field(index=True)
    status: str = Field(default=Status.success)
    parse_status: str = Field(default="pending")
    rag_index_status: str = Field(default="pending")
    graph_index_status: str = Field(default="pending")
    last_task_id: Optional[str] = Field(default=None, index=True)
    last_error: Optional[str] = Field(default=None, max_length=2048)
    user_id: str = Field(index=True)
    oss_url: str = Field(default="")
    file_size: int = Field(default=0)
    update_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
        )
    )
    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
