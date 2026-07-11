from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.platform.model_gateway import ModelCategory, ModelGatewayRequest
from zuno.platform.model_roles import ModelRole


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
        role = _model_role(step)
        result = deps.model_gateway.invoke(
            ModelGatewayRequest(
                category=ModelCategory.CHAT,
                role=role,
                prompt=_prompt_for_step(state=state, step=step),
                run_id=state.run_id,
                trace_id=state.trace_id,
                task_id=state.task_id,
                workspace_id=state.workspace_id,
                user_id=state.user_id,
                metadata={"runtime_node": "model_step", "step_id": step.step_id, "action_type": step.action_type},
            )
        )
        status = _status(result.status)
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.MODEL,
            status=status,
            source="ModelStepExecutor",
            summary=_summary(result.output, status),
            failure_reason=None if status == ObservationStatus.COMPLETED else result.status,
            metadata={
                "model_gateway_call": True,
                "model_output": result.output,
                "model_role": role.value,
                "action_type": step.action_type,
                "model_status": result.status,
                "model_metrics": result.metrics.to_dict(),
                "budget_verdict": result.budget_verdict.to_dict(),
                "trace_event": dict(result.trace_event),
            },
        )
        return StepExecutionResult(step_id=step.step_id, status=status, observation=observation)


def _model_role(step: PlanStep) -> ModelRole:
    if step.model_role:
        return ModelRole(step.model_role)
    if step.action_type in {"reflect_before_final", "run_verification"}:
        return ModelRole.CRITIC
    if step.action_type in {"draft_answer", "draft_report", "answer_from_context", "answer_with_evidence"}:
        return ModelRole.SYNTHESIS
    return ModelRole.EXECUTOR


def _prompt_for_step(*, state: AgentRuntimeState, step: PlanStep) -> str:
    return (
        f"Task goal: {state.goal}\n"
        f"Current PlanStep: {step.goal}\n"
        f"Action type: {step.action_type}\n"
        f"Expected output: {step.expected_output}\n"
        f"Acceptance criteria: {', '.join(step.acceptance_criteria)}\n"
        "Return only the observation needed by this PlanStep."
    )


def _status(status: str) -> ObservationStatus:
    if status == "succeeded":
        return ObservationStatus.COMPLETED
    if status == "blocked":
        return ObservationStatus.BLOCKED
    return ObservationStatus.FAILED


def _summary(output: str, status: ObservationStatus) -> str:
    if status != ObservationStatus.COMPLETED:
        return f"model step {status.value}"
    return output.strip() or "model step completed"


__all__ = ["ModelStepExecutor"]
