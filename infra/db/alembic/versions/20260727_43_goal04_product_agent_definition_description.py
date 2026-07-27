"""add product agent definition description

Revision ID: 20260727_43
Revises: 20260727_42
Create Date: 2026-07-27 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260727_43"
down_revision = "20260727_42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "product_agent_definitions",
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
    )
    op.alter_column("product_agent_definitions", "description", server_default=None)


def downgrade() -> None:
    op.drop_column("product_agent_definitions", "description")
