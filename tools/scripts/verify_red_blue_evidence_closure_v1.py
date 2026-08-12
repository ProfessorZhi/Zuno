"""Verify the recorded RB-EVIDENCE-CLOSURE-001 evidence campaign."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-EVIDENCE-CLOSURE-001"
P0_IDS = ["Q005", "Q016", "Q033", "Q039", "Q053", "Q061", "Q063", "Q064", "Q066", "Q067", "Q070", "Q097"]
RC_IDS = [f"RC-{index:03d}" for index in range(1, 11)]
REQUIRED_FILES = (
    "manifest.yaml",
    "README.md",
    "evidence-matrix.md",
    "verification-plan.md",
    "red-evidence-review.md",
    "blue-actions.md",
    "counter-retest.md",
    "scorecard.md",
    "closure-report.md",
    "results/command-log.md",
    "results/evidence-levels.md",
    "experiments/README.md",
)
ALLOWED_STATUSES = {
    "UNPLANNED",
    "PLAN_READY",
    "READY_TO_EXECUTE",
    "EXECUTED_PASS",
    "EXECUTED_FAIL",
    "BLOCKED_EXTERNAL",
    "BLOCKED_FACT",
    "USER_GATE_REQUIRED",
    "RED_REVIEW_PENDING",
    "COUNTER_RETEST_PENDING",
    "CLOSED",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_session(session: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (session / relative).exists():
            errors.append(f"missing evidence closure file: {relative}")
    for index in range(1, 13):
        if not (session / "p0" / f"P0-{index:03d}.md").exists():
            errors.append(f"missing P0 package: P0-{index:03d}.md")
    if errors:
        return errors

    try:
        manifest = yaml.safe_load(_text(session / "manifest.yaml"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]

    expected = {
        "protocol_version": "ZUNO-EVIDENCE-CLOSURE-V1",
        "session_id": "RB-EVIDENCE-CLOSURE-001",
        "source_repair_session": "RB-BLUE-REPAIR-001",
        "canonical_sync_status": "NOT_APPLIED",
        "user_architecture_gate": "PENDING",
        "round_002_status": "BLOCKED",
        "status": "COUNTER_RETEST_PENDING",
        "root_cause_cluster_count": 10,
        "final_p0_count": 12,
        "closed_p0_count": 0,
        "executed_p0_count": 10,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"manifest {key} must be {value!r}")
    critical = manifest.get("critical_closure") or {}
    if critical != {"closed_p0": 0, "final_p0": 12, "percentage": 0}:
        errors.append("critical_closure must be exactly 0/12 and 0 percent")
    coverage = manifest.get("evidence_coverage") or {}
    if coverage.get("closure_grade_items") != 0 or coverage.get("total_items") != 12 or coverage.get("percentage") != 0:
        errors.append("evidence_coverage must be 0/12 and 0 percent")

    matrix = _text(session / "evidence-matrix.md")
    matrix_ids = re.findall(r"(?m)^\|\s*(EV-CLOSE-\d{3})\s*\|", matrix)
    if matrix_ids != [f"EV-CLOSE-{index:03d}" for index in range(1, 13)]:
        errors.append("evidence-matrix.md must contain EV-CLOSE-001..012 in order")
    matrix_p0 = re.findall(r"(?m)^\|\s*EV-CLOSE-\d{3}\s*\|\s*RC-\d{3}\s*\|\s*(Q\d{3})\s*\|", matrix)
    if matrix_p0 != P0_IDS:
        errors.append("evidence-matrix.md must contain the 12 Final P0 IDs in order")
    if matrix.count("| OPEN |") != 12:
        errors.append("evidence-matrix.md must keep all 12 Final Closure cells OPEN")
    statuses = re.findall(r"(?m)^\|\s*EV-CLOSE-\d{3}\s*\|[^\n]*?\|\s*(%s)\s*\|" % "|".join(ALLOWED_STATUSES), matrix)
    if len(statuses) != 12:
        errors.append("evidence-matrix.md must provide one allowed Status for every P0")
    if "| CLOSED |" in matrix:
        errors.append("evidence-matrix.md must not mark a P0 CLOSED before retest")

    for index, p0_id in enumerate(P0_IDS, start=1):
        package = _text(session / "p0" / f"P0-{index:03d}.md")
        for marker in (
            f"P0 ID: `{p0_id}`",
            "Architecture Claim:",
            "Risk:",
            "Closure Condition:",
            "Required Evidence:",
            "Evidence Strength Target:",
            "Verification Method:",
            "Environment:",
            "Inputs:",
            "Expected Result:",
            "Failure Result:",
            "Artifact Path:",
            "Owner:",
            "Status:",
            "Red Review:",
            "Blue Action:",
            "Counter Retest:",
            "Final Closure: `OPEN`",
        ):
            if marker not in package:
                errors.append(f"P0-{index:03d}.md missing {marker}")

    review = _text(session / "red-evidence-review.md")
    if "Accepted closure evidence: 0 / 12" not in review or "Counter Retest: not run" not in review:
        errors.append("red-evidence-review.md must reject closure for all P0s")
    if not all(f"| {p0_id} |" in review for p0_id in P0_IDS):
        errors.append("red-evidence-review.md must review every Final P0")

    retest = _text(session / "counter-retest.md")
    if len(re.findall(r"(?m)^\| CRT-Q\d{3} \|", retest)) != 12:
        errors.append("counter-retest.md must contain 12 retest rows")
    if "Counter Retest Status: NOT_RUN" not in retest or "Final P0 closed: 0 / 12" not in retest:
        errors.append("counter-retest.md must keep retest not run and closure at 0/12")

    scorecard = _text(session / "scorecard.md")
    for marker in ("Closure-grade Evidence", "0 / 12 = 0%", "`Measured Complexity` 为 `0 / 10`", "RC-001", "RC-010", "Round-002: BLOCKED"):
        if marker not in scorecard:
            errors.append(f"scorecard.md missing {marker}")
    if not all(f"| RC-{index:03d} |" in scorecard for index in range(1, 11)):
        errors.append("scorecard.md must report RC-001..RC-010")

    closure = _text(session / "closure-report.md")
    for marker in ("P0 CLOSED: 0 / 12", "Closure-grade Evidence: 0 / 12 = 0%", "Counter Retest: NOT_RUN", "Canonical Docs Sync: NOT_APPLIED"):
        if marker not in closure:
            errors.append(f"closure-report.md missing {marker}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Evidence Closure V1 record")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_session(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue Evidence Closure V1 verification passed: 12 Final P0s, 0 closed, counter retest pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
