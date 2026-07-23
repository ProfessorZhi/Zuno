"""add agent core runtime closure ledgers

Revision ID: 20260724_26
Revises: 20260724_25
Create Date: 2026-07-24 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260724_26"
down_revision = "20260724_25"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_request_idempotency_keys",
        sa.Column("idempotency_key", sa.String(length=240), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("aggregate_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_agent_request_idempotency_tenant_key"),
        sa.CheckConstraint("char_length(payload_hash) = 64", name="ck_agent_request_idempotency_hash"),
    )
    op.create_table(
        "agent_action_runs",
        sa.Column("action_run_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("step_run_id", sa.String(length=180), nullable=False),
        sa.Column("owner_port", sa.String(length=80), nullable=False),
        sa.Column("proposal_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("trace_ref", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_action_runs_run"),
        sa.UniqueConstraint("tenant_id", "step_run_id", "owner_port", "proposal_hash", name="uq_agent_action_runs_step_owner_proposal"),
        sa.CheckConstraint("char_length(proposal_hash) = 64", name="ck_agent_action_runs_hash"),
    )
    op.create_table(
        "agent_observations",
        sa.Column("observation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("action_run_id", sa.String(length=180), nullable=False),
        sa.Column("observation_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("evidence_refs", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["action_run_id"], ["agent_action_runs.action_run_id"], name="fk_agent_observations_action"),
        sa.UniqueConstraint("tenant_id", "action_run_id", "observation_hash", name="uq_agent_observations_action_hash"),
        sa.CheckConstraint("char_length(observation_hash) = 64", name="ck_agent_observations_hash"),
    )
    op.create_table(
        "agent_step_acceptances",
        sa.Column("acceptance_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("step_run_id", sa.String(length=180), nullable=False),
        sa.Column("observation_id", sa.String(length=180), nullable=False),
        sa.Column("acceptance_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["observation_id"], ["agent_observations.observation_id"], name="fk_agent_acceptances_observation"),
        sa.UniqueConstraint("tenant_id", "step_run_id", name="uq_agent_step_acceptances_step"),
        sa.CheckConstraint("char_length(acceptance_hash) = 64", name="ck_agent_step_acceptances_hash"),
    )
    op.create_table(
        "agent_effect_claims",
        sa.Column("effect_claim_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("owner_port", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("effect_ref", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_agent_effect_claims_tenant_key"),
        sa.CheckConstraint("char_length(payload_hash) = 64", name="ck_agent_effect_claims_hash"),
    )
    op.create_table(
        "agent_final_gate_receipts",
        sa.Column("final_gate_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("decision", sa.String(length=40), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("answer_policy_ref", sa.String(length=240), nullable=False),
        sa.Column("evidence_ref", sa.String(length=240), nullable=False),
        sa.Column("security_decision_ref", sa.String(length=240), nullable=False),
        sa.Column("budget_settlement_ref", sa.String(length=240), nullable=False),
        sa.Column("step_acceptance_ref", sa.String(length=240), nullable=False),
        sa.Column("publication_eligible", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_final_gate_run"),
        sa.UniqueConstraint("tenant_id", "run_id", name="uq_agent_final_gate_run"),
        sa.CheckConstraint("char_length(decision_hash) = 64", name="ck_agent_final_gate_hash"),
    )
    op.create_table(
        "agent_run_outcomes",
        sa.Column("run_outcome_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("final_gate_id", sa.String(length=180), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("outcome_hash", sa.String(length=64), nullable=False),
        sa.Column("publication_ref", sa.String(length=240), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_run_outcomes_run"),
        sa.ForeignKeyConstraint(["final_gate_id"], ["agent_final_gate_receipts.final_gate_id"], name="fk_agent_run_outcomes_final_gate"),
        sa.UniqueConstraint("tenant_id", "run_id", name="uq_agent_run_outcomes_run"),
        sa.CheckConstraint("char_length(outcome_hash) = 64", name="ck_agent_run_outcomes_hash"),
    )
    op.create_table(
        "agent_runtime_signals",
        sa.Column("signal_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("signal_type", sa.String(length=60), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_runtime_signals_run"),
        sa.UniqueConstraint("tenant_id", "run_id", "signal_type", "payload_hash", name="uq_agent_runtime_signals_payload"),
        sa.CheckConstraint("char_length(payload_hash) = 64", name="ck_agent_runtime_signals_hash"),
    )
    op.create_table(
        "agent_reconciliation_findings",
        sa.Column("finding_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("run_id", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("fact_owner", sa.String(length=60), nullable=False),
        sa.Column("auto_repair", sa.Boolean(), nullable=False),
        sa.Column("replay_allowed", sa.Boolean(), nullable=False),
        sa.Column("terminate_run", sa.Boolean(), nullable=False),
        sa.Column("audit_event_ref", sa.String(length=240), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_domain_runs.run_id"], name="fk_agent_reconciliation_run"),
        sa.UniqueConstraint("tenant_id", "run_id", "status", "payload_hash", name="uq_agent_reconciliation_status_payload"),
        sa.CheckConstraint(
            "status in ('aligned','domain_ahead','checkpoint_ahead','orphan_checkpoint','orphan_domain','stale_schema','stale_controller_epoch','unrecoverable_conflict')",
            name="ck_agent_reconciliation_status",
        ),
        sa.CheckConstraint("char_length(payload_hash) = 64", name="ck_agent_reconciliation_hash"),
    )
    op.create_table(
        "agent_cutover_audit_events",
        sa.Column("cutover_event_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("request_id", sa.String(length=180), nullable=False),
        sa.Column("mode", sa.String(length=40), nullable=False),
        sa.Column("primary_runtime", sa.String(length=40), nullable=False),
        sa.Column("effect_committed", sa.Boolean(), nullable=False),
        sa.Column("fallback_allowed", sa.Boolean(), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("trace_ref", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "request_id", "mode", name="uq_agent_cutover_audit_request_mode"),
        sa.CheckConstraint("mode in ('shadow','canary','new_default','rollback')", name="ck_agent_cutover_audit_mode"),
        sa.CheckConstraint("char_length(request_hash) = 64", name="ck_agent_cutover_audit_hash"),
    )


def downgrade() -> None:
    op.drop_table("agent_cutover_audit_events")
    op.drop_table("agent_reconciliation_findings")
    op.drop_table("agent_runtime_signals")
    op.drop_table("agent_run_outcomes")
    op.drop_table("agent_final_gate_receipts")
    op.drop_table("agent_effect_claims")
    op.drop_table("agent_step_acceptances")
    op.drop_table("agent_observations")
    op.drop_table("agent_action_runs")
    op.drop_table("agent_request_idempotency_keys")
