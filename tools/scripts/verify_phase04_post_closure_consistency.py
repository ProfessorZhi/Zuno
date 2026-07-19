from __future__ import annotations

import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
PHASE04_READINESS = WORK_PRODUCTS / "phase04-readiness.yaml"
REQUIREMENT_LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
PROGRAM_MANIFEST = REPO_ROOT / ".agent" / "programs" / "program-manifest.yaml"
CURRENT_PROGRAM = REPO_ROOT / ".agent" / "programs" / "current.md"
ROADMAP = REPO_ROOT / ".agent" / "programs" / "implementation-roadmap.md"
CLOSURE_CHECKLIST = REPO_ROOT / ".agent" / "programs" / "closure-checklist.md"
PRODUCTION_READINESS = REPO_ROOT / "docs" / "status" / "production-readiness.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix in {".md", ".yaml", ".yml", ".txt"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _phase04_target_not_current_requirements(ledger: str) -> list[str]:
    gaps: list[str] = []
    for block in re.split(r"\n(?=  - requirement_id: )", ledger):
        if 'target_phase: "PHASE04"' not in block:
            continue
        if "mandatory: true" not in block:
            continue
        if "current_status: target_not_current" in block:
            match = re.search(r"requirement_id:\s+([A-Z0-9-]+)", block)
            gaps.append(match.group(1) if match else "unknown PHASE04 requirement")
    return gaps


def _current_status_counts_are_self_consistent(ledger: str) -> bool:
    declared_match = re.search(
        r"(?ms)^current_status_counts:\n(?P<body>(?:  [^\n]+\n)+)",
        ledger,
    )
    if declared_match is None:
        return False
    declared: dict[str, int] = {}
    for line in declared_match.group("body").splitlines():
        item = re.match(r"\s+([^:]+):\s+(\d+)\s*$", line)
        if item:
            declared[item.group(1)] = int(item.group(2))
    actual: dict[str, int] = {}
    for status in re.findall(r"(?m)^\s+current_status:\s+([^\r\n]+)\s*$", ledger):
        actual[status] = actual.get(status, 0) + 1
    return declared == actual


def _evidence_hashes(readiness: str) -> dict[str, str]:
    match = re.search(r"(?ms)^evidence_hashes:\n(?P<body>(?:  .+\n)+)", readiness)
    if match is None:
        return {}
    hashes: dict[str, str] = {}
    for line in match.group("body").splitlines():
        item = re.match(r'\s+"([^"]+)":\s+"([0-9a-f]{64})"\s*$', line)
        if item:
            hashes[item.group(1)] = item.group(2)
    return hashes


def verify_phase04_post_closure_consistency() -> list[str]:
    errors: list[str] = []
    readiness = _read(PHASE04_READINESS)
    ledger = _read(REQUIREMENT_LEDGER)
    manifest = _read(PROGRAM_MANIFEST)
    current = _read(CURRENT_PROGRAM)
    roadmap = _read(ROADMAP)
    checklist = _read(CLOSURE_CHECKLIST)
    production = _read(PRODUCTION_READINESS)

    for task_id in [f"P04-T{index:02d}" for index in range(1, 8)]:
        if re.search(rf"(?s){task_id}:\s*\n\s+state:\s+completed\b", readiness) is None:
            errors.append(f"{task_id} is not completed in phase04-readiness.yaml")
    for phrase in [
        "current_phase_status: completed",
        "coordinator_approval: approved",
        "may_start_phase05_after_validation: true",
    ]:
        if phrase not in readiness:
            errors.append(f"phase04-readiness.yaml missing closure phrase: {phrase}")
    if not _current_status_counts_are_self_consistent(ledger):
        errors.append("Requirement Ledger current_status_counts are not self-consistent")
    gaps = _phase04_target_not_current_requirements(ledger)
    if gaps:
        errors.append("PHASE04 mandatory target_not_current remains: " + ", ".join(gaps))

    for phrase in [
        "current_phase: PHASE05",
        "{id: PHASE04, file: .agent/programs/PHASE04_postgres-domain-and-transaction-foundation.md, state: completed",
        "{id: PHASE05, file: .agent/programs/PHASE05_security-control-plane.md, state: ready",
    ]:
        if phrase not in manifest:
            errors.append(f"program-manifest.yaml missing closure phrase: {phrase}")
    for phrase in [
        "current_phase: PHASE05",
        "PHASE04 completed",
        "PHASE05 ready",
    ]:
        if phrase not in current:
            errors.append(f"current.md missing closure phrase: {phrase}")
    for label, text in [
        ("implementation-roadmap.md", roadmap),
        ("closure-checklist.md", checklist),
        ("production-readiness.md", production),
    ]:
        for phrase in ["PHASE04 completed", "PHASE05 ready"]:
            if phrase not in text:
                errors.append(f"{label} missing closure phrase: {phrase}")

    hashes = _evidence_hashes(readiness)
    if not hashes:
        errors.append("phase04-readiness.yaml has no evidence_hashes manifest")
    for relative_path, expected_hash in hashes.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"evidence hash path missing: {relative_path}")
            continue
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            errors.append(
                f"evidence hash mismatch for {relative_path}: {actual_hash} != {expected_hash}"
            )
    return errors


def main() -> int:
    errors = verify_phase04_post_closure_consistency()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 post-closure consistency gate failed.")
        return 1
    print("PHASE04 post-closure consistency gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
