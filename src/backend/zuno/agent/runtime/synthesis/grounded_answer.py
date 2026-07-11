from __future__ import annotations

from dataclasses import asdict

from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.agent.runtime.synthesis.citation_binding import RuntimeCitationBinder
from zuno.agent.runtime.synthesis.claims import ClaimExtractor


class GroundedSynthesisEngine:
    def __init__(
        self,
        *,
        claim_extractor: ClaimExtractor | None = None,
        citation_binder: RuntimeCitationBinder | None = None,
    ) -> None:
        self.claim_extractor = claim_extractor or ClaimExtractor()
        self.citation_binder = citation_binder or RuntimeCitationBinder()

    def synthesize(self, state: AgentRuntimeState) -> NormalizedObservation:
        evidence_ids = _evidence_ids(state.observations) or list(state.evidence_refs)
        citation_ids = _citation_ids(state.observations)
        requires_citation = any(observation.kind == ObservationKind.RETRIEVAL for observation in state.observations)
        rewritten = any(item.metadata.get("answer_rewritten") for item in state.observations)
        final_answer = _final_answer(goal=state.goal, observations=state.observations, citation_ids=citation_ids, rewritten=rewritten)
        claims = tuple(
            claim.__class__(
                claim_id=claim.claim_id,
                text=claim.text,
                required_citation=requires_citation,
            )
            for claim in self.claim_extractor.extract(goal=state.goal, draft=final_answer)
        )
        bindings = self.citation_binder.bind(claims=claims, observations=state.observations)
        unsupported_claims = [
            claim.text
            for claim, binding in zip(claims, bindings)
            if claim.required_citation and binding.support_verdict != "supported"
        ]
        return NormalizedObservation(
            observation_id=f"synthesis:{state.run_id}:{len(state.observations) + 1}",
            kind=ObservationKind.MODEL,
            status=ObservationStatus.COMPLETED,
            source="GroundedSynthesisEngine",
            summary="grounded draft and claim bindings prepared",
            evidence_ids=evidence_ids,
            citation_ids=citation_ids,
            metadata={
                "grounded_synthesis": True,
                "final_answer": final_answer,
                "claims": [asdict(claim) for claim in claims],
                "citation_bindings": [asdict(binding) for binding in bindings],
                "unsupported_claims": unsupported_claims,
                "rewritten": rewritten,
            },
        )


def _final_answer(*, goal: str, observations: list[NormalizedObservation], citation_ids: list[str], rewritten: bool) -> str:
    normalized_goal = goal.strip().rstrip(".。")
    model_outputs = [
        str(observation.metadata.get("model_output", "")).strip()
        for observation in observations
        if observation.metadata.get("model_output")
    ]
    if model_outputs and citation_ids:
        return f"{model_outputs[-1]} {' '.join(citation_ids)}"
    if model_outputs and not rewritten:
        return model_outputs[-1]
    if citation_ids:
        return f"Grounded answer for {normalized_goal}: {' '.join(citation_ids)}"
    if rewritten:
        return f"Abstain: unsupported claims remain for {normalized_goal}."
    return f"Insufficient cited evidence to answer: {normalized_goal}."


def _evidence_ids(observations: list[NormalizedObservation]) -> list[str]:
    result: list[str] = []
    for observation in observations:
        result.extend(observation.evidence_ids)
    return result


def _citation_ids(observations: list[NormalizedObservation]) -> list[str]:
    result: list[str] = []
    for observation in observations:
        if observation.kind == ObservationKind.RETRIEVAL:
            result.extend(observation.citation_ids)
    return result


__all__ = ["GroundedSynthesisEngine"]
