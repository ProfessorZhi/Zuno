"""wave b memory and readonly tool runtime cutover

Revision ID: 20260727_41
Revises: 20260726_40
Create Date: 2026-07-27 00:41:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260727_41"
down_revision = "20260726_40"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "memory_capture_intents",
        sa.Column("capture_intent_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("source_module", sa.String(length=80), nullable=False),
        sa.Column("source_ref", sa.String(length=240), nullable=False),
        sa.Column("trigger_type", sa.String(length=80), nullable=False),
        sa.Column("policy_ref", sa.String(length=180), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=180), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "idempotency_key", name="uq_memory_capture_intents_idempotency"),
        _hash_check("payload_hash", "ck_memory_capture_intents_payload_hash"),
    )
    op.create_table(
        "memory_candidates_v2",
        sa.Column("candidate_id", sa.String(length=180), primary_key=True),
        sa.Column("capture_intent_id", sa.String(length=180), nullable=False),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("memory_kind", sa.String(length=40), nullable=False),
        sa.Column("origin", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_strength", sa.Float(), nullable=False),
        sa.Column("conflict_key", sa.String(length=240), nullable=False),
        sa.Column("dedupe_key", sa.String(length=240), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("source_refs", sa.JSON(), nullable=False),
        sa.Column("hidden_cot", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["capture_intent_id"], ["memory_capture_intents.capture_intent_id"], name="fk_memory_candidates_v2_intent"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "dedupe_key", name="uq_memory_candidates_v2_dedupe"),
        _hash_check("payload_hash", "ck_memory_candidates_v2_payload_hash"),
        sa.CheckConstraint("status in ('PROPOSED','VALIDATING','PENDING_REVIEW','APPROVED','REJECTED','QUARANTINED','EXPIRED')", name="ck_memory_candidates_v2_status"),
        sa.CheckConstraint("confidence >= 0 and confidence <= 1", name="ck_memory_candidates_v2_confidence"),
        sa.CheckConstraint("evidence_strength >= 0 and evidence_strength <= 1", name="ck_memory_candidates_v2_evidence"),
    )
    op.create_table(
        "memory_governance_decisions_v2",
        sa.Column("decision_id", sa.String(length=180), primary_key=True),
        sa.Column("candidate_id", sa.String(length=180), nullable=False),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("decision", sa.String(length=40), nullable=False),
        sa.Column("reviewer_type", sa.String(length=40), nullable=False),
        sa.Column("reviewer_ref", sa.String(length=180), nullable=False),
        sa.Column("policy_ref", sa.String(length=180), nullable=False),
        sa.Column("security_decision_ref", sa.String(length=180), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["memory_candidates_v2.candidate_id"], name="fk_memory_governance_v2_candidate"),
        _hash_check("decision_hash", "ck_memory_governance_v2_hash"),
        sa.CheckConstraint("reviewer_type in ('POLICY','HUMAN','SYSTEM')", name="ck_memory_governance_v2_reviewer"),
        sa.CheckConstraint("decision in ('APPROVE','REJECT','QUARANTINE','REQUEST_MORE_EVIDENCE')", name="ck_memory_governance_v2_decision"),
    )
    op.create_table(
        "memory_records",
        sa.Column("memory_record_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("memory_kind", sa.String(length=40), nullable=False),
        sa.Column("conflict_key", sa.String(length=240), nullable=False),
        sa.Column("active_version_id", sa.String(length=180), nullable=True),
        sa.Column("aggregate_generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "conflict_key", name="uq_memory_records_conflict_key"),
    )
    op.create_table(
        "memory_commit_receipts",
        sa.Column("receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("capture_intent_id", sa.String(length=180), nullable=False),
        sa.Column("candidate_id", sa.String(length=180), nullable=False),
        sa.Column("memory_record_id", sa.String(length=180), nullable=False),
        sa.Column("memory_version_id", sa.String(length=180), nullable=False),
        sa.Column("commit_state", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("domain_generation", sa.Integer(), nullable=False),
        sa.Column("receipt_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["capture_intent_id"], ["memory_capture_intents.capture_intent_id"], name="fk_memory_commit_receipt_intent"),
        sa.ForeignKeyConstraint(["candidate_id"], ["memory_candidates_v2.candidate_id"], name="fk_memory_commit_receipt_candidate"),
        sa.ForeignKeyConstraint(["memory_record_id"], ["memory_records.memory_record_id"], name="fk_memory_commit_receipt_record"),
        sa.ForeignKeyConstraint(["memory_version_id"], ["memory_versions.memory_version_id"], name="fk_memory_commit_receipt_version"),
        sa.UniqueConstraint("idempotency_key", name="uq_memory_commit_receipts_idempotency"),
        _hash_check("receipt_hash", "ck_memory_commit_receipts_hash"),
    )
    op.create_table(
        "context_selection_decisions",
        sa.Column("decision_id", sa.String(length=180), primary_key=True),
        sa.Column("context_pack_id", sa.String(length=180), nullable=False),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("source_ref", sa.String(length=240), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False),
        sa.Column("fidelity", sa.String(length=20), nullable=False),
        sa.Column("reason_code", sa.String(length=80), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["context_pack_id"], ["context_pack_versions.context_pack_id"], name="fk_context_selection_pack"),
        _hash_check("decision_hash", "ck_context_selection_decisions_hash"),
    )
    op.create_table(
        "context_compression_traces",
        sa.Column("compression_trace_id", sa.String(length=180), primary_key=True),
        sa.Column("context_pack_id", sa.String(length=180), nullable=False),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("strategy", sa.String(length=80), nullable=False),
        sa.Column("pre_tokens", sa.Integer(), nullable=False),
        sa.Column("post_tokens", sa.Integer(), nullable=False),
        sa.Column("trace_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["context_pack_id"], ["context_pack_versions.context_pack_id"], name="fk_context_compression_pack"),
        _hash_check("trace_hash", "ck_context_compression_traces_hash"),
    )
    op.create_table(
        "memory_use_traces",
        sa.Column("memory_use_trace_id", sa.String(length=180), primary_key=True),
        sa.Column("memory_version_id", sa.String(length=180), nullable=False),
        sa.Column("context_pack_id", sa.String(length=180), nullable=False),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=180), nullable=False),
        sa.Column("adopted_by_agent_core", sa.Boolean(), nullable=False),
        sa.Column("influenced_plan", sa.Boolean(), nullable=False),
        sa.Column("influenced_action", sa.Boolean(), nullable=False),
        sa.Column("trace_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["memory_version_id"], ["memory_versions.memory_version_id"], name="fk_memory_use_trace_version"),
        sa.ForeignKeyConstraint(["context_pack_id"], ["context_pack_versions.context_pack_id"], name="fk_memory_use_trace_pack"),
        _hash_check("trace_hash", "ck_memory_use_traces_hash"),
    )
    op.create_table(
        "tool_adapter_bindings",
        sa.Column("adapter_binding_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("tool_version_id", sa.String(length=180), nullable=False),
        sa.Column("adapter_kind", sa.String(length=40), nullable=False),
        sa.Column("adapter_version", sa.String(length=80), nullable=False),
        sa.Column("conformance_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tool_version_id"], ["tool_versions.tool_version_id"], name="fk_tool_adapter_bindings_version"),
        _hash_check("conformance_hash", "ck_tool_adapter_bindings_hash"),
    )
    op.create_table(
        "tool_bypass_guard_receipts",
        sa.Column("receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("scope", sa.String(length=120), nullable=False),
        sa.Column("allowlist_count", sa.Integer(), nullable=False),
        sa.Column("guard_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        _hash_check("guard_hash", "ck_tool_bypass_guard_receipts_hash"),
    )


def downgrade() -> None:
    op.drop_table("tool_bypass_guard_receipts")
    op.drop_table("tool_adapter_bindings")
    op.drop_table("memory_use_traces")
    op.drop_table("context_compression_traces")
    op.drop_table("context_selection_decisions")
    op.drop_table("memory_commit_receipts")
    op.drop_table("memory_records")
    op.drop_table("memory_governance_decisions_v2")
    op.drop_table("memory_candidates_v2")
    op.drop_table("memory_capture_intents")
