"""add Product runtime canonical execution binding

Revision ID: 20260920_62
Revises: 20260920_61
Create Date: 2026-09-20 20:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260920_62"
down_revision = "20260920_61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_runtime_execution_bindings",
        sa.Column("binding_ref", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("runtime_request_ref", sa.String(length=240), nullable=False),
        sa.Column("runtime_execution_spec_ref", sa.String(length=180), nullable=False),
        sa.Column("runtime_execution_spec_hash", sa.String(length=64), nullable=False),
        sa.Column("agent_run_ref", sa.String(length=240), nullable=False),
        sa.Column("canonical_task_id", sa.String(length=180), nullable=False),
        sa.Column("canonical_run_id", sa.String(length=220), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("runtime_final_state", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["runtime_execution_spec_ref"],
            ["product_runtime_execution_specs.runtime_execution_spec_ref"],
            name="fk_product_runtime_bindings_spec",
        ),
        sa.UniqueConstraint("tenant_id", "runtime_request_ref", name="uq_product_runtime_bindings_request"),
        sa.UniqueConstraint("tenant_id", "canonical_task_id", name="uq_product_runtime_bindings_task"),
        sa.UniqueConstraint("tenant_id", "canonical_run_id", name="uq_product_runtime_bindings_run"),
        sa.CheckConstraint(
            "char_length(runtime_execution_spec_hash) = 64",
            name="ck_product_runtime_bindings_spec_hash",
        ),
        sa.CheckConstraint(
            "status in ('OWNER_ADMITTED','RUNTIME_OBSERVED')",
            name="ck_product_runtime_bindings_status",
        ),
    )
    op.create_index(
        "ix_product_runtime_bindings_tenant_spec",
        "product_runtime_execution_bindings",
        ["tenant_id", "runtime_execution_spec_ref"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_product_runtime_bindings_tenant_spec",
        table_name="product_runtime_execution_bindings",
    )
    op.drop_table("product_runtime_execution_bindings")
