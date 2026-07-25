"""wave b memory and tool runtime persistence

Revision ID: 20260725_36
Revises: 20260725_35
Create Date: 2026-07-25 00:36:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260725_36"
down_revision = "20260725_35"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "memory_versions",
        sa.Column("memory_version_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("memory_scope_ref", sa.String(length=240), nullable=False),
        sa.Column("memory_kind", sa.String(length=40), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("content_ref", sa.String(length=240), nullable=False),
        sa.Column("source_refs", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("current_snapshot_ref", sa.String(length=180), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "memory_scope_ref", "version_no", name="uq_memory_versions_scope_version"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "memory_scope_ref", "content_hash", name="uq_memory_versions_scope_hash"),
        _hash_check("content_hash", "ck_memory_versions_content_hash"),
        sa.CheckConstraint("version_no > 0", name="ck_memory_versions_version_no"),
        sa.CheckConstraint("confidence >= 0 and confidence <= 1", name="ck_memory_versions_confidence"),
        sa.CheckConstraint("status in ('CANDIDATE','REVIEWING','APPROVED','REJECTED','ACTIVE','SUPERSEDED','REVOKED','DELETED')", name="ck_memory_versions_status"),
    )
    op.create_table(
        "memory_snapshots",
        sa.Column("snapshot_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("memory_version_id", sa.String(length=180), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("serving_watermark_ref", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["memory_version_id"], ["memory_versions.memory_version_id"], name="fk_memory_snapshots_version"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "snapshot_hash", name="uq_memory_snapshots_scope_hash"),
        _hash_check("snapshot_hash", "ck_memory_snapshots_hash"),
    )
    op.create_table(
        "memory_manifest_snapshots",
        sa.Column("manifest_snapshot_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("manifest_hash", sa.String(length=64), nullable=False),
        sa.Column("snapshot_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "generation", name="uq_memory_manifest_scope_generation"),
        _hash_check("manifest_hash", "ck_memory_manifest_hash"),
        sa.CheckConstraint("generation > 0", name="ck_memory_manifest_generation_positive"),
    )
    op.create_table(
        "context_pack_versions",
        sa.Column("context_pack_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=180), nullable=False),
        sa.Column("step_run_id", sa.String(length=180), nullable=False),
        sa.Column("memory_version_id", sa.String(length=180), nullable=False),
        sa.Column("budget_tokens", sa.Integer(), nullable=False),
        sa.Column("selection_hash", sa.String(length=64), nullable=False),
        sa.Column("compression_hash", sa.String(length=64), nullable=False),
        sa.Column("trace_hash", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=40), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["memory_version_id"], ["memory_versions.memory_version_id"], name="fk_context_pack_memory_version"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "run_id", "step_run_id", "generation", name="uq_context_pack_scope_generation"),
        _hash_check("selection_hash", "ck_context_pack_selection_hash"),
        _hash_check("compression_hash", "ck_context_pack_compression_hash"),
        _hash_check("trace_hash", "ck_context_pack_trace_hash"),
        sa.CheckConstraint("budget_tokens > 0", name="ck_context_pack_budget_positive"),
        sa.CheckConstraint("state in ('PREPARED','ACTIVE','OBSOLETE','REHYDRATED')", name="ck_context_pack_state"),
    )
    op.create_table(
        "memory_deletion_requests",
        sa.Column("deletion_request_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("memory_scope_ref", sa.String(length=240), nullable=False),
        sa.Column("requested_by", sa.String(length=180), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("state", sa.String(length=40), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "memory_scope_ref", "reason", name="uq_memory_delete_scope_reason"),
        sa.CheckConstraint("state in ('REQUESTED','APPROVED','REJECTED','EXECUTED','VERIFIED')", name="ck_memory_delete_state"),
    )
    op.create_table(
        "memory_deletion_receipts",
        sa.Column("deletion_receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("deletion_request_id", sa.String(length=180), nullable=False),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("deleted_hash", sa.String(length=64), nullable=False),
        sa.Column("verification_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["deletion_request_id"], ["memory_deletion_requests.deletion_request_id"], name="fk_memory_delete_receipt_request"),
        _hash_check("deleted_hash", "ck_memory_delete_deleted_hash"),
        _hash_check("verification_hash", "ck_memory_delete_verification_hash"),
    )
    op.create_table(
        "memory_reconciliation_decisions",
        sa.Column("reconciliation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("memory_version_id", sa.String(length=180), nullable=False),
        sa.Column("decision", sa.String(length=40), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["memory_version_id"], ["memory_versions.memory_version_id"], name="fk_memory_reconciliation_version"),
        _hash_check("decision_hash", "ck_memory_reconciliation_hash"),
        sa.CheckConstraint("decision in ('APPROVE','REJECT','SUSPEND','ACTIVE','REVOKE')", name="ck_memory_reconciliation_decision"),
    )
    op.create_table(
        "tool_providers",
        sa.Column("provider_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("owner_module", sa.String(length=120), nullable=False),
        sa.Column("provider_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("schema_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "provider_name", name="uq_tool_providers_scope_name"),
        _hash_check("schema_hash", "ck_tool_providers_schema_hash"),
    )
    op.create_table(
        "tool_definitions",
        sa.Column("tool_definition_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("provider_id", sa.String(length=180), nullable=False),
        sa.Column("tool_id", sa.String(length=180), nullable=False),
        sa.Column("semantic_identity", sa.String(length=240), nullable=False),
        sa.Column("owner_module", sa.String(length=120), nullable=False),
        sa.Column("effect_class", sa.String(length=40), nullable=False),
        sa.Column("input_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("output_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["tool_providers.provider_id"], name="fk_tool_definitions_provider"),
        sa.UniqueConstraint("tenant_id", "tool_id", "generation", name="uq_tool_definitions_tool_generation"),
        _hash_check("input_schema_hash", "ck_tool_definitions_input_schema_hash"),
        _hash_check("output_schema_hash", "ck_tool_definitions_output_schema_hash"),
        sa.CheckConstraint("status in ('DRAFT','ACTIVE','DEPRECATED','REVOKED')", name="ck_tool_definitions_status"),
    )
    op.create_table(
        "tool_versions",
        sa.Column("tool_version_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("tool_definition_id", sa.String(length=180), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("input_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("output_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("adapter_kind", sa.String(length=40), nullable=False),
        sa.Column("effect_level", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tool_definition_id"], ["tool_definitions.tool_definition_id"], name="fk_tool_versions_definition"),
        sa.UniqueConstraint("tenant_id", "tool_definition_id", "version_no", name="uq_tool_versions_definition_version"),
        _hash_check("input_schema_hash", "ck_tool_versions_input_schema_hash"),
        _hash_check("output_schema_hash", "ck_tool_versions_output_schema_hash"),
        sa.CheckConstraint("status in ('DRAFT','ACTIVE','DEPRECATED','REVOKED')", name="ck_tool_versions_status"),
    )
    op.create_table(
        "tool_operations",
        sa.Column("tool_operation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("tool_version_id", sa.String(length=180), nullable=False),
        sa.Column("operation_name", sa.String(length=120), nullable=False),
        sa.Column("input_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("output_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("effect_level", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tool_version_id"], ["tool_versions.tool_version_id"], name="fk_tool_operations_version"),
        sa.UniqueConstraint("tenant_id", "tool_version_id", "operation_name", name="uq_tool_operations_version_name"),
        _hash_check("input_schema_hash", "ck_tool_operations_input_schema_hash"),
        _hash_check("output_schema_hash", "ck_tool_operations_output_schema_hash"),
    )
    op.create_table(
        "tool_installations",
        sa.Column("tool_installation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("tool_version_id", sa.String(length=180), nullable=False),
        sa.Column("policy_ref", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tool_version_id"], ["tool_versions.tool_version_id"], name="fk_tool_installations_version"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "tool_version_id", name="uq_tool_installations_scope_version"),
        sa.CheckConstraint("status in ('INSTALLED','ACTIVE','PAUSED','REVOKED')", name="ck_tool_installations_status"),
    )
    op.create_table(
        "tool_activations",
        sa.Column("tool_activation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("tool_installation_id", sa.String(length=180), nullable=False),
        sa.Column("expected_generation", sa.Integer(), nullable=False),
        sa.Column("committed_generation", sa.Integer(), nullable=False),
        sa.Column("activation_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tool_installation_id"], ["tool_installations.tool_installation_id"], name="fk_tool_activations_installation"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "committed_generation", name="uq_tool_activations_committed_generation"),
        _hash_check("activation_hash", "ck_tool_activations_hash"),
        sa.CheckConstraint("committed_generation = expected_generation + 1", name="ck_tool_activations_cas"),
    )
    op.create_table(
        "prepared_tool_actions",
        sa.Column("prepared_tool_action_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("tool_operation_id", sa.String(length=180), nullable=False),
        sa.Column("canonical_args_hash", sa.String(length=64), nullable=False),
        sa.Column("target_resources_hash", sa.String(length=64), nullable=False),
        sa.Column("prepared_action_hash", sa.String(length=64), nullable=False),
        sa.Column("effect_level", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("approval_required", sa.Boolean(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=180), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tool_operation_id"], ["tool_operations.tool_operation_id"], name="fk_prepared_actions_operation"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "idempotency_key", name="uq_prepared_actions_idempotency"),
        _hash_check("canonical_args_hash", "ck_prepared_actions_args_hash"),
        _hash_check("target_resources_hash", "ck_prepared_actions_resources_hash"),
        _hash_check("prepared_action_hash", "ck_prepared_actions_hash"),
        sa.CheckConstraint("status in ('PREPARED','APPROVAL_WAITING','READY','DISPATCHED','OBSOLETE','CANCEL_REQUESTED','CANCELLED')", name="ck_prepared_actions_status"),
    )
    op.create_table(
        "tool_attempts",
        sa.Column("attempt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("dispatch_certainty", sa.String(length=40), nullable=False),
        sa.Column("adapter_family", sa.String(length=40), nullable=False),
        sa.Column("hidden_retry_count", sa.Integer(), nullable=False),
        sa.Column("state_history", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["prepared_tool_action_id"], ["prepared_tool_actions.prepared_tool_action_id"], name="fk_tool_attempts_prepared_action"),
        sa.UniqueConstraint("tenant_id", "prepared_tool_action_id", "hidden_retry_count", name="uq_tool_attempts_retry"),
        sa.CheckConstraint("hidden_retry_count >= 0", name="ck_tool_attempts_retry_nonnegative"),
    )
    op.create_table(
        "tool_observations",
        sa.Column("observation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("owner_module", sa.String(length=120), nullable=False),
        sa.Column("normalized_projection_owner", sa.String(length=120), nullable=False),
        sa.Column("output_trusted", sa.Boolean(), nullable=False),
        sa.Column("schema_valid", sa.Boolean(), nullable=False),
        sa.Column("memory_write_allowed", sa.Boolean(), nullable=False),
        sa.Column("evidence_write_allowed", sa.Boolean(), nullable=False),
        sa.Column("redacted_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_observations_attempt"),
        _hash_check("redacted_payload_hash", "ck_tool_observations_hash"),
    )
    op.create_table(
        "tool_execution_receipts",
        sa.Column("receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("dispatch_certainty", sa.String(length=40), nullable=False),
        sa.Column("effect_certainty", sa.String(length=40), nullable=False),
        sa.Column("append_only_generation", sa.Integer(), nullable=False),
        sa.Column("receipt_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["prepared_tool_action_id"], ["prepared_tool_actions.prepared_tool_action_id"], name="fk_tool_receipts_prepared_action"),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_receipts_attempt"),
        sa.UniqueConstraint("tenant_id", "prepared_tool_action_id", "append_only_generation", name="uq_tool_receipts_generation"),
        _hash_check("receipt_hash", "ck_tool_receipts_hash"),
    )


def downgrade() -> None:
    op.drop_table("tool_execution_receipts")
    op.drop_table("tool_observations")
    op.drop_table("tool_attempts")
    op.drop_table("prepared_tool_actions")
    op.drop_table("tool_activations")
    op.drop_table("tool_installations")
    op.drop_table("tool_operations")
    op.drop_table("tool_versions")
    op.drop_table("tool_definitions")
    op.drop_table("tool_providers")
    op.drop_table("memory_reconciliation_decisions")
    op.drop_table("memory_deletion_receipts")
    op.drop_table("memory_deletion_requests")
    op.drop_table("context_pack_versions")
    op.drop_table("memory_manifest_snapshots")
    op.drop_table("memory_snapshots")
    op.drop_table("memory_versions")
