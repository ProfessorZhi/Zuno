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
        "tool_sandbox_receipts",
        "sandbox_profile_id",
        "adapter_tier",
        "session_ref",
        "profile_hash",
        "limits_hash",
        "session_hash",
        "state_integrity_hash",
        "adapter_tier in ('WASM_PYTHON','OCI_PROCESS')",
        "isolation_verified = true",
        "allowlist_enforced = true",
        "fk_tool_sandbox_receipts_prepared",
        "fk_tool_sandbox_receipts_attempt",
    )

    for fragment in required_fragments:
        assert fragment in text
