"""add Product canonical runtime owner binding

Revision ID: 20260920_62
Revises: 20260920_61
Create Date: 2026-09-20 22:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260920_62"
down_revision = "20260920_61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name in (
        "runtime_request_ref",
        "canonical_task_id",
        "canonical_run_id",
        "runtime_execution_spec_ref",
    ):
        op.add_column(
            "product_command_receipts",
            sa.Column(name, sa.String(length=240), nullable=True),
        )
    op.add_column(
        "product_command_receipts",
        sa.Column("runtime_execution_spec_hash", sa.String(length=64), nullable=True),
    )
    op.create_check_constraint(
        "ck_product_command_receipts_runtime_spec_hash",
        "product_command_receipts",
        "runtime_execution_spec_hash IS NULL OR char_length(runtime_execution_spec_hash) = 64",
    )
    op.create_index(
        "ix_product_command_receipts_canonical_task",
        "product_command_receipts",
        ["tenant_id", "canonical_task_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_product_command_receipts_canonical_task",
        table_name="product_command_receipts",
    )
    op.drop_constraint(
        "ck_product_command_receipts_runtime_spec_hash",
        "product_command_receipts",
        type_="check",
    )
    for name in (
        "runtime_execution_spec_hash",
        "runtime_execution_spec_ref",
        "canonical_run_id",
        "canonical_task_id",
        "runtime_request_ref",
    ):
        op.drop_column("product_command_receipts", name)
