"""add product agent editor payload snapshots

Revision ID: 20260728_50
Revises: 20260728_49
Create Date: 2026-07-27 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260728_50"
down_revision = "20260728_49"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product_agent_drafts", sa.Column("draft_payload_json", sa.JSON(), nullable=True))
    op.add_column("product_agent_versions", sa.Column("configuration_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("product_agent_versions", "configuration_json")
    op.drop_column("product_agent_drafts", "draft_payload_json")
