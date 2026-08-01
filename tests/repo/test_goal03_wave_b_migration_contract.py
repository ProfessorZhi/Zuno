from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260725_36_wave_b_memory_tool_runtime.py"
CUTOVER_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260727_41_wave_b_runtime_cutover.py"
PHASE16_EFFECT_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260727_42_phase16_tool_effect_receipts.py"
PHASE16_RECONCILIATION_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260727_43_phase16_tool_effect_reconciliations.py"
PHASE16_ASYNC_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260727_44_phase16_tool_async_cancellation.py"
PHASE16_COMPENSATION_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260727_45_phase16_tool_compensation_manual_assessment.py"
GOAL05_SANDBOX_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260728_52_goal05_tool_sandbox_receipts.py"
PHASE20_EVAL_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260729_53_phase20_observability_eval_runtime.py"
PHASE20_EVAL_QUERY_SCOPE_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260729_54_phase20_eval_query_scope.py"
PHASE20_RELEASE_GATE_IDENTITY_MIGRATION = (
    REPO_ROOT / "infra/db/alembic/versions/20260729_55_phase20_release_gate_query_identity.py"
)
PHASE20_RESULT_REVISION_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260729_56_phase20_eval_result_revisions.py"


def test_goal03_wave_b_migration_is_append_only_single_head_successor() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    cutover = CUTOVER_MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260725_36"' in text
    assert 'down_revision = "20260725_35"' in text
    assert text.count("op.create_table(") == text.count("op.drop_table(")
    assert 'revision = "20260727_41"' in cutover
    assert 'down_revision = "20260726_40"' in cutover
    assert cutover.count("op.create_table(") == cutover.count("op.drop_table(")
    phase16_effect = PHASE16_EFFECT_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260727_42"' in phase16_effect
    assert 'down_revision = "20260727_41"' in phase16_effect
    assert phase16_effect.count("op.create_table(") == phase16_effect.count("op.drop_table(")
    phase16_reconciliation = PHASE16_RECONCILIATION_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260727_43"' in phase16_reconciliation
    assert 'down_revision = "20260727_42"' in phase16_reconciliation
    assert phase16_reconciliation.count("op.create_table(") == phase16_reconciliation.count("op.drop_table(")
    phase16_async = PHASE16_ASYNC_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260727_44"' in phase16_async
    assert 'down_revision = "20260727_43"' in phase16_async
    assert phase16_async.count("op.create_table(") == phase16_async.count("op.drop_table(")
    phase16_compensation = PHASE16_COMPENSATION_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260727_45"' in phase16_compensation
    assert 'down_revision = "20260727_44"' in phase16_compensation
    assert phase16_compensation.count("op.create_table(") == phase16_compensation.count("op.drop_table(")
    goal05_sandbox = GOAL05_SANDBOX_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260728_52"' in goal05_sandbox
    assert 'down_revision = "20260728_51"' in goal05_sandbox
    assert goal05_sandbox.count("op.create_table(") == goal05_sandbox.count("op.drop_table(")
    phase20_eval = PHASE20_EVAL_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260729_53"' in phase20_eval
    assert 'down_revision = "20260728_52"' in phase20_eval
    assert phase20_eval.count("op.create_table(") == phase20_eval.count("op.drop_table(")
    phase20_eval_query_scope = PHASE20_EVAL_QUERY_SCOPE_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260729_54"' in phase20_eval_query_scope
    assert 'down_revision = "20260729_53"' in phase20_eval_query_scope
    phase20_gate_identity = PHASE20_RELEASE_GATE_IDENTITY_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260729_55"' in phase20_gate_identity
    assert 'down_revision = "20260729_54"' in phase20_gate_identity
    phase20_result_revision = PHASE20_RESULT_REVISION_MIGRATION.read_text(encoding="utf-8")
    assert 'revision = "20260729_56"' in phase20_result_revision
    assert 'down_revision = "20260729_55"' in phase20_result_revision


def test_goal03_wave_b_migration_contains_memory_and_tool_owner_fact_tables() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "memory_versions",
        "memory_snapshots",
        "memory_manifest_snapshots",
        "context_pack_versions",
        "memory_deletion_requests",
        "memory_deletion_receipts",
        "memory_reconciliation_decisions",
        "ck_memory_versions_status",
        "ck_context_pack_budget_positive",
        "tool_providers",
        "tool_definitions",
        "tool_versions",
        "tool_operations",
        "tool_installations",
        "tool_activations",
        "prepared_tool_actions",
        "tool_attempts",
        "tool_observations",
        "tool_execution_receipts",
        "ck_tool_activations_cas",
        "uq_prepared_actions_idempotency",
    )

    for fragment in required_fragments:
        assert fragment in text


def test_goal03_wave_b_cutover_migration_contains_default_runtime_fact_tables() -> None:
    text = CUTOVER_MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "memory_capture_intents",
        "memory_candidates_v2",
        "memory_governance_decisions_v2",
        "memory_records",
        "memory_commit_receipts",
        "context_selection_decisions",
        "context_compression_traces",
        "memory_use_traces",
        "tool_adapter_bindings",
        "tool_bypass_guard_receipts",
        "uq_memory_capture_intents_idempotency",
        "uq_memory_records_conflict_key",
        "ck_memory_candidates_v2_status",
        "ck_tool_bypass_guard_receipts_hash",
    )

    for fragment in required_fragments:
        assert fragment in text

def test_phase16_effect_receipt_migration_contains_known_effect_fact_table() -> None:
    text = PHASE16_EFFECT_MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "tool_effect_receipts",
        "provider_effect_id",
        "effect_status",
        "effect_certainty",
        "idempotency_scope",
        "idempotency_generation",
        "fencing_resource_id",
        "fencing_lease_id",
        "secret_lease_id",
        "native_result_hash",
        "effect_payload_hash",
        "uq_tool_effect_receipts_provider_effect",
        "uq_tool_effect_receipts_idempotency",
        "ck_tool_effect_receipts_certainty",
    )

    for fragment in required_fragments:
        assert fragment in text

def test_phase16_reconciliation_migration_contains_unknown_effect_fact_table() -> None:
    text = PHASE16_RECONCILIATION_MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "tool_effect_reconciliations",
        "provider_effect_id",
        "next_action",
        "reconciliation_query_hash",
        "manual_assessment_required",
        "age_escalation_after_seconds",
        "idempotency_generation",
        "fencing_lease_id",
        "secret_lease_id",
        "reconciliation_payload_hash",
        "uq_tool_effect_reconciliations_provider_effect",
        "uq_tool_effect_reconciliations_idempotency",
        "ck_tool_effect_reconciliations_next_action",
    )

    for fragment in required_fragments:
        assert fragment in text

def test_phase16_async_migration_contains_async_callback_and_cancel_fact_tables() -> None:
    text = PHASE16_ASYNC_MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "tool_async_jobs",
        "tool_async_callbacks",
        "tool_cancellation_receipts",
        "provider_job_id",
        "callback_binding_ref",
        "callback_order",
        "authenticity_status",
        "external_effect_revoked",
        "NOT_GUARANTEED",
        "uq_tool_async_callbacks_order",
        "ck_tool_async_callbacks_authenticity",
        "ck_tool_cancellation_status",
    )

    for fragment in required_fragments:
        assert fragment in text

def test_phase16_compensation_migration_contains_manual_assessment_and_compensation_fact_tables() -> None:
    text = PHASE16_COMPENSATION_MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "tool_compensation_definitions",
        "tool_compensation_attempts",
        "tool_manual_effect_assessments",
        "source_effect_receipt_id",
        "source_reconciliation_id",
        "new_action_proposal_ref",
        "hidden_rollback",
        "MANUAL_COMPENSATION",
        "BEST_EFFORT_COMPENSATION",
        "AUTOMATIC_COMPENSATION",
        "CONFIRMED_NOT_EXECUTED",
        "UNRESOLVED",
        "uq_tool_comp_def_action_proposal",
        "ck_tool_comp_attempt_no_hidden_rollback",
        "ck_tool_manual_assessment_conclusion",
    )

    for fragment in required_fragments:
        assert fragment in text


def test_goal05_sandbox_migration_contains_append_only_receipt_table() -> None:
    text = GOAL05_SANDBOX_MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "tool_sandbox_sessions",
        "tool_sandbox_receipts",
        "sandbox_profile_id",
        "adapter_tier",
        "session_ref",
        "session_size_bytes",
        "expires_at",
        "profile_hash",
        "limits_hash",
        "session_hash",
        "state_integrity_hash",
        "uq_tool_sandbox_sessions_scope",
        "ck_tool_sandbox_sessions_session_version",
        "ck_tool_sandbox_sessions_size",
        "adapter_tier in ('WASM_PYTHON','OCI_PROCESS')",
        "isolation_verified = true",
        "allowlist_enforced = true",
        "fk_tool_sandbox_receipts_prepared",
        "fk_tool_sandbox_receipts_attempt",
        "fk_tool_sandbox_receipts_session",
    )

    for fragment in required_fragments:
        assert fragment in text


def test_phase20_eval_migration_contains_runtime_gate_and_evidence_tables() -> None:
    text = PHASE20_EVAL_MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "observability_eval_datasets",
        "observability_eval_cases",
        "observability_eval_runs",
        "observability_eval_case_executions",
        "observability_eval_metric_results",
        "observability_graphrag_diagnostics",
        "observability_agent_efficiency_snapshots",
        "observability_failure_buckets",
        "observability_benchmark_comparisons",
        "observability_evidence_records",
        "observability_release_gate_evaluations",
        "dataset_hash",
        "case_hashes",
        "reference_claim_refs",
        "gold_evidence_refs",
        "security_scope_ref",
        "corpus_snapshot_hash",
        "index_snapshot_hash",
        "model_profile_hash",
        "judge_policy_hash",
        "embedding_profile_hash",
        "metric_config_hash",
        "runtime_profile_hash",
        "security_scope_hash",
        "measurement_status in ('MEASURED','BLOCKED','UNAVAILABLE','INVALID')",
        "status in ('PASSED','FAILED','BLOCKED','INCOMPARABLE','ERROR')",
        "settled_cost_available",
        "comparison_hash",
        "evidence_hash",
        "gate_hash",
    )

    for fragment in required_fragments:
        assert fragment in text


def test_phase20_eval_query_scope_migration_contains_authorization_boundary() -> None:
    text = PHASE20_EVAL_QUERY_SCOPE_MIGRATION.read_text(encoding="utf-8")
    for fragment in (
        "tenant_id",
        "workspace_id",
        "ix_observability_eval_runs_scope",
        "observability_eval_runs",
    ):
        assert fragment in text


def test_phase20_release_gate_identity_migration_contains_query_identity_constraint() -> None:
    text = PHASE20_RELEASE_GATE_IDENTITY_MIGRATION.read_text(encoding="utf-8")
    for fragment in (
        "uq_observability_release_gate_evaluations_gate_id",
        "observability_release_gate_evaluations",
        "gate_id",
    ):
        assert fragment in text


def test_phase20_result_revision_migration_contains_append_only_late_revision_table() -> None:
    text = PHASE20_RESULT_REVISION_MIGRATION.read_text(encoding="utf-8")
    for fragment in (
        "observability_eval_result_revisions",
        "previous_result_set_hash",
        "revised_result_set_hash",
        "revision_hash",
        "previous_result_set_hash <> revised_result_set_hash",
        "uq_observability_eval_result_revisions_pair",
    ):
        assert fragment in text
