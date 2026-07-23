"""add ingestion human review task and decision audit tables

Revision ID: 20260724_24
Revises: 20260723_23
Create Date: 2026-07-24 00:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260724_24"
down_revision = "20260723_23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_review_tasks",
        sa.Column("review_task_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parse_snapshot_id", sa.String(length=160), nullable=False),
        sa.Column("quality_decision_id", sa.String(length=160), nullable=False),
        sa.Column("document_version_id", sa.String(length=160), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("reviewer_scope", sa.String(length=128), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["parse_snapshot_id"],
            ["ingestion_parse_snapshots.parse_snapshot_id"],
            ondelete="RESTRICT",
            name="fk_ingestion_review_tasks_snapshot",
        ),
        sa.ForeignKeyConstraint(
            ["quality_decision_id"],
            ["ingestion_quality_gate_decisions.quality_decision_id"],
            ondelete="RESTRICT",
            name="fk_ingestion_review_tasks_quality",
        ),
        sa.ForeignKeyConstraint(
            ["document_version_id"],
            ["ingestion_document_versions.document_version_id"],
            ondelete="RESTRICT",
            name="fk_ingestion_review_tasks_document_version",
        ),
        sa.UniqueConstraint("quality_decision_id", name="uq_ingestion_review_tasks_quality"),
        sa.CheckConstraint("length(decision_hash) = 64", name="ck_ingestion_review_tasks_hash"),
        sa.CheckConstraint(
            "status in ('pending','approved','rejected','expired','cancelled')",
            name="ck_ingestion_review_tasks_status",
        ),
    )

    op.create_table(
        "ingestion_review_decision_receipts",
        sa.Column("decision_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("review_task_id", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reviewer_id", sa.String(length=160), nullable=False),
        sa.Column("reviewer_scope", sa.String(length=128), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=240), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["review_task_id"],
            ["ingestion_review_tasks.review_task_id"],
            ondelete="RESTRICT",
            name="fk_ingestion_review_decision_receipts_task",
        ),
        sa.UniqueConstraint("review_task_id", name="uq_ingestion_review_decision_receipts_task"),
        sa.CheckConstraint("length(decision_hash) = 64", name="ck_ingestion_review_decision_receipts_hash"),
        sa.CheckConstraint(
            "status in ('approved','rejected','expired','cancelled')",
            name="ck_ingestion_review_decision_receipts_status",
        ),
    )

    op.create_index(
        "ix_ingestion_review_tasks_snapshot",
        "ingestion_review_tasks",
        ["parse_snapshot_id"],
    )
    op.create_index(
        "ix_ingestion_review_decision_receipts_task",
        "ingestion_review_decision_receipts",
        ["review_task_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_ingestion_review_decision_receipts_task", table_name="ingestion_review_decision_receipts")
    op.drop_index("ix_ingestion_review_tasks_snapshot", table_name="ingestion_review_tasks")
    op.drop_table("ingestion_review_decision_receipts")
    op.drop_table("ingestion_review_tasks")
