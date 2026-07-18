"""add mandatory audit durability primitives

Revision ID: 20260718_12
Revises: 20260718_11
Create Date: 2026-07-18 12:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260718_12"
down_revision = "20260718_11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_audit_channels",
        sa.Column("channel_id", sa.String(length=160), primary_key=True),
        sa.Column("capacity_limit", sa.Integer(), nullable=False),
        sa.Column("fail_mode", sa.String(length=32), nullable=False),
        sa.Column("drained", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "capacity_limit > 0",
            name="ck_infra_audit_channels_limit_positive",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_infra_audit_channels_generation_positive",
        ),
        sa.CheckConstraint(
            "fail_mode in ('fail_closed')",
            name="ck_infra_audit_channels_fail_mode",
        ),
    )

    op.create_table(
        "infra_mandatory_audit_events",
        sa.Column("audit_id", sa.String(length=160), primary_key=True),
        sa.Column("channel_id", sa.String(length=160), nullable=False),
        sa.Column("effect_id", sa.String(length=160), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("effect_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["infra_audit_channels.channel_id"],
            ondelete="CASCADE",
            name="fk_infra_mandatory_audit_events_channel",
        ),
        sa.UniqueConstraint(
            "effect_id",
            name="uq_infra_mandatory_audit_events_effect",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_infra_mandatory_audit_events_generation_positive",
        ),
        sa.CheckConstraint(
            "status in ('durable','effect_observed')",
            name="ck_infra_mandatory_audit_events_status",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_infra_mandatory_audit_events_payload_hash",
        ),
    )
    op.create_index(
        "ix_infra_mandatory_audit_events_channel_status",
        "infra_mandatory_audit_events",
        ["channel_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_infra_mandatory_audit_events_channel_status",
        table_name="infra_mandatory_audit_events",
    )
    op.drop_table("infra_mandatory_audit_events")
    op.drop_table("infra_audit_channels")
