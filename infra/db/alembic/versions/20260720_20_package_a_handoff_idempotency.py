"""add package a handoff idempotency keys

Revision ID: 20260720_20
Revises: 20260720_19
Create Date: 2026-07-20 20:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260720_20"
down_revision = "20260720_19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingestion_indexable_document_snapshots",
        sa.Column("handoff_idempotency_key", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "ingestion_outbox_events",
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
    )
    op.execute(
        """
        UPDATE ingestion_outbox_events
        SET idempotency_key = payload ->> 'idempotency_key'
        WHERE event_type = 'ingestion.indexable_snapshot.ready'
          AND idempotency_key IS NULL
          AND payload::jsonb ? 'idempotency_key'
        """
    )
    op.execute(
        """
        UPDATE ingestion_indexable_document_snapshots AS snapshot
        SET handoff_idempotency_key = outbox.idempotency_key
        FROM ingestion_outbox_events AS outbox
        WHERE outbox.aggregate_ref = snapshot.indexable_snapshot_id
          AND outbox.event_type = 'ingestion.indexable_snapshot.ready'
          AND outbox.idempotency_key IS NOT NULL
          AND snapshot.handoff_idempotency_key IS NULL
        """
    )
    op.create_index(
        "uq_ingestion_indexable_snapshots_tenant_handoff_idem",
        "ingestion_indexable_document_snapshots",
        ["tenant_id", "handoff_idempotency_key"],
        unique=True,
        postgresql_where=sa.text("handoff_idempotency_key IS NOT NULL"),
    )
    op.create_index(
        "uq_ingestion_outbox_events_tenant_event_idem",
        "ingestion_outbox_events",
        ["tenant_id", "event_type", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_ingestion_outbox_events_tenant_event_idem", table_name="ingestion_outbox_events")
    op.drop_index(
        "uq_ingestion_indexable_snapshots_tenant_handoff_idem",
        table_name="ingestion_indexable_document_snapshots",
    )
    op.drop_column("ingestion_outbox_events", "idempotency_key")
    op.drop_column("ingestion_indexable_document_snapshots", "handoff_idempotency_key")
