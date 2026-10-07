"""add mandatory audit dispatch-aborted lifecycle

Revision ID: 20260920_60
Revises: 20260918_59
Create Date: 2026-09-20 09:45:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260920_60"
down_revision = "20260918_59"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infra_mandatory_audit_events",
        sa.Column("dispatch_aborted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.drop_constraint(
        "ck_infra_mandatory_audit_events_status",
        "infra_mandatory_audit_events",
        type_="check",
    )
    op.create_check_constraint(
        "ck_infra_mandatory_audit_events_status",
        "infra_mandatory_audit_events",
        "status in ('durable','effect_observed','dispatch_aborted')",
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE infra_mandatory_audit_events
        SET status = 'durable',
            dispatch_aborted_at = NULL
        WHERE status = 'dispatch_aborted'
        """
    )
    op.drop_constraint(
        "ck_infra_mandatory_audit_events_status",
        "infra_mandatory_audit_events",
        type_="check",
    )
    op.create_check_constraint(
        "ck_infra_mandatory_audit_events_status",
        "infra_mandatory_audit_events",
        "status in ('durable','effect_observed')",
    )
    op.drop_column("infra_mandatory_audit_events", "dispatch_aborted_at")
