"""PHASE22 CC-D evidence verifier.

Validates that the CC-D evidence bundle and matrix loader stay honest:

* Every matrix row has all required fields.
* All rows are ``NOT_RUN_DEPENDENCY_BLOCKED`` while
  ``snapshot_id`` / ``profile_run_ids`` are placeholders.
* No row carries a forged ``receipt_ref`` or ``trace_ref``.
* The evidence bundle has no secret-like patterns.
* The environment probe does not claim write/read verified.
* The ``commands`` log records real ``exit_code`` / ``stdout`` / ``stderr``;
  unrun commands have ``exit_code == None`` and
  ``status == NOT_RUN_DEPENDENCY_BLOCKED`` (never a manufactured ``0``).
* Every recorded command uses the canonical ``python tools/scripts/...``
  form — never a host-specific ``sys.executable`` absolute path, drive
  letter, ``/home/<user>/``, ``/Users/<user>/``, or ``file://`` URL.
* The bundle does not self-verify: the verifier command must be
  ``NOT_RUN_IN_BUILDER``.
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

# Patterns that must NEVER appear in committed evidence because they leak
# the host machine. The patterns require an actual path separator AFTER
# the drive letter or user directory so they do not match English prose
# like "drive-letter" or "file://" used as a literal mention. Patterns
# accept either single or doubled backslashes so the scan works on the
# JSON-encoded payload.
HOST_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]+[^/\\<>:\"\s]"),
    re.compile(r"(?<![A-Za-z])/home/[^/\s\"<>|?*]+/"),
    re.compile(r"(?<![A-Za-z])/Users/[^/\s\"<>|?*]+/"),
    re.compile(r"(?i)\bfile://[A-Za-z0-9_./%-]+/"),
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


def _scan_text_for_host_paths(text: str) -> list[str]:
    return [p.pattern for p in HOST_PATH_PATTERNS if p.search(text)]


def _verify_command_truth(record: dict[str, Any]) -> list[str]:
    """Return errors for any command record that breaks the truth contract."""

    errors: list[str] = []
    label = record.get("command", "<unknown>")
    launched = record.get("launched")
    exit_code = record.get("exit_code")
    status = record.get("status")

    if launched is True:
        if exit_code is None and status not in {"TIMEOUT", "LAUNCH_FAILED"}:
            errors.append(
                f"command {label!r}: launched=True but exit_code is null and status is not TIMEOUT/LAUNCH_FAILED"
            )
        if status in {"NOT_RUN_DEPENDENCY_BLOCKED", "NOT_RUN"}:
            errors.append(
                f"command {label!r}: launched=True but status is {status!r}"
            )
    elif launched is False:
        if exit_code is not None:
            errors.append(
                f"command {label!r}: launched=False but exit_code={exit_code!r} (must be null)"
            )
        if status not in {"NOT_RUN_DEPENDENCY_BLOCKED", "NOT_RUN_IN_BUILDER", "NOT_RUN"}:
            errors.append(
                f"command {label!r}: launched=False but status={status!r}"
            )
        if not record.get("not_run_reason"):
            errors.append(
                f"command {label!r}: launched=False must carry not_run_reason"
            )
    else:
        errors.append(
            f"command {label!r}: missing launched flag (must be bool)"
        )

    stdout = record.get("stdout")
    stderr = record.get("stderr")
    if launched is True and status not in {"TIMEOUT", "LAUNCH_FAILED"}:
        if stdout is None:
            errors.append(
                f"command {label!r}: launched=True must record stdout (even if empty)"
            )
        if stderr is None:
            errors.append(
                f"command {label!r}: launched=True must record stderr (even if empty)"
            )

    if not record.get("started_at"):
        errors.append(f"command {label!r}: missing started_at")
    if not record.get("ended_at"):
        errors.append(f"command {label!r}: missing ended_at")
    if record.get("elapsed_seconds") is None:
        errors.append(f"command {label!r}: missing elapsed_seconds")

    # Canonical command form: every record must use ``executable`` from a
    # known whitelist (``python``, ``git``, or empty for non-script
    # invocations). Anything else is treated as a host-specific absolute
    # path that escaped canonicalization.
    executable = record.get("executable")
    allowed_executables = {"python", "git", ""}
    if executable not in allowed_executables:
        errors.append(
            f"command {label!r}: executable must be one of "
            f"{sorted(allowed_executables)}, got {executable!r}"
        )
    script = record.get("script", "")
    if script:
        if script.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", script):
            errors.append(
                f"command {label!r}: script must be repo-relative, got {script!r}"
            )

    return errors


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

        commands = bundle.get("commands") or []
        if not isinstance(commands, list) or not commands:
            errors.append("evidence bundle must carry a non-empty commands log")
        else:
            for record in commands:
                if not isinstance(record, dict):
                    errors.append("evidence bundle commands entries must be objects")
                    continue
                errors.extend(_verify_command_truth(record))

            # Self-verification loop check: the CC-D verifier command must
            # be recorded as NOT_RUN_IN_BUILDER.
            verifier_records = [
                r
                for r in commands
                if isinstance(r.get("script"), str)
                and r["script"].endswith("verify_phase22_cc_d_evidence.py")
            ]
            if not verifier_records:
                errors.append(
                    "evidence bundle must record the CC-D verifier command "
                    "(even if it was not run inside the builder)"
                )
            else:
                for record in verifier_records:
                    if record.get("status") != "NOT_RUN_IN_BUILDER":
                        errors.append(
                            f"verifier command {record.get('command')!r} must be "
                            "NOT_RUN_IN_BUILDER; builder must not run its own verifier"
                        )
                    if record.get("launched") is not False:
                        errors.append(
                            f"verifier command {record.get('command')!r} must have "
                            "launched=False inside the bundle"
                        )

        # Per-case runs: status must never be PASSED while matrix is blocked.
        for run in bundle.get("case_runs", []) or []:
            if run.get("status") == "PASSED":
                errors.append(
                    f"evidence bundle run for {run.get('case_id')} must not be PASSED"
                )
            execution = run.get("execution") or {}
            if execution.get("launched") is True:
                errors.append(
                    f"evidence bundle run for {run.get('case_id')} execution.launched must be False while matrix is blocked"
                )
            if execution.get("exit_code") is not None:
                errors.append(
                    f"evidence bundle run for {run.get('case_id')} execution.exit_code must be null while matrix is blocked"
                )
            # would_run_argv must be repo-relative.
            argv = execution.get("would_run_argv")
            if argv is not None:
                argv_str = " ".join(str(p) for p in argv)
                host_hits = _scan_text_for_host_paths(argv_str)
                if host_hits:
                    errors.append(
                        f"evidence bundle run for {run.get('case_id')} "
                        f"would_run_argv leaks host path: {host_hits}"
                    )

        # Bundle-wide host-path scan.
        host_hits = _scan_text_for_host_paths(json.dumps(bundle, ensure_ascii=False))
        if host_hits:
            errors.append(
                "evidence bundle leaks host-specific absolute paths: "
                + ", ".join(host_hits)
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
        host_hits = _scan_text_for_host_paths(json.dumps(probe, ensure_ascii=False))
        if host_hits:
            errors.append(
                "environment probe leaks host-specific absolute paths: "
                + ", ".join(host_hits)
            )

    fault_run = _read_json(FAULT_RUN_PATH) or {}
    if fault_run:
        secret_hits = _scan_text_for_secrets(json.dumps(fault_run, ensure_ascii=False))
        if secret_hits:
            errors.append(
                "fault matrix run leaks secret-like patterns: " + ", ".join(secret_hits)
            )
        host_hits = _scan_text_for_host_paths(json.dumps(fault_run, ensure_ascii=False))
        if host_hits:
            errors.append(
                "fault matrix run leaks host-specific absolute paths: "
                + ", ".join(host_hits)
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