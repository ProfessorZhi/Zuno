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
PR100_FILE_CLASSIFICATION = TRACK_DIR / "pr100-file-classification.json"
SEED_DATASET_MANIFEST = TRACK_DIR / "seed-dataset" / "seed_dataset_manifest.json"
CANDIDATE_DATASET_MANIFEST = TRACK_DIR / "candidate-dataset" / "candidate_dataset_manifest.json"
CANDIDATE_DERIVATION_REPORT = TRACK_DIR / "candidate-dataset" / "candidate_derivation_report.json"
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
        PR100_FILE_CLASSIFICATION,
        SEED_DATASET_MANIFEST,
        CANDIDATE_DATASET_MANIFEST,
        CANDIDATE_DERIVATION_REPORT,
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
    pr100_classification = _read_json(PR100_FILE_CLASSIFICATION)
    seed_manifest = _read_json(SEED_DATASET_MANIFEST)
    candidate_manifest = _read_json(CANDIDATE_DATASET_MANIFEST)
    derivation_report = _read_json(CANDIDATE_DERIVATION_REPORT)
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
    if boundary.get("machine_attested_count") != candidate_manifest.get("case_count"):
        errors.append("machine_attested_count must match candidate dataset case_count")
    if boundary.get("synthetic_regression_eligible_count") != 0:
        errors.append("synthetic_regression_eligible_count must remain 0 until full 80 is valid")
    if seed_manifest.get("status") != "PARTIAL_SEED_VALIDATED":
        errors.append("seed dataset manifest must be PARTIAL_SEED_VALIDATED")
    if seed_manifest.get("runtime_eligible") is not False:
        errors.append("seed dataset must not be runtime eligible")
    if seed_manifest.get("synthetic_regression_eligible") is not False:
        errors.append("seed dataset must not be synthetic regression eligible")
    if candidate_manifest.get("status") != "FULL_80_CANDIDATE_VALIDATED":
        errors.append("candidate dataset manifest must be FULL_80_CANDIDATE_VALIDATED")
    if candidate_manifest.get("case_count") != 80:
        errors.append("candidate dataset case_count must be 80")
    if candidate_manifest.get("runtime_eligible") is not False:
        errors.append("candidate dataset must not be runtime eligible before ingestion")
    if candidate_manifest.get("synthetic_regression_eligible") is not False:
        errors.append("candidate dataset must not be synthetic regression eligible before runtime")
    if derivation_report.get("case_count") != 80:
        errors.append("candidate derivation report case_count must be 80")
    if derivation_report.get("derivation_valid_count") != 80:
        errors.append("candidate derivation report derivation_valid_count must be 80")
    if derivation_report.get("source_evidence_valid_count") != 80:
        errors.append("candidate derivation report source_evidence_valid_count must be 80")
    if derivation_report.get("unsupported_answer_count") != 0:
        errors.append("candidate derivation report unsupported_answer_count must be 0")
    if derivation_report.get("duplicate_question_count") != 0:
        errors.append("candidate derivation report duplicate_question_count must be 0")
    if derivation_report.get("gold_leakage_count") != 0:
        errors.append("candidate derivation report gold_leakage_count must be 0")
    if derivation_report.get("hard_negative_valid_count") != 5:
        errors.append("candidate derivation report hard_negative_valid_count must be 5")
    if derivation_report.get("hash_valid_count") != 80:
        errors.append("candidate derivation report hash_valid_count must be 80")
    current_evidence = manifest.get("current_evidence", {})
    report_field_pairs = {
        "candidate_derivation_valid_count": "derivation_valid_count",
        "candidate_source_evidence_valid_count": "source_evidence_valid_count",
        "candidate_unsupported_answer_count": "unsupported_answer_count",
        "candidate_duplicate_question_count": "duplicate_question_count",
        "candidate_gold_leakage_count": "gold_leakage_count",
        "candidate_hard_negative_valid_count": "hard_negative_valid_count",
        "candidate_hash_valid_count": "hash_valid_count",
    }
    for manifest_field, report_field in report_field_pairs.items():
        if current_evidence.get(manifest_field) != derivation_report.get(report_field):
            errors.append(f"track_manifest {manifest_field} must match derivation report {report_field}")
    if current_evidence.get("candidate_derivation_report_hash") != derivation_report.get("report_hash"):
        errors.append("track_manifest candidate_derivation_report_hash must match derivation report")

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

    files_by_path = {
        item.get("path"): item.get("classification")
        for item in pr100_classification.get("files", [])
        if isinstance(item, dict)
    }
    required_classifications = {
        "docs/evidence/goal05-phase22-synthetic-benchmark/build_world_model.py": "ACCEPT_AFTER_REWORK",
        "docs/evidence/goal05-phase22-synthetic-benchmark/build_cases.py": "ACCEPT_AFTER_REWORK",
        "docs/evidence/goal05-phase22-synthetic-benchmark/synthetic_cases.jsonl": "ACCEPT_AFTER_REWORK",
        "docs/evidence/goal05-phase22-synthetic-benchmark/ingest_and_run.py": "DROP",
        "docs/evidence/goal05-phase22-synthetic-benchmark/profile_results/*.json": "DROP",
        "docs/evidence/goal05-phase22-synthetic-benchmark/release_decision.json": "DROP",
        "docs/evidence/goal05-phase22-synthetic-benchmark/runtime_ingestion.json": "DROP",
    }
    for path, expected in required_classifications.items():
        if files_by_path.get(path) != expected:
            errors.append(
                f"PR100 file classification for {path} must be {expected}, got {files_by_path.get(path)!r}"
            )

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
