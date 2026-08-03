"""PHASE22 CC-D evidence verifier.

Validates that the CC-D evidence bundle and matrix loader stay honest:

* Every matrix row has all required fields.
* All rows are ``NOT_RUN_DEPENDENCY_BLOCKED`` while
  ``snapshot_id`` / ``profile_run_ids`` are placeholders.
* No row carries a forged ``receipt_ref`` or ``trace_ref``.
* The evidence bundle has no secret-like patterns.
* The environment probe does not claim write/read verified.
* Required counters line up.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

EVIDENCE_DIR = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "minimax2-cc-d"
)
BUNDLE_PATH = EVIDENCE_DIR / "evidence_bundle.json"
ENV_PROBE_PATH = EVIDENCE_DIR / "environment_probe.json"
FAULT_RUN_PATH = EVIDENCE_DIR / "fault_matrix_run.json"

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)postgres:postgres@"),
    re.compile(r"(?i)neo4j/neo4j12345"),
    re.compile(r"(?i)minioadmin:minioadmin"),
    re.compile(r"(?i)guest:guest@"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{16,}"),
)


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _scan_text_for_secrets(text: str) -> list[str]:
    return [p.pattern for p in SECRET_PATTERNS if p.search(text)]


def verify() -> list[str]:
    import yaml  # type: ignore[import-untyped]

    errors: list[str] = []

    matrix_path = (
        REPO_ROOT
        / "tools"
        / "evals"
        / "zuno"
        / "synthetic_benchmark"
        / "phase22_cc_d_fault_matrix.yaml"
    )
    matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))
    cases = [c for c in matrix.get("cases", []) if isinstance(c, dict)]
    if len(cases) < 22:
        errors.append(f"matrix must define at least 22 cases, found {len(cases)}")

    case_ids = [str(c.get("case_id", "")) for c in cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append("matrix case_ids must be unique")

    required_fields = {
        "case_id",
        "trigger",
        "state_before",
        "state_after",
        "owner",
        "failure_class",
        "propagation",
        "retryability",
        "recovery",
        "idempotency_key",
        "receipt_ref",
        "trace_ref",
        "test_command",
        "exit_code",
        "cleanup",
        "status",
        "not_run_reason",
    }
    for case in cases:
        missing = required_fields - set(case.keys())
        if missing:
            errors.append(
                f"case {case.get('case_id', '<unknown>')} missing required fields: {sorted(missing)}"
            )

    matrix_state = matrix.get("matrix_status")
    if matrix_state != "NOT_RUN_DEPENDENCY_BLOCKED":
        errors.append(
            f"matrix_status must remain NOT_RUN_DEPENDENCY_BLOCKED until DeepSeek CC-B/CC-C deliver, got {matrix_state!r}"
        )
    if matrix.get("snapshot_id") is not None:
        errors.append("snapshot_id must remain null while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED")
    if matrix.get("profile_run_ids") not in (None, [], ()):
        errors.append("profile_run_ids must remain empty while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED")

    for case in cases:
        if case.get("status") == "PASSED":
            errors.append(
                f"case {case.get('case_id')} must not be PASSED while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED"
            )
        if case.get("receipt_ref") is not None:
            errors.append(
                f"case {case.get('case_id')} must not carry receipt_ref while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED"
            )
        if case.get("trace_ref") is not None:
            errors.append(
                f"case {case.get('case_id')} must not carry trace_ref while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED"
            )

    for path in (BUNDLE_PATH, ENV_PROBE_PATH, FAULT_RUN_PATH):
        if not path.exists():
            errors.append(f"missing evidence artifact: {path.relative_to(REPO_ROOT).as_posix()}")

    bundle = _read_json(BUNDLE_PATH) or {}
    if bundle:
        if bundle.get("matrix_status") != "NOT_RUN_DEPENDENCY_BLOCKED":
            errors.append("evidence bundle matrix_status must be NOT_RUN_DEPENDENCY_BLOCKED")
        if bundle.get("case_count") != len(cases):
            errors.append("evidence bundle case_count mismatch")
        for run in bundle.get("case_runs", []) or []:
            if run.get("recorded_run", {}).get("status") == "PASSED":
                errors.append(
                    f"evidence bundle run for {run.get('case_id')} must not be PASSED"
                )
        secret_hits = _scan_text_for_secrets(json.dumps(bundle, ensure_ascii=False))
        if secret_hits:
            errors.append(
                "evidence bundle leaks secret-like patterns: " + ", ".join(secret_hits)
            )

    probe = _read_json(ENV_PROBE_PATH) or {}
    if probe:
        for service in probe.get("services", []) or []:
            if service.get("service_write_read_verified") is True:
                errors.append(
                    f"environment probe must not claim write/read verified for {service.get('id')}"
                )
        secret_hits = _scan_text_for_secrets(json.dumps(probe, ensure_ascii=False))
        if secret_hits:
            errors.append(
                "environment probe leaks secret-like patterns: " + ", ".join(secret_hits)
            )

    fault_run = _read_json(FAULT_RUN_PATH) or {}
    if fault_run:
        secret_hits = _scan_text_for_secrets(json.dumps(fault_run, ensure_ascii=False))
        if secret_hits:
            errors.append(
                "fault matrix run leaks secret-like patterns: " + ", ".join(secret_hits)
            )

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE22 CC-D evidence verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())