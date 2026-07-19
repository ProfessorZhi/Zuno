"""add durable ingestion source lineage facts

Revision ID: 20260719_18
Revises: 20260719_17
Create Date: 2026-07-19 18:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260719_18"
down_revision = "20260719_17"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingestion_source_objects",
        sa.Column("source_object_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("source_kind", sa.String(length=48), nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("mime_type", sa.String(length=160), nullable=False),
        sa.Column("declared_format", sa.String(length=64), nullable=False),
        sa.Column("storage_uri", sa.String(length=1024), nullable=False),
        sa.Column("object_manifest_ref", sa.String(length=240), nullable=False),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("classification_ref", sa.String(length=240), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "source_sha256", name="uq_ingestion_source_objects_content"),
        sa.CheckConstraint("length(source_sha256) = 64", name="ck_ingestion_source_objects_sha"),
        sa.CheckConstraint("size_bytes >= 0", name="ck_ingestion_source_objects_size"),
        sa.CheckConstraint("status in ('uploading','committed','quarantined','revoked','deleted')", name="ck_ingestion_source_objects_status"),
    )

    op.create_table(
        "ingestion_document_versions",
        sa.Column("document_version_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("source_object_id", sa.String(length=160), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata_hash", sa.String(length=64), nullable=False),
        sa.Column("immutability_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["source_object_id"], ["ingestion_source_objects.source_object_id"], ondelete="RESTRICT", name="fk_ingestion_document_versions_source"),
        sa.UniqueConstraint("source_object_id", "version_no", name="uq_ingestion_document_versions_version"),
        sa.CheckConstraint("version_no > 0", name="ck_ingestion_document_versions_version_no"),
        sa.CheckConstraint("length(content_hash) = 64", name="ck_ingestion_document_versions_content_hash"),
        sa.CheckConstraint("length(metadata_hash) = 64", name="ck_ingestion_document_versions_metadata_hash"),
        sa.CheckConstraint("status in ('active','superseded','revoked','deleted')", name="ck_ingestion_document_versions_status"),
    )

    op.create_table(
        "ingestion_parse_plans",
        sa.Column("parse_plan_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("document_version_id", sa.String(length=160), nullable=False),
        sa.Column("parser_route", sa.JSON(), nullable=False),
        sa.Column("parser_policy_ref", sa.String(length=240), nullable=False),
        sa.Column("parser_bundle_hash", sa.String(length=64), nullable=False),
        sa.Column("quality_policy_ref", sa.String(length=240), nullable=False),
        sa.Column("security_decision_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_version_id"], ["ingestion_document_versions.document_version_id"], ondelete="RESTRICT", name="fk_ingestion_parse_plans_document_version"),
        sa.CheckConstraint("length(parser_bundle_hash) = 64", name="ck_ingestion_parse_plans_bundle_hash"),
        sa.CheckConstraint("status in ('planned','blocked','superseded','cancelled')", name="ck_ingestion_parse_plans_status"),
    )

    op.create_table(
        "ingestion_parse_jobs",
        sa.Column("parse_job_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parse_plan_id", sa.String(length=160), nullable=False),
        sa.Column("document_version_id", sa.String(length=160), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("priority_class", sa.String(length=48), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parse_plan_id"], ["ingestion_parse_plans.parse_plan_id"], ondelete="RESTRICT", name="fk_ingestion_parse_jobs_plan"),
        sa.ForeignKeyConstraint(["document_version_id"], ["ingestion_document_versions.document_version_id"], ondelete="RESTRICT", name="fk_ingestion_parse_jobs_document_version"),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_ingestion_parse_jobs_idempotency"),
        sa.CheckConstraint("attempt_count >= 0", name="ck_ingestion_parse_jobs_attempt_count"),
        sa.CheckConstraint("status in ('queued','leased','running','succeeded','blocked','failed','cancelled','dead_letter')", name="ck_ingestion_parse_jobs_status"),
    )

    op.create_table(
        "ingestion_parse_attempts",
        sa.Column("parse_attempt_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parse_job_id", sa.String(length=160), nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.String(length=160), nullable=False),
        sa.Column("lease_ref", sa.String(length=160), nullable=False),
        sa.Column("fencing_token", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("failure_code", sa.String(length=128), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["parse_job_id"], ["ingestion_parse_jobs.parse_job_id"], ondelete="RESTRICT", name="fk_ingestion_parse_attempts_job"),
        sa.UniqueConstraint("parse_job_id", "attempt_no", name="uq_ingestion_parse_attempts_attempt_no"),
        sa.CheckConstraint("attempt_no > 0", name="ck_ingestion_parse_attempts_attempt_no"),
        sa.CheckConstraint("fencing_token > 0", name="ck_ingestion_parse_attempts_fencing"),
        sa.CheckConstraint("status in ('started','heartbeat','succeeded','blocked','failed','cancelled','fenced_out')", name="ck_ingestion_parse_attempts_status"),
    )

    op.create_table(
        "ingestion_parse_snapshots",
        sa.Column("parse_snapshot_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parse_job_id", sa.String(length=160), nullable=False),
        sa.Column("parse_attempt_id", sa.String(length=160), nullable=False),
        sa.Column("document_version_id", sa.String(length=160), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("canonical_ir_ref", sa.String(length=240), nullable=False),
        sa.Column("canonical_ir_schema_ref", sa.String(length=160), nullable=False),
        sa.Column("parser_id", sa.String(length=160), nullable=False),
        sa.Column("parser_version", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("diagnostics", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parse_job_id"], ["ingestion_parse_jobs.parse_job_id"], ondelete="RESTRICT", name="fk_ingestion_parse_snapshots_job"),
        sa.ForeignKeyConstraint(["parse_attempt_id"], ["ingestion_parse_attempts.parse_attempt_id"], ondelete="RESTRICT", name="fk_ingestion_parse_snapshots_attempt"),
        sa.ForeignKeyConstraint(["document_version_id"], ["ingestion_document_versions.document_version_id"], ondelete="RESTRICT", name="fk_ingestion_parse_snapshots_document_version"),
        sa.UniqueConstraint("parse_job_id", "parse_attempt_id", name="uq_ingestion_parse_snapshots_attempt"),
        sa.CheckConstraint("length(snapshot_hash) = 64", name="ck_ingestion_parse_snapshots_hash"),
        sa.CheckConstraint("status in ('succeeded','blocked','failed','review_required')", name="ck_ingestion_parse_snapshots_status"),
    )

    op.create_table(
        "ingestion_source_spans",
        sa.Column("source_span_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parse_snapshot_id", sa.String(length=160), nullable=False),
        sa.Column("document_version_id", sa.String(length=160), nullable=False),
        sa.Column("block_id", sa.String(length=160), nullable=False),
        sa.Column("page_no", sa.Integer(), nullable=True),
        sa.Column("region_ref", sa.String(length=240), nullable=True),
        sa.Column("coordinate_ref", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("span_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["parse_snapshot_id"], ["ingestion_parse_snapshots.parse_snapshot_id"], ondelete="RESTRICT", name="fk_ingestion_source_spans_snapshot"),
        sa.ForeignKeyConstraint(["document_version_id"], ["ingestion_document_versions.document_version_id"], ondelete="RESTRICT", name="fk_ingestion_source_spans_document_version"),
        sa.CheckConstraint("page_no IS NULL OR page_no > 0", name="ck_ingestion_source_spans_page"),
        sa.CheckConstraint("length(span_hash) = 64", name="ck_ingestion_source_spans_hash"),
    )

    op.create_table(
        "ingestion_quality_gate_decisions",
        sa.Column("quality_decision_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parse_snapshot_id", sa.String(length=160), nullable=False),
        sa.Column("coverage_score", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("review_task_ref", sa.String(length=240), nullable=True),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parse_snapshot_id"], ["ingestion_parse_snapshots.parse_snapshot_id"], ondelete="RESTRICT", name="fk_ingestion_quality_gate_decisions_snapshot"),
        sa.UniqueConstraint("parse_snapshot_id", name="uq_ingestion_quality_gate_decisions_snapshot"),
        sa.CheckConstraint("coverage_score >= 0 and coverage_score <= 1", name="ck_ingestion_quality_gate_decisions_coverage"),
        sa.CheckConstraint("confidence_score >= 0 and confidence_score <= 1", name="ck_ingestion_quality_gate_decisions_confidence"),
        sa.CheckConstraint("length(decision_hash) = 64", name="ck_ingestion_quality_gate_decisions_hash"),
        sa.CheckConstraint("decision in ('publish','block','human_review','fallback')", name="ck_ingestion_quality_gate_decisions_decision"),
    )

    op.create_table(
        "ingestion_indexable_document_snapshots",
        sa.Column("indexable_snapshot_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("parse_snapshot_id", sa.String(length=160), nullable=False),
        sa.Column("document_version_id", sa.String(length=160), nullable=False),
        sa.Column("quality_decision_id", sa.String(length=160), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("handoff_envelope_hash", sa.String(length=64), nullable=False),
        sa.Column("visibility_ref", sa.String(length=240), nullable=False),
        sa.Column("knowledge_handoff_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parse_snapshot_id"], ["ingestion_parse_snapshots.parse_snapshot_id"], ondelete="RESTRICT", name="fk_ingestion_indexable_snapshots_parse_snapshot"),
        sa.ForeignKeyConstraint(["document_version_id"], ["ingestion_document_versions.document_version_id"], ondelete="RESTRICT", name="fk_ingestion_indexable_snapshots_document_version"),
        sa.ForeignKeyConstraint(["quality_decision_id"], ["ingestion_quality_gate_decisions.quality_decision_id"], ondelete="RESTRICT", name="fk_ingestion_indexable_snapshots_quality"),
        sa.UniqueConstraint("parse_snapshot_id", name="uq_ingestion_indexable_snapshots_parse_snapshot"),
        sa.CheckConstraint("length(snapshot_hash) = 64", name="ck_ingestion_indexable_snapshots_hash"),
        sa.CheckConstraint("length(handoff_envelope_hash) = 64", name="ck_ingestion_indexable_snapshots_envelope_hash"),
        sa.CheckConstraint("knowledge_handoff_status in ('pending','published','blocked','dead_letter')", name="ck_ingestion_indexable_snapshots_handoff"),
    )

    op.create_table(
        "ingestion_outbox_events",
        sa.Column("outbox_event_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("aggregate_ref", sa.String(length=240), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("publish_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("length(payload_hash) = 64", name="ck_ingestion_outbox_events_payload_hash"),
        sa.CheckConstraint("publish_status in ('pending','published','failed','dead_letter')", name="ck_ingestion_outbox_events_status"),
    )

    op.create_table(
        "ingestion_dead_letters",
        sa.Column("dead_letter_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("source_ref", sa.String(length=240), nullable=False),
        sa.Column("failure_code", sa.String(length=128), nullable=False),
        sa.Column("retryable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    for table_name in [
        "ingestion_dead_letters",
        "ingestion_outbox_events",
        "ingestion_indexable_document_snapshots",
        "ingestion_quality_gate_decisions",
        "ingestion_source_spans",
        "ingestion_parse_snapshots",
        "ingestion_parse_attempts",
        "ingestion_parse_jobs",
        "ingestion_parse_plans",
        "ingestion_document_versions",
        "ingestion_source_objects",
    ]:
        op.drop_table(table_name)
