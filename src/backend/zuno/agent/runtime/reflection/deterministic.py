from __future__ import annotations

from dataclasses import dataclass

from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus, ReflectionDecision
from zuno.agent.runtime.state import AgentRuntimeState


@dataclass(frozen=True, slots=True)
class ReflectionGateResult:
    decision: ReflectionDecision
    reason: str
    unsupported_claims: tuple[str, ...] = ()


class DeterministicReflectionGate:
    def decide(self, state: AgentRuntimeState) -> ReflectionGateResult:
        preset = self._first_reflection_preset(state)
        if preset is not None:
            return ReflectionGateResult(preset, "preset_reflection_decision")
        if state.counters.reflections >= state.limits.max_reflections:
            return ReflectionGateResult(ReflectionDecision.ABSTAIN, "max_reflections_reached")
        if self._has_failed_tool(state.observations):
            return ReflectionGateResult(ReflectionDecision.RETRIEVE_MORE, "tool_failed")
        if self._explicit_retrieval_empty(state.observations):
            if state.counters.replans >= state.limits.max_replans:
                return ReflectionGateResult(ReflectionDecision.ABSTAIN, "max_replans_reached_after_empty_retrieval")
            return ReflectionGateResult(ReflectionDecision.RETRIEVE_MORE, "retrieval_empty")
        synthesis = self._latest_synthesis(state.observations)
        unsupported = tuple(synthesis.metadata.get("unsupported_claims", ())) if synthesis is not None else ()
        if unsupported and self._has_any_rewrite(state.observations):
            return ReflectionGateResult(ReflectionDecision.ABSTAIN, "unsupported_after_rewrite", unsupported)
        if unsupported:
            return ReflectionGateResult(ReflectionDecision.REWRITE_ANSWER, "unsupported_claims", unsupported)
        return ReflectionGateResult(ReflectionDecision.PASS, "deterministic_gate_pass")

    def _first_reflection_preset(self, state: AgentRuntimeState) -> ReflectionDecision | None:
        if state.reflection_decision is None:
            return None
        if any(observation.kind == ObservationKind.REFLECTION for observation in state.observations):
            return None
        return ReflectionDecision(state.reflection_decision)

    def _explicit_retrieval_empty(self, observations: list[NormalizedObservation]) -> bool:
        retrievals = [item for item in observations if item.kind == ObservationKind.RETRIEVAL]
        if not retrievals:
            return False
        latest = retrievals[-1]
        return not latest.evidence_ids and latest.metadata.get("retrieval_request") is not True

    def _has_failed_tool(self, observations: list[NormalizedObservation]) -> bool:
        return any(
            item.kind == ObservationKind.TOOL and item.status == ObservationStatus.FAILED
            for item in observations
        )

    def _latest_synthesis(self, observations: list[NormalizedObservation]) -> NormalizedObservation | None:
        for observation in reversed(observations):
            if observation.metadata.get("grounded_synthesis"):
                return observation
        return None

    def _has_any_rewrite(self, observations: list[NormalizedObservation]) -> bool:
        return any(observation.metadata.get("answer_rewritten") for observation in observations)


__all__ = ["DeterministicReflectionGate", "ReflectionGateResult"]
