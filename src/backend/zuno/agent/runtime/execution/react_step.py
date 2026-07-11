from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.execution.react_runner import ReActStepRunner
from zuno.agent.runtime.state import AgentRuntimeState


class ReActStepExecutor:
    action_types = frozenset({"*", "inspect_failure", "prepare_replan_if_evidence_low"})

    def __init__(self, runner: ReActStepRunner | None = None) -> None:
        self.runner = runner or ReActStepRunner()

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        run = self.runner.run(state=state, step=step, deps=deps)
        return StepExecutionResult(step_id=step.step_id, status=run.status, observation=run.observation)


__all__ = ["ReActStepExecutor"]
