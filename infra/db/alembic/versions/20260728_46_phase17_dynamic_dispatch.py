"""phase17 dynamic plan dispatch persistence

Revision ID: 20260728_46
Revises: 20260727_45
Create Date: 2026-07-28 09:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260728_46"
down_revision = "20260727_45"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.drop_constraint("ck_agent_plan_versions_kind", "agent_plan_versions", type_="check")
    op.create_check_constraint(
        "ck_agent_plan_versions_kind",
        "agent_plan_versions",
        "plan_kind in ('DETERMINISTIC_SINGLE_STEP','DYNAMIC_DAG')",
    )
    op.drop_constraint("ck_agent_plan_step_definitions_single_step", "agent_plan_step_definitions", type_="check")
    op.drop_constraint("ck_agent_plan_step_definitions_executor", "agent_plan_step_definitions", type_="check")
    op.add_column("agent_plan_step_definitions", sa.Column("dynamic_step_id", sa.String(length=160), nullable=True))
    op.add_column("agent_plan_step_definitions", sa.Column("dependency_step_ids", sa.JSON(), nullable=True))
    op.add_column("agent_plan_step_definitions", sa.Column("dependency_rule", sa.String(length=48), nullable=True))
    op.add_column("agent_plan_step_definitions", sa.Column("activation_condition_ref", sa.String(length=240), nullable=True))
    op.add_column("agent_plan_step_definitions", sa.Column("resource_claim_refs", sa.JSON(), nullable=True))
    op.add_column("agent_plan_step_definitions", sa.Column("join_policy_ref", sa.String(length=120), nullable=True))
    op.create_check_constraint(
        "ck_agent_plan_step_definitions_executor",
        "agent_plan_step_definitions",
        "executor_type in ('MODEL','KNOWLEDGE','CAPABILITY','TOOL','DETERMINISTIC','JOIN','INGESTION_WAIT','FINAL_GATE')",
    )
    op.create_unique_constraint(
        "uq_agent_plan_step_definitions_dynamic_step",
        "agent_plan_step_definitions",
        ["plan_version_id", "dynamic_step_id"],
    )

    op.create_table(
        "agent_dispatch_groups",
        sa.Column("dispatch_group_id", sa.String(length=220), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("plan_id", sa.String(length=180), nullable=False),
        sa.Column("plan_version_id", sa.String(length=160), nullable=False),
        sa.Column("execution_epoch", sa.Integer(), nullable=False),
        sa.Column("admitted_step_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("committed_before_send", sa.Boolean(), nullable=False),
        sa.Column("group_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_dispatch_groups_run"),
        sa.ForeignKeyConstraint(["plan_version_id"], ["agent_plan_versions.plan_version_id"], name="fk_agent_dispatch_groups_plan"),
        sa.UniqueConstraint("run_id", "plan_version_id", "execution_epoch", name="uq_agent_dispatch_groups_epoch"),
        sa.CheckConstraint("execution_epoch > 0", name="ck_agent_dispatch_groups_epoch"),
        sa.CheckConstraint("status in ('COMMITTED','CANCELLED','DRAINED')", name="ck_agent_dispatch_groups_status"),
        sa.CheckConstraint("committed_before_send = true", name="ck_agent_dispatch_groups_commit_before_send"),
        _hash_check("group_hash", "ck_agent_dispatch_groups_hash"),
    )
    op.create_table(
        "agent_step_runs",
        sa.Column("step_run_id", sa.String(length=240), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("plan_version_id", sa.String(length=160), nullable=False),
        sa.Column("dynamic_step_id", sa.String(length=160), nullable=False),
        sa.Column("execution_epoch", sa.Integer(), nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("step_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_step_runs_run"),
        sa.ForeignKeyConstraint(["plan_version_id"], ["agent_plan_versions.plan_version_id"], name="fk_agent_step_runs_plan"),
        sa.UniqueConstraint(
            "run_id",
            "plan_version_id",
            "dynamic_step_id",
            "execution_epoch",
            "attempt_no",
            name="uq_agent_step_runs_attempt",
        ),
        sa.CheckConstraint("execution_epoch > 0", name="ck_agent_step_runs_epoch"),
        sa.CheckConstraint("attempt_no > 0", name="ck_agent_step_runs_attempt"),
        sa.CheckConstraint(
            "status in ('QUEUED','CLAIMED','RUNNING','SUCCEEDED','FAILED','CANCELLED','OBSOLETE')",
            name="ck_agent_step_runs_status",
        ),
        _hash_check("step_hash", "ck_agent_step_runs_hash"),
    )
    op.create_table(
        "agent_dispatch_items",
        sa.Column("dispatch_item_id", sa.String(length=260), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("dispatch_group_id", sa.String(length=220), nullable=False),
        sa.Column("step_run_id", sa.String(length=240), nullable=False),
        sa.Column("dynamic_step_id", sa.String(length=160), nullable=False),
        sa.Column("send_idempotency_key", sa.String(length=320), nullable=False),
        sa.Column("outbox_event_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dispatch_group_id"], ["agent_dispatch_groups.dispatch_group_id"], name="fk_agent_dispatch_items_group"),
        sa.ForeignKeyConstraint(["step_run_id"], ["agent_step_runs.step_run_id"], name="fk_agent_dispatch_items_step_run"),
        sa.UniqueConstraint("tenant_id", "send_idempotency_key", name="uq_agent_dispatch_items_send_key"),
        sa.UniqueConstraint("tenant_id", "outbox_event_id", name="uq_agent_dispatch_items_outbox"),
        sa.CheckConstraint("status in ('PENDING_SEND','SENT','CANCELLED','OBSOLETE')", name="ck_agent_dispatch_items_status"),
    )


def downgrade() -> None:
    op.drop_table("agent_dispatch_items")
    op.drop_table("agent_step_runs")
    op.drop_table("agent_dispatch_groups")
    op.drop_constraint("uq_agent_plan_step_definitions_dynamic_step", "agent_plan_step_definitions", type_="unique")
    op.drop_constraint("ck_agent_plan_step_definitions_executor", "agent_plan_step_definitions", type_="check")
    op.drop_column("agent_plan_step_definitions", "join_policy_ref")
    op.drop_column("agent_plan_step_definitions", "resource_claim_refs")
    op.drop_column("agent_plan_step_definitions", "activation_condition_ref")
    op.drop_column("agent_plan_step_definitions", "dependency_rule")
    op.drop_column("agent_plan_step_definitions", "dependency_step_ids")
    op.drop_column("agent_plan_step_definitions", "dynamic_step_id")
    op.create_check_constraint(
        "ck_agent_plan_step_definitions_executor",
        "agent_plan_step_definitions",
        "executor_type in ('MODEL','KNOWLEDGE','CAPABILITY','TOOL','INGESTION_WAIT','FINAL_GATE')",
    )
    op.create_check_constraint(
        "ck_agent_plan_step_definitions_single_step",
        "agent_plan_step_definitions",
        "step_no = 1",
    )
    op.drop_constraint("ck_agent_plan_versions_kind", "agent_plan_versions", type_="check")
    op.create_check_constraint(
        "ck_agent_plan_versions_kind",
        "agent_plan_versions",
        "plan_kind in ('DETERMINISTIC_SINGLE_STEP')",
    )
