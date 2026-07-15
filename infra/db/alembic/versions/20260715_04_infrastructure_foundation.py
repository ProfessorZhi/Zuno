"""add infrastructure foundation primitives

Revision ID: 20260715_04
Revises: 20260417_01
Create Date: 2026-07-15 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260715_04"
down_revision = "20260417_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_outbox_events",
        sa.Column("event_id", sa.String(length=128), primary_key=True),
        sa.Column("aggregate_id", sa.String(length=128), nullable=False),
        sa.Column("topic", sa.String(length=160), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("claim_owner", sa.String(length=128), nullable=True),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "status in ('pending','claimed','published','quarantined','dead_letter')",
            name="ck_infra_outbox_events_status",
        ),
    )
    op.create_index("ix_infra_outbox_events_pending", "infra_outbox_events", ["status", "created_at"])
    op.create_index("ix_infra_outbox_events_idempotency_key", "infra_outbox_events", ["idempotency_key"])

    op.create_table(
        "infra_inbox_messages",
        sa.Column("consumer", sa.String(length=128), primary_key=True),
        sa.Column("message_id", sa.String(length=160), primary_key=True),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("conflict_hash", sa.String(length=64), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status in ('received','processed','quarantined')", name="ck_infra_inbox_messages_status"),
    )

    op.create_table(
        "infra_idempotency_claims",
        sa.Column("claim_id", postgresql.UUID(as_uuid=False), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("scope", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=160), nullable=False),
        sa.Column("owner", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("result_ref", sa.String(length=256), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("scope", "idempotency_key", name="uq_infra_idempotency_claims_scope_key"),
        sa.CheckConstraint("status in ('in_progress','completed','expired','conflict')", name="ck_infra_idempotency_claims_status"),
    )

    op.create_table(
        "infra_worker_leases",
        sa.Column("resource_id", sa.String(length=160), primary_key=True),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column("lease_id", sa.String(length=128), nullable=False),
        sa.Column("epoch", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "infra_object_manifests",
        sa.Column("object_ref", sa.String(length=256), primary_key=True),
        sa.Column("owner", sa.String(length=128), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("conflict_hash", sa.String(length=64), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("visibility", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("visibility in ('staged','visible','deleted','restored','quarantined')", name="ck_infra_object_manifests_visibility"),
    )

    op.create_table(
        "infra_checkpoints",
        sa.Column("checkpoint_id", sa.String(length=160), primary_key=True),
        sa.Column("thread_id", sa.String(length=160), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("owner", sa.String(length=128), nullable=False),
        sa.Column("state_hash", sa.String(length=64), nullable=False),
        sa.Column("state_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("thread_id", "generation", name="uq_infra_checkpoints_thread_generation"),
    )
    op.create_index("ix_infra_checkpoints_thread_generation", "infra_checkpoints", ["thread_id", "generation"])


def downgrade() -> None:
    op.drop_index("ix_infra_checkpoints_thread_generation", table_name="infra_checkpoints")
    op.drop_table("infra_checkpoints")
    op.drop_table("infra_object_manifests")
    op.drop_table("infra_worker_leases")
    op.drop_table("infra_idempotency_claims")
    op.drop_table("infra_inbox_messages")
    op.drop_index("ix_infra_outbox_events_idempotency_key", table_name="infra_outbox_events")
    op.drop_index("ix_infra_outbox_events_pending", table_name="infra_outbox_events")
    op.drop_table("infra_outbox_events")
