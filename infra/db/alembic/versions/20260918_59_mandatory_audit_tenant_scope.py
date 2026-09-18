"""scope mandatory audit storage by tenant

Revision ID: 20260918_59
Revises: 20260916_58
Create Date: 2026-09-18 10:15:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260918_59"
down_revision = "20260916_58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infra_audit_channels",
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "infra_mandatory_audit_events",
        sa.Column("tenant_id", sa.String(length=128), nullable=True),
    )

    op.execute(
        """
        UPDATE infra_mandatory_audit_events
        SET tenant_id = COALESCE(NULLIF(payload->>'tenant_id', ''), 'legacy-unscoped')
        WHERE tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE infra_audit_channels AS channel
        SET tenant_id = COALESCE(
            (
                SELECT CASE
                    WHEN COUNT(DISTINCT event.tenant_id) = 1
                    THEN MIN(event.tenant_id)
                    ELSE NULL
                END
                FROM infra_mandatory_audit_events AS event
                WHERE event.channel_id = channel.channel_id
            ),
            'legacy-unscoped'
        )
        WHERE channel.tenant_id IS NULL
        """
    )

    op.alter_column(
        "infra_audit_channels",
        "tenant_id",
        existing_type=sa.String(length=128),
        nullable=False,
    )
    op.alter_column(
        "infra_mandatory_audit_events",
        "tenant_id",
        existing_type=sa.String(length=128),
        nullable=False,
    )
    op.create_check_constraint(
        "ck_infra_audit_channels_tenant_nonempty",
        "infra_audit_channels",
        "char_length(tenant_id) > 0",
    )
    op.create_check_constraint(
        "ck_infra_mandatory_audit_events_tenant_nonempty",
        "infra_mandatory_audit_events",
        "char_length(tenant_id) > 0",
    )
    op.create_index(
        "ix_infra_audit_channels_tenant_channel",
        "infra_audit_channels",
        ["tenant_id", "channel_id"],
    )
    op.create_index(
        "ix_infra_mandatory_audit_events_tenant_channel_status",
        "infra_mandatory_audit_events",
        ["tenant_id", "channel_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_infra_mandatory_audit_events_tenant_channel_status",
        table_name="infra_mandatory_audit_events",
    )
    op.drop_index(
        "ix_infra_audit_channels_tenant_channel",
        table_name="infra_audit_channels",
    )
    op.drop_constraint(
        "ck_infra_mandatory_audit_events_tenant_nonempty",
        "infra_mandatory_audit_events",
        type_="check",
    )
    op.drop_constraint(
        "ck_infra_audit_channels_tenant_nonempty",
        "infra_audit_channels",
        type_="check",
    )
    op.drop_column("infra_mandatory_audit_events", "tenant_id")
    op.drop_column("infra_audit_channels", "tenant_id")
