from __future__ import annotations

import hashlib
from typing import Iterable

from zuno.knowledge.agentic.contracts import EvidenceCoverageSummary, EvidenceFrontier, EvidenceLedgerRecord


class EvidenceLedger:
    def __init__(self) -> None:
        self._records: list[EvidenceLedgerRecord] = []
        self._dedupe_keys: set[tuple[str, str, str]] = set()

    def add(self, record: EvidenceLedgerRecord) -> bool:
        normalized = record.model_copy(
            update={
                "text_hash": record.text_hash or _hash(record.text),
                "strict_citation_allowed": bool(record.source_span),
            }
        )
        key = (normalized.document_version or normalized.document_id, _span_key(normalized), normalized.text_hash)
        if key in self._dedupe_keys:
            return False
        self._dedupe_keys.add(key)
        self._records.append(normalized)
        return True

    def extend(self, records: Iterable[EvidenceLedgerRecord]) -> int:
        return sum(1 for record in records if self.add(record))

    def records(self) -> tuple[EvidenceLedgerRecord, ...]:
        return tuple(self._records)

    def by_round(self, retrieval_round: int) -> tuple[EvidenceLedgerRecord, ...]:
        return tuple(record for record in self._records if record.retrieval_round == retrieval_round)

    def novelty_for_round(self, retrieval_round: int) -> float:
        records = self.by_round(retrieval_round)
        if not records:
            return 0.0
        previous = {record.text_hash for record in self._records if record.retrieval_round < retrieval_round}
        new = [record for record in records if record.text_hash not in previous]
        return len(new) / len(records)

    def frontier(self, *, claims: list[str] | tuple[str, ...] = ()) -> EvidenceFrontier:
        claim_refs = [str(claim) for claim in claims if str(claim)]
        claim_set = set(claim_refs)
        covered_claims = {claim for record in self._records for claim in record.claim_refs if claim in claim_set}
        strict_records = [record for record in self._records if record.strict_citation_allowed]
        conflict_groups: dict[str, list[str]] = {}
        for record in self._records:
            if record.contradiction_group:
                conflict_groups.setdefault(record.contradiction_group, []).append(record.evidence_id)
        newest_round = max((record.retrieval_round for record in self._records), default=0)
        missing_strict = [record.evidence_id for record in self._records if not record.strict_citation_allowed]
        authority_refs = sorted({record.freshness_version for record in self._records if record.freshness_version})
        temporal_versions = sorted({record.document_version for record in self._records if record.document_version})
        stop_reasons: list[str] = []
        if claim_refs and len(covered_claims) < len(claim_set):
            stop_reasons.append("coverage_incomplete")
        if missing_strict:
            stop_reasons.append("strict_citation_missing")
        if conflict_groups:
            stop_reasons.append("conflict_unresolved")
        if not self._records:
            stop_reasons.append("no_evidence")
        coverage = EvidenceCoverageSummary(
            claim_count=len(claim_set),
            covered_claim_count=len(covered_claims),
            strict_citation_count=len(strict_records),
            authority_count=len(authority_refs),
            temporal_version_count=len(temporal_versions),
            conflict_group_count=len(conflict_groups),
            coverage_ratio=(len(covered_claims) / len(claim_set)) if claim_set else (1.0 if self._records else 0.0),
            strict_citation_ratio=(len(strict_records) / len(self._records)) if self._records else 0.0,
        )
        return EvidenceFrontier(
            total_records=len(self._records),
            newest_round=newest_round,
            novelty=self.novelty_for_round(newest_round) if newest_round else 0.0,
            uncovered_claim_refs=sorted(claim_set - covered_claims),
            missing_strict_citation_ids=missing_strict,
            conflict_groups={key: sorted(value) for key, value in sorted(conflict_groups.items())},
            authority_refs=authority_refs,
            temporal_versions=temporal_versions,
            stop_reasons=stop_reasons,
            coverage=coverage,
        )

    def to_trace(self) -> dict:
        frontier = self.frontier()
        return {
            "record_count": len(self._records),
            "rounds": sorted({record.retrieval_round for record in self._records}),
            "frontier": frontier.model_dump(mode="json"),
            "records": [record.model_dump(mode="json") for record in self._records],
        }


def _span_key(record: EvidenceLedgerRecord) -> str:
    if not record.source_span:
        return "no_source_span"
    return repr(sorted(record.source_span.items()))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


__all__ = ["EvidenceLedger"]
