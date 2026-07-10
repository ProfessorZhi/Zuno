from __future__ import annotations

import pytest

from zuno.agent.contracts import PlanState, PlanStep
from zuno.agent.runtime import RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.agent.runtime.planning import PlanExecutor, PlanValidationError, PlanValidator


def _request(task_id: str, goal: str) -> RuntimeStartRequest:
    return RuntimeStartRequest(
        run_id=f"run:{task_id}",
        thread_id="thread_plan",
        workspace_id="workspace_plan",
        user_id="user_plan",
        task_id=task_id,
        trace_id=f"trace:{task_id}",
        goal=goal,
    )


def test_unified_runtime_executes_multiple_plan_steps_before_reflection(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))

    snapshot = service.start(
        _request(
            "task_multistep",
            "Compare evidence across documents and synthesize conflicts with citations.",
        )
    )

    assert snapshot.finalization_status == "finalized"
    assert snapshot.plan_state is not None
    assert snapshot.plan_state.status == "completed"
    assert len(snapshot.plan_state.steps) >= 2
    assert all(step.status == "completed" for step in snapshot.plan_state.steps)
    assert snapshot.counters.steps_executed >= 2
    assert len(snapshot.observations) >= 2
    assert all(step.observation_refs for step in snapshot.plan_state.steps)


def test_plan_validator_rejects_invalid_dag_and_missing_acceptance() -> None:
    validator = PlanValidator()

    with pytest.raises(PlanValidationError, match="no acceptance"):
        validator.validate(
            PlanState(
                plan_id="plan_invalid",
                steps=[
                    PlanStep(
                        step_id="step_1",
                        goal="missing acceptance",
                        action_type="model_transform",
                    )
                ],
            )
        )

    with pytest.raises(PlanValidationError, match="cycle"):
        validator.validate(
            PlanState(
                plan_id="plan_cycle",
                steps=[
                    PlanStep(
                        step_id="step_1",
                        goal="a",
                        action_type="model_transform",
                        dependencies=["step_2"],
                        acceptance_criteria=["done"],
                    ),
                    PlanStep(
                        step_id="step_2",
                        goal="b",
                        action_type="model_transform",
                        dependencies=["step_1"],
                        acceptance_criteria=["done"],
                    ),
                ],
            )
        )


def test_plan_executor_marks_attempt_status_and_observation_refs() -> None:
    plan = PlanState(
        plan_id="plan_executor",
        steps=[
            PlanStep(
                step_id="step_1",
                goal="retrieve",
                action_type="retrieve_evidence",
                acceptance_criteria=["done"],
            ),
            PlanStep(
                step_id="step_2",
                goal="draft",
                action_type="draft_answer",
                dependencies=["step_1"],
                acceptance_criteria=["done"],
            ),
        ],
    )
    executor = PlanExecutor()

    first = executor.next_ready_step(plan)
    assert first.step_id == "step_1"
    running = executor.mark_running(plan, first)
    assert running.steps[0].status == "running"
    assert running.steps[0].attempt == 1
    completed = executor.mark_completed(running, running.steps[0], observation_ref="obs_1")

    assert completed.steps[0].status == "completed"
    assert completed.steps[0].observation_refs == ["obs_1"]
    assert completed.current_step_id == "step_2"
    assert executor.next_ready_step(completed).step_id == "step_2"


def test_step_budget_limit_forces_finalize_without_fake_completion(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))
    request = _request("task_budget", "Compare evidence across documents and synthesize conflicts.")
    snapshot = service.start(request)

    assert snapshot.counters.steps_executed <= snapshot.limits.max_steps
    assert not any(step.status == "completed" and not step.observation_refs for step in snapshot.plan_state.steps)
