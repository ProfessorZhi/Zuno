from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.state import AgentRuntimeState


@dataclass(frozen=True, slots=True)
class StepExecutionResult:
    step_id: str
    status: ObservationStatus
    observation: NormalizedObservation
    trace_event_ids: list[str] = field(default_factory=list)


class StepExecutor(Protocol):
    action_types: frozenset[str]

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult: ...


class StepExecutorRegistry:
    def __init__(self, executors: list[StepExecutor] | tuple[StepExecutor, ...]) -> None:
        self._executors = list(executors)

    def executor_for(self, action_type: str) -> StepExecutor:
        for executor in self._executors:
            if action_type in executor.action_types:
                return executor
        for executor in self._executors:
            if "*" in executor.action_types:
                return executor
        raise KeyError(f"no step executor for action type: {action_type}")

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        return self.executor_for(step.action_type).execute(state=state, step=step, deps=deps)


__all__ = ["StepExecutionResult", "StepExecutor", "StepExecutorRegistry"]
