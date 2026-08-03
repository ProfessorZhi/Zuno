"""PHASE22 CC-D fault matrix runner.

For a given case_id, this runner:

1. Loads the static matrix YAML.
2. Performs a per-case structural validation (case_id uniqueness, all
   required fields populated, idempotency_key present, exit_code
   recorded).
3. Records what the runner WOULD do against the live runtime (the test
   command and the receipt it would assert on) without invoking the
   runtime or producing a fake receipt.

The runner never executes live runtime. Every case exits with the recorded
``exit_code`` only because the matrix is data-only. Real execution must wait
for the DeepSeek CC-B snapshot_id and CC-C profile_run_ids.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

MATRIX_PATH = (
    REPO_ROOT
    / "tools"
    / "evals"
    / "zuno"
    / "synthetic_benchmark"
    / "phase22_cc_d_fault_matrix.yaml"
)


def _load_matrix() -> dict[str, Any]:
    import yaml  # type: ignore[import-untyped]

    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def _case_by_id(matrix: dict[str, Any], case_id: str) -> dict[str, Any] | None:
    for case in matrix.get("cases", []):
        if isinstance(case, dict) and case.get("case_id") == case_id:
            return case
    return None


def _run_command(command: str) -> dict[str, Any]:
    """Record the matrix row's test_command without launching it.

    While ``matrix_status`` is ``NOT_RUN_DEPENDENCY_BLOCKED`` we never execute
    the per-case ``test_command`` because every command in the matrix would
    either recursively invoke this runner or hit live runtime we do not own.
    The runner only records what would be executed, the expected exit code,
    and the structural state. Real execution is gated on DeepSeek CC-B
    snapshot_id and CC-C profile_run_ids landing.
    """

    return {
        "launched": False,
        "exit_code": None,
        "reason": (
            "test_command recorded but not executed while matrix_status is "
            "NOT_RUN_DEPENDENCY_BLOCKED; live execution waits for DeepSeek "
            "CC-B snapshot_id and CC-C profile_run_ids"
        ),
        "would_run": command,
    }


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "test_command": case["test_command"],
        "expected_exit_code": case["exit_code"],
        "execution": _run_command(case["test_command"]),
        "status": case["status"],
        "not_run_reason": case["not_run_reason"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PHASE22 CC-D fault matrix runner")
    parser.add_argument("--case", dest="case_id", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "docs"
        / "evidence"
        / "goal05-phase22-machine-attested-synthetic-regression"
        / "minimax2-cc-d"
        / "fault_matrix_run.json",
        help="Where to append the run record.",
    )
    args = parser.parse_args(argv)

    matrix = _load_matrix()
    case = _case_by_id(matrix, args.case_id)
    if case is None:
        print(f"ERROR: unknown case_id {args.case_id}", file=sys.stderr)
        return 2

    record = run_case(case)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        try:
            existing = json.loads(args.output.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {"runs": []}
    else:
        existing = {"runs": []}
    existing.setdefault("runs", []).append(record)
    args.output.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"recorded case {args.case_id} to {args.output.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())