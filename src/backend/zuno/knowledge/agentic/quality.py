from __future__ import annotations

from zuno.knowledge.agentic.contracts import EvidenceLedgerRecord, RetrievalQualityVerdict


class RetrievalQualityGate:
    def evaluate(self, records: list[EvidenceLedgerRecord] | tuple[EvidenceLedgerRecord, ...]) -> RetrievalQualityVerdict:
        if not records:
            return RetrievalQualityVerdict.IRRELEVANT
        if any(record.contradiction_group for record in records):
            return RetrievalQualityVerdict.CONFLICTING
        if any(not record.source_span for record in records):
            return RetrievalQualityVerdict.INSUFFICIENT_SPAN
        if max(record.rerank_score or record.fusion_score or record.raw_score for record in records) < 0.1:
            return RetrievalQualityVerdict.AMBIGUOUS
        return RetrievalQualityVerdict.RELEVANT


__all__ = ["RetrievalQualityGate"]
