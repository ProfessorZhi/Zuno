from __future__ import annotations

DOMAIN_TABLE_OWNERS = {
    "agent": "Product Surface",
    "agent_runtime_checkpoints": "Agent Core / Planning & Control",
    "agent_runtime_events": "Agent Core / Planning & Control",
    "agent_runtime_interrupts": "Agent Core / Planning & Control",
    "agent_runtime_runs": "Agent Core / Planning & Control",
    "agent_skill": "Capability / Skill",
    "dialog": "Product Surface",
    "history": "Product Surface",
    "knowledge": "Knowledge / Retrieval",
    "knowledge_file": "Input / Document Ingestion",
    "knowledge_task": "Input / Document Ingestion",
    "knowledge_task_event": "Input / Document Ingestion",
    "llm": "Model Gateway",
    "mcp_agent": "Capability / Skill",
    "mcp_server": "Tool Execution",
    "mcp_stdio_server": "Tool Execution",
    "mcp_user_config": "Tool Execution",
    "memory_candidate": "Memory / Context",
    "memory_governance_ledger": "Memory / Context",
    "memory_history": "Memory / Context",
    "memory_raw_event": "Memory / Context",
    "memory_review_decision": "Memory / Context",
    "memory_task_summary": "Memory / Context",
    "message_down": "Product Surface",
    "message_like": "Product Surface",
    "role": "Security",
    "tool": "Tool Execution",
    "usage_stats": "Observability / Eval",
    "user": "Security",
    "user_role": "Security",
    "workspace_session": "Product Surface",
}

INFRASTRUCTURE_TABLES = {
    "infra_active_snapshot_refs",
    "infra_audit_channels",
    "infra_capacity_admissions",
    "infra_capacity_reservations",
    "infra_checkpoints",
    "infra_cutover_snapshots",
    "infra_cutover_targets",
    "infra_delivery_watermarks",
    "infra_idempotency_claims",
    "infra_inbox_messages",
    "infra_migration_backfill_chunks",
    "infra_migration_backfills",
    "infra_mandatory_audit_events",
    "infra_object_manifests",
    "infra_outbox_events",
    "infra_outbox_sequences",
    "infra_worker_leases",
}

REVISION_OWNERS = {
    "20260417_01": "Cross-module frozen baseline",
    "20260715_04": "Infrastructure",
    "20260716_05": "Infrastructure",
    "20260717_06": "Infrastructure",
    "20260717_07": "Infrastructure",
    "20260717_08": "Infrastructure",
    "20260717_09": "Product Surface",
    "20260717_10": "Infrastructure",
    "20260718_11": "Infrastructure",
    "20260718_12": "Infrastructure",
    "20260718_13": "Infrastructure",
}

ONLINE_SCHEMA_OBJECTS = {
    "ck_infra_migration_backfills_owner_nonempty",
    "ix_workspace_session_user_update_time",
}

__all__ = [
    "DOMAIN_TABLE_OWNERS",
    "INFRASTRUCTURE_TABLES",
    "ONLINE_SCHEMA_OBJECTS",
    "REVISION_OWNERS",
]
