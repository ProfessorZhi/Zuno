from __future__ import annotations

from zuno.agent.contracts import RetrievalProfile
from zuno.agent.planning import PlanningRequest, build_default_strategy_selector
from zuno.agent.runtime.contracts import StrategyDecision, StrategyMode
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.state import AgentRuntimeState


class RuntimeStrategySelector:
    def select(self, state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
        del deps
        output = build_default_strategy_selector().select(
            PlanningRequest(
                task_id=state.task_id,
                trace_id=state.trace_id,
                workspace_id=state.workspace_id,
                user_goal=state.goal,
                requested_retrieval_profile=RetrievalProfile.STANDARD,
                context_pack=state.context_pack.model_dump(mode="json") if state.context_pack else {},
                available_capability_ids=tuple(state.capability_plan.allowed_capabilities),
                user_roles=("analyst",),
            )
        )
        mode = StrategyMode(output.strategy.strategy)
        lowered_goal = state.goal.lower()
        if mode == StrategyMode.DIRECT_ANSWER and "plan" in lowered_goal and "execute" in lowered_goal:
            mode = StrategyMode.PLAN_EXECUTE
        strategy = StrategyDecision(
            mode=mode,
            reason=output.strategy.reason,
            selected_skill_id=output.strategy.selected_skill,
            retrieval_profile=output.strategy.retrieval_profile.value if output.strategy.retrieval_profile else None,
            trace_event_ids=[event.event_id for event in output.trace_events],
        )
        state.strategy = strategy
        state.plan_state = output.plan_state
        state.retrieval_plan = output.retrieval_plan
        state.capability_plan = output.capability_plan
        state.trace_event_ids.extend(event.event_id for event in output.trace_events)
        return state


__all__ = ["RuntimeStrategySelector"]
