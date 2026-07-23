"""add ingestion delete lifecycle audit table

Revision ID: 20260724_25
Revises: 20260724_24
Create Date: 2026-07-24 00:35:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260724_25"
down_revision = "20260724_24"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_delete_lifecycles",
        sa.Column("delete_ref", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("snapshot_ref", sa.String(length=240), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("visibility_ref", sa.String(length=240), nullable=False),
        sa.Column("indexable_snapshot_id", sa.String(length=160), nullable=True),
        sa.Column("handoff_outbox_event_id", sa.String(length=160), nullable=True),
        sa.Column("parse_job_id", sa.String(length=160), nullable=True),
        sa.Column("parse_attempt_id", sa.String(length=160), nullable=True),
        sa.Column("fencing_token", sa.Integer(), nullable=True),
        sa.Column("cleanup_ref", sa.String(length=240), nullable=True),
        sa.Column("projection_cleanup_ref", sa.String(length=240), nullable=True),
        sa.Column("physical_delete_ref", sa.String(length=240), nullable=True),
        sa.Column("verification_ref", sa.String(length=240), nullable=True),
        sa.Column("cleanup_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("physical_delete_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("legal_hold_ref", sa.String(length=240), nullable=True),
        sa.Column("restored_authorization", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("duplicate", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("late_worker_result_rejected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("receipt_hash", sa.String(length=64), nullable=False),
        sa.Column("history", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["indexable_snapshot_id"],
            ["ingestion_indexable_document_snapshots.indexable_snapshot_id"],
            ondelete="RESTRICT",
            name="fk_ingestion_delete_lifecycles_indexable_snapshot",
        ),
        sa.ForeignKeyConstraint(
            ["parse_job_id"],
            ["ingestion_parse_jobs.parse_job_id"],
            ondelete="RESTRICT",
            name="fk_ingestion_delete_lifecycles_parse_job",
        ),
        sa.ForeignKeyConstraint(
            ["parse_attempt_id"],
            ["ingestion_parse_attempts.parse_attempt_id"],
            ondelete="RESTRICT",
            name="fk_ingestion_delete_lifecycles_parse_attempt",
        ),
        sa.CheckConstraint("length(receipt_hash) = 64", name="ck_ingestion_delete_lifecycles_hash"),
        sa.CheckConstraint("fencing_token IS NULL OR fencing_token > 0", name="ck_ingestion_delete_lifecycles_fencing"),
        sa.CheckConstraint(
            "state in ('visibility_revoked','cleanup_requested','physically_deleted','verified','legal_hold','restored')",
            name="ck_ingestion_delete_lifecycles_state",
        ),
        sa.CheckConstraint(
            "state <> 'verified' OR (cleanup_verified = true AND physical_delete_verified = true)",
            name="ck_ingestion_delete_lifecycles_verified_requires_checks",
        ),
        sa.CheckConstraint(
            "legal_hold_ref IS NULL OR physical_delete_ref IS NULL",
            name="ck_ingestion_delete_lifecycles_legal_hold_no_physical_delete",
        ),
    )
    op.create_index(
        "ix_ingestion_delete_lifecycles_snapshot_ref",
        "ingestion_delete_lifecycles",
        ["snapshot_ref"],
    )
    op.create_index(
        "ix_ingestion_delete_lifecycles_parse_attempt",
        "ingestion_delete_lifecycles",
        ["parse_attempt_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_ingestion_delete_lifecycles_parse_attempt", table_name="ingestion_delete_lifecycles")
    op.drop_index("ix_ingestion_delete_lifecycles_snapshot_ref", table_name="ingestion_delete_lifecycles")
    op.drop_table("ingestion_delete_lifecycles")
