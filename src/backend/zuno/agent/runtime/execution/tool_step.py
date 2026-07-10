from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.state import AgentRuntimeState


class ToolStepExecutor:
    action_types = frozenset({"select_capability", "observe_tool_result"})

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        del deps
        tool_id = (state.capability_plan.allowed_tools or ["tool.intent"])[0]
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.TOOL,
            status=ObservationStatus.COMPLETED,
            source="ToolStepExecutor",
            summary="tool call intent prepared; execution remains governed by Tool Control Plane",
            tool_id=tool_id,
            metadata={"tool_call_intent": True, "action_type": step.action_type},
        )
        return StepExecutionResult(step_id=step.step_id, status=ObservationStatus.COMPLETED, observation=observation)


__all__ = ["ToolStepExecutor"]
