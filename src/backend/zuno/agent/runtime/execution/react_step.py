from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.state import AgentRuntimeState


class ReActStepExecutor:
    action_types = frozenset({"*", "inspect_failure", "prepare_replan_if_evidence_low"})

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        del deps
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.SYSTEM,
            status=ObservationStatus.COMPLETED,
            source="ReActStepExecutor",
            summary=f"single ReAct step completed for {step.action_type}",
            metadata={"react_step": True, "action_type": step.action_type},
        )
        return StepExecutionResult(step_id=step.step_id, status=ObservationStatus.COMPLETED, observation=observation)


__all__ = ["ReActStepExecutor"]
