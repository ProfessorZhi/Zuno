from __future__ import annotations

from zuno.knowledge.agentic import CorrectiveAction, CorrectiveRetrievalPolicy, EvidenceLedger, EvidenceLedgerRecord, QueryStrategy, RetrievalQualityGate, RetrievalQualityVerdict


def _record(evidence_id: str, *, text: str = "alpha", span: dict | None = None, round_number: int = 1) -> EvidenceLedgerRecord:
    return EvidenceLedgerRecord(
        evidence_id=evidence_id,
        document_id="doc_1",
        document_version="v1",
        source_span=span if span is not None else {"page": 1, "line_range": [1, 1]},
        retrieval_round=round_number,
        query_id=f"q{round_number}",
        query_strategy=QueryStrategy.DIRECT,
        retriever="bm25",
        raw_score=0.8,
        rerank_score=0.8,
        text=text,
    )


def test_evidence_ledger_dedupes_by_version_span_and_text_hash() -> None:
    ledger = EvidenceLedger()

    assert ledger.add(_record("ev_1")) is True
    assert ledger.add(_record("ev_2")) is False
    assert ledger.add(_record("ev_3", text="beta")) is True

    assert len(ledger.records()) == 2
    assert ledger.records()[0].strict_citation_allowed is True
    assert ledger.to_trace()["record_count"] == 2


def test_graph_evidence_without_source_span_is_not_strict_citation() -> None:
    ledger = EvidenceLedger()

    ledger.add(_record("ev_graph", span={}))

    record = ledger.records()[0]
    assert record.strict_citation_allowed is False
    assert RetrievalQualityGate().evaluate([record]) == RetrievalQualityVerdict.INSUFFICIENT_SPAN


def test_failure_bucket_maps_to_corrective_action_sequence() -> None:
    policy = CorrectiveRetrievalPolicy()

    assert policy.decide(verdict=RetrievalQualityVerdict.IRRELEVANT, failure_bucket="doc_miss") == CorrectiveAction.QUERY_REWRITE
    assert policy.decide(
        verdict=RetrievalQualityVerdict.IRRELEVANT,
        failure_bucket="doc_miss",
        used_actions=[CorrectiveAction.QUERY_REWRITE],
    ) == CorrectiveAction.MULTI_QUERY
    assert policy.decide(
        verdict=RetrievalQualityVerdict.INSUFFICIENT_SPAN,
        failure_bucket="text_hit_citation_miss",
    ) == CorrectiveAction.FOCUSED_CITATION_RETRIEVE
    assert (
        policy.decide(
            verdict=RetrievalQualityVerdict.RELEVANT,
            failure_bucket="doc_miss",
            novelty=0.0,
            max_rounds_reached=True,
        )
        == CorrectiveAction.CONTINUE
    )
    assert policy.decide(
        verdict=RetrievalQualityVerdict.IRRELEVANT,
        novelty=0.0,
    ) == CorrectiveAction.ABSTAIN
