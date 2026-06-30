from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, Text, text
from sqlmodel import Field

from zuno.database.models.base import SQLModelSerializable


class MemoryRawEventTable(SQLModelSerializable, table=True):
    __tablename__ = "memory_raw_event"
    __table_args__ = {"extend_existing": True}

    event_id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    agent_id: Optional[str] = Field(default=None, index=True)
    project_id: Optional[str] = Field(default=None, index=True)
    thread_id: Optional[str] = Field(default=None, index=True)
    trace_id: str = Field(default="", index=True)
    task_id: str = Field(default="", index=True)
    event_type: str = Field(index=True)
    layer: str = Field(index=True)
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    memory_metadata: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )


class MemoryTaskSummaryTable(SQLModelSerializable, table=True):
    __tablename__ = "memory_task_summary"
    __table_args__ = {"extend_existing": True}

    summary_id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    agent_id: Optional[str] = Field(default=None, index=True)
    project_id: Optional[str] = Field(default=None, index=True)
    thread_id: Optional[str] = Field(default=None, index=True)
    layer: str = Field(index=True)
    content: str = Field(sa_column=Column(Text))
    source_event_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    token_count: int = Field(default=0)
    memory_metadata: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )


class MemoryCandidateTable(SQLModelSerializable, table=True):
    __tablename__ = "memory_candidate"
    __table_args__ = {"extend_existing": True}

    candidate_id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    agent_id: Optional[str] = Field(default=None, index=True)
    project_id: Optional[str] = Field(default=None, index=True)
    thread_id: Optional[str] = Field(default=None, index=True)
    layer: str = Field(index=True)
    content: str = Field(sa_column=Column(Text))
    confidence: float = Field(default=0)
    source_event_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    dedupe_key: str = Field(index=True)
    retention_policy: dict = Field(default_factory=dict, sa_column=Column(JSON))
    review_status: str = Field(default="pending", index=True)
    requires_review: bool = Field(default=True, index=True)
    memory_metadata: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=text("CURRENT_TIMESTAMP"),
        ),
    )
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )


class MemoryReviewDecisionTable(SQLModelSerializable, table=True):
    __tablename__ = "memory_review_decision"
    __table_args__ = {"extend_existing": True}

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    candidate_id: str = Field(index=True)
    status: str = Field(index=True)
    reviewer_id: str = Field(index=True)
    reason: str = Field(sa_column=Column(Text))
    source_event_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    memory_metadata: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )


class MemoryGovernanceLedgerTable(SQLModelSerializable, table=True):
    __tablename__ = "memory_governance_ledger"
    __table_args__ = {"extend_existing": True}

    entry_id: str = Field(primary_key=True)
    action: str = Field(index=True)
    user_id: str = Field(index=True)
    agent_id: Optional[str] = Field(default=None, index=True)
    project_id: Optional[str] = Field(default=None, index=True)
    thread_id: Optional[str] = Field(default=None, index=True)
    trace_id: str = Field(default="", index=True)
    task_id: str = Field(default="", index=True)
    source_event_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    reason: str = Field(default="", sa_column=Column(Text))
    memory_metadata: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    )


__all__ = [
    "MemoryCandidateTable",
    "MemoryGovernanceLedgerTable",
    "MemoryRawEventTable",
    "MemoryReviewDecisionTable",
    "MemoryTaskSummaryTable",
]
