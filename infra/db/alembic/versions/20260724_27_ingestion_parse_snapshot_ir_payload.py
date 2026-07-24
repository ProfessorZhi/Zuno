"""store canonical parse IR for approved resume

Revision ID: 20260724_27
Revises: 20260724_26
Create Date: 2026-07-24 00:20:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260724_27"
down_revision = "20260724_26"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingestion_parse_snapshots",
        sa.Column("canonical_ir_json", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ingestion_parse_snapshots", "canonical_ir_json")
