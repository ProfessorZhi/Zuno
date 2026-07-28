"""phase17 replan barriers persistence

Revision ID: 20260728_49
Revises: 20260728_48
Create Date: 2026-07-28 11:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260728_49"
down_revision = "20260728_48"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "agent_replan_barriers",
        sa.Column("barrier_id", sa.String(length=220), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("plan_id", sa.String(length=180), nullable=False),
        sa.Column("plan_version_id", sa.String(length=160), nullable=False),
        sa.Column("execution_epoch", sa.Integer(), nullable=False),
        sa.Column("source_control_decision_id", sa.String(length=220), nullable=False),
        sa.Column("source_control_decision_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("freeze_new_dispatch", sa.Boolean(), nullable=False),
        sa.Column("new_plan_version_required", sa.Boolean(), nullable=False),
        sa.Column("retry_permitted", sa.Boolean(), nullable=False),
        sa.Column("next_execution_epoch", sa.Integer(), nullable=False),
        sa.Column("step_decisions", sa.JSON(), nullable=False),
        sa.Column("barrier_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_replan_barriers_run"),
        sa.ForeignKeyConstraint(["plan_version_id"], ["agent_plan_versions.plan_version_id"], name="fk_agent_replan_barriers_plan"),
        sa.UniqueConstraint("tenant_id", "plan_version_id", "execution_epoch", name="uq_agent_replan_barriers_epoch"),
        sa.UniqueConstraint("tenant_id", "source_control_decision_hash", name="uq_agent_replan_barriers_control_hash"),
        sa.CheckConstraint("execution_epoch > 0", name="ck_agent_replan_barriers_epoch_positive"),
        sa.CheckConstraint("next_execution_epoch > execution_epoch", name="ck_agent_replan_barriers_next_epoch"),
        sa.CheckConstraint("freeze_new_dispatch = true", name="ck_agent_replan_barriers_freeze_dispatch"),
        sa.CheckConstraint("new_plan_version_required = true", name="ck_agent_replan_barriers_new_plan_version"),
        sa.CheckConstraint("retry_permitted = false", name="ck_agent_replan_barriers_no_retry"),
        sa.CheckConstraint("status in ('REQUESTED','DRAINING','READY_FOR_REPLAN','CANCELLED')", name="ck_agent_replan_barriers_status"),
        _hash_check("source_control_decision_hash", "ck_agent_replan_barriers_control_hash_format"),
        _hash_check("barrier_hash", "ck_agent_replan_barriers_hash"),
    )


def downgrade() -> None:
    op.drop_table("agent_replan_barriers")
