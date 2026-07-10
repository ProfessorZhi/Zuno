from __future__ import annotations

from typing import Any, Protocol

from zuno.agent.harness import ControllerRuntimeState, RuntimeCheckpoint, RuntimeInterrupt


class AgentRunStore(Protocol):
    def create_task(self, state: ControllerRuntimeState, *, status: str = "running") -> None:
        ...

    def has_task(self, task_id: str) -> bool:
        ...

    def update_state(self, state: ControllerRuntimeState) -> None:
        ...

    def update_status(self, task_id: str, status: str) -> None:
        ...

    def save_checkpoint(self, checkpoint: RuntimeCheckpoint) -> None:
        ...

    def latest_checkpoint(self, task_id: str) -> RuntimeCheckpoint | None:
        ...

    def save_interrupt(self, interrupt: RuntimeInterrupt) -> None:
        ...

    def pending_interrupt(self, task_id: str) -> RuntimeInterrupt | None:
        ...

    def clear_interrupt(self, task_id: str) -> None:
        ...

    def mark_failure(self, task_id: str, failure: dict[str, Any]) -> None:
        ...

    def append_event(self, event: Any) -> None:
        ...

    def events(self, task_id: str) -> tuple[Any, ...]:
        ...

    def snapshot(self, task_id: str) -> Any:
        ...


__all__ = ["AgentRunStore"]
