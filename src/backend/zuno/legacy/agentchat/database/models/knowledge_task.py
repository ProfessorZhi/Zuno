from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, text
from sqlmodel import Field

from agentchat.database.models.base import SQLModelSerializable
from agentchat.services.pipeline.models import KnowledgeTaskStage, KnowledgeTaskStatus


def get_task_id() -> str:
    return f"task_{uuid4().hex[:16]}"


class KnowledgeTaskTable(SQLModelSerializable, table=True):
    __tablename__ = "knowledge_task"

    id: str = Field(default_factory=get_task_id, primary_key=True)
    knowledge_id: str = Field(index=True)
    knowledge_file_id: str = Field(index=True)
    task_type: str = Field(default="ingest", index=True)
    status: str = Field(default=KnowledgeTaskStatus.pending, index=True)
    current_stage: str = Field(default=KnowledgeTaskStage.uploaded, index=True)
    retry_count: int = Field(default=0)
    error_message: Optional[str] = Field(default=None, max_length=2048)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    result_summary: dict = Field(default_factory=dict, sa_column=Column(JSON))
    started_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    finished_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
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


class KnowledgeTaskEventTable(SQLModelSerializable, table=True):
    __tablename__ = "knowledge_task_event"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    task_id: str = Field(index=True)
    stage: str = Field(index=True)
    status: str = Field(index=True)
    message: str = Field(max_length=1024)
    detail: dict = Field(default_factory=dict, sa_column=Column(JSON))
    create_time: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
