"""PHASE22 Release Decision Engine CLI.

The CLI is intentionally minimal and fail-closed:

* It only loads a JSON Mapping input file, evaluates the deterministic
  Release Decision, and writes the JSON output file.
* It does not import ``runtime_evidence_binding`` or ``benchmark_preflight``.
* It never prints tracebacks, raw OS errors, or absolute paths. Failures are
  reported as a deterministic ``ReleaseDecision`` with status ``BLOCKED`` /
  ``ERROR`` along with a closed-set reason code.

Reproduce command template is part of the public output so that the same
input always produces byte-identical results.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.evals.zuno.rag_eval.paths import REPO_ROOT
from tools.evals.zuno.rag_eval.release_decision import (
    BLOCKED_REASONS,
    ERROR_REASONS,
    REPRODUCE_COMMAND_TEMPLATE,
    ReleaseDecision,
    ReleaseDecisionError,
    ReleaseDecisionStatus,
    evaluate_release_decision,
)


def _read_input(path: Path) -> Any:
    if not path.exists():
        return {"__cli_error__": "missing_input_path"}
    if not path.is_file():
        return {"__cli_error__": "missing_input_path"}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {"__cli_error__": "input_unreadable"}
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return {"__cli_error__": "input_unreadable"}


def _write_output(path: Path, payload: dict[str, Any]) -> str | None:
    if path.exists() and path.is_dir():
        return "output_unwritable"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=False), encoding="utf-8")
    except OSError:
        return "output_unwritable"
    return None


def _blocked_cli_decision(reason: str) -> ReleaseDecision:
    decision = evaluate_release_decision(
        {
            "profiles": {},
            "comparability_fingerprint": _placeholder_fingerprint(),
        }
    )
    # The structured evaluation will return ERROR for an empty input;
    # we override with a CLI-specific BLOCKED status with closed reasons.
    from dataclasses import replace

    if reason in BLOCKED_REASONS:
        return replace(
            decision,
            status=ReleaseDecisionStatus.BLOCKED,
            reason_codes=(reason,),
        )
    if reason in ERROR_REASONS:
        return replace(
            decision,
            status=ReleaseDecisionStatus.ERROR,
            reason_codes=(reason,),
        )
    raise ReleaseDecisionError(f"unknown cli reason: {reason}")


def _placeholder_fingerprint() -> dict[str, str | None]:
    return {
        "dataset_version": "cli-placeholder-v0",
        "case_set_hash": "cli-placeholder-v0",
        "corpus_snapshot": "cli-placeholder-v0",
        "knowledge_snapshot": "cli-placeholder-v0",
        "graph_snapshot": None,
        "model_profile": "cli-placeholder-v0",
        "judge_policy": "cli-placeholder-v0",
        "embedding_profile": "cli-placeholder-v0",
        "metric_definition": "cli-placeholder-v0",
        "runtime_profile": "cli-placeholder-v0",
        "security_scope": "cli-placeholder-v0",
        "budget_class": "cli-placeholder-v0",
    }


def run_cli(
    *,
    input_path: Path,
    output_path: Path,
    writer=_write_output,
) -> int:
    raw = _read_input(input_path)
    if isinstance(raw, dict) and raw.get("__cli_error__") == "missing_input_path":
        blocked = _blocked_cli_decision("missing_input_path")
        decision_dict = blocked.to_dict()
        decision_dict["cli_input_path"] = str(input_path)
        decision_dict["cli_output_path"] = str(output_path)
        decision_dict["reproduce_command_template"] = REPRODUCE_COMMAND_TEMPLATE
        write_error = writer(output_path, {"release_decision": decision_dict})
        return 2
    if isinstance(raw, dict) and raw.get("__cli_error__") == "input_unreadable":
        blocked = _blocked_cli_decision("input_unreadable")
        decision_dict = blocked.to_dict()
        decision_dict["cli_input_path"] = str(input_path)
        decision_dict["cli_output_path"] = str(output_path)
        decision_dict["reproduce_command_template"] = REPRODUCE_COMMAND_TEMPLATE
        write_error = writer(output_path, {"release_decision": decision_dict})
        return 2
    try:
        decision = evaluate_release_decision(raw)
    except ReleaseDecisionError:
        decision = _blocked_cli_decision("decision_input_invalid")
    decision_dict = decision.to_dict()
    decision_dict["cli_input_path"] = str(input_path)
    decision_dict["cli_output_path"] = str(output_path)
    decision_dict["reproduce_command_template"] = REPRODUCE_COMMAND_TEMPLATE
    write_error = writer(output_path, {"release_decision": decision_dict})
    if write_error is not None:
        # Writing the output failed — return a deterministic non-zero exit
        # without leaking tracebacks or absolute paths to stdout/stderr.
        return 3
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase22 Benchmark Comparison and Release Decision Engine."
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        required=True,
        help="Path to the JSON Mapping input describing the four profile manifests.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        required=True,
        help="Path where the immutable evidence pack JSON will be written.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_cli(input_path=args.input_json, output_path=args.output_json)


if __name__ == "__main__":
    raise SystemExit(main())
