"""Regression tests for PHASE22 public benchmark candidate generation."""

from __future__ import annotations

from tools.evals.zuno.rag_eval.datasets.generate_candidate_pack import (
    load_graphrag_cases,
    load_multihop_cases,
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


def test_multihop_selection_skips_records_without_upstream_evidence(tmp_path, monkeypatch) -> None:
    import json
    import tools.evals.zuno.rag_eval.datasets.generate_candidate_pack as generator

    cache = tmp_path / "multihop_rag"
    cache.mkdir(parents=True)
    rows = [{"query": "missing", "answer": "missing", "evidence_list": []}]
    rows.extend(
        {
            "query": f"question {index}",
            "answer": f"answer {index}",
            "evidence_list": [{"title": f"doc-{index}", "source": f"src-{index}"}],
        }
        for index in range(24)
    )
    (cache / "queries.json").write_text(json.dumps(rows), encoding="utf-8")
    monkeypatch.setattr(generator, "CACHE_ROOT", tmp_path)

    cases = load_multihop_cases(start_idx=33, limit=24)

    assert len(cases) == 24
    assert cases[0]["source_record_id"] == "multihop_query_002"
    assert all(case["evidence_status"] == "evidence_complete" for case in cases)


def test_graphrag_selection_requires_exact_official_textbook_match(tmp_path, monkeypatch) -> None:
    import json
    import tools.evals.zuno.rag_eval.datasets.generate_candidate_pack as generator

    cache = tmp_path / "microsoft_graphrag"
    textbook = cache / "textbooks" / "textbook1"
    textbook.mkdir(parents=True)
    questions = [
        {"Question": f"Official question {index}?", "Answer": f"answer {index}"}
        for index in range(24)
    ]
    (cache / "questions.jsonl").write_text(
        "\n".join(json.dumps(item) for item in questions), encoding="utf-8"
    )
    (textbook / "textbook1.md").write_text(
        "\n".join(item["Question"] for item in questions), encoding="utf-8"
    )
    monkeypatch.setattr(generator, "CACHE_ROOT", tmp_path)

    cases = load_graphrag_cases(start_idx=57, limit=24)

    assert len(cases) == 24
    assert all(case["evidence_status"] == "evidence_complete" for case in cases)
    assert all(case["gold_document_refs"] == ["textbooks/textbook1/textbook1.md"] for case in cases)
    assert all("#L" in case["gold_evidence_refs"][0] for case in cases)
