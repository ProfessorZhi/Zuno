from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM = "zuno-canonical-architecture-runtime-realization-v1"
PHASE_COUNT = 22
PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"

PHASE_FILES = [
    "PHASE01_current-baseline-and-requirement-ledger.md",
    "PHASE02_legacy-runtime-compatibility-and-cutover-map.md",
    "PHASE03_executable-cross-module-contract-bundle.md",
    "PHASE04_postgres-domain-and-transaction-foundation.md",
    "PHASE05_security-control-plane.md",
    "PHASE06_observability-minimum-black-box.md",
    "PHASE07_model-gateway-runtime.md",
    "PHASE08_deterministic-single-controller-runtime.md",
    "PHASE09_product-surface-backend-runtime.md",
    "PHASE10_web-desktop-product-adaptation.md",
    "PHASE11_durable-ingestion-and-source-lineage.md",
    "PHASE12_knowledge-version-and-standard-rag.md",
    "PHASE13_memory-context-governance-runtime.md",
    "PHASE14_capability-skill-control-plane.md",
    "PHASE15_tool-runtime-definition-and-readonly-cutover.md",
    "PHASE16_tool-side-effect-and-reconciliation.md",
    "PHASE17_dynamic-plan-dag-parallel-control.md",
    "PHASE18_agentic-graphrag-inner-loop.md",
    "PHASE19_final-synthesis-publication-reflexion.md",
    "PHASE20_observability-eval-benchmark-release-gate.md",
    "PHASE21_fault-recovery-full-e2e-and-cutover.md",
    "PHASE22_fixed-benchmark-production-readiness-and-closure.md",
]

REQUIRED_SHARED = [
    PROGRAM_ROOT / "README.md",
    PROGRAM_ROOT / "current.md",
    PROGRAM_ROOT / "implementation-roadmap.md",
    PROGRAM_ROOT / "task-execution-contract.md",
    PROGRAM_ROOT / "codex-medium-runbook.md",
    PROGRAM_ROOT / "legacy-to-target-migration-map.md",
    PROGRAM_ROOT / "program-manifest.yaml",
    PROGRAM_ROOT / "closure-checklist.md",
    REPO_ROOT / ".agent" / "references" / "current-program.md",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_manifest() -> dict[str, object]:
    return {
        "program": PROGRAM,
        "state": "active",
        "current_phase": "PHASE01",
        "phase_count": PHASE_COUNT,
        "architecture_baseline_commit": "249f1c95855043627cedd289a5de1fd3719f6cd0",
        "measurement_status": "measurement_blocked",
        "quality_gate_status": "quality_not_proven",
    }


def verify_current_program() -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_SHARED:
        if not path.exists():
            errors.append(f"missing active program file: {path.relative_to(REPO_ROOT).as_posix()}")
    for name in PHASE_FILES:
        if not (PROGRAM_ROOT / name).exists():
            errors.append(f"missing phase file: .agent/programs/{name}")
    if errors:
        return errors

    current = _read(PROGRAM_ROOT / "current.md")
    roadmap = _read(PROGRAM_ROOT / "implementation-roadmap.md")
    closure = _read(PROGRAM_ROOT / "closure-checklist.md")
    manifest = _read(PROGRAM_ROOT / "program-manifest.yaml")
    reference = _read(REPO_ROOT / ".agent" / "references" / "current-program.md")
    runbook = _read(PROGRAM_ROOT / "codex-medium-runbook.md")
    migration = _read(PROGRAM_ROOT / "legacy-to-target-migration-map.md")

    for phrase in [
        "state: active",
        f"active_program: {PROGRAM}",
        "current_phase: PHASE01",
        f"phase_count: {PHASE_COUNT}",
        "measurement blocked",
        "quality not yet proven",
    ]:
        if phrase not in current:
            errors.append(f"current.md missing phrase: {phrase}")

    for phrase in [PROGRAM, "phase_count: 22", "Web and Desktop", "Legacy", "Fixed Benchmark"]:
        if phrase not in roadmap + reference + manifest:
            errors.append(f"program surfaces missing phrase: {phrase}")

    for phrase in ["GPT-5.5 medium", "一次只执行一个 Work Package", "不降低架构能力", "Minimal Read Set"]:
        if phrase not in runbook:
            errors.append(f"Codex medium runbook missing phrase: {phrase}")

    for phrase in ["apps/web/src/product", "apps/desktop/src/product", "GeneralAgent", "EffectReconciliation", "Feature Flag"]:
        if phrase not in migration:
            errors.append(f"migration map missing required surface: {phrase}")

    all_task_ids: list[str] = []
    required_sections = [
        "## Phase 目标",
        "## Minimal Read Set",
        "## Current Anchors",
        "## Allowed Paths",
        "## Forbidden Paths",
        "## Work Packages",
        "## Phase 完成定义",
    ]
    for index, name in enumerate(PHASE_FILES, start=1):
        text = _read(PROGRAM_ROOT / name)
        phase_id = f"PHASE{index:02d}"
        for phrase in [f"phase_id: {phase_id}", *required_sections]:
            if phrase not in text:
                errors.append(f"{name} missing phrase: {phrase}")
        task_ids = re.findall(rf"P{index:02d}-T\d{{2}}", text)
        unique_ids = sorted(set(task_ids))
        if len(unique_ids) < 6:
            errors.append(f"{name} must define at least 6 atomic work packages")
        for task_id in unique_ids:
            if task_id not in manifest:
                errors.append(f"manifest missing task id: {task_id}")
        all_task_ids.extend(unique_ids)

    duplicates = sorted({task for task in all_task_ids if all_task_ids.count(task) > 1})
    if duplicates:
        errors.append(f"duplicate task ids across phases: {duplicates}")
    if len(all_task_ids) < 150:
        errors.append(f"program must expose at least 150 atomic work packages, found {len(all_task_ids)}")

    for index in range(1, PHASE_COUNT + 1):
        if f"PHASE{index:02d}" not in closure:
            errors.append(f"closure checklist missing PHASE{index:02d}")

    combined = "\n".join([current, roadmap, closure, manifest, reference, runbook, migration])
    if re.search(r"[A-Za-z]:\\\\Users\\\\", combined):
        errors.append("active program contains a local absolute path")
    if "Agentic GraphRAG 已稳定优于" in combined and "不得声明" not in combined:
        errors.append("active program improperly promotes Agentic GraphRAG superiority")
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
