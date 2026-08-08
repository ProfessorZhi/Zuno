"""phase22: bind budget owner facts and security expires_at to postgres

Revision ID: 20260808_57
Revises: 20260729_56
Create Date: 2026-08-08 00:00:00.000000

PHASE22-OWNER-FACTS-POSTGRES-INTEGRATION
-----------------------------------------

Two minimal additions are required so the Budget / Security owner-fact
resolvers can resolve Server-owned facts from PostgreSQL with fail-closed
semantics:

1. ``budget_owner_admissions`` -- the durable Budget Admission fact. The
   Budget owner writes the canonical row; Runtime Resolver reads it
   read-only and never mints an allow. Schema carries
   ``budget_decision_id``, ``tenant_id``, ``workspace_id``,
   ``principal_id``, ``run_id``, ``allowed``, ``requested_limits``,
   ``admitted_limits``, ``policy_ref``, ``owner``, ``issued_at``,
   ``expires_at``, ``status`` and an immutable ``decision_hash`` over
   the canonical payload.

2. ``security_authorization_decisions.expires_at`` -- the runtime
   resolver refuses to admit a Security-owner fact whose ``expires_at``
   is missing / malformed / passed. The existing table already records
   ``decision_hash`` and the canonical scope; this column is the only
   owner-side field still missing. A server-side default keeps existing
   inserts working; new decisions carry an explicit owner-supplied
   expiry.

Indexes satisfy the spec requirements:

- decision id unique (primary key on both tables)
- tenant / workspace composite lookup
- run id (Budget)
- status (Budget)
- expires_at (Budget and Security)

No Kafka / Event Sourcing / Distributed Lock / new microservice.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260808_57"
down_revision = "20260729_56"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"char_length({column_name}) = 64 and {column_name} ~ '^[0-9a-f]+$'",
        name=constraint_name,
    )


def upgrade() -> None:
    # --- 1. Budget owner fact table -------------------------------------
    op.create_table(
        "budget_owner_admissions",
        sa.Column("budget_decision_id", sa.String(length=200), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("principal_id", sa.String(length=160), nullable=False),
        sa.Column("run_id", sa.String(length=200), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False),
        sa.Column("requested_limits", sa.JSON(), nullable=False),
        sa.Column("admitted_limits", sa.JSON(), nullable=False),
        sa.Column("policy_ref", sa.String(length=240), nullable=False),
        sa.Column("owner", sa.String(length=160), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        _hash_check("decision_hash", "ck_budget_owner_admissions_decision_hash"),
        sa.CheckConstraint(
            "status in ('ACTIVE','DENIED','EXPIRED','REVOKED')",
            name="ck_budget_owner_admissions_status",
        ),
        sa.CheckConstraint(
            "owner = 'platform.budget.admission'",
            name="ck_budget_owner_admissions_owner",
        ),
    )
    op.create_index(
        "ix_budget_owner_admissions_tenant_workspace",
        "budget_owner_admissions",
        ["tenant_id", "workspace_id"],
    )
    op.create_index(
        "ix_budget_owner_admissions_run",
        "budget_owner_admissions",
        ["run_id"],
    )
    op.create_index(
        "ix_budget_owner_admissions_status_expires",
        "budget_owner_admissions",
        ["status", "expires_at"],
    )

    # --- 2. Security owner fact: expires_at -----------------------------
    op.add_column(
        "security_authorization_decisions",
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now() + interval '15 minutes'"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_security_authorization_decisions_expires",
        "security_authorization_decisions",
        ["tenant_id", "expires_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_security_authorization_decisions_expires",
        table_name="security_authorization_decisions",
    )
    op.drop_column("security_authorization_decisions", "expires_at")

    op.drop_index(
        "ix_budget_owner_admissions_status_expires",
        table_name="budget_owner_admissions",
    )
    op.drop_index(
        "ix_budget_owner_admissions_run",
        table_name="budget_owner_admissions",
    )
    op.drop_index(
        "ix_budget_owner_admissions_tenant_workspace",
        table_name="budget_owner_admissions",
    )
    op.drop_table("budget_owner_admissions")