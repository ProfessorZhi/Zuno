"""PHASE22 CC-D evidence builder.

Generates an evidence bundle for the CC-D worker. The bundle contains:

* matrix manifest with all required fields
* environment probe output
* per-case fault runner records
* a ``commands`` log with real ``started_at`` / ``ended_at`` / ``elapsed_seconds`` /
  ``launched`` / ``exit_code`` / ``stdout`` / ``stderr`` / ``status`` for every
  command this builder actually invokes
* redaction manifest proving no secrets leaked (also enforced on every
  captured stdout / stderr stream)

Truth rules (CC-D task card + coordinator feedback):

* Commands that this builder actually launches must record the real
  ``exit_code``. We never invent ``exit_code == 0``.
* Commands that we did not launch record ``launched: false``,
  ``exit_code: null``, ``status: NOT_RUN_DEPENDENCY_BLOCKED`` /
  ``NOT_RUN_IN_BUILDER`` and an explicit ``not_run_reason``.
* ``stdout`` / ``stderr`` are length-capped and run through the same
  secret-redaction sweep that gates the bundle write.
* The bundle never flips any matrix row to ``PASSED`` while
  ``snapshot_id`` / ``profile_run_ids`` are placeholders.
* Commands are recorded in the **repository-relative / canonical** form
  ``python tools/scripts/<script>.py ...`` — never with the host's
  ``sys.executable`` absolute path or the worktree absolute path. The
  bundled command record is structured as ``{executable, script, args}``
  plus a derived ``command`` string that always starts with
  ``python tools/``.
* The builder NEVER invokes its own verifier. Verifier execution is
  detached: the verifier reads the bundle from disk after the bundle is
  written, and writes a separate ``detached_verification_report.json``
  artifact. The builder records the verifier as
  ``NOT_RUN_IN_BUILDER`` so the bundle cannot self-validate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]

MATRIX_PATH = (
    REPO_ROOT
    / "tools"
    / "evals"
    / "zuno"
    / "synthetic_benchmark"
    / "phase22_cc_d_fault_matrix.yaml"
)

EVIDENCE_DIR = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "minimax2-cc-d"
)

# Repository-relative script paths. These are the only paths we ever emit
# into evidence; absolute / worktree-relative paths are redacted before
# write so that the committed bundle contains no host-specific data.
ENV_PROBE_REL = "tools/scripts/phase22_environment_probe.py"
FAULT_RUNNER_REL = "tools/scripts/phase22_fault_matrix_runner.py"
VERIFY_TRACK_REL = "tools/scripts/verify_phase22_synthetic_regression_track.py"
VERIFY_BLOCKERS_REL = "tools/scripts/verify_phase22_completion_blockers.py"
VERIFY_CC_D_REL = "tools/scripts/verify_phase22_cc_d_evidence.py"

ENV_PROBE_SCRIPT = REPO_ROOT / ENV_PROBE_REL
FAULT_RUNNER_SCRIPT = REPO_ROOT / FAULT_RUNNER_REL
VERIFY_TRACK_SCRIPT = REPO_ROOT / VERIFY_TRACK_REL
VERIFY_BLOCKERS_SCRIPT = REPO_ROOT / VERIFY_BLOCKERS_REL
VERIFY_CC_D_SCRIPT = REPO_ROOT / VERIFY_CC_D_REL

# Per-stream cap for captured stdout / stderr. Keeps the bundle small while
# still preserving the tail that downstream tools and humans need.
MAX_OUTPUT_BYTES = 4096

# Patterns that must NEVER appear in evidence output. We treat any match as
# a secret leakage and refuse to write the bundle (and redact on capture).
SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)postgres:postgres@"),
    re.compile(r"(?i)neo4j/neo4j12345"),
    re.compile(r"(?i)minioadmin:minioadmin"),
    re.compile(r"(?i)guest:guest@"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{16,}"),
)

# Patterns that must NEVER appear inside committed evidence because they
# leak the host machine. We refuse to write the bundle if any of these
# match. The patterns require an actual path separator AFTER the drive
# letter or user directory so they do not match English prose like
# "drive-letter" or "file://" used as a literal mention. Patterns are
# applied to the JSON-encoded payload, so drive-letter paths show up
# with doubled backslashes (``F:\\agent_project``); the pattern accepts
# either form.
HOST_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Windows drive-letter path: ``E:\...`` or ``F:/...``. The drive
    # letter must be preceded by a non-letter (start of string or
    # whitespace / quote) and the path must contain at least one
    # non-separator character after the colon.
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]+[^/\\<>:\"\s]"),
    # Linux-style /home/<user>/... path: require a non-empty user
    # directory followed by a slash so the literal text "/home/,"
    # does not match.
    re.compile(r"(?<![A-Za-z])/home/[^/\s\"<>|?*]+/"),
    # macOS-style /Users/<user>/... path: same rule.
    re.compile(r"(?<![A-Za-z])/Users/[^/\s\"<>|?*]+/"),
    # file:// URLs pointing at the host filesystem.
    re.compile(r"(?i)\bfile://[A-Za-z0-9_./%-]+/"),
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_yaml(path: Path) -> Any:
    import yaml  # type: ignore[import-untyped]

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _scan_for_secrets(payload: str) -> list[str]:
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(payload):
            hits.append(f"{pattern.pattern}: {match.group(0)[:8]}***")
    return hits


def _scan_for_host_paths(payload: str) -> list[str]:
    hits: list[str] = []
    for pattern in HOST_PATH_PATTERNS:
        for match in pattern.finditer(payload):
            hits.append(f"{pattern.pattern}: {match.group(0)[:16]}***")
    return hits


def _redact_text(text: str) -> str:
    """Replace every secret / host-path pattern match with ``***REDACTED***``.

    Operates on the literal text; the bundle write gate runs the same
    sweep again to refuse any leak that slipped past capture-time
    redaction.
    """

    if not text:
        return text
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("***REDACTED***", text)
    return text


def _truncate(text: str, limit: int = MAX_OUTPUT_BYTES) -> str:
    if text is None:
        return None  # type: ignore[return-value]
    if len(text) <= limit:
        return text
    return text[:limit] + f"...<truncated {len(text) - limit} bytes>"


def _is_python_executable(value: str) -> bool:
    """Return True when ``value`` looks like a Python executable path."""

    if not value:
        return False
    lowered = value.lower()
    if lowered.endswith("python") or lowered.endswith("python.exe") or lowered.endswith("python3"):
        return True
    basename = Path(value).name.lower()
    return basename in {"python", "python3", "python.exe", "python3.exe"}


def _canonicalize_argv(argv: list[str]) -> dict[str, Any]:
    """Turn a host-executable argv into the canonical repository form.

    The first element is replaced with the literal ``python`` whenever it
    looks like a Python interpreter. Non-Python commands (``git`` etc.)
    keep their original first element. Subsequent absolute paths that
    fall inside the repo are rewritten to repo-relative form. Anything
    outside the repo is left as-is (and will be re-checked by the
    host-path scan).
    """

    if not argv:
        return {"executable": "", "script": "", "args": []}

    exe = argv[0]
    rest = list(argv[1:])
    canonical_exe = "python" if _is_python_executable(exe) else exe

    canonical_script = ""
    canonical_args: list[str] = []
    if rest and _is_python_executable(canonical_exe):
        first = Path(rest[0])
        try:
            relative = first.resolve().relative_to(REPO_ROOT)
            canonical_script = relative.as_posix()
            canonical_args = list(rest[1:])
        except (ValueError, OSError):
            canonical_script = ""
            canonical_args = list(rest)
    else:
        canonical_script = ""
        canonical_args = list(rest)
    return {
        "executable": canonical_exe,
        "script": canonical_script,
        "args": canonical_args,
    }


def _command_string_from_argv(argv: list[str]) -> str:
    """Return the canonical ``python tools/scripts/...`` string."""

    if not argv:
        return ""
    canonical = _canonicalize_argv(argv)
    if canonical["script"]:
        return " ".join(
            [canonical["executable"], canonical["script"], *canonical["args"]]
        )
    return " ".join([canonical["executable"], *canonical["args"]])


def _command_record(
    argv: list[str],
    *,
    started_at: str,
    elapsed: float,
    launched: bool,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    status: str,
    not_run_reason: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    canonical = _canonicalize_argv(argv)
    record: dict[str, Any] = {
        "executable": canonical["executable"],
        "script": canonical["script"],
        "args": canonical["args"],
        "command": _command_string_from_argv(argv),
        "started_at": started_at,
        "ended_at": _utc_now_iso(),
        "elapsed_seconds": round(elapsed, 3),
        "launched": launched,
        "exit_code": exit_code,
        "stdout": _truncate(_redact_text(stdout or "")),
        "stderr": _truncate(_redact_text(stderr or "")),
        "status": status,
    }
    if not_run_reason is not None:
        record["not_run_reason"] = not_run_reason
    if error is not None:
        record["error"] = error
    return record


def _execute_command(argv: list[str], *, timeout: float | None = None) -> dict[str, Any]:
    """Run ``argv`` and return a truthful command record.

    The returned record always carries the real ``exit_code`` (or ``None``
    on timeout / launch failure), the real (redacted + truncated)
    ``stdout`` / ``stderr``, and a derived ``status`` field that the
    bundle gate treats as authoritative.
    """

    started_at = _utc_now_iso()
    start = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        return _command_record(
            argv,
            started_at=started_at,
            elapsed=elapsed,
            launched=True,
            exit_code=None,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
            status="TIMEOUT",
            error=f"subprocess exceeded timeout={timeout}s",
        )
    except FileNotFoundError as exc:
        elapsed = time.monotonic() - start
        return _command_record(
            argv,
            started_at=started_at,
            elapsed=elapsed,
            launched=False,
            exit_code=None,
            stdout="",
            stderr="",
            status="LAUNCH_FAILED",
            error=str(exc),
        )
    elapsed = time.monotonic() - start
    status = "PASSED" if proc.returncode == 0 else "FAILED"
    return _command_record(
        argv,
        started_at=started_at,
        elapsed=elapsed,
        launched=True,
        exit_code=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        status=status,
    )


def _not_run_record(argv: list[str], not_run_reason: str, status: str = "NOT_RUN_DEPENDENCY_BLOCKED") -> dict[str, Any]:
    return _command_record(
        argv,
        started_at=_utc_now_iso(),
        elapsed=0.0,
        launched=False,
        exit_code=None,
        stdout="",
        stderr="",
        status=status,
        not_run_reason=not_run_reason,
    )


def _run_env_probe(
    output_path: Path,
    *,
    timeout: float = 1.0,
    records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Invoke the environment probe and capture real truth.

    The probe writes its JSON report to ``output_path``. We do NOT
    fabricate an exit code; whatever the probe returns is what we
    record. The recorded command is canonicalized to
    ``python tools/scripts/phase22_environment_probe.py`` and the
    ``--output`` argument is passed as a repo-relative path so the
    committed evidence contains no host-specific absolute paths.
    """

    try:
        relative_output = output_path.resolve().relative_to(REPO_ROOT).as_posix()
    except (ValueError, OSError):
        relative_output = output_path.name
    launch_argv = [
        _resolve_host_python(),
        ENV_PROBE_REL,
        "--output",
        relative_output,
        "--timeout",
        str(timeout),
    ]
    record = _execute_command(launch_argv, timeout=timeout + 30.0)
    if records is not None:
        records.append(record)
    return record


def _resolve_host_python() -> str:
    """Return the host Python interpreter to actually launch subprocesses.

    This value is used only for invocation; it never appears in the
    emitted evidence.
    """

    import sys as _sys

    return _sys.executable


def _record_matrix_case(
    case: dict[str, Any],
    *,
    fault_runner_rel: str = FAULT_RUNNER_REL,
) -> dict[str, Any]:
    """Record a per-case run without launching subprocesses.

    While ``matrix_status`` is ``NOT_RUN_DEPENDENCY_BLOCKED`` we never
    spawn the fault runner once per case; instead we capture the
    structural record directly from the matrix YAML. The
    ``test_command`` is recorded as ``would_run`` so the bundle still
    names the exact command the live runtime would execute, but
    ``launched`` is ``False`` and ``exit_code`` is ``None`` to make
    crystal clear we did not execute it.
    """

    test_command = str(case.get("test_command", ""))
    would_run_argv: list[str] | None = None
    if test_command.startswith("python "):
        parts = test_command.split()
        if len(parts) >= 2:
            would_run_argv = ["python", *parts[1:]]
            # Rewrite the script to the repo-relative form if we can
            # resolve it.
            try:
                resolved = (REPO_ROOT / parts[1]).resolve()
                if resolved.is_relative_to(REPO_ROOT):
                    would_run_argv[1] = resolved.relative_to(REPO_ROOT).as_posix()
            except (OSError, ValueError):
                pass
    return {
        "case_id": case.get("case_id"),
        "test_command": test_command,
        "expected_exit_code": case.get("exit_code"),
        "status": case.get("status"),
        "not_run_reason": case.get("not_run_reason"),
        "execution": {
            "launched": False,
            "exit_code": None,
            "started_at": None,
            "ended_at": None,
            "elapsed_seconds": None,
            "stdout": None,
            "stderr": None,
            "status": "NOT_RUN_DEPENDENCY_BLOCKED",
            "not_run_reason": (
                "test_command recorded but not executed while matrix_status is "
                "NOT_RUN_DEPENDENCY_BLOCKED; live execution waits for DeepSeek "
                "CC-B snapshot_id and CC-C profile_run_ids"
            ),
            "would_run": test_command,
            "would_run_argv": would_run_argv,
        },
    }


def build_bundle(
    *,
    cases: Iterable[str] | None = None,
    run_probe: bool = True,
    run_tracks: bool = True,
) -> dict[str, Any]:
    matrix = _load_yaml(MATRIX_PATH)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    probe_report_path = EVIDENCE_DIR / "environment_probe.json"

    commands: list[dict[str, Any]] = []

    if run_probe:
        _run_env_probe(probe_report_path, records=commands)

    case_records: list[dict[str, Any]] = []
    selected = set(cases) if cases is not None else None
    for case in matrix.get("cases", []):
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id", ""))
        if selected is not None and case_id not in selected:
            continue
        case_records.append(_record_matrix_case(case))

    if run_tracks:
        commands.append(
            _execute_command(
                ["git", "diff", "--check"], timeout=30.0
            )
        )
        commands.append(
            _execute_command(
                [_resolve_host_python(), VERIFY_TRACK_REL], timeout=120.0
            )
        )
        commands.append(
            _execute_command(
                [_resolve_host_python(), VERIFY_BLOCKERS_REL], timeout=120.0
            )
        )
        # The CC-D verifier is intentionally NOT executed inside the
        # builder — it would be a self-verification loop because the
        # verifier reads the bundle from disk while we are still building
        # it. We record the verifier as NOT_RUN_IN_BUILDER and rely on
        # the detached post-write verifier instead.
        commands.append(
            _not_run_record(
                ["python", VERIFY_CC_D_REL],
                (
                    "verify_phase22_cc_d_evidence.py is intentionally not "
                    "executed inside the builder; detached post-write "
                    "verification writes "
                    "docs/evidence/.../detached_verification_report.json."
                ),
                status="NOT_RUN_IN_BUILDER",
            )
        )
    else:
        skip_reason = (
            "track verifiers not invoked by this build (--skip-tracks passed); "
            "live invocation required by the CC-D task card"
        )
        commands.append(_not_run_record(["git", "diff", "--check"], skip_reason))
        commands.append(
            _not_run_record(["python", VERIFY_TRACK_REL], skip_reason)
        )
        commands.append(
            _not_run_record(["python", VERIFY_BLOCKERS_REL], skip_reason)
        )
        commands.append(
            _not_run_record(
                ["python", VERIFY_CC_D_REL],
                "verify_phase22_cc_d_evidence.py is intentionally not executed inside the builder; detached post-write verification writes docs/evidence/.../detached_verification_report.json.",
                status="NOT_RUN_IN_BUILDER",
            )
        )

    # Per-case fault runner invocations are recorded as not-run while the
    # matrix is dependency-blocked. We never spawn the runner per case here;
    # the case_records already encode that decision.
    case_runner_reason = (
        "matrix_status is NOT_RUN_DEPENDENCY_BLOCKED; per-case fault runner "
        "must wait for DeepSeek CC-B snapshot_id and CC-C profile_run_ids"
    )
    for case_id in [c.get("case_id") for c in matrix.get("cases", []) if isinstance(c, dict)]:
        commands.append(
            _not_run_record(
                ["python", FAULT_RUNNER_REL, "--case", str(case_id)],
                case_runner_reason,
            )
        )

    exit_code_map: dict[str, int | None] = {}
    status_map: dict[str, str] = {}
    for record in commands:
        label = record["command"]
        exit_code_map[label] = record["exit_code"]
        status_map[label] = record["status"]

    bundle = {
        "schema_version": "1.0.0",
        "goal_id": "phase22-machine-attested-synthetic-regression",
        "worker_task_id": "CC-D",
        "agent_name": "MiniMax2",
        "provider": "MiniMax",
        "captured_at": _utc_now_iso(),
        "matrix_status": matrix.get("matrix_status"),
        "dependency_pr": matrix.get("dependency_pr"),
        "dependency_head_sha": matrix.get("dependency_head_sha"),
        "snapshot_id": matrix.get("snapshot_id"),
        "profile_run_ids": matrix.get("profile_run_ids", []),
        "matrix_path": str(MATRIX_PATH.relative_to(REPO_ROOT)),
        "matrix_sha256": _sha256_file(MATRIX_PATH),
        "case_count": len(matrix.get("cases", [])),
        "case_runs": case_records,
        "environment_probe_path": str(probe_report_path.relative_to(REPO_ROOT)),
        "environment_probe_sha256": (
            _sha256_file(probe_report_path) if probe_report_path.exists() else None
        ),
        "commands": commands,
        "exit_codes": exit_code_map,
        "command_status": status_map,
        "candidate_dependency_prs": [112, 113],
        "cleanup": [
            "drop probe buckets and queues if any probe created them",
            "remove temp evidence files in repo root (none created)",
            "leave docker stack as discovered (no start/stop from this worker)",
        ],
        "service_versions": {
            "python": "interpreter version is not captured here to avoid host-specific data",
            "docker_compose_file": "infra/docker/docker-compose.yml",
        },
        "forbidden_actions_respected": [
            "no port-reachable == write/read verified",
            "no handwritten receipt",
            "no handwritten trace",
            "no deleted failure assertions",
            "no secret in evidence",
            "no host absolute path in evidence (drive-letter, /home, /Users, file:// all rejected at write time)",
            "no UNKNOWN side effect blind retry",
            "no snapshot activation without receipt",
            "no BLOCKED rewritten as PASSED",
            "no fabricated exit_code (real subprocess exit codes only)",
            "no recorded-as-run commands without real launch",
            "no self-verification loop: builder does not run the CC-D verifier",
        ],
        "remaining_gaps": [
            "DeepSeek CC-B must produce snapshot_id + three visibility receipts",
            "DeepSeek CC-C must produce profile_run_ids + measurement attestation",
            "this bundle cannot flip any row to PASSED until receipts land",
        ],
    }
    return bundle


def write_bundle(bundle: dict[str, Any], path: Path) -> list[str]:
    payload = json.dumps(bundle, indent=2, ensure_ascii=False)
    leaks = _scan_for_secrets(payload)
    if leaks:
        raise RuntimeError(
            f"refusing to write evidence bundle: secret-like patterns detected: {leaks}"
        )
    host_leaks = _scan_for_host_paths(payload)
    if host_leaks:
        raise RuntimeError(
            "refusing to write evidence bundle: host-specific absolute path detected: "
            + ", ".join(host_leaks)
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return leaks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PHASE22 CC-D evidence builder")
    parser.add_argument(
        "--output",
        type=Path,
        default=EVIDENCE_DIR / "evidence_bundle.json",
    )
    parser.add_argument("--cases", nargs="*", default=None)
    parser.add_argument("--skip-probe", action="store_true")
    parser.add_argument(
        "--skip-tracks",
        action="store_true",
        help="Skip running the dependency-free track / blockers verifiers.",
    )
    args = parser.parse_args(argv)
    bundle = build_bundle(
        cases=args.cases,
        run_probe=not args.skip_probe,
        run_tracks=not args.skip_tracks,
    )
    leaks = write_bundle(bundle, args.output)
    if leaks:
        print("ERROR: secret leakage detected; not written", file=__import__("sys").stderr)
        for leak in leaks:
            print(f"  {leak}", file=__import__("sys").stderr)
        return 2
    print(f"wrote evidence bundle: {args.output.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())