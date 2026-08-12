"""Verify the RB-BLUE-REPAIR-001 root-cause repair record."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-BLUE-REPAIR-001"
REQUIRED_FILES = (
    "manifest.yaml",
    "root-cause-clusters.md",
    "part-a-blue-repair.md",
    "repair-scorecard.md",
    "counter-retest.md",
    "round-closure.md",
)
EXPECTED_CLUSTERS = [f"RC-{index:03d}" for index in range(1, 11)]
EXPECTED_P0 = {5, 16, 33, 39, 53, 61, 63, 64, 66, 67, 70, 97}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_repair(session: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (session / name).exists():
            errors.append(f"missing repair file: {name}")
    if errors:
        return errors

    try:
        manifest = yaml.safe_load(_text(session / "manifest.yaml"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]

    expected_markers = {
        "protocol_version": "ZUNO-BLUE-REPAIR-V1",
        "source_round_id": "RB-WORKFLOW-V2-001",
        "status": "COUNTER_RETEST_REOPENED",
        "counter_retest_status": "REOPENED_PENDING_EVIDENCE",
        "canonical_sync_status": "NOT_APPLIED",
        "user_architecture_gate": "PENDING",
        "round_002_status": "BLOCKED",
    }
    for key, expected in expected_markers.items():
        if manifest.get(key) != expected:
            errors.append(f"manifest {key} must be {expected}")
    if manifest.get("root_cause_cluster_count") != 10 or manifest.get("source_question_count") != 100:
        errors.append("manifest must declare 10 root clusters and 100 source questions")
    if manifest.get("source_severity") != {"p0": 58, "p1": 42}:
        errors.append("manifest source severity must be P0=58/P1=42")
    if manifest.get("final_severity") != {"p0": 12, "p1": 46, "p2": 32, "p3": 10}:
        errors.append("manifest final severity must be P0=12/P1=46/P2=32/P3=10")
    critical = manifest.get("critical_closure") or {}
    if critical.get("closed_p0") != 0 or critical.get("final_p0") != 12 or critical.get("percentage") != 0:
        errors.append("critical closure must be 0/12 and 0 percent")

    clusters = _text(session / "root-cause-clusters.md")
    cluster_ids = re.findall(r"(?m)^## (RC-\d{3})\s*$", clusters)
    if not cluster_ids:
        cluster_ids = re.findall(r"(?m)^\|\s*(RC-\d{3})\s*\|", clusters)
    if cluster_ids != EXPECTED_CLUSTERS:
        errors.append("root-cause-clusters.md must contain RC-001..RC-010 in order")
    for cluster_id in EXPECTED_CLUSTERS:
        section_match = re.search(
            rf"(?ms)^## {cluster_id}\s*\n(.*?)(?=^## RC-\d{{3}}\s*$|\Z)", clusters
        )
        if not section_match:
            continue
        section = section_match.group(1)
        for marker in ("Questions", "Initial P0/P1", "Final P0/P1/P2/P3", "Blue Repair"):
            if marker not in section:
                errors.append(f"{cluster_id} missing {marker}")

    part_a = _text(session / "part-a-blue-repair.md")
    for marker in (
        "Problem / Goal",
        "Product Context",
        "Architectural Drivers",
        "System Context",
        "Domain Boundary",
        "Canonical Owner",
        "State Ownership",
        "Main Runtime",
        "Trust Boundary",
        "Tool Effect Contract",
        "Data / Provider Boundary",
        "Happy / Failure / Recovery",
        "Physical Service Boundary",
        "Reversal Criteria",
        "CANONICAL_SYNC_NOT_APPLIED",
    ):
        if marker not in part_a:
            errors.append(f"part-a-blue-repair.md missing {marker}")

    scorecard = _text(session / "repair-scorecard.md")
    for marker in (
        "Answer Quality",
        "Architecture Fitness",
        "Evidence Coverage",
        "Critical Closure",
        "Complexity Justification",
        "72.2",
        "91.4",
        "0/12 = 0%",
        "P0=12",
        "Q097",
        "Round Pass = FALSE",
    ):
        if marker not in scorecard:
            errors.append(f"repair-scorecard.md missing {marker}")
    p0_questions = {
        int(value)
        for value in re.findall(r"(?m)^\|\s*Q(\d{3})\s*\|", scorecard)
    }
    listed_p0 = {
        int(value)
        for value in re.findall(r"(?m)^\|\s*Q(\d{3})\s*\|[^\n]*OPEN\s*\|?\s*$", scorecard)
    }
    if not EXPECTED_P0.issubset(p0_questions):
        errors.append("repair-scorecard.md must list every Final P0 question")
    if not EXPECTED_P0.issubset(listed_p0):
        errors.append("repair-scorecard.md must keep every Final P0 OPEN")

    retest = _text(session / "counter-retest.md")
    retest_ids = re.findall(r"(?m)^## (RETEST-RC-\d{3})\s*$", retest)
    if retest_ids != [f"RETEST-RC-{index:03d}" for index in range(1, 11)]:
        errors.append("counter-retest.md must contain RETEST-RC-001..010 in order")
    if len(re.findall(r"(?m)^- Result[：:]\s*`REOPEN`$", retest)) != 9:
        errors.append("counter-retest.md must contain 9 REOPEN results")
    if not re.search(r"(?m)^- Result[：:]\s*`WAITING_FOR_EVIDENCE`$", retest):
        errors.append("counter-retest.md must contain one WAITING_FOR_EVIDENCE result")
    if "Final P0 closed              0 / 12" not in retest:
        errors.append("counter-retest.md must declare 0/12 Final P0 closed")

    closure = _text(session / "round-closure.md")
    for marker in (
        "BLUE_REPAIR_COMPLETE / COUNTER_RETEST_REOPENED / ROUND-001_NOT_CLOSED",
        "58 / 42",
        "12 / 46 / 32 / 10",
        "0 / 12",
        "Round-002                             BLOCKED",
        "Canonical Docs Changed: NONE",
        "User Architecture Gate: PENDING",
    ):
        if marker not in closure:
            errors.append(f"round-closure.md missing {marker}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Blue Repair V1 record")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_repair(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue Blue Repair V1 verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
