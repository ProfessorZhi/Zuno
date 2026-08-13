"""Verify that the Red/Blue workspace is reset and no round is active.

This verifier checks only the current governance boundary.  Historical round
verifiers remain responsible for their immutable artifacts and are not called
as part of this check.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = REPO_ROOT / "project-reconstruction-lab"
RED_BLUE_ROOT = LAB_ROOT / "05-red-blue"
SESSIONS_ROOT = LAB_ROOT / "sessions"
RESET_SESSION = SESSIONS_ROOT / "RB-RESET-001"

REQUIRED_ACTIVE_FILES = {
    "README.md",
    "principles.md",
    "workflow-status.md",
    "history/README.md",
}
POINTER_FILES = {
    "11-plus-1-canonical-coverage-map.md",
    "evidence-closure-protocol.md",
    "round-protocol-v2.md",
    "round-protocol-v3.md",
    "round-protocol-v3.1.md",
    "round-protocol-v3.1.2.md",
    "round-protocol-v3.1.3.md",
    "round-protocol-v4.md",
    "round-protocol-v4.1.md",
    "round-protocol-v4.2.md",
    "v4/README.md",
    "v4.1/README.md",
    "v4.1/interview-calibration-packet.md",
    "v4.2/README.md",
}
RESET_FILES = {
    "README.md",
    "red-blue-inventory.md",
    "protocol-lineage.md",
    "active-vs-history-map.md",
    "legacy-verifier-map.md",
    "routing-impact.md",
    "reset-plan.md",
}


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []

    if not RED_BLUE_ROOT.is_dir():
        return ["missing project-reconstruction-lab/05-red-blue"]

    files = {
        path.relative_to(RED_BLUE_ROOT).as_posix()
        for path in RED_BLUE_ROOT.rglob("*")
        if path.is_file()
    }
    missing = sorted(REQUIRED_ACTIVE_FILES - files)
    for path in missing:
        errors.append(f"missing reset entry: project-reconstruction-lab/05-red-blue/{path}")

    for path in sorted(POINTER_FILES):
        if path not in files:
            errors.append(f"missing historical compatibility pointer: {path}")
            continue
        content = _read(RED_BLUE_ROOT / path)
        if not content.startswith("# Historical compatibility pointer"):
            errors.append(f"active legacy path is not a compatibility pointer: {path}")
        if "not an active protocol" not in content.lower() and "historical" not in content.lower():
            errors.append(f"compatibility pointer does not declare history-only status: {path}")

    active_root_files = {
        path.relative_to(RED_BLUE_ROOT).as_posix()
        for path in RED_BLUE_ROOT.iterdir()
        if path.is_file()
    }
    unexpected_root_files = sorted(active_root_files - {"README.md", "principles.md", "workflow-status.md"} - POINTER_FILES)
    for path in unexpected_root_files:
        errors.append(f"unexpected active Red/Blue file: {path}")

    status_path = RED_BLUE_ROOT / "workflow-status.md"
    if status_path.exists():
        status = _read(status_path)
        expected_markers = {
            "RED_BLUE_STATE: RESET",
            "ACTIVE_PROTOCOL: NONE",
            "ACTIVE_ROUND: NONE",
            "ROUND_007: CANCELLED_BEFORE_START",
            "NEXT_ROUND: NOT_SCHEDULED",
            "ARCHITECTURE_READABILITY_GATE: IN_PROGRESS",
            "FINAL_MODULE_COUNT: NOT_DECIDED",
        }
        for marker in sorted(expected_markers):
            if marker not in status:
                errors.append(f"workflow-status.md missing marker: {marker}")
        for forbidden in ("100Q", "BATCH_ADVERSARIAL", "LIVE_ADAPTIVE", "questions_frozen_sha"):
            if forbidden in status:
                errors.append(f"workflow-status.md contains retired protocol detail: {forbidden}")

    readme_path = RED_BLUE_ROOT / "README.md"
    if readme_path.exists():
        readme = _read(readme_path)
        for marker in ("RESET / PAUSED", "ACTIVE_PROTOCOL: NONE", "Round-007", "history/"):
            if marker not in readme:
                errors.append(f"README.md missing reset boundary marker: {marker}")

    principles_path = RED_BLUE_ROOT / "principles.md"
    if principles_path.exists():
        principles = _read(principles_path)
        principles_body = principles.split("## 不在本文定义", 1)[0]
        for marker in ("必要", "Owner", "失败", "恢复", "替代方案", "删除"):
            if marker not in principles_body:
                errors.append(f"principles.md missing stable principle: {marker}")

    if not RESET_SESSION.is_dir():
        errors.append("missing RB-RESET-001 audit session")
    else:
        reset_files = {path.name for path in RESET_SESSION.iterdir() if path.is_file()}
        for name in sorted(RESET_FILES - reset_files):
            errors.append(f"RB-RESET-001 missing report: {name}")

    round_007 = [
        path.name
        for path in SESSIONS_ROOT.iterdir()
        if path.is_dir() and re.search(r"ROUND[-_.]?007", path.name, re.IGNORECASE)
    ] if SESSIONS_ROOT.is_dir() else []
    if round_007:
        errors.append(f"Round-007 session unexpectedly exists: {', '.join(sorted(round_007))}")

    program_paths = [
        REPO_ROOT / ".agent/programs/current.md",
        REPO_ROOT / ".agent/references/current-program.md",
    ]
    for path in program_paths:
        if not path.exists():
            errors.append(f"missing current program route: {_relative(path)}")
            continue
        content = _read(path)
        for marker in ("state: `no-active`", "active_program: `none`", "Round-007"):
            if marker not in content:
                errors.append(f"{_relative(path)} missing program marker: {marker}")
        if "CANCELLED_BEFORE_START" not in content:
            errors.append(f"{_relative(path)} does not record Round-007 cancellation")

    architecture = REPO_ROOT / "docs/project/architecture/architecture.md"
    if architecture.exists():
        content = _read(architecture)
        for marker in ("readability_state: READABILITY_BASELINE_REFOUNDED", "readability_gate: REQUIRED_BEFORE_NEXT_RED_BLUE_PROTOCOL"):
            if marker not in content:
                errors.append(f"architecture.md missing readability marker: {marker}")
    else:
        errors.append("missing canonical architecture.md")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Red/Blue reset verification failed: {len(errors)} error(s).")
        return 1
    print("Red/Blue reset verification passed: active protocol NONE; Round-007 not started.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
