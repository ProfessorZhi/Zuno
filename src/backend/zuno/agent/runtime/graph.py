from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.nodes import DEFAULT_RUNTIME_NODES
from zuno.agent.runtime.contracts import FinalizationStatus
from zuno.agent.runtime.routing import RuntimeNode, route_after_reflection, route_after_strategy
from zuno.agent.runtime.state import AgentRuntimeSnapshot, AgentRuntimeState


def build_agent_graph(dependencies: RuntimeDependencies | None = None, checkpointer: Any | None = None) -> Any:
    """Build the unified runtime graph.

    ``checkpointer`` is Zuno's domain checkpoint bridge, not a LangGraph BaseCheckpointSaver.
    Nodes persist through it after execution so the existing SQLite run store remains the
    domain source of truth while LangGraph owns transition control.
    """

    deps = dependencies or RuntimeDependencies()
    graph = StateGraph(dict)

    for node, handler in DEFAULT_RUNTIME_NODES.items():
        graph.add_node(node.value, _wrap_node(handler, deps, node=node, checkpointer=checkpointer))

    graph.add_edge(START, RuntimeNode.INPUT_GATE.value)
    graph.add_edge(RuntimeNode.INPUT_GATE.value, RuntimeNode.BUILD_CONTEXT.value)
    graph.add_edge(RuntimeNode.BUILD_CONTEXT.value, RuntimeNode.STRATEGY_SELECT.value)
    graph.add_conditional_edges(
        RuntimeNode.STRATEGY_SELECT.value,
        _route_after_strategy_payload,
        {
            RuntimeNode.CREATE_OR_UPDATE_PLAN.value: RuntimeNode.CREATE_OR_UPDATE_PLAN.value,
            RuntimeNode.DRAFT_AND_BIND_CLAIMS.value: RuntimeNode.DRAFT_AND_BIND_CLAIMS.value,
        },
    )
    graph.add_edge(RuntimeNode.CREATE_OR_UPDATE_PLAN.value, RuntimeNode.EXECUTE_STEP.value)
    graph.add_conditional_edges(
        RuntimeNode.EXECUTE_STEP.value,
        _route_after_execute_payload,
        {
            RuntimeNode.OBSERVE.value: RuntimeNode.OBSERVE.value,
            END: END,
        },
    )
    graph.add_conditional_edges(
        RuntimeNode.OBSERVE.value,
        _route_after_observe_payload,
        {
            RuntimeNode.EXECUTE_STEP.value: RuntimeNode.EXECUTE_STEP.value,
            RuntimeNode.EVIDENCE_GATE.value: RuntimeNode.EVIDENCE_GATE.value,
        },
    )
    graph.add_edge(RuntimeNode.EVIDENCE_GATE.value, RuntimeNode.DRAFT_AND_BIND_CLAIMS.value)
    graph.add_edge(RuntimeNode.DRAFT_AND_BIND_CLAIMS.value, RuntimeNode.REFLECTION.value)
    graph.add_conditional_edges(
        RuntimeNode.REFLECTION.value,
        _route_after_reflection_payload,
        {
            RuntimeNode.FINALIZE.value: RuntimeNode.FINALIZE.value,
            RuntimeNode.REVISE_DRAFT.value: RuntimeNode.REVISE_DRAFT.value,
            RuntimeNode.REPLAN.value: RuntimeNode.REPLAN.value,
            RuntimeNode.APPROVAL.value: RuntimeNode.APPROVAL.value,
            RuntimeNode.INTERRUPT.value: RuntimeNode.INTERRUPT.value,
        },
    )
    graph.add_edge(RuntimeNode.REPLAN.value, RuntimeNode.EXECUTE_STEP.value)
    graph.add_edge(RuntimeNode.REVISE_DRAFT.value, RuntimeNode.DRAFT_AND_BIND_CLAIMS.value)
    graph.add_edge(RuntimeNode.APPROVAL.value, END)
    graph.add_edge(RuntimeNode.INTERRUPT.value, END)
    graph.add_edge(RuntimeNode.FINALIZE.value, RuntimeNode.POST_TURN_COMMIT.value)
    graph.add_edge(RuntimeNode.POST_TURN_COMMIT.value, END)
    return graph.compile()


def _wrap_node(handler: Any, deps: RuntimeDependencies, *, node: RuntimeNode, checkpointer: Any | None) -> Any:
    def _node(payload: dict[str, Any]) -> dict[str, Any]:
        state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(payload)))
        next_state = handler(state, deps)
        if checkpointer is not None:
            next_state = checkpointer.persist_node(next_state, node=node.value)
            if next_state.finalization_status == FinalizationStatus.INTERRUPTED:
                last_observation = next_state.observations[-1] if next_state.observations else None
                metadata = dict(last_observation.metadata) if last_observation is not None else {}
                next_state = checkpointer.persist_interrupt(
                    next_state,
                    node=node.value,
                    reason=str(metadata.get("tool_runtime_status") or "interrupt_required"),
                    required_approval=str(metadata.get("required_approval") or "tool_or_capability"),
                    payload=metadata,
                )
            elif node == RuntimeNode.POST_TURN_COMMIT:
                checkpointer.complete(next_state)
        return next_state.to_snapshot().model_dump(mode="json")

    return _node


def _route_after_execute_payload(payload: dict[str, Any]) -> str:
    state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(payload)))
    if state.finalization_status == FinalizationStatus.INTERRUPTED:
        return END
    return RuntimeNode.OBSERVE.value


def _route_after_observe_payload(payload: dict[str, Any]) -> str:
    state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(payload)))
    if state.plan_state is not None and state.plan_state.status == "running" and state.plan_state.current_step_id:
        return RuntimeNode.EXECUTE_STEP.value
    return RuntimeNode.EVIDENCE_GATE.value


def _route_after_strategy_payload(payload: dict[str, Any]) -> str:
    state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(payload)))
    return route_after_strategy(state).value


def _route_after_reflection_payload(payload: dict[str, Any]) -> str:
    state = AgentRuntimeState.from_snapshot(AgentRuntimeSnapshot.from_payload(dict(payload)))
    return route_after_reflection(state).value


__all__ = ["build_agent_graph"]
