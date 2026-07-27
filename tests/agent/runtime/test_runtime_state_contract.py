from __future__ import annotations

import pytest

from zuno.agent.contracts import CapabilityPlan, ContextPack, PlanState, PlanStep
from zuno.agent.runtime import (
    AGENT_RUNTIME_STATE_VERSION,
    AgentRuntimeSnapshot,
    AgentRuntimeState,
    FinalizationStatus,
    NormalizedObservation,
    ObservationKind,
    ReflectionDecision,
    RuntimeCounters,
    RuntimeLimits,
    StrategyDecision,
    StrategyMode,
    UnsupportedRuntimeStateVersion,
)
from zuno.agent.runtime.planning import RuntimeStrategySelector
from zuno.agent.runtime.dependencies import RuntimeDependencies


def test_runtime_snapshot_round_trips_as_json_with_string_enums() -> None:
    state = AgentRuntimeState(
        run_id="run-1",
        thread_id="thread-1",
        workspace_id="workspace-1",
        user_id="user-1",
        task_id="task-1",
        trace_id="trace-1",
        goal="answer with cited evidence",
        current_node="reflection",
        current_step_id="step-1",
        strategy=StrategyDecision(
            mode="plan_execute_with_replan",
            reason="multi-hop evidence needed",
            selected_skill_id="research_report",
            retrieval_profile="deep",
        ),
        plan_state=PlanState(
            plan_id="plan-1",
            status="planned",
            steps=[
                PlanStep(
                    step_id="step-1",
                    goal="retrieve evidence",
                    action_type="retrieve_evidence",
                    dependencies=[],
                    expected_output="evidence bundle",
                    acceptance_criteria=["evidence_count > 0"],
                    retrieval_policy_ref="retrieval:deep",
                    tool_policy_ref="tool:none",
                    model_role="executor",
                    attempt=1,
                )
            ],
            current_step_id="step-1",
        ),
        capability_plan=CapabilityPlan(allowed_capabilities=["knowledge.search"]),
        observations=[
            NormalizedObservation(
                observation_id="obs-1",
                step_id="step-1",
                kind=ObservationKind.RETRIEVAL,
                status="completed",
                source="test",
                summary="gold span found",
                evidence_ids=["ev-1"],
                citation_ids=["cite-1"],
            )
        ],
        reflection_decision=ReflectionDecision.PASS,
        finalization_status=FinalizationStatus.FINALIZED,
        limits=RuntimeLimits(max_steps=5, max_replans=2, max_reflections=2),
        counters=RuntimeCounters(steps_executed=1, reflections=1, retrieval_rounds=1),
        evidence_refs=["ev-1"],
        trace_event_ids=["evt-1"],
    )

    snapshot = state.to_snapshot()
    payload = snapshot.model_dump_json()
    restored = AgentRuntimeSnapshot.model_validate_json(payload)

    assert restored.state_version == AGENT_RUNTIME_STATE_VERSION
    assert restored.strategy is not None
    assert restored.strategy.mode == StrategyMode.PLAN_EXECUTE_WITH_REPLAN
    assert restored.observations[0].kind == ObservationKind.RETRIEVAL
    assert restored.finalization_status == FinalizationStatus.FINALIZED
    assert restored.plan_state is not None
    assert restored.plan_state.steps[0].expected_output == "evidence bundle"
    assert restored.plan_state.steps[0].acceptance_criteria == ["evidence_count > 0"]


def test_unknown_runtime_state_version_is_rejected() -> None:
    payload = {
        "state_version": "agent-runtime-v999",
        "run_id": "run-1",
        "thread_id": "thread-1",
        "workspace_id": "workspace-1",
        "user_id": "user-1",
        "task_id": "task-1",
        "trace_id": "trace-1",
        "goal": "goal",
    }

    with pytest.raises(UnsupportedRuntimeStateVersion):
        AgentRuntimeSnapshot.from_payload(payload)


def test_runtime_state_keeps_payload_refs_instead_of_raw_sensitive_payload() -> None:
    observation = NormalizedObservation(
        observation_id="obs-sensitive",
        kind="tool",
        status="completed",
        source="tool",
        summary="tool succeeded",
        payload_ref="object-store://observations/obs-sensitive",
        metadata={"credential_ref": "cred:workspace:mail"},
    )
    snapshot = AgentRuntimeState(
        run_id="run-1",
        thread_id="thread-1",
        workspace_id="workspace-1",
        user_id="user-1",
        task_id="task-1",
        trace_id="trace-1",
        goal="send email",
        observations=[observation],
    ).to_snapshot()

    json_payload = snapshot.model_dump_json()

    assert "object-store://observations/obs-sensitive" in json_payload
    assert "raw_secret" not in json_payload
    assert "api_key" not in json_payload


def test_runtime_strategy_selection_pins_capability_snapshot_refs_in_context_pack() -> None:
    state = AgentRuntimeState(
        run_id="run-capability",
        thread_id="thread-capability",
        workspace_id="workspace-capability",
        user_id="user-capability",
        task_id="task-capability",
        trace_id="trace-capability",
        goal="Search the web for sources and summarize the result.",
        context_pack=ContextPack(
            context_pack_id="context-capability",
            user_goal="Search the web for sources and summarize the result.",
            task_state={"caller_ref": "kept"},
        ),
        capability_plan=CapabilityPlan(
            allowed_capabilities=["knowledge.research_corpus", "tool.web.search"]
        ),
    )

    selected = RuntimeStrategySelector().select(state, deps=None)
    snapshot = selected.to_snapshot()
    task_state = snapshot.context_pack.task_state

    assert selected.capability_plan.selection_validity == "fixed_planning_snapshot"
    assert task_state["caller_ref"] == "kept"
    assert task_state["capability_availability_snapshot_ref"] == selected.capability_plan.availability_snapshot_ref
    assert task_state["capability_selection_result_ref"] == selected.capability_plan.selection_result_ref
    assert task_state["capability_selection_validity"] == "fixed_planning_snapshot"
    assert task_state["capability_planner_exposure_ref"] == (
        selected.capability_plan.risk_summary["planner_exposure"]["exposure_ref"]
    )
    assert task_state["capability_planner_exposure_visibility"] == (
        "planner_authorized_summary_schema_only"
    )


def test_runtime_strategy_selection_reuses_pinned_capability_refs() -> None:
    state = AgentRuntimeState(
        run_id="run-pinned-capability",
        thread_id="thread-pinned-capability",
        workspace_id="workspace-capability",
        user_id="user-pinned-capability",
        task_id="task-pinned-capability",
        trace_id="trace-pinned-capability",
        goal="Search the web for sources and summarize the result.",
        context_pack=ContextPack(
            context_pack_id="context-pinned-capability",
            user_goal="Search the web for sources and summarize the result.",
            task_state={
                "capability_availability_snapshot_ref": "capability_snapshot:pinned",
                "capability_selection_result_ref": "capability_selection:pinned",
                "capability_selection_validity": "fixed_planning_snapshot",
                "capability_planner_exposure_ref": "capability_exposure:pinned",
                "capability_planner_exposure_visibility": "planner_authorized_summary_schema_only",
            },
        ),
        capability_plan=CapabilityPlan(
            allowed_capabilities=["tool.web.search"],
            allowed_tools=["tool.web.search"],
        ),
    )

    selected = RuntimeStrategySelector().select(state, deps=None)

    assert selected.capability_plan.availability_snapshot_ref == "capability_snapshot:pinned"
    assert selected.capability_plan.selection_result_ref == "capability_selection:pinned"
    assert selected.capability_plan.allowed_tools == ["tool.web.search"]
    assert selected.capability_plan.executed_tools == []
    assert all(
        step.input_refs == ["capability_snapshot:pinned", "capability_selection:pinned"]
        for step in selected.plan_state.steps
    )
    assert all(step.tool_policy_ref == "capability_selection:pinned" for step in selected.plan_state.steps)


def test_runtime_strategy_selection_uses_capability_runtime_port() -> None:
    class FakeCapabilityRuntime:
        def __init__(self) -> None:
            self.requests = []

        def select(self, request):
            self.requests.append(dict(request))
            return CapabilityPlan(
                availability_snapshot_ref="capability_snapshot:runtime",
                selection_result_ref="capability_selection:runtime",
                selection_validity="fixed_planning_snapshot",
                allowed_capabilities=["tool.web.search"],
                allowed_tools=["tool.web.search"],
                risk_summary={
                    "planner_exposure": {
                        "exposure_ref": "capability_exposure:runtime",
                        "visibility": "planner_authorized_summary_schema_only",
                    }
                },
            )

    capability_runtime = FakeCapabilityRuntime()
    state = AgentRuntimeState(
        run_id="run-runtime-capability",
        thread_id="thread-runtime-capability",
        workspace_id="workspace-capability",
        user_id="user-runtime-capability",
        task_id="task-runtime-capability",
        trace_id="trace-runtime-capability",
        goal="Search the web for sources and summarize the result.",
        capability_plan=CapabilityPlan(
            allowed_capabilities=["tool.web.search"],
        ),
    )

    selected = RuntimeStrategySelector().select(
        state,
        deps=RuntimeDependencies(capability_runtime=capability_runtime),
    )

    assert capability_runtime.requests[0]["available_capability_ids"] == ("tool.web.search",)
    assert selected.capability_plan.availability_snapshot_ref == "capability_snapshot:runtime"
    assert selected.capability_plan.selection_result_ref == "capability_selection:runtime"
    assert all(step.tool_policy_ref == "capability_selection:runtime" for step in selected.plan_state.steps)


def test_runtime_strategy_selection_blocks_when_capability_runtime_fails() -> None:
    class FailingCapabilityRuntime:
        def select(self, request):
            del request
            raise RuntimeError("capability-db-unavailable")

    state = AgentRuntimeState(
        run_id="run-capability-fail",
        thread_id="thread-capability-fail",
        workspace_id="workspace-capability",
        user_id="user-capability-fail",
        task_id="task-capability-fail",
        trace_id="trace-capability-fail",
        goal="Search the web for sources and summarize the result.",
        capability_plan=CapabilityPlan(
            allowed_capabilities=["tool.web.search"],
        ),
    )

    selected = RuntimeStrategySelector().select(
        state,
        deps=RuntimeDependencies(capability_runtime=FailingCapabilityRuntime()),
    )

    assert selected.capability_plan.selection_validity == "blocked_capability_selection"
    assert selected.capability_plan.allowed_tools == []
    assert selected.capability_plan.blocked_capability_reasons == {
        "tool.web.search": "capability_runtime_unavailable:RuntimeError"
    }
