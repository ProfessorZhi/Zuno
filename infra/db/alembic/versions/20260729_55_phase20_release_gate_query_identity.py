"""add phase20 release gate query identity

Revision ID: 20260729_55
Revises: 20260729_54
Create Date: 2026-07-29 00:55:00.000000
"""

from __future__ import annotations

from alembic import op


revision = "20260729_55"
down_revision = "20260729_54"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_observability_release_gate_evaluations_gate_id",
        "observability_release_gate_evaluations",
        ["gate_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_observability_release_gate_evaluations_gate_id",
        "observability_release_gate_evaluations",
        type_="unique",
    )
