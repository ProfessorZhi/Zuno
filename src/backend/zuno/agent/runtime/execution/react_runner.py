from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.platform.model_gateway import ModelCategory, ModelGatewayRequest
from zuno.platform.model_roles import ModelRole


@dataclass(frozen=True, slots=True)
class ReActStepRun:
    status: ObservationStatus
    observation: NormalizedObservation


class ReActStepRunner:
    def run(self, *, state: AgentRuntimeState, step: PlanStep, deps: RuntimeDependencies) -> ReActStepRun:
        if deps.model_gateway is None:
            observation = NormalizedObservation(
                observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
                step_id=step.step_id,
                kind=ObservationKind.SYSTEM,
                status=ObservationStatus.BLOCKED,
                source="ReActStepRunner",
                summary="model gateway dependency missing for ReAct step",
                failure_reason="missing_model_gateway",
                metadata={"blocked": True, "missing_dependency": "model_gateway", "react_step": True},
            )
            return ReActStepRun(status=ObservationStatus.BLOCKED, observation=observation)

        request = ModelGatewayRequest(
            category=ModelCategory.CHAT,
            role=ModelRole.EXECUTOR,
            prompt=_react_prompt(state=state, step=step),
            run_id=state.run_id,
            trace_id=state.trace_id,
            task_id=state.task_id,
            workspace_id=state.workspace_id,
            user_id=state.user_id,
            metadata={"runtime_node": "react_step", "step_id": step.step_id, "action_type": step.action_type},
        )
        result = deps.model_gateway.invoke(request)
        status = _status(result.status)
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.SYSTEM,
            status=status,
            source="ReActStepRunner",
            summary=_summary(result.output, status),
            failure_reason=None if status == ObservationStatus.COMPLETED else result.status,
            metadata={
                "react_step": True,
                "thought": f"execute current PlanStep only: {step.goal}",
                "action": step.action_type,
                "observation": result.output,
                "model_status": result.status,
                "model_metrics": result.metrics.to_dict(),
                "budget_verdict": result.budget_verdict.to_dict(),
                "trace_event": _trace_event(result.trace_event),
            },
        )
        return ReActStepRun(status=status, observation=observation)


def _react_prompt(*, state: AgentRuntimeState, step: PlanStep) -> str:
    return (
        "Run exactly one ReAct step for the current plan step.\n"
        f"Task goal: {state.goal}\n"
        f"Step goal: {step.goal}\n"
        f"Action type: {step.action_type}\n"
        f"Acceptance criteria: {', '.join(step.acceptance_criteria)}\n"
        "Return a concise observation, not the final answer."
    )


def _status(status: str) -> ObservationStatus:
    if status == "succeeded":
        return ObservationStatus.COMPLETED
    if status == "blocked":
        return ObservationStatus.BLOCKED
    return ObservationStatus.FAILED


def _summary(output: str, status: ObservationStatus) -> str:
    if status != ObservationStatus.COMPLETED:
        return f"react step {status.value}"
    return output.strip() or "react step completed"


def _trace_event(event: Any) -> dict[str, Any]:
    return dict(event) if isinstance(event, dict) else {}


__all__ = ["ReActStepRun", "ReActStepRunner"]
