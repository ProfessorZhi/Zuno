"""allow ingestion review handoff pending status

Revision ID: 20260724_33
Revises: 20260724_32
Create Date: 2026-07-24 17:00:00
"""

from alembic import op

revision = "20260724_33"
down_revision = "20260724_32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_ingestion_parse_attempts_status", "ingestion_parse_attempts", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_attempts_status",
        "ingestion_parse_attempts",
        "status in ('created','lease_claimed','running','succeeded','blocked','review_pending','approved','handoff_pending','rejected','expired','failed','cancelled','lease_lost','dead_letter','fenced_out')",
    )
    op.drop_constraint("ck_ingestion_parse_jobs_status", "ingestion_parse_jobs", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_jobs_status",
        "ingestion_parse_jobs",
        "status in ('planned','queued','leased','running','succeeded','blocked','review_pending','approved','handoff_pending','rejected','expired','failed','cancelled','dead_letter')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_ingestion_parse_jobs_status", "ingestion_parse_jobs", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_jobs_status",
        "ingestion_parse_jobs",
        "status in ('planned','queued','leased','running','succeeded','blocked','review_pending','approved','rejected','expired','failed','cancelled','dead_letter')",
    )
    op.drop_constraint("ck_ingestion_parse_attempts_status", "ingestion_parse_attempts", type_="check")
    op.create_check_constraint(
        "ck_ingestion_parse_attempts_status",
        "ingestion_parse_attempts",
        "status in ('created','lease_claimed','running','succeeded','blocked','review_pending','approved','rejected','expired','failed','cancelled','lease_lost','dead_letter','fenced_out')",
    )
