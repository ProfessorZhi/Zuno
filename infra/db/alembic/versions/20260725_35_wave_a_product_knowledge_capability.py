"""add wave a product knowledge capability owner facts

Revision ID: 20260725_35
Revises: 20260724_34
Create Date: 2026-07-25 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260725_35"
down_revision = "20260724_34"
branch_labels = None
depends_on = None


def _hash_check(column: str, name: str) -> sa.CheckConstraint:
    return sa.CheckConstraint(f"char_length({column}) = 64", name=name)


def upgrade() -> None:
    op.create_table(
        "product_agent_definitions",
        sa.Column("agent_definition_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("owner_principal_id", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("aggregate_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "display_name", name="uq_product_agent_definitions_name"),
        sa.CheckConstraint("aggregate_version > 0", name="ck_product_agent_definitions_version"),
        sa.CheckConstraint("status in ('DRAFT','ACTIVE','ARCHIVED','REVOKED')", name="ck_product_agent_definitions_status"),
    )
    op.create_table(
        "product_agent_versions",
        sa.Column("agent_version_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("agent_definition_id", sa.String(length=180), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("config_hash", sa.String(length=64), nullable=False),
        sa.Column("primary_agent_core_profile_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_definition_id"], ["product_agent_definitions.agent_definition_id"], name="fk_product_agent_versions_definition"),
        sa.UniqueConstraint("agent_definition_id", "version_no", name="uq_product_agent_versions_no"),
        _hash_check("config_hash", "ck_product_agent_versions_config_hash"),
        sa.CheckConstraint("version_no > 0", name="ck_product_agent_versions_no"),
        sa.CheckConstraint("status in ('DRAFT','PUBLISHED','REVOKED','SUPERSEDED')", name="ck_product_agent_versions_status"),
    )
    op.create_table(
        "product_conversation_threads",
        sa.Column("conversation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("principal_id", sa.String(length=120), nullable=False),
        sa.Column("active_agent_version_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["active_agent_version_id"], ["product_agent_versions.agent_version_id"], name="fk_product_conversations_agent_version"),
        sa.CheckConstraint("status in ('OPEN','ARCHIVED','DELETED')", name="ck_product_conversations_status"),
    )
    op.create_table(
        "product_submissions",
        sa.Column("submission_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("conversation_id", sa.String(length=180), nullable=False),
        sa.Column("client_request_id", sa.String(length=180), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("raw_intent_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["product_conversation_threads.conversation_id"], name="fk_product_submissions_conversation"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "client_request_id", name="uq_product_submissions_idempotency"),
        _hash_check("request_hash", "ck_product_submissions_request_hash"),
        sa.CheckConstraint("status in ('RECEIVED','ACCEPTED','REJECTED')", name="ck_product_submissions_status"),
    )
    op.create_table(
        "product_commands",
        sa.Column("command_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("submission_id", sa.String(length=180), nullable=False),
        sa.Column("command_kind", sa.String(length=80), nullable=False),
        sa.Column("owner_module", sa.String(length=80), nullable=False),
        sa.Column("runtime_request_ref", sa.String(length=240), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("journal_sequence_no", sa.Integer(), nullable=False),
        sa.Column("outbox_message_id", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["product_submissions.submission_id"], name="fk_product_commands_submission"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "journal_sequence_no", name="uq_product_commands_journal"),
        sa.UniqueConstraint("tenant_id", "outbox_message_id", name="uq_product_commands_outbox"),
        _hash_check("payload_hash", "ck_product_commands_payload_hash"),
        sa.CheckConstraint("journal_sequence_no > 0", name="ck_product_commands_journal_positive"),
        sa.CheckConstraint("owner_module in ('Agent Core','Input','Memory','Security')", name="ck_product_commands_owner"),
        sa.CheckConstraint("status in ('DISPATCH_COMMITTED','OWNER_ACCEPTED','OWNER_REJECTED','BLOCKED')", name="ck_product_commands_status"),
    )
    op.create_table(
        "product_command_receipts",
        sa.Column("receipt_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("command_id", sa.String(length=180), nullable=False),
        sa.Column("receipt_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("owner_receipt_ref", sa.String(length=240), nullable=True),
        sa.Column("receipt_hash", sa.String(length=64), nullable=False),
        sa.Column("domain_success_ref", sa.String(length=240), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["command_id"], ["product_commands.command_id"], name="fk_product_receipts_command"),
        sa.UniqueConstraint("command_id", "receipt_version", name="uq_product_receipts_append_only"),
        _hash_check("receipt_hash", "ck_product_receipts_hash"),
        sa.CheckConstraint("receipt_version > 0", name="ck_product_receipts_version"),
        sa.CheckConstraint("domain_success_ref is null", name="ck_product_receipts_not_domain_success"),
        sa.CheckConstraint("status in ('ACCEPTED','DUPLICATE','CONFLICT','REJECTED','BLOCKED','OWNER_TIMEOUT')", name="ck_product_receipts_status"),
    )
    op.create_table(
        "product_projection_events",
        sa.Column("projection_event_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("source_module", sa.String(length=80), nullable=False),
        sa.Column("source_event_id", sa.String(length=180), nullable=False),
        sa.Column("source_watermark", sa.Integer(), nullable=False),
        sa.Column("projection_hash", sa.String(length=64), nullable=False),
        sa.Column("redaction_decision_ref", sa.String(length=240), nullable=False),
        sa.Column("gap_detected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "source_module", "source_event_id", name="uq_product_projection_source_event"),
        _hash_check("projection_hash", "ck_product_projection_hash"),
        sa.CheckConstraint("source_watermark > 0", name="ck_product_projection_watermark"),
    )
    op.create_table(
        "product_action_tokens",
        sa.Column("action_token_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("principal_id", sa.String(length=120), nullable=False),
        sa.Column("target_ref", sa.String(length=240), nullable=False),
        sa.Column("command_kind", sa.String(length=80), nullable=False),
        sa.Column("effective_security_epoch_ref", sa.String(length=240), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("nonce", sa.String(length=120), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "nonce", name="uq_product_action_tokens_nonce"),
        _hash_check("token_hash", "ck_product_action_tokens_hash"),
    )
    op.create_table(
        "product_stream_cursors",
        sa.Column("cursor_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("principal_id", sa.String(length=120), nullable=False),
        sa.Column("projection_event_id", sa.String(length=180), nullable=False),
        sa.Column("last_sequence_no", sa.Integer(), nullable=False),
        sa.Column("effective_security_epoch_ref", sa.String(length=240), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reauthorized_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["projection_event_id"], ["product_projection_events.projection_event_id"], name="fk_product_stream_cursors_projection"),
        sa.CheckConstraint("last_sequence_no >= 0", name="ck_product_stream_cursors_sequence"),
    )

    op.create_table(
        "knowledge_domain_versions",
        sa.Column("knowledge_version_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("knowledge_space_id", sa.String(length=180), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("document_set_hash", sa.String(length=64), nullable=False),
        sa.Column("source_span_manifest_hash", sa.String(length=64), nullable=False),
        sa.Column("index_spec_hash", sa.String(length=64), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "knowledge_space_id", "version_no", name="uq_knowledge_versions_space_version"),
        _hash_check("document_set_hash", "ck_knowledge_versions_doc_hash"),
        _hash_check("source_span_manifest_hash", "ck_knowledge_versions_span_hash"),
        _hash_check("index_spec_hash", "ck_knowledge_versions_spec_hash"),
        sa.CheckConstraint("version_no > 0", name="ck_knowledge_versions_no"),
        sa.CheckConstraint("generation > 0", name="ck_knowledge_versions_generation"),
        sa.CheckConstraint("status in ('DRAFT','BUILDING','VERIFYING','READY','ACTIVE','SUPERSEDED','REVOKED','DELETED','FAILED')", name="ck_knowledge_versions_status"),
    )
    op.create_table(
        "knowledge_snapshots",
        sa.Column("snapshot_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("knowledge_version_id", sa.String(length=180), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("serving_watermark_ref", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_version_id"], ["knowledge_domain_versions.knowledge_version_id"], name="fk_knowledge_snapshots_version"),
        sa.UniqueConstraint("knowledge_version_id", "snapshot_hash", name="uq_knowledge_snapshots_version_hash"),
        _hash_check("snapshot_hash", "ck_knowledge_snapshots_hash"),
    )
    op.create_table(
        "knowledge_chunks",
        sa.Column("chunk_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("knowledge_version_id", sa.String(length=180), nullable=False),
        sa.Column("document_version_id", sa.String(length=180), nullable=False),
        sa.Column("source_span_ref", sa.String(length=240), nullable=False),
        sa.Column("chunk_hash", sa.String(length=64), nullable=False),
        sa.Column("acl_ref", sa.String(length=240), nullable=False),
        sa.Column("authority_ref", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_version_id"], ["knowledge_domain_versions.knowledge_version_id"], name="fk_knowledge_chunks_version"),
        sa.UniqueConstraint("knowledge_version_id", "source_span_ref", "chunk_hash", name="uq_knowledge_chunks_span_hash"),
        _hash_check("chunk_hash", "ck_knowledge_chunks_hash"),
    )
    op.create_table(
        "knowledge_index_build_jobs",
        sa.Column("job_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("knowledge_version_id", sa.String(length=180), nullable=False),
        sa.Column("index_kind", sa.String(length=40), nullable=False),
        sa.Column("lease_ref", sa.String(length=240), nullable=False),
        sa.Column("fencing_token", sa.Integer(), nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("write_batch_hash", sa.String(length=64), nullable=False),
        sa.Column("visibility_receipt_ref", sa.String(length=240), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_version_id"], ["knowledge_domain_versions.knowledge_version_id"], name="fk_knowledge_index_jobs_version"),
        sa.UniqueConstraint("knowledge_version_id", "index_kind", "attempt_no", name="uq_knowledge_index_jobs_attempt"),
        _hash_check("write_batch_hash", "ck_knowledge_index_jobs_batch_hash"),
        sa.CheckConstraint("index_kind in ('BM25','VECTOR','GRAPH')", name="ck_knowledge_index_jobs_kind"),
        sa.CheckConstraint("fencing_token > 0 and attempt_no > 0", name="ck_knowledge_index_jobs_attempt_positive"),
        sa.CheckConstraint("status in ('LEASED','WRITING','VERIFYING','VISIBLE','FAILED','STALE_FENCE')", name="ck_knowledge_index_jobs_status"),
    )
    op.create_table(
        "knowledge_cutover_decisions",
        sa.Column("cutover_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("knowledge_space_id", sa.String(length=180), nullable=False),
        sa.Column("from_version_id", sa.String(length=180), nullable=True),
        sa.Column("to_version_id", sa.String(length=180), nullable=False),
        sa.Column("expected_generation", sa.Integer(), nullable=False),
        sa.Column("committed_generation", sa.Integer(), nullable=False),
        sa.Column("decision_hash", sa.String(length=64), nullable=False),
        sa.Column("rollback_of_cutover_id", sa.String(length=180), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["to_version_id"], ["knowledge_domain_versions.knowledge_version_id"], name="fk_knowledge_cutovers_to_version"),
        sa.UniqueConstraint("tenant_id", "knowledge_space_id", "committed_generation", name="uq_knowledge_cutovers_generation"),
        _hash_check("decision_hash", "ck_knowledge_cutovers_hash"),
        sa.CheckConstraint("committed_generation = expected_generation + 1", name="ck_knowledge_cutovers_cas"),
    )
    op.create_table(
        "knowledge_query_runs",
        sa.Column("query_run_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("agent_core_decision_ref", sa.String(length=240), nullable=False),
        sa.Column("snapshot_id", sa.String(length=180), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["knowledge_snapshots.snapshot_id"], name="fk_knowledge_query_runs_snapshot"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "request_hash", name="uq_knowledge_query_runs_request"),
        _hash_check("request_hash", "ck_knowledge_query_runs_hash"),
        sa.CheckConstraint("status in ('RUNNING','SUFFICIENT_EVIDENCE','PARTIAL_EVIDENCE','CONTROL_PROPOSAL','FAILED','CANCELLED')", name="ck_knowledge_query_runs_status"),
    )
    op.create_table(
        "knowledge_retrieval_rounds",
        sa.Column("round_id", sa.String(length=180), primary_key=True),
        sa.Column("query_run_id", sa.String(length=180), nullable=False),
        sa.Column("round_no", sa.Integer(), nullable=False),
        sa.Column("retriever_set_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["query_run_id"], ["knowledge_query_runs.query_run_id"], name="fk_knowledge_rounds_query_run"),
        sa.UniqueConstraint("query_run_id", "round_no", name="uq_knowledge_rounds_no"),
        _hash_check("retriever_set_hash", "ck_knowledge_rounds_hash"),
        sa.CheckConstraint("round_no > 0", name="ck_knowledge_rounds_no_positive"),
    )
    op.create_table(
        "knowledge_evidence_records",
        sa.Column("evidence_id", sa.String(length=180), primary_key=True),
        sa.Column("query_run_id", sa.String(length=180), nullable=False),
        sa.Column("round_id", sa.String(length=180), nullable=False),
        sa.Column("chunk_id", sa.String(length=180), nullable=False),
        sa.Column("source_span_ref", sa.String(length=240), nullable=False),
        sa.Column("evidence_hash", sa.String(length=64), nullable=False),
        sa.Column("citation_eligibility", sa.String(length=40), nullable=False),
        sa.Column("selection_status", sa.String(length=40), nullable=False),
        sa.Column("authority_ref", sa.String(length=240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["query_run_id"], ["knowledge_query_runs.query_run_id"], name="fk_knowledge_evidence_query_run"),
        sa.ForeignKeyConstraint(["round_id"], ["knowledge_retrieval_rounds.round_id"], name="fk_knowledge_evidence_round"),
        sa.ForeignKeyConstraint(["chunk_id"], ["knowledge_chunks.chunk_id"], name="fk_knowledge_evidence_chunk"),
        sa.UniqueConstraint("query_run_id", "evidence_hash", name="uq_knowledge_evidence_hash"),
        _hash_check("evidence_hash", "ck_knowledge_evidence_hash"),
        sa.CheckConstraint("source_span_ref <> ''", name="ck_knowledge_evidence_source_span"),
        sa.CheckConstraint("citation_eligibility in ('STRICT','SUPPORTING','AUXILIARY_ONLY','REJECTED')", name="ck_knowledge_evidence_citation"),
    )
    op.create_table(
        "knowledge_citation_lineage",
        sa.Column("citation_lineage_id", sa.String(length=180), primary_key=True),
        sa.Column("evidence_id", sa.String(length=180), nullable=False),
        sa.Column("document_version_id", sa.String(length=180), nullable=False),
        sa.Column("source_span_ref", sa.String(length=240), nullable=False),
        sa.Column("span_text_hash", sa.String(length=64), nullable=False),
        sa.Column("authorization_ref", sa.String(length=240), nullable=False),
        sa.Column("deleted_or_tainted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["evidence_id"], ["knowledge_evidence_records.evidence_id"], name="fk_knowledge_citation_evidence"),
        _hash_check("span_text_hash", "ck_knowledge_citation_span_hash"),
    )

    op.create_table(
        "capability_definitions",
        sa.Column("capability_definition_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("semantic_identity", sa.String(length=240), nullable=False),
        sa.Column("owner_module", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "semantic_identity", name="uq_capability_definitions_identity"),
        sa.CheckConstraint("owner_module in ('Knowledge','Memory','Input','Tool Runtime','Artifact','Domain')", name="ck_capability_definitions_owner"),
        sa.CheckConstraint("status in ('DRAFT','ACTIVE','DEPRECATED','REVOKED')", name="ck_capability_definitions_status"),
    )
    op.create_table(
        "capability_versions",
        sa.Column("capability_version_id", sa.String(length=180), primary_key=True),
        sa.Column("capability_definition_id", sa.String(length=180), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("input_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("output_schema_hash", sa.String(length=64), nullable=False),
        sa.Column("risk_profile_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["capability_definition_id"], ["capability_definitions.capability_definition_id"], name="fk_capability_versions_definition"),
        sa.UniqueConstraint("capability_definition_id", "version_no", name="uq_capability_versions_no"),
        _hash_check("input_schema_hash", "ck_capability_versions_input_hash"),
        _hash_check("output_schema_hash", "ck_capability_versions_output_hash"),
        sa.CheckConstraint("version_no > 0", name="ck_capability_versions_no"),
    )
    op.create_table(
        "skill_versions",
        sa.Column("skill_version_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("skill_identity", sa.String(length=240), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("metadata_hash", sa.String(length=64), nullable=False),
        sa.Column("instruction_hash", sa.String(length=64), nullable=False),
        sa.Column("resource_manifest_hash", sa.String(length=64), nullable=False),
        sa.Column("signature_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "skill_identity", "version_no", name="uq_skill_versions_identity"),
        _hash_check("metadata_hash", "ck_skill_versions_metadata_hash"),
        _hash_check("instruction_hash", "ck_skill_versions_instruction_hash"),
        _hash_check("resource_manifest_hash", "ck_skill_versions_manifest_hash"),
        sa.CheckConstraint("status in ('DRAFT','VERIFIED','ACTIVE','QUARANTINED','REVOKED')", name="ck_skill_versions_status"),
    )
    op.create_table(
        "capability_provider_bindings",
        sa.Column("binding_id", sa.String(length=180), primary_key=True),
        sa.Column("capability_version_id", sa.String(length=180), nullable=False),
        sa.Column("provider_instance_ref", sa.String(length=240), nullable=False),
        sa.Column("tool_definition_ref", sa.String(length=240), nullable=False),
        sa.Column("binding_hash", sa.String(length=64), nullable=False),
        sa.Column("proposal_source", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["capability_version_id"], ["capability_versions.capability_version_id"], name="fk_capability_bindings_version"),
        sa.UniqueConstraint("capability_version_id", "provider_instance_ref", "tool_definition_ref", name="uq_capability_bindings_provider"),
        _hash_check("binding_hash", "ck_capability_bindings_hash"),
        sa.CheckConstraint("proposal_source in ('CURATED','RULE_DERIVED','MODEL_PROPOSED','IMPORTED_CONNECTOR_PACK')", name="ck_capability_bindings_source"),
        sa.CheckConstraint("status in ('PROPOSED','CONFORMANCE_PENDING','ACTIVE','REVOKED','FAILED')", name="ck_capability_bindings_status"),
        sa.CheckConstraint("not (proposal_source = 'MODEL_PROPOSED' and status = 'ACTIVE')", name="ck_capability_bindings_model_not_active"),
    )
    op.create_table(
        "capability_conformance_records",
        sa.Column("conformance_id", sa.String(length=180), primary_key=True),
        sa.Column("binding_id", sa.String(length=180), nullable=False),
        sa.Column("conformance_hash", sa.String(length=64), nullable=False),
        sa.Column("covers_input", sa.Boolean(), nullable=False),
        sa.Column("covers_output", sa.Boolean(), nullable=False),
        sa.Column("covers_idempotency", sa.Boolean(), nullable=False),
        sa.Column("covers_reconciliation", sa.Boolean(), nullable=False),
        sa.Column("covers_security", sa.Boolean(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["binding_id"], ["capability_provider_bindings.binding_id"], name="fk_capability_conformance_binding"),
        _hash_check("conformance_hash", "ck_capability_conformance_hash"),
        sa.CheckConstraint(
            "passed = (covers_input and covers_output and covers_idempotency and covers_reconciliation and covers_security)",
            name="ck_capability_conformance_passed_complete",
        ),
    )
    op.create_table(
        "capability_installations",
        sa.Column("installation_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("capability_version_id", sa.String(length=180), nullable=False),
        sa.Column("policy_ref", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["capability_version_id"], ["capability_versions.capability_version_id"], name="fk_capability_installations_version"),
        sa.UniqueConstraint("tenant_id", "workspace_id", "capability_version_id", name="uq_capability_installations_scope"),
    )
    op.create_table(
        "capability_availability_snapshots",
        sa.Column("snapshot_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("workspace_id", sa.String(length=120), nullable=False),
        sa.Column("principal_id", sa.String(length=120), nullable=False),
        sa.Column("security_epoch_ref", sa.String(length=240), nullable=False),
        sa.Column("source_generation", sa.Integer(), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("ttl_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "workspace_id", "principal_id", "snapshot_hash", name="uq_capability_snapshots_hash"),
        _hash_check("snapshot_hash", "ck_capability_snapshots_hash"),
    )
    op.create_table(
        "capability_selection_results",
        sa.Column("selection_id", sa.String(length=180), primary_key=True),
        sa.Column("snapshot_id", sa.String(length=180), nullable=False),
        sa.Column("requirement_hash", sa.String(length=64), nullable=False),
        sa.Column("selected_binding_id", sa.String(length=180), nullable=True),
        sa.Column("candidate_summary_hash", sa.String(length=64), nullable=False),
        sa.Column("rejection_reason_codes", sa.JSON(), nullable=False),
        sa.Column("selection_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["capability_availability_snapshots.snapshot_id"], name="fk_capability_selection_snapshot"),
        sa.ForeignKeyConstraint(["selected_binding_id"], ["capability_provider_bindings.binding_id"], name="fk_capability_selection_binding"),
        _hash_check("requirement_hash", "ck_capability_selection_requirement_hash"),
        _hash_check("candidate_summary_hash", "ck_capability_selection_candidate_hash"),
        _hash_check("selection_hash", "ck_capability_selection_hash"),
    )
    op.create_table(
        "capability_transition_events",
        sa.Column("transition_id", sa.String(length=180), primary_key=True),
        sa.Column("tenant_id", sa.String(length=120), nullable=False),
        sa.Column("aggregate_ref", sa.String(length=240), nullable=False),
        sa.Column("expected_generation", sa.Integer(), nullable=False),
        sa.Column("committed_generation", sa.Integer(), nullable=False),
        sa.Column("event_hash", sa.String(length=64), nullable=False),
        sa.Column("outbox_message_id", sa.String(length=180), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tenant_id", "outbox_message_id", name="uq_capability_transition_outbox"),
        _hash_check("event_hash", "ck_capability_transition_hash"),
        sa.CheckConstraint("committed_generation = expected_generation + 1", name="ck_capability_transition_cas"),
    )


def downgrade() -> None:
    op.drop_table("capability_transition_events")
    op.drop_table("capability_selection_results")
    op.drop_table("capability_availability_snapshots")
    op.drop_table("capability_installations")
    op.drop_table("capability_conformance_records")
    op.drop_table("capability_provider_bindings")
    op.drop_table("skill_versions")
    op.drop_table("capability_versions")
    op.drop_table("capability_definitions")
    op.drop_table("knowledge_citation_lineage")
    op.drop_table("knowledge_evidence_records")
    op.drop_table("knowledge_retrieval_rounds")
    op.drop_table("knowledge_query_runs")
    op.drop_table("knowledge_cutover_decisions")
    op.drop_table("knowledge_index_build_jobs")
    op.drop_table("knowledge_chunks")
    op.drop_table("knowledge_snapshots")
    op.drop_table("knowledge_domain_versions")
    op.drop_table("product_stream_cursors")
    op.drop_table("product_action_tokens")
    op.drop_table("product_projection_events")
    op.drop_table("product_command_receipts")
    op.drop_table("product_commands")
    op.drop_table("product_submissions")
    op.drop_table("product_conversation_threads")
    op.drop_table("product_agent_versions")
    op.drop_table("product_agent_definitions")
