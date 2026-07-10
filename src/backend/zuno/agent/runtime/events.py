from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RuntimeEvent(BaseModel):
    event_id: str
    task_id: str
    trace_id: str
    event_type: str
    node: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


__all__ = ["RuntimeEvent"]
