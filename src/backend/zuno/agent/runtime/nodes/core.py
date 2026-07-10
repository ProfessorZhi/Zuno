from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Callable

from zuno.agent.contracts import ContextPack
from zuno.agent.runtime.contracts import (
    FinalizationStatus,
    NodeOutcome,
    NormalizedObservation,
    ObservationKind,
    ObservationStatus,
    ReflectionDecision,
    StrategyDecision,
    StrategyMode,
)
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution import (
    KnowledgeStepExecutor,
    ModelStepExecutor,
    ReActStepExecutor,
    StepExecutorRegistry,
    ToolStepExecutor,
)
from zuno.agent.runtime.planning import PlanExecutor, RuntimePlanner, RuntimeStrategySelector
from zuno.agent.runtime.routing import RuntimeNode
from zuno.agent.runtime.state import AgentRuntimeState

RuntimeNodeHandler = Callable[[AgentRuntimeState, RuntimeDependencies], AgentRuntimeState]
_STRATEGY_SELECTOR = RuntimeStrategySelector()
_PLANNER = RuntimePlanner()
_PLAN_EXECUTOR = PlanExecutor()
_STEP_EXECUTORS = StepExecutorRegistry(
    (
        KnowledgeStepExecutor(),
        ToolStepExecutor(),
        ModelStepExecutor(),
        ReActStepExecutor(),
    )
)


def input_gate(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    return _record_node(state, RuntimeNode.INPUT_GATE, summary="input accepted")


def build_context(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    context_pack = state.context_pack or ContextPack(
        context_pack_id=f"context:{state.run_id}",
        user_goal=state.goal,
        task_state={"thread_id": state.thread_id, "task_id": state.task_id},
        output_contract={"runtime": "unified_graph_skeleton"},
        budget=state.limits.model_dump(),
    )
    return _record_node(
        replace(state, context_pack=context_pack),
        RuntimeNode.BUILD_CONTEXT,
        summary="context pack prepared",
    )


def strategy_select(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    if state.strategy is None:
        state = _STRATEGY_SELECTOR.select(state, deps)
    return _record_node(
        state,
        RuntimeNode.STRATEGY_SELECT,
        summary=f"strategy={StrategyMode(state.strategy.mode).value if state.strategy else 'missing'}",
    )


def create_or_update_plan(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    state = _PLANNER.plan(state, deps)
    plan_state = state.plan_state
    return _record_node(
        replace(state, plan_state=plan_state, current_step_id=plan_state.current_step_id),
        RuntimeNode.CREATE_OR_UPDATE_PLAN,
        summary="plan available",
    )


def execute_step(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    if state.plan_state is None:
        state = _PLANNER.plan(state, deps)
    step = _PLAN_EXECUTOR.next_ready_step(state.plan_state)
    if step is None:
        return _record_node(state, RuntimeNode.EXECUTE_STEP, summary="no ready step")
    running_plan = _PLAN_EXECUTOR.mark_running(state.plan_state, step)
    running_step = next(item for item in running_plan.steps if item.step_id == step.step_id)
    result = _STEP_EXECUTORS.execute(state=replace(state, plan_state=running_plan), step=running_step, deps=deps)
    if result.status == ObservationStatus.COMPLETED:
        plan_state = _PLAN_EXECUTOR.mark_completed(
            running_plan,
            running_step,
            observation_ref=result.observation.observation_id,
        )
        finalization_status = state.finalization_status
        interrupt_refs = state.interrupt_refs
    elif result.status == ObservationStatus.WAITING and result.interrupt_required:
        plan_state = running_plan
        finalization_status = FinalizationStatus.INTERRUPTED
        interrupt_refs = [*state.interrupt_refs, result.idempotency_key]
    else:
        plan_state = _PLAN_EXECUTOR.mark_failed(
            running_plan,
            running_step,
            observation_ref=result.observation.observation_id,
        )
        finalization_status = state.finalization_status
        interrupt_refs = state.interrupt_refs
    counters = state.counters.model_copy(update={"steps_executed": state.counters.steps_executed + 1})
    return _record_node(
        replace(
            state,
            observations=[*state.observations, result.observation],
            plan_state=plan_state,
            current_step_id=plan_state.current_step_id,
            counters=counters,
            finalization_status=finalization_status,
            interrupt_refs=interrupt_refs,
        ),
        RuntimeNode.EXECUTE_STEP,
        summary=f"step executed: {running_step.action_type}",
    )


def observe(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    return _record_node(state, RuntimeNode.OBSERVE, summary="observation normalized")


def evidence_gate(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    evidence_refs = state.evidence_refs or [f"evidence:{state.run_id}:skeleton"]
    counters = state.counters.model_copy(update={"retrieval_rounds": state.counters.retrieval_rounds + 1})
    return _record_node(
        replace(state, evidence_refs=evidence_refs, counters=counters),
        RuntimeNode.EVIDENCE_GATE,
        summary="evidence gate recorded deterministic evidence ref",
    )


def draft_and_bind_claims(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    return _record_node(state, RuntimeNode.DRAFT_AND_BIND_CLAIMS, summary="claim binding boundary reached")


def reflection(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    decision = ReflectionDecision(state.reflection_decision or ReflectionDecision.PASS)
    counters = state.counters.model_copy(update={"reflections": state.counters.reflections + 1})
    return _record_node(
        replace(state, reflection_decision=decision, counters=counters),
        RuntimeNode.REFLECTION,
        summary=f"reflection={decision.value}",
    )


def replan(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    counters = state.counters.model_copy(update={"replans": state.counters.replans + 1})
    plan_state = state.plan_state
    if plan_state is not None:
        plan_state = plan_state.model_copy(update={"status": "replanned"})
    return _record_node(
        replace(state, counters=counters, plan_state=plan_state, reflection_decision=ReflectionDecision.PASS),
        RuntimeNode.REPLAN,
        summary="remaining plan modified",
    )


def revise_draft(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    return _record_node(
        replace(state, reflection_decision=ReflectionDecision.PASS),
        RuntimeNode.REVISE_DRAFT,
        summary="draft revision boundary reached",
    )


def approval(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    counters = state.counters.model_copy(update={"interrupts": state.counters.interrupts + 1})
    interrupt_ref = f"interrupt:{state.run_id}:approval"
    return _record_node(
        replace(
            state,
            counters=counters,
            interrupt_refs=[*state.interrupt_refs, interrupt_ref],
            finalization_status=FinalizationStatus.INTERRUPTED,
        ),
        RuntimeNode.APPROVAL,
        summary="approval interrupt requested",
    )


def interrupt(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    counters = state.counters.model_copy(update={"interrupts": state.counters.interrupts + 1})
    interrupt_ref = f"interrupt:{state.run_id}:ask_user"
    return _record_node(
        replace(
            state,
            counters=counters,
            interrupt_refs=[*state.interrupt_refs, interrupt_ref],
            finalization_status=FinalizationStatus.INTERRUPTED,
        ),
        RuntimeNode.INTERRUPT,
        summary="user interrupt requested",
    )


def finalize(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    decision = ReflectionDecision(state.reflection_decision or ReflectionDecision.PASS)
    if decision in {ReflectionDecision.ABSTAIN, ReflectionDecision.REFUSE}:
        status = FinalizationStatus.ABSTAINED
    else:
        status = FinalizationStatus.FINALIZED
    artifact_refs = state.artifact_refs or [f"artifact:{state.run_id}:answer"]
    return _record_node(
        replace(state, finalization_status=status, artifact_refs=artifact_refs),
        RuntimeNode.FINALIZE,
        summary=f"finalization={status.value}",
    )


def post_turn_commit(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    memory_refs = state.memory_candidate_refs or [f"memory_candidate:{state.run_id}:summary"]
    return _record_node(
        replace(state, memory_candidate_refs=memory_refs),
        RuntimeNode.POST_TURN_COMMIT,
        summary="post-turn commit boundary reached",
    )


def _record_node(state: AgentRuntimeState, node: RuntimeNode, *, summary: str) -> AgentRuntimeState:
    trace_event_id = f"{state.trace_id}:{len(state.trace_event_ids) + 1:04d}:{node.value}"
    outcome = NodeOutcome(
        node=node.value,
        status=ObservationStatus.COMPLETED,
        trace_event_ids=[trace_event_id],
    )
    return replace(
        state,
        current_node=node.value,
        node_outcomes=[*deepcopy(state.node_outcomes), outcome.model_dump(mode="json")],
        trace_event_ids=[*state.trace_event_ids, trace_event_id],
    )


DEFAULT_RUNTIME_NODES: dict[RuntimeNode, RuntimeNodeHandler] = {
    RuntimeNode.INPUT_GATE: input_gate,
    RuntimeNode.BUILD_CONTEXT: build_context,
    RuntimeNode.STRATEGY_SELECT: strategy_select,
    RuntimeNode.CREATE_OR_UPDATE_PLAN: create_or_update_plan,
    RuntimeNode.EXECUTE_STEP: execute_step,
    RuntimeNode.OBSERVE: observe,
    RuntimeNode.EVIDENCE_GATE: evidence_gate,
    RuntimeNode.DRAFT_AND_BIND_CLAIMS: draft_and_bind_claims,
    RuntimeNode.REFLECTION: reflection,
    RuntimeNode.REPLAN: replan,
    RuntimeNode.REVISE_DRAFT: revise_draft,
    RuntimeNode.APPROVAL: approval,
    RuntimeNode.INTERRUPT: interrupt,
    RuntimeNode.FINALIZE: finalize,
    RuntimeNode.POST_TURN_COMMIT: post_turn_commit,
}


__all__ = ["DEFAULT_RUNTIME_NODES", "RuntimeNodeHandler"]
