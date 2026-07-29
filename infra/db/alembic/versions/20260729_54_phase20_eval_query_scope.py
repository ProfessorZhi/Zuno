"""add phase20 eval query authorization scope

Revision ID: 20260729_54
Revises: 20260729_53
Create Date: 2026-07-29 00:54:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260729_54"
down_revision = "20260729_53"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "observability_eval_runs",
        sa.Column("tenant_id", sa.String(length=128), nullable=False, server_default="tenant-unknown"),
    )
    op.add_column(
        "observability_eval_runs",
        sa.Column("workspace_id", sa.String(length=128), nullable=False, server_default="workspace-unknown"),
    )
    op.create_index(
        "ix_observability_eval_runs_scope",
        "observability_eval_runs",
        ["tenant_id", "workspace_id", "run_id"],
        unique=False,
    )
    op.alter_column("observability_eval_runs", "tenant_id", server_default=None)
    op.alter_column("observability_eval_runs", "workspace_id", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_observability_eval_runs_scope", table_name="observability_eval_runs")
    op.drop_column("observability_eval_runs", "workspace_id")
    op.drop_column("observability_eval_runs", "tenant_id")
