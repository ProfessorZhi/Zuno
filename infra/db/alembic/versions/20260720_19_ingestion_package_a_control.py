"""add ingestion package a parse control facts

Revision ID: 20260720_19
Revises: 20260719_18
Create Date: 2026-07-20 19:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260720_19"
down_revision = "20260719_18"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ingestion_parse_attempts", sa.Column("workspace_id", sa.String(length=128), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("source_object_id", sa.String(length=160), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("document_version_id", sa.String(length=160), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("parse_plan_id", sa.String(length=160), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("idempotency_key", sa.String(length=240), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("security_epoch_ref", sa.String(length=160), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("ingestion_parse_attempts", sa.Column("domain_commit_ref", sa.String(length=240), nullable=True))
    op.create_foreign_key(
        "fk_ingestion_parse_attempts_source_object",
        "ingestion_parse_attempts",
        "ingestion_source_objects",
        ["source_object_id"],
        ["source_object_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_ingestion_parse_attempts_document_version",
        "ingestion_parse_attempts",
        "ingestion_document_versions",
        ["document_version_id"],
        ["document_version_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_ingestion_parse_attempts_plan",
        "ingestion_parse_attempts",
        "ingestion_parse_plans",
        ["parse_plan_id"],
        ["parse_plan_id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_ingestion_parse_attempts_tenant_idempotency",
        "ingestion_parse_attempts",
        ["tenant_id", "idempotency_key"],
    )
    op.create_index(
        "ix_ingestion_parse_attempts_current_lease",
        "ingestion_parse_attempts",
        ["parse_job_id", "fencing_token", "worker_id", "status"],
    )

    op.drop_constraint("ck_ingestion_parse_attempts_status", "ingestion_parse_attempts", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_attempts_status",
        "ingestion_parse_attempts",
        "status in ('created','lease_claimed','running','succeeded','blocked','failed','cancelled','lease_lost','dead_letter','fenced_out')",
    )
    op.drop_constraint("ck_ingestion_parse_jobs_status", "ingestion_parse_jobs", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_jobs_status",
        "ingestion_parse_jobs",
        "status in ('planned','queued','leased','running','succeeded','blocked','failed','cancelled','dead_letter')",
    )

    op.create_table(
        "ingestion_parse_leases",
        sa.Column("lease_ref", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("parse_job_id", sa.String(length=160), nullable=False),
        sa.Column("parse_attempt_id", sa.String(length=160), nullable=False),
        sa.Column("worker_id", sa.String(length=160), nullable=False),
        sa.Column("fencing_token", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("domain_commit_ref", sa.String(length=240), nullable=True),
        sa.ForeignKeyConstraint(["parse_job_id"], ["ingestion_parse_jobs.parse_job_id"], ondelete="RESTRICT", name="fk_ingestion_parse_leases_job"),
        sa.ForeignKeyConstraint(["parse_attempt_id"], ["ingestion_parse_attempts.parse_attempt_id"], ondelete="RESTRICT", name="fk_ingestion_parse_leases_attempt"),
        sa.UniqueConstraint("parse_job_id", "fencing_token", name="uq_ingestion_parse_leases_fencing"),
        sa.CheckConstraint("fencing_token > 0", name="ck_ingestion_parse_leases_fencing"),
        sa.CheckConstraint("state in ('claimed','renewed','committed','released','expired','lost','reconciled')", name="ck_ingestion_parse_leases_state"),
    )

    op.add_column("ingestion_dead_letters", sa.Column("parse_job_id", sa.String(length=160), nullable=True))
    op.add_column("ingestion_dead_letters", sa.Column("parse_attempt_id", sa.String(length=160), nullable=True))
    op.add_column("ingestion_dead_letters", sa.Column("rabbitmq_dead_letter_ref", sa.String(length=240), nullable=True))
    op.add_column("ingestion_dead_letters", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.create_foreign_key(
        "fk_ingestion_dead_letters_parse_job",
        "ingestion_dead_letters",
        "ingestion_parse_jobs",
        ["parse_job_id"],
        ["parse_job_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_ingestion_dead_letters_parse_attempt",
        "ingestion_dead_letters",
        "ingestion_parse_attempts",
        ["parse_attempt_id"],
        ["parse_attempt_id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_ingestion_dead_letters_parse_job", "ingestion_dead_letters", ["parse_job_id"])


def downgrade() -> None:
    op.drop_index("ix_ingestion_dead_letters_parse_job", table_name="ingestion_dead_letters")
    op.drop_constraint("fk_ingestion_dead_letters_parse_attempt", "ingestion_dead_letters", type_="foreignkey")
    op.drop_constraint("fk_ingestion_dead_letters_parse_job", "ingestion_dead_letters", type_="foreignkey")
    op.drop_column("ingestion_dead_letters", "retry_count")
    op.drop_column("ingestion_dead_letters", "rabbitmq_dead_letter_ref")
    op.drop_column("ingestion_dead_letters", "parse_attempt_id")
    op.drop_column("ingestion_dead_letters", "parse_job_id")

    op.drop_table("ingestion_parse_leases")

    op.drop_constraint("ck_ingestion_parse_jobs_status", "ingestion_parse_jobs", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_jobs_status",
        "ingestion_parse_jobs",
        "status in ('queued','leased','running','succeeded','blocked','failed','cancelled','dead_letter')",
    )
    op.drop_constraint("ck_ingestion_parse_attempts_status", "ingestion_parse_attempts", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_attempts_status",
        "ingestion_parse_attempts",
        "status in ('started','heartbeat','succeeded','blocked','failed','cancelled','fenced_out')",
    )
    op.drop_index("ix_ingestion_parse_attempts_current_lease", table_name="ingestion_parse_attempts")
    op.drop_constraint("uq_ingestion_parse_attempts_tenant_idempotency", "ingestion_parse_attempts", type_="unique")
    op.drop_constraint("fk_ingestion_parse_attempts_plan", "ingestion_parse_attempts", type_="foreignkey")
    op.drop_constraint("fk_ingestion_parse_attempts_document_version", "ingestion_parse_attempts", type_="foreignkey")
    op.drop_constraint("fk_ingestion_parse_attempts_source_object", "ingestion_parse_attempts", type_="foreignkey")
    for column_name in [
        "domain_commit_ref",
        "heartbeat_at",
        "lease_expires_at",
        "security_epoch_ref",
        "idempotency_key",
        "parse_plan_id",
        "document_version_id",
        "source_object_id",
        "workspace_id",
    ]:
        op.drop_column("ingestion_parse_attempts", column_name)
