"""phase16 tool effect reconciliation persistence

Revision ID: 20260727_43
Revises: 20260727_42
Create Date: 2026-07-27 17:43:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260727_43"
down_revision = "20260727_42"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "tool_effect_reconciliations",
        sa.Column("reconciliation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("execution_receipt_id", sa.String(length=180), nullable=False),
        sa.Column("provider_effect_id", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("next_action", sa.String(length=40), nullable=False),
        sa.Column("reconciliation_query_hash", sa.String(length=64), nullable=False),
        sa.Column("manual_assessment_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("age_escalation_after_seconds", sa.Integer(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error_code", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("idempotency_scope", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("idempotency_generation", sa.Integer(), nullable=False),
        sa.Column("fencing_resource_id", sa.String(length=240), nullable=False),
        sa.Column("fencing_lease_id", sa.String(length=180), nullable=False),
        sa.Column("fencing_epoch", sa.Integer(), nullable=False),
        sa.Column("secret_lease_id", sa.String(length=180), nullable=True),
        sa.Column("reconciliation_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["prepared_tool_action_id"], ["prepared_tool_actions.prepared_tool_action_id"], name="fk_tool_effect_reconciliations_prepared"),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_effect_reconciliations_attempt"),
        sa.ForeignKeyConstraint(["execution_receipt_id"], ["tool_execution_receipts.receipt_id"], name="fk_tool_effect_reconciliations_execution"),
        sa.UniqueConstraint("tenant_id", "provider_effect_id", name="uq_tool_effect_reconciliations_provider_effect"),
        sa.UniqueConstraint("tenant_id", "idempotency_scope", "idempotency_key", name="uq_tool_effect_reconciliations_idempotency"),
        sa.CheckConstraint("status in ('OPEN','WAITING_PROVIDER','MANUAL_ASSESSMENT','RESOLVED','ESCALATED')", name="ck_tool_effect_reconciliations_status"),
        sa.CheckConstraint("next_action in ('RECONCILE','WAIT','MANUAL_ASSESSMENT')", name="ck_tool_effect_reconciliations_next_action"),
        sa.CheckConstraint("age_escalation_after_seconds > 0", name="ck_tool_effect_reconciliations_age_positive"),
        sa.CheckConstraint("attempt_count >= 0", name="ck_tool_effect_reconciliations_attempt_count"),
        sa.CheckConstraint("idempotency_generation > 0", name="ck_tool_effect_reconciliations_idem_generation"),
        sa.CheckConstraint("fencing_epoch > 0", name="ck_tool_effect_reconciliations_fencing_epoch"),
        _hash_check("reconciliation_query_hash", "ck_tool_effect_reconciliations_query_hash"),
        _hash_check("reconciliation_payload_hash", "ck_tool_effect_reconciliations_payload_hash"),
    )


def downgrade() -> None:
    op.drop_table("tool_effect_reconciliations")