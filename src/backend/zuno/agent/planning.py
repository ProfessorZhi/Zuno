from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import Any

from zuno.agent.contracts import (
    CapabilityPlan,
    PlanState,
    PlanStep,
    PlannerOutput,
    ReflectionVerdict,
    ReflexionLesson,
    ReplanDecision,
    RetrievalPlan,
    RetrievalProfile,
    SelectedSkill,
    StrategySelectorOutput,
    TraceRecord,
)
from zuno.capability.layer import (
    CapabilityLayerRegistry,
    CapabilityRouteRequest,
    CapabilityRouter,
    build_default_capability_layer_registry,
)


@dataclass(frozen=True, slots=True)
class PlanningRequest:
    task_id: str
    trace_id: str
    workspace_id: str
    user_goal: str
    requested_retrieval_profile: RetrievalProfile = RetrievalProfile.STANDARD
    context_pack: dict[str, Any] = field(default_factory=dict)
    pinned_skill_id: str | None = None
    available_capability_ids: tuple[str, ...] = ()
    user_roles: tuple[str, ...] = ()
    security_summary: dict[str, Any] = field(default_factory=dict)
    budget_verdict: Any | None = None
    graph_available: bool = True


class StrategySelector:
    def __init__(self, registry: CapabilityLayerRegistry | None = None) -> None:
        self._registry = registry or build_default_capability_layer_registry()
        self._capability_router = CapabilityRouter(self._registry)

    def select(self, request: PlanningRequest) -> PlannerOutput:
        selected_skill = self._select_skill(request)
        retrieval_plan = self._build_retrieval_plan(request, selected_skill)
        capability_plan = self._build_capability_plan(request)
        security_blocked = _is_security_blocked(request.security_summary)
        budget_blocked = _is_budget_blocked(request.budget_verdict)

        strategy = self._select_strategy(
            request=request,
            selected_skill=selected_skill,
            security_blocked=security_blocked,
            budget_blocked=budget_blocked,
        )
        plan_state = self._build_plan_state(
            request=request,
            strategy=strategy.strategy,
            selected_skill=selected_skill,
            capability_plan=capability_plan,
            security_blocked=security_blocked,
            budget_blocked=budget_blocked,
        )
        reflection_verdict = self._build_reflection_verdict(
            request=request,
            security_blocked=security_blocked,
            budget_blocked=budget_blocked,
        )
        replan_decision = self._build_replan_decision(plan_state, strategy.strategy)
        reflexion_lesson = self._build_reflexion_lesson(request, strategy.strategy)
        trace_events = self._build_trace_events(
            request=request,
            strategy=strategy,
            selected_skill=selected_skill,
            retrieval_plan=retrieval_plan,
            capability_plan=capability_plan,
            security_blocked=security_blocked,
        )

        return PlannerOutput(
            task_id=request.task_id,
            trace_id=request.trace_id,
            strategy=strategy,
            selected_skill=selected_skill,
            capability_plan=capability_plan,
            retrieval_plan=retrieval_plan,
            plan_state=plan_state,
            reflection_verdict=reflection_verdict,
            replan_decision=replan_decision,
            reflexion_lesson=reflexion_lesson,
            trace_events=trace_events,
        )

    def _select_skill(self, request: PlanningRequest) -> SelectedSkill:
        skill_id = request.pinned_skill_id or _automatic_skill_id(request.user_goal)
        skill = self._registry.require_skill(skill_id)
        return SelectedSkill(
            skill_id=skill.skill_id,
            skill_version=skill.skill_version,
            selection_mode="pinned" if request.pinned_skill_id else "automatic",
            reason="pinned_by_request" if request.pinned_skill_id else "matched_goal_terms",
            allowed_tools=list(skill.allowed_tools),
            required_evidence=list(skill.required_evidence),
            retrieval_profile=skill.recommended_retrieval_profile,
        )

    def _build_retrieval_plan(
        self,
        request: PlanningRequest,
        selected_skill: SelectedSkill,
    ) -> RetrievalPlan:
        requested = _stronger_profile(
            request.requested_retrieval_profile,
            selected_skill.retrieval_profile,
        )
        effective = requested
        fallback_reason = None
        if requested == RetrievalProfile.DEEP and not request.graph_available:
            effective = RetrievalProfile.DEEP_WITHOUT_GRAPH
            fallback_reason = "graph_index_missing"

        if effective == RetrievalProfile.STANDARD:
            retrievers = ["bm25", "vector", "light_fusion"]
        elif effective == RetrievalProfile.DEEP_WITHOUT_GRAPH:
            retrievers = ["bm25", "vector", "staged_requery", "deep_without_graph_fallback"]
        else:
            retrievers = ["bm25", "vector", "staged_requery", "graph_expand"]

        return RetrievalPlan(
            requested_profile=requested,
            effective_profile=effective,
            retrievers_used=retrievers,
            fallback_reason=fallback_reason,
            evidence_requirements=list(selected_skill.required_evidence),
        )

    def _build_capability_plan(self, request: PlanningRequest) -> CapabilityPlan:
        if not request.available_capability_ids:
            return CapabilityPlan()
        route = self._capability_router.route(
            CapabilityRouteRequest(
                task_id=request.task_id,
                workspace_id=request.workspace_id,
                task_goal=request.user_goal,
                requested_capability_ids=request.available_capability_ids,
                pinned_skill_id=request.pinned_skill_id,
                user_roles=request.user_roles,
            )
        )
        approval_required = []
        for capability_id in route.allowed_capability_ids:
            capability = self._registry.require_capability(capability_id)
            if capability.policy.approval_required:
                approval_required.append(capability_id)
        return CapabilityPlan(
            allowed_capabilities=list(route.allowed_capability_ids),
            allowed_tools=list(route.allowed_tool_ids),
            blocked_capability_reasons=dict(route.blocked_capability_reasons),
            approval_required_tools=approval_required,
            executed_tools=[],
            risk_summary={
                "blocked_count": len(route.blocked_capability_reasons),
                "approval_required_count": len(approval_required),
            },
        )

    def _select_strategy(
        self,
        *,
        request: PlanningRequest,
        selected_skill: SelectedSkill,
        security_blocked: bool,
        budget_blocked: bool,
    ) -> StrategySelectorOutput:
        if security_blocked:
            return StrategySelectorOutput(
                strategy="direct_answer",
                reason="security_blocked",
                selected_skill=selected_skill.skill_id,
                retrieval_profile=request.requested_retrieval_profile,
            )
        if budget_blocked:
            return StrategySelectorOutput(
                strategy="direct_answer",
                reason="budget_guard_blocked",
                selected_skill=selected_skill.skill_id,
                retrieval_profile=request.requested_retrieval_profile,
            )

        goal = request.user_goal.lower()
        if any(term in goal for term in ("pytest", "test", "bug", "fix failing", "code")):
            strategy = "reflexion_enabled"
            reason = "code_or_test_feedback_task"
        elif any(term in goal for term in ("search the web", "web", "browser", "send", "email", "tool")) or any(
            capability_id.startswith("tool.") for capability_id in request.available_capability_ids
        ):
            strategy = "react"
            reason = "tool_or_observation_required"
        elif any(term in goal for term in ("formal", "report", "research report", "citations")):
            strategy = "reflection_enabled"
            reason = "formal_report_requires_reflection"
        elif any(term in goal for term in ("compare", "across", "conflict", "multi-hop", "multihop", "analyze", "synthesize")):
            strategy = "plan_execute_with_replan"
            reason = "multi_hop_evidence_needed"
        else:
            strategy = "direct_answer"
            reason = "lookup_or_low_complexity_goal"

        return StrategySelectorOutput(
            strategy=strategy,
            reason=reason,
            selected_skill=selected_skill.skill_id,
            retrieval_profile=request.requested_retrieval_profile,
        )

    def _build_plan_state(
        self,
        *,
        request: PlanningRequest,
        strategy: str,
        selected_skill: SelectedSkill,
        capability_plan: CapabilityPlan,
        security_blocked: bool,
        budget_blocked: bool,
    ) -> PlanState:
        if security_blocked or budget_blocked:
            return PlanState(
                plan_id=_stable_id("plan", request.task_id, request.trace_id),
                status="blocked",
                steps=[],
                current_step_id=None,
            )

        step_specs = {
            "direct_answer": [
                ("answer_from_context", "Answer from current context and light retrieval evidence."),
            ],
            "react": [
                ("select_capability", "Select an allowed capability without executing it."),
                ("observe_tool_result", "Wait for governed observation from tool or retrieval."),
                ("answer_with_evidence", "Answer only from observed evidence."),
            ],
            "plan_execute": [
                ("retrieve_evidence", "Collect required evidence."),
                ("draft_answer", "Draft cited answer or artifact."),
            ],
            "plan_execute_with_replan": [
                ("retrieve_evidence", "Collect multi-hop evidence."),
                ("compare_evidence", "Compare evidence across sources."),
                ("prepare_replan_if_evidence_low", "Prepare replan when retrieval is empty or citation coverage is low."),
                ("answer_with_citations", "Produce cited answer."),
            ],
            "reflection_enabled": [
                ("retrieve_evidence", "Collect report evidence."),
                ("draft_report", "Draft report with citations."),
                ("reflect_before_final", "Run reflection before final answer."),
            ],
            "reflexion_enabled": [
                ("inspect_failure", "Inspect failing code or test feedback."),
                ("apply_candidate_fix", "Prepare a candidate fix."),
                ("run_verification", "Run verification before completion."),
                ("create_reflexion_candidate", "Create Reflexion lesson candidate for review."),
            ],
        }.get(strategy, [])

        steps = [
            PlanStep(
                step_id=f"step_{index + 1}",
                goal=goal,
                action_type=action_type,
                required_evidence=list(selected_skill.required_evidence),
                allowed_capabilities=list(capability_plan.allowed_capabilities),
                failure_conditions=_failure_conditions_for_step(action_type),
                budget={"max_steps": len(step_specs)},
            )
            for index, (action_type, goal) in enumerate(step_specs)
        ]
        return PlanState(
            plan_id=_stable_id("plan", request.task_id, request.trace_id),
            status="planned",
            steps=steps,
            current_step_id=steps[0].step_id if steps else None,
        )

    def _build_reflection_verdict(
        self,
        *,
        request: PlanningRequest,
        security_blocked: bool,
        budget_blocked: bool,
    ) -> ReflectionVerdict:
        if security_blocked:
            action = str(request.security_summary.get("recommended_action") or "refuse")
            decision = "ask_user" if action == "ask_user" else "refuse"
            return ReflectionVerdict(
                decision=decision,
                security_blocked=True,
                reason="security_policy_blocked",
            )
        if budget_blocked:
            return ReflectionVerdict(
                decision="ask_user",
                security_blocked=False,
                reason="budget_guard_blocked",
            )
        return ReflectionVerdict(
            decision="continue",
            evidence_enough=False,
            reason="planning_ready",
        )

    def _build_replan_decision(self, plan_state: PlanState, strategy: str) -> ReplanDecision | None:
        if strategy != "plan_execute_with_replan":
            return None
        return ReplanDecision(
            trigger="retrieval_empty_or_citation_coverage_low",
            replaced_step_ids=[],
            new_steps=[
                step
                for step in plan_state.steps
                if "citation_coverage_low" in step.failure_conditions
            ],
            reason="planner_prepares_replan_boundary_for_phase10",
        )

    def _build_reflexion_lesson(
        self,
        request: PlanningRequest,
        strategy: str,
    ) -> ReflexionLesson | None:
        if strategy != "reflexion_enabled":
            return None
        return ReflexionLesson(
            lesson_id=_stable_id("reflexion", request.task_id, request.trace_id),
            task_type="code_test_debug",
            failure_type="verification_feedback",
            root_cause="unknown_until_phase10_execution",
            lesson="Create a reviewed Reflexion candidate after verification feedback.",
            recommended_fix="Inspect failure, apply minimal fix, rerun focused verification.",
            trigger_condition="code_or_test_task_with_verification_feedback",
            evidence_refs=[],
        )

    def _build_trace_events(
        self,
        *,
        request: PlanningRequest,
        strategy: StrategySelectorOutput,
        selected_skill: SelectedSkill,
        retrieval_plan: RetrievalPlan,
        capability_plan: CapabilityPlan,
        security_blocked: bool,
    ) -> list[TraceRecord]:
        budget_payload = _budget_payload(request.budget_verdict)
        return [
            TraceRecord(
                event_id=_stable_id("evt_strategy", request.task_id, request.trace_id),
                task_id=request.task_id,
                trace_id=request.trace_id,
                event_type="strategy_selected",
                payload={
                    "strategy": strategy.strategy,
                    "reason": strategy.reason,
                    "retrieval_profile": strategy.retrieval_profile.value if strategy.retrieval_profile else None,
                    "security_blocked": security_blocked,
                    "budget_verdict": budget_payload,
                },
            ),
            TraceRecord(
                event_id=_stable_id("evt_skill", request.task_id, selected_skill.skill_id),
                task_id=request.task_id,
                trace_id=request.trace_id,
                event_type="skill_selected",
                payload=selected_skill.model_dump(mode="json"),
            ),
            TraceRecord(
                event_id=_stable_id("evt_plan", request.task_id, request.trace_id),
                task_id=request.task_id,
                trace_id=request.trace_id,
                event_type="plan_created",
                payload={
                    "effective_profile": retrieval_plan.effective_profile.value,
                    "fallback_reason": retrieval_plan.fallback_reason,
                    "allowed_capabilities": list(capability_plan.allowed_capabilities),
                    "allowed_tools": list(capability_plan.allowed_tools),
                    "executed_tools": list(capability_plan.executed_tools),
                },
            ),
        ]


def build_default_strategy_selector() -> StrategySelector:
    return StrategySelector()


def _automatic_skill_id(goal: str) -> str:
    text = goal.lower()
    if any(term in text for term in ("contract", "clause", "renewal", "termination", "agreement")):
        return "contract_review"
    return "research_report"


def _stronger_profile(
    requested: RetrievalProfile,
    skill_profile: RetrievalProfile,
) -> RetrievalProfile:
    # Product selection is standard/deep per knowledge space; skills can recommend,
    # but the selector must not silently upgrade a standard user profile.
    return requested


def _is_security_blocked(summary: dict[str, Any]) -> bool:
    decision = str(summary.get("decision") or "").lower()
    recommended = str(summary.get("recommended_action") or "").lower()
    return decision in {"block", "blocked", "deny", "refuse"} or recommended in {"refuse", "ask_user"}


def _is_budget_blocked(verdict: Any | None) -> bool:
    if verdict is None:
        return False
    if isinstance(verdict, dict):
        return verdict.get("allowed") is False
    return getattr(verdict, "allowed", True) is False


def _budget_payload(verdict: Any | None) -> dict[str, Any]:
    if verdict is None:
        return {"allowed": True, "reason": "not_provided"}
    if isinstance(verdict, dict):
        return dict(verdict)
    if hasattr(verdict, "to_dict"):
        return verdict.to_dict()
    return {
        "allowed": getattr(verdict, "allowed", True),
        "reason": getattr(verdict, "reason", "unknown"),
    }


def _failure_conditions_for_step(action_type: str) -> list[str]:
    if action_type == "prepare_replan_if_evidence_low":
        return ["retrieval_empty", "citation_coverage_low"]
    if action_type == "reflect_before_final":
        return ["unsupported_claims", "citation_coverage_low", "security_blocked"]
    if action_type == "run_verification":
        return ["test_failed", "verification_missing"]
    return []


def _stable_id(prefix: str, *parts: str) -> str:
    source = "|".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(source.encode('utf-8')).hexdigest()[:12]}"


__all__ = [
    "PlanningRequest",
    "StrategySelector",
    "build_default_strategy_selector",
]
