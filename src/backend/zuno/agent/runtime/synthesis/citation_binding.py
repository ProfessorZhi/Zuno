from __future__ import annotations

from dataclasses import dataclass

from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind
from zuno.agent.runtime.synthesis.claims import StructuredClaim


@dataclass(frozen=True, slots=True)
class CitationBinding:
    claim_id: str
    citation_id: str | None
    support_verdict: str


class RuntimeCitationBinder:
    def bind(
        self,
        *,
        claims: tuple[StructuredClaim, ...],
        observations: list[NormalizedObservation],
    ) -> tuple[CitationBinding, ...]:
        strict_citations = _strict_citations(observations)
        bindings: list[CitationBinding] = []
        for index, claim in enumerate(claims):
            citation_id = strict_citations[index] if index < len(strict_citations) else None
            bindings.append(
                CitationBinding(
                    claim_id=claim.claim_id,
                    citation_id=citation_id,
                    support_verdict="supported" if citation_id else "insufficient",
                )
            )
        return tuple(bindings)


def _strict_citations(observations: list[NormalizedObservation]) -> list[str]:
    citations: list[str] = []
    for observation in observations:
        if observation.kind != ObservationKind.RETRIEVAL:
            continue
        citations.extend(observation.citation_ids)
    return citations


__all__ = ["CitationBinding", "RuntimeCitationBinder"]
