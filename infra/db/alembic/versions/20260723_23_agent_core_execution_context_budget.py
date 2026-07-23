"""add agent core execution context snapshot and budget ledger

Revision ID: 20260723_23
Revises: 20260723_22
Create Date: 2026-07-23 23:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260723_23"
down_revision = "20260723_22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_budget_reservations",
        sa.Column("budget_reservation_id", sa.String(length=160), primary_key=True),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("budget_ref", sa.String(length=240), nullable=False),
        sa.Column("reservation_scope", sa.String(length=64), nullable=False),
        sa.Column("requested_units", sa.Integer(), nullable=False),
        sa.Column("reserved_units", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("aggregate_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["agent_domain_runs.run_id"],
            ondelete="RESTRICT",
            name="fk_agent_budget_reservations_run",
        ),
        sa.CheckConstraint("requested_units > 0", name="ck_agent_budget_reservations_requested"),
        sa.CheckConstraint("reserved_units > 0", name="ck_agent_budget_reservations_reserved"),
        sa.CheckConstraint("reserved_units <= requested_units", name="ck_agent_budget_reservations_capacity"),
        sa.CheckConstraint("aggregate_version > 0", name="ck_agent_budget_reservations_version"),
        sa.CheckConstraint("status in ('RESERVED','SETTLED')", name="ck_agent_budget_reservations_status"),
    )

    op.create_table(
        "agent_budget_settlements",
        sa.Column("budget_settlement_id", sa.String(length=180), primary_key=True),
        sa.Column("budget_reservation_id", sa.String(length=160), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("consumed_units", sa.Integer(), nullable=False),
        sa.Column("released_units", sa.Integer(), nullable=False),
        sa.Column("reason_ref", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["budget_reservation_id"],
            ["agent_budget_reservations.budget_reservation_id"],
            ondelete="RESTRICT",
            name="fk_agent_budget_settlements_reservation",
        ),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["agent_domain_runs.run_id"],
            ondelete="RESTRICT",
            name="fk_agent_budget_settlements_run",
        ),
        sa.UniqueConstraint("budget_reservation_id", name="uq_agent_budget_settlements_reservation"),
        sa.CheckConstraint("consumed_units >= 0", name="ck_agent_budget_settlements_consumed"),
        sa.CheckConstraint("released_units >= 0", name="ck_agent_budget_settlements_released"),
    )

    op.create_table(
        "agent_execution_context_snapshots",
        sa.Column("execution_snapshot_id", sa.String(length=160), primary_key=True),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("principal_id", sa.String(length=128), nullable=False),
        sa.Column("task_contract_id", sa.String(length=160), nullable=False),
        sa.Column("security_context_ref", sa.String(length=240), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=240), nullable=False),
        sa.Column("model_policy_ref", sa.String(length=240), nullable=False),
        sa.Column("capability_profile_ref", sa.String(length=240), nullable=False),
        sa.Column("knowledge_snapshot_ref", sa.String(length=240), nullable=False),
        sa.Column("answer_policy_ref", sa.String(length=240), nullable=False),
        sa.Column("budget_reservation_id", sa.String(length=160), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("context_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["agent_domain_runs.run_id"],
            ondelete="RESTRICT",
            name="fk_agent_execution_context_snapshots_run",
        ),
        sa.ForeignKeyConstraint(
            ["task_contract_id"],
            ["agent_task_contracts.task_contract_id"],
            ondelete="RESTRICT",
            name="fk_agent_execution_context_snapshots_task",
        ),
        sa.ForeignKeyConstraint(
            ["budget_reservation_id"],
            ["agent_budget_reservations.budget_reservation_id"],
            ondelete="RESTRICT",
            name="fk_agent_execution_context_snapshots_budget",
        ),
        sa.UniqueConstraint("run_id", "context_hash", name="uq_agent_execution_context_snapshots_run_hash"),
        sa.CheckConstraint("length(context_hash) = 64", name="ck_agent_execution_context_snapshots_hash"),
    )


def downgrade() -> None:
    op.drop_table("agent_execution_context_snapshots")
    op.drop_table("agent_budget_settlements")
    op.drop_table("agent_budget_reservations")
