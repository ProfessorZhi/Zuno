"""add Product RuntimeExecutionSpec durable handoff

Revision ID: 20260920_61
Revises: 20260920_60
Create Date: 2026-09-20 10:55:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260920_61"
down_revision = "20260920_60"
branch_labels = None
depends_on = None


def _hash_check(column: str, name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(f"char_length({column}) = 64", name=name)


def upgrade() -> None:
    op.create_table(
        "product_runtime_execution_specs",
        sa.Column("runtime_execution_spec_ref", sa.String(length=180), primary_key=True),
        sa.Column("runtime_request_ref", sa.String(length=240), nullable=False),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("conversation_id", sa.String(length=180), nullable=False),
        sa.Column("principal_id", sa.String(length=120), nullable=False),
        sa.Column("submission_id", sa.String(length=180), nullable=False),
        sa.Column("client_request_id", sa.String(length=180), nullable=False),
        sa.Column("active_agent_version_id", sa.String(length=180), nullable=False),
        sa.Column("goal_material_ref", sa.String(length=240), nullable=False),
        sa.Column("goal_text", sa.Text(), nullable=False),
        sa.Column("runtime_surface", sa.String(length=80), nullable=False),
        sa.Column("plan_kind", sa.String(length=80), nullable=False),
        sa.Column("knowledge_space_refs", sa.JSON(), nullable=False),
        sa.Column("budget_limits", sa.JSON(), nullable=False),
        sa.Column("tool_id", sa.String(length=240), nullable=True),
        sa.Column("tool_arguments", sa.JSON(), nullable=True),
        sa.Column("data_classification", sa.String(length=40), nullable=False),
        sa.Column("retention_scope", sa.String(length=40), nullable=False),
        sa.Column("content_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("spec_version", sa.String(length=80), nullable=False),
        sa.Column("spec_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["product_submissions.submission_id"],
            name="fk_product_runtime_specs_submission",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["product_conversation_threads.conversation_id"],
            name="fk_product_runtime_specs_conversation",
        ),
        sa.ForeignKeyConstraint(
            ["active_agent_version_id"],
            ["product_agent_versions.agent_version_id"],
            name="fk_product_runtime_specs_agent_version",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "runtime_request_ref",
            name="uq_product_runtime_specs_runtime_request",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "workspace_id",
            "client_request_id",
            name="uq_product_runtime_specs_client_request",
        ),
        _hash_check("content_fingerprint", "ck_product_runtime_specs_content_fingerprint"),
        _hash_check("spec_hash", "ck_product_runtime_specs_hash"),
        sa.CheckConstraint(
            "char_length(goal_text) > 0",
            name="ck_product_runtime_specs_goal_nonempty",
        ),
        sa.CheckConstraint(
            "data_classification = 'internal'",
            name="ck_product_runtime_specs_classification",
        ),
        sa.CheckConstraint(
            "retention_scope = 'CONVERSATION'",
            name="ck_product_runtime_specs_retention_scope",
        ),
    )
    op.create_index(
        "ix_product_runtime_specs_tenant_submission",
        "product_runtime_execution_specs",
        ["tenant_id", "submission_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_product_runtime_specs_tenant_submission",
        table_name="product_runtime_execution_specs",
    )
    op.drop_table("product_runtime_execution_specs")
