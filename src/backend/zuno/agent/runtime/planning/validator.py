from __future__ import annotations

from zuno.agent.contracts import PlanState


class PlanValidationError(ValueError):
    pass


class PlanValidator:
    def validate(self, plan_state: PlanState) -> None:
        seen: set[str] = set()
        for step in plan_state.steps:
            if step.step_id in seen:
                raise PlanValidationError(f"duplicate plan step: {step.step_id}")
            seen.add(step.step_id)
            if not step.acceptance_criteria:
                raise PlanValidationError(f"plan step has no acceptance criteria: {step.step_id}")
            if step.step_id in step.dependencies:
                raise PlanValidationError(f"plan step depends on itself: {step.step_id}")
        for step in plan_state.steps:
            missing = set(step.dependencies) - seen
            if missing:
                raise PlanValidationError(f"plan step has missing dependencies: {step.step_id}")
        self._reject_cycles(plan_state)

    def _reject_cycles(self, plan_state: PlanState) -> None:
        deps = {step.step_id: set(step.dependencies) for step in plan_state.steps}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(step_id: str) -> None:
            if step_id in visited:
                return
            if step_id in visiting:
                raise PlanValidationError("plan dependency cycle detected")
            visiting.add(step_id)
            for dep in deps.get(step_id, set()):
                visit(dep)
            visiting.remove(step_id)
            visited.add(step_id)

        for step_id in deps:
            visit(step_id)


__all__ = ["PlanValidationError", "PlanValidator"]
