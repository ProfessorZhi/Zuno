from contextvars import ContextVar
from typing import Optional


trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
unique_id: ContextVar[Optional[str]] = ContextVar("unique_id", default=None)
user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
agent_name: ContextVar[Optional[str]] = ContextVar("agent_name", default=None)


def get_trace_id_context() -> str:
    if (tid := trace_id.get()) is None:
        raise ValueError("trace_id context not initialized")
    return tid


def set_trace_id_context(tid: str):
    trace_id.set(tid)


def get_user_id_context():
    if uid := user_id.get():
        return uid
    return None


def set_user_id_context(uid: str):
    user_id.set(uid)


def get_agent_name_context():
    if ag_name := agent_name.get():
        return ag_name
    return "其他"


def set_agent_name_context(ag_name):
    agent_name.set(ag_name)


__all__ = [
    "agent_name",
    "get_agent_name_context",
    "get_trace_id_context",
    "get_user_id_context",
    "set_agent_name_context",
    "set_trace_id_context",
    "set_user_id_context",
    "trace_id",
    "unique_id",
    "user_id",
]
