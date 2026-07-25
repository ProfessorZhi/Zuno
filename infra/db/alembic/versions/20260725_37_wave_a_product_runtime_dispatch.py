"""add product message and dispatch outbox bridge

Revision ID: 20260725_37
Revises: 20260725_36
Create Date: 2026-07-25 01:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260725_37"
down_revision = "20260725_36"
branch_labels = None
depends_on = None


def _hash_check(column: str, name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(f"char_length({column}) = 64", name=name)


def upgrade() -> None:
    op.create_table(
        "product_messages",
        sa.Column("message_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("conversation_id", sa.String(length=180), nullable=False),
        sa.Column("submission_id", sa.String(length=180), nullable=False),
        sa.Column("principal_id", sa.String(length=120), nullable=False),
        sa.Column("message_role", sa.String(length=40), nullable=False),
        sa.Column("message_hash", sa.String(length=64), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("publication_ref", sa.String(length=240), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["product_conversation_threads.conversation_id"],
            name="fk_product_messages_conversation",
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["product_submissions.submission_id"],
            name="fk_product_messages_submission",
        ),
        sa.UniqueConstraint("conversation_id", "sequence_no", name="uq_product_messages_sequence"),
        sa.UniqueConstraint("submission_id", "message_role", name="uq_product_messages_submission_role"),
        _hash_check("message_hash", "ck_product_messages_hash"),
        sa.CheckConstraint("sequence_no > 0", name="ck_product_messages_sequence_positive"),
        sa.CheckConstraint("message_role in ('USER','ASSISTANT_PROJECTION')", name="ck_product_messages_role"),
        sa.CheckConstraint(
            "(message_role = 'USER' and publication_ref is null) or "
            "(message_role = 'ASSISTANT_PROJECTION' and publication_ref is not null)",
            name="ck_product_messages_publication_boundary",
        ),
    )


def downgrade() -> None:
    op.drop_table("product_messages")
