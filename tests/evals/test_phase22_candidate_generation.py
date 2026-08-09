"""Regression tests for PHASE22 public benchmark candidate generation."""

from __future__ import annotations

from tools.evals.zuno.rag_eval.datasets.generate_candidate_pack import (
    _normalize_hotpot_supporting_facts,
)


def test_hotpot_parallel_supporting_fact_arrays_are_normalized() -> None:
    facts = _normalize_hotpot_supporting_facts(
        {"title": ["Alpha", "Beta"], "sent_id": [1, 0]}
    )

    assert facts == [("Alpha", 1), ("Beta", 0)]


def test_hotpot_legacy_pair_list_is_normalized() -> None:
    facts = _normalize_hotpot_supporting_facts([["Alpha", 1], ["Beta", 0]])

    assert facts == [("Alpha", 1), ("Beta", 0)]


def test_hotpot_malformed_supporting_facts_are_not_promoted() -> None:
    facts = _normalize_hotpot_supporting_facts(
        {"title": ["Alpha", "Beta"], "sent_id": [1]}
    )

    assert facts == [("Alpha", 1)]
