from __future__ import annotations

from zuno.agent.contracts import CapabilityPlan, RetrievalProfile
from zuno.agent.planning import PlanningRequest, build_default_strategy_selector
from zuno.agent.runtime.contracts import StrategyDecision, StrategyMode
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.state import AgentRuntimeState


class RuntimeStrategySelector:
    def select(self, state: AgentRuntimeState, deps: RuntimeDependencies) -> AgentRuntimeState:
        output = build_default_strategy_selector().select(
            PlanningRequest(
                task_id=state.task_id,
                trace_id=state.trace_id,
                workspace_id=state.workspace_id,
                user_goal=state.goal,
                requested_retrieval_profile=RetrievalProfile.STANDARD,
                context_pack=state.context_pack.model_dump(mode="json") if state.context_pack else {},
                pinned_capability_plan=_capability_plan(state=state, deps=deps),
                available_capability_ids=tuple(state.capability_plan.allowed_capabilities),
                user_roles=("analyst",),
                security_summary=dict(state.security_summary or {}),
                budget_verdict=state.budget_verdict,
            )
        )
        mode = StrategyMode(output.strategy.strategy)
        lowered_goal = state.goal.lower()
        if mode == StrategyMode.DIRECT_ANSWER and "plan" in lowered_goal and "execute" in lowered_goal:
            mode = StrategyMode.PLAN_EXECUTE
        memory_influenced_strategy = bool(
            state.context_pack
            and state.context_pack.task_state.get("memory_influenced_strategy")
        )
        if memory_influenced_strategy and mode == StrategyMode.DIRECT_ANSWER:
            mode = StrategyMode.PLAN_EXECUTE_WITH_REPLAN
        reason = output.strategy.reason
        if memory_influenced_strategy:
            reason = f"{reason}; memory_influenced_strategy"
        strategy = StrategyDecision(
            mode=mode,
            reason=reason,
            selected_skill_id=output.strategy.selected_skill,
            retrieval_profile=output.strategy.retrieval_profile.value if output.strategy.retrieval_profile else None,
            trace_event_ids=[
                *[event.event_id for event in output.trace_events],
                *(["memory:influenced_strategy"] if memory_influenced_strategy else []),
            ],
        )
        state.strategy = strategy
        state.plan_state = output.plan_state
        state.retrieval_plan = output.retrieval_plan
        state.capability_plan = output.capability_plan
        if state.context_pack is not None:
            task_state = dict(state.context_pack.task_state)
            task_state.update(
                {
                    "capability_availability_snapshot_ref": output.capability_plan.availability_snapshot_ref,
                    "capability_selection_result_ref": output.capability_plan.selection_result_ref,
                    "capability_selection_validity": output.capability_plan.selection_validity,
                }
            )
            if output.capability_plan.risk_summary.get("planner_exposure"):
                exposure = dict(output.capability_plan.risk_summary["planner_exposure"])
                task_state["capability_planner_exposure_ref"] = exposure.get("exposure_ref")
                task_state["capability_planner_exposure_visibility"] = exposure.get("visibility")
            state.context_pack = state.context_pack.model_copy(update={"task_state": task_state})
        state.trace_event_ids.extend(event.event_id for event in output.trace_events)
        return state


def _capability_plan(state: AgentRuntimeState, deps: RuntimeDependencies | None) -> CapabilityPlan | None:
    pinned = _pinned_capability_plan(state)
    if pinned is not None:
        return pinned
    if deps is None or deps.capability_runtime is None or not state.capability_plan.allowed_capabilities:
        return None
    try:
        selected = deps.capability_runtime.select(
            {
                "task_id": state.task_id,
                "trace_id": state.trace_id,
                "workspace_id": state.workspace_id,
                "user_id": state.user_id,
                "tenant_id": f"user:{state.user_id}",
                "user_goal": state.goal,
                "available_capability_ids": tuple(state.capability_plan.allowed_capabilities),
                "user_roles": ("analyst",),
            }
        )
    except Exception as exc:
        return CapabilityPlan(
            selection_validity="blocked_capability_selection",
            blocked_capability_reasons={
                capability_id: f"capability_runtime_unavailable:{type(exc).__name__}"
                for capability_id in state.capability_plan.allowed_capabilities
            },
            risk_summary={
                "blocked": True,
                "reason": "capability_runtime_unavailable",
                "failure_type": type(exc).__name__,
            },
        )
    if isinstance(selected, CapabilityPlan):
        return selected
    return CapabilityPlan.model_validate(selected)


def _pinned_capability_plan(state: AgentRuntimeState) -> CapabilityPlan | None:
    if state.context_pack is None:
        return None
    task_state = state.context_pack.task_state
    snapshot_ref = task_state.get("capability_availability_snapshot_ref")
    selection_ref = task_state.get("capability_selection_result_ref")
    selection_validity = task_state.get("capability_selection_validity")
    if not snapshot_ref or not selection_ref or selection_validity != "fixed_planning_snapshot":
        return None
    risk_summary = {}
    exposure_ref = task_state.get("capability_planner_exposure_ref")
    exposure_visibility = task_state.get("capability_planner_exposure_visibility")
    if exposure_ref or exposure_visibility:
        risk_summary["planner_exposure"] = {
            "exposure_ref": exposure_ref,
            "visibility": exposure_visibility,
        }
    return CapabilityPlan(
        availability_snapshot_ref=str(snapshot_ref),
        selection_result_ref=str(selection_ref),
        selection_validity="fixed_planning_snapshot",
        allowed_capabilities=list(state.capability_plan.allowed_capabilities),
        allowed_tools=list(state.capability_plan.allowed_tools),
        blocked_capability_reasons=dict(state.capability_plan.blocked_capability_reasons),
        approval_required_tools=list(state.capability_plan.approval_required_tools),
        executed_tools=[],
        risk_summary=risk_summary,
    )


__all__ = ["RuntimeStrategySelector"]
