from __future__ import annotations

import re
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM = "zuno-canonical-architecture-runtime-realization-v1"
CURRENT_PHASE = "PHASE05"
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


def _require_phrases(text: str, phrases: list[str], label: str) -> list[str]:
    return [
        f"{label} missing phrase: {phrase}" for phrase in phrases if phrase not in text
    ]


def _extract_requirement_ids_from_source(path: Path) -> set[str]:
    ids: set[str] = set()
    pattern = re.compile(r"ARCH-[A-Z]+(?:-[A-Z]+)*-\d{3}")
    for line in _read(path).splitlines():
        if not line.lstrip().startswith("|"):
            continue
        match = pattern.search(line)
        if not match:
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if cells and cells[0].startswith(match.group(0)):
            ids.add(match.group(0))
    return ids


def _load_verifier(path: Path, module_name: str, function_name: str) -> list[str]:
    if not path.exists():
        return [f"missing verifier: {path.relative_to(REPO_ROOT).as_posix()}"]
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return [f"cannot load verifier: {path.relative_to(REPO_ROOT).as_posix()}"]
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, function_name)
    return list(function())


def _load_verifier_function(path: Path, module_name: str, function_name: str):
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"cannot load verifier: {path.relative_to(REPO_ROOT).as_posix()}"
        )
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def _verify_requirement_ledger() -> list[str]:
    errors: list[str] = []
    ledger_path = WORK_PRODUCTS / "requirement-ledger.yaml"
    if not ledger_path.exists():
        return [
            "missing PHASE01 work product: .agent/programs/work-products/requirement-ledger.yaml"
        ]
    ledger = _read(ledger_path)
    source_ids: set[str] = set()
    for path in MODULE_REQUIREMENT_SOURCES:
        if not path.exists():
            errors.append(
                f"missing requirement source: {path.relative_to(REPO_ROOT).as_posix()}"
            )
            continue
        source_ids.update(_extract_requirement_ids_from_source(path))
    ledger_ids = set(
        re.findall(
            r"^\s+- requirement_id: (ARCH-[A-Z]+(?:-[A-Z]+)*-\d{3})$",
            ledger,
            re.MULTILINE,
        )
    )
    missing = sorted(source_ids - ledger_ids)
    extra = sorted(ledger_ids - source_ids)
    if missing:
        errors.append(
            f"requirement-ledger.yaml missing requirement ids: {missing[:10]}"
        )
    if extra:
        errors.append(
            f"requirement-ledger.yaml has extra requirement ids: {extra[:10]}"
        )
    count_match = re.search(r"^requirement_count: (\d+)$", ledger, re.MULTILINE)
    if not count_match:
        errors.append("requirement-ledger.yaml missing requirement_count")
    elif int(count_match.group(1)) != len(source_ids):
        errors.append(
            f"requirement-ledger.yaml requirement_count {count_match.group(1)} does not match source count {len(source_ids)}"
        )
    for phrase in [
        "mandatory: true",
        "current_status: target_not_current",
        "target_phase:",
        "test_ids:",
        "evidence_refs:",
    ]:
        if phrase not in ledger:
            errors.append(
                f"requirement-ledger.yaml missing required field phrase: {phrase}"
            )
    return errors


def _verify_correction_states() -> list[str]:
    errors: list[str] = []
    expected_phase_states = {
        PHASE_FILES[0]: "completed",
        PHASE_FILES[1]: "completed",
        PHASE_FILES[2]: "completed",
        PHASE_FILES[3]: "completed",
        PHASE_FILES[4]: "ready",
    }
    for filename, expected in expected_phase_states.items():
        text = _read(PROGRAM_ROOT / filename)
        if f"status: {expected}" not in text:
            errors.append(f"{filename} must be {expected} after PHASE01-04 correction")
    readiness_checks = {
        "phase-readiness.yaml": [
            "current_phase_status: completed",
            "prior_completion_candidate: superseded",
            "may_start_phase02_after_validation: true",
        ],
        "phase02-readiness.yaml": [
            "current_phase_status: completed",
            "prior_completion_candidate: superseded",
            "may_start_phase03_after_validation: true",
        ],
        "phase03-readiness.yaml": [
            "current_phase_status: completed",
            "prior_completion_candidate: superseded",
            "may_start_phase04_after_validation: true",
        ],
        "phase04-readiness.yaml": [
            "current_phase_status: completed",
            "prior_completion_candidate: superseded",
            "may_start_phase05_after_validation: true",
        ],
    }
    for filename, phrases in readiness_checks.items():
        path = WORK_PRODUCTS / filename
        if not path.exists():
            errors.append(
                f"missing corrected readiness file: {path.relative_to(REPO_ROOT).as_posix()}"
            )
            continue
        errors.extend(_require_phrases(_read(path), phrases, filename))
    for evidence_name in [
        "phase03-contract-bundle.md",
        "phase04-postgres-foundation.md",
    ]:
        path = REPO_ROOT / "docs" / "evidence" / evidence_name
        if not path.exists():
            errors.append(f"missing partial evidence: docs/evidence/{evidence_name}")
            continue
        errors.extend(
            _require_phrases(
                _read(path),
                [
                    "partial_implementation_available",
                    "phase_completion: `withdrawn`",
                    "2026-07-16",
                ],
                evidence_name,
            )
        )
    return errors


def load_manifest() -> dict[str, object]:
    return {
        "program": PROGRAM,
        "state": "active",
        "current_phase": CURRENT_PHASE,
        "phase_count": PHASE_COUNT,
        "atomic_task_count": ATOMIC_TASK_COUNT,
        "architecture_baseline_commit": "249f1c95855043627cedd289a5de1fd3719f6cd0",
        "correction_baseline_commit": "49a6aec8392bfa4be8e0662f98b9d1ef6a65960a",
        "measurement_status": "measurement_blocked",
        "quality_gate_status": "quality_not_proven",
    }


def verify_current_program() -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_SHARED:
        if not path.exists():
            errors.append(
                f"missing active program file: {path.relative_to(REPO_ROOT).as_posix()}"
            )
    for name in PHASE_FILES:
        if not (PROGRAM_ROOT / name).exists():
            errors.append(f"missing phase file: .agent/programs/{name}")
    for path in REQUIRED_PHASE01_WORK_PRODUCTS:
        if not path.exists():
            errors.append(
                f"missing PHASE01 work product: {path.relative_to(REPO_ROOT).as_posix()}"
            )
    if errors:
        return errors

    current = _read(PROGRAM_ROOT / "current.md")
    roadmap = _read(PROGRAM_ROOT / "implementation-roadmap.md")
    manifest = _read(PROGRAM_ROOT / "program-manifest.yaml")
    closure = _read(PROGRAM_ROOT / "closure-checklist.md")
    readme = _read(PROGRAM_ROOT / "README.md")
    reference = _read(REPO_ROOT / ".agent" / "references" / "current-program.md")
    task_contract = _read(PROGRAM_ROOT / "task-execution-contract.md")
    runbook = _read(PROGRAM_ROOT / "codex-medium-runbook.md")
    migration = _read(PROGRAM_ROOT / "legacy-to-target-migration-map.md")
    directory_contract = _read(PROGRAM_ROOT / "canonical-directory-contract.md")
    phase22 = _read(PROGRAM_ROOT / PHASE_FILES[-1])

    errors.extend(
        _require_phrases(
            current,
            [
                "state: active",
                f"active_program: {PROGRAM}",
                "current_phase: PHASE05",
                "program_version: 2",
                "PHASE01–04 订正决定",
                "最小 Vertical Slice 只能作为阶段中的中间检查点",
                "partial implementation available",
                "measurement blocked",
                "quality not yet proven",
            ],
            "current.md",
        )
    )
    errors.extend(
        _require_phrases(
            roadmap + manifest + closure + readme + reference,
            [
                PROGRAM,
                "current_phase: PHASE05",
                "program_version: 2",
                "reopen_phase01_through_phase04",
                "partial implementation",
                "RabbitMQ",
                "Object Store",
                "LangGraph PostgreSQL Checkpointer",
                "Fixed Benchmark",
            ],
            "program correction surfaces",
        )
    )
    errors.extend(
        _require_phrases(
            manifest,
            [
                "minimum_vertical_slice_is_phase_completion: false",
                "state: completed, depends_on: [], tasks: [P01-T01",
                "id: PHASE02, file: .agent/programs/PHASE02_legacy-runtime-compatibility-and-cutover-map.md, state: completed",
                "id: PHASE03, file: .agent/programs/PHASE03_executable-cross-module-contract-bundle.md, state: completed",
                "id: PHASE04, file: .agent/programs/PHASE04_postgres-domain-and-transaction-foundation.md, state: completed",
                "id: PHASE05, file: .agent/programs/PHASE05_security-control-plane.md, state: ready",
            ],
            "program-manifest.yaml",
        )
    )

    errors.extend(_verify_correction_states())
    errors.extend(_verify_requirement_ledger())
    errors.extend(
        _load_verifier(
            REPO_ROOT
            / "tools"
            / "scripts"
            / "verify_requirement_ledger_evidence_gate.py",
            "verify_requirement_ledger_evidence_gate",
            "verify_requirement_ledger_evidence_gate",
        )
    )

    task_count = 0
    for phase_file in PHASE_FILES:
        task_count += len(
            set(re.findall(r"P\d{2}-T\d{2}", _read(PROGRAM_ROOT / phase_file)))
        )
    if task_count != ATOMIC_TASK_COUNT:
        errors.append(
            f"phase files contain {task_count} atomic tasks, expected {ATOMIC_TASK_COUNT}"
        )

    for phrase in [
        "GPT-5.5 medium",
        "一次只执行一个 Work Package",
        "不降低架构能力",
        "Minimal Read Set",
    ]:
        if phrase not in runbook:
            errors.append(f"Codex medium runbook missing phrase: {phrase}")
    for phrase in ["只有接口或 Stub", "只有 Mock Test", "Coordinator 合并前必须确认"]:
        if phrase not in task_contract:
            errors.append(f"task execution contract missing phrase: {phrase}")
    for phrase in [
        "apps/web/src/product",
        "apps/desktop/src/product",
        "GeneralAgent",
        "EffectReconciliation",
        "Feature Flag",
    ]:
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
    ]:
        if phrase not in phase22:
            errors.append(f"PHASE22 missing final cleanup phrase: {phrase}")

    errors.extend(
        _load_verifier(
            REPO_ROOT
            / "tools"
            / "scripts"
            / "verify_phase02_compatibility_boundaries.py",
            "verify_phase02_compatibility_boundaries",
            "verify_phase02_compatibility_boundaries",
        )
    )
    errors.extend(
        _load_verifier(
            REPO_ROOT / "tools" / "scripts" / "verify_phase03_contract_bundle.py",
            "verify_phase03_contract_bundle",
            "verify_phase03_contract_bundle",
        )
    )
    errors.extend(
        _load_verifier(
            REPO_ROOT / "tools" / "scripts" / "verify_phase04_postgres_foundation.py",
            "verify_phase04_postgres_foundation",
            "verify_phase04_postgres_foundation",
        )
    )
    phase04_pre_closure_path = (
        REPO_ROOT / "tools" / "scripts" / "verify_phase04_pre_closure_gate.py"
    )
    phase04_post_closure_path = (
        REPO_ROOT / "tools" / "scripts" / "verify_phase04_post_closure_consistency.py"
    )
    phase04_blocker = (
        REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
    )
    if not phase04_pre_closure_path.exists():
        errors.append("missing PHASE04 pre-closure verifier")
    elif not phase04_post_closure_path.exists():
        errors.append("missing PHASE04 post-closure consistency verifier")
    elif not phase04_blocker.exists():
        errors.append("missing PHASE04 aggregate evidence")
    else:
        pre_closure_errors = _load_verifier_function(
            phase04_pre_closure_path,
            "verify_phase04_pre_closure_gate",
            "verify_phase04_pre_closure_gate",
        )()
        post_closure_errors = _load_verifier_function(
            phase04_post_closure_path,
            "verify_phase04_post_closure_consistency",
            "verify_phase04_post_closure_consistency",
        )()
        errors.extend(
            f"PHASE04 pre-closure gate failed after closure: {error}"
            for error in pre_closure_errors
        )
        errors.extend(
            f"PHASE04 post-closure consistency gate failed after closure: {error}"
            for error in post_closure_errors
        )
        blocker_text = _read(phase04_blocker)
        for phrase in [
            "status: completed",
            "coordinator_decision: approved",
            "Docker engine `29.4.0`",
            "real_services_smoke: passed",
            "generic_replay_framework: proven",
        ]:
            if phrase not in blocker_text:
                errors.append(f"PHASE04 blocker evidence missing phrase: {phrase}")
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
