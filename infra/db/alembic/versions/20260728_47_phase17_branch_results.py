"""phase17 branch result refs persistence

Revision ID: 20260728_47
Revises: 20260728_46
Create Date: 2026-07-28 10:15:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260728_47"
down_revision = "20260728_46"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "agent_branch_result_refs",
        sa.Column("branch_result_id", sa.String(length=220), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("step_run_id", sa.String(length=240), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("plan_version_id", sa.String(length=160), nullable=False),
        sa.Column("dynamic_step_id", sa.String(length=160), nullable=False),
        sa.Column("execution_epoch", sa.Integer(), nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("result_ref", sa.String(length=512), nullable=False),
        sa.Column("result_hash", sa.String(length=64), nullable=False),
        sa.Column("producer_ref", sa.String(length=240), nullable=False),
        sa.Column("ref_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["step_run_id"], ["agent_step_runs.step_run_id"], name="fk_agent_branch_result_step_run"),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_branch_result_run"),
        sa.ForeignKeyConstraint(["plan_version_id"], ["agent_plan_versions.plan_version_id"], name="fk_agent_branch_result_plan"),
        sa.UniqueConstraint(
            "step_run_id",
            "execution_epoch",
            "attempt_no",
            "result_hash",
            name="uq_agent_branch_result_step_attempt_hash",
        ),
        sa.CheckConstraint("execution_epoch > 0", name="ck_agent_branch_result_epoch"),
        sa.CheckConstraint("attempt_no > 0", name="ck_agent_branch_result_attempt"),
        sa.CheckConstraint("result_ref like 'object://%'", name="ck_agent_branch_result_object_ref"),
        _hash_check("result_hash", "ck_agent_branch_result_result_hash"),
        _hash_check("ref_hash", "ck_agent_branch_result_ref_hash"),
    )


def downgrade() -> None:
    op.drop_table("agent_branch_result_refs")
