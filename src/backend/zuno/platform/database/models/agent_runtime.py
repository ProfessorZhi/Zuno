from __future__ import annotations

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class AgentRuntimeRunTable(SQLModel, table=True):
    __tablename__ = "agent_runtime_runs"

    task_id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    trace_id: str = Field(index=True)
    thread_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    user_id: str = Field(index=True)
    status: str = Field(index=True)
    state_version: str
    state_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    checkpoint_ids_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    latest_checkpoint_id: str | None = Field(default=None, index=True)
    pending_interrupt_id: str | None = Field(default=None, index=True)
    failure_json: dict | None = Field(default=None, sa_column=Column(JSON))


class AgentRuntimeCheckpointTable(SQLModel, table=True):
    __tablename__ = "agent_runtime_checkpoints"

    checkpoint_id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    trace_id: str = Field(index=True)
    thread_id: str = Field(index=True)
    node: str = Field(index=True)
    route: str = ""
    state_version: str
    state_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))


class AgentRuntimeEventTable(SQLModel, table=True):
    __tablename__ = "agent_runtime_events"

    event_id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    trace_id: str = Field(index=True)
    thread_id: str = Field(index=True)
    sequence: int = Field(index=True)
    type: str = Field(index=True)
    status: str = Field(index=True)
    node: str = Field(index=True)
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    timestamp: float = Field(index=True)


class AgentRuntimeInterruptTable(SQLModel, table=True):
    __tablename__ = "agent_runtime_interrupts"

    interrupt_id: str = Field(primary_key=True)
    task_id: str = Field(index=True)
    trace_id: str = Field(index=True)
    thread_id: str = Field(index=True)
    node: str = Field(index=True)
    status: str = Field(index=True)
    reason: str
    required_approval: str = ""
    payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    resumable: bool = True


AGENT_RUNTIME_TABLES = [
    AgentRuntimeRunTable,
    AgentRuntimeCheckpointTable,
    AgentRuntimeEventTable,
    AgentRuntimeInterruptTable,
]


__all__ = [
    "AGENT_RUNTIME_TABLES",
    "AgentRuntimeCheckpointTable",
    "AgentRuntimeEventTable",
    "AgentRuntimeInterruptTable",
    "AgentRuntimeRunTable",
]
