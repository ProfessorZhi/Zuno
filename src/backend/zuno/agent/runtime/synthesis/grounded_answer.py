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
        draft = _draft_text(goal=state.goal, citation_ids=citation_ids, rewritten=rewritten)
        claims = tuple(
            claim.__class__(
                claim_id=claim.claim_id,
                text=claim.text,
                required_citation=requires_citation,
            )
            for claim in self.claim_extractor.extract(goal=state.goal, draft=draft)
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
                "draft": draft,
                "claims": [asdict(claim) for claim in claims],
                "citation_bindings": [asdict(binding) for binding in bindings],
                "unsupported_claims": unsupported_claims,
                "rewritten": rewritten,
            },
        )


def _draft_text(*, goal: str, citation_ids: list[str], rewritten: bool) -> str:
    if citation_ids:
        return f"{goal} {' '.join(citation_ids)}"
    if rewritten:
        return f"Abstain from unsupported answer for: {goal}"
    return f"Draft answer for: {goal}"


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
