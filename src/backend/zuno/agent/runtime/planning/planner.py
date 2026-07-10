from __future__ import annotations

from zuno.agent.contracts import PlanState, PlanStep
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.planning.validator import PlanValidator
from zuno.agent.runtime.state import AgentRuntimeState


class RuntimePlanner:
    def __init__(self, validator: PlanValidator | None = None) -> None:
        self.validator = validator or PlanValidator()

    def plan(self, state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
        del deps
        if state.plan_state is None:
            state.plan_state = PlanState(
                plan_id=f"plan:{state.run_id}",
                status="planned",
                steps=[
                    PlanStep(
                        step_id=f"{state.run_id}:step:1",
                        goal=state.goal,
                        action_type="model_transform",
                        expected_output="grounded answer draft",
                        acceptance_criteria=["step status completed"],
                        model_role="executor",
                        attempt=0,
                    )
                ],
            )
        steps = [
            step
            if step.acceptance_criteria
            else step.model_copy(update={"acceptance_criteria": ["step status completed"]})
            for step in state.plan_state.steps
        ]
        if steps and state.plan_state.current_step_id is None:
            state.plan_state = state.plan_state.model_copy(update={"steps": steps, "current_step_id": steps[0].step_id})
        else:
            state.plan_state = state.plan_state.model_copy(update={"steps": steps})
        self.validator.validate(state.plan_state)
        return state


__all__ = ["RuntimePlanner"]
