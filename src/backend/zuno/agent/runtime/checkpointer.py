from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any

from zuno.agent.durable_runtime import DurableRuntimeEvent
from zuno.agent.harness import ControllerRuntimeState, RuntimeCheckpoint, RuntimeInterrupt
from zuno.agent.runtime.state import AgentRuntimeSnapshot, AgentRuntimeState
from zuno.agent.runtime.store import AgentRunStore


class RuntimeGraphCheckpointer:
    """Store-backed PHASE05 checkpoint bridge for the unified runtime skeleton."""

    def __init__(self, store: AgentRunStore) -> None:
        self.store = store

    def ensure_run(self, state: AgentRuntimeState, *, status: str = "running") -> None:
        if not self.store.has_task(state.task_id):
            self.store.create_task(_controller_state_from_runtime_state(state), status=status)

    def persist_node(self, state: AgentRuntimeState, *, node: str, status: str = "completed") -> AgentRuntimeState:
        checkpoint = RuntimeCheckpoint(
            checkpoint_id=f"{state.trace_id}:{node}:checkpoint:{len(state.checkpoint_refs) + 1}",
            thread_id=state.thread_id,
            task_id=state.task_id,
            trace_id=state.trace_id,
            node=node,
            state=state.to_snapshot().model_dump(mode="json"),
            payload={"runtime": "unified_graph_skeleton"},
            state_version=state.to_snapshot().state_version,
        )
        self.store.update_state(_controller_state_from_runtime_state(state))
        self.store.save_checkpoint(checkpoint)
        checkpointed = replace(state, checkpoint_refs=[*state.checkpoint_refs, checkpoint.checkpoint_id])
        self.store.update_state(_controller_state_from_runtime_state(checkpointed))
        self.append_event(checkpointed, event_type="runtime_node", status=status, node=node)
        return checkpointed

    def persist_interrupt(
        self,
        state: AgentRuntimeState,
        *,
        node: str,
        reason: str,
        required_approval: str = "",
        payload: dict[str, Any] | None = None,
    ) -> AgentRuntimeState:
        interrupt = RuntimeInterrupt(
            interrupt_id=f"{state.trace_id}:{node}:interrupt",
            thread_id=state.thread_id,
            task_id=state.task_id,
            trace_id=state.trace_id,
            node=node,
            reason=reason,
            required_approval=required_approval,
            payload=deepcopy(dict(payload or {})),
        )
        self.store.save_interrupt(interrupt)
        self.store.update_status(state.task_id, "approval_waiting")
        self.append_event(
            state,
            event_type="runtime_interrupt",
            status="approval_waiting",
            node=node,
            payload=interrupt.to_dict(),
        )
        return state

    def complete(self, state: AgentRuntimeState) -> None:
        self.store.update_state(_controller_state_from_runtime_state(state))
        self.store.update_status(state.task_id, "completed")
        self.append_event(state, event_type="runtime_completed", status="completed")

    def cancel(self, task_id: str, *, reason: str) -> None:
        snapshot = self.store.snapshot(task_id)
        self.store.update_status(task_id, "cancelled")
        self.append_event(
            _runtime_state_from_checkpoint_state(snapshot.state.to_dict()),
            event_type="runtime_cancelled",
            status="cancelled",
            node=snapshot.state.current_step,
            payload={"reason": reason},
        )

    def append_event(
        self,
        state: AgentRuntimeState,
        *,
        event_type: str,
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
                type=event_type,
                status=status,
                node=node,
                payload=deepcopy(dict(payload or {})),
            )
        )


def _controller_state_from_runtime_state(state: AgentRuntimeState) -> ControllerRuntimeState:
    return ControllerRuntimeState(
        thread_id=state.thread_id,
        workspace_id=state.workspace_id,
        user_id=state.user_id,
        task_id=state.task_id,
        trace_id=state.trace_id,
        goal=state.goal,
        context_pack=state.to_snapshot().model_dump(mode="json"),
        current_step=state.current_node,
        observations=[obs.model_dump(mode="json") for obs in state.observations],
        approval_interrupts=tuple({"interrupt_ref": ref} for ref in state.interrupt_refs),
        memory_candidates=tuple(state.memory_candidate_refs),
        artifact_refs=tuple(state.artifact_refs),
        checkpoints=tuple(state.checkpoint_refs),
    )


def _runtime_state_from_checkpoint_state(payload: dict[str, Any]) -> AgentRuntimeState:
    context_pack = dict(payload.get("context_pack") or {})
    if context_pack.get("state_version"):
        return AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(context_pack))
    return AgentRuntimeState(
        run_id=f"run:{payload.get('task_id') or ''}",
        thread_id=str(payload.get("thread_id") or ""),
        workspace_id=str(payload.get("workspace_id") or ""),
        user_id=str(payload.get("user_id") or ""),
        task_id=str(payload.get("task_id") or ""),
        trace_id=str(payload.get("trace_id") or ""),
        goal=str(payload.get("goal") or ""),
        current_node=str(payload.get("current_step") or ""),
    )


__all__ = ["RuntimeGraphCheckpointer"]
