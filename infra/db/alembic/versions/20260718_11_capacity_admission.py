"""add capacity admission and reservation primitives

Revision ID: 20260718_11
Revises: 20260717_10
Create Date: 2026-07-18 11:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260718_11"
down_revision = "20260717_10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_capacity_admissions",
        sa.Column("resource_id", sa.String(length=160), primary_key=True),
        sa.Column("capacity_limit", sa.Integer(), nullable=False),
        sa.Column("drained", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("updated_by", sa.String(length=128), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "capacity_limit > 0",
            name="ck_infra_capacity_admissions_limit_positive",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_infra_capacity_admissions_generation_positive",
        ),
    )

    op.create_table(
        "infra_capacity_reservations",
        sa.Column("reservation_id", sa.String(length=160), primary_key=True),
        sa.Column("resource_id", sa.String(length=160), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["infra_capacity_admissions.resource_id"],
            ondelete="CASCADE",
            name="fk_infra_capacity_reservations_admission",
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_infra_capacity_reservations_amount_positive",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_infra_capacity_reservations_generation_positive",
        ),
        sa.CheckConstraint(
            "status in ('active','released','expired')",
            name="ck_infra_capacity_reservations_status",
        ),
    )
    op.create_index(
        "ix_infra_capacity_reservations_resource_active",
        "infra_capacity_reservations",
        ["resource_id", "status", "expires_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_infra_capacity_reservations_resource_active",
        table_name="infra_capacity_reservations",
    )
    op.drop_table("infra_capacity_reservations")
    op.drop_table("infra_capacity_admissions")
