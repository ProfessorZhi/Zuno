from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_CURRENT_PROGRAM = REPO_ROOT / "tools" / "scripts" / "verify_current_program.py"


def _load_verifier():
    spec = spec_from_file_location("verify_current_program", VERIFY_CURRENT_PROGRAM)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_active_program_is_machine_verifiable() -> None:
    verifier = _load_verifier()
    assert verifier.verify_current_program() == []


def test_active_program_manifest_preserves_current_status_boundary() -> None:
    verifier = _load_verifier()
    manifest = verifier.load_manifest()
    assert manifest["state"] == "active"
    assert manifest["current_phase"] == "PHASE22"
    assert manifest["phase_count"] == 22
    assert manifest["atomic_task_count"] == 163
    assert manifest["measurement_status"] == "measurement_in_progress"
    assert manifest["quality_gate_status"] == "quality_not_proven"


def test_phase_states_reflect_goal05_target_coverage_audit() -> None:
    program_root = REPO_ROOT / ".agent" / "programs"
    expected = {
        "PHASE04_postgres-domain-and-transaction-foundation.md": "status: completed",
        "PHASE05_security-control-plane.md": "status: completed",
        "PHASE06_observability-minimum-black-box.md": "status: completed",
        "PHASE07_model-gateway-runtime.md": "status: completed",
        "PHASE08_deterministic-single-controller-runtime.md": "status: completed",
        "PHASE09_product-surface-backend-runtime.md": "status: completed",
        "PHASE10_web-desktop-product-adaptation.md": "status: completed",
        "PHASE11_durable-ingestion-and-source-lineage.md": "status: completed",
        "PHASE12_knowledge-version-and-standard-rag.md": "status: completed",
        "PHASE13_memory-context-governance-runtime.md": "status: completed",
        "PHASE14_capability-skill-control-plane.md": "status: completed",
        "PHASE15_tool-runtime-definition-and-readonly-cutover.md": "status: completed",
        "PHASE16_tool-side-effect-and-reconciliation.md": "status: completed",
        "PHASE17_dynamic-plan-dag-parallel-control.md": "status: completed",
        "PHASE18_agentic-graphrag-inner-loop.md": "status: completed",
        "PHASE19_final-synthesis-publication-reflexion.md": "status: completed",
        "PHASE20_observability-eval-benchmark-release-gate.md": "status: completed",
        "PHASE21_fault-recovery-full-e2e-and-cutover.md": "status: completed",
        "PHASE22_fixed-benchmark-production-readiness-and-closure.md": "status: in_progress",
    }
    for filename, state in expected.items():
        text = (program_root / filename).read_text(encoding="utf-8")
        assert state in text

    manifest = (program_root / "program-manifest.yaml").read_text(encoding="utf-8")
    assert "minimum_vertical_slice_is_phase_completion: false" in manifest
    assert "id: PHASE09, file: .agent/programs/PHASE09_product-surface-backend-runtime.md, state: completed" in manifest
    assert "id: PHASE10, file: .agent/programs/PHASE10_web-desktop-product-adaptation.md, state: completed" in manifest
    assert "id: PHASE12, file: .agent/programs/PHASE12_knowledge-version-and-standard-rag.md, state: completed" in manifest
    assert "id: PHASE15, file: .agent/programs/PHASE15_tool-runtime-definition-and-readonly-cutover.md, state: completed" in manifest
    assert "id: PHASE16, file: .agent/programs/PHASE16_tool-side-effect-and-reconciliation.md, state: completed" in manifest
    assert "id: PHASE17, file: .agent/programs/PHASE17_dynamic-plan-dag-parallel-control.md, state: completed" in manifest
    assert "id: PHASE18, file: .agent/programs/PHASE18_agentic-graphrag-inner-loop.md, state: completed" in manifest
    assert "id: PHASE19, file: .agent/programs/PHASE19_final-synthesis-publication-reflexion.md, state: completed" in manifest
    assert "id: PHASE20, file: .agent/programs/PHASE20_observability-eval-benchmark-release-gate.md, state: completed" in manifest
    assert "id: PHASE21, file: .agent/programs/PHASE21_fault-recovery-full-e2e-and-cutover.md, state: completed" in manifest
    assert "id: PHASE22, file: .agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md, state: in_progress" in manifest


def test_goal05_audit_reopens_phase15_without_production_ready() -> None:
    readiness = (
        REPO_ROOT / ".agent/programs/work-products/phase11-readiness.yaml"
    ).read_text(encoding="utf-8")
    current = (REPO_ROOT / ".agent/programs/current.md").read_text(encoding="utf-8")
    production = (REPO_ROOT / "docs/status/production-readiness.md").read_text(
        encoding="utf-8"
    )

    assert "current_phase_status: completed" in readiness
    assert "coordinator_approval: approved" in readiness
    assert "target_not_current: 0" in readiness
    assert "current_phase: PHASE22" in current
    assert "PHASE09 completed" in current
    assert "PHASE15 completed" in current
    assert "PHASE10 completed" in current
    assert "PHASE16 completed" in current
    assert "PHASE17 completed" in current
    assert "goal04-phase17-coordinator-closure.md" in current
    assert "PHASE18 completed" in current
    assert "goal04-phase18-coordinator-closure.md" in current
    assert "goal04-phase10-coordinator-closure.md" in current
    assert "PHASE19 completed" in current
    assert "goal04-phase19-coordinator-closure.md" in current
    assert "PHASE20 completed" in current
    assert "PHASE21 completed" in current
    assert "PHASE22 in progress" in current
    assert "goal05-target-coverage-audit.md" in current
    assert "production readiness not established" in production


def test_program_has_all_phase_files_and_atomic_tasks() -> None:
    verifier = _load_verifier()
    assert len(verifier.PHASE_FILES) == 22
    task_count = 0
    for phase_file in verifier.PHASE_FILES:
        text = (verifier.PROGRAM_ROOT / phase_file).read_text(encoding="utf-8")
        import re

        task_count += len(set(re.findall(r"P\d{2}-T\d{2}", text)))
    assert task_count == 163


def test_phase17_dynamic_dag_closure_evidence_is_guarded() -> None:
    evidence = (REPO_ROOT / "docs/evidence/goal04-phase17-startup-audit.md").read_text(
        encoding="utf-8"
    )
    closure = (
        REPO_ROOT / "docs/evidence/goal04-phase17-coordinator-closure.md"
    ).read_text(encoding="utf-8")
    runtime = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/dynamic_dag.py"
    ).read_text(encoding="utf-8")
    dynamic_controller = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/dynamic_controller.py"
    ).read_text(encoding="utf-8")
    admission = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/admission.py"
    ).read_text(encoding="utf-8")
    branch_result = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/branch_result.py"
    ).read_text(encoding="utf-8")
    dispatch = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/dispatch.py"
    ).read_text(encoding="utf-8")
    reducer = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/reducer.py"
    ).read_text(encoding="utf-8")
    control_decision = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/control_decision.py"
    ).read_text(encoding="utf-8")
    replan_barrier = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/replan_barrier.py"
    ).read_text(encoding="utf-8")
    dynamic_send = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/send.py"
    ).read_text(encoding="utf-8")
    dynamic_worker = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/dynamic_worker.py"
    ).read_text(encoding="utf-8")
    parallel_recovery = (
        REPO_ROOT / "src/backend/zuno/agent/runtime/planning/recovery.py"
    ).read_text(encoding="utf-8")
    migration = (
        REPO_ROOT / "infra/db/alembic/versions/20260728_46_phase17_dynamic_dispatch.py"
    ).read_text(encoding="utf-8")
    branch_result_migration = (
        REPO_ROOT / "infra/db/alembic/versions/20260728_47_phase17_branch_results.py"
    ).read_text(encoding="utf-8")
    join_outcome_migration = (
        REPO_ROOT / "infra/db/alembic/versions/20260728_48_phase17_join_outcomes.py"
    ).read_text(encoding="utf-8")
    replan_barrier_migration = (
        REPO_ROOT / "infra/db/alembic/versions/20260728_49_phase17_replan_barriers.py"
    ).read_text(encoding="utf-8")
    repository = (
        REPO_ROOT / "src/backend/zuno/platform/database/agent/domain.py"
    ).read_text(encoding="utf-8")
    domain = (
        REPO_ROOT / "src/backend/zuno/agent/domain/task_contracts.py"
    ).read_text(encoding="utf-8")
    tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_dynamic_dag_validator.py"
    ).read_text(encoding="utf-8")
    dynamic_controller_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_dynamic_runtime_controller.py"
    ).read_text(encoding="utf-8")
    domain_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_dynamic_plan_version_domain.py"
    ).read_text(encoding="utf-8")
    admission_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_readyset_admission.py"
    ).read_text(encoding="utf-8")
    branch_result_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_branch_result_fencing.py"
    ).read_text(encoding="utf-8")
    dispatch_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_dispatch_commit.py"
    ).read_text(encoding="utf-8")
    reducer_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_reducer_join_policy.py"
    ).read_text(encoding="utf-8")
    control_decision_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_control_decision.py"
    ).read_text(encoding="utf-8")
    replan_barrier_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_replan_barrier.py"
    ).read_text(encoding="utf-8")
    dynamic_send_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_dynamic_step_send.py"
    ).read_text(encoding="utf-8")
    dynamic_worker_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_dynamic_step_worker.py"
    ).read_text(encoding="utf-8")
    parallel_recovery_tests = (
        REPO_ROOT / "tests/agent/dag/test_phase17_parallel_recovery.py"
    ).read_text(encoding="utf-8")
    persistence_tests = (
        REPO_ROOT / "tests/integration/agent/test_phase17_dispatch_commit_persistence.py"
    ).read_text(encoding="utf-8")

    assert "P17-T01 Dynamic DAG Proposal and Validator Slice" in evidence
    assert "DynamicPlanProposal" in runtime
    assert "DynamicPlanValidator" in runtime
    assert "DynamicPlanRepairer" in runtime
    assert "test_phase17_dynamic_plan_validator_rejects_unsafe_parallel_writes" in tests
    assert "P17-T02 Dynamic PlanVersion Domain and Supersession Slice" in evidence
    assert "class PlanKind" in domain
    assert "class DynamicStepDefinition" in domain
    assert "def create_dynamic_dag" in domain
    assert "def supersede" in domain
    assert "test_phase17_dynamic_plan_version_supersession_requires_active_cas" in domain_tests
    assert "P17-T03 ReadySet and Admission Domain Slice" in evidence
    assert "class ReadySetBuilder" in admission
    assert "class AdmissionController" in admission
    assert "class AdmissionContext" in admission
    assert "class AdmissionRejectionCode" in admission
    assert "STALE_SECURITY_EPOCH" in admission
    assert "CAPABILITY_NOT_AUTHORIZED" in admission
    assert "test_phase17_readyset_finds_dependency_satisfied_steps" in admission_tests
    assert "test_phase17_admission_defers_budget_quota_capacity_and_resource_conflicts" in admission_tests
    assert "P17-T04 Dispatch Commit-before-Send Domain Slice" in evidence
    assert "class DispatchCommitBuilder" in dispatch
    assert "class DispatchGroup" in dispatch
    assert "class DispatchItem" in dispatch
    assert "class StepRun" in dispatch
    assert "class DispatchOutboxMessage" in dispatch
    assert "commit_required_before_send" in dispatch
    assert "agent.dynamic_step.dispatch.requested" in dispatch
    assert "test_phase17_dispatch_commit_binds_group_items_step_runs_and_outbox_before_send" in dispatch_tests
    assert "test_phase17_dispatch_commit_is_deterministic_for_same_admission" in dispatch_tests
    assert "P17-T05 Dispatch PostgreSQL Persistence Slice" in evidence
    assert "20260728_46" in migration
    assert "agent_dispatch_groups" in migration
    assert "agent_step_runs" in migration
    assert "agent_dispatch_items" in migration
    assert "def record_dispatch_commit" in repository
    assert "InfrastructureRepository" in repository
    assert "test_phase17_dispatch_commit_persists_step_runs_and_outbox_in_one_uow" in persistence_tests
    assert "P17-T06 BranchResultRef and Late-result Fencing Slice" in evidence
    assert "class BranchResultSubmission" in branch_result
    assert "class BranchResultFencer" in branch_result
    assert "class BranchResultRef" in branch_result
    assert "REJECTED_STALE_PLAN" in branch_result
    assert "REJECTED_STALE_EPOCH" in branch_result
    assert "REJECTED_STALE_STEP_HASH" in branch_result
    assert "REJECTED_OBSOLETE_STEP_RUN" in branch_result
    assert "REJECTED_INLINE_PAYLOAD" in branch_result
    assert "test_phase17_branch_result_fencer_rejects_late_result_fencing_mismatch" in branch_result_tests
    assert "P17-T07 BranchResultRef PostgreSQL Persistence Slice" in evidence
    assert "20260728_47" in branch_result_migration
    assert "agent_branch_result_refs" in branch_result_migration
    assert "def record_branch_result_ref" in repository
    assert "duplicate:ACCEPTED" in repository
    assert "test_phase17_branch_result_ref_persistence_records_only_fenced_object_refs" in persistence_tests
    assert "P17-T08 Idempotent Reducer and JoinPolicy Slice" in evidence
    assert "class BranchResultReducer" in reducer
    assert "class ReducedJoinOutcome" in reducer
    assert "class JoinDecision" in reducer
    assert "ALL_REQUIRED" in reducer
    assert "BEST_EFFORT" in reducer
    assert "FAIL_FAST" in reducer
    assert "test_phase17_reducer_is_order_independent_and_idempotent_for_duplicate_refs" in reducer_tests
    assert "test_phase17_reducer_evaluates_join_policy" in reducer_tests
    assert "P17-T09 JoinOutcome PostgreSQL Persistence Slice" in evidence
    assert "20260728_48" in join_outcome_migration
    assert "agent_join_outcomes" in join_outcome_migration
    assert "def record_join_outcome" in repository
    assert "duplicate:{existing['decision']}" in repository
    assert "duplicate:CONTINUE" in persistence_tests
    assert "test_phase17_join_outcome_persistence_records_reducer_decision" in persistence_tests
    assert "P17-T10 Conditional Reflection ControlDecision Slice" in evidence
    assert "class JoinControlDecisionEngine" in control_decision
    assert "class ConditionalReflectionPolicy" in control_decision
    assert "class DynamicControlAction" in control_decision
    assert "REQUEST_REFLECTION" in control_decision
    assert "REQUEST_REPLAN_BARRIER" in control_decision
    assert "retry_permitted" in control_decision
    assert "test_phase17_control_decision_requests_reflection_for_best_effort_partial_join" in control_decision_tests
    assert "test_phase17_control_decision_requests_replan_barrier_for_failed_join" in control_decision_tests
    assert "test_phase17_control_decision_hash_fences_mutation" in control_decision_tests
    assert "P17-T11 Replan Barrier Domain Slice" in evidence
    assert "class ReplanBarrierBuilder" in replan_barrier
    assert "class ReplanBarrierRequest" in replan_barrier
    assert "class StepRunBarrierDecision" in replan_barrier
    assert "freeze_new_dispatch" in replan_barrier
    assert "new_plan_version_required" in replan_barrier
    assert "DRAIN_NON_INTERRUPTIBLE" in replan_barrier
    assert "test_phase17_replan_barrier_freezes_dispatch_and_advances_epoch" in replan_barrier_tests
    assert "test_phase17_replan_barrier_assigns_cancel_drain_and_terminal_actions" in replan_barrier_tests
    assert "test_phase17_replan_barrier_hash_fences_mutation" in replan_barrier_tests
    assert "P17-T12 Replan Barrier PostgreSQL Persistence Slice" in evidence
    assert "20260728_49" in replan_barrier_migration
    assert "agent_replan_barriers" in replan_barrier_migration
    assert "def record_replan_barrier_request" in repository
    assert "duplicate:REQUESTED" in persistence_tests
    assert "test_phase17_replan_barrier_persistence_records_frozen_epoch_boundary" in persistence_tests
    assert "P17-T13 LangGraph Send and Outbox Claim Boundary Slice" in evidence
    assert "class DynamicStepSendBuilder" in dynamic_send
    assert "class DynamicStepSendEnvelope" in dynamic_send
    assert "DYNAMIC_STEP_WORKER_NODE" in dynamic_send
    assert "from langgraph.types import Send" in dynamic_send
    assert "def record_dynamic_step_send_claim" in repository
    assert "duplicate:CLAIMED_FOR_SEND" in repository
    assert "test_phase17_dynamic_step_send_builds_real_langgraph_send_from_claimed_outbox" in dynamic_send_tests
    assert "test_phase17_dynamic_step_send_claim_requires_claimed_committed_outbox" in persistence_tests
    assert "P17-T14 Dynamic Step Worker and BranchResultRef Writeback Slice" in evidence
    assert "class DynamicStepWorker" in dynamic_worker
    assert "class LocalBranchResultObjectStore" in dynamic_worker
    assert "class BranchResultObjectStore" in dynamic_worker
    assert "StepExecutorRegistry" in dynamic_worker
    assert "BranchResultFencer" in dynamic_worker
    assert "test_phase17_dynamic_step_worker_executes_and_returns_fenced_branch_result" in dynamic_worker_tests
    assert "test_phase17_dynamic_step_worker_writes_branch_result_ref_after_send_claim" in persistence_tests
    assert "P17-T15 Restart Parallel Recovery Slice" in evidence
    assert "class ParallelRecoveryPlanner" in parallel_recovery
    assert "class PersistedStepRunSnapshot" in parallel_recovery
    assert "class RecoveryAction" in parallel_recovery
    assert "def load_parallel_recovery_snapshot" in repository
    assert "HONOR_REPLAN_BARRIER" in parallel_recovery
    assert "RESEND_OUTBOX" in parallel_recovery
    assert "RESUME_IN_FLIGHT" in parallel_recovery
    assert "REDUCE_RESULT" in parallel_recovery
    assert "test_phase17_parallel_recovery_honors_replan_barrier_before_resend" in parallel_recovery_tests
    assert "test_phase17_parallel_recovery_snapshot_restores_dispatch_branch_and_barrier_facts" in persistence_tests
    assert "P17-T16 Replan Barrier Execution Slice" in evidence
    assert "class ReplanBarrierExecutor" in replan_barrier
    assert "class ReplanBarrierExecutionResult" in replan_barrier
    assert "def record_replan_barrier_execution" in repository
    assert "duplicate:DRAINING" in persistence_tests
    assert "READY_FOR_REPLAN" in replan_barrier
    assert "test_phase17_replan_barrier_executor_marks_ready_when_no_in_flight_drain_remains" in replan_barrier_tests
    assert "test_phase17_replan_barrier_execution_persists_cancel_and_drain_state" in persistence_tests
    assert "P17-T17 Default Dynamic Runtime Controller Slice" in evidence
    assert "class DynamicPlanRuntimeController" in dynamic_controller
    assert "class DynamicRuntimeDispatchResult" in dynamic_controller
    assert "def dispatch_ready_steps" in dynamic_controller
    assert "record_dispatch_commit" in dynamic_controller
    assert "test_phase17_dynamic_runtime_controller_dispatches_ready_steps_through_commit_before_send" in dynamic_controller_tests
    assert "test_phase17_dynamic_runtime_controller_is_default_dynamic_dispatch_entry" in persistence_tests
    assert "Goal04 PHASE17 Coordinator Closure" in closure
    assert "phase_status: completed" in closure
    assert "coordinator_decision: approved" in closure
    assert "closure_head_sha: b27d45a5" in closure
    assert "20260728_49 (head)" in closure
    assert "59 passed in 29.18s" in closure
    assert "9 passed in 41.32s" in closure
    assert "refined Agent Core target architecture verification passed" in closure


def test_phase18_agentic_graphrag_startup_evidence_is_guarded() -> None:
    startup = (
        REPO_ROOT / "docs/evidence/goal04-phase18-startup-audit.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "Goal04 PHASE18 Startup Audit",
        "phase_status: in_progress",
        "branch: codex/goal04-phase18-agentic-graphrag",
        "base_main_sha: 4d14ae9e8cd953359c82e51d55279cc123ab47ae",
        "phase17_merge_sha: 4d14ae9e8cd953359c82e51d55279cc123ab47ae",
        "20260728_49 (head)",
        "Frozen Gap List",
        "P18-T01 EvidenceRequirement and Profile Selection",
        "P18-T02 Fixed KnowledgeRetrievalGraph and Round Domain",
        "P18-T03 Graph Entity/Relation/Path/Community Runtime",
        "P18-T04 DRIFT and Multi-retriever Dispatch",
        "P18-T05 Fusion, Rerank and Rank Lineage",
        "P18-T06 EvidenceLedger, Frontier and Quality Verdict",
        "P18-T07 Corrective Retrieval Decision",
        "P18-T08 KnowledgeControlProposal and Agent Integration",
        "CorrectiveAgenticRetrievalRuntime",
        "EvidenceLedger",
        "DurableKnowledgeRetrievalPort",
        "GraphRAGQueryService",
        "RetrievalPlanner / RetrievalOrchestrator",
        "KnowledgeControlProposal",
        "PHASE18 已启动并冻结 Gap List",
    ]:
        assert phrase in startup


def test_phase18_agentic_graphrag_closure_evidence_is_guarded() -> None:
    closure = (
        REPO_ROOT / "docs/evidence/goal04-phase18-coordinator-closure.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "Goal04 PHASE18 Coordinator Closure",
        "status: completed",
        "coordinator_approval: approved",
        "head_sha: 42a77f9fccf0b328bb48098eb6b16dcad883abcd",
        "P18-T01",
        "P18-T08",
        "KnowledgeRetrievalGraph",
        "RetrievalPlan",
        "EvidenceFrontier",
        "KnowledgeControlProposal",
        "CorrectiveAgenticGraphRAGRuntime",
        "KnowledgeQueryService.query()",
        "26 passed, 1 warning in 23.28s",
        "PR #49 GitHub validate",
        "retry count: 1",
        "Production readiness not established",
    ]:
        assert phrase in closure
