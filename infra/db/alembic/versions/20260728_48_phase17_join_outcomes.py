"""phase17 join outcomes persistence

Revision ID: 20260728_48
Revises: 20260728_47
Create Date: 2026-07-28 10:45:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260728_48"
down_revision = "20260728_47"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "agent_join_outcomes",
        sa.Column("join_outcome_id", sa.String(length=220), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("plan_id", sa.String(length=180), nullable=False),
        sa.Column("plan_version_id", sa.String(length=160), nullable=False),
        sa.Column("join_policy", sa.String(length=40), nullable=False),
        sa.Column("expected_branch_count", sa.Integer(), nullable=False),
        sa.Column("reduced_results", sa.JSON(), nullable=False),
        sa.Column("duplicate_result_ids", sa.JSON(), nullable=False),
        sa.Column("decision", sa.String(length=40), nullable=False),
        sa.Column("outcome_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["plan_version_id"], ["agent_plan_versions.plan_version_id"], name="fk_agent_join_outcomes_plan"),
        sa.UniqueConstraint("tenant_id", "plan_version_id", "outcome_hash", name="uq_agent_join_outcomes_plan_hash"),
        sa.CheckConstraint("expected_branch_count > 0", name="ck_agent_join_outcomes_expected_count"),
        sa.CheckConstraint("join_policy in ('ALL_REQUIRED','BEST_EFFORT','QUORUM','FAIL_FAST')", name="ck_agent_join_outcomes_policy"),
        sa.CheckConstraint("decision in ('CONTINUE','WAIT','FAIL','PARTIAL_CONTINUE')", name="ck_agent_join_outcomes_decision"),
        _hash_check("outcome_hash", "ck_agent_join_outcomes_hash"),
    )


def downgrade() -> None:
    op.drop_table("agent_join_outcomes")
