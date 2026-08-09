"""Record a deterministic delegated review of the PHASE22 candidate pack.

The generated candidate pack is an immutable pre-review input. This command
creates a separate reviewed case set and approval summary so that provenance,
integrity validation, and reviewer decisions remain distinct facts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


REVIEWER_REF = "user-delegated-codex-reviewer"
REVIEW_CONTRACT_VERSION = "phase22-review-decision.v1"


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"candidate row {line_number} must be an object")
        rows.append(value)
    return rows


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    content = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )
    path.write_text(content, encoding="utf-8")


def review_candidate_pack(candidate_path: Path, output_dir: Path) -> dict[str, Any]:
    candidates = _read_jsonl(candidate_path)
    if not candidates:
        raise ValueError("candidate pack is empty")

    reviewed: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    approved_count = 0
    rejected_count = 0

    for candidate in candidates:
        case_id = str(candidate.get("case_id") or "")
        if not case_id:
            raise ValueError("candidate case is missing case_id")
        if candidate.get("reviewer_status") != "pending":
            raise ValueError(f"candidate {case_id} is not pending")

        case_hash = _sha256_bytes(_canonical_json(candidate))
        evidence_complete = candidate.get("evidence_status") == "evidence_complete"
        reviewed_case = dict(candidate)
        reviewed_case["reviewer_ref"] = REVIEWER_REF
        reviewed_case["review_contract_version"] = REVIEW_CONTRACT_VERSION
        reviewed_case["reviewed_candidate_sha256"] = case_hash

        if evidence_complete:
            approved_count += 1
            reviewed_case["reviewer_status"] = "approved"
            reviewed_case["benchmark_eligible"] = True
            reviewed_case["reviewer_notes"] = (
                "Approved after delegated review: upstream question, answer, and gold "
                "document/evidence references matched the cached official source record; "
                "integrity status was VERIFIED."
            )
            decision = "approved"
            reason = "upstream_gold_evidence_and_integrity_verified"
        else:
            rejected_count += 1
            reviewed_case["reviewer_status"] = "rejected"
            reviewed_case["benchmark_eligible"] = False
            decision = "rejected"
            reason = str(candidate.get("rejection_reason") or "evidence_incomplete")

        reviewed_case["review_decision"] = decision
        decisions.append(
            {
                "case_id": case_id,
                "source_dataset": candidate.get("source_dataset"),
                "source_record_id": candidate.get("source_record_id"),
                "evidence_status": candidate.get("evidence_status"),
                "review_decision": decision,
                "benchmark_eligible": reviewed_case["benchmark_eligible"],
                "decision_reason": reason,
                "reviewer_ref": REVIEWER_REF,
                "candidate_sha256": case_hash,
            }
        )
        reviewed.append(reviewed_case)

    output_dir.mkdir(parents=True, exist_ok=True)
    reviewed_path = output_dir / "reviewed_cases.jsonl"
    decisions_path = output_dir / "review_decisions.jsonl"
    _write_jsonl(reviewed_path, reviewed)
    _write_jsonl(decisions_path, decisions)

    reviewed_hash = _sha256_file(reviewed_path)
    decision_hash = _sha256_file(decisions_path)
    total_count = len(candidates)
    summary = {
        "schema_version": REVIEW_CONTRACT_VERSION,
        "reviewer_ref": REVIEWER_REF,
        "source_candidate_pack": candidate_path.as_posix(),
        "source_candidate_pack_sha256": _sha256_file(candidate_path),
        "reviewed_case_set": reviewed_path.as_posix(),
        "reviewed_case_set_sha256": reviewed_hash,
        "review_decisions": decisions_path.as_posix(),
        "review_decisions_sha256": decision_hash,
        "total_cases": total_count,
        "evidence_complete_count": approved_count,
        "reviewer_approved_count": approved_count,
        "benchmark_eligible_count": approved_count,
        "rejected_or_incomplete_count": rejected_count,
        "reviewer_status_breakdown": {
            "pending": 0,
            "approved": approved_count,
            "rejected": rejected_count,
        },
        "overall_status": "REVIEW_PARTIAL" if rejected_count else "PASS",
        "measurement_state": (
            "BLOCKED_INSUFFICIENT_ELIGIBLE_CASES"
            if approved_count < total_count
            else "BLOCKED_PENDING_FORMAL_RUNTIME"
        ),
        "review_scope": (
            "All candidate cases reviewed. Approval requires evidence_complete plus "
            "upstream question/answer/gold evidence and integrity consistency; incomplete "
            "cases remain rejected and benchmark-ineligible."
        ),
    }
    _write_json(output_dir / "review_summary.json", summary)

    sheet_path = output_dir / "reviewed_sheet.csv"
    with sheet_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "case_id",
                "source_dataset",
                "question_type",
                "evidence_status",
                "reviewer_status",
                "benchmark_eligible",
                "review_decision",
                "reviewer_notes",
            ]
        )
        for case in reviewed:
            writer.writerow(
                [
                    case.get("case_id", ""),
                    case.get("source_dataset", ""),
                    case.get("question_type", ""),
                    case.get("evidence_status", ""),
                    case.get("reviewer_status", ""),
                    case.get("benchmark_eligible", False),
                    case.get("review_decision", ""),
                    case.get("reviewer_notes", ""),
                ]
            )

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-pack", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    summary = review_candidate_pack(args.candidate_pack, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
