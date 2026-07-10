from __future__ import annotations

import hashlib
from typing import Iterable

from zuno.knowledge.agentic.contracts import EvidenceLedgerRecord


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

    def to_trace(self) -> dict:
        return {
            "record_count": len(self._records),
            "rounds": sorted({record.retrieval_round for record in self._records}),
            "records": [record.model_dump(mode="json") for record in self._records],
        }


def _span_key(record: EvidenceLedgerRecord) -> str:
    if not record.source_span:
        return "no_source_span"
    return repr(sorted(record.source_span.items()))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


__all__ = ["EvidenceLedger"]
