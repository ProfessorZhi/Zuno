"""add agent core deterministic plan version domain facts

Revision ID: 20260723_22
Revises: 20260723_21
Create Date: 2026-07-23 22:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260723_22"
down_revision = "20260723_21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_plan_versions",
        sa.Column("plan_version_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("goal_version_id", sa.String(length=160), nullable=False),
        sa.Column("plan_kind", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("plan_hash", sa.String(length=64), nullable=False),
        sa.Column("aggregate_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["goal_version_id"],
            ["agent_goal_versions.goal_version_id"],
            ondelete="RESTRICT",
            name="fk_agent_plan_versions_goal_version",
        ),
        sa.UniqueConstraint("goal_version_id", "plan_hash", name="uq_agent_plan_versions_goal_hash"),
        sa.CheckConstraint("length(plan_hash) = 64", name="ck_agent_plan_versions_hash"),
        sa.CheckConstraint("aggregate_version > 0", name="ck_agent_plan_versions_version"),
        sa.CheckConstraint("plan_kind in ('DETERMINISTIC_SINGLE_STEP')", name="ck_agent_plan_versions_kind"),
        sa.CheckConstraint("status in ('DRAFT','ACTIVE','REJECTED','SUPERSEDED')", name="ck_agent_plan_versions_status"),
    )

    op.create_table(
        "agent_plan_step_definitions",
        sa.Column("step_definition_id", sa.String(length=160), primary_key=True),
        sa.Column("plan_version_id", sa.String(length=160), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("step_no", sa.Integer(), nullable=False),
        sa.Column("objective_ref", sa.String(length=240), nullable=False),
        sa.Column("input_contract_ref", sa.String(length=240), nullable=False),
        sa.Column("output_contract_ref", sa.String(length=240), nullable=False),
        sa.Column("acceptance_refs", sa.JSON(), nullable=False),
        sa.Column("executor_type", sa.String(length=48), nullable=False),
        sa.Column("required_evidence_refs", sa.JSON(), nullable=False),
        sa.Column("budget_ref", sa.String(length=240), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("step_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["plan_version_id"],
            ["agent_plan_versions.plan_version_id"],
            ondelete="RESTRICT",
            name="fk_agent_plan_step_definitions_plan",
        ),
        sa.UniqueConstraint("plan_version_id", "step_no", name="uq_agent_plan_step_definitions_no"),
        sa.UniqueConstraint("plan_version_id", "step_hash", name="uq_agent_plan_step_definitions_hash"),
        sa.CheckConstraint("step_no = 1", name="ck_agent_plan_step_definitions_single_step"),
        sa.CheckConstraint("length(step_hash) = 64", name="ck_agent_plan_step_definitions_hash"),
        sa.CheckConstraint(
            "executor_type in ('MODEL','KNOWLEDGE','CAPABILITY','TOOL','INGESTION_WAIT','FINAL_GATE')",
            name="ck_agent_plan_step_definitions_executor",
        ),
    )


def downgrade() -> None:
    op.drop_table("agent_plan_step_definitions")
    op.drop_table("agent_plan_versions")
