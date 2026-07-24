"""add restore authorization ref to ingestion delete lifecycle

Revision ID: 20260724_29
Revises: 20260724_28
Create Date: 2026-07-24 01:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260724_29"
down_revision = "20260724_28"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingestion_delete_lifecycles",
        sa.Column("restore_authorization_ref", sa.String(length=240), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ingestion_delete_lifecycles", "restore_authorization_ref")
