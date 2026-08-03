from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

TRACK_DIR = Path(
    "docs/evidence/goal05-phase22-machine-attested-synthetic-regression"
)
TRACK_MANIFEST = TRACK_DIR / "track_manifest.json"
READINESS_REPORT = TRACK_DIR / "readiness-report.md"
PUBLIC_APPROVAL_SUMMARY = Path(
    "docs/evidence/goal05-phase22-public-benchmark-review-pack/approval_summary.json"
)
PUBLIC_INTEGRITY_REPORT = Path(
    "docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json"
)
INVALIDATION_NOTICE = Path(
    "docs/evidence/goal05-phase22-synthetic-benchmark/INVALIDATION_NOTICE.md"
)
TASK_CARDS = [
    Path(".agent/programs/thread-prompts/CC-A-phase22-dataset-corpus-derivation-validator.md"),
    Path(".agent/programs/thread-prompts/CC-B-phase22-canonical-ingestion-three-indexes.md"),
    Path(".agent/programs/thread-prompts/CC-C-phase22-four-profile-runtime-benchmark.md"),
    Path(".agent/programs/thread-prompts/CC-D-phase22-integration-fault-security-evidence.md"),
]


def _read_text(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read_text(path))


def verify_phase22_synthetic_regression_track() -> list[str]:
    errors: list[str] = []
    required_files = [
        TRACK_MANIFEST,
        READINESS_REPORT,
        PUBLIC_APPROVAL_SUMMARY,
        PUBLIC_INTEGRITY_REPORT,
        INVALIDATION_NOTICE,
        *TASK_CARDS,
    ]
    for path in required_files:
        if not (REPO_ROOT / path).exists():
            errors.append(f"missing required synthetic regression track file: {path.as_posix()}")
    if errors:
        return errors

    manifest = _read_json(TRACK_MANIFEST)
    approval = _read_json(PUBLIC_APPROVAL_SUMMARY)
    integrity = _read_json(PUBLIC_INTEGRITY_REPORT)
    report = _read_text(READINESS_REPORT)
    invalidation = _read_text(INVALIDATION_NOTICE)

    if manifest.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("track_manifest track_id must be machine_attested_synthetic_regression")
    if manifest.get("status") != "BLOCKED_WITH_EXACT_GAPS":
        errors.append("track_manifest must remain BLOCKED_WITH_EXACT_GAPS until full runtime evidence exists")
    decision = manifest.get("synthetic_release_decision", {})
    if decision.get("scope") != "machine_attested_synthetic_regression":
        errors.append("synthetic release decision must be scoped to machine_attested_synthetic_regression")
    if decision.get("status") != "BLOCKED":
        errors.append("synthetic release decision must remain BLOCKED before runtime execution")

    boundary = manifest.get("synthetic_public_boundary", {})
    for field in ["reviewer_approved_count", "benchmark_eligible_count"]:
        if approval.get(field) != 0 or integrity.get(field) != 0 or boundary.get(field) != 0:
            errors.append(f"public benchmark {field} must remain 0 for synthetic track")
    for field in ["machine_attested_count", "synthetic_regression_eligible_count"]:
        if field not in boundary:
            errors.append(f"synthetic boundary missing independent field: {field}")

    required_report_phrases = [
        "status: BLOCKED_WITH_EXACT_GAPS",
        "PHASE22：`in_progress`",
        "Production Readiness：not established",
        "Public Benchmark：`reviewer_approved_count=0`",
        "PR #100",
        "PR #104",
        "PR #105",
    ]
    for phrase in required_report_phrases:
        if phrase not in report:
            errors.append(f"readiness report missing phrase: {phrase}")

    for phrase in ["INVALIDATED", "canonical_runtime_not_executed", "SUCCESS_REAL_INGESTION"]:
        if phrase not in invalidation:
            errors.append(f"synthetic invalidation notice missing phrase: {phrase}")

    required_card_fields = [
        "WORKER_TASK_ID",
        "Base SHA",
        "Goal",
        "Current Gap",
        "Allowed Paths",
        "Forbidden Paths",
        "Contracts",
        "Owner",
        "State Transitions",
        "Failure Semantics",
        "Retry / Recovery / Idempotency",
        "Security",
        "Required Tests",
        "Acceptance Criteria",
        "Commit Contract",
        "Handoff Format",
    ]
    for card in TASK_CARDS:
        text = _read_text(card)
        for field in required_card_fields:
            if field not in text:
                errors.append(f"{card.as_posix()} missing task-card field: {field}")

    return errors


def main() -> int:
    errors = verify_phase22_synthetic_regression_track()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE22 synthetic regression track boundary passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
