"""add secret rotation and cross-tenant hit gates

Revision ID: 20260718_15
Revises: 20260718_14
Create Date: 2026-07-18 15:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260718_15"
down_revision = "20260718_14"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "infra_secret_versions",
        sa.Column("secret_ref", sa.String(length=160), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("kms_key_ref", sa.String(length=160), nullable=False),
        sa.Column("config_hash", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint(
            "secret_ref", "version", name="pk_infra_secret_versions"
        ),
        sa.CheckConstraint("version > 0", name="ck_infra_secret_versions_version"),
        sa.CheckConstraint(
            "length(config_hash) = 64",
            name="ck_infra_secret_versions_config_hash",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_infra_secret_versions_payload_hash",
        ),
        sa.CheckConstraint(
            "status in ('staged','active','retired')",
            name="ck_infra_secret_versions_status",
        ),
    )

    op.create_table(
        "infra_secret_rotation_heads",
        sa.Column("secret_ref", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("active_version", sa.Integer(), nullable=False),
        sa.Column("previous_version", sa.Integer(), nullable=True),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["secret_ref", "active_version"],
            ["infra_secret_versions.secret_ref", "infra_secret_versions.version"],
            ondelete="RESTRICT",
            name="fk_infra_secret_rotation_heads_active",
        ),
        sa.ForeignKeyConstraint(
            ["secret_ref", "previous_version"],
            ["infra_secret_versions.secret_ref", "infra_secret_versions.version"],
            ondelete="RESTRICT",
            name="fk_infra_secret_rotation_heads_previous",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_infra_secret_rotation_heads_generation",
        ),
        sa.CheckConstraint(
            "active_version > 0",
            name="ck_infra_secret_rotation_heads_active_version",
        ),
        sa.CheckConstraint(
            "previous_version IS NULL OR previous_version > 0",
            name="ck_infra_secret_rotation_heads_previous_version",
        ),
        sa.CheckConstraint(
            "status in ('active','rolled_back')",
            name="ck_infra_secret_rotation_heads_status",
        ),
    )

    op.create_table(
        "infra_secret_leases",
        sa.Column("lease_id", sa.String(length=160), primary_key=True),
        sa.Column("secret_ref", sa.String(length=160), nullable=False),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["secret_ref", "version"],
            ["infra_secret_versions.secret_ref", "infra_secret_versions.version"],
            ondelete="RESTRICT",
            name="fk_infra_secret_leases_version",
        ),
        sa.CheckConstraint("version > 0", name="ck_infra_secret_leases_version"),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_infra_secret_leases_generation",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_infra_secret_leases_payload_hash",
        ),
    )

    op.create_table(
        "infra_cross_tenant_hits",
        sa.Column("hit_id", sa.String(length=160), primary_key=True),
        sa.Column("service_kind", sa.String(length=64), nullable=False),
        sa.Column("resource_ref", sa.String(length=240), nullable=False),
        sa.Column("expected_tenant_id", sa.String(length=128), nullable=False),
        sa.Column("observed_tenant_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "expected_tenant_id <> observed_tenant_id",
            name="ck_infra_cross_tenant_hits_mismatch",
        ),
        sa.CheckConstraint(
            "action in ('QUARANTINE','FAIL_CLOSED','MANDATORY_AUDIT')",
            name="ck_infra_cross_tenant_hits_action",
        ),
        sa.CheckConstraint(
            "status in ('quarantined','blocked','mandatory_audit')",
            name="ck_infra_cross_tenant_hits_status",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_infra_cross_tenant_hits_payload_hash",
        ),
    )

    op.create_index(
        "ix_infra_secret_versions_tenant_status",
        "infra_secret_versions",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_infra_secret_leases_secret_generation",
        "infra_secret_leases",
        ["secret_ref", "generation"],
    )
    op.create_index(
        "ix_infra_cross_tenant_hits_resource",
        "infra_cross_tenant_hits",
        ["service_kind", "resource_ref", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_infra_cross_tenant_hits_resource",
        table_name="infra_cross_tenant_hits",
    )
    op.drop_index(
        "ix_infra_secret_leases_secret_generation",
        table_name="infra_secret_leases",
    )
    op.drop_index(
        "ix_infra_secret_versions_tenant_status",
        table_name="infra_secret_versions",
    )
    op.drop_table("infra_cross_tenant_hits")
    op.drop_table("infra_secret_leases")
    op.drop_table("infra_secret_rotation_heads")
    op.drop_table("infra_secret_versions")
