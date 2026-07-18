"""add cutover generation and active snapshot guards

Revision ID: 20260718_13
Revises: 20260718_12
Create Date: 2026-07-18 13:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260718_13"
down_revision = "20260718_12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_cutover_targets",
        sa.Column("target_id", sa.String(length=160), primary_key=True),
        sa.Column("active_snapshot_id", sa.String(length=160), nullable=True),
        sa.Column("active_generation", sa.Integer(), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "active_generation > 0",
            name="ck_infra_cutover_targets_generation_positive",
        ),
    )

    op.create_table(
        "infra_cutover_snapshots",
        sa.Column("snapshot_id", sa.String(length=160), primary_key=True),
        sa.Column("target_id", sa.String(length=160), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("activated_generation", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_by", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["target_id"],
            ["infra_cutover_targets.target_id"],
            ondelete="CASCADE",
            name="fk_infra_cutover_snapshots_target",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_infra_cutover_snapshots_payload_hash",
        ),
        sa.CheckConstraint(
            "status in ('candidate','active','superseded','retired')",
            name="ck_infra_cutover_snapshots_status",
        ),
        sa.CheckConstraint(
            "activated_generation IS NULL OR activated_generation > 0",
            name="ck_infra_cutover_snapshots_generation_positive",
        ),
    )

    op.create_foreign_key(
        "fk_infra_cutover_targets_active_snapshot",
        "infra_cutover_targets",
        "infra_cutover_snapshots",
        ["active_snapshot_id"],
        ["snapshot_id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "infra_active_snapshot_refs",
        sa.Column("ref_id", sa.String(length=160), primary_key=True),
        sa.Column("target_id", sa.String(length=160), nullable=False),
        sa.Column("snapshot_id", sa.String(length=160), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["target_id"],
            ["infra_cutover_targets.target_id"],
            ondelete="CASCADE",
            name="fk_infra_active_snapshot_refs_target",
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["infra_cutover_snapshots.snapshot_id"],
            ondelete="CASCADE",
            name="fk_infra_active_snapshot_refs_snapshot",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_infra_active_snapshot_refs_generation_positive",
        ),
        sa.CheckConstraint(
            "status in ('active','released')",
            name="ck_infra_active_snapshot_refs_status",
        ),
    )
    op.create_index(
        "ix_infra_active_snapshot_refs_snapshot_active",
        "infra_active_snapshot_refs",
        ["target_id", "snapshot_id", "status"],
    )
    op.create_index(
        "ix_infra_cutover_snapshots_target_status",
        "infra_cutover_snapshots",
        ["target_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_infra_cutover_snapshots_target_status",
        table_name="infra_cutover_snapshots",
    )
    op.drop_index(
        "ix_infra_active_snapshot_refs_snapshot_active",
        table_name="infra_active_snapshot_refs",
    )
    op.drop_table("infra_active_snapshot_refs")
    op.drop_constraint(
        "fk_infra_cutover_targets_active_snapshot",
        "infra_cutover_targets",
        type_="foreignkey",
    )
    op.drop_table("infra_cutover_snapshots")
    op.drop_table("infra_cutover_targets")
