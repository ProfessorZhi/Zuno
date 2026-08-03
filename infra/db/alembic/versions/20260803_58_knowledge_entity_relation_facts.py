"""add canonical knowledge entity and directed relation facts

PHASE22 CC-B1/B2 hardening (DeepSeek1): canonical entity and directed-relation
facts become first-class PostgreSQL domain facts owned by Knowledge, consumed
from the formal canonical IR manifest (the frozen extractor output). Neo4j
remains an index / read-model owner only.

Revision ID: 20260803_58
Revises: 20260803_57
Create Date: 2026-08-03 00:58:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260803_58"
down_revision = "20260803_57"
branch_labels = None
depends_on = None


def _hash_check(column_name: str, constraint_name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(
        f"length({column_name}) = 64", name=constraint_name
    )


def upgrade() -> None:
    op.create_table(
        "knowledge_entities",
        sa.Column("entity_id", sa.String(length=240), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("knowledge_version_id", sa.String(length=180), nullable=False),
        sa.Column("entity_kind", sa.String(length=80), nullable=False),
        sa.Column("canonical_name", sa.String(length=240), nullable=False),
        sa.Column("source_chunk_id", sa.String(length=240), nullable=False),
        sa.Column("source_span_ref", sa.String(length=240), nullable=False),
        sa.Column("entity_hash", sa.String(length=64), nullable=False),
        sa.Column("authority_ref", sa.String(length=240), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_version_id"],
            ["knowledge_domain_versions.knowledge_version_id"],
            ondelete="RESTRICT",
            name="fk_knowledge_entities_version",
        ),
        sa.UniqueConstraint(
            "tenant_id", "knowledge_version_id", "entity_id",
            name="uq_knowledge_entities_version_entity",
        ),
        sa.CheckConstraint("length(entity_kind) > 0", name="ck_knowledge_entities_kind"),
        sa.CheckConstraint("length(canonical_name) > 0", name="ck_knowledge_entities_name"),
        _hash_check("entity_hash", "ck_knowledge_entities_hash"),
    )
    op.create_index(
        "ix_knowledge_entities_scope",
        "knowledge_entities",
        ["tenant_id", "workspace_id", "knowledge_version_id"],
    )

    op.create_table(
        "knowledge_relations",
        sa.Column("relation_id", sa.String(length=240), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("workspace_id", sa.String(length=128), nullable=False),
        sa.Column("knowledge_version_id", sa.String(length=180), nullable=False),
        sa.Column("from_entity_id", sa.String(length=240), nullable=False),
        sa.Column("to_entity_id", sa.String(length=240), nullable=False),
        sa.Column("relation_kind", sa.String(length=120), nullable=False),
        sa.Column("source_chunk_id", sa.String(length=240), nullable=False),
        sa.Column("source_span_ref", sa.String(length=240), nullable=False),
        sa.Column("relation_hash", sa.String(length=64), nullable=False),
        sa.Column("authority_ref", sa.String(length=240), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_version_id"],
            ["knowledge_domain_versions.knowledge_version_id"],
            ondelete="RESTRICT",
            name="fk_knowledge_relations_version",
        ),
        sa.ForeignKeyConstraint(
            ["from_entity_id"],
            ["knowledge_entities.entity_id"],
            ondelete="RESTRICT",
            name="fk_knowledge_relations_from_entity",
        ),
        sa.ForeignKeyConstraint(
            ["to_entity_id"],
            ["knowledge_entities.entity_id"],
            ondelete="RESTRICT",
            name="fk_knowledge_relations_to_entity",
        ),
        sa.UniqueConstraint(
            "tenant_id", "knowledge_version_id", "relation_id",
            name="uq_knowledge_relations_version_relation",
        ),
        sa.CheckConstraint(
            "from_entity_id <> to_entity_id",
            name="ck_knowledge_relations_directed",
        ),
        sa.CheckConstraint("length(relation_kind) > 0", name="ck_knowledge_relations_kind"),
        _hash_check("relation_hash", "ck_knowledge_relations_hash"),
    )
    op.create_index(
        "ix_knowledge_relations_scope",
        "knowledge_relations",
        ["tenant_id", "workspace_id", "knowledge_version_id"],
    )
    op.create_index(
        "ix_knowledge_relations_from",
        "knowledge_relations",
        ["knowledge_version_id", "from_entity_id"],
    )


def downgrade() -> None:
    op.drop_table("knowledge_relations")
    op.drop_table("knowledge_entities")
