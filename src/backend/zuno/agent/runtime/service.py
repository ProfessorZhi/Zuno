from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from zuno.agent.durable_runtime import DurableRuntimeTaskSnapshot
from zuno.agent.runtime.checkpointer import RuntimeGraphCheckpointer
from zuno.agent.runtime.contracts import FinalizationStatus, ReflectionDecision, StrategyDecision, StrategyMode
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.factory import RuntimeDependencyFactory
from zuno.agent.runtime.graph import build_agent_graph
from zuno.agent.runtime.routing import (
    RuntimeNode,
    hard_limit_route,
    route_after_reflection,
    route_after_strategy,
)
from zuno.agent.runtime.state import AgentRuntimeSnapshot, AgentRuntimeState
from zuno.agent.runtime.store import AgentRunStore


@dataclass(frozen=True, slots=True)
class RuntimeStartRequest:
    run_id: str
    thread_id: str
    workspace_id: str
    user_id: str
    task_id: str
    trace_id: str
    goal: str
    strategy_mode: StrategyMode | str | None = None
    reflection_decision: ReflectionDecision | str | None = None


@dataclass(frozen=True, slots=True)
class RuntimeStreamEvent:
    event_type: str
    run_id: str
    task_id: str
    trace_id: str
    node: str
    status: str
    payload: dict


class UnifiedAgentRuntimeService:
    """PHASE05 unified graph skeleton facade.

    Product traffic stays on the existing path until the later feature-flag phase. This service
    gives tests and future integration work a single start/stream/resume/cancel/snapshot surface.
    """

    def __init__(
        self,
        *,
        dependencies: RuntimeDependencies | None = None,
        store: AgentRunStore,
        graph=None,
    ) -> None:
        self.dependencies = dependencies or RuntimeDependencyFactory().dependencies()
        self.store = store
        self.checkpointer = RuntimeGraphCheckpointer(store)
        self.graph = graph or build_agent_graph(dependencies=self.dependencies, checkpointer=self.checkpointer)

    def start(self, request: RuntimeStartRequest) -> AgentRuntimeSnapshot:
        state = AgentRuntimeState(
            run_id=request.run_id,
            thread_id=request.thread_id,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            goal=request.goal,
            strategy=(
                StrategyDecision(mode=StrategyMode(request.strategy_mode), reason="preset by caller")
                if request.strategy_mode
                else None
            ),
            reflection_decision=(
                ReflectionDecision(request.reflection_decision)
                if request.reflection_decision
                else None
            ),
        )
        self.checkpointer.ensure_run(state)
        self.checkpointer.append_event(state, event_type="runtime_started", status="running")
        final_payload = self.graph.invoke(state.to_snapshot().model_dump(mode="json"))
        final_state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(final_payload)))
        return final_state.to_snapshot()

    def stream(self, request: RuntimeStartRequest) -> Iterable[RuntimeStreamEvent]:
        snapshot = self.start(request)
        for event in self.store.events(request.task_id):
            yield RuntimeStreamEvent(
                event_type=event.type,
                run_id=request.run_id,
                task_id=event.task_id,
                trace_id=event.trace_id,
                node=event.node,
                status=event.status,
                payload=dict(event.payload),
            )
        if snapshot.finalization_status == FinalizationStatus.INTERRUPTED:
            return

    def resume(self, *, task_id: str, approval_decision: str = "approved") -> AgentRuntimeSnapshot:
        interrupt = self.store.pending_interrupt(task_id)
        if interrupt is None:
            raise ValueError(f"runtime task is not waiting for interrupt resume: {task_id}")
        if approval_decision.strip().lower() != "approved":
            snapshot = self.store.snapshot(task_id)
            self.store.clear_interrupt(task_id)
            self.store.update_status(task_id, "failed")
            return _runtime_state_from_task_snapshot(snapshot).to_snapshot()
        latest = self.store.latest_checkpoint(task_id)
        if latest is None:
            raise ValueError(f"runtime task has no checkpoint to resume: {task_id}")
        state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(latest.state)))
        interrupt_payload = dict(interrupt.payload or {})
        idempotency_key = str(interrupt_payload.get("idempotency_key") or "")
        if idempotency_key and f"approved:{idempotency_key}" not in state.interrupt_refs:
            if hasattr(self.store, "claim_tool_execution"):
                claimed = self.store.claim_tool_execution(
                    task_id=state.task_id,
                    workspace_id=state.workspace_id,
                    user_id=state.user_id,
                    idempotency_key=idempotency_key,
                    tool_name=str(interrupt_payload.get("required_approval") or "tool").removeprefix("tool:"),
                    payload={"step_id": state.current_step_id or "", "status": "claimed"},
                )
                if not claimed:
                    return state.to_snapshot()
            state = replace(
                state,
                interrupt_refs=[*state.interrupt_refs, f"approved:{idempotency_key}"],
                finalization_status=FinalizationStatus.NOT_READY,
            )
        else:
            state = replace(state, finalization_status=FinalizationStatus.NOT_READY)
        self.store.clear_interrupt(task_id)
        self.store.update_status(task_id, "running")
        resume_payload = {
            "interrupt_id": interrupt.interrupt_id,
            "decision": approval_decision,
            "approved_by": "runtime_resume",
            "idempotency_key": idempotency_key,
        }
        self.checkpointer.append_event(
            state,
            event_type="runtime_resumed",
            status="running",
            node=interrupt.node,
            payload=resume_payload,
        )
        final_payload = self.graph.invoke(state.to_snapshot().model_dump(mode="json"))
        final_state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(final_payload)))
        return final_state.to_snapshot()

    def cancel(self, *, task_id: str, reason: str) -> DurableRuntimeTaskSnapshot:
        self.checkpointer.cancel(task_id, reason=reason)
        return self.store.snapshot(task_id)

    def get_snapshot(self, task_id: str) -> AgentRuntimeSnapshot | None:
        if not self.store.has_task(task_id):
            return None
        return _runtime_state_from_task_snapshot(self.store.snapshot(task_id)).to_snapshot()


def _runtime_state_from_task_snapshot(snapshot: DurableRuntimeTaskSnapshot) -> AgentRuntimeState:
    checkpoint = snapshot.latest_checkpoint
    if checkpoint is not None and dict(checkpoint.state).get("state_version"):
        return AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(checkpoint.state)))
    context_pack = dict(snapshot.state.context_pack or {})
    if context_pack.get("state_version"):
        return AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(context_pack))
    return AgentRuntimeState(
        run_id=f"run:{snapshot.task_id}",
        thread_id=snapshot.thread_id,
        workspace_id=snapshot.workspace_id,
        user_id=snapshot.state.user_id,
        task_id=snapshot.task_id,
        trace_id=snapshot.trace_id,
        goal=snapshot.state.goal,
        current_node=snapshot.state.current_step,
    )


__all__ = [
    "RuntimeStartRequest",
    "RuntimeStreamEvent",
    "UnifiedAgentRuntimeService",
]
