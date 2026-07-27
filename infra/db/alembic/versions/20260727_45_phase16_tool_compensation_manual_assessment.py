"""phase16 tool compensation manual assessment persistence

Revision ID: 20260727_45
Revises: 20260727_44
Create Date: 2026-07-27 19:35:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260727_45"
down_revision = "20260727_44"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "tool_compensation_definitions",
        sa.Column("compensation_definition_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("source_effect_receipt_id", sa.String(length=180), nullable=True),
        sa.Column("source_reconciliation_id", sa.String(length=180), nullable=True),
        sa.Column("compensation_capability", sa.String(length=40), nullable=False),
        sa.Column("operation_ref", sa.String(length=240), nullable=False),
        sa.Column("new_action_proposal_ref", sa.String(length=180), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False),
        sa.Column("window_deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("residual_impact", sa.String(length=80), nullable=False),
        sa.Column("policy_ref", sa.String(length=180), nullable=False),
        sa.Column("definition_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_effect_receipt_id"], ["tool_effect_receipts.effect_receipt_id"], name="fk_tool_comp_def_effect"),
        sa.ForeignKeyConstraint(["source_reconciliation_id"], ["tool_effect_reconciliations.reconciliation_id"], name="fk_tool_comp_def_reconciliation"),
        sa.UniqueConstraint("tenant_id", "new_action_proposal_ref", name="uq_tool_comp_def_action_proposal"),
        sa.CheckConstraint("compensation_capability in ('NON_COMPENSATABLE','MANUAL_COMPENSATION','BEST_EFFORT_COMPENSATION','AUTOMATIC_COMPENSATION')", name="ck_tool_comp_def_capability"),
        sa.CheckConstraint("(source_effect_receipt_id is not null) or (source_reconciliation_id is not null)", name="ck_tool_comp_def_source_present"),
        sa.CheckConstraint("residual_impact in ('NONE','LOW','PARTIAL','HIGH','UNKNOWN')", name="ck_tool_comp_def_residual_impact"),
        _hash_check("definition_payload_hash", "ck_tool_comp_def_payload_hash"),
    )
    op.create_table(
        "tool_compensation_attempts",
        sa.Column("compensation_attempt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("compensation_definition_id", sa.String(length=180), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("execution_receipt_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("hidden_rollback", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("idempotency_scope", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("idempotency_generation", sa.Integer(), nullable=False),
        sa.Column("audit_requirement_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["compensation_definition_id"], ["tool_compensation_definitions.compensation_definition_id"], name="fk_tool_comp_attempt_definition"),
        sa.ForeignKeyConstraint(["prepared_tool_action_id"], ["prepared_tool_actions.prepared_tool_action_id"], name="fk_tool_comp_attempt_prepared"),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_comp_attempt_attempt"),
        sa.ForeignKeyConstraint(["execution_receipt_id"], ["tool_execution_receipts.receipt_id"], name="fk_tool_comp_attempt_execution"),
        sa.UniqueConstraint("tenant_id", "idempotency_scope", "idempotency_key", name="uq_tool_comp_attempt_idempotency"),
        sa.CheckConstraint("status in ('PROPOSED','APPROVED','DISPATCHED','CONFIRMED','UNKNOWN','FAILED')", name="ck_tool_comp_attempt_status"),
        sa.CheckConstraint("hidden_rollback = false", name="ck_tool_comp_attempt_no_hidden_rollback"),
        sa.CheckConstraint("idempotency_generation > 0", name="ck_tool_comp_attempt_idem_generation"),
        _hash_check("attempt_payload_hash", "ck_tool_comp_attempt_payload_hash"),
    )
    op.create_table(
        "tool_manual_effect_assessments",
        sa.Column("manual_assessment_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("reconciliation_id", sa.String(length=180), nullable=False),
        sa.Column("provider_effect_id", sa.String(length=240), nullable=False),
        sa.Column("conclusion", sa.String(length=40), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("assessor_principal_id", sa.String(length=180), nullable=False),
        sa.Column("residual_uncertainty", sa.String(length=80), nullable=False),
        sa.Column("evidence_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["reconciliation_id"], ["tool_effect_reconciliations.reconciliation_id"], name="fk_tool_manual_assessment_reconciliation"),
        sa.UniqueConstraint("tenant_id", "reconciliation_id", name="uq_tool_manual_assessment_reconciliation"),
        sa.CheckConstraint("conclusion in ('CONFIRMED_EXECUTED','CONFIRMED_NOT_EXECUTED','PARTIAL','UNRESOLVED','ESCALATED')", name="ck_tool_manual_assessment_conclusion"),
        sa.CheckConstraint("confidence >= 0 and confidence <= 1", name="ck_tool_manual_assessment_confidence"),
        _hash_check("evidence_payload_hash", "ck_tool_manual_assessment_evidence_hash"),
    )


def downgrade() -> None:
    op.drop_table("tool_manual_effect_assessments")
    op.drop_table("tool_compensation_attempts")
    op.drop_table("tool_compensation_definitions")