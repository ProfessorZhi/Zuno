"""validate non-empty backfill owners with the online constraint pattern

Revision ID: 20260717_10
Revises: 20260717_09
Create Date: 2026-07-17 10:00:00
"""

from alembic import op

revision = "20260717_10"
down_revision = "20260717_09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE infra_migration_backfills
        ADD CONSTRAINT ck_infra_migration_backfills_owner_nonempty
        CHECK (length(btrim(module_owner)) > 0) NOT VALID
        """)
    op.execute("""
        ALTER TABLE infra_migration_backfills
        VALIDATE CONSTRAINT ck_infra_migration_backfills_owner_nonempty
        """)


def downgrade() -> None:
    op.drop_constraint(
        "ck_infra_migration_backfills_owner_nonempty",
        "infra_migration_backfills",
        type_="check",
    )
