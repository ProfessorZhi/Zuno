"""Tests for the delegated PHASE22 candidate review boundary."""

from __future__ import annotations

import json
from pathlib import Path

from tools.scripts.review_phase22_candidate_pack import review_candidate_pack


def _write_candidates(path: Path) -> None:
    rows = [
        {
            "case_id": "case_approved",
            "source_dataset": "test",
            "source_record_id": "source-1",
            "evidence_status": "evidence_complete",
            "reviewer_status": "pending",
            "reviewer_notes": "",
        },
        {
            "case_id": "case_rejected",
            "source_dataset": "test",
            "source_record_id": "source-2",
            "evidence_status": "evidence_incomplete",
            "rejection_reason": "missing_upstream_gold_evidence",
            "reviewer_status": "pending",
            "reviewer_notes": "missing evidence",
        },
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_review_separates_approved_and_rejected_cases(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidate_cases.jsonl"
    _write_candidates(candidate_path)

    summary = review_candidate_pack(candidate_path, tmp_path / "reviewed")

    assert summary["reviewer_approved_count"] == 1
    assert summary["benchmark_eligible_count"] == 1
    assert summary["rejected_or_incomplete_count"] == 1
    assert summary["overall_status"] == "REVIEW_PARTIAL"
    reviewed = [
        json.loads(line)
        for line in (tmp_path / "reviewed" / "reviewed_cases.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert reviewed[0]["reviewer_status"] == "approved"
    assert reviewed[0]["benchmark_eligible"] is True
    assert reviewed[1]["reviewer_status"] == "rejected"
    assert reviewed[1]["benchmark_eligible"] is False


def test_review_refuses_already_reviewed_input(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidate_cases.jsonl"
    _write_candidates(candidate_path)
    candidate_path.write_text(
        candidate_path.read_text(encoding="utf-8").replace(
            '"reviewer_status": "pending"', '"reviewer_status": "approved"', 1
        ),
        encoding="utf-8",
    )

    try:
        review_candidate_pack(candidate_path, tmp_path / "reviewed")
    except ValueError as exc:
        assert "not pending" in str(exc)
    else:
        raise AssertionError("review must refuse already-reviewed input")
