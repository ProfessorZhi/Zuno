"""add goal03 product agent publication installation facts

Revision ID: 20260726_38
Revises: 20260725_37
Create Date: 2026-07-26 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260726_38"
down_revision = "20260725_37"
branch_labels = None
depends_on = None


def _hash_check(column: str, name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(f"char_length({column}) = 64", name=name)


def upgrade() -> None:
    op.create_table(
        "product_agent_drafts",
        sa.Column("draft_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("agent_definition_id", sa.String(length=180), nullable=False),
        sa.Column("draft_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_definition_id"],
            ["product_agent_definitions.agent_definition_id"],
            name="fk_product_agent_drafts_definition",
        ),
        sa.UniqueConstraint("agent_definition_id", "draft_hash", name="uq_product_agent_drafts_hash"),
        _hash_check("draft_hash", "ck_product_agent_drafts_hash"),
        sa.CheckConstraint("status in ('DRAFT','LOCKED','DISCARDED')", name="ck_product_agent_drafts_status"),
    )
    op.create_table(
        "product_agent_publications",
        sa.Column("publication_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("agent_version_id", sa.String(length=180), nullable=False),
        sa.Column("publication_scope", sa.String(length=40), nullable=False),
        sa.Column("publication_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_version_id"],
            ["product_agent_versions.agent_version_id"],
            name="fk_product_agent_publications_version",
        ),
        sa.UniqueConstraint("tenant_id", "workspace_id", "agent_version_id", "publication_scope", name="uq_product_agent_publications_scope"),
        _hash_check("publication_hash", "ck_product_agent_publications_hash"),
        sa.CheckConstraint("publication_scope in ('PRIVATE','WORKSPACE','TENANT')", name="ck_product_agent_publications_scope"),
        sa.CheckConstraint("status in ('PUBLISHED','REVOKED','SUPERSEDED')", name="ck_product_agent_publications_status"),
    )
    op.create_table(
        "product_agent_installations",
        sa.Column("installation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("agent_version_id", sa.String(length=180), nullable=False),
        sa.Column("principal_id", sa.String(length=120), nullable=False),
        sa.Column("installation_scope", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_version_id"],
            ["product_agent_versions.agent_version_id"],
            name="fk_product_agent_installations_version",
        ),
        sa.UniqueConstraint("tenant_id", "workspace_id", "principal_id", "agent_version_id", name="uq_product_agent_installations_principal_version"),
        sa.CheckConstraint("installation_scope in ('USER','WORKSPACE','TENANT')", name="ck_product_agent_installations_scope"),
        sa.CheckConstraint("status in ('INSTALLED','ACTIVE','PAUSED','REVOKED')", name="ck_product_agent_installations_status"),
    )
    op.create_table(
        "product_agent_catalog_entries",
        sa.Column("catalog_entry_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("agent_definition_id", sa.String(length=180), nullable=False),
        sa.Column("latest_version_id", sa.String(length=180), nullable=False),
        sa.Column("visibility_scope", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_definition_id"],
            ["product_agent_definitions.agent_definition_id"],
            name="fk_product_agent_catalog_definition",
        ),
        sa.ForeignKeyConstraint(
            ["latest_version_id"],
            ["product_agent_versions.agent_version_id"],
            name="fk_product_agent_catalog_version",
        ),
        sa.UniqueConstraint("tenant_id", "workspace_id", "agent_definition_id", name="uq_product_agent_catalog_definition"),
        sa.CheckConstraint("visibility_scope in ('PRIVATE','WORKSPACE','TENANT')", name="ck_product_agent_catalog_visibility"),
        sa.CheckConstraint("status in ('VISIBLE','HIDDEN','REVOKED')", name="ck_product_agent_catalog_status"),
    )


def downgrade() -> None:
    op.drop_table("product_agent_catalog_entries")
    op.drop_table("product_agent_installations")
    op.drop_table("product_agent_publications")
    op.drop_table("product_agent_drafts")
