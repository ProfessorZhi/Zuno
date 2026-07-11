from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime import RuntimeDependencyFactory
from zuno.agent.runtime.execution.model_step import ModelStepExecutor
from zuno.agent.runtime.execution.react_step import ReActStepExecutor
from zuno.agent.runtime.state import AgentRuntimeState


def _state() -> AgentRuntimeState:
    return AgentRuntimeState(
        run_id="run:real_execution",
        thread_id="thread:real_execution",
        workspace_id="workspace:real_execution",
        user_id="user:real_execution",
        task_id="task:real_execution",
        trace_id="trace:real_execution",
        goal="Produce a grounded answer.",
    )


def _step(action_type: str) -> PlanStep:
    return PlanStep(
        step_id=f"step:{action_type}",
        goal=f"Execute {action_type}",
        action_type=action_type,
        expected_output="one runtime observation",
        acceptance_criteria=["observation produced"],
    )


def test_model_step_executor_calls_model_gateway_and_records_metrics() -> None:
    result = ModelStepExecutor().execute(
        state=_state(),
        step=_step("draft_answer"),
        deps=RuntimeDependencyFactory().dependencies(),
    )

    assert result.observation.status == "completed"
    assert result.observation.metadata["model_gateway_call"] is True
    assert result.observation.metadata["model_output"]
    assert result.observation.metadata["model_metrics"]["provider_id"].startswith("local_mock_")
    assert result.observation.metadata["model_metrics"]["latency_ms"] >= 0
    assert result.observation.metadata["model_metrics"]["token_count"] > 0
    assert "trace_event" in result.observation.metadata


def test_react_step_executor_runs_single_step_through_runner() -> None:
    result = ReActStepExecutor().execute(
        state=_state(),
        step=_step("inspect_failure"),
        deps=RuntimeDependencyFactory().dependencies(),
    )

    assert result.observation.status == "completed"
    assert result.observation.metadata["react_step"] is True
    assert result.observation.metadata["action"] == "inspect_failure"
    assert result.observation.metadata["observation"]
    assert result.observation.metadata["model_metrics"]["provider_id"].startswith("local_mock_")
