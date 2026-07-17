"""add tenant-scoped delivery ordering and watermarks

Revision ID: 20260717_06
Revises: 20260716_05
Create Date: 2026-07-17 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260717_06"
down_revision = "20260716_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_outbox_sequences",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("ordering_key", sa.String(length=160), nullable=False),
        sa.Column("last_sequence", sa.BigInteger(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "tenant_id",
            "ordering_key",
            name="pk_infra_outbox_sequences",
        ),
        sa.CheckConstraint(
            "last_sequence > 0",
            name="ck_infra_outbox_sequences_positive",
        ),
    )

    op.add_column(
        "infra_outbox_events",
        sa.Column("tenant_id", sa.String(length=128), server_default="", nullable=False),
    )
    op.add_column(
        "infra_outbox_events",
        sa.Column("ordering_key", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "infra_outbox_events",
        sa.Column("ordering_sequence", sa.BigInteger(), nullable=True),
    )
    op.create_check_constraint(
        "ck_infra_outbox_events_ordering_pair",
        "infra_outbox_events",
        "(ordering_key IS NULL AND ordering_sequence IS NULL) OR "
        "(ordering_key IS NOT NULL AND ordering_sequence > 0)",
    )
    op.create_unique_constraint(
        "uq_infra_outbox_events_tenant_ordering_sequence",
        "infra_outbox_events",
        ["tenant_id", "ordering_key", "ordering_sequence"],
    )
    op.create_index(
        "ix_infra_outbox_events_tenant_ordering",
        "infra_outbox_events",
        ["tenant_id", "ordering_key", "ordering_sequence"],
    )
    op.alter_column("infra_outbox_events", "tenant_id", server_default=None)

    op.add_column(
        "infra_inbox_messages",
        sa.Column("tenant_id", sa.String(length=128), server_default="", nullable=False),
    )
    op.add_column(
        "infra_inbox_messages",
        sa.Column("ordering_key", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "infra_inbox_messages",
        sa.Column("ordering_sequence", sa.BigInteger(), nullable=True),
    )
    op.drop_constraint(
        "ck_infra_inbox_messages_status",
        "infra_inbox_messages",
        type_="check",
    )
    op.execute(
        "UPDATE infra_inbox_messages SET status = 'quarantined' WHERE status = 'buffered'"
    )
    op.create_check_constraint(
        "ck_infra_inbox_messages_status",
        "infra_inbox_messages",
        "status in ('buffered','received','processed','quarantined')",
    )
    op.create_check_constraint(
        "ck_infra_inbox_messages_ordering_pair",
        "infra_inbox_messages",
        "(ordering_key IS NULL AND ordering_sequence IS NULL) OR "
        "(ordering_key IS NOT NULL AND ordering_sequence > 0)",
    )
    op.create_unique_constraint(
        "uq_infra_inbox_messages_tenant_consumer_ordering_sequence",
        "infra_inbox_messages",
        ["tenant_id", "consumer", "ordering_key", "ordering_sequence"],
    )
    op.create_index(
        "ix_infra_inbox_messages_buffered",
        "infra_inbox_messages",
        ["tenant_id", "consumer", "ordering_key", "status", "ordering_sequence"],
    )
    op.alter_column("infra_inbox_messages", "tenant_id", server_default=None)

    op.create_table(
        "infra_delivery_watermarks",
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("consumer", sa.String(length=128), nullable=False),
        sa.Column("ordering_key", sa.String(length=160), nullable=False),
        sa.Column("contiguous_sequence", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("max_seen_sequence", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "tenant_id",
            "consumer",
            "ordering_key",
            name="pk_infra_delivery_watermarks",
        ),
        sa.CheckConstraint(
            "contiguous_sequence >= 0 AND max_seen_sequence >= contiguous_sequence",
            name="ck_infra_delivery_watermarks_sequence",
        ),
    )


def downgrade() -> None:
    op.drop_table("infra_delivery_watermarks")

    op.drop_index("ix_infra_inbox_messages_buffered", table_name="infra_inbox_messages")
    op.drop_constraint(
        "uq_infra_inbox_messages_tenant_consumer_ordering_sequence",
        "infra_inbox_messages",
        type_="unique",
    )
    op.drop_constraint(
        "ck_infra_inbox_messages_ordering_pair",
        "infra_inbox_messages",
        type_="check",
    )
    op.drop_constraint(
        "ck_infra_inbox_messages_status",
        "infra_inbox_messages",
        type_="check",
    )
    op.create_check_constraint(
        "ck_infra_inbox_messages_status",
        "infra_inbox_messages",
        "status in ('received','processed','quarantined')",
    )
    op.drop_column("infra_inbox_messages", "ordering_sequence")
    op.drop_column("infra_inbox_messages", "ordering_key")
    op.drop_column("infra_inbox_messages", "tenant_id")

    op.drop_index("ix_infra_outbox_events_tenant_ordering", table_name="infra_outbox_events")
    op.drop_constraint(
        "uq_infra_outbox_events_tenant_ordering_sequence",
        "infra_outbox_events",
        type_="unique",
    )
    op.drop_constraint(
        "ck_infra_outbox_events_ordering_pair",
        "infra_outbox_events",
        type_="check",
    )
    op.drop_column("infra_outbox_events", "ordering_sequence")
    op.drop_column("infra_outbox_events", "ordering_key")
    op.drop_column("infra_outbox_events", "tenant_id")

    op.drop_table("infra_outbox_sequences")
