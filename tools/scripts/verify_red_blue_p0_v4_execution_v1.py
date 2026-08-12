"""Verify the recorded RB-P0-V4-EXECUTION-001 campaign."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-P0-V4-EXECUTION-001"
ORIGINAL_P0 = ["Q005", "Q016", "Q033", "Q039", "Q053", "Q061", "Q063", "Q064", "Q066", "Q067", "Q070", "Q097"]
REQUIRED_FILES = (
    "manifest.yaml",
    "README.md",
    "scope-audit.md",
    "execution-matrix.md",
    "track-a-state-recovery.md",
    "track-b-tool-effect.md",
    "track-c-security.md",
    "track-d-legal-evidence.md",
    "red-evidence-review.md",
    "counter-retest.md",
    "closure-scorecard.md",
    "canonical-sync-candidate.md",
    "final-report.md",
    "results/command-log.md",
    "results/fixtures/README.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_session(session: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (session / relative).exists():
            errors.append(f"missing V4 session file: {relative}")
    for p0_id in ORIGINAL_P0:
        if not (session / "p0" / f"{p0_id}.md").exists():
            errors.append(f"missing P0 execution record: {p0_id}.md")
    if errors:
        return errors

    try:
        manifest = yaml.safe_load(_text(session / "manifest.yaml"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]
    expected = {
        "protocol_version": "ZUNO-P0-V4-EXECUTION-V1",
        "session_id": "RB-P0-V4-EXECUTION-001",
        "source_evidence_closure_session": "RB-EVIDENCE-CLOSURE-001",
        "baseline_sha": "71630f16edf027b610e9b0ca7f17a6a4c0fc9080",
        "round_002_status": "BLOCKED",
        "canonical_sync_status": "NOT_APPLIED",
        "user_architecture_gate": "PENDING",
        "runtime_changes": "NONE",
        "schema_or_migration_changes": "NONE",
        "original_p0_count": 12,
        "scope_split_count": 1,
        "v4_execution_records": 6,
        "v3_or_narrow_records": 4,
        "v4_accepted": 0,
        "counter_retest_passed": 0,
        "p0_closed": 0,
        "p0_open": 12,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"manifest {key} must be {value!r}")

    matrix = _text(session / "execution-matrix.md")
    for p0_id in ORIGINAL_P0:
        if p0_id == "Q039":
            if "| Q039-C |" not in matrix or "| Q039-B |" not in matrix:
                errors.append("execution-matrix.md missing Q039 scope split")
            continue
        if not re.search(rf"(?m)^\| {re.escape(p0_id)} \|", matrix):
            errors.append(f"execution-matrix.md missing original P0 {p0_id}")
    if "| Q039-C |" not in matrix or "| Q039-B |" not in matrix:
        errors.append("execution-matrix.md must retain Q039-C and Q039-B scope split")
    if matrix.count("| OPEN |") < 12:
        errors.append("execution-matrix.md must keep all original P0 closure cells OPEN")
    if "| V4 accepted by Red | 0 / 12 |" not in _text(session / "closure-scorecard.md"):
        errors.append("closure-scorecard.md must record zero Red-accepted V4 evidence")

    audit = _text(session / "scope-audit.md")
    for marker in ("Original P0", "Q039-C", "Q039-B", "SCOPE_SPLIT_ACCEPTED", "原始 P0 不得"):
        if marker not in audit:
            errors.append(f"scope-audit.md missing {marker}")

    review = _text(session / "red-evidence-review.md")
    for p0_id in ORIGINAL_P0:
        if p0_id not in review:
            errors.append(f"red-evidence-review.md missing {p0_id}")
    if "ACCEPT_EVIDENCE: 0" not in review or "Counter Retest: NOT_RUN" not in review:
        errors.append("red-evidence-review.md must reject closure acceptance")

    retest = _text(session / "counter-retest.md")
    if "Counter Retest: NOT_RUN" not in retest or "P0 Closed: 0 / 12" not in retest:
        errors.append("counter-retest.md must remain NOT_RUN and 0/12")

    report = _text(session / "final-report.md")
    for marker in (
        "V4 Accepted: 0 / 12",
        "P0 Closed: 0 / 12",
        "Implementation-dependent: 4",
        "External-blocked: 1",
        "V5 Benchmark Gaps: 1",
        "Historical Facts changed: NONE",
        "Runtime changed: NONE",
        "Canonical docs changed: NONE",
    ):
        if marker not in report:
            errors.append(f"final-report.md missing {marker}")

    for p0_id in ORIGINAL_P0:
        package = _text(session / "p0" / f"{p0_id}.md")
        for marker in (
            f"P0 ID: `{p0_id}`",
            "Architecture Claim:",
            "Scope:",
            "Verification Level:",
            "Environment:",
            "Command:",
            "Fixture / Input:",
            "Fault Injected:",
            "Expected:",
            "Actual:",
            "Exit Code:",
            "Trace:",
            "State Before:",
            "State After:",
            "Evidence Artifact:",
            "Limitations:",
            "Cannot Infer:",
            "Red Decision:",
            "Counter Retest:",
            "Final Status:",
        ):
            if marker not in package:
                errors.append(f"{p0_id}.md missing {marker}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno P0 V4 execution record")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_session(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue P0 V4 execution verification passed: 12 P0 records, 0 accepted, 0 closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
