from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.state import AgentRuntimeState


class ModelStepExecutor:
    action_types = frozenset({"model_transform", "draft_answer", "draft_report", "reflect_before_final", "answer_from_context", "answer_with_evidence", "apply_candidate_fix", "run_verification", "create_reflexion_candidate"})

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        if deps.model_gateway is None:
            observation = NormalizedObservation(
                observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
                step_id=step.step_id,
                kind=ObservationKind.MODEL,
                status=ObservationStatus.BLOCKED,
                source="ModelStepExecutor",
                summary="model gateway dependency missing",
                failure_reason="missing_model_gateway",
                metadata={
                    "blocked": True,
                    "missing_dependency": "model_gateway",
                    "action_type": step.action_type,
                    "model_role": step.model_role or "executor",
                },
            )
            return StepExecutionResult(step_id=step.step_id, status=ObservationStatus.BLOCKED, observation=observation)
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.MODEL,
            status=ObservationStatus.COMPLETED,
            source="ModelStepExecutor",
            summary=f"model role {step.model_role or 'executor'} selected for {step.action_type}",
            metadata={"model_role": step.model_role or "executor", "action_type": step.action_type},
        )
        return StepExecutionResult(step_id=step.step_id, status=ObservationStatus.COMPLETED, observation=observation)


__all__ = ["ModelStepExecutor"]
