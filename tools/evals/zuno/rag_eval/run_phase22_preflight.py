"""PHASE22 Benchmark Preflight CLI (v3).

Reads a JSON preflight payload from ``--input`` and writes a deterministic
JSON preflight report to ``--output``. Exit codes mirror the four
preflight states:

* 0 -- ``READY``
* 2 -- ``BLOCKED``
* 3 -- ``INCOMPARABLE``
* 4 -- ``INVALID`` (or input / parse / write / CLI usage failure)

The CLI must never:

* execute retrieval, agents, or models
* touch the network
* read environment secrets
* print Python tracebacks
* print raw OS exceptions
* leak credentials, absolute paths, or user names in the output /
  stderr
* modify the input file
* use argparse's default exit code 2 on CLI usage errors
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping, Optional, Tuple


# Allow running directly: ``python tools/evals/zuno/rag_eval/run_phase22_preflight.py``
# The canonical absolute import works whenever the repo root is on
# sys.path.  The standalone fallback imports the module from its own
# directory so the script works when executed directly, without going
# through the package ``__init__`` (which imports the merged Release
# Decision engine and must not be loaded for a plain script run).
_HERE = os.path.dirname(os.path.abspath(__file__))

try:
    from tools.evals.zuno.rag_eval.benchmark_preflight import (  # noqa: E402
        BenchmarkPreflightEvaluator,
        BenchmarkPreflightReport,
        STATE_BLOCKED,
        STATE_INCOMPARABLE,
        STATE_INVALID,
        STATE_READY,
        report_to_dict,
    )
except ModuleNotFoundError:
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    from benchmark_preflight import (  # noqa: E402
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
    """Raised when the CLI cannot write the report to its output path.

    Carries only a fixed error code (no path, no raw exception, no
    Windows shell path) so the CLI can map it to a stable stderr line
    and exit code 4.
    """

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _strict_parse_constant(value: str) -> None:
    """Reject the non-standard JSON constants ``NaN``, ``Infinity``,
    ``-Infinity`` that ``json`` accepts by default."""

    raise ValueError(f"invalid JSON constant: {value}")


def _read_input(path: str) -> Tuple[Optional[Mapping[str, Any]], Optional[str]]:
    """Read UTF-8 JSON. Returns ``(payload, error_code)``.

    All I/O and parse failures are mapped to fixed error codes. No raw
    exception text is ever returned.
    """

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle, parse_constant=_strict_parse_constant)
    except FileNotFoundError:
        return None, "input_file_not_found"
    except PermissionError:
        return None, "input_file_not_readable"
    except IsADirectoryError:
        return None, "input_path_is_directory"
    except UnicodeDecodeError:
        return None, "input_invalid_utf8"
    except json.JSONDecodeError:
        return None, "input_invalid_json"
    except ValueError as exc:
        if "invalid JSON constant" in str(exc):
            return None, "input_invalid_number"
        return None, "input_invalid_json"
    except OSError:
        return None, "input_file_not_readable"
    if not isinstance(data, Mapping):
        return None, "input_not_object"
    return data, None


def _ensure_output_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        try:
            os.makedirs(parent, exist_ok=True)
        except (OSError, PermissionError):
            raise OutputWriteError("output_dir_creation_failed")


def _write_output(path: str, report: BenchmarkPreflightReport) -> None:
    """Write a deterministic JSON report. Any OS-level failure must
    surface as :class:`OutputWriteError` so the CLI can map it to
    exit code 4. The raised error carries only a fixed code; it never
    embeds the absolute path, the OS exception text, or any user name."""

    _ensure_output_dir(path)

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
    except (OSError, PermissionError):
        raise OutputWriteError("output_write_failed")


class _FixedExitArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that exits 4 (not 2) on usage errors and never
    prints a Python traceback."""

    def error(self, message: str) -> None:  # pragma: no cover  (defensive)
        sys.stderr.write("preflight: argparse_error\n")
        sys.stderr.write(self.format_usage())
        raise SystemExit(EXIT_INVALID)


def run(argv: Optional[list] = None) -> int:
    parser = _FixedExitArgumentParser(
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
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else EXIT_INVALID

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
        sys.stderr.write("preflight: " + exc.code + "\n")
        return EXIT_INVALID

    return STATE_TO_EXIT.get(report.state, EXIT_INVALID)


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
