from __future__ import annotations

import hashlib

from zuno.agent.contracts import ReflexionLesson
from zuno.agent.runtime.contracts import FinalizationStatus, ReflectionDecision
from zuno.agent.runtime.state import AgentRuntimeState


class ReflexionCandidateBuilder:
    def build(self, state: AgentRuntimeState) -> ReflexionLesson | None:
        if state.finalization_status not in {
            FinalizationStatus.ABSTAINED,
            FinalizationStatus.BLOCKED,
            FinalizationStatus.FAILED,
        } and state.reflection_decision not in {ReflectionDecision.ABSTAIN, ReflectionDecision.REFUSE}:
            return None
        evidence_refs = tuple(state.trace_event_ids[-5:] or [state.trace_id])
        failure_type = (
            state.reflection_decision.value
            if state.reflection_decision is not None
            else state.finalization_status.value
        )
        return ReflexionLesson(
            lesson_id=_stable_id("runtime_reflexion", state.task_id, failure_type),
            task_type="unified_agent_runtime",
            failure_type=failure_type,
            root_cause="Runtime ended without a supported final answer.",
            lesson="For similar tasks, require evidence and citation checks before final answer.",
            recommended_fix="Prefer plan_execute_with_replan and retrieve more evidence when citation support is missing.",
            trigger_condition="unsupported claims, missing citations, or abstain finalization",
            evidence_refs=list(evidence_refs),
            review_status="candidate",
        )


def _stable_id(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:16]


__all__ = ["ReflexionCandidateBuilder"]
