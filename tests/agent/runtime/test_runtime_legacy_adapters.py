from __future__ import annotations

from zuno.agent.contracts import (
    EvidenceBundle,
    PlanState,
    PlanStep,
    PlannerOutput,
    ReflectionVerdict,
    RetrievalPlan,
    RetrievalProfile,
    StrategySelectorOutput,
)
from zuno.agent.control_runtime import RuntimeObservation
from zuno.agent.harness import ControllerRuntimeState
from zuno.agent.runtime.adapters import (
    normalized_observation_from_controller_payload,
    normalized_observation_from_runtime_observation,
    runtime_state_from_controller_state,
    runtime_state_from_planner_output,
)
from zuno.agent.runtime.contracts import ObservationKind, ObservationStatus, ReflectionDecision, StrategyMode


def test_runtime_observation_adapter_preserves_evidence_and_redacts_sensitive_metadata() -> None:
    legacy = RuntimeObservation(
        step_id="step-1",
        status="failed",
        evidence=EvidenceBundle(
            evidence_ids=["ev-1"],
            citation_ids=["cite-1"],
            evidence_count=1,
            citation_coverage=0.5,
        ),
        output="partial answer",
        failure_reason="citation_coverage_low",
        tool_id="tool.search",
        metadata={
            "retriever": "bm25",
            "api_key": "should-not-leak",
            "nested": {"raw": "large"},
        },
    )

    normalized = normalized_observation_from_runtime_observation(legacy)

    assert normalized.step_id == "step-1"
    assert normalized.kind == ObservationKind.TOOL
    assert normalized.status == ObservationStatus.FAILED
    assert normalized.evidence_ids == ["ev-1"]
    assert normalized.citation_ids == ["cite-1"]
    assert normalized.tool_id == "tool.search"
    assert normalized.failure_reason == "citation_coverage_low"
    assert normalized.payload_ref is not None
    serialized = normalized.model_dump_json()
    assert "should-not-leak" not in serialized
    assert "[redacted]" in serialized
    assert "<dict>" in serialized


def test_controller_state_adapter_preserves_identity_refs_and_observations() -> None:
    controller_state = ControllerRuntimeState(
        thread_id="thread-1",
        workspace_id="workspace-1",
        user_id="user-1",
        task_id="task-1",
        trace_id="trace-1",
        goal="summarize workspace evidence",
        context_pack={
            "context_pack_id": "ctx-1",
            "selected_memory_refs": ["mem-1"],
            "selected_evidence_refs": ["ev-1"],
            "allowed_capabilities": ["knowledge.search"],
        },
        current_step="observe",
        observations=({"node": "observe", "result": "observed"},),
        artifact_refs=("artifact:task-1:answer",),
        memory_candidates=("summary:task-1",),
        approval_interrupts=({"interrupt_id": "interrupt-1"},),
        checkpoints=("checkpoint-1",),
    )

    runtime_state = runtime_state_from_controller_state(controller_state)
    snapshot = runtime_state.to_snapshot()

    assert snapshot.thread_id == "thread-1"
    assert snapshot.workspace_id == "workspace-1"
    assert snapshot.current_node == "observe"
    assert snapshot.context_pack is not None
    assert snapshot.context_pack.selected_memory_refs == ["mem-1"]
    assert snapshot.context_pack.selected_evidence_refs == ["ev-1"]
    assert snapshot.observations[0].summary == "observed"
    assert snapshot.artifact_refs == ["artifact:task-1:answer"]
    assert snapshot.memory_candidate_refs == ["summary:task-1"]
    assert snapshot.interrupt_refs == ["interrupt-1"]
    assert snapshot.checkpoint_refs == ["checkpoint-1"]


def test_planner_output_adapter_preserves_strategy_plan_and_reflection_route() -> None:
    planner = PlannerOutput(
        task_id="task-1",
        trace_id="trace-1",
        strategy=StrategySelectorOutput(
            strategy="plan_execute_with_replan",
            reason="multi-hop evidence",
            selected_skill="research_report",
            retrieval_profile=RetrievalProfile.DEEP,
        ),
        retrieval_plan=RetrievalPlan(
            requested_profile=RetrievalProfile.DEEP,
            effective_profile=RetrievalProfile.DEEP,
            retrievers_used=["bm25", "vector", "graph_expand"],
        ),
        plan_state=PlanState(
            plan_id="plan-1",
            status="planned",
            steps=[
                PlanStep(
                    step_id="step-1",
                    goal="retrieve",
                    action_type="retrieve_evidence",
                    expected_output="evidence bundle",
                )
            ],
            current_step_id="step-1",
        ),
        reflection_verdict=ReflectionVerdict(decision="replan", reason="citation_coverage_low"),
    )

    runtime_state = runtime_state_from_planner_output(
        planner,
        thread_id="thread-1",
        workspace_id="workspace-1",
        user_id="user-1",
        goal="answer",
    )
    snapshot = runtime_state.to_snapshot()

    assert snapshot.strategy is not None
    assert snapshot.strategy.mode == StrategyMode.PLAN_EXECUTE_WITH_REPLAN
    assert snapshot.plan_state is not None
    assert snapshot.plan_state.steps[0].expected_output == "evidence bundle"
    assert snapshot.retrieval_plan is not None
    assert snapshot.retrieval_plan.retrievers_used == ["bm25", "vector", "graph_expand"]
    assert snapshot.reflection_decision == ReflectionDecision.REPLAN


def test_controller_payload_adapter_does_not_store_raw_sensitive_payload() -> None:
    observation = normalized_observation_from_controller_payload(
        {
            "node": "tool_call",
            "result": "ok",
            "password": "plain-password",
            "credential_ref": "cred:workspace:mail",
        }
    )

    serialized = observation.model_dump_json()

    assert observation.kind == ObservationKind.TOOL
    assert observation.payload_ref is not None
    assert "plain-password" not in serialized
    assert "[redacted]" in serialized
