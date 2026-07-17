"""add durable outbox delivery policy

Revision ID: 20260717_07
Revises: 20260717_06
Create Date: 2026-07-17 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260717_07"
down_revision = "20260717_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infra_outbox_events",
        sa.Column("publish_attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "infra_outbox_events",
        sa.Column("retry_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "infra_outbox_events",
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column("infra_outbox_events", sa.Column("last_error_code", sa.String(length=128), nullable=True))
    op.add_column("infra_outbox_events", sa.Column("last_failed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("infra_outbox_events", sa.Column("dead_lettered_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "infra_outbox_events",
        sa.Column("replay_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column("infra_outbox_events", sa.Column("last_replay_owner", sa.String(length=128), nullable=True))
    op.add_column("infra_outbox_events", sa.Column("replayed_at", sa.DateTime(timezone=True), nullable=True))

    op.execute(
        """
        UPDATE infra_outbox_events
        SET claim_owner = NULL,
            claimed_at = NULL
        WHERE status <> 'claimed'
        """
    )
    op.execute(
        """
        UPDATE infra_outbox_events
        SET status = 'pending',
            claim_owner = NULL,
            claimed_at = NULL
        WHERE status = 'claimed'
          AND (claim_owner IS NULL OR claimed_at IS NULL)
        """
    )
    op.execute(
        """
        UPDATE infra_outbox_events
        SET dead_lettered_at = COALESCE(published_at, created_at)
        WHERE status = 'dead_letter'
        """
    )

    op.create_check_constraint(
        "ck_infra_outbox_events_delivery_counts",
        "infra_outbox_events",
        "publish_attempts >= 0 AND retry_count >= 0 AND replay_count >= 0",
    )
    op.create_check_constraint(
        "ck_infra_outbox_events_claim_state",
        "infra_outbox_events",
        "(status = 'claimed') = (claim_owner IS NOT NULL AND claimed_at IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_infra_outbox_events_dead_letter_state",
        "infra_outbox_events",
        "(status = 'dead_letter') = (dead_lettered_at IS NOT NULL)",
    )
    op.create_index(
        "ix_infra_outbox_events_delivery_ready",
        "infra_outbox_events",
        ["status", "next_attempt_at", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_infra_outbox_events_delivery_ready", table_name="infra_outbox_events")
    op.drop_constraint(
        "ck_infra_outbox_events_dead_letter_state",
        "infra_outbox_events",
        type_="check",
    )
    op.drop_constraint(
        "ck_infra_outbox_events_claim_state",
        "infra_outbox_events",
        type_="check",
    )
    op.drop_constraint(
        "ck_infra_outbox_events_delivery_counts",
        "infra_outbox_events",
        type_="check",
    )
    op.drop_column("infra_outbox_events", "replayed_at")
    op.drop_column("infra_outbox_events", "last_replay_owner")
    op.drop_column("infra_outbox_events", "replay_count")
    op.drop_column("infra_outbox_events", "dead_lettered_at")
    op.drop_column("infra_outbox_events", "last_failed_at")
    op.drop_column("infra_outbox_events", "last_error_code")
    op.drop_column("infra_outbox_events", "next_attempt_at")
    op.drop_column("infra_outbox_events", "retry_count")
    op.drop_column("infra_outbox_events", "publish_attempts")
