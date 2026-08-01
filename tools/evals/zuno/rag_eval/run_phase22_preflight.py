"""PHASE22 Benchmark Preflight CLI (v2).

Reads a JSON preflight payload from ``--input`` and writes a deterministic
JSON preflight report to ``--output``. Exit codes mirror the four
preflight states:

* 0 -- ``READY``
* 2 -- ``BLOCKED``
* 3 -- ``INCOMPARABLE``
* 4 -- ``INVALID`` (or input / parse / write failure)

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


class OutputWriteError(RuntimeError):
    """Raised when the CLI cannot write the report to its output path."""


def _strict_parse_constant(value: str) -> None:
    """Reject the non-standard JSON constants ``NaN``, ``Infinity``,
    ``-Infinity`` that ``json`` accepts by default."""

    raise ValueError(f"invalid JSON constant: {value}")


def _read_input(path: str) -> Tuple[Optional[Mapping[str, Any]], Optional[str]]:
    """Read UTF-8 JSON. Returns ``(payload, error_code)``."""

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle, parse_constant=_strict_parse_constant)
    except FileNotFoundError:
        return None, "input_file_not_found"
    except PermissionError:
        return None, "input_file_not_readable"
    except json.JSONDecodeError:
        return None, "input_invalid_json"
    except UnicodeDecodeError:
        return None, "input_invalid_utf8"
    except ValueError as exc:
        # ``parse_constant`` raises ValueError to reject NaN/Infinity.
        if "invalid JSON constant" in str(exc):
            return None, "input_invalid_number"
        return None, "input_invalid_json"
    if not isinstance(data, Mapping):
        return None, "input_not_object"
    return data, None


def _ensure_output_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def _write_output(path: str, report: BenchmarkPreflightReport) -> None:
    """Write a deterministic JSON report. Any OS-level failure must
    surface as :class:`OutputWriteError` so the CLI can map it to
    exit code 4."""

    try:
        _ensure_output_dir(path)
    except (OSError, PermissionError) as exc:
        raise OutputWriteError(f"output_dir_creation_failed: {exc}") from exc

    payload = report_to_dict(report)
    text = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    if not text.endswith("\n"):
        text += "\n"
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    except (OSError, PermissionError) as exc:
        raise OutputWriteError(f"output_write_failed: {exc}") from exc


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
        sys.stderr.write("preflight: " + read_error + "\n")
        return EXIT_INVALID

    evaluator = BenchmarkPreflightEvaluator()
    try:
        report = evaluator.evaluate(payload)
    except Exception:  # pragma: no cover  (defensive only)
        sys.stderr.write("preflight: evaluation_failed\n")
        return EXIT_INVALID

    try:
        _write_output(args.output, report)
    except OutputWriteError as exc:
        sys.stderr.write("preflight: " + str(exc) + "\n")
        return EXIT_INVALID

    return STATE_TO_EXIT.get(report.state, EXIT_INVALID)


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
