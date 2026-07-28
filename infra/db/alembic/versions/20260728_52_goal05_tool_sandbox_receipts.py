"""add tool sandbox receipts

Revision ID: 20260728_52
Revises: 20260728_51
Create Date: 2026-07-28 00:52:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260728_52"
down_revision = "20260728_51"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "tool_sandbox_receipts",
        sa.Column("sandbox_receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("sandbox_profile_id", sa.String(length=180), nullable=False),
        sa.Column("adapter_tier", sa.String(length=40), nullable=False),
        sa.Column("session_ref", sa.String(length=240), nullable=False),
        sa.Column("session_version", sa.Integer(), nullable=False),
        sa.Column("profile_hash", sa.String(length=64), nullable=False),
        sa.Column("limits_hash", sa.String(length=64), nullable=False),
        sa.Column("session_hash", sa.String(length=64), nullable=False),
        sa.Column("state_integrity_hash", sa.String(length=64), nullable=False),
        sa.Column("isolation_verified", sa.Boolean(), nullable=False),
        sa.Column("allowlist_enforced", sa.Boolean(), nullable=False),
        sa.Column("receipt_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["prepared_tool_action_id"],
            ["prepared_tool_actions.prepared_tool_action_id"],
            name="fk_tool_sandbox_receipts_prepared",
        ),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_sandbox_receipts_attempt"),
        sa.UniqueConstraint("tenant_id", "prepared_tool_action_id", "attempt_id", name="uq_tool_sandbox_receipts_attempt"),
        _hash_check("profile_hash", "ck_tool_sandbox_receipts_profile_hash"),
        _hash_check("limits_hash", "ck_tool_sandbox_receipts_limits_hash"),
        _hash_check("session_hash", "ck_tool_sandbox_receipts_session_hash"),
        _hash_check("state_integrity_hash", "ck_tool_sandbox_receipts_state_hash"),
        _hash_check("receipt_payload_hash", "ck_tool_sandbox_receipts_payload_hash"),
        sa.CheckConstraint("session_version > 0", name="ck_tool_sandbox_receipts_session_version"),
        sa.CheckConstraint("adapter_tier in ('WASM_PYTHON','OCI_PROCESS')", name="ck_tool_sandbox_receipts_adapter_tier"),
        sa.CheckConstraint("isolation_verified = true", name="ck_tool_sandbox_receipts_isolation_verified"),
        sa.CheckConstraint("allowlist_enforced = true", name="ck_tool_sandbox_receipts_allowlist_enforced"),
    )


def downgrade() -> None:
    op.drop_table("tool_sandbox_receipts")
