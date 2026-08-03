"""PHASE22 CC-D detached post-write verifier runner.

The evidence builder does not run its own verifier (a self-verification
loop would validate the previous artifact, not the bundle being written).
Instead, after the bundle is on disk, the orchestrator invokes this
script which:

1. Computes the SHA-256 of the bundle it is about to verify.
2. Launches the CC-D verifier as a subprocess.
3. Captures the verifier's real exit code, stdout, and stderr.
4. Writes ``detached_verification_report.json`` next to the bundle.

The report carries the artifact path and hash so the verifier cannot
self-validate: the hash that ends up in the report is the hash of the
bundle the verifier actually saw, computed before the verifier runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
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
DEFAULT_BUNDLE_PATH = EVIDENCE_DIR / "evidence_bundle.json"
DEFAULT_REPORT_PATH = EVIDENCE_DIR / "detached_verification_report.json"

VERIFY_CC_D_REL = "tools/scripts/verify_phase22_cc_d_evidence.py"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonicalize_argv(argv: list[str]) -> dict[str, Any]:
    if not argv:
        return {"executable": "", "script": "", "args": []}

    exe = argv[0]
    rest = list(argv[1:])
    exe_lower = exe.lower()
    is_python = (
        exe_lower.endswith("python")
        or exe_lower.endswith("python.exe")
        or exe_lower.endswith("python3")
        or Path(exe).name.lower() in {"python", "python3", "python.exe", "python3.exe"}
    )
    canonical_exe = "python" if is_python else exe

    canonical_script = ""
    canonical_args: list[str] = []
    if rest and is_python:
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
    if not argv:
        return ""
    canonical = _canonicalize_argv(argv)
    if canonical["script"]:
        return " ".join(
            [canonical["executable"], canonical["script"], *canonical["args"]]
        )
    return " ".join([canonical["executable"], *canonical["args"]])


def run_detached_verification(
    *,
    bundle_path: Path,
    report_path: Path,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Run the CC-D verifier on ``bundle_path`` and write a detached report."""

    if not bundle_path.exists():
        raise FileNotFoundError(f"bundle not found: {bundle_path.as_posix()}")

    artifact_hash = _sha256_file(bundle_path)
    artifact_size = bundle_path.stat().st_size

    argv = [sys.executable, str(REPO_ROOT / VERIFY_CC_D_REL)]
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
        return _build_report(
            bundle_path=bundle_path,
            report_path=report_path,
            artifact_hash=artifact_hash,
            artifact_size=artifact_size,
            argv=argv,
            started_at=started_at,
            elapsed=elapsed,
            launched=True,
            exit_code=None,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else "",
            status="TIMEOUT",
            error=f"subprocess exceeded timeout={timeout}s",
        )
    elapsed = time.monotonic() - start
    status = "PASSED" if proc.returncode == 0 else "FAILED"
    return _build_report(
        bundle_path=bundle_path,
        report_path=report_path,
        artifact_hash=artifact_hash,
        artifact_size=artifact_size,
        argv=argv,
        started_at=started_at,
        elapsed=elapsed,
        launched=True,
        exit_code=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        status=status,
    )


def _build_report(
    *,
    bundle_path: Path,
    report_path: Path,
    artifact_hash: str,
    artifact_size: int,
    argv: list[str],
    started_at: str,
    elapsed: float,
    launched: bool,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    status: str,
    error: str | None = None,
) -> dict[str, Any]:
    canonical = _canonicalize_argv(argv)
    report = {
        "schema_version": "1.0.0",
        "report_kind": "phase22_cc_d_detached_verification",
        "verified_at": _utc_now_iso(),
        "artifact_path": str(bundle_path.relative_to(REPO_ROOT)),
        "artifact_hash_sha256": artifact_hash,
        "artifact_size_bytes": artifact_size,
        "command": {
            "executable": canonical["executable"],
            "script": canonical["script"],
            "args": canonical["args"],
            "command": _command_string_from_argv(argv),
        },
        "started_at": started_at,
        "ended_at": _utc_now_iso(),
        "elapsed_seconds": round(elapsed, 3),
        "launched": launched,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "status": status,
    }
    if error is not None:
        report["error"] = error

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(payload, encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PHASE22 CC-D detached post-write verifier runner"
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        default=DEFAULT_BUNDLE_PATH,
        help="Path to the evidence bundle to verify.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Where to write the detached verification report.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Verifier subprocess timeout in seconds.",
    )
    args = parser.parse_args(argv)

    try:
        report = run_detached_verification(
            bundle_path=args.bundle,
            report_path=args.report,
            timeout=args.timeout,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if report["status"] == "PASSED":
        print(
            f"detached verification passed; report at {args.report.as_posix()}; "
            f"artifact_hash={report['artifact_hash_sha256'][:16]}***"
        )
        return 0
    print(
        f"detached verification failed (exit_code={report['exit_code']}); "
        f"report at {args.report.as_posix()}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())