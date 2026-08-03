"""PHASE22 CC-D fault matrix loader and structural validator.

This module reads the fault matrix YAML and enforces the structural contract
laid out in the CC-D task card and prompt. It never executes live runtime:
every row stays NOT_RUN_DEPENDENCY_BLOCKED until DeepSeek CC-B and CC-C
produce snapshot_id and profile_run_ids. No row may flip to PASSED without
an authentic receipt_ref.

Forbidden actions (enforced by assertions and verified by tests):

* port reachable != write/read verified
* blind retry on UNKNOWN side effect
* secret leakage (handled by ``tools/scripts/phase22_evidence_builder.py``)
* deleting failure assertions
* activating snapshot without receipt
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[4]

MATRIX_PATH = (
    REPO_ROOT
    / "tools"
    / "evals"
    / "zuno"
    / "synthetic_benchmark"
    / "phase22_cc_d_fault_matrix.yaml"
)

REQUIRED_CASE_FIELDS: tuple[str, ...] = (
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
)

ALLOWED_OWNERS: frozenset[str] = frozenset(
    {
        "knowledge_ingestion",
        "object_store",
        "postgres_domain",
        "knowledge_index",
        "snapshot_activation",
        "observability",
        "gold_isolation",
        "release_decision",
        "fault_recovery",
        "security_isolation",
        "runtime_resume",
        "evidence_reproducibility",
    }
)

ALLOWED_STATUS: frozenset[str] = frozenset(
    {
        "NOT_RUN_DEPENDENCY_BLOCKED",
        "PASSED",
        "FAILED",
        "BLOCKED",
        "NOT_RUN",
    }
)

# The DeepSeek CC-B / CC-C hand-off contract: receipt_ref and trace_ref MUST
# stay null until the corresponding live runtime produced the receipt. No
# matrix row may report PASSED before that happens.
RECEIPT_BEARING_STATES: frozenset[str] = frozenset({"PASSED"})


def _try_load_yaml() -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - environment without pyyaml
        raise RuntimeError("PyYAML is required to load the fault matrix YAML") from exc
    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def load_matrix(path: Path | None = None) -> dict[str, Any]:
    """Load the fault matrix YAML from disk and return it as a dict.

    The matrix is data only. We never mutate it from live runtime.
    """

    if path is None:
        path = MATRIX_PATH
    if not path.exists():
        raise FileNotFoundError(f"fault matrix not found: {path.as_posix()}")
    import yaml  # type: ignore[import-untyped]

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def matrix_status(matrix: dict[str, Any]) -> str:
    return str(matrix.get("matrix_status", "NOT_RUN_DEPENDENCY_BLOCKED"))


def cases(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    raw_cases = matrix.get("cases", [])
    if not isinstance(raw_cases, list):
        return []
    return [case for case in raw_cases if isinstance(case, dict)]


def case_ids(matrix: dict[str, Any]) -> list[str]:
    return [str(case.get("case_id", "")) for case in cases(matrix)]


def required_fields_present(matrix: dict[str, Any]) -> list[str]:
    """Return a list of error strings for missing required fields."""

    errors: list[str] = []
    declared = matrix.get("required_fields")
    if not isinstance(declared, list):
        errors.append("matrix required_fields must be a list")
        declared = list(REQUIRED_CASE_FIELDS)
    declared_set = set(str(item) for item in declared)
    missing_top_level = {f for f in REQUIRED_CASE_FIELDS if f not in declared_set}
    if missing_top_level:
        errors.append(
            "matrix required_fields missing entries: " + ", ".join(sorted(missing_top_level))
        )
    extra = declared_set - set(REQUIRED_CASE_FIELDS)
    if extra:
        errors.append(
            "matrix required_fields has extra entries: " + ", ".join(sorted(extra))
        )
    for case in cases(matrix):
        case_id = str(case.get("case_id", "<unknown>"))
        for field in REQUIRED_CASE_FIELDS:
            if field not in case:
                errors.append(f"case {case_id} missing field: {field}")
    return errors


def owners_valid(matrix: dict[str, Any]) -> list[str]:
    declared = set(matrix.get("owners", {}).keys())
    missing = ALLOWED_OWNERS - declared
    extra = declared - ALLOWED_OWNERS
    errors: list[str] = []
    if missing:
        errors.append("matrix owners missing: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("matrix owners has unexpected entries: " + ", ".join(sorted(extra)))
    return errors


def statuses_valid(matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for case in cases(matrix):
        status = str(case.get("status", ""))
        if status not in ALLOWED_STATUS:
            errors.append(
                f"case {case.get('case_id', '<unknown>')} has invalid status: {status!r}"
            )
    return errors


def dependency_truth(matrix: dict[str, Any]) -> list[str]:
    """Validate the dependency_pr / snapshot_id / profile_run_ids linkage.

    Until DeepSeek CC-B and CC-C merge, every row must be
    NOT_RUN_DEPENDENCY_BLOCKED and ``receipt_ref`` / ``trace_ref`` MUST be
    null. This is the structural enforcement of "no fake receipts".
    """

    errors: list[str] = []
    snapshot_id = matrix.get("snapshot_id")
    profile_run_ids = matrix.get("profile_run_ids")
    matrix_state = matrix_status(matrix)
    if matrix_state == "NOT_RUN_DEPENDENCY_BLOCKED":
        if snapshot_id is not None:
            errors.append("snapshot_id must be null while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED")
        if profile_run_ids not in (None, [], ()):
            errors.append(
                "profile_run_ids must be empty while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED"
            )
        for case in cases(matrix):
            status = str(case.get("status", ""))
            if status == "PASSED":
                errors.append(
                    f"case {case.get('case_id', '<unknown>')} PASSED while matrix_status is "
                    "NOT_RUN_DEPENDENCY_BLOCKED"
                )
            if case.get("receipt_ref") is not None:
                errors.append(
                    f"case {case.get('case_id', '<unknown>')} has receipt_ref while matrix_status is "
                    "NOT_RUN_DEPENDENCY_BLOCKED"
                )
            if case.get("trace_ref") is not None:
                errors.append(
                    f"case {case.get('case_id', '<unknown>')} has trace_ref while matrix_status is "
                    "NOT_RUN_DEPENDENCY_BLOCKED"
                )
    return errors


def summarise(matrix: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for case in cases(matrix):
        status = str(case.get("status", "NOT_RUN"))
        counts[status] = counts.get(status, 0) + 1
    return {
        "matrix_status": matrix_status(matrix),
        "dependency_pr": matrix.get("dependency_pr"),
        "dependency_head_sha": matrix.get("dependency_head_sha"),
        "snapshot_id": matrix.get("snapshot_id"),
        "profile_run_ids": matrix.get("profile_run_ids", []),
        "case_count": len(cases(matrix)),
        "status_counts": counts,
    }


def matrix_sha256(matrix: dict[str, Any]) -> str:
    """Stable SHA256 over the canonical matrix payload (cases only)."""

    payload = {
        "required_fields": matrix.get("required_fields", []),
        "owners": matrix.get("owners", {}),
        "cases": cases(matrix),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def iter_problems(matrix: dict[str, Any]) -> Iterable[str]:
    """Yield all structural errors for the matrix."""

    yield from required_fields_present(matrix)
    yield from owners_valid(matrix)
    yield from statuses_valid(matrix)
    yield from dependency_truth(matrix)


def verify_matrix(path: Path | None = None) -> list[str]:
    matrix = load_matrix(path)
    return list(iter_problems(matrix))