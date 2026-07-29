"""add phase20 eval result revisions

Revision ID: 20260729_56
Revises: 20260729_55
Create Date: 2026-07-29 00:56:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260729_56"
down_revision = "20260729_55"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    op.create_table(
        "observability_eval_result_revisions",
        sa.Column("revision_id", sa.String(length=220), primary_key=True),
        sa.Column("run_id", sa.String(length=180), nullable=False),
        sa.Column("previous_result_set_hash", sa.String(length=64), nullable=False),
        sa.Column("revised_result_set_hash", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("revision_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["observability_eval_runs.run_id"], name="fk_observability_eval_result_revisions_run"),
        _hash_check("previous_result_set_hash", "ck_observability_eval_result_revisions_previous_hash"),
        _hash_check("revised_result_set_hash", "ck_observability_eval_result_revisions_revised_hash"),
        _hash_check("revision_hash", "ck_observability_eval_result_revisions_hash"),
        sa.CheckConstraint(
            "previous_result_set_hash <> revised_result_set_hash",
            name="ck_observability_eval_result_revisions_changed",
        ),
        sa.UniqueConstraint("run_id", "previous_result_set_hash", "revised_result_set_hash", name="uq_observability_eval_result_revisions_pair"),
    )


def downgrade() -> None:
    op.drop_table("observability_eval_result_revisions")
