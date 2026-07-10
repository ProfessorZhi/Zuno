from __future__ import annotations

from zuno.agent.contracts import PlanState, PlanStep


class PlanExecutor:
    def next_ready_step(self, plan_state: PlanState) -> PlanStep | None:
        if plan_state.current_step_id:
            for step in plan_state.steps:
                if step.step_id == plan_state.current_step_id and step.status == "running":
                    return step
        completed = {step.step_id for step in plan_state.steps if step.status == "completed"}
        for step in plan_state.steps:
            if step.status != "pending":
                continue
            if set(step.dependencies) <= completed:
                return step
        return None

    def mark_running(self, plan_state: PlanState, step: PlanStep) -> PlanState:
        return self._replace_step(
            plan_state,
            step.model_copy(update={"status": "running", "attempt": step.attempt + 1}),
            current_step_id=step.step_id,
            status="running",
        )

    def mark_completed(self, plan_state: PlanState, step: PlanStep, *, observation_ref: str) -> PlanState:
        completed = step.model_copy(
            update={
                "status": "completed",
                "observation_refs": [*step.observation_refs, observation_ref],
            }
        )
        next_plan = self._replace_step(plan_state, completed, current_step_id=None, status="running")
        next_step = self.next_ready_step(next_plan)
        return next_plan.model_copy(
            update={
                "current_step_id": next_step.step_id if next_step else None,
                "status": "completed" if next_step is None else "running",
            }
        )

    def mark_failed(self, plan_state: PlanState, step: PlanStep, *, observation_ref: str) -> PlanState:
        failed = step.model_copy(
            update={
                "status": "failed",
                "observation_refs": [*step.observation_refs, observation_ref],
            }
        )
        return self._replace_step(plan_state, failed, current_step_id=step.step_id, status="failed")

    def _replace_step(
        self,
        plan_state: PlanState,
        step: PlanStep,
        *,
        current_step_id: str | None,
        status: str,
    ) -> PlanState:
        return plan_state.model_copy(
            update={
                "status": status,
                "current_step_id": current_step_id,
                "steps": [step if item.step_id == step.step_id else item for item in plan_state.steps],
            }
        )


__all__ = ["PlanExecutor"]
