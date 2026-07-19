"""add security control plane durable facts

Revision ID: 20260719_16
Revises: 20260718_15
Create Date: 2026-07-19 16:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260719_16"
down_revision = "20260718_15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "security_principal_contexts",
        sa.Column("principal_context_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("user_principal_id", sa.String(length=160), nullable=False),
        sa.Column("agent_principal_id", sa.String(length=160), nullable=True),
        sa.Column("task_principal_id", sa.String(length=160), nullable=True),
        sa.Column("session_principal_id", sa.String(length=160), nullable=True),
        sa.Column("run_id", sa.String(length=160), nullable=True),
        sa.Column("epoch_ref", sa.String(length=160), nullable=False),
        sa.Column("context_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(context_hash) = 64",
            name="ck_security_principal_contexts_context_hash",
        ),
        sa.CheckConstraint(
            "status in ('active','expired','revoked')",
            name="ck_security_principal_contexts_status",
        ),
    )

    op.create_table(
        "security_effective_epochs",
        sa.Column("epoch_ref", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("policy_bundle_ref", sa.String(length=240), nullable=False),
        sa.Column("policy_bundle_hash", sa.String(length=64), nullable=False),
        sa.Column("action_set_version", sa.String(length=80), nullable=False),
        sa.Column("principal_context_hash", sa.String(length=64), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(policy_bundle_hash) = 64",
            name="ck_security_effective_epochs_policy_hash",
        ),
        sa.CheckConstraint(
            "length(principal_context_hash) = 64",
            name="ck_security_effective_epochs_context_hash",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_security_effective_epochs_generation",
        ),
        sa.CheckConstraint(
            "status in ('active','superseded','revoked')",
            name="ck_security_effective_epochs_status",
        ),
    )

    op.create_table(
        "security_authorization_decisions",
        sa.Column("decision_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("principal_context_id", sa.String(length=160), nullable=False),
        sa.Column("epoch_ref", sa.String(length=160), nullable=False),
        sa.Column("resource_ref", sa.String(length=240), nullable=False),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("reason_code", sa.String(length=128), nullable=False),
        sa.Column("prepared_action_hash", sa.String(length=64), nullable=True),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["principal_context_id"],
            ["security_principal_contexts.principal_context_id"],
            ondelete="RESTRICT",
            name="fk_security_authorization_decisions_context",
        ),
        sa.ForeignKeyConstraint(
            ["epoch_ref"],
            ["security_effective_epochs.epoch_ref"],
            ondelete="RESTRICT",
            name="fk_security_authorization_decisions_epoch",
        ),
        sa.CheckConstraint(
            "decision in ('DENY','USE_ONLY','USE_AND_DELEGATE','REQUIRES_APPROVAL')",
            name="ck_security_authorization_decisions_decision",
        ),
        sa.CheckConstraint(
            "prepared_action_hash IS NULL OR length(prepared_action_hash) = 64",
            name="ck_security_authorization_decisions_prepared_hash",
        ),
        sa.CheckConstraint(
            "length(decision_hash) = 64",
            name="ck_security_authorization_decisions_decision_hash",
        ),
    )

    op.create_table(
        "security_approval_requests",
        sa.Column("approval_request_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("decision_id", sa.String(length=160), nullable=False),
        sa.Column("prepared_action_hash", sa.String(length=64), nullable=False),
        sa.Column("requested_by_principal_id", sa.String(length=160), nullable=False),
        sa.Column("required_approver_policy_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["security_authorization_decisions.decision_id"],
            ondelete="RESTRICT",
            name="fk_security_approval_requests_decision",
        ),
        sa.CheckConstraint(
            "length(prepared_action_hash) = 64",
            name="ck_security_approval_requests_prepared_hash",
        ),
        sa.CheckConstraint(
            "status in ('pending','approved','denied','expired','cancelled')",
            name="ck_security_approval_requests_status",
        ),
    )

    op.create_table(
        "security_approval_decisions",
        sa.Column("approval_decision_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("approval_request_id", sa.String(length=160), nullable=False),
        sa.Column("approver_principal_id", sa.String(length=160), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["approval_request_id"],
            ["security_approval_requests.approval_request_id"],
            ondelete="RESTRICT",
            name="fk_security_approval_decisions_request",
        ),
        sa.UniqueConstraint(
            "approval_request_id",
            name="uq_security_approval_decisions_request",
        ),
        sa.CheckConstraint(
            "decision in ('approved','denied')",
            name="ck_security_approval_decisions_decision",
        ),
        sa.CheckConstraint(
            "length(decision_hash) = 64",
            name="ck_security_approval_decisions_decision_hash",
        ),
    )

    op.create_table(
        "security_secret_refs",
        sa.Column("secret_ref", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("credential_version_ref", sa.String(length=240), nullable=False),
        sa.Column("audience", sa.String(length=240), nullable=False),
        sa.Column("owner_principal_id", sa.String(length=160), nullable=False),
        sa.Column("scope_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(scope_hash) = 64",
            name="ck_security_secret_refs_scope_hash",
        ),
        sa.CheckConstraint(
            "status in ('active','rotating','revoked')",
            name="ck_security_secret_refs_status",
        ),
    )

    op.create_table(
        "security_secret_leases",
        sa.Column("lease_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("secret_ref", sa.String(length=160), nullable=False),
        sa.Column("workload_identity_ref", sa.String(length=240), nullable=False),
        sa.Column("on_behalf_of_binding_ref", sa.String(length=240), nullable=False),
        sa.Column("audience", sa.String(length=240), nullable=False),
        sa.Column("lease_generation", sa.Integer(), nullable=False),
        sa.Column("lease_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["secret_ref"],
            ["security_secret_refs.secret_ref"],
            ondelete="RESTRICT",
            name="fk_security_secret_leases_secret_ref",
        ),
        sa.CheckConstraint(
            "lease_generation > 0",
            name="ck_security_secret_leases_generation",
        ),
        sa.CheckConstraint(
            "length(lease_hash) = 64",
            name="ck_security_secret_leases_lease_hash",
        ),
    )

    op.create_table(
        "security_redaction_decisions",
        sa.Column("redaction_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("source_ref", sa.String(length=240), nullable=False),
        sa.Column("sink_ref", sa.String(length=240), nullable=False),
        sa.Column("trust_label", sa.String(length=80), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("redaction_policy_ref", sa.String(length=240), nullable=False),
        sa.Column("redacted_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "decision in ('allow','redact','block','declassify')",
            name="ck_security_redaction_decisions_decision",
        ),
        sa.CheckConstraint(
            "length(redacted_payload_hash) = 64",
            name="ck_security_redaction_decisions_payload_hash",
        ),
        sa.CheckConstraint(
            "length(decision_hash) = 64",
            name="ck_security_redaction_decisions_decision_hash",
        ),
    )

    op.create_table(
        "security_audit_requirements",
        sa.Column("audit_requirement_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("decision_id", sa.String(length=160), nullable=False),
        sa.Column("audit_channel_id", sa.String(length=160), nullable=False),
        sa.Column("requirement_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("effect_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["security_authorization_decisions.decision_id"],
            ondelete="RESTRICT",
            name="fk_security_audit_requirements_decision",
        ),
        sa.CheckConstraint(
            "length(requirement_hash) = 64",
            name="ck_security_audit_requirements_hash",
        ),
        sa.CheckConstraint(
            "status in ('required','durable','effect_observed','failed_closed')",
            name="ck_security_audit_requirements_status",
        ),
    )

    op.create_table(
        "security_outbox_events",
        sa.Column("event_id", sa.String(length=160), primary_key=True),
        sa.Column("tenant_id", sa.String(length=128), nullable=False),
        sa.Column("aggregate_id", sa.String(length=160), nullable=False),
        sa.Column("topic", sa.String(length=160), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_security_outbox_events_idempotency",
        ),
        sa.CheckConstraint(
            "length(payload_hash) = 64",
            name="ck_security_outbox_events_payload_hash",
        ),
        sa.CheckConstraint(
            "status in ('pending','claimed','published','dead_letter')",
            name="ck_security_outbox_events_status",
        ),
    )

    op.create_index(
        "ix_security_principal_contexts_tenant_status",
        "security_principal_contexts",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_security_authorization_decisions_context_action",
        "security_authorization_decisions",
        ["principal_context_id", "resource_ref", "action"],
    )
    op.create_index(
        "ix_security_approval_requests_status_deadline",
        "security_approval_requests",
        ["status", "deadline_at"],
    )
    op.create_index(
        "ix_security_secret_leases_secret_expiry",
        "security_secret_leases",
        ["secret_ref", "expires_at"],
    )
    op.create_index(
        "ix_security_audit_requirements_status",
        "security_audit_requirements",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_security_outbox_events_status",
        "security_outbox_events",
        ["tenant_id", "status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_security_outbox_events_status",
        table_name="security_outbox_events",
    )
    op.drop_index(
        "ix_security_audit_requirements_status",
        table_name="security_audit_requirements",
    )
    op.drop_index(
        "ix_security_secret_leases_secret_expiry",
        table_name="security_secret_leases",
    )
    op.drop_index(
        "ix_security_approval_requests_status_deadline",
        table_name="security_approval_requests",
    )
    op.drop_index(
        "ix_security_authorization_decisions_context_action",
        table_name="security_authorization_decisions",
    )
    op.drop_index(
        "ix_security_principal_contexts_tenant_status",
        table_name="security_principal_contexts",
    )
    op.drop_table("security_outbox_events")
    op.drop_table("security_audit_requirements")
    op.drop_table("security_redaction_decisions")
    op.drop_table("security_secret_leases")
    op.drop_table("security_secret_refs")
    op.drop_table("security_approval_decisions")
    op.drop_table("security_approval_requests")
    op.drop_table("security_authorization_decisions")
    op.drop_table("security_effective_epochs")
    op.drop_table("security_principal_contexts")
