from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"
WORK_PRODUCTS = PROGRAM_ROOT / "work-products"
LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
MANIFEST = PROGRAM_ROOT / "program-manifest.yaml"
CURRENT = PROGRAM_ROOT / "current.md"
CHECKLIST = PROGRAM_ROOT / "closure-checklist.md"
PHASE_FILE = PROGRAM_ROOT / "PHASE07_model-gateway-runtime.md"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "model-gateway-runtime-batch.md"
PRE_CLOSURE = REPO_ROOT / "docs" / "evidence" / "phase07-pre-closure.md"
CLOSURE = REPO_ROOT / "docs" / "evidence" / "phase07-coordinator-closure.md"
READINESS = WORK_PRODUCTS / "phase07-readiness.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _phase_target_not_current_requirements(ledger: str, phase_id: str) -> list[str]:
    gaps: list[str] = []
    for block in re.split(r"\n(?=  - requirement_id: )", ledger):
        if f'target_phase: "{phase_id}"' not in block:
            continue
        if "mandatory: true" not in block:
            continue
        if "current_status: target_not_current" in block:
            match = re.search(r"requirement_id:\s+([A-Z0-9-]+)", block)
            gaps.append(match.group(1) if match else f"unknown {phase_id} requirement")
    return gaps


def verify_phase07_post_closure_consistency() -> list[str]:
    errors: list[str] = []
    ledger_gaps = _phase_target_not_current_requirements(_read(LEDGER), "PHASE07")
    if ledger_gaps:
        errors.append("PHASE07 mandatory target_not_current remains: " + ", ".join(ledger_gaps))
    for label, path, phrases in [
        ("phase file", PHASE_FILE, ["status: completed"]),
        ("evidence", EVIDENCE, ["状态：`implementation_available` 证据", "Provider SDK 只存在"]),
        ("pre-closure evidence", PRE_CLOSURE, ["status: passed", "gate: pre_closure"]),
        ("closure decision", CLOSURE, ["status: approved", "coordinator_approval: approved", "phase07_state: completed"]),
        ("readiness", READINESS, ["current_phase_status: completed", "coordinator_approval: approved", "target_not_current: 0"]),
        ("manifest", MANIFEST, ["current_phase: PHASE08", "id: PHASE07", "state: completed", "id: PHASE08", "state: in_progress"]),
        ("current", CURRENT, ["current_phase: PHASE08", "PHASE07 completed", "PHASE08 in_progress"]),
        ("closure checklist", CHECKLIST, ["[x] PHASE07 Model Gateway Runtime"]),
    ]:
        text = _read(path)
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{label} missing phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify_phase07_post_closure_consistency()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE07 post-closure consistency gate failed.")
        return 1
    print("PHASE07 post-closure consistency gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
