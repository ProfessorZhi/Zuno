from __future__ import annotations

from zuno.knowledge.agentic import CorrectiveAction, CorrectiveRetrievalPolicy, EvidenceLedger, EvidenceLedgerRecord, QueryStrategy, RetrievalQualityGate, RetrievalQualityVerdict


def _record(
    evidence_id: str,
    *,
    text: str = "alpha",
    span: dict | None = None,
    round_number: int = 1,
    claim_refs: list[str] | None = None,
    contradiction_group: str = "",
    document_version: str = "v1",
) -> EvidenceLedgerRecord:
    return EvidenceLedgerRecord(
        evidence_id=evidence_id,
        document_id="doc_1",
        document_version=document_version,
        source_span=span if span is not None else {"page": 1, "line_range": [1, 1]},
        retrieval_round=round_number,
        query_id=f"q{round_number}",
        query_strategy=QueryStrategy.DIRECT,
        retriever="bm25",
        raw_score=0.8,
        rerank_score=0.8,
        text=text,
        claim_refs=claim_refs or [],
        contradiction_group=contradiction_group,
        freshness_version=document_version,
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


def test_evidence_frontier_tracks_coverage_conflict_authority_and_temporal_versions() -> None:
    ledger = EvidenceLedger()

    ledger.add(_record("ev_claim_a", text="alpha covered", claim_refs=["claim:a"], document_version="v1"))
    ledger.add(
        _record(
            "ev_conflict",
            text="beta conflict",
            claim_refs=["claim:b"],
            contradiction_group="policy-date",
            document_version="v2",
            round_number=2,
        )
    )
    ledger.add(_record("ev_no_span", text="graph summary", span={}, round_number=2))

    frontier = ledger.frontier(claims=["claim:a", "claim:b", "claim:c"])

    assert frontier.total_records == 3
    assert frontier.newest_round == 2
    assert frontier.coverage.claim_count == 3
    assert frontier.coverage.covered_claim_count == 2
    assert frontier.coverage.coverage_ratio == 2 / 3
    assert frontier.coverage.strict_citation_count == 2
    assert frontier.coverage.strict_citation_ratio == 2 / 3
    assert frontier.uncovered_claim_refs == ["claim:c"]
    assert frontier.missing_strict_citation_ids == ["ev_no_span"]
    assert frontier.conflict_groups == {"policy-date": ["ev_conflict"]}
    assert frontier.authority_refs == ["v1", "v2"]
    assert frontier.temporal_versions == ["v1", "v2"]
    assert frontier.stop_reasons == ["coverage_incomplete", "strict_citation_missing", "conflict_unresolved"]


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
    assert (
        policy.decide(
            verdict=RetrievalQualityVerdict.RELEVANT,
            frontier_stop_reasons=["coverage_incomplete"],
        )
        == CorrectiveAction.QUERY_REWRITE
    )
    assert (
        policy.decide(
            verdict=RetrievalQualityVerdict.RELEVANT,
            frontier_stop_reasons=["strict_citation_missing"],
        )
        == CorrectiveAction.FOCUSED_CITATION_RETRIEVE
    )
    assert (
        policy.decide(
            verdict=RetrievalQualityVerdict.RELEVANT,
            frontier_stop_reasons=["conflict_unresolved"],
        )
        == CorrectiveAction.GRAPH_EXPAND
    )
