from __future__ import annotations

from enum import StrEnum

from zuno.agent.runtime.contracts import ReflectionDecision, StrategyMode
from zuno.agent.runtime.state import AgentRuntimeState


class RuntimeNode(StrEnum):
    INPUT_GATE = "input_gate"
    BUILD_CONTEXT = "build_context"
    STRATEGY_SELECT = "strategy_select"
    CREATE_OR_UPDATE_PLAN = "create_or_update_plan"
    EXECUTE_STEP = "execute_step"
    OBSERVE = "observe"
    EVIDENCE_GATE = "evidence_gate"
    DRAFT_AND_BIND_CLAIMS = "draft_and_bind_claims"
    REFLECTION = "reflection"
    REPLAN = "replan"
    REVISE_DRAFT = "revise_draft"
    APPROVAL = "approval"
    INTERRUPT = "interrupt"
    FINALIZE = "finalize"
    POST_TURN_COMMIT = "post_turn_commit"
    END = "end"


GRAPH_NODE_ORDER: tuple[RuntimeNode, ...] = (
    RuntimeNode.INPUT_GATE,
    RuntimeNode.BUILD_CONTEXT,
    RuntimeNode.STRATEGY_SELECT,
    RuntimeNode.CREATE_OR_UPDATE_PLAN,
    RuntimeNode.EXECUTE_STEP,
    RuntimeNode.OBSERVE,
    RuntimeNode.EVIDENCE_GATE,
    RuntimeNode.DRAFT_AND_BIND_CLAIMS,
    RuntimeNode.REFLECTION,
    RuntimeNode.REPLAN,
    RuntimeNode.REVISE_DRAFT,
    RuntimeNode.APPROVAL,
    RuntimeNode.INTERRUPT,
    RuntimeNode.FINALIZE,
    RuntimeNode.POST_TURN_COMMIT,
)


def route_after_strategy(state: AgentRuntimeState) -> RuntimeNode:
    if state.strategy is None:
        return RuntimeNode.CREATE_OR_UPDATE_PLAN
    if state.strategy.mode == StrategyMode.DIRECT_ANSWER:
        return RuntimeNode.DRAFT_AND_BIND_CLAIMS
    return RuntimeNode.CREATE_OR_UPDATE_PLAN


def route_after_reflection(state: AgentRuntimeState) -> RuntimeNode:
    decision = ReflectionDecision(state.reflection_decision or ReflectionDecision.PASS)
    if decision == ReflectionDecision.PASS:
        return RuntimeNode.FINALIZE
    if decision == ReflectionDecision.REWRITE_ANSWER:
        return RuntimeNode.REVISE_DRAFT
    if decision in {ReflectionDecision.RETRIEVE_MORE, ReflectionDecision.REPLAN}:
        return RuntimeNode.REPLAN
    if decision == ReflectionDecision.USE_TOOL:
        return RuntimeNode.APPROVAL
    if decision == ReflectionDecision.ASK_USER:
        return RuntimeNode.INTERRUPT
    if decision in {ReflectionDecision.ABSTAIN, ReflectionDecision.REFUSE}:
        return RuntimeNode.FINALIZE
    return RuntimeNode.FINALIZE


def hard_limit_route(state: AgentRuntimeState) -> RuntimeNode | None:
    if state.counters.steps_executed >= state.limits.max_steps:
        return RuntimeNode.FINALIZE
    if state.counters.replans > state.limits.max_replans:
        return RuntimeNode.FINALIZE
    if state.counters.reflections > state.limits.max_reflections:
        return RuntimeNode.FINALIZE
    return None


__all__ = [
    "GRAPH_NODE_ORDER",
    "RuntimeNode",
    "hard_limit_route",
    "route_after_reflection",
    "route_after_strategy",
]
