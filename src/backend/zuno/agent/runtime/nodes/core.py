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
from zuno.agent.runtime.planning.replan import ReplanEngine
from zuno.agent.runtime.reflection import ReflectionEngine
from zuno.agent.runtime.routing import RuntimeNode
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.agent.runtime.synthesis import GroundedSynthesisEngine
from zuno.memory.contracts import MemoryScope
from zuno.memory.policy import RetentionPolicy
from zuno.memory.reflexion import ReflexionCandidateBuilder

RuntimeNodeHandler = Callable[[AgentRuntimeState, RuntimeDependencies], AgentRuntimeState]
_STRATEGY_SELECTOR = RuntimeStrategySelector()
_PLANNER = RuntimePlanner()
_PLAN_EXECUTOR = PlanExecutor()
_REPLAN_ENGINE = ReplanEngine()
_REFLECTION_ENGINE = ReflectionEngine()
_SYNTHESIS_ENGINE = GroundedSynthesisEngine()
_REFLEXION_BUILDER = ReflexionCandidateBuilder()
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
    if deps.memory_engine is not None and hasattr(deps.memory_engine, "build_context_pack"):
        scope = _memory_scope(state)
        memory_context = deps.memory_engine.build_context_pack(
            scope=scope,
            context_pack_id=f"context:{state.run_id}",
            user_goal=state.goal,
            task_state={"thread_id": state.thread_id, "task_id": state.task_id},
            selected_evidence=[],
            allowed_capabilities=state.capability_plan.allowed_capabilities,
            safety_policy={"memory_context": "enabled"},
            output_contract={"runtime": "unified_graph_memory_context"},
            budget_tokens=state.limits.token_budget or 512,
            task_id=state.task_id,
            trace_id=state.trace_id,
        )
        context_payload = dict(memory_context["context_pack"])
        items = list(memory_context.get("items") or [])
        context_payload["task_state"] = {
            **dict(context_payload.get("task_state") or {}),
            "memory_context_trace": memory_context.get("trace", {}),
            "memory_context_items": items,
            "memory_influenced_strategy": bool(context_payload.get("selected_memory_refs")),
            "memory_strategy_hints": [
                str(item.get("content"))
                for item in items
                if item.get("source") in {"procedural_memory", "episodic_memory"}
            ],
        }
        context_pack = ContextPack.model_validate(context_payload)
        return _record_node(
            replace(state, context_pack=context_pack),
            RuntimeNode.BUILD_CONTEXT,
            summary="context pack prepared with memory read",
        )
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
    evidence_refs = state.evidence_refs or [
        evidence_id
        for observation in state.observations
        for evidence_id in observation.evidence_ids
    ]
    has_explicit_retrieval = any(observation.kind == ObservationKind.RETRIEVAL for observation in state.observations)
    if not evidence_refs and not has_explicit_retrieval:
        evidence_refs = [f"evidence:{state.run_id}:skeleton"]
    counters = state.counters.model_copy(update={"retrieval_rounds": state.counters.retrieval_rounds + 1})
    return _record_node(
        replace(state, evidence_refs=evidence_refs, counters=counters),
        RuntimeNode.EVIDENCE_GATE,
        summary="evidence gate recorded evidence refs",
    )


def draft_and_bind_claims(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    synthesis_observation = _SYNTHESIS_ENGINE.synthesize(state)
    return _record_node(
        replace(state, observations=[*state.observations, synthesis_observation]),
        RuntimeNode.DRAFT_AND_BIND_CLAIMS,
        summary="claim binding boundary reached",
    )


def reflection(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    gate_result = _REFLECTION_ENGINE.decide(state)
    decision = gate_result.decision
    counters = state.counters.model_copy(update={"reflections": state.counters.reflections + 1})
    observation = NormalizedObservation(
        observation_id=f"reflection:{state.run_id}:{counters.reflections}",
        kind=ObservationKind.REFLECTION,
        status=ObservationStatus.COMPLETED,
        source="ReflectionEngine",
        summary=f"reflection={decision.value}",
        failure_reason=None if decision == ReflectionDecision.PASS else gate_result.reason,
        metadata={
            "reflection_decision": decision.value,
            "reason": gate_result.reason,
            "unsupported_claims": list(gate_result.unsupported_claims),
        },
    )
    return _record_node(
        replace(
            state,
            reflection_decision=decision,
            counters=counters,
            observations=[*state.observations, observation],
        ),
        RuntimeNode.REFLECTION,
        summary=f"reflection={decision.value}",
    )


def replan(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    decision = ReflectionDecision(state.reflection_decision or ReflectionDecision.RETRIEVE_MORE)
    replan_result = _REPLAN_ENGINE.replan(state, decision)
    counters = state.counters.model_copy(update={"replans": state.counters.replans + 1})
    observation = NormalizedObservation(
        observation_id=f"replan:{state.run_id}:{counters.replans}",
        kind=ObservationKind.REPLAN,
        status=ObservationStatus.COMPLETED,
        source="ReplanEngine",
        summary=f"replan added {replan_result.diff['added_step_id']}",
        metadata={"replan_diff": replan_result.diff},
    )
    return _record_node(
        replace(
            state,
            counters=counters,
            plan_state=replan_result.plan_state,
            reflection_decision=None,
            observations=[*state.observations, observation],
        ),
        RuntimeNode.REPLAN,
        summary="remaining plan modified",
    )


def revise_draft(state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
    del deps
    observation = NormalizedObservation(
        observation_id=f"rewrite:{state.run_id}:{len(state.observations) + 1}",
        kind=ObservationKind.MODEL,
        status=ObservationStatus.COMPLETED,
        source="GroundedSynthesisEngine",
        summary="answer draft rewritten before finalization",
        evidence_ids=list(state.evidence_refs),
        metadata={"answer_rewritten": True},
    )
    return _record_node(
        replace(state, reflection_decision=None, observations=[*state.observations, observation]),
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
    if deps.memory_engine is not None:
        scope = _memory_scope(state)
        event = deps.memory_engine.append_event(
            scope=scope,
            event_id=f"event:{state.run_id}:post_turn",
            event_type="agent_turn",
            payload={
                "task": state.goal,
                "finalization_status": state.finalization_status.value,
                "reflection_decision": state.reflection_decision.value if state.reflection_decision else "",
                "artifact_refs": list(state.artifact_refs),
                "evidence_refs": list(state.evidence_refs),
            },
            trace_id=state.trace_id,
            task_id=state.task_id,
        )
        deps.memory_engine.summarize_task(
            scope=scope,
            summary_id=f"summary:{state.run_id}",
            content=f"{state.goal} -> {state.finalization_status.value}",
            source_event_ids=(event.event_id,),
            token_count=max(1, len(state.goal) // 4),
            metadata={"trace_id": state.trace_id, "task_id": state.task_id},
        )
        refs = [f"summary:{state.run_id}"]
        lesson = _REFLEXION_BUILDER.build(state)
        if lesson is not None:
            candidate = deps.memory_engine.submit_reflexion_lesson_candidate(
                scope=scope,
                lesson=lesson,
                retention_policy=RetentionPolicy(ttl_days=365),
            )
            refs.append(candidate.candidate_id)
        return _record_node(
            replace(state, memory_candidate_refs=[*state.memory_candidate_refs, *refs]),
            RuntimeNode.POST_TURN_COMMIT,
            summary="post-turn memory committed",
        )
    memory_refs = state.memory_candidate_refs or [f"memory_candidate:{state.run_id}:summary"]
    return _record_node(
        replace(state, memory_candidate_refs=memory_refs),
        RuntimeNode.POST_TURN_COMMIT,
        summary="post-turn commit boundary reached",
    )


def _memory_scope(state: AgentRuntimeState) -> MemoryScope:
    return MemoryScope(
        user_id=state.user_id,
        agent_id="unified_runtime",
        project_id=state.workspace_id,
        thread_id=state.thread_id,
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
