"""add physical delete refs to ingestion lifecycle

Revision ID: 20260724_28
Revises: 20260724_27
Create Date: 2026-07-24 00:30:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260724_28"
down_revision = "20260724_27"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ingestion_delete_lifecycles", sa.Column("object_ref", sa.String(length=1024), nullable=True))
    op.add_column(
        "ingestion_delete_lifecycles",
        sa.Column("restore_point_name", sa.String(length=1024), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ingestion_delete_lifecycles", "restore_point_name")
    op.drop_column("ingestion_delete_lifecycles", "object_ref")
