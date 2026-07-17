"""add the workspace session owner index without blocking writes

Revision ID: 20260717_09
Revises: 20260717_08
Create Date: 2026-07-17 09:00:00
"""

from alembic import op

revision = "20260717_09"
down_revision = "20260717_08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
                ix_workspace_session_user_update_time
            ON workspace_session (user_id, update_time DESC)
            """)


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            "DROP INDEX CONCURRENTLY IF EXISTS ix_workspace_session_user_update_time"
        )
