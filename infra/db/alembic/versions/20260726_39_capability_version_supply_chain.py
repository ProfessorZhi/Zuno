"""add capability version supply-chain verification facts

Revision ID: 20260726_39
Revises: 20260726_38
Create Date: 2026-07-26 02:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260726_39"
down_revision = "20260726_38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("capability_versions", sa.Column("source_ref", sa.String(length=240), nullable=True))
    op.add_column("capability_versions", sa.Column("license_ref", sa.String(length=240), nullable=True))
    op.add_column("capability_versions", sa.Column("dependency_refs_hash", sa.String(length=64), nullable=True))
    op.add_column("capability_versions", sa.Column("runtime_requirement_refs_hash", sa.String(length=64), nullable=True))
    op.add_column("capability_versions", sa.Column("signature_ref", sa.String(length=240), nullable=True))
    op.add_column("capability_versions", sa.Column("verification_ref", sa.String(length=240), nullable=True))
    op.add_column("capability_versions", sa.Column("supply_chain_hash", sa.String(length=64), nullable=True))
    op.add_column(
        "capability_versions",
        sa.Column("supply_chain_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_check_constraint(
        "ck_capability_versions_dependency_refs_hash",
        "capability_versions",
        "dependency_refs_hash is null or char_length(dependency_refs_hash) = 64",
    )
    op.create_check_constraint(
        "ck_capability_versions_runtime_req_hash",
        "capability_versions",
        "runtime_requirement_refs_hash is null or char_length(runtime_requirement_refs_hash) = 64",
    )
    op.create_check_constraint(
        "ck_capability_versions_supply_chain_hash",
        "capability_versions",
        "supply_chain_hash is null or char_length(supply_chain_hash) = 64",
    )
    op.create_check_constraint(
        "ck_capability_versions_verified_refs",
        "capability_versions",
        "supply_chain_verified = false or ("
        "source_ref is not null and license_ref is not null and dependency_refs_hash is not null and "
        "runtime_requirement_refs_hash is not null and signature_ref is not null and "
        "verification_ref is not null and supply_chain_hash is not null"
        ")",
    )


def downgrade() -> None:
    op.drop_constraint("ck_capability_versions_verified_refs", "capability_versions", type_="check")
    op.drop_constraint("ck_capability_versions_supply_chain_hash", "capability_versions", type_="check")
    op.drop_constraint("ck_capability_versions_runtime_req_hash", "capability_versions", type_="check")
    op.drop_constraint("ck_capability_versions_dependency_refs_hash", "capability_versions", type_="check")
    op.drop_column("capability_versions", "supply_chain_verified")
    op.drop_column("capability_versions", "supply_chain_hash")
    op.drop_column("capability_versions", "verification_ref")
    op.drop_column("capability_versions", "signature_ref")
    op.drop_column("capability_versions", "runtime_requirement_refs_hash")
    op.drop_column("capability_versions", "dependency_refs_hash")
    op.drop_column("capability_versions", "license_ref")
    op.drop_column("capability_versions", "source_ref")
