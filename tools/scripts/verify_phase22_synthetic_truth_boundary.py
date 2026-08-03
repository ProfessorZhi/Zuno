from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_EVIDENCE_DIR = Path("docs/evidence/goal05-phase22-synthetic-benchmark")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_phase22_synthetic_truth_boundary(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    evidence_dir = repo_root / SYNTHETIC_EVIDENCE_DIR
    if not evidence_dir.exists():
        return errors

    invalidation = evidence_dir / "INVALIDATION_NOTICE.md"
    if not invalidation.exists():
        errors.append(
            "synthetic PHASE22 benchmark evidence must include INVALIDATION_NOTICE.md "
            "unless it has passed Coordinator review and is no longer derived from PR #100"
        )

    release_decision = evidence_dir / "release_decision.json"
    if release_decision.exists():
        release = _read_json(release_decision)
        if release.get("verdict") == "PASSED":
            errors.append("synthetic PHASE22 release_decision.json must not claim PASSED")
        thresholds = release.get("thresholds")
        if isinstance(thresholds, dict) and thresholds:
            zero_thresholds = [
                name for name, value in thresholds.items() if isinstance(value, (int, float)) and value <= 0
            ]
            if zero_thresholds:
                errors.append(
                    "synthetic PHASE22 release_decision.json must not use zero-or-lower release thresholds: "
                    + ", ".join(sorted(zero_thresholds))
                )

    core_five = evidence_dir / "core_five_metrics.json"
    if core_five.exists():
        metrics = _read_json(core_five)
        measured_profiles = [
            profile
            for profile, payload in metrics.items()
            if isinstance(payload, dict) and payload.get("measurement_state") == "MEASURED"
        ]
        if measured_profiles:
            errors.append(
                "synthetic PHASE22 core_five_metrics.json must not mark profiles MEASURED: "
                + ", ".join(sorted(measured_profiles))
            )

    runtime_ingestion = evidence_dir / "runtime_ingestion.json"
    if runtime_ingestion.exists():
        ingestion = _read_json(runtime_ingestion)
        index_evidence = ingestion.get("index_construction_evidence")
        if isinstance(index_evidence, dict):
            submitted = []
            for index_name, payload in index_evidence.items():
                if isinstance(payload, dict) and payload.get("ingestion_status") == "submitted":
                    submitted.append(index_name)
            if submitted:
                errors.append(
                    "synthetic PHASE22 runtime_ingestion.json must not treat submitted index jobs as canonical "
                    "write/read-back proof: " + ", ".join(sorted(submitted))
                )

    return errors


def main() -> int:
    errors = verify_phase22_synthetic_truth_boundary()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE22 synthetic truth boundary gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
