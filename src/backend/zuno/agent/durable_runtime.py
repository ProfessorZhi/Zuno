from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import Any

from zuno.agent.harness import (
    ControllerRuntimeState,
    RuntimeCheckpoint,
    RuntimeInterrupt,
    build_single_controller_runtime_harness,
)


@dataclass(frozen=True, slots=True)
class DurableRuntimeEvent:
    event_id: str
    task_id: str
    trace_id: str
    thread_id: str
    type: str
    status: str
    node: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "thread_id": self.thread_id,
            "type": self.type,
            "status": self.status,
            "node": self.node,
            "payload": deepcopy(self.payload),
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DurableRuntimeEvent":
        return cls(
            event_id=str(payload.get("event_id") or ""),
            task_id=str(payload.get("task_id") or ""),
            trace_id=str(payload.get("trace_id") or ""),
            thread_id=str(payload.get("thread_id") or ""),
            type=str(payload.get("type") or ""),
            status=str(payload.get("status") or ""),
            node=str(payload.get("node") or ""),
            payload=deepcopy(dict(payload.get("payload") or {})),
            timestamp=float(payload.get("timestamp") or time.time()),
        )


@dataclass(slots=True)
class DurableRuntimeTaskSnapshot:
    task_id: str
    trace_id: str
    thread_id: str
    workspace_id: str
    status: str
    state: ControllerRuntimeState
    checkpoint_ids: tuple[str, ...] = ()
    latest_checkpoint: RuntimeCheckpoint | None = None
    pending_interrupt: RuntimeInterrupt | None = None
    failure: dict[str, Any] | None = None
    events: tuple[DurableRuntimeEvent, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "thread_id": self.thread_id,
            "workspace_id": self.workspace_id,
            "status": self.status,
            "state": self.state.to_dict(),
            "checkpoint_ids": list(self.checkpoint_ids),
            "latest_checkpoint": (
                self.latest_checkpoint.to_dict() if self.latest_checkpoint is not None else None
            ),
            "pending_interrupt": (
                self.pending_interrupt.to_dict() if self.pending_interrupt is not None else None
            ),
            "failure": deepcopy(self.failure),
            "events": [event.to_dict() for event in self.events],
        }


@dataclass(slots=True)
class _DurableRuntimeRecord:
    state: ControllerRuntimeState
    status: str = "created"
    checkpoint_ids: list[str] = field(default_factory=list)
    latest_checkpoint_id: str | None = None
    pending_interrupt_id: str | None = None
    failure: dict[str, Any] | None = None


class InMemoryDurableRuntimeStore:
    """Deterministic local PHASE06 store for checkpoint/resume semantics."""

    def __init__(self) -> None:
        self._records: dict[str, _DurableRuntimeRecord] = {}
        self._checkpoints: dict[str, RuntimeCheckpoint] = {}
        self._interrupts: dict[str, RuntimeInterrupt] = {}
        self._events: dict[str, list[DurableRuntimeEvent]] = {}

    def create_task(self, state: ControllerRuntimeState, *, status: str = "running") -> None:
        self._records[state.task_id] = _DurableRuntimeRecord(state=state, status=status)
        self._events[state.task_id] = []

    def has_task(self, task_id: str) -> bool:
        return task_id in self._records

    def get_record(self, task_id: str) -> _DurableRuntimeRecord:
        record = self._records.get(task_id)
        if record is None:
            raise KeyError(f"unknown durable runtime task: {task_id}")
        return record

    def update_state(self, state: ControllerRuntimeState) -> None:
        self.get_record(state.task_id).state = state

    def update_status(self, task_id: str, status: str) -> None:
        self.get_record(task_id).status = status

    def save_checkpoint(self, checkpoint: RuntimeCheckpoint) -> None:
        record = self.get_record(checkpoint.task_id)
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
        record.checkpoint_ids.append(checkpoint.checkpoint_id)
        record.latest_checkpoint_id = checkpoint.checkpoint_id

    def latest_checkpoint(self, task_id: str) -> RuntimeCheckpoint | None:
        record = self.get_record(task_id)
        if record.latest_checkpoint_id is None:
            return None
        return self._checkpoints[record.latest_checkpoint_id]

    def save_interrupt(self, interrupt: RuntimeInterrupt) -> None:
        self._interrupts[interrupt.interrupt_id] = interrupt
        self.get_record(interrupt.task_id).pending_interrupt_id = interrupt.interrupt_id

    def pending_interrupt(self, task_id: str) -> RuntimeInterrupt | None:
        interrupt_id = self.get_record(task_id).pending_interrupt_id
        if interrupt_id is None:
            return None
        return self._interrupts[interrupt_id]

    def clear_interrupt(self, task_id: str) -> None:
        self.get_record(task_id).pending_interrupt_id = None

    def mark_failure(self, task_id: str, failure: dict[str, Any]) -> None:
        record = self.get_record(task_id)
        record.status = "failed"
        record.failure = deepcopy(failure)

    def append_event(self, event: DurableRuntimeEvent) -> None:
        self._events.setdefault(event.task_id, []).append(event)

    def events(self, task_id: str) -> tuple[DurableRuntimeEvent, ...]:
        return tuple(self._events.get(task_id, ()))

    def snapshot(self, task_id: str) -> DurableRuntimeTaskSnapshot:
        record = self.get_record(task_id)
        return DurableRuntimeTaskSnapshot(
            task_id=record.state.task_id,
            trace_id=record.state.trace_id,
            thread_id=record.state.thread_id,
            workspace_id=record.state.workspace_id,
            status=record.status,
            state=record.state,
            checkpoint_ids=tuple(record.checkpoint_ids),
            latest_checkpoint=self.latest_checkpoint(task_id),
            pending_interrupt=self.pending_interrupt(task_id),
            failure=deepcopy(record.failure),
            events=self.events(task_id),
        )

    def to_persistence_payload(self) -> dict[str, Any]:
        return {
            "records": {
                task_id: {
                    "state": record.state.to_dict(),
                    "status": record.status,
                    "checkpoint_ids": list(record.checkpoint_ids),
                    "latest_checkpoint_id": record.latest_checkpoint_id,
                    "pending_interrupt_id": record.pending_interrupt_id,
                    "failure": deepcopy(record.failure),
                }
                for task_id, record in self._records.items()
            },
            "checkpoints": {
                checkpoint_id: checkpoint.to_dict()
                for checkpoint_id, checkpoint in self._checkpoints.items()
            },
            "interrupts": {
                interrupt_id: interrupt.to_dict()
                for interrupt_id, interrupt in self._interrupts.items()
            },
            "events": {
                task_id: [event.to_dict() for event in events]
                for task_id, events in self._events.items()
            },
        }

    @classmethod
    def from_persistence_payload(cls, payload: dict[str, Any]) -> "InMemoryDurableRuntimeStore":
        store = cls()
        store._records = {
            task_id: _DurableRuntimeRecord(
                state=ControllerRuntimeState.from_dict(dict(record.get("state") or {})),
                status=str(record.get("status") or "created"),
                checkpoint_ids=[str(item) for item in record.get("checkpoint_ids") or []],
                latest_checkpoint_id=record.get("latest_checkpoint_id"),
                pending_interrupt_id=record.get("pending_interrupt_id"),
                failure=deepcopy(record.get("failure")),
            )
            for task_id, record in dict(payload.get("records") or {}).items()
        }
        store._checkpoints = {
            checkpoint_id: RuntimeCheckpoint.from_dict(dict(checkpoint))
            for checkpoint_id, checkpoint in dict(payload.get("checkpoints") or {}).items()
        }
        store._interrupts = {
            interrupt_id: RuntimeInterrupt.from_dict(dict(interrupt))
            for interrupt_id, interrupt in dict(payload.get("interrupts") or {}).items()
        }
        store._events = {
            task_id: [DurableRuntimeEvent.from_dict(dict(event)) for event in events]
            for task_id, events in dict(payload.get("events") or {}).items()
        }
        return store


class SingleControllerDurableRuntime:
    """PHASE06 durable state machine on top of the Single Controller harness."""

    def __init__(self, *, store: InMemoryDurableRuntimeStore | None = None) -> None:
        self.store = store or InMemoryDurableRuntimeStore()
        self.harness = build_single_controller_runtime_harness()

    def start_task(
        self,
        state: ControllerRuntimeState,
        *,
        interrupt_at_node: str | None = None,
        required_approval: str = "",
        interrupt_payload: dict[str, Any] | None = None,
        stop_after_node: str | None = None,
    ) -> DurableRuntimeTaskSnapshot:
        if self.store.has_task(state.task_id):
            raise ValueError(f"durable runtime task already exists: {state.task_id}")
        self.store.create_task(state, status="running")
        self._append_event(state, type="runtime_started", status="running")
        return self._run_from_node(
            state=state,
            start_node=self.harness.node_names()[0],
            interrupt_at_node=interrupt_at_node,
            required_approval=required_approval,
            interrupt_payload=interrupt_payload,
            stop_after_node=stop_after_node,
        )

    def resume_task(
        self,
        *,
        task_id: str,
        approval_decision: str,
        comment: str | None = None,
    ) -> DurableRuntimeTaskSnapshot:
        interrupt = self.store.pending_interrupt(task_id)
        if interrupt is None:
            raise ValueError(f"durable runtime task is not waiting for approval: {task_id}")
        normalized_decision = approval_decision.strip().lower()
        if normalized_decision not in {"approved", "rejected"}:
            raise ValueError("approval_decision must be approved or rejected")

        state = self.harness.resume_from_checkpoint(self.store.latest_checkpoint(task_id))
        self._append_event(
            state,
            type="runtime_approval_decision",
            status="resuming" if normalized_decision == "approved" else "failed",
            node=interrupt.node,
            payload={"decision": normalized_decision, "comment": comment},
        )
        if normalized_decision == "rejected":
            self.store.clear_interrupt(task_id)
            return self.mark_failure(
                task_id,
                node=interrupt.node,
                error=comment or "approval rejected",
                recoverable=False,
            )

        self.store.clear_interrupt(task_id)
        self.store.update_status(task_id, "running")
        self._append_event(
            state,
            type="runtime_resumed",
            status="running",
            node=interrupt.node,
            payload={"approval": "approved"},
        )
        return self._run_from_node(state=state, start_node=interrupt.node)

    def cancel_task(self, task_id: str, *, reason: str) -> DurableRuntimeTaskSnapshot:
        record = self.store.get_record(task_id)
        if record.status in {"completed", "failed", "cancelled"}:
            raise ValueError(f"durable runtime task cannot be cancelled from {record.status}")
        self.store.update_status(task_id, "cancelled")
        self._append_event(
            record.state,
            type="runtime_cancelled",
            status="cancelled",
            node=record.state.current_step,
            payload={"reason": reason},
        )
        return self.store.snapshot(task_id)

    def mark_failure(
        self,
        task_id: str,
        *,
        node: str,
        error: str,
        recoverable: bool,
        details: dict[str, Any] | None = None,
    ) -> DurableRuntimeTaskSnapshot:
        record = self.store.get_record(task_id)
        failure = {
            "task_id": task_id,
            "trace_id": record.state.trace_id,
            "thread_id": record.state.thread_id,
            "workspace_id": record.state.workspace_id,
            "node": node,
            "error": error,
            "recoverable": recoverable,
            "latest_checkpoint_id": record.latest_checkpoint_id,
            **deepcopy(dict(details or {})),
        }
        self.store.mark_failure(task_id, failure)
        self._append_event(
            record.state,
            type="runtime_failed",
            status="failed",
            node=node,
            payload=failure,
        )
        return self.store.snapshot(task_id)

    def get_task_snapshot(self, task_id: str) -> DurableRuntimeTaskSnapshot | None:
        if not self.store.has_task(task_id):
            return None
        return self.store.snapshot(task_id)

    def _run_from_node(
        self,
        *,
        state: ControllerRuntimeState,
        start_node: str,
        interrupt_at_node: str | None = None,
        required_approval: str = "",
        interrupt_payload: dict[str, Any] | None = None,
        stop_after_node: str | None = None,
    ) -> DurableRuntimeTaskSnapshot:
        node_names = self.harness.node_names()
        start_index = node_names.index(start_node)
        current_state = state
        for node in node_names[start_index:]:
            if interrupt_at_node == node:
                current_state = self._checkpoint(current_state, node=node, reason="approval_wait")
                interrupt = self.harness.request_interrupt(
                    current_state,
                    node=node,
                    reason="approval_required",
                    required_approval=required_approval,
                    payload=deepcopy(dict(interrupt_payload or {})),
                )
                self.store.save_interrupt(interrupt)
                self.store.update_status(current_state.task_id, "approval_waiting")
                self._append_event(
                    current_state,
                    type="runtime_interrupt",
                    status="approval_waiting",
                    node=node,
                    payload=interrupt.to_dict(),
                )
                return self.store.snapshot(current_state.task_id)

            current_state = self._execute_node(current_state, node)
            current_state = self._checkpoint(current_state, node=node, reason="node_completed")
            self._append_event(
                current_state,
                type="runtime_node",
                status="completed",
                node=node,
                payload={"checkpoint_id": current_state.checkpoints[-1]},
            )
            if stop_after_node == node:
                self.store.update_status(current_state.task_id, "running")
                return self.store.snapshot(current_state.task_id)

        self.store.update_status(current_state.task_id, "completed")
        self._append_event(current_state, type="runtime_completed", status="completed")
        return self.store.snapshot(current_state.task_id)

    def _execute_node(self, state: ControllerRuntimeState, node: str) -> ControllerRuntimeState:
        if node == "prepare_context":
            context_pack = {
                **state.context_pack,
                "runtime_topology": self.harness.runtime_topology,
                "goal": state.goal,
            }
            return replace(state, current_step=node, context_pack=context_pack)
        if node == "plan":
            plan = state.plan or (f"Complete task: {state.goal}",)
            return replace(state, current_step=node, plan=plan)
        if node == "act_react_loop":
            tool_calls = state.tool_calls + ({"node": node, "status": "completed"},)
            observations = state.observations + ({"node": node, "result": "action_completed"},)
            return replace(
                state,
                current_step=node,
                tool_calls=tool_calls,
                observations=observations,
            )
        if node == "observe":
            observations = state.observations + ({"node": node, "result": "observed"},)
            return replace(state, current_step=node, observations=observations)
        if node == "evidence_check":
            retrieval_events = state.retrieval_events + (
                {"node": node, "coverage": "deterministic"},
            )
            return replace(state, current_step=node, retrieval_events=retrieval_events)
        if node == "reflect":
            observations = state.observations + ({"node": node, "reflection": "sufficient"},)
            return replace(state, current_step=node, observations=observations)
        if node == "replan_if_needed":
            return replace(state, current_step=node)
        if node == "answer_or_artifact":
            artifact_refs = state.artifact_refs + (f"artifact:{state.task_id}:answer",)
            return replace(state, current_step=node, artifact_refs=artifact_refs)
        if node == "post_turn_commit":
            memory_candidates = state.memory_candidates + (f"summary:{state.task_id}",)
            return replace(state, current_step=node, memory_candidates=memory_candidates)
        return replace(state, current_step=node)

    def _checkpoint(
        self,
        state: ControllerRuntimeState,
        *,
        node: str,
        reason: str,
    ) -> ControllerRuntimeState:
        checkpoint = self.harness.checkpoint_state(
            state,
            node=node,
            payload={"reason": reason},
        )
        self.store.save_checkpoint(checkpoint)
        checkpointed_state = replace(
            state,
            checkpoints=state.checkpoints + (checkpoint.checkpoint_id,),
        )
        self.store.update_state(checkpointed_state)
        return checkpointed_state

    def _append_event(
        self,
        state: ControllerRuntimeState,
        *,
        type: str,
        status: str,
        node: str = "",
        payload: dict[str, Any] | None = None,
    ) -> None:
        event_index = len(self.store.events(state.task_id)) + 1
        self.store.append_event(
            DurableRuntimeEvent(
                event_id=f"{state.task_id}:runtime_event:{event_index}",
                task_id=state.task_id,
                trace_id=state.trace_id,
                thread_id=state.thread_id,
                type=type,
                status=status,
                node=node,
                payload=deepcopy(dict(payload or {})),
            )
        )


__all__ = [
    "DurableRuntimeEvent",
    "DurableRuntimeTaskSnapshot",
    "InMemoryDurableRuntimeStore",
    "SingleControllerDurableRuntime",
]
