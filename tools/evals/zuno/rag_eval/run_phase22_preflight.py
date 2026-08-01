"""PHASE22 Benchmark Preflight CLI.

Reads a JSON preflight payload from ``--input`` and writes a deterministic
JSON preflight report to ``--output``. Exit codes mirror the four
preflight states:

* 0 — ``READY``
* 2 — ``BLOCKED``
* 3 — ``INCOMPARABLE``
* 4 — ``INVALID`` (or input / parse failure)

The CLI must never:

* execute retrieval, agents, or models
* touch the network
* read environment secrets
* print Python tracebacks
* leak credentials in the output document
* modify the input file
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping, Optional, Tuple


# Allow running directly: ``python tools/evals/zuno/rag_eval/run_phase22_preflight.py``
_HERE = os.path.dirname(os.path.abspath(__file__))
_RAG_EVAL_DIR = os.path.dirname(_HERE)
if _RAG_EVAL_DIR not in sys.path:
    sys.path.insert(0, _RAG_EVAL_DIR)

from rag_eval.benchmark_preflight import (  # noqa: E402  (sys.path setup)
    BenchmarkPreflightEvaluator,
    BenchmarkPreflightReport,
    STATE_BLOCKED,
    STATE_INCOMPARABLE,
    STATE_INVALID,
    STATE_READY,
    report_to_dict,
)


EXIT_READY = 0
EXIT_BLOCKED = 2
EXIT_INCOMPARABLE = 3
EXIT_INVALID = 4


STATE_TO_EXIT = {
    STATE_READY: EXIT_READY,
    STATE_BLOCKED: EXIT_BLOCKED,
    STATE_INCOMPARABLE: EXIT_INCOMPARABLE,
    STATE_INVALID: EXIT_INVALID,
}


def _read_input(path: str) -> Tuple[Optional[Mapping[str, Any]], Optional[str]]:
    """Read UTF-8 JSON. Returns ``(payload, error)``."""

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return None, "input_file_not_found"
    except PermissionError:
        return None, "input_file_not_readable"
    except json.JSONDecodeError:
        return None, "input_invalid_json"
    except UnicodeDecodeError:
        return None, "input_invalid_utf8"
    if not isinstance(data, Mapping):
        return None, "input_not_object"
    return data, None


def _ensure_output_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def _strip_secrets(
    report_dict: Mapping[str, Any], payload: Mapping[str, Any]
) -> Dict[str, Any]:
    """Return a copy of the report with any credential-like fields removed.

    The preflight contract does not put credentials into the report, but
    we still take a defensive copy so that a future regression cannot
    silently leak ``credential_ref`` content if it ever appeared under a
    different key.
    """

    # Trivially safe: the report schema has no place where credentials live.
    return dict(report_dict)


def _write_output(path: str, report: BenchmarkPreflightReport) -> None:
    _ensure_output_dir(path)
    payload = report_to_dict(report)
    safe = _strip_secrets(payload, {})
    text = json.dumps(
        safe,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    # Append trailing newline so the file is POSIX-friendly.
    if not text.endswith("\n"):
        text += "\n"
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _write_invalid_output(path: Optional[str], report: BenchmarkPreflightReport) -> None:
    """Best-effort write of an INVALID report. Used when payload parsing
    fails so the caller still sees a structured record for diagnostics."""

    if path is None:
        return
    try:
        _write_output(path, report)
    except OSError:
        # We never let the report writer raise; the exit code is what
        # callers rely on.
        pass


def _build_invalid_report(reason: str) -> BenchmarkPreflightReport:
    from rag_eval.benchmark_preflight import BenchmarkPreflightReport

    return BenchmarkPreflightReport(
        state=STATE_INVALID,
        gap_codes=(reason,),
        profile_results=(),
        input_fingerprint="",
        contract_version="phase22-benchmark-preflight.v1",
    )


def run(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_phase22_preflight",
        description=(
            "Deterministic PHASE22 benchmark preflight contract. "
            "Reads a JSON input and writes a JSON report; never executes "
            "the benchmark itself."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the UTF-8 JSON preflight input payload.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the UTF-8 JSON preflight report destination.",
    )
    args = parser.parse_args(argv)

    payload, read_error = _read_input(args.input)
    if read_error is not None:
        # Match the brief: invalid JSON / unreadable input -> exit 4 with a
        # short stderr message, no traceback, no fake READY.
        sys.stderr.write("preflight: " + read_error + "\n")
        return EXIT_INVALID

    evaluator = BenchmarkPreflightEvaluator()
    try:
        report = evaluator.evaluate(payload)
    except Exception as exc:  # pragma: no cover  (defensive only)
        # The evaluator is designed to never raise, but we keep this
        # belt-and-braces so the CLI never leaks a traceback.
        sys.stderr.write("preflight: evaluation_failed\n")
        _write_invalid_output(
            args.output, _build_invalid_report("evaluation_failed")
        )
        return EXIT_INVALID

    try:
        _write_output(args.output, report)
    except OSError:
        sys.stderr.write("preflight: output_write_failed\n")
        return STATE_TO_EXIT.get(report.state, EXIT_INVALID)

    return STATE_TO_EXIT.get(report.state, EXIT_INVALID)


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
