"""PHASE22 Release Decision Engine CLI.

The CLI is intentionally minimal and fail-closed:

* It only loads a JSON Mapping input file, evaluates the deterministic
  Release Decision, and writes the JSON output file.
* It does not import ``runtime_evidence_binding`` or ``benchmark_preflight``.
* It never prints tracebacks, raw OS errors, or absolute paths to the user.
* Failures are reported as a deterministic ``ReleaseDecision`` with status
  ``BLOCKED`` or ``ERROR`` along with a closed-set reason code. The exit
  code matches the documented Exit Code Contract:

  * 0 -- PASSED
  * 1 -- FAILED
  * 2 -- BLOCKED
  * 3 -- INCOMPARABLE
  * 4 -- ERROR or CLI read/write/parse failure

  The output JSON contains the canonical input hash, decision hash, profile
  hashes, gate results, evidence refs, reproduce command template and the
  computed ``exit_code`` so that downstream tools can rely on either the
  numeric exit code or the value in the evidence pack.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.evals.zuno.rag_eval.release_decision import (
    DECISION_ENGINE_VERSION,
    EXIT_CODE_BY_STATUS,
    ReleaseDecision,
    ReleaseDecisionError,
    ReleaseDecisionStatus,
    REPRODUCE_COMMAND_TEMPLATE,
    evaluate_release_decision,
    exit_code_for,
)


class _CliReadFailure(LookupError):
    """Raised internally by ``run_cli`` when the input JSON cannot be read."""


def _read_input(path: Path) -> Any:
    """Return the parsed JSON input, or raise ``_CliReadFailure``."""
    if not path.exists() or not path.is_file():
        raise _CliReadFailure("missing_input_path")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        raise _CliReadFailure("input_unreadable") from None
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        raise _CliReadFailure("input_unreadable") from None


def _write_output(path: Path, payload: dict[str, Any]) -> None:
    """Persist the evidence pack; raise OSError on failure."""
    if path.exists() and path.is_dir():
        raise OSError("output path is a directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=False),
        encoding="utf-8",
    )


def _blocked_decision_for(reason: str, decision_engine_version: str) -> ReleaseDecision:
    """Build a small BLOCKED decision for CLI I/O failures without invoking
    the full evaluation.  The decision uses the same version / closed-set
    contract but is byte-deterministic given the same reason code."""
    from tools.evals.zuno.rag_eval.release_decision import (  # local import to avoid cycles
        CLOSED_SET_VERSION,
        GateFailure,
        canonical_sha256,
    )

    canonical_input_hash = canonical_sha256({"cli_blocked_reason": reason})
    payload = {
        "canonical_input_hash": canonical_input_hash,
        "decision_engine_version": decision_engine_version,
        "closed_set_version": CLOSED_SET_VERSION,
        "status": ReleaseDecisionStatus.BLOCKED.value,
        "reason_codes": [reason],
        "profile_hashes": {},
        "comparability_fingerprint_hash": canonical_sha256({}),
        "gate_results": [
            GateFailure(
                gate="cli_io",
                reason=reason,
                profile_id=None,
                metric=None,
                detail_kind="cli_io",
            ).to_dict(),
        ],
        "evidence_refs": [],
        "exit_code": EXIT_CODE_BY_STATUS[ReleaseDecisionStatus.BLOCKED],
    }
    decision_hash = canonical_sha256(payload)
    return ReleaseDecision(
        status=ReleaseDecisionStatus.BLOCKED,
        reason_codes=(reason,),
        canonical_input_hash=canonical_input_hash,
        decision_hash=decision_hash,
        profile_hashes={},
        comparability_fingerprint_hash=canonical_sha256({}),
        gate_results=(
            GateFailure(
                gate="cli_io",
                reason=reason,
                profile_id=None,
                metric=None,
                detail_kind="cli_io",
            ),
        ),
        evidence_refs=(),
        reproduce_command_template=REPRODUCE_COMMAND_TEMPLATE,
        decision_engine_version=decision_engine_version,
        closed_set_version=CLOSED_SET_VERSION,
    )


def _to_evidence_pack(decision: ReleaseDecision) -> dict[str, Any]:
    return {"release_decision": decision.to_dict()}


def run_cli(
    *,
    input_path: Path,
    output_path: Path,
) -> int:
    """Execute the CLI. Returns the exit code per the documented contract."""
    try:
        raw = _read_input(input_path)
    except _CliReadFailure as failure:
        reason = str(failure)
        decision = _blocked_decision_for(reason, DECISION_ENGINE_VERSION)
        pack = _to_evidence_pack(decision)
        try:
            _write_output(output_path, pack)
        except OSError:
            return int(exit_code_for(ReleaseDecisionStatus.ERROR))
        return int(exit_code_for(decision))

    try:
        decision = evaluate_release_decision(raw)
    except ReleaseDecisionError:
        decision = _blocked_decision_for(
            "decision_input_invalid", DECISION_ENGINE_VERSION
        )

    pack = _to_evidence_pack(decision)
    try:
        _write_output(output_path, pack)
    except OSError:
        return int(exit_code_for(ReleaseDecisionStatus.ERROR))
    return int(exit_code_for(decision))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase22 Benchmark Comparison and Release Decision Engine.",
        add_help=True,
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
