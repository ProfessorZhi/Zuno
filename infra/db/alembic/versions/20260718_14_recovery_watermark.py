"""add recovery watermark and recovery set primitives

Revision ID: 20260718_14
Revises: 20260718_13
Create Date: 2026-07-18 14:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260718_14"
down_revision = "20260718_13"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_recovery_watermarks",
        sa.Column("component_id", sa.String(length=160), primary_key=True),
        sa.Column("service_kind", sa.String(length=64), nullable=False),
        sa.Column("authority", sa.String(length=32), nullable=False),
        sa.Column("watermark", sa.String(length=160), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "authority in ('authoritative','derived')",
            name="ck_infra_recovery_watermarks_authority",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_infra_recovery_watermarks_payload_hash",
        ),
    )

    op.create_table(
        "infra_recovery_sets",
        sa.Column("recovery_set_id", sa.String(length=160), primary_key=True),
        sa.Column("recovery_point", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("verification_hash", sa.String(length=64), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status in ('verified')",
            name="ck_infra_recovery_sets_status",
        ),
        sa.CheckConstraint(
            "length(verification_hash) = 64",
            name="ck_infra_recovery_sets_verification_hash",
        ),
    )

    op.create_table(
        "infra_recovery_set_members",
        sa.Column("recovery_set_id", sa.String(length=160), nullable=False),
        sa.Column("component_id", sa.String(length=160), nullable=False),
        sa.Column("service_kind", sa.String(length=64), nullable=False),
        sa.Column("authority", sa.String(length=32), nullable=False),
        sa.Column("watermark", sa.String(length=160), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["recovery_set_id"],
            ["infra_recovery_sets.recovery_set_id"],
            ondelete="CASCADE",
            name="fk_infra_recovery_set_members_set",
        ),
        sa.ForeignKeyConstraint(
            ["component_id"],
            ["infra_recovery_watermarks.component_id"],
            ondelete="RESTRICT",
            name="fk_infra_recovery_set_members_watermark",
        ),
        sa.PrimaryKeyConstraint(
            "recovery_set_id",
            "component_id",
            name="pk_infra_recovery_set_members",
        ),
        sa.CheckConstraint(
            "authority in ('authoritative','derived')",
            name="ck_infra_recovery_set_members_authority",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_infra_recovery_set_members_payload_hash",
        ),
    )
    op.create_index(
        "ix_infra_recovery_watermarks_kind_watermark",
        "infra_recovery_watermarks",
        ["service_kind", "watermark"],
    )
    op.create_index(
        "ix_infra_recovery_sets_recovery_point",
        "infra_recovery_sets",
        ["recovery_point"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_infra_recovery_sets_recovery_point",
        table_name="infra_recovery_sets",
    )
    op.drop_index(
        "ix_infra_recovery_watermarks_kind_watermark",
        table_name="infra_recovery_watermarks",
    )
    op.drop_table("infra_recovery_set_members")
    op.drop_table("infra_recovery_sets")
    op.drop_table("infra_recovery_watermarks")
