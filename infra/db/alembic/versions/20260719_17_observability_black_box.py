"""add observability durable black box facts

Revision ID: 20260719_17
Revises: 20260719_16
Create Date: 2026-07-19 17:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260719_17"
down_revision = "20260719_16"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "observability_ingest_envelopes",
        sa.Column("envelope_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("trace_id", sa.String(length=160), nullable=False),
        sa.Column("schema_ref", sa.String(length=160), nullable=False),
        sa.Column("schema_version", sa.String(length=80), nullable=False),
        sa.Column("producer", sa.String(length=160), nullable=False),
        sa.Column("scope_ref", sa.String(length=240), nullable=False),
        sa.Column("effective_security_epoch_ref", sa.String(length=160), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("redaction_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("quarantine_reason", sa.String(length=160), nullable=True),
        sa.Column(
            "accepted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "schema_ref",
            "payload_hash",
            name="uq_observability_ingest_envelopes_dedup",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_observability_ingest_envelopes_payload_hash",
        ),
        sa.CheckConstraint(
            "length(redaction_hash) = 64",
            name="ck_observability_ingest_envelopes_redaction_hash",
        ),
        sa.CheckConstraint(
            "status in ('accepted','duplicate','quarantined','dead_letter')",
            name="ck_observability_ingest_envelopes_status",
        ),
    )

    op.create_table(
        "observability_traces",
        sa.Column("trace_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("root_run_id", sa.String(length=160), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=48), nullable=False),
        sa.Column("terminal", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("trace_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "length(trace_hash) = 64",
            name="ck_observability_traces_trace_hash",
        ),
        sa.CheckConstraint(
            "lifecycle_state in ('prepared','runtime_observed','measured','blocked','quality_proven')",
            name="ck_observability_traces_lifecycle_state",
        ),
    )

    op.create_table(
        "observability_spans",
        sa.Column("span_id", sa.String(length=160), primary_key=True),
        sa.Column("trace_id", sa.String(length=160), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parent_span_id", sa.String(length=160), nullable=True),
        sa.Column("causation_id", sa.String(length=160), nullable=True),
        sa.Column("span_kind", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("span_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["trace_id"],
            ["observability_traces.trace_id"],
            ondelete="RESTRICT",
            name="fk_observability_spans_trace",
        ),
        sa.CheckConstraint(
            "length(span_hash) = 64",
            name="ck_observability_spans_span_hash",
        ),
        sa.CheckConstraint(
            "status in ('open','completed','failed','late_revision')",
            name="ck_observability_spans_status",
        ),
    )

    op.create_table(
        "observability_runtime_events",
        sa.Column("event_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("trace_id", sa.String(length=160), nullable=False),
        sa.Column("span_id", sa.String(length=160), nullable=True),
        sa.Column("stream_id", sa.String(length=160), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("redacted_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "accepted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["trace_id"],
            ["observability_traces.trace_id"],
            ondelete="RESTRICT",
            name="fk_observability_runtime_events_trace",
        ),
        sa.ForeignKeyConstraint(
            ["span_id"],
            ["observability_spans.span_id"],
            ondelete="SET NULL",
            name="fk_observability_runtime_events_span",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "stream_id",
            "sequence",
            name="uq_observability_runtime_events_stream_sequence",
        ),
        sa.CheckConstraint(
            "sequence > 0",
            name="ck_observability_runtime_events_sequence",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_observability_runtime_events_payload_hash",
        ),
        sa.CheckConstraint(
            "status in ('accepted','duplicate','quarantined','late')",
            name="ck_observability_runtime_events_status",
        ),
    )

    op.create_table(
        "observability_audit_records",
        sa.Column("audit_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("trace_id", sa.String(length=160), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("previous_hash", sa.String(length=64), nullable=False),
        sa.Column("audit_hash", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("redacted_payload", sa.JSON(), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "accepted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["trace_id"],
            ["observability_traces.trace_id"],
            ondelete="RESTRICT",
            name="fk_observability_audit_records_trace",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "trace_id",
            "sequence",
            name="uq_observability_audit_records_sequence",
        ),
        sa.CheckConstraint(
            "sequence > 0",
            name="ck_observability_audit_records_sequence",
        ),
        sa.CheckConstraint(
            "length(previous_hash) = 64",
            name="ck_observability_audit_records_previous_hash",
        ),
        sa.CheckConstraint(
            "length(audit_hash) = 64",
            name="ck_observability_audit_records_audit_hash",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_observability_audit_records_payload_hash",
        ),
    )

    op.create_table(
        "observability_projection_watermarks",
        sa.Column("watermark_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("projection_id", sa.String(length=160), nullable=False),
        sa.Column("stream_id", sa.String(length=160), nullable=False),
        sa.Column("contiguous_sequence", sa.Integer(), nullable=False),
        sa.Column("max_seen_sequence", sa.Integer(), nullable=False),
        sa.Column("freshness_status", sa.String(length=32), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "projection_id",
            "stream_id",
            name="uq_observability_projection_watermarks_stream",
        ),
        sa.CheckConstraint(
            "contiguous_sequence >= 0",
            name="ck_observability_projection_watermarks_contiguous",
        ),
        sa.CheckConstraint(
            "max_seen_sequence >= contiguous_sequence",
            name="ck_observability_projection_watermarks_max_seen",
        ),
        sa.CheckConstraint(
            "freshness_status in ('fresh','stale','gap','rebuilding')",
            name="ck_observability_projection_watermarks_freshness",
        ),
    )

    op.create_table(
        "observability_gaps",
        sa.Column("gap_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("stream_id", sa.String(length=160), nullable=False),
        sa.Column("missing_after_sequence", sa.Integer(), nullable=False),
        sa.Column("missing_before_sequence", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "missing_before_sequence > missing_after_sequence",
            name="ck_observability_gaps_range",
        ),
        sa.CheckConstraint(
            "status in ('open','filled','dead_lettered')",
            name="ck_observability_gaps_status",
        ),
    )

    op.create_table(
        "observability_dead_letters",
        sa.Column("dead_letter_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("source_ref", sa.String(length=240), nullable=False),
        sa.Column("reason_code", sa.String(length=160), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("redacted_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_observability_dead_letters_payload_hash",
        ),
        sa.CheckConstraint(
            "status in ('open','replayed','ignored')",
            name="ck_observability_dead_letters_status",
        ),
    )

    op.create_table(
        "observability_projection_rebuilds",
        sa.Column("rebuild_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("projection_id", sa.String(length=160), nullable=False),
        sa.Column("claim_owner", sa.String(length=160), nullable=False),
        sa.Column("fencing_token", sa.String(length=160), nullable=False),
        sa.Column("replay_from_sequence", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "replay_from_sequence >= 0",
            name="ck_observability_projection_rebuilds_replay_from",
        ),
        sa.CheckConstraint(
            "status in ('claimed','running','completed','failed','stale_rejected')",
            name="ck_observability_projection_rebuilds_status",
        ),
    )

    op.create_index(
        "ix_observability_ingest_envelopes_trace_status",
        "observability_ingest_envelopes",
        ["tenant_id", "trace_id", "status"],
    )
    op.create_index(
        "ix_observability_runtime_events_stream",
        "observability_runtime_events",
        ["tenant_id", "stream_id", "sequence"],
    )
    op.create_index(
        "ix_observability_audit_records_trace_sequence",
        "observability_audit_records",
        ["tenant_id", "trace_id", "sequence"],
    )
    op.create_index(
        "ix_observability_gaps_stream_status",
        "observability_gaps",
        ["tenant_id", "stream_id", "status"],
    )
    op.create_index(
        "ix_observability_dead_letters_status",
        "observability_dead_letters",
        ["tenant_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_observability_dead_letters_status",
        table_name="observability_dead_letters",
    )
    op.drop_index(
        "ix_observability_gaps_stream_status",
        table_name="observability_gaps",
    )
    op.drop_index(
        "ix_observability_audit_records_trace_sequence",
        table_name="observability_audit_records",
    )
    op.drop_index(
        "ix_observability_runtime_events_stream",
        table_name="observability_runtime_events",
    )
    op.drop_index(
        "ix_observability_ingest_envelopes_trace_status",
        table_name="observability_ingest_envelopes",
    )
    op.drop_table("observability_projection_rebuilds")
    op.drop_table("observability_dead_letters")
    op.drop_table("observability_gaps")
    op.drop_table("observability_projection_watermarks")
    op.drop_table("observability_audit_records")
    op.drop_table("observability_runtime_events")
    op.drop_table("observability_spans")
    op.drop_table("observability_traces")
    op.drop_table("observability_ingest_envelopes")
