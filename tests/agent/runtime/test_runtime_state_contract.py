from __future__ import annotations

import pytest

from zuno.agent.contracts import CapabilityPlan, PlanState, PlanStep
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
