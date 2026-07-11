from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM = "zuno-real-unified-runtime-cutover-v1"
ARCHIVE = REPO_ROOT / "docs/history/programs/zuno-real-unified-runtime-cutover-v1"

CURRENT_PATH = REPO_ROOT / ".agent/programs/current.md"
ROADMAP_PATH = REPO_ROOT / ".agent/programs/implementation-roadmap.md"
CLOSURE_PATH = REPO_ROOT / ".agent/programs/closure-checklist.md"
REFERENCE_PATH = REPO_ROOT / ".agent/references/current-program.md"
QUEUED_SOURCE = REPO_ROOT / ".agent/programs/queued-programs/PROGRAM01_real-unified-runtime-cutover.md"

ARCHIVED_PHASE_FILES = [
    "PHASE01_real-runtime-baseline.md",
    "PHASE02_langgraph-execution-cutover.md",
    "PHASE03_runtime-dependency-factory.md",
    "PHASE04_real-agent-execution.md",
    "PHASE05_knowledge-tool-memory-integration.md",
    "PHASE06_product-cutover.md",
    "PHASE07_benchmark-and-closure.md",
]


def load_manifest() -> dict:
    return {
        "program": PROGRAM,
        "state": "no-active",
        "implementation_status": "implementation_complete",
        "measurement_status": "measurement_blocked",
        "quality_gate_status": "quality_not_proven",
        "blocked_reason": "enterprise_rag_sample8_timeout_and_agentic_profile_incomplete",
        "archive": "docs/history/programs/zuno-real-unified-runtime-cutover-v1/",
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_current_program() -> list[str]:
    errors: list[str] = []
    for path in [CURRENT_PATH, ROADMAP_PATH, CLOSURE_PATH, REFERENCE_PATH, QUEUED_SOURCE, ARCHIVE]:
        if not path.exists():
            errors.append(f"missing current program path: {path.relative_to(REPO_ROOT).as_posix()}")
    for phase_name in ARCHIVED_PHASE_FILES:
        if (REPO_ROOT / ".agent/programs" / phase_name).exists():
            errors.append(f"completed phase file must be archived away from .agent/programs: {phase_name}")
        if not (ARCHIVE / phase_name).exists():
            errors.append(f"missing archived phase file: {phase_name}")
    if errors:
        return errors

    current = _read(CURRENT_PATH)
    reference = _read(REFERENCE_PATH)
    roadmap = _read(ROADMAP_PATH)
    closure = _read(CLOSURE_PATH)
    queued = _read(QUEUED_SOURCE)
    archive_text = "\n".join(
        _read(ARCHIVE / name)
        for name in ["README.md", "closure-summary.md", *ARCHIVED_PHASE_FILES]
        if (ARCHIVE / name).exists()
    )

    for phrase in [
        "state: no-active",
        "active_program: none",
        "current_phase: none",
        f"latest_completed_program: {PROGRAM}",
        "implementation_status: implementation_complete",
        "measurement_status: measurement_blocked",
        "quality_gate_status: quality_not_proven",
        "enterprise_rag_sample8_timeout_and_agentic_profile_incomplete",
    ]:
        if phrase not in current:
            errors.append(f"current.md missing no-active closure phrase: {phrase}")
    for phrase in [
        "state: no-active",
        f"latest_completed_program: {PROGRAM}",
        "blocked benchmark",
    ]:
        if phrase not in reference:
            errors.append(f"current-program reference missing phrase: {phrase}")
    for phrase in [
        "state: activated_from_queue",
        f"active_program: {PROGRAM}",
        "不再作为执行状态事实源",
    ]:
        if phrase not in queued:
            errors.append(f"queued source missing activation phrase: {phrase}")
    if "created_from:" in queued or "C:\\Users\\" in queued:
        errors.append("activated queued source must not contain local absolute created_from path")
    for phrase in [
        f"docs/history/programs/{PROGRAM}/",
        "implementation_complete_measurement_blocked",
        "fixed EnterpriseRAG paired benchmark measured pass",
    ]:
        if phrase not in roadmap + closure + archive_text:
            errors.append(f"program closure surfaces missing phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify_current_program()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Current program verification failed.")
        return 1
    print("Current program verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
