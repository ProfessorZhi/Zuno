"""initialize postgresql schema

Revision ID: 20260417_01
Revises:
Create Date: 2026-04-17 03:30:00
"""

from alembic import op

from agentchat.database.metadata import metadata

revision = "20260417_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    metadata.drop_all(bind=bind)
