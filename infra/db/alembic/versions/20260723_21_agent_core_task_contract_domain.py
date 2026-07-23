"""add agent core task contract domain facts

Revision ID: 20260723_21
Revises: 20260720_20
Create Date: 2026-07-23 21:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260723_21"
down_revision = "20260720_20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_goal_versions",
        sa.Column("goal_version_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("principal_id", sa.String(length=160), nullable=False),
        sa.Column("goal_sequence", sa.Integer(), nullable=False),
        sa.Column("input_classification", sa.String(length=48), nullable=False),
        sa.Column("objective_hash", sa.String(length=64), nullable=False),
        sa.Column("output_contract_ref", sa.String(length=240), nullable=False),
        sa.Column("constraints_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint(
            "tenant_id",
            "workspace_id",
            "principal_id",
            "goal_sequence",
            name="uq_agent_goal_versions_sequence",
        ),
        sa.CheckConstraint("goal_sequence > 0", name="ck_agent_goal_versions_sequence"),
        sa.CheckConstraint("length(objective_hash) = 64", name="ck_agent_goal_versions_objective_hash"),
        sa.CheckConstraint("length(constraints_hash) = 64", name="ck_agent_goal_versions_constraints_hash"),
        sa.CheckConstraint(
            "input_classification in ("
            "'SUPPLEMENTAL_INPUT','CLARIFICATION_RESPONSE','CONSTRAINT_CHANGE',"
            "'OUTPUT_CONTRACT_CHANGE','OBJECTIVE_CHANGE','CANCELLATION_REQUEST','NEW_TASK'"
            ")",
            name="ck_agent_goal_versions_classification",
        ),
    )

    op.create_table(
        "agent_task_contracts",
        sa.Column("task_contract_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("principal_id", sa.String(length=160), nullable=False),
        sa.Column("goal_version_id", sa.String(length=160), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("security_context_ref", sa.String(length=240), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=160), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("budget_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("aggregate_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["goal_version_id"],
            ["agent_goal_versions.goal_version_id"],
            ondelete="RESTRICT",
            name="fk_agent_task_contracts_goal_version",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "workspace_id",
            "idempotency_key",
            name="uq_agent_task_contracts_idempotency",
        ),
        sa.CheckConstraint("aggregate_version > 0", name="ck_agent_task_contracts_version"),
        sa.CheckConstraint("status in ('ACTIVE','CANCELLED','FAILED','COMPLETED')", name="ck_agent_task_contracts_status"),
    )

    op.create_table(
        "agent_domain_runs",
        sa.Column("run_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("principal_id", sa.String(length=160), nullable=False),
        sa.Column("task_contract_id", sa.String(length=160), nullable=False),
        sa.Column("trace_id", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("aggregate_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("domain_generation", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_code", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_contract_id"],
            ["agent_task_contracts.task_contract_id"],
            ondelete="RESTRICT",
            name="fk_agent_domain_runs_task_contract",
        ),
        sa.UniqueConstraint("task_contract_id", name="uq_agent_domain_runs_task_contract"),
        sa.CheckConstraint("aggregate_version > 0", name="ck_agent_domain_runs_version"),
        sa.CheckConstraint("domain_generation > 0", name="ck_agent_domain_runs_generation"),
        sa.CheckConstraint(
            "status in ('CREATED','AUTHORIZED','STARTED','CANCELLING','CANCELLED','FAILED','COMPLETED')",
            name="ck_agent_domain_runs_status",
        ),
    )

    op.create_table(
        "agent_domain_events",
        sa.Column("event_id", sa.String(length=200), primary_key=True),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("domain_generation", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["agent_domain_runs.run_id"],
            ondelete="RESTRICT",
            name="fk_agent_domain_events_run",
        ),
        sa.UniqueConstraint("run_id", "sequence_no", name="uq_agent_domain_events_sequence"),
        sa.CheckConstraint("sequence_no > 0", name="ck_agent_domain_events_sequence"),
        sa.CheckConstraint("domain_generation > 0", name="ck_agent_domain_events_generation"),
    )


def downgrade() -> None:
    op.drop_table("agent_domain_events")
    op.drop_table("agent_domain_runs")
    op.drop_table("agent_task_contracts")
    op.drop_table("agent_goal_versions")
