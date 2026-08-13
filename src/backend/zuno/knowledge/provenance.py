from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Any


class CitationValidationStatus(StrEnum):
    PASS = "PASS"
    REJECT = "REJECT"


class CitationFailureClass(StrEnum):
    INVALID_PROVENANCE = "INVALID_PROVENANCE"
    UNSUPPORTED = "UNSUPPORTED"
    STALE = "STALE"
    SCOPE_DENIED = "SCOPE_DENIED"


@dataclass(frozen=True, slots=True)
class CitationCandidate:
    claim_id: str
    evidence_id: str
    document_version_id: str
    source_span_id: str
    citation_id: str
    provenance_ref: str | None = None
    scope_ref: str | None = None
    trace_ref: str | None = None


@dataclass(frozen=True, slots=True)
class EvidenceLineage:
    evidence_id: str
    document_version_id: str
    source_span_id: str
    claim_refs: tuple[str, ...] = ()
    scope_ref: str | None = None
    provenance_ref: str | None = None
    trace_ref: str | None = None
    stale: bool = False


@dataclass(frozen=True, slots=True)
class SourceSpanLineage:
    source_span_id: str
    evidence_id: str
    document_version_id: str
    scope_ref: str | None = None


@dataclass(frozen=True, slots=True)
class CitationValidationResult:
    status: CitationValidationStatus
    failure_class: CitationFailureClass | None
    reason_code: str
    claim_id: str
    evidence_id: str
    document_version_id: str | None
    source_span_id: str | None
    trace_ref: str | None = None

    @property
    def accepted(self) -> bool:
        return self.status is CitationValidationStatus.PASS


class CitationProvenanceGuard:
    """Deterministic identity and lineage validation for citation candidates."""

    def validate(
        self,
        candidate: CitationCandidate,
        *,
        evidence_by_id: Mapping[str, EvidenceLineage | Mapping[str, Any]],
        spans_by_id: Mapping[str, SourceSpanLineage | Mapping[str, Any]],
        claim_evidence_by_id: Mapping[str, Iterable[str]] | None = None,
        visible_scope_refs: set[str] | None = None,
    ) -> CitationValidationResult:
        evidence_value = evidence_by_id.get(candidate.evidence_id)
        if evidence_value is None:
            return self._reject(candidate, CitationFailureClass.UNSUPPORTED, "evidence_missing")
        evidence = _evidence_lineage(evidence_value, evidence_id=candidate.evidence_id)
        if evidence.stale:
            return self._reject(candidate, CitationFailureClass.STALE, "evidence_stale")
        if not candidate.document_version_id or not evidence.document_version_id:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "document_version_missing")
        if candidate.document_version_id != evidence.document_version_id:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "document_version_mismatch")
        if not candidate.source_span_id or not evidence.source_span_id:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "source_span_missing")
        if candidate.source_span_id != evidence.source_span_id:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "evidence_span_mismatch")

        span_value = spans_by_id.get(candidate.source_span_id)
        if span_value is None:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "source_span_not_found")
        span = _source_span_lineage(span_value, source_span_id=candidate.source_span_id)
        if span.evidence_id != evidence.evidence_id:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "source_span_evidence_mismatch")
        if span.document_version_id != evidence.document_version_id:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "source_span_document_mismatch")

        if claim_evidence_by_id is not None and candidate.claim_id in claim_evidence_by_id:
            allowed_evidence = {str(item) for item in claim_evidence_by_id[candidate.claim_id]}
            if candidate.evidence_id not in allowed_evidence:
                return self._reject(candidate, CitationFailureClass.UNSUPPORTED, "claim_evidence_relation_missing")
        elif evidence.claim_refs and candidate.claim_id not in set(evidence.claim_refs):
            return self._reject(candidate, CitationFailureClass.UNSUPPORTED, "claim_evidence_relation_missing")

        if evidence.scope_ref and candidate.scope_ref and evidence.scope_ref != candidate.scope_ref:
            return self._reject(candidate, CitationFailureClass.SCOPE_DENIED, "candidate_scope_mismatch")
        if visible_scope_refs is not None:
            effective_scope = candidate.scope_ref or evidence.scope_ref
            if effective_scope is None or effective_scope not in visible_scope_refs:
                return self._reject(candidate, CitationFailureClass.SCOPE_DENIED, "citation_scope_not_visible")

        if evidence.provenance_ref and candidate.provenance_ref != evidence.provenance_ref:
            return self._reject(candidate, CitationFailureClass.INVALID_PROVENANCE, "provenance_reference_mismatch")

        return CitationValidationResult(
            status=CitationValidationStatus.PASS,
            failure_class=None,
            reason_code="provenance_valid",
            claim_id=candidate.claim_id,
            evidence_id=candidate.evidence_id,
            document_version_id=candidate.document_version_id,
            source_span_id=candidate.source_span_id,
            trace_ref=candidate.trace_ref,
        )

    @staticmethod
    def _reject(
        candidate: CitationCandidate,
        failure_class: CitationFailureClass,
        reason_code: str,
    ) -> CitationValidationResult:
        return CitationValidationResult(
            status=CitationValidationStatus.REJECT,
            failure_class=failure_class,
            reason_code=reason_code,
            claim_id=candidate.claim_id,
            evidence_id=candidate.evidence_id,
            document_version_id=candidate.document_version_id or None,
            source_span_id=candidate.source_span_id or None,
            trace_ref=candidate.trace_ref,
        )


def lineage_index_from_observations(
    observations: Iterable[Mapping[str, Any] | Any],
) -> tuple[dict[str, EvidenceLineage], dict[str, SourceSpanLineage]]:
    evidence: dict[str, EvidenceLineage] = {}
    spans: dict[str, SourceSpanLineage] = {}
    for observation in observations:
        metadata = _value(observation, "metadata", {}) or {}
        records: list[Mapping[str, Any]] = []
        ledger = metadata.get("ledger")
        if isinstance(ledger, Mapping):
            records.extend(item for item in ledger.get("records", []) if isinstance(item, Mapping))
        bundle = metadata.get("evidence_bundle")
        if isinstance(bundle, Mapping):
            records.extend(item for item in bundle.get("items", []) if isinstance(item, Mapping))
        records.extend(item for item in metadata.get("citation_lineage", []) if isinstance(item, Mapping))
        for record in records:
            evidence_id = str(record.get("evidence_id") or "").strip()
            if not evidence_id:
                continue
            source_span = record.get("source_span")
            source_span = source_span if isinstance(source_span, Mapping) else {}
            document_version_id = str(
                record.get("document_version_id")
                or record.get("document_version")
                or source_span.get("document_version_id")
                or ""
            )
            source_span_id = _source_span_id(record, source_span)
            if not document_version_id or not source_span_id:
                continue
            lineage = EvidenceLineage(
                evidence_id=evidence_id,
                document_version_id=document_version_id,
                source_span_id=source_span_id,
                claim_refs=tuple(str(item) for item in record.get("claim_refs", []) if str(item)),
                scope_ref=_optional_text(record.get("scope_ref") or record.get("acl_scope")),
                provenance_ref=_optional_text(
                    record.get("provenance_ref")
                    or record.get("source_reference")
                    or record.get("citation_lineage_id")
                ),
                trace_ref=_optional_text(record.get("trace_span") or record.get("trace_ref")),
                stale=bool(record.get("stale")),
            )
            evidence[evidence_id] = lineage
            spans[source_span_id] = SourceSpanLineage(
                source_span_id=source_span_id,
                evidence_id=evidence_id,
                document_version_id=document_version_id,
                scope_ref=lineage.scope_ref,
            )
    return evidence, spans


def evidence_id_from_citation(citation_id: str) -> str:
    return citation_id.removeprefix("citation:")


def _evidence_lineage(value: EvidenceLineage | Mapping[str, Any], *, evidence_id: str) -> EvidenceLineage:
    if isinstance(value, EvidenceLineage):
        return value
    source_span = value.get("source_span") if isinstance(value.get("source_span"), Mapping) else {}
    return EvidenceLineage(
        evidence_id=str(value.get("evidence_id") or evidence_id),
        document_version_id=str(value.get("document_version_id") or value.get("document_version") or source_span.get("document_version_id") or ""),
        source_span_id=str(value.get("source_span_id") or _source_span_id(value, source_span)),
        claim_refs=tuple(str(item) for item in value.get("claim_refs", []) if str(item)),
        scope_ref=_optional_text(value.get("scope_ref") or value.get("acl_scope")),
        provenance_ref=_optional_text(value.get("provenance_ref") or value.get("source_reference")),
        trace_ref=_optional_text(value.get("trace_span") or value.get("trace_ref")),
        stale=bool(value.get("stale")),
    )


def _source_span_lineage(value: SourceSpanLineage | Mapping[str, Any], *, source_span_id: str) -> SourceSpanLineage:
    if isinstance(value, SourceSpanLineage):
        return value
    return SourceSpanLineage(
        source_span_id=str(value.get("source_span_id") or value.get("span_id") or source_span_id),
        evidence_id=str(value.get("evidence_id") or ""),
        document_version_id=str(value.get("document_version_id") or ""),
        scope_ref=_optional_text(value.get("scope_ref")),
    )


def _source_span_id(record: Mapping[str, Any], source_span: Mapping[str, Any]) -> str:
    explicit = str(
        record.get("source_span_id")
        or source_span.get("source_span_id")
        or source_span.get("span_id")
        or source_span.get("chunk_id")
        or source_span.get("block_id")
        or record.get("chunk_id")
        or record.get("block_id")
        or ""
    )
    if explicit:
        return explicit
    if not source_span:
        return ""
    canonical = json.dumps(dict(source_span), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return f"span:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:24]}"


def _optional_text(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _value(value: object, name: str, default: Any) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


__all__ = [
    "CitationCandidate",
    "CitationFailureClass",
    "CitationProvenanceGuard",
    "CitationValidationResult",
    "CitationValidationStatus",
    "EvidenceLineage",
    "SourceSpanLineage",
    "evidence_id_from_citation",
    "lineage_index_from_observations",
]
