"""add canonical domain mutation and version tables

Revision ID: 20260813_57
Revises: 20260729_56
Create Date: 2026-08-13 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260813_57"
down_revision = "20260729_56"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "domain_aggregate_heads",
        sa.Column("tenant_id", sa.String(length=180), nullable=False),
        sa.Column("matter_id", sa.String(length=220), nullable=False),
        sa.Column("scope_ref", sa.String(length=240), nullable=False),
        sa.Column("domain_version", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("last_mutation_id", sa.String(length=220), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("tenant_id", "matter_id", name="pk_domain_aggregate_heads"),
    )
    op.create_table(
        "domain_mutation_records",
        sa.Column("mutation_id", sa.String(length=220), nullable=False),
        sa.Column("tenant_id", sa.String(length=180), nullable=False),
        sa.Column("matter_id", sa.String(length=220), nullable=False),
        sa.Column("scope_ref", sa.String(length=240), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("expected_domain_version", sa.BigInteger(), nullable=False),
        sa.Column("mutation_type", sa.String(length=160), nullable=False),
        sa.Column("proposal_json", sa.JSON(), nullable=False),
        sa.Column("proposal_reference", sa.String(length=512), nullable=True),
        sa.Column("principal_ref", sa.String(length=220), nullable=False),
        sa.Column("correlation_id", sa.String(length=240), nullable=False),
        sa.Column("causation_ref", sa.String(length=512), nullable=True),
        sa.Column("security_context_ref", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reason_code", sa.String(length=160), nullable=False),
        sa.Column("domain_version_before", sa.BigInteger(), nullable=False),
        sa.Column("domain_version_after", sa.BigInteger(), nullable=False),
        sa.Column("committed_version_ref", sa.String(length=300), nullable=True),
        sa.Column("result_ref", sa.String(length=300), nullable=False),
        sa.Column("trace_ref", sa.String(length=300), nullable=False),
        sa.Column("audit_ref", sa.String(length=300), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("mutation_id", name="pk_domain_mutation_records"),
        sa.UniqueConstraint(
            "tenant_id",
            "matter_id",
            "idempotency_key",
            name="uq_domain_mutation_idempotency",
        ),
    )
    op.create_table(
        "domain_state_versions",
        sa.Column("version_id", sa.String(length=300), nullable=False),
        sa.Column("tenant_id", sa.String(length=180), nullable=False),
        sa.Column("matter_id", sa.String(length=220), nullable=False),
        sa.Column("scope_ref", sa.String(length=240), nullable=False),
        sa.Column("domain_version", sa.BigInteger(), nullable=False),
        sa.Column("mutation_id", sa.String(length=220), nullable=False),
        sa.Column("mutation_type", sa.String(length=160), nullable=False),
        sa.Column("proposal_json", sa.JSON(), nullable=False),
        sa.Column("provenance_json", sa.JSON(), nullable=False),
        sa.Column("principal_ref", sa.String(length=220), nullable=False),
        sa.Column("correlation_id", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("version_id", name="pk_domain_state_versions"),
        sa.UniqueConstraint(
            "tenant_id",
            "matter_id",
            "domain_version",
            name="uq_domain_state_version",
        ),
    )


def downgrade() -> None:
    op.drop_table("domain_state_versions")
    op.drop_table("domain_mutation_records")
    op.drop_table("domain_aggregate_heads")
