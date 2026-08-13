from __future__ import annotations

from zuno.knowledge.provenance import (
    CitationCandidate,
    CitationFailureClass,
    CitationProvenanceGuard,
    CitationValidationStatus,
    EvidenceLineage,
    SourceSpanLineage,
)


def _candidate(**overrides) -> CitationCandidate:
    payload = {
        "claim_id": "claim:1",
        "evidence_id": "evidence:1",
        "document_version_id": "document:1:v1",
        "source_span_id": "span:1",
        "citation_id": "citation:evidence:1",
        "provenance_ref": "lineage:1",
        "scope_ref": "matter:1",
    }
    payload.update(overrides)
    return CitationCandidate(**payload)


def _indexes(*, claim_refs=("claim:1",), document_version="document:1:v1"):
    evidence = EvidenceLineage(
        evidence_id="evidence:1",
        document_version_id=document_version,
        source_span_id="span:1",
        claim_refs=claim_refs,
        scope_ref="matter:1",
        provenance_ref="lineage:1",
    )
    span = SourceSpanLineage(
        source_span_id="span:1",
        evidence_id="evidence:1",
        document_version_id=document_version,
        scope_ref="matter:1",
    )
    return {"evidence:1": evidence}, {"span:1": span}


def test_correct_document_version_and_span_pass() -> None:
    evidence, spans = _indexes()

    result = CitationProvenanceGuard().validate(
        _candidate(), evidence_by_id=evidence, spans_by_id=spans, visible_scope_refs={"matter:1"}
    )

    assert result.status is CitationValidationStatus.PASS
    assert result.accepted is True


def test_wrong_document_version_is_rejected() -> None:
    evidence, spans = _indexes()

    result = CitationProvenanceGuard().validate(
        _candidate(document_version_id="document:1:v2"), evidence_by_id=evidence, spans_by_id=spans
    )

    assert result.status is CitationValidationStatus.REJECT
    assert result.failure_class is CitationFailureClass.INVALID_PROVENANCE
    assert result.reason_code == "document_version_mismatch"


def test_correct_document_with_wrong_span_is_rejected() -> None:
    evidence, spans = _indexes()

    result = CitationProvenanceGuard().validate(
        _candidate(source_span_id="span:wrong"), evidence_by_id=evidence, spans_by_id=spans
    )

    assert result.failure_class is CitationFailureClass.INVALID_PROVENANCE
    assert result.reason_code == "evidence_span_mismatch"


def test_missing_evidence_is_unsupported() -> None:
    _, spans = _indexes()

    result = CitationProvenanceGuard().validate(
        _candidate(), evidence_by_id={}, spans_by_id=spans
    )

    assert result.failure_class is CitationFailureClass.UNSUPPORTED
    assert result.reason_code == "evidence_missing"


def test_claim_without_evidence_relation_is_rejected() -> None:
    evidence, spans = _indexes(claim_refs=("claim:other",))

    result = CitationProvenanceGuard().validate(
        _candidate(), evidence_by_id=evidence, spans_by_id=spans
    )

    assert result.failure_class is CitationFailureClass.UNSUPPORTED
    assert result.reason_code == "claim_evidence_relation_missing"


def test_stale_evidence_and_cross_scope_are_not_silently_rewritten() -> None:
    evidence, spans = _indexes()
    evidence["evidence:1"] = EvidenceLineage(
        evidence_id="evidence:1",
        document_version_id="document:1:v1",
        source_span_id="span:1",
        claim_refs=("claim:1",),
        scope_ref="matter:1",
        provenance_ref="lineage:1",
        stale=True,
    )
    stale = CitationProvenanceGuard().validate(
        _candidate(), evidence_by_id=evidence, spans_by_id=spans
    )
    denied = CitationProvenanceGuard().validate(
        _candidate(scope_ref="matter:other"), evidence_by_id=_indexes()[0], spans_by_id=_indexes()[1], visible_scope_refs={"matter:1"}
    )

    assert stale.failure_class is CitationFailureClass.STALE
    assert denied.failure_class is CitationFailureClass.SCOPE_DENIED
