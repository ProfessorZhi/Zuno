from __future__ import annotations

from dataclasses import dataclass

from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind
from zuno.agent.runtime.synthesis.claims import StructuredClaim
from zuno.knowledge.provenance import (
    CitationCandidate,
    CitationProvenanceGuard,
    CitationValidationResult,
    evidence_id_from_citation,
    lineage_index_from_observations,
)


@dataclass(frozen=True, slots=True)
class CitationBinding:
    claim_id: str
    citation_id: str | None
    support_verdict: str
    evidence_id: str | None = None
    document_version_id: str | None = None
    source_span_id: str | None = None
    provenance_ref: str | None = None
    failure_class: str | None = None
    reason_code: str | None = None
    attempted_citation_id: str | None = None
    trace_ref: str | None = None


class RuntimeCitationBinder:
    def __init__(self, *, provenance_guard: CitationProvenanceGuard | None = None) -> None:
        self.provenance_guard = provenance_guard or CitationProvenanceGuard()

    def bind(
        self,
        *,
        claims: tuple[StructuredClaim, ...],
        observations: list[NormalizedObservation],
    ) -> tuple[CitationBinding, ...]:
        strict_citations = _strict_citations(observations)
        evidence_by_id, spans_by_id = lineage_index_from_observations(observations)
        bindings: list[CitationBinding] = []
        claim_list = list(claims)
        for claim in claim_list:
            candidates = _candidate_citations(
                claim,
                strict_citations=strict_citations,
                evidence_by_id=evidence_by_id,
                single_claim=len(claim_list) == 1,
            )
            if len(candidates) != 1:
                bindings.append(
                    CitationBinding(
                        claim_id=claim.claim_id,
                        citation_id=None,
                        support_verdict="insufficient",
                        failure_class="UNSUPPORTED",
                        reason_code=("citation_ambiguous_without_claim_relation" if candidates else "citation_provenance_unavailable"),
                    )
                )
                continue
            citation_id = candidates[0]
            evidence_id = evidence_id_from_citation(citation_id)
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                bindings.append(
                    CitationBinding(
                        claim_id=claim.claim_id,
                        citation_id=None,
                        support_verdict="insufficient",
                        failure_class="UNSUPPORTED",
                        reason_code="evidence_missing",
                        attempted_citation_id=citation_id,
                    )
                )
                continue
            candidate = CitationCandidate(
                claim_id=claim.claim_id,
                evidence_id=evidence_id,
                document_version_id=evidence.document_version_id,
                source_span_id=evidence.source_span_id,
                citation_id=citation_id,
                provenance_ref=evidence.provenance_ref,
                scope_ref=evidence.scope_ref,
                trace_ref=evidence.trace_ref,
            )
            validation = self.provenance_guard.validate(
                candidate,
                evidence_by_id=evidence_by_id,
                spans_by_id=spans_by_id,
            )
            bindings.append(_binding_from_validation(citation_id, validation, evidence))
        return tuple(bindings)


def _strict_citations(observations: list[NormalizedObservation]) -> list[str]:
    citations: list[str] = []
    for observation in observations:
        if observation.kind != ObservationKind.RETRIEVAL:
            continue
        citations.extend(observation.citation_ids)
    return citations


def _candidate_citations(
    claim: StructuredClaim,
    *,
    strict_citations: list[str],
    evidence_by_id: dict,
    single_claim: bool,
) -> list[str]:
    if claim.evidence_ids:
        requested = {str(item) for item in claim.evidence_ids}
        return [
            citation_id
            for citation_id in strict_citations
            if evidence_id_from_citation(citation_id) in requested
        ]
    related = [
        citation_id
        for citation_id in strict_citations
        if evidence_id_from_citation(citation_id) in evidence_by_id
        and claim.claim_id in set(evidence_by_id[evidence_id_from_citation(citation_id)].claim_refs)
    ]
    if related:
        return related
    if single_claim and len(strict_citations) == 1:
        return list(strict_citations)
    return []


def _binding_from_validation(citation_id: str, validation: CitationValidationResult, evidence) -> CitationBinding:
    return CitationBinding(
        claim_id=validation.claim_id,
        citation_id=citation_id if validation.accepted else None,
        support_verdict="supported" if validation.accepted else "insufficient",
        evidence_id=validation.evidence_id,
        document_version_id=validation.document_version_id,
        source_span_id=validation.source_span_id,
        provenance_ref=evidence.provenance_ref,
        failure_class=validation.failure_class.value if validation.failure_class else None,
        reason_code=validation.reason_code,
        attempted_citation_id=citation_id,
        trace_ref=validation.trace_ref,
    )


__all__ = ["CitationBinding", "RuntimeCitationBinder"]
