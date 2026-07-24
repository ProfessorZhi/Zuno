"""add review task binding refs

Revision ID: 20260724_31
Revises: 20260724_30
Create Date: 2026-07-24 03:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260724_31"
down_revision = "20260724_30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ingestion_review_tasks", sa.Column("reviewer_principal_id", sa.String(length=160), nullable=True))
    op.add_column("ingestion_review_tasks", sa.Column("security_decision_ref", sa.String(length=240), nullable=True))
    op.add_column("ingestion_review_tasks", sa.Column("idempotency_key", sa.String(length=240), nullable=True))
    op.add_column("ingestion_review_tasks", sa.Column("trace_id", sa.String(length=160), nullable=True))
    op.add_column("ingestion_review_tasks", sa.Column("audit_ref", sa.String(length=240), nullable=True))
    op.create_index(
        "ix_ingestion_review_tasks_trace",
        "ingestion_review_tasks",
        ["tenant_id", "trace_id"],
        postgresql_where=sa.text("trace_id IS NOT NULL"),
    )
    op.create_unique_constraint(
        "uq_ingestion_review_tasks_tenant_idempotency",
        "ingestion_review_tasks",
        ["tenant_id", "idempotency_key"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_ingestion_review_tasks_tenant_idempotency", "ingestion_review_tasks", type_="unique")
    op.drop_index("ix_ingestion_review_tasks_trace", table_name="ingestion_review_tasks")
    op.drop_column("ingestion_review_tasks", "audit_ref")
    op.drop_column("ingestion_review_tasks", "trace_id")
    op.drop_column("ingestion_review_tasks", "idempotency_key")
    op.drop_column("ingestion_review_tasks", "security_decision_ref")
    op.drop_column("ingestion_review_tasks", "reviewer_principal_id")
