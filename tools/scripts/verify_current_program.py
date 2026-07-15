from __future__ import annotations

import re
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM = "zuno-canonical-architecture-runtime-realization-v1"
CURRENT_PHASE = "PHASE03"
PHASE_COUNT = 22
ATOMIC_TASK_COUNT = 163
PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"
WORK_PRODUCTS = PROGRAM_ROOT / "work-products"

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
    PROGRAM_ROOT / "canonical-directory-contract.md",
    PROGRAM_ROOT / "program-manifest.yaml",
    PROGRAM_ROOT / "closure-checklist.md",
    REPO_ROOT / ".agent" / "references" / "current-program.md",
]

REQUIRED_PHASE01_WORK_PRODUCTS = [
    WORK_PRODUCTS / "current-runtime-inventory.md",
    WORK_PRODUCTS / "current-persistence-inventory.md",
    WORK_PRODUCTS / "requirement-ledger.yaml",
    WORK_PRODUCTS / "frontend-current-inventory.md",
    WORK_PRODUCTS / "legacy-bypass-inventory.yaml",
    WORK_PRODUCTS / "program-risk-register.md",
    WORK_PRODUCTS / "phase-readiness.yaml",
]

PHASE02_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase02_compatibility_boundaries.py"

MODULE_REQUIREMENT_SOURCES = [
    REPO_ROOT / "docs" / "modules" / "01-product-surface.md",
    REPO_ROOT / "docs" / "modules" / "02-input-document-ingestion.md",
    REPO_ROOT / "docs" / "modules" / "03-knowledge-agentic-graphrag.md",
    REPO_ROOT / "docs" / "modules" / "04-model-gateway.md",
    REPO_ROOT / "docs" / "modules" / "05-memory-context.md",
    REPO_ROOT / "docs" / "modules" / "06-agent-core-planning-control.md",
    REPO_ROOT / "docs" / "modules" / "07-capability-skill.md",
    REPO_ROOT / "docs" / "modules" / "08-tool-runtime.md",
    REPO_ROOT / "docs" / "modules" / "09-security.md",
    REPO_ROOT / "docs" / "modules" / "10-observability-eval.md",
    REPO_ROOT / "docs" / "modules" / "11-infrastructure.md",
    REPO_ROOT / "docs" / "governance" / "wave1-cross-module-contract-registry.md",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_requirement_ids_from_source(path: Path) -> set[str]:
    """Extract only table-row requirement IDs, not narrative placeholders."""
    ids: set[str] = set()
    pattern = re.compile(r"ARCH-[A-Z]+(?:-[A-Z]+)?-\d{3}")
    for line in _read(path).splitlines():
        if not line.lstrip().startswith("|"):
            continue
        match = pattern.search(line)
        if not match:
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == match.group(0):
            ids.add(match.group(0))
    return ids


def _extract_list_item_blocks(text: str, marker: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith(marker):
            if current:
                blocks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _verify_phase01_work_products() -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_PHASE01_WORK_PRODUCTS:
        if not path.exists():
            errors.append(f"missing PHASE01 work product: {path.relative_to(REPO_ROOT).as_posix()}")
    if errors:
        return errors

    runtime = _read(WORK_PRODUCTS / "current-runtime-inventory.md")
    persistence = _read(WORK_PRODUCTS / "current-persistence-inventory.md")
    frontend = _read(WORK_PRODUCTS / "frontend-current-inventory.md")
    legacy = _read(WORK_PRODUCTS / "legacy-bypass-inventory.yaml")
    risks = _read(WORK_PRODUCTS / "program-risk-register.md")
    readiness = _read(WORK_PRODUCTS / "phase-readiness.yaml")
    ledger = _read(WORK_PRODUCTS / "requirement-ledger.yaml")

    required_runtime_phrases = [
        "CompletionService",
        "WorkspaceTaskRuntimeService",
        "UnifiedAgentRuntimeService",
        "GeneralAgent",
        "ModelGateway",
        "ToolControlPlaneRuntime",
        "AgenticRetrievalRuntime",
        "SQLiteAgentRunStore",
        "legacy_aliases.py",
    ]
    for phrase in required_runtime_phrases:
        if phrase not in runtime:
            errors.append(f"current-runtime-inventory.md missing runtime anchor: {phrase}")

    for phrase in [
        "SQLiteDurableIngestionStore",
        "LocalObjectStore",
        "LocalQueueBackend",
        "SQLiteAgentRunStore",
        "PostgreSQL",
        "RabbitMQ",
        "MinIO/S3",
        "not proven Current",
    ]:
        if phrase not in persistence:
            errors.append(f"current-persistence-inventory.md missing infrastructure anchor: {phrase}")

    for phrase in [
        "apps/web/src/apis/workspace.ts",
        "fetch-event-source",
        "pendingToolApproval",
        "apps/desktop/bridge.cjs",
        "No Playwright/Cypress/Selenium/browser Electron E2E",
    ]:
        if phrase not in frontend:
            errors.append(f"frontend-current-inventory.md missing frontend anchor: {phrase}")

    legacy_blocks = _extract_list_item_blocks(legacy, "  - path: ")
    if len(legacy_blocks) < 20:
        errors.append("legacy-bypass-inventory.yaml must register at least 20 bypass/legacy entries")
    for block in legacy_blocks:
        for field in [
            "symbol:",
            "owner:",
            "risk:",
            "target_gateway:",
            "temporary_allowlist:",
            "migration_task:",
            "removal_task:",
        ]:
            if field not in block:
                errors.append(f"legacy-bypass-inventory.yaml entry missing {field}: {block.splitlines()[0]}")
        if "P22-T03" not in block:
            errors.append(f"legacy-bypass-inventory.yaml entry missing P22-T03 removal: {block.splitlines()[0]}")

    source_ids: set[str] = set()
    for path in MODULE_REQUIREMENT_SOURCES:
        source_ids.update(_extract_requirement_ids_from_source(path))
    ledger_ids = set(re.findall(r"^\s+- requirement_id: (ARCH-[A-Z]+(?:-[A-Z]+)?-\d{3})$", ledger, re.MULTILINE))
    if source_ids != ledger_ids:
        missing = sorted(source_ids - ledger_ids)
        extra = sorted(ledger_ids - source_ids)
        if missing:
            errors.append(f"requirement-ledger.yaml missing requirement ids: {missing[:10]}")
        if extra:
            errors.append(f"requirement-ledger.yaml has extra requirement ids: {extra[:10]}")
    count_match = re.search(r"^requirement_count: (\d+)$", ledger, re.MULTILINE)
    if not count_match:
        errors.append("requirement-ledger.yaml missing requirement_count")
    elif int(count_match.group(1)) != len(source_ids):
        errors.append(
            f"requirement-ledger.yaml requirement_count {count_match.group(1)} does not match source count {len(source_ids)}"
        )
    if "ARCH-MEM-NNN" in ledger:
        errors.append("requirement-ledger.yaml must not include narrative placeholder ARCH-MEM-NNN")
    for phrase in [
        "mandatory: true",
        "current_status: target_not_current",
        "target_phase:",
        "test_ids:",
        "evidence_refs:",
    ]:
        if phrase not in ledger:
            errors.append(f"requirement-ledger.yaml missing required field phrase: {phrase}")

    for phrase in ["P01-R001", "P01-R008", "severity | owner", "needs-evidence", "assigned"]:
        if phrase not in risks:
            errors.append(f"program-risk-register.md missing risk phrase: {phrase}")
    if "unassigned: []" not in readiness:
        errors.append("phase-readiness.yaml must explicitly show no unassigned P0 risks")
    for task_id in [f"P01-T{index:02d}" for index in range(1, 7)]:
        if task_id not in readiness:
            errors.append(f"phase-readiness.yaml missing work package: {task_id}")
    for phrase in ["current_phase_status: completion_candidate", "PHASE02", "ready_after_phase01_closure"]:
        if phrase not in readiness:
            errors.append(f"phase-readiness.yaml missing readiness phrase: {phrase}")

    return errors


def _verify_phase02_work_products() -> list[str]:
    if not PHASE02_VERIFIER.exists():
        return ["missing PHASE02 verifier: tools/scripts/verify_phase02_compatibility_boundaries.py"]
    spec = spec_from_file_location("verify_phase02_compatibility_boundaries", PHASE02_VERIFIER)
    if spec is None or spec.loader is None:
        return ["cannot load PHASE02 compatibility boundary verifier"]
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.verify_phase02_compatibility_boundaries())


def load_manifest() -> dict[str, object]:
    return {
        "program": PROGRAM,
        "state": "active",
        "current_phase": CURRENT_PHASE,
        "phase_count": PHASE_COUNT,
        "atomic_task_count": ATOMIC_TASK_COUNT,
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

    errors.extend(_verify_phase01_work_products())
    errors.extend(_verify_phase02_work_products())

    current = _read(PROGRAM_ROOT / "current.md")
    roadmap = _read(PROGRAM_ROOT / "implementation-roadmap.md")
    closure = _read(PROGRAM_ROOT / "closure-checklist.md")
    manifest = _read(PROGRAM_ROOT / "program-manifest.yaml")
    reference = _read(REPO_ROOT / ".agent" / "references" / "current-program.md")
    runbook = _read(PROGRAM_ROOT / "codex-medium-runbook.md")
    migration = _read(PROGRAM_ROOT / "legacy-to-target-migration-map.md")
    directory_contract = _read(PROGRAM_ROOT / "canonical-directory-contract.md")
    phase22 = _read(PROGRAM_ROOT / PHASE_FILES[-1])

    for phrase in [
        "state: active",
        f"active_program: {PROGRAM}",
        f"current_phase: {CURRENT_PHASE}",
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

    for phrase in [
        "生产源码零 legacy 目录",
        "零 legacy alias registry",
        "src/backend/zuno/platform/compatibility/legacy_aliases.py",
        "apps/web/src/product",
        "apps/desktop/src/product",
        "api/product/v1",
    ]:
        if phrase not in directory_contract:
            errors.append(f"canonical directory contract missing phrase: {phrase}")

    for phrase in [
        "Legacy-free Canonical Directory Cleanup",
        "生产源码树零 Legacy 文件夹",
        "legacy_aliases.py",
        "tests/legacy_guards",
        "永久双路径",
    ]:
        if phrase not in phase22:
            errors.append(f"PHASE22 missing mandatory cleanup phrase: {phrase}")

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
    if len(all_task_ids) != ATOMIC_TASK_COUNT:
        errors.append(
            f"program must expose exactly {ATOMIC_TASK_COUNT} atomic work packages, found {len(all_task_ids)}"
        )

    for index in range(1, PHASE_COUNT + 1):
        if f"PHASE{index:02d}" not in closure:
            errors.append(f"closure checklist missing PHASE{index:02d}")

    combined = "\n".join(
        [current, roadmap, closure, manifest, reference, runbook, migration, directory_contract]
    )
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
