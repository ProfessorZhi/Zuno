"""add tenant boundary to idempotency claims

Revision ID: 20260716_05
Revises: 20260715_04
Create Date: 2026-07-16 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260716_05"
down_revision = "20260715_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "infra_idempotency_claims",
        sa.Column("tenant_id", sa.String(length=128), server_default="", nullable=False),
    )
    op.drop_constraint("uq_infra_idempotency_claims_scope_key", "infra_idempotency_claims", type_="unique")
    op.create_unique_constraint(
        "uq_infra_idempotency_claims_tenant_scope_key",
        "infra_idempotency_claims",
        ["tenant_id", "scope", "idempotency_key"],
    )
    op.alter_column("infra_idempotency_claims", "tenant_id", server_default=None)


def downgrade() -> None:
    op.drop_constraint("uq_infra_idempotency_claims_tenant_scope_key", "infra_idempotency_claims", type_="unique")
    op.create_unique_constraint(
        "uq_infra_idempotency_claims_scope_key",
        "infra_idempotency_claims",
        ["scope", "idempotency_key"],
    )
    op.drop_column("infra_idempotency_claims", "tenant_id")
