"""Allow explicit Product late owner receipt status.

Revision ID: 20260726_40
Revises: 20260726_39
Create Date: 2026-07-26
"""

from __future__ import annotations

from alembic import op


revision = "20260726_40"
down_revision = "20260726_39"
branch_labels = None
depends_on = None


OLD_STATUS_CHECK = (
    "status in ('ACCEPTED','DUPLICATE','CONFLICT','REJECTED','BLOCKED','OWNER_TIMEOUT')"
)
NEW_STATUS_CHECK = (
    "status in ("
    "'ACCEPTED','DUPLICATE','CONFLICT','REJECTED','BLOCKED','OWNER_TIMEOUT','LATE_OWNER_RECEIPT'"
    ")"
)


def upgrade() -> None:
    op.drop_constraint("ck_product_receipts_status", "product_command_receipts", type_="check")
    op.create_check_constraint(
        "ck_product_receipts_status",
        "product_command_receipts",
        NEW_STATUS_CHECK,
    )


def downgrade() -> None:
    op.drop_constraint("ck_product_receipts_status", "product_command_receipts", type_="check")
    op.create_check_constraint(
        "ck_product_receipts_status",
        "product_command_receipts",
        OLD_STATUS_CHECK,
    )
