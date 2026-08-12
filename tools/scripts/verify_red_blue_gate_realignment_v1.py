"""Verify the Gate Deadlock realignment record without changing product evidence."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-GATE-REALIGNMENT-001"
CANONICAL_SYNC_DOCS = (
    ROOT / "docs/project/architecture/architecture.md",
    ROOT / "docs/project/product/product-architecture.md",
    ROOT / "docs/project/domain/legal-domain-model.md",
    ROOT / "docs/project/domain/domain-state-lifecycle.md",
    ROOT / "docs/project/agents/agent-platform.md",
    ROOT / "docs/project/agents/multi-agent-runtime.md",
    ROOT / "docs/project/knowledge/knowledge-evidence-architecture.md",
    ROOT / "docs/project/services/service-architecture.md",
    ROOT / "docs/project/data/data-ownership-and-recovery.md",
    ROOT / "docs/project/security/security-architecture.md",
    ROOT / "docs/project/eval/legal-eval-and-benchmark.md",
    ROOT / "docs/project/deployment/microservice-deployment.md",
)
ORIGINAL_P0 = ["Q005", "Q016", "Q033", "Q039", "Q053", "Q061", "Q063", "Q064", "Q066", "Q067", "Q070", "Q097"]
DERIVED = ["Q005", "Q016", "Q033", "Q039-C", "Q039-B", "Q053", "Q061", "Q063", "Q064", "Q066", "Q067", "Q070", "Q097"]
REQUIRED_FILES = (
    "manifest.yaml",
    "README.md",
    "gate-dependency-graph.md",
    "closure-classification.md",
    "user-architecture-gate.md",
    "implementation-track.md",
    "benchmark-track.md",
    "external-qualification-track.md",
    "canonical-sync-plan.md",
    "final-report.md",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_session(session: Path = DEFAULT_SESSION) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (session / relative).exists():
            errors.append(f"missing Gate Realignment file: {relative}")
    if errors:
        return errors

    try:
        manifest = yaml.safe_load(_text(session / "manifest.yaml"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]

    expected = {
        "protocol_version": "ZUNO-GATE-REALIGNMENT-V1",
        "session_id": "RB-GATE-REALIGNMENT-001",
        "baseline_sha": "deda7eb551eb401808c40494cb193187cbd51101",
        "defense_base_sha": "deda7eb551eb401808c40494cb193187cbd51101",
        "status": "COMPLETED",
        "original_p0_count": 12,
        "derived_closure_record_count": 13,
        "original_p0_closed": 0,
        "user_architecture_gate": "APPROVED",
        "canonical_sync_status": "APPLIED",
        "round_002_status": "READY_NOT_STARTED",
        "implementation_program": "READY_FOR_TASK_DEFINITION",
        "runtime_changes": "NONE",
        "schema_or_migration_changes": "NONE",
        "canonical_facts_changed": "NONE",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"manifest {key} must be {value!r}")
    if manifest.get("closure_class_counts") != {
        "architecture_blocking": 0,
        "implementation_blocking": 11,
        "evidence_measurement_blocking": 1,
        "external_qualification_blocking": 1,
    }:
        errors.append("manifest closure_class_counts must be 0/11/1/1")

    classification = _text(session / "closure-classification.md")
    rows: dict[str, str] = {}
    row_pattern = re.compile(r"^\|\s*([^|]+?)\s*\|\s*P0\s*\|\s*(P0-[AIEX])\s*\|")
    for line in classification.splitlines():
        match = row_pattern.match(line)
        if match:
            rows[match.group(1).strip()] = match.group(2)
    if list(rows) != DERIVED:
        errors.append(f"closure classification rows must be {DERIVED}, got {list(rows)}")
    if list(rows.values()).count("P0-A") != 0:
        errors.append("closure classification must contain zero P0-A rows")
    if list(rows.values()).count("P0-I") != 11:
        errors.append("closure classification must contain eleven P0-I rows")
    if list(rows.values()).count("P0-E") != 1:
        errors.append("closure classification must contain one P0-E row")
    if list(rows.values()).count("P0-X") != 1:
        errors.append("closure classification must contain one P0-X row")
    for identifier in ORIGINAL_P0:
        if identifier not in classification:
            errors.append(f"closure classification missing original P0 {identifier}")
    if "Q039-C" not in classification or "Q039-B" not in classification:
        errors.append("closure classification must retain Q039 scope split")
    for marker in ("Original P0: 12", "Derived closure records: 13", "Original P0 closed: 0 / 12"):
        if marker not in classification:
            errors.append(f"closure-classification.md missing {marker}")

    graph = _text(session / "gate-dependency-graph.md")
    for marker in (
        "Final P0 = 0",
        "Implementation Task",
        "V4 closure-grade evidence",
        "这是 Governance Deadlock",
        "A-P0 = 0",
        "I-P0 必须有 Target Contract",
        "用户 Gate 必须由用户明确记录",
    ):
        if marker not in graph:
            errors.append(f"gate-dependency-graph.md missing {marker}")

    package = _text(session / "user-architecture-gate.md")
    for marker in (
        "Status: APPROVED",
        "User decision: APPROVE",
        "Canonical Sync: APPLIED",
        "Approved scope: Canonical Part-A Target Architecture only",
        "## 1. Product / Architecture Thesis",
        "## 3. Canonical State Ownership",
        "## 4. Runtime vs Domain State",
        "## 5. Tool Side-effect Contract",
        "## 6. Memory Contract / Provider Boundary",
        "## 7. Knowledge / Graph Boundary",
        "## 8. Database / Projection Ownership",
        "## 9. Microservice Boundary Candidates",
        "## 10. Security / Sandbox Boundary",
        "## 11. Eval Architecture",
        "## 12. 12 P0 Gate Classification",
        "## 22. Proposed first Codex implementation tasks",
        "不能在本轮执行",
    ):
        if marker not in package:
            errors.append(f"user-architecture-gate.md missing {marker}")
    for marker in ("A=0 / I=11 / E=1 / X=1", "Q039-B", "Q066", "APPROVED", "ACCEPTED_TARGET"):
        if marker not in _text(session / "README.md") + package:
            errors.append(f"Gate record missing {marker}")

    plan = _text(session / "canonical-sync-plan.md")
    for marker in ("Status: APPLIED", "User Gate: APPROVED", "Applied Commit SHA: recorded in final handoff"):
        if marker not in plan:
            errors.append(f"canonical-sync-plan.md missing {marker}")

    final = _text(session / "final-report.md")
    for marker in (
        "BASE_SHA: deda7eb551eb401808c40494cb193187cbd51101",
        "Original P0: 12",
        "Derived closure records: 13",
        "A-P0: 0",
        "I-P0: 11",
        "E-P0: 1",
        "X-P0: 1",
        "Original P0 closed: 0 / 12",
        "User Architecture Gate: APPROVED",
        "Canonical Sync: APPLIED",
        "Architecture State: ACCEPTED_TARGET",
        "Runtime / UI / Schema / Migration changed: NONE",
        "Production Readiness: NOT_ESTABLISHED (UNCHANGED)",
        "Full CI: NOT_RUN",
    ):
        if marker not in final:
            errors.append(f"final-report.md missing {marker}")

    original = ROOT / "project-reconstruction-lab" / "sessions" / "RB-P0-V4-EXECUTION-001"
    if not (original / "final-report.md").exists():
        errors.append("original V4 final report is missing")
    else:
        original_report = _text(original / "final-report.md")
        for marker in ("V4 Accepted: 0 / 12", "P0 Closed: 0 / 12", "Historical Facts changed: NONE", "Runtime changed: NONE"):
            if marker not in original_report:
                errors.append(f"original V4 record no longer contains {marker}")
        for p0_id in ORIGINAL_P0:
            if not (original / "p0" / f"{p0_id}.md").exists():
                errors.append(f"original V4 P0 record missing: {p0_id}")

    policy = ROOT / "docs" / "governance" / "architecture-gate-policy.md"
    if not policy.exists():
        errors.append("missing docs/governance/architecture-gate-policy.md")
    else:
        policy_text = _text(policy)
        for marker in ("Severity 与 Closure Class 分离", "A-P0 = 0", "I-P0 = 0", "E-P0 = 0", "X-P0 = 0", "PENDING_USER_DECISION"):
            if marker not in policy_text:
                errors.append(f"architecture-gate-policy.md missing {marker}")
    for path in CANONICAL_SYNC_DOCS:
        if not path.exists():
            errors.append(f"Canonical Sync document is missing: {path.relative_to(ROOT)}")
        elif "architecture_state: ACCEPTED_TARGET" not in _text(path):
            errors.append(f"Canonical Sync document lacks ACCEPTED_TARGET: {path.relative_to(ROOT)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Gate Realignment V1 record")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_session(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue Gate Realignment V1 verification passed: 12 original P0s, 0 A-P0, Part-A Target approved and synced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
