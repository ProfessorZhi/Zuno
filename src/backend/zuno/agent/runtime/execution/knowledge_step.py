from __future__ import annotations

from zuno.agent.contracts import PlanStep
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.state import AgentRuntimeState


class KnowledgeStepExecutor:
    action_types = frozenset({"retrieve_evidence", "compare_evidence", "answer_with_citations"})

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
            kind=ObservationKind.RETRIEVAL,
            status=ObservationStatus.COMPLETED,
            source="KnowledgeStepExecutor",
            summary=f"retrieval request prepared for {step.action_type}",
            evidence_ids=[f"evidence:{state.run_id}:{step.step_id}"],
            citation_ids=[f"citation:{state.run_id}:{step.step_id}"],
            metadata={"retrieval_request": True, "action_type": step.action_type},
        )
        return StepExecutionResult(step_id=step.step_id, status=ObservationStatus.COMPLETED, observation=observation)


__all__ = ["KnowledgeStepExecutor"]
