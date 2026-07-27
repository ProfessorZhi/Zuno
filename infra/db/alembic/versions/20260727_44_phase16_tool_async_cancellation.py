"""phase16 tool async cancellation persistence

Revision ID: 20260727_44
Revises: 20260727_43
Create Date: 2026-07-27 18:44:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260727_44"
down_revision = "20260727_43"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "tool_async_jobs",
        sa.Column("async_job_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("execution_receipt_id", sa.String(length=180), nullable=False),
        sa.Column("provider_job_id", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("callback_binding_ref", sa.String(length=180), nullable=False),
        sa.Column("callback_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_scope", sa.String(length=120), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("idempotency_generation", sa.Integer(), nullable=False),
        sa.Column("fencing_resource_id", sa.String(length=240), nullable=False),
        sa.Column("fencing_lease_id", sa.String(length=180), nullable=False),
        sa.Column("fencing_epoch", sa.Integer(), nullable=False),
        sa.Column("secret_lease_id", sa.String(length=180), nullable=True),
        sa.Column("job_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["prepared_tool_action_id"], ["prepared_tool_actions.prepared_tool_action_id"], name="fk_tool_async_jobs_prepared"),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_async_jobs_attempt"),
        sa.ForeignKeyConstraint(["execution_receipt_id"], ["tool_execution_receipts.receipt_id"], name="fk_tool_async_jobs_execution"),
        sa.UniqueConstraint("tenant_id", "provider_job_id", name="uq_tool_async_jobs_provider_job"),
        sa.UniqueConstraint("tenant_id", "idempotency_scope", "idempotency_key", name="uq_tool_async_jobs_idempotency"),
        sa.CheckConstraint("status in ('STARTED','WAITING_CALLBACK','COMPLETED','CANCEL_REQUESTED','CANCELLED','TIMEOUT','UNKNOWN')", name="ck_tool_async_jobs_status"),
        sa.CheckConstraint("callback_order >= 0", name="ck_tool_async_jobs_callback_order"),
        sa.CheckConstraint("idempotency_generation > 0", name="ck_tool_async_jobs_idem_generation"),
        sa.CheckConstraint("fencing_epoch > 0", name="ck_tool_async_jobs_fencing_epoch"),
        _hash_check("job_payload_hash", "ck_tool_async_jobs_payload_hash"),
    )
    op.create_table(
        "tool_async_callbacks",
        sa.Column("callback_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("async_job_id", sa.String(length=180), nullable=False),
        sa.Column("provider_job_id", sa.String(length=240), nullable=False),
        sa.Column("callback_order", sa.Integer(), nullable=False),
        sa.Column("authenticity_status", sa.String(length=40), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=False),
        sa.Column("callback_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["async_job_id"], ["tool_async_jobs.async_job_id"], name="fk_tool_async_callbacks_job"),
        sa.UniqueConstraint("tenant_id", "provider_job_id", "callback_order", name="uq_tool_async_callbacks_order"),
        sa.CheckConstraint("callback_order > 0", name="ck_tool_async_callbacks_order_positive"),
        sa.CheckConstraint("authenticity_status in ('VERIFIED','REPLAY','FORGED','OUT_OF_ORDER')", name="ck_tool_async_callbacks_authenticity"),
        _hash_check("callback_payload_hash", "ck_tool_async_callbacks_payload_hash"),
    )
    op.create_table(
        "tool_cancellation_receipts",
        sa.Column("cancellation_receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("prepared_tool_action_id", sa.String(length=180), nullable=False),
        sa.Column("attempt_id", sa.String(length=180), nullable=False),
        sa.Column("async_job_id", sa.String(length=180), nullable=True),
        sa.Column("provider_job_id", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("external_effect_revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requested_by_principal_id", sa.String(length=180), nullable=False),
        sa.Column("audit_requirement_id", sa.String(length=180), nullable=False),
        sa.Column("cancellation_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["prepared_tool_action_id"], ["prepared_tool_actions.prepared_tool_action_id"], name="fk_tool_cancellation_prepared"),
        sa.ForeignKeyConstraint(["attempt_id"], ["tool_attempts.attempt_id"], name="fk_tool_cancellation_attempt"),
        sa.ForeignKeyConstraint(["async_job_id"], ["tool_async_jobs.async_job_id"], name="fk_tool_cancellation_async_job"),
        sa.CheckConstraint("status in ('REQUESTED','ACKNOWLEDGED','FAILED','NOT_GUARANTEED')", name="ck_tool_cancellation_status"),
        _hash_check("cancellation_payload_hash", "ck_tool_cancellation_payload_hash"),
    )


def downgrade() -> None:
    op.drop_table("tool_cancellation_receipts")
    op.drop_table("tool_async_callbacks")
    op.drop_table("tool_async_jobs")
