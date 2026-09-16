"""add product security decision scope and expiry

Revision ID: 20260916_58
Revises: 20260813_57
Create Date: 2026-09-16 16:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260916_58"
down_revision = "20260813_57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "security_principal_contexts",
        sa.Column("workspace_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "security_authorization_decisions",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("security_authorization_decisions", "expires_at")
    op.drop_column("security_principal_contexts", "workspace_id")
