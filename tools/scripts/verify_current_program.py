from __future__ import annotations

import re
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM = "zuno-canonical-architecture-runtime-realization-v1"
CURRENT_PHASE = "PHASE10"
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
    sys.modules[spec.name] = module
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
    sys.modules[spec.name] = module
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
        PHASE_FILES[4]: "completed",
        PHASE_FILES[5]: "completed",
        PHASE_FILES[6]: "completed",
        PHASE_FILES[7]: "completed",
        PHASE_FILES[8]: "completed",
        PHASE_FILES[9]: "ready",
        PHASE_FILES[10]: "completed",
        PHASE_FILES[11]: "completed",
        PHASE_FILES[12]: "completed",
        PHASE_FILES[13]: "completed",
        PHASE_FILES[14]: "completed",
        PHASE_FILES[15]: "completed",
        PHASE_FILES[16]: "in_progress",
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
    phase17_evidence = _read(REPO_ROOT / "docs" / "evidence" / "goal04-phase17-startup-audit.md")
    dynamic_dag = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "dynamic_dag.py")
    dynamic_admission = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "admission.py")
    branch_result = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "branch_result.py")
    dynamic_dispatch = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "dispatch.py")
    dynamic_reducer = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "reducer.py")
    control_decision = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "control_decision.py")
    replan_barrier = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "replan_barrier.py")
    dynamic_send = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "send.py")
    dynamic_worker = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime" / "planning" / "dynamic_worker.py")
    dispatch_migration = _read(
        REPO_ROOT / "infra" / "db" / "alembic" / "versions" / "20260728_46_phase17_dynamic_dispatch.py"
    )
    branch_result_migration = _read(
        REPO_ROOT / "infra" / "db" / "alembic" / "versions" / "20260728_47_phase17_branch_results.py"
    )
    join_outcome_migration = _read(
        REPO_ROOT / "infra" / "db" / "alembic" / "versions" / "20260728_48_phase17_join_outcomes.py"
    )
    replan_barrier_migration = _read(
        REPO_ROOT / "infra" / "db" / "alembic" / "versions" / "20260728_49_phase17_replan_barriers.py"
    )
    agent_repository = _read(REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database" / "agent" / "domain.py")
    agent_domain = _read(REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "domain" / "task_contracts.py")
    dynamic_dag_tests = _read(REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_dynamic_dag_validator.py")
    dynamic_plan_version_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_dynamic_plan_version_domain.py"
    )
    readyset_admission_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_readyset_admission.py"
    )
    branch_result_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_branch_result_fencing.py"
    )
    dispatch_commit_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_dispatch_commit.py"
    )
    reducer_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_reducer_join_policy.py"
    )
    control_decision_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_control_decision.py"
    )
    replan_barrier_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_replan_barrier.py"
    )
    dynamic_send_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_dynamic_step_send.py"
    )
    dynamic_worker_tests = _read(
        REPO_ROOT / "tests" / "agent" / "dag" / "test_phase17_dynamic_step_worker.py"
    )
    dispatch_persistence_tests = _read(
        REPO_ROOT / "tests" / "integration" / "agent" / "test_phase17_dispatch_commit_persistence.py"
    )

    errors.extend(
        _require_phrases(
            current,
            [
                "state: active",
                f"active_program: {PROGRAM}",
                "current_phase: PHASE10",
                "program_version: 2",
                "PHASE01–04 订正决定",
                "PHASE05 completed",
                "PHASE06 completed",
                "PHASE07 completed",
                "PHASE08 completed",
                "PHASE11 completed",
                "PHASE09 completed",
                "PHASE12 completed",
                "PHASE13 completed",
                "PHASE14 completed",
                "PHASE15 completed",
                "PHASE10 ready",
                "PHASE16 completed",
                "PHASE17 in_progress",
                "最小 Vertical Slice 只能作为阶段中的中间检查点",
                "implementation available",
                "measurement blocked",
                "production readiness not established",
            ],
            "current.md",
        )
    )
    errors.extend(
        _require_phrases(
            roadmap + manifest + closure + readme + reference,
            [
                PROGRAM,
                "current_phase: PHASE10",
                "program_version: 2",
                "reopen_phase01_through_phase04",
                "implementation available",
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
                "id: PHASE05, file: .agent/programs/PHASE05_security-control-plane.md, state: completed",
                "id: PHASE06, file: .agent/programs/PHASE06_observability-minimum-black-box.md, state: completed",
                "id: PHASE07, file: .agent/programs/PHASE07_model-gateway-runtime.md, state: completed",
                "id: PHASE08, file: .agent/programs/PHASE08_deterministic-single-controller-runtime.md, state: completed",
                "id: PHASE09, file: .agent/programs/PHASE09_product-surface-backend-runtime.md, state: completed",
                "id: PHASE10, file: .agent/programs/PHASE10_web-desktop-product-adaptation.md, state: ready",
                "id: PHASE11, file: .agent/programs/PHASE11_durable-ingestion-and-source-lineage.md, state: completed",
                "id: PHASE12, file: .agent/programs/PHASE12_knowledge-version-and-standard-rag.md, state: completed",
                "id: PHASE13, file: .agent/programs/PHASE13_memory-context-governance-runtime.md, state: completed",
                "id: PHASE14, file: .agent/programs/PHASE14_capability-skill-control-plane.md, state: completed",
                "id: PHASE15, file: .agent/programs/PHASE15_tool-runtime-definition-and-readonly-cutover.md, state: completed",
                "id: PHASE16, file: .agent/programs/PHASE16_tool-side-effect-and-reconciliation.md, state: completed",
                "id: PHASE17, file: .agent/programs/PHASE17_dynamic-plan-dag-parallel-control.md, state: in_progress",
            ],
            "program-manifest.yaml",
        )
    )
    errors.extend(
        _require_phrases(
            (
                phase17_evidence
                + dynamic_dag
                + dynamic_dag_tests
                + agent_domain
                + dynamic_plan_version_tests
                + dynamic_admission
                + readyset_admission_tests
                + branch_result
                + branch_result_tests
                + dynamic_dispatch
                + dispatch_commit_tests
                + dynamic_reducer
                + reducer_tests
                + control_decision
                + control_decision_tests
                + replan_barrier
                + replan_barrier_tests
                + dynamic_send
                + dynamic_send_tests
                + dynamic_worker
                + dynamic_worker_tests
                + dispatch_migration
                + branch_result_migration
                + join_outcome_migration
                + replan_barrier_migration
                + agent_repository
                + dispatch_persistence_tests
            ),
            [
                "P17-T01 Dynamic DAG Proposal and Validator Slice",
                "DynamicPlanProposal",
                "DynamicPlanValidator",
                "DynamicPlanRepairer",
                "DynamicPlanSideEffectClass",
                "DynamicPlanResourceClaim",
                "test_phase17_dynamic_plan_validator_rejects_unsafe_parallel_writes",
                "test_phase17_dynamic_plan_repairer_adds_deterministic_acceptance_and_output_contract",
                "P17-T02 Dynamic PlanVersion Domain and Supersession Slice",
                "PlanKind",
                "DYNAMIC_DAG",
                "DynamicStepDefinition",
                "create_dynamic_dag",
                "supersede",
                "test_phase17_dynamic_plan_version_supersession_requires_active_cas",
                "test_phase17_dynamic_plan_version_rejects_unknown_dependency_and_cycles",
                "P17-T03 ReadySet and Admission Domain Slice",
                "ReadySetBuilder",
                "AdmissionController",
                "AdmissionContext",
                "AdmissionRejectionCode",
                "STALE_SECURITY_EPOCH",
                "CAPABILITY_NOT_AUTHORIZED",
                "test_phase17_readyset_finds_dependency_satisfied_steps",
                "test_phase17_admission_defers_budget_quota_capacity_and_resource_conflicts",
                "P17-T04 Dispatch Commit-before-Send Domain Slice",
                "DispatchCommitBuilder",
                "DispatchGroup",
                "DispatchItem",
                "StepRun",
                "DispatchOutboxMessage",
                "commit_required_before_send",
                "agent.dynamic_step.dispatch.requested",
                "test_phase17_dispatch_commit_binds_group_items_step_runs_and_outbox_before_send",
                "test_phase17_dispatch_commit_is_deterministic_for_same_admission",
                "P17-T05 Dispatch PostgreSQL Persistence Slice",
                "20260728_46_phase17_dynamic_dispatch",
                "agent_dispatch_groups",
                "agent_step_runs",
                "agent_dispatch_items",
                "record_dispatch_commit",
                "InfrastructureRepository",
                "test_phase17_dispatch_commit_persists_step_runs_and_outbox_in_one_uow",
                "P17-T06 BranchResultRef and Late-result Fencing Slice",
                "BranchResultSubmission",
                "BranchResultFencer",
                "BranchResultRef",
                "REJECTED_STALE_PLAN",
                "REJECTED_STALE_EPOCH",
                "REJECTED_STALE_STEP_HASH",
                "REJECTED_OBSOLETE_STEP_RUN",
                "REJECTED_INLINE_PAYLOAD",
                "test_phase17_branch_result_fencer_rejects_late_result_fencing_mismatch",
                "P17-T07 BranchResultRef PostgreSQL Persistence Slice",
                "20260728_47_phase17_branch_results",
                "agent_branch_result_refs",
                "record_branch_result_ref",
                "duplicate:ACCEPTED",
                "test_phase17_branch_result_ref_persistence_records_only_fenced_object_refs",
                "P17-T08 Idempotent Reducer and JoinPolicy Slice",
                "BranchResultReducer",
                "ReducedJoinOutcome",
                "JoinDecision",
                "ALL_REQUIRED",
                "BEST_EFFORT",
                "FAIL_FAST",
                "test_phase17_reducer_is_order_independent_and_idempotent_for_duplicate_refs",
                "test_phase17_reducer_evaluates_join_policy",
                "P17-T09 JoinOutcome PostgreSQL Persistence Slice",
                "20260728_48_phase17_join_outcomes",
                "agent_join_outcomes",
                "record_join_outcome",
                "duplicate:CONTINUE",
                "test_phase17_join_outcome_persistence_records_reducer_decision",
                "P17-T10 Conditional Reflection ControlDecision Slice",
                "JoinControlDecisionEngine",
                "ConditionalReflectionPolicy",
                "DynamicControlAction",
                "REQUEST_REFLECTION",
                "REQUEST_REPLAN_BARRIER",
                "retry_permitted",
                "test_phase17_control_decision_requests_reflection_for_best_effort_partial_join",
                "test_phase17_control_decision_requests_replan_barrier_for_failed_join",
                "test_phase17_control_decision_hash_fences_mutation",
                "P17-T11 Replan Barrier Domain Slice",
                "ReplanBarrierBuilder",
                "ReplanBarrierRequest",
                "StepRunBarrierDecision",
                "freeze_new_dispatch",
                "new_plan_version_required",
                "DRAIN_NON_INTERRUPTIBLE",
                "test_phase17_replan_barrier_freezes_dispatch_and_advances_epoch",
                "test_phase17_replan_barrier_assigns_cancel_drain_and_terminal_actions",
                "test_phase17_replan_barrier_hash_fences_mutation",
                "P17-T12 Replan Barrier PostgreSQL Persistence Slice",
                "20260728_49_phase17_replan_barriers",
                "agent_replan_barriers",
                "record_replan_barrier_request",
                "duplicate:REQUESTED",
                "test_phase17_replan_barrier_persistence_records_frozen_epoch_boundary",
                "P17-T13 LangGraph Send and Outbox Claim Boundary Slice",
                "DynamicStepSendBuilder",
                "DynamicStepSendEnvelope",
                "DYNAMIC_STEP_WORKER_NODE",
                "langgraph.types",
                "record_dynamic_step_send_claim",
                "duplicate:CLAIMED_FOR_SEND",
                "test_phase17_dynamic_step_send_builds_real_langgraph_send_from_claimed_outbox",
                "test_phase17_dynamic_step_send_claim_requires_claimed_committed_outbox",
                "P17-T14 Dynamic Step Worker and BranchResultRef Writeback Slice",
                "DynamicStepWorker",
                "LocalBranchResultObjectStore",
                "BranchResultObjectStore",
                "StepExecutorRegistry",
                "BranchResultFencer",
                "test_phase17_dynamic_step_worker_executes_and_returns_fenced_branch_result",
                "test_phase17_dynamic_step_worker_writes_branch_result_ref_after_send_claim",
            ],
            "PHASE17 dynamic DAG startup evidence",
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
    errors.extend(
        str(issue)
        for issue in _load_verifier(
            REPO_ROOT / "tools" / "scripts" / "verify_utf8_doc_encoding.py",
            "verify_utf8_doc_encoding",
            "verify_utf8_doc_encoding",
        )
    )
    errors.extend(
        _load_verifier(
            REPO_ROOT
            / "tools"
            / "scripts"
            / "verify_phase11_legacy_upload_parser_cutover.py",
            "verify_phase11_legacy_upload_parser_cutover",
            "verify_phase11_legacy_upload_parser_cutover",
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
        post_closure_errors = _load_verifier_function(
            phase04_post_closure_path,
            "verify_phase04_post_closure_consistency",
            "verify_phase04_post_closure_consistency",
        )()
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
    phase07_post_closure_path = (
        REPO_ROOT / "tools" / "scripts" / "verify_phase07_post_closure_consistency.py"
    )
    if not phase07_post_closure_path.exists():
        errors.append("missing PHASE07 post-closure consistency verifier")
    else:
        phase07_post_errors = _load_verifier_function(
            phase07_post_closure_path,
            "verify_phase07_post_closure_consistency",
            "verify_phase07_post_closure_consistency",
        )()
        errors.extend(
            f"PHASE07 post-closure consistency gate failed after closure: {error}"
            for error in phase07_post_errors
        )
    phase11_file = _read(PROGRAM_ROOT / "PHASE11_durable-ingestion-and-source-lineage.md")
    phase11_readiness = _read(WORK_PRODUCTS / "phase11-readiness.yaml")
    for phrase in [
        "status: completed",
        "Goal02 final closure",
        "coordinator_approval: approved",
        "Human Review Resume",
        "Delete / Restore / Reconciliation",
    ]:
        if phrase not in phase11_file:
            errors.append(f"PHASE11 repair phase file missing phrase: {phrase}")
    for phrase in [
        "current_phase_status: completed",
        "coordinator_approval: approved",
        "implementation_available: 80",
        "target_not_current: 0",
        "PHASE08 completed",
        "PHASE11 completed",
        "PHASE09 ready",
        "PHASE12 ready",
    ]:
        if phrase not in phase11_readiness:
            errors.append(f"PHASE11 repair readiness missing phrase: {phrase}")
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
