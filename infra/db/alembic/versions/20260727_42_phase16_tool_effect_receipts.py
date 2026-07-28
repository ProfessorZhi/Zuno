"""phase16 tool effect receipt persistence

Revision ID: 20260727_42
Revises: 20260727_41
Create Date: 2026-07-27 16:42:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260727_42"
down_revision = "20260727_41"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "tool_effect_receipts",
        sa.Column("effect_receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("execution_receipt_id", sa.String(length=180), nullable=False),
        sa.Column("provider_effect_id", sa.String(length=240), nullable=False),
        sa.Column("effect_status", sa.String(length=40), nullable=False),
        sa.Column("effect_certainty", sa.String(length=40), nullable=False),
        sa.Column("idempotency_scope", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("idempotency_generation", sa.Integer(), nullable=False),
        sa.Column("fencing_resource_id", sa.String(length=240), nullable=False),
        sa.Column("fencing_lease_id", sa.String(length=180), nullable=False),
        sa.Column("fencing_epoch", sa.Integer(), nullable=False),
        sa.Column("secret_lease_id", sa.String(length=180), nullable=True),
        sa.Column("native_result_hash", sa.String(length=64), nullable=False),
        sa.Column("effect_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("append_only_generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["prepared_tool_action_id"], ["prepared_tool_actions.prepared_tool_action_id"], name="fk_tool_effect_receipts_prepared"),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_effect_receipts_attempt"),
        sa.ForeignKeyConstraint(["execution_receipt_id"], ["tool_execution_receipts.receipt_id"], name="fk_tool_effect_receipts_execution"),
        sa.UniqueConstraint("tenant_id", "provider_effect_id", name="uq_tool_effect_receipts_provider_effect"),
        sa.UniqueConstraint("tenant_id", "idempotency_scope", "idempotency_key", name="uq_tool_effect_receipts_idempotency"),
        sa.CheckConstraint("effect_status in ('CONFIRMED','FAILED','NO_EFFECT')", name="ck_tool_effect_receipts_status"),
        sa.CheckConstraint("effect_certainty in ('CONFIRMED_EFFECT','CONFIRMED_NO_EFFECT')", name="ck_tool_effect_receipts_certainty"),
        sa.CheckConstraint("idempotency_generation > 0", name="ck_tool_effect_receipts_idem_generation"),
        sa.CheckConstraint("fencing_epoch > 0", name="ck_tool_effect_receipts_fencing_epoch"),
        sa.CheckConstraint("append_only_generation > 0", name="ck_tool_effect_receipts_generation"),
        _hash_check("native_result_hash", "ck_tool_effect_receipts_native_hash"),
        _hash_check("effect_payload_hash", "ck_tool_effect_receipts_payload_hash"),
    )


def downgrade() -> None:
    op.drop_table("tool_effect_receipts")
