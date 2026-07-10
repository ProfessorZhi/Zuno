from __future__ import annotations

from dataclasses import dataclass

from zuno.agent.contracts import PlanState, PlanStep
from zuno.agent.runtime.contracts import ReflectionDecision
from zuno.agent.runtime.state import AgentRuntimeState


@dataclass(frozen=True, slots=True)
class ReplanResult:
    plan_state: PlanState
    diff: dict


class ReplanEngine:
    def replan(self, state: AgentRuntimeState, decision: ReflectionDecision) -> ReplanResult:
        if state.plan_state is None:
            raise ValueError("cannot replan without plan_state")
        old_step_ids = [step.step_id for step in state.plan_state.steps]
        next_index = state.counters.replans + 1
        action_type = "retrieve_evidence" if decision in {ReflectionDecision.RETRIEVE_MORE, ReflectionDecision.REPLAN} else "model_transform"
        new_step = PlanStep(
            step_id=f"{state.run_id}:replan:{next_index}",
            goal=f"Correct trajectory after {decision.value}: {state.goal}",
            action_type=action_type,
            expected_output="new observation that resolves reflection failure",
            acceptance_criteria=["new observation produced", "trajectory changed"],
            required_evidence=["source_span"],
            retrieval_policy_ref="corrective_agentic_retrieval",
            model_role="executor",
            budget={
                "trajectory_changed": True,
                "failure_bucket": _failure_bucket(state),
                "max_retrieval_rounds": 1,
            },
            status="pending",
        )
        plan_state = state.plan_state.model_copy(
            update={
                "status": "replanned",
                "current_step_id": new_step.step_id,
                "steps": [*state.plan_state.steps, new_step],
            }
        )
        diff = {
            "old_step_ids": old_step_ids,
            "new_step_ids": [step.step_id for step in plan_state.steps],
            "added_step_id": new_step.step_id,
            "changed_fields": ["steps", "current_step_id", "retrieval_policy_ref", "budget"],
            "trajectory_changed": True,
        }
        return ReplanResult(plan_state=plan_state, diff=diff)


def _failure_bucket(state: AgentRuntimeState) -> str:
    latest = state.observations[-1] if state.observations else None
    if latest is not None and not latest.evidence_ids:
        return "doc_miss"
    return "doc_hit_text_miss"


__all__ = ["ReplanEngine", "ReplanResult"]
