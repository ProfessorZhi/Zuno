from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import TYPE_CHECKING, Any, Literal

from zuno.agent.contracts import (
    CapabilityPlan,
    EvidenceBundle,
    PlannerOutput,
    PlanState,
    PlanStep,
    ReflectionVerdict,
    ReflexionLesson,
    ReplanDecision,
    TraceRecord,
)
if TYPE_CHECKING:
    from zuno.memory.contracts import MemoryCandidate, MemoryScope
    from zuno.memory.engine import MemoryEngine
    from zuno.memory.policy import RetentionPolicy


@dataclass(frozen=True, slots=True)
class RuntimeObservation:
    step_id: str
    status: Literal["completed", "failed", "blocked"] = "completed"
    evidence: EvidenceBundle = field(default_factory=EvidenceBundle)
    output: str = ""
    failure_reason: str | None = None
    tool_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentRuntimeResult:
    task_id: str
    trace_id: str
    plan_state: PlanState
    capability_plan: CapabilityPlan
    reflection_verdict: ReflectionVerdict
    replan_decision: ReplanDecision | None
    reflexion_lesson: ReflexionLesson | None
    trace_events: list[TraceRecord]
    finalized: bool = False
    final_answer: str | None = None
    memory_candidate: MemoryCandidate | None = None


class AgentControlRuntime:
    def __init__(
        self,
        *,
        memory_engine: MemoryEngine | None = None,
        required_citation_coverage: float = 0.8,
    ) -> None:
        self._memory_engine = memory_engine
        self._required_citation_coverage = required_citation_coverage

    def run(
        self,
        planner_output: PlannerOutput,
        *,
        observations: list[RuntimeObservation] | tuple[RuntimeObservation, ...] = (),
        memory_scope: MemoryScope | None = None,
        retention_policy: RetentionPolicy | None = None,
    ) -> AgentRuntimeResult:
        trace_events = list(planner_output.trace_events)
        capability_plan = _capability_plan_with_executed_tools(
            planner_output.capability_plan,
            observations,
        )

        if _blocked_before_execution(planner_output):
            verdict = planner_output.reflection_verdict
            trace_events.append(
                _trace_event(
                    planner_output,
                    "reflection_completed",
                    {
                        "decision": verdict.decision,
                        "reason": verdict.reason,
                        "executed_step_count": 0,
                    },
                    ordinal=len(trace_events),
                )
            )
            return AgentRuntimeResult(
                task_id=planner_output.task_id,
                trace_id=planner_output.trace_id,
                plan_state=planner_output.plan_state,
                capability_plan=capability_plan,
                reflection_verdict=verdict,
                replan_decision=None,
                reflexion_lesson=None,
                trace_events=trace_events,
            )

        for observation in observations:
            trace_events.append(
                _trace_event(
                    planner_output,
                    "step_completed",
                    {
                        "step_id": observation.step_id,
                        "status": observation.status,
                        "tool_id": observation.tool_id,
                        "failure_reason": observation.failure_reason,
                        "evidence_count": observation.evidence.evidence_count,
                        "citation_coverage": observation.evidence.citation_coverage,
                    },
                    ordinal=len(trace_events),
                )
            )
            if observation.status in {"failed", "blocked"}:
                return self._handle_failed_observation(
                    planner_output=planner_output,
                    observation=observation,
                    capability_plan=capability_plan,
                    trace_events=trace_events,
                    memory_scope=memory_scope,
                    retention_policy=retention_policy,
                )

        if not observations:
            verdict = planner_output.reflection_verdict
            trace_events.append(
                _trace_event(
                    planner_output,
                    "reflection_completed",
                    {"decision": verdict.decision, "reason": verdict.reason},
                    ordinal=len(trace_events),
                )
            )
            return AgentRuntimeResult(
                task_id=planner_output.task_id,
                trace_id=planner_output.trace_id,
                plan_state=planner_output.plan_state,
                capability_plan=capability_plan,
                reflection_verdict=verdict,
                replan_decision=planner_output.replan_decision,
                reflexion_lesson=planner_output.reflexion_lesson,
                trace_events=trace_events,
            )

        reflected_observation = _observation_for_reflection(observations)
        trigger = _replan_trigger(reflected_observation.evidence, self._required_citation_coverage)
        if trigger:
            return _replanned_result(
                planner_output=planner_output,
                trigger=trigger,
                observation=reflected_observation,
                capability_plan=capability_plan,
                trace_events=trace_events,
                citation_threshold=self._required_citation_coverage,
            )

        verdict = ReflectionVerdict(
            decision="finish",
            evidence_enough=True,
            citation_coverage=reflected_observation.evidence.citation_coverage,
            reason="evidence_passed_reflection",
        )
        trace_events.append(
            _trace_event(
                planner_output,
                "reflection_completed",
                {
                    "decision": verdict.decision,
                    "evidence_enough": verdict.evidence_enough,
                    "citation_coverage": verdict.citation_coverage,
                },
                ordinal=len(trace_events),
            )
        )
        final_answer = _last_non_empty_output(observations)
        trace_events.append(
            _trace_event(
                planner_output,
                "answer_finalized",
                {
                    "answer_present": bool(final_answer),
                    "citation_coverage": verdict.citation_coverage,
                },
                ordinal=len(trace_events),
            )
        )
        return AgentRuntimeResult(
            task_id=planner_output.task_id,
            trace_id=planner_output.trace_id,
            plan_state=planner_output.plan_state,
            capability_plan=capability_plan,
            reflection_verdict=verdict,
            replan_decision=None,
            reflexion_lesson=None,
            trace_events=trace_events,
            finalized=True,
            final_answer=final_answer,
        )

    def _handle_failed_observation(
        self,
        *,
        planner_output: PlannerOutput,
        observation: RuntimeObservation,
        capability_plan: CapabilityPlan,
        trace_events: list[TraceRecord],
        memory_scope: MemoryScope | None,
        retention_policy: RetentionPolicy | None,
    ) -> AgentRuntimeResult:
        failure_reason = observation.failure_reason or observation.status
        if failure_reason == "security_blocked":
            verdict = ReflectionVerdict(
                decision="refuse",
                security_blocked=True,
                reason="security_blocked_during_runtime",
            )
            trace_events.append(
                _trace_event(
                    planner_output,
                    "reflection_completed",
                    {"decision": verdict.decision, "reason": verdict.reason},
                    ordinal=len(trace_events),
                )
            )
            return AgentRuntimeResult(
                task_id=planner_output.task_id,
                trace_id=planner_output.trace_id,
                plan_state=PlanState(
                    plan_id=planner_output.plan_state.plan_id,
                    status="blocked",
                    steps=[],
                    current_step_id=None,
                ),
                capability_plan=capability_plan,
                reflection_verdict=verdict,
                replan_decision=None,
                reflexion_lesson=None,
                trace_events=trace_events,
            )

        if planner_output.strategy.strategy == "reflexion_enabled" or failure_reason == "test_failed":
            return self._create_reflexion_result(
                planner_output=planner_output,
                observation=observation,
                capability_plan=capability_plan,
                trace_events=trace_events,
                memory_scope=memory_scope,
                retention_policy=retention_policy,
                failure_reason=failure_reason,
            )

        return _replanned_result(
            planner_output=planner_output,
            trigger=failure_reason,
            observation=observation,
            capability_plan=capability_plan,
            trace_events=trace_events,
            citation_threshold=self._required_citation_coverage,
        )

    def _create_reflexion_result(
        self,
        *,
        planner_output: PlannerOutput,
        observation: RuntimeObservation,
        capability_plan: CapabilityPlan,
        trace_events: list[TraceRecord],
        memory_scope: MemoryScope | None,
        retention_policy: RetentionPolicy | None,
        failure_reason: str,
    ) -> AgentRuntimeResult:
        evidence_refs = _evidence_refs(observation)
        base_lesson = planner_output.reflexion_lesson
        lesson = ReflexionLesson(
            lesson_id=(base_lesson.lesson_id if base_lesson else _stable_id("reflexion", planner_output.task_id, planner_output.trace_id)),
            task_type=(base_lesson.task_type if base_lesson else "agent_runtime"),
            failure_type=failure_reason,
            root_cause="runtime_observation_failed_verification",
            lesson=(
                base_lesson.lesson
                if base_lesson
                else "Create a reviewed Reflexion candidate after runtime failure."
            ),
            recommended_fix=(
                base_lesson.recommended_fix
                if base_lesson
                else "Inspect observation evidence, adjust plan, and rerun verification."
            ),
            trigger_condition=failure_reason,
            evidence_refs=evidence_refs,
        )
        candidate = None
        if self._memory_engine and memory_scope and retention_policy:
            candidate = self._memory_engine.submit_reflexion_lesson_candidate(
                scope=memory_scope,
                lesson=lesson,
                retention_policy=retention_policy,
            )
        verdict = ReflectionVerdict(
            decision="replan",
            evidence_enough=False,
            reason=failure_reason,
        )
        trace_events.append(
            _trace_event(
                planner_output,
                "reflection_completed",
                {"decision": verdict.decision, "reason": verdict.reason},
                ordinal=len(trace_events),
            )
        )
        trace_events.append(
            _trace_event(
                planner_output,
                "reflexion_candidate_created",
                {
                    "lesson_id": lesson.lesson_id,
                    "evidence_refs": list(lesson.evidence_refs),
                    "memory_candidate_id": candidate.candidate_id if candidate else None,
                    "review_status": candidate.review_status.value if candidate else lesson.review_status,
                },
                ordinal=len(trace_events),
            )
        )
        return AgentRuntimeResult(
            task_id=planner_output.task_id,
            trace_id=planner_output.trace_id,
            plan_state=planner_output.plan_state,
            capability_plan=capability_plan,
            reflection_verdict=verdict,
            replan_decision=None,
            reflexion_lesson=lesson,
            trace_events=trace_events,
            memory_candidate=candidate,
        )


def _blocked_before_execution(planner_output: PlannerOutput) -> bool:
    return planner_output.plan_state.status == "blocked" or planner_output.reflection_verdict.decision in {
        "ask_user",
        "refuse",
    }


def _capability_plan_with_executed_tools(
    plan: CapabilityPlan,
    observations: list[RuntimeObservation] | tuple[RuntimeObservation, ...],
) -> CapabilityPlan:
    executed_tools: list[str] = []
    for observation in observations:
        if observation.tool_id and observation.status == "completed" and observation.tool_id not in executed_tools:
            executed_tools.append(observation.tool_id)
    return plan.model_copy(update={"executed_tools": executed_tools})


def _observation_for_reflection(
    observations: list[RuntimeObservation] | tuple[RuntimeObservation, ...],
) -> RuntimeObservation:
    for observation in reversed(observations):
        evidence = observation.evidence
        if evidence.evidence_count or evidence.citation_coverage or evidence.unsupported_claim_inputs:
            return observation
    return observations[-1]


def _replan_trigger(evidence: EvidenceBundle, citation_threshold: float) -> str | None:
    if evidence.evidence_count == 0:
        return "retrieval_empty"
    if evidence.citation_coverage < citation_threshold:
        return "citation_coverage_low"
    if evidence.unsupported_claim_inputs:
        return "unsupported_claim"
    return None


def _replanned_result(
    *,
    planner_output: PlannerOutput,
    trigger: str,
    observation: RuntimeObservation,
    capability_plan: CapabilityPlan,
    trace_events: list[TraceRecord],
    citation_threshold: float,
) -> AgentRuntimeResult:
    verdict = ReflectionVerdict(
        decision="replan",
        evidence_enough=False,
        citation_coverage=observation.evidence.citation_coverage,
        unsupported_claims=list(observation.evidence.unsupported_claim_inputs),
        reason=trigger,
    )
    new_step = PlanStep(
        step_id="replan_step_1",
        goal=f"Change retrieval trajectory after {trigger}.",
        action_type="retrieve_deeper_evidence",
        required_evidence=_required_evidence(planner_output),
        allowed_capabilities=list(capability_plan.allowed_capabilities),
        failure_conditions=["retrieval_empty", "citation_coverage_low", "unsupported_claim"],
        budget={
            "trajectory_changed": True,
            "trigger": trigger,
            "required_citation_coverage": citation_threshold,
            "retrievers_used": [
                "bm25",
                "vector",
                "staged_requery",
                "graph_expand",
                "rerank",
            ],
        },
    )
    follow_up = PlanStep(
        step_id="replan_step_2",
        goal="Reflect again before final answer.",
        action_type="reflect_before_final",
        required_evidence=_required_evidence(planner_output),
        allowed_capabilities=list(capability_plan.allowed_capabilities),
        failure_conditions=["citation_coverage_low", "unsupported_claim", "security_blocked"],
        budget={"requires_previous_step": new_step.step_id},
    )
    plan_state = PlanState(
        plan_id=planner_output.plan_state.plan_id,
        status="replanned",
        steps=[new_step, follow_up],
        current_step_id=new_step.step_id,
    )
    replan_decision = ReplanDecision(
        trigger=trigger,
        replaced_step_ids=[observation.step_id],
        new_steps=[new_step, follow_up],
        reason="reflection_gate_changed_subsequent_trajectory",
    )
    trace_events.append(
        _trace_event(
            planner_output,
            "reflection_completed",
            {
                "decision": verdict.decision,
                "reason": verdict.reason,
                "citation_coverage": verdict.citation_coverage,
                "unsupported_claims": list(verdict.unsupported_claims),
            },
            ordinal=len(trace_events),
        )
    )
    trace_events.append(
        _trace_event(
            planner_output,
            "replan_created",
            {
                "trigger": trigger,
                "replaced_step_ids": list(replan_decision.replaced_step_ids),
                "new_step_ids": [step.step_id for step in replan_decision.new_steps],
                "trajectory_changed": True,
            },
            ordinal=len(trace_events),
        )
    )
    return AgentRuntimeResult(
        task_id=planner_output.task_id,
        trace_id=planner_output.trace_id,
        plan_state=plan_state,
        capability_plan=capability_plan,
        reflection_verdict=verdict,
        replan_decision=replan_decision,
        reflexion_lesson=None,
        trace_events=trace_events,
    )


def _required_evidence(planner_output: PlannerOutput) -> list[str]:
    if planner_output.selected_skill:
        return list(planner_output.selected_skill.required_evidence)
    return list(planner_output.retrieval_plan.evidence_requirements)


def _evidence_refs(observation: RuntimeObservation) -> list[str]:
    refs = list(observation.evidence.evidence_ids)
    if refs:
        return refs
    if observation.metadata.get("evidence_ref"):
        return [str(observation.metadata["evidence_ref"])]
    return [f"runtime_observation:{observation.step_id}"]


def _last_non_empty_output(
    observations: list[RuntimeObservation] | tuple[RuntimeObservation, ...],
) -> str:
    for observation in reversed(observations):
        if observation.output:
            return observation.output
    return ""


def _trace_event(
    planner_output: PlannerOutput,
    event_type: str,
    payload: dict[str, Any],
    *,
    ordinal: int,
) -> TraceRecord:
    return TraceRecord(
        event_id=_stable_id("evt", planner_output.task_id, planner_output.trace_id, event_type, str(ordinal)),
        task_id=planner_output.task_id,
        trace_id=planner_output.trace_id,
        event_type=event_type,
        payload=payload,
    )


def _stable_id(prefix: str, *parts: str) -> str:
    source = "|".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(source.encode('utf-8')).hexdigest()[:12]}"


__all__ = [
    "AgentControlRuntime",
    "AgentRuntimeResult",
    "RuntimeObservation",
]
