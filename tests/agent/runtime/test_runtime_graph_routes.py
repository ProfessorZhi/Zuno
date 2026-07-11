from __future__ import annotations

from zuno.agent.runtime import (
    ReflectionDecision,
    RuntimeNode,
    RuntimeStartRequest,
    SQLiteAgentRunStore,
    StrategyDecision,
    StrategyMode,
    UnifiedAgentRuntimeService,
    build_agent_graph,
    route_after_reflection,
    route_after_strategy,
)
from zuno.agent.runtime.state import AgentRuntimeState


def _request(task_id: str = "task_graph", **overrides) -> RuntimeStartRequest:
    payload = {
        "run_id": f"run:{task_id}",
        "thread_id": "thread_graph",
        "workspace_id": "workspace_graph",
        "user_id": "user_graph",
        "task_id": task_id,
        "trace_id": f"trace:{task_id}",
        "goal": "plan and execute a grounded answer",
    }
    payload.update(overrides)
    return RuntimeStartRequest(**payload)


def test_build_agent_graph_compiles_with_langgraph_1_0_10() -> None:
    graph = build_agent_graph()

    assert graph is not None


def test_runtime_routes_cover_direct_replan_rewrite_and_tool_paths() -> None:
    state = AgentRuntimeState(
        run_id="run",
        thread_id="thread",
        workspace_id="workspace",
        user_id="user",
        task_id="task",
        trace_id="trace",
        goal="goal",
        strategy=StrategyDecision(mode=StrategyMode.DIRECT_ANSWER, reason="unit"),
    )

    assert route_after_strategy(state) == RuntimeNode.DRAFT_AND_BIND_CLAIMS
    assert route_after_reflection(state) == RuntimeNode.FINALIZE
    assert route_after_reflection(_with_reflection(state, ReflectionDecision.RETRIEVE_MORE)) == RuntimeNode.REPLAN
    assert route_after_reflection(_with_reflection(state, ReflectionDecision.REWRITE_ANSWER)) == RuntimeNode.REVISE_DRAFT
    assert route_after_reflection(_with_reflection(state, ReflectionDecision.USE_TOOL)) == RuntimeNode.APPROVAL
    assert route_after_reflection(_with_reflection(state, ReflectionDecision.ASK_USER)) == RuntimeNode.INTERRUPT


def test_unified_runtime_service_completes_graph_and_persists_checkpoints(tmp_path) -> None:
    store = SQLiteAgentRunStore(tmp_path / "runtime.db")
    service = UnifiedAgentRuntimeService(store=store)

    snapshot = service.start(_request())

    assert snapshot.finalization_status == "finalized"
    assert snapshot.current_node == RuntimeNode.POST_TURN_COMMIT.value
    assert snapshot.plan_state is not None
    assert snapshot.artifact_refs == ["artifact:run:task_graph:answer"]
    assert snapshot.memory_candidate_refs
    assert snapshot.memory_candidate_refs[0] in {
        "memory_candidate:run:task_graph:summary",
        "summary:run:task_graph",
    }
    assert snapshot.checkpoint_refs
    assert store.snapshot("task_graph").status == "completed"
    assert store.latest_checkpoint("task_graph").node == RuntimeNode.POST_TURN_COMMIT.value


def test_unified_runtime_stream_order_uses_runtime_events(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))

    events = list(service.stream(_request("task_stream")))

    assert [event.event_type for event in events][:2] == ["runtime_started", "runtime_node"]
    assert events[1].node == RuntimeNode.INPUT_GATE.value
    assert events[-1].event_type == "runtime_completed"
    assert events[-1].status == "completed"


def test_unified_runtime_skeleton_does_not_emit_simulated_marker(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))

    service.start(_request("task_no_simulated"))
    payload = store_payloads(service.store, "task_no_simulated")

    assert "status': 'simulated" not in payload
    assert '"status": "simulated"' not in payload


def _with_reflection(state: AgentRuntimeState, decision: ReflectionDecision) -> AgentRuntimeState:
    state.reflection_decision = decision
    return state


def store_payloads(store: SQLiteAgentRunStore, task_id: str) -> str:
    snapshot = store.snapshot(task_id).to_dict()
    return repr(snapshot)
