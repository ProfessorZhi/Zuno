from __future__ import annotations

import argparse
import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json


REQUIRED_SYNTHETIC_METRICS = (
    "answer_exact_match",
    "answer_semantic_score",
    "recall_at_5",
    "context_precision_at_5",
    "hit_at_5",
    "citation_accuracy",
    "citation_completeness",
    "abstention_accuracy",
    "security_violation_rate",
    "unsupported_claim_rate",
    "profile_failure_rate",
    "resume_success_rate",
    "p50_latency",
    "p95_latency",
    "cost_per_case",
    "budget_overrun_rate",
)

DEFAULT_SYNTHETIC_THRESHOLDS = {
    "answer_exact_match": {"operator": ">=", "threshold": 0.60},
    "answer_semantic_score": {"operator": ">=", "threshold": 0.75},
    "recall_at_5": {"operator": ">=", "threshold": 0.70},
    "context_precision_at_5": {"operator": ">=", "threshold": 0.35},
    "hit_at_5": {"operator": ">=", "threshold": 0.70},
    "citation_accuracy": {"operator": ">=", "threshold": 0.85},
    "citation_completeness": {"operator": ">=", "threshold": 0.80},
    "abstention_accuracy": {"operator": ">=", "threshold": 0.80},
    "security_violation_rate": {"operator": "==", "threshold": 0.0},
    "unsupported_claim_rate": {"operator": "<=", "threshold": 0.10},
    "profile_failure_rate": {"operator": "<=", "threshold": 0.05},
    "resume_success_rate": {"operator": ">=", "threshold": 0.95},
    "p50_latency": {"operator": "<=", "threshold": 30_000},
    "p95_latency": {"operator": "<=", "threshold": 120_000},
    "cost_per_case": {"operator": "<=", "threshold": 0.25},
    "budget_overrun_rate": {"operator": "==", "threshold": 0.0},
}

ALLOWED_RELEASE_DECISIONS = ("PASSED", "FAILED", "BLOCKED", "INCOMPARABLE")


@dataclass
class SyntheticReleaseContractValidation:
    passed: bool
    errors: list[str] = field(default_factory=list)
    threshold_hash: str | None = None
    decision_hash: str | None = None


def build_threshold_set() -> dict[str, Any]:
    payload = {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "status": "FROZEN_BEFORE_RUNTIME",
        "metrics": copy.deepcopy(DEFAULT_SYNTHETIC_THRESHOLDS),
        "required_metric_names": list(REQUIRED_SYNTHETIC_METRICS),
        "runtime_results_bound": False,
        "notes": [
            "Thresholds are frozen before runtime metrics exist.",
            "Zero thresholds are permitted only for must-be-zero safety/failure rates.",
        ],
    }
    payload["threshold_hash"] = sha256_json(
        {key: value for key, value in payload.items() if key != "threshold_hash"}
    )
    return payload


def build_blocked_release_decision(threshold_set: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "status": "BLOCKED",
        "scope": "machine_attested_synthetic_regression",
        "reason_codes": [
            "runtime_metrics_missing",
            "four_profile_runs_missing",
            "snapshot_activation_missing",
        ],
        "threshold_hash": threshold_set.get("threshold_hash"),
        "runtime_metrics_ref": None,
        "profile_run_ids": [],
        "public_benchmark_claim": False,
        "production_release_claim": False,
    }
    payload["decision_hash"] = sha256_json(
        {key: value for key, value in payload.items() if key != "decision_hash"}
    )
    return payload


def validate_release_contract(
    threshold_set: dict[str, Any],
    release_decision: dict[str, Any],
) -> SyntheticReleaseContractValidation:
    errors: list[str] = []
    if threshold_set.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("threshold set track_id mismatch")
    if threshold_set.get("status") != "FROZEN_BEFORE_RUNTIME":
        errors.append("threshold set must be FROZEN_BEFORE_RUNTIME")
    metrics = threshold_set.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("threshold metrics must be an object")
        metrics = {}
    missing = sorted(set(REQUIRED_SYNTHETIC_METRICS) - set(metrics))
    if missing:
        errors.append(f"threshold metrics missing {missing}")
    numeric_thresholds: list[float] = []
    for metric_name in REQUIRED_SYNTHETIC_METRICS:
        spec = metrics.get(metric_name)
        if not isinstance(spec, dict):
            errors.append(f"{metric_name}: threshold spec must be an object")
            continue
        if spec.get("operator") not in {">=", "<=", "=="}:
            errors.append(f"{metric_name}: unsupported operator")
        threshold = spec.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            errors.append(f"{metric_name}: threshold must be numeric")
            continue
        if threshold < 0:
            errors.append(f"{metric_name}: threshold must be non-negative")
        numeric_thresholds.append(float(threshold))
    if numeric_thresholds and all(value == 0.0 for value in numeric_thresholds):
        errors.append("threshold set must not be all zero")

    expected_threshold_hash = sha256_json(
        {key: value for key, value in threshold_set.items() if key != "threshold_hash"}
    )
    if threshold_set.get("threshold_hash") != expected_threshold_hash:
        errors.append("threshold_hash mismatch")

    if release_decision.get("status") not in ALLOWED_RELEASE_DECISIONS:
        errors.append("release decision status is not in closed set")
    if release_decision.get("status") != "BLOCKED":
        errors.append("release decision must remain BLOCKED until runtime metrics exist")
    if release_decision.get("scope") != "machine_attested_synthetic_regression":
        errors.append("release decision scope mismatch")
    if release_decision.get("threshold_hash") != threshold_set.get("threshold_hash"):
        errors.append("release decision threshold_hash mismatch")
    if release_decision.get("runtime_metrics_ref") is not None:
        errors.append("blocked release decision must not reference runtime metrics")
    if release_decision.get("public_benchmark_claim") is not False:
        errors.append("release decision must not claim public benchmark")
    if release_decision.get("production_release_claim") is not False:
        errors.append("release decision must not claim production release")

    expected_decision_hash = sha256_json(
        {key: value for key, value in release_decision.items() if key != "decision_hash"}
    )
    if release_decision.get("decision_hash") != expected_decision_hash:
        errors.append("decision_hash mismatch")

    return SyntheticReleaseContractValidation(
        passed=not errors,
        errors=errors,
        threshold_hash=threshold_set.get("threshold_hash"),
        decision_hash=release_decision.get("decision_hash"),
    )


def write_release_contract(out_root: Path) -> dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    threshold_set = build_threshold_set()
    release_decision = build_blocked_release_decision(threshold_set)
    validation = validate_release_contract(threshold_set, release_decision)
    (out_root / "synthetic_threshold_set.json").write_text(
        json.dumps(threshold_set, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "synthetic_release_decision.json").write_text(
        json.dumps(release_decision, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "synthetic_release_contract_report.json").write_text(
        json.dumps(validation.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return validation.__dict__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    args = parser.parse_args()
    result = write_release_contract(args.out_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
