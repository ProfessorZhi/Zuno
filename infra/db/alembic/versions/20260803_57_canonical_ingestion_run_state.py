"""add canonical ingestion run domain state

PHASE22 CC-B1/B2 hardening (DeepSeek1): the canonical ingestion state machine
gains a durable, tenant-scoped current-state owner. Outbox delivery events and
domain/current-state ownership are separated: current state is read from
``canonical_ingestion_runs`` only, while ``ingestion_outbox_events`` remains a
delivery fact.

Revision ID: 20260803_57
Revises: 20260729_56
Create Date: 2026-08-03 00:57:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260803_57"
down_revision = "20260729_56"
branch_labels = None
depends_on = None

# Canonical ingestion state machine (normal + failure + designed retry /
# reconciliation transitions). Terminal states reject ordinary overwrites in
# the repository; only the explicit reconciliation transition may follow.
_CANONICAL_RUN_STATES = (
    "accepted",
    "object_staged",
    "object_committed",
    "canonical_ir_ready",
    "knowledge_version_ready",
    "security_denied",
    "credential_blocked",
    "object_stage_failed",
    "object_commit_failed",
    "canonicalization_failed",
    "reconciliation_required",
)


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"length({column_name}) = 64", name=constraint_name
    )


def upgrade() -> None:
    op.create_table(
        "canonical_ingestion_runs",
        sa.Column("run_id", sa.String(length=240), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("source_set_ref", sa.String(length=240), nullable=False),
        sa.Column("corpus_manifest_ref", sa.String(length=240), nullable=False),
        sa.Column("current_state", sa.String(length=64), nullable=False),
        sa.Column("state_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("knowledge_version_id", sa.String(length=240), nullable=True),
        sa.Column("last_error_code", sa.String(length=160), nullable=True),
        sa.Column("last_error_detail", sa.String(length=1024), nullable=True),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_canonical_ingestion_runs_idempotency"),
        sa.CheckConstraint(
            "current_state in ("
            + ", ".join(f"'{state}'" for state in _CANONICAL_RUN_STATES)
            + ")",
            name="ck_canonical_ingestion_runs_state",
        ),
        sa.CheckConstraint("state_version > 0", name="ck_canonical_ingestion_runs_state_version"),
        sa.CheckConstraint("attempt_number > 0", name="ck_canonical_ingestion_runs_attempt"),
        _hash_check("payload_hash", "ck_canonical_ingestion_runs_payload_hash"),
    )
    op.create_index(
        "ix_canonical_ingestion_runs_tenant_state",
        "canonical_ingestion_runs",
        ["tenant_id", "current_state", "updated_at"],
    )

    op.create_table(
        "canonical_ingestion_run_history",
        sa.Column("history_id", sa.String(length=240), primary_key=True),
        sa.Column("run_id", sa.String(length=240), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("from_state", sa.String(length=64), nullable=True),
        sa.Column("to_state", sa.String(length=64), nullable=False),
        sa.Column("state_version", sa.Integer(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=240), nullable=True),
        sa.Column("source_hash", sa.String(length=64), nullable=True),
        sa.Column("outbox_event_id", sa.String(length=240), nullable=True),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("transitioned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["canonical_ingestion_runs.run_id"], ondelete="CASCADE", name="fk_canonical_run_history_run"),
        sa.UniqueConstraint("run_id", "state_version", name="uq_canonical_run_history_version"),
        _hash_check("payload_hash", "ck_canonical_run_history_payload_hash"),
    )
    op.create_index(
        "ix_canonical_run_history_run",
        "canonical_ingestion_run_history",
        ["run_id", "state_version"],
    )


def downgrade() -> None:
    op.drop_table("canonical_ingestion_run_history")
    op.drop_table("canonical_ingestion_runs")
