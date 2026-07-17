"""add durable migration backfill control

Revision ID: 20260717_08
Revises: 20260717_07
Create Date: 2026-07-17 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260717_08"
down_revision = "20260717_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_migration_backfills",
        sa.Column("backfill_id", sa.String(length=160), primary_key=True),
        sa.Column("module_owner", sa.String(length=128), nullable=False),
        sa.Column("source_ref", sa.String(length=512), nullable=False),
        sa.Column("target_ref", sa.String(length=512), nullable=False),
        sa.Column("transform_version", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column(
            "cursor",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("cursor_hash", sa.String(length=64), nullable=False),
        sa.Column("source_watermark", sa.String(length=256), nullable=True),
        sa.Column("processed_count", sa.BigInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("conflict_count", sa.BigInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("chunk_size", sa.Integer(), nullable=False),
        sa.Column("generation", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("lease_owner", sa.String(length=128), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_hash", sa.String(length=64), nullable=True),
        sa.Column("error_code", sa.String(length=128), nullable=True),
        sa.Column("forward_fix_of", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["forward_fix_of"],
            ["infra_migration_backfills.backfill_id"],
            name="fk_infra_migration_backfills_forward_fix_of",
        ),
        sa.CheckConstraint(
            "state in ('declared','running','paused','completed','failed','superseded')",
            name="ck_infra_migration_backfills_state",
        ),
        sa.CheckConstraint(
            "processed_count >= 0 AND conflict_count >= 0 AND chunk_size > 0 AND generation >= 0",
            name="ck_infra_migration_backfills_counts",
        ),
        sa.CheckConstraint(
            "(state = 'running') = (lease_owner IS NOT NULL AND lease_expires_at IS NOT NULL)",
            name="ck_infra_migration_backfills_lease_state",
        ),
        sa.CheckConstraint(
            "state <> 'completed' OR (verification_hash IS NOT NULL AND completed_at IS NOT NULL)",
            name="ck_infra_migration_backfills_completed_state",
        ),
    )
    op.create_index(
        "ix_infra_migration_backfills_state_lease",
        "infra_migration_backfills",
        ["state", "lease_expires_at"],
    )
    op.create_index(
        "ix_infra_migration_backfills_owner",
        "infra_migration_backfills",
        ["module_owner", "created_at"],
    )

    op.create_table(
        "infra_migration_backfill_chunks",
        sa.Column("backfill_id", sa.String(length=160), nullable=False),
        sa.Column("chunk_id", sa.String(length=160), nullable=False),
        sa.Column("start_cursor", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("end_cursor", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("start_cursor_hash", sa.String(length=64), nullable=False),
        sa.Column("end_cursor_hash", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("source_watermark", sa.String(length=256), nullable=True),
        sa.Column("row_count", sa.BigInteger(), nullable=False),
        sa.Column("applied_generation", sa.Integer(), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["backfill_id"],
            ["infra_migration_backfills.backfill_id"],
            name="fk_infra_migration_backfill_chunks_backfill",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "backfill_id",
            "chunk_id",
            name="pk_infra_migration_backfill_chunks",
        ),
        sa.CheckConstraint(
            "row_count >= 0 AND applied_generation > 0",
            name="ck_infra_migration_backfill_chunks_counts",
        ),
    )
    op.create_index(
        "ix_infra_migration_backfill_chunks_applied",
        "infra_migration_backfill_chunks",
        ["backfill_id", "applied_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_infra_migration_backfill_chunks_applied",
        table_name="infra_migration_backfill_chunks",
    )
    op.drop_table("infra_migration_backfill_chunks")
    op.drop_index("ix_infra_migration_backfills_owner", table_name="infra_migration_backfills")
    op.drop_index(
        "ix_infra_migration_backfills_state_lease",
        table_name="infra_migration_backfills",
    )
    op.drop_table("infra_migration_backfills")
