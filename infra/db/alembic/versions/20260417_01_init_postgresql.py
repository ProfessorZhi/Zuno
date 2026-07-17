"""initialize the frozen PostgreSQL domain schema

Revision ID: 20260417_01
Revises:
Create Date: 2026-04-17 03:30:00
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision = "20260417_01"
down_revision = None
branch_labels = None
depends_on = None


# This revision is intentionally explicit. Runtime metadata must never mutate
# the historical baseline after PHASE04 freezes the chain.
def upgrade() -> None:
    op.create_table(
        "agent",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("logo_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.Column("system_prompt", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("llm_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("enable_memory", sa.Boolean(), nullable=False),
        sa.Column("mcp_ids", sa.JSON(), nullable=True),
        sa.Column("tool_ids", sa.JSON(), nullable=True),
        sa.Column("agent_skill_ids", sa.JSON(), nullable=True),
        sa.Column("knowledge_ids", sa.JSON(), nullable=True),
        sa.Column("domain_pack_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_user_id"), "agent", ["user_id"], unique=False)
    op.create_table(
        "agent_runtime_checkpoints",
        sa.Column("checkpoint_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("trace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("node", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("route", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state_version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state_json", sa.JSON(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("checkpoint_id"),
    )
    op.create_index(
        op.f("ix_agent_runtime_checkpoints_node"),
        "agent_runtime_checkpoints",
        ["node"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_checkpoints_task_id"),
        "agent_runtime_checkpoints",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_checkpoints_thread_id"),
        "agent_runtime_checkpoints",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_checkpoints_trace_id"),
        "agent_runtime_checkpoints",
        ["trace_id"],
        unique=False,
    )
    op.create_table(
        "agent_runtime_events",
        sa.Column("event_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("trace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("node", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("timestamp", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        op.f("ix_agent_runtime_events_node"),
        "agent_runtime_events",
        ["node"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_events_sequence"),
        "agent_runtime_events",
        ["sequence"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_events_status"),
        "agent_runtime_events",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_events_task_id"),
        "agent_runtime_events",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_events_thread_id"),
        "agent_runtime_events",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_events_timestamp"),
        "agent_runtime_events",
        ["timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_events_trace_id"),
        "agent_runtime_events",
        ["trace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_events_type"),
        "agent_runtime_events",
        ["type"],
        unique=False,
    )
    op.create_table(
        "agent_runtime_interrupts",
        sa.Column("interrupt_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("trace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("node", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("reason", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "required_approval", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("resumable", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("interrupt_id"),
    )
    op.create_index(
        op.f("ix_agent_runtime_interrupts_node"),
        "agent_runtime_interrupts",
        ["node"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_interrupts_status"),
        "agent_runtime_interrupts",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_interrupts_task_id"),
        "agent_runtime_interrupts",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_interrupts_thread_id"),
        "agent_runtime_interrupts",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_interrupts_trace_id"),
        "agent_runtime_interrupts",
        ["trace_id"],
        unique=False,
    )
    op.create_table(
        "agent_runtime_runs",
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("run_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("trace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("workspace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state_version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state_json", sa.JSON(), nullable=True),
        sa.Column("checkpoint_ids_json", sa.JSON(), nullable=True),
        sa.Column(
            "latest_checkpoint_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "pending_interrupt_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("failure_json", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("task_id"),
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_latest_checkpoint_id"),
        "agent_runtime_runs",
        ["latest_checkpoint_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_pending_interrupt_id"),
        "agent_runtime_runs",
        ["pending_interrupt_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_run_id"),
        "agent_runtime_runs",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_status"),
        "agent_runtime_runs",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_thread_id"),
        "agent_runtime_runs",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_trace_id"),
        "agent_runtime_runs",
        ["trace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_user_id"),
        "agent_runtime_runs",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_agent_runtime_runs_workspace_id"),
        "agent_runtime_runs",
        ["workspace_id"],
        unique=False,
    )
    op.create_table(
        "agent_skill",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("as_tool_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("folder", sa.JSON(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dialog",
        sa.Column("dialog_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("agent_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("agent_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("dialog_id"),
    )
    op.create_table(
        "history",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("dialog_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("events", sa.JSON(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "knowledge",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=128), nullable=False),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(length=1024), nullable=True
        ),
        sa.Column(
            "default_retrieval_mode",
            sqlmodel.sql.sqltypes.AutoString(length=32),
            nullable=False,
        ),
        sa.Column("knowledge_config", sa.JSON(), nullable=False),
        sa.Column(
            "user_id", sqlmodel.sql.sqltypes.AutoString(length=128), nullable=True
        ),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_name"), "knowledge", ["name"], unique=True)
    op.create_index(
        op.f("ix_knowledge_user_id"), "knowledge", ["user_id"], unique=False
    )
    op.create_table(
        "knowledge_file",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("file_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("knowledge_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("parse_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "rag_index_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "graph_index_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("last_task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "last_error", sqlmodel.sql.sqltypes.AutoString(length=2048), nullable=True
        ),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("oss_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_knowledge_file_file_name"),
        "knowledge_file",
        ["file_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_file_knowledge_id"),
        "knowledge_file",
        ["knowledge_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_file_last_task_id"),
        "knowledge_file",
        ["last_task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_file_user_id"), "knowledge_file", ["user_id"], unique=False
    )
    op.create_table(
        "knowledge_task",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("knowledge_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "knowledge_file_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("task_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("current_stage", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column(
            "error_message",
            sqlmodel.sql.sqltypes.AutoString(length=2048),
            nullable=True,
        ),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("result_summary", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_knowledge_task_current_stage"),
        "knowledge_task",
        ["current_stage"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_task_knowledge_file_id"),
        "knowledge_task",
        ["knowledge_file_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_task_knowledge_id"),
        "knowledge_task",
        ["knowledge_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_task_status"), "knowledge_task", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_knowledge_task_task_type"),
        "knowledge_task",
        ["task_type"],
        unique=False,
    )
    op.create_table(
        "knowledge_task_event",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("stage", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "message", sqlmodel.sql.sqltypes.AutoString(length=1024), nullable=False
        ),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_knowledge_task_event_stage"),
        "knowledge_task_event",
        ["stage"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_task_event_status"),
        "knowledge_task_event",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_knowledge_task_event_task_id"),
        "knowledge_task_event",
        ["task_id"],
        unique=False,
    )
    op.create_table(
        "llm",
        sa.Column("llm_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("llm_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("model", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("base_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("api_key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("provider", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("model_slot", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("llm_id"),
    )
    op.create_table(
        "mcp_agent",
        sa.Column("mcp_agent_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("mcp_server_id", sa.JSON(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("logo_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("mcp_agent_id"),
    )
    op.create_index(
        op.f("ix_mcp_agent_user_id"), "mcp_agent", ["user_id"], unique=False
    )
    op.create_table(
        "mcp_server",
        sa.Column("mcp_server_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("server_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "mcp_as_tool_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("type", sa.VARCHAR(length=255), nullable=False),
        sa.Column("logo_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("tools", sa.JSON(), nullable=True),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("imported_config", sa.JSON(), nullable=True),
        sa.Column("config_enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("mcp_server_id"),
    )
    op.create_table(
        "mcp_stdio_server",
        sa.Column("mcp_server_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "mcp_server_path", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "mcp_server_command", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("mcp_server_env", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("mcp_server_id"),
    )
    op.create_table(
        "mcp_user_config",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("mcp_server_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "memory_candidate",
        sa.Column("candidate_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("agent_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("project_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("layer", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_event_ids", sa.JSON(), nullable=True),
        sa.Column("dedupe_key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("retention_policy", sa.JSON(), nullable=True),
        sa.Column("review_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("requires_review", sa.Boolean(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("candidate_id"),
    )
    op.create_index(
        op.f("ix_memory_candidate_agent_id"),
        "memory_candidate",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_candidate_dedupe_key"),
        "memory_candidate",
        ["dedupe_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_candidate_layer"), "memory_candidate", ["layer"], unique=False
    )
    op.create_index(
        op.f("ix_memory_candidate_project_id"),
        "memory_candidate",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_candidate_requires_review"),
        "memory_candidate",
        ["requires_review"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_candidate_review_status"),
        "memory_candidate",
        ["review_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_candidate_thread_id"),
        "memory_candidate",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_candidate_user_id"),
        "memory_candidate",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "memory_governance_ledger",
        sa.Column("entry_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("action", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("agent_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("project_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("trace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_event_ids", sa.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("entry_id"),
    )
    op.create_index(
        op.f("ix_memory_governance_ledger_action"),
        "memory_governance_ledger",
        ["action"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_governance_ledger_agent_id"),
        "memory_governance_ledger",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_governance_ledger_project_id"),
        "memory_governance_ledger",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_governance_ledger_task_id"),
        "memory_governance_ledger",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_governance_ledger_thread_id"),
        "memory_governance_ledger",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_governance_ledger_trace_id"),
        "memory_governance_ledger",
        ["trace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_governance_ledger_user_id"),
        "memory_governance_ledger",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "memory_history",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("memory_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("old_memory", sa.Text(), nullable=True),
        sa.Column("new_memory", sa.Text(), nullable=True),
        sa.Column("event", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("actor_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "memory_raw_event",
        sa.Column("event_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("agent_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("project_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("trace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("event_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("layer", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        op.f("ix_memory_raw_event_agent_id"),
        "memory_raw_event",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_raw_event_event_type"),
        "memory_raw_event",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_raw_event_layer"), "memory_raw_event", ["layer"], unique=False
    )
    op.create_index(
        op.f("ix_memory_raw_event_project_id"),
        "memory_raw_event",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_raw_event_task_id"),
        "memory_raw_event",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_raw_event_thread_id"),
        "memory_raw_event",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_raw_event_trace_id"),
        "memory_raw_event",
        ["trace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_raw_event_user_id"),
        "memory_raw_event",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "memory_review_decision",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("candidate_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("reviewer_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("source_event_ids", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_memory_review_decision_candidate_id"),
        "memory_review_decision",
        ["candidate_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_review_decision_reviewer_id"),
        "memory_review_decision",
        ["reviewer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_review_decision_status"),
        "memory_review_decision",
        ["status"],
        unique=False,
    )
    op.create_table(
        "memory_task_summary",
        sa.Column("summary_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("agent_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("project_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("thread_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("layer", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("source_event_ids", sa.JSON(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("summary_id"),
    )
    op.create_index(
        op.f("ix_memory_task_summary_agent_id"),
        "memory_task_summary",
        ["agent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_task_summary_layer"),
        "memory_task_summary",
        ["layer"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_task_summary_project_id"),
        "memory_task_summary",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_task_summary_thread_id"),
        "memory_task_summary",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_memory_task_summary_user_id"),
        "memory_task_summary",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "message_down",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_input", sa.Text(), nullable=True),
        sa.Column("agent_output", sa.Text(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "message_like",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_input", sa.Text(), nullable=True),
        sa.Column("agent_output", sa.Text(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "role",
        sa.Column("role_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("remark", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_name", name="group_role_name_uniq"),
    )
    op.create_index(op.f("ix_role_create_time"), "role", ["create_time"], unique=False)
    op.create_table(
        "tool",
        sa.Column("tool_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("display_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("logo_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("openapi_schema", sa.JSON(), nullable=True),
        sa.Column("is_user_defined", sa.Boolean(), nullable=False),
        sa.Column("auth_config", sa.JSON(), nullable=True),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("tool_id"),
    )
    op.create_table(
        "usage_stats",
        sa.Column("agent", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("model", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_avatar", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "user_description", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("user_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("delete", sa.Boolean(), nullable=False),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_create_time"), "user", ["create_time"], unique=False)
    op.create_index(op.f("ix_user_user_name"), "user", ["user_name"], unique=True)
    op.create_table(
        "user_role",
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("role_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_role_role_id"), "user_role", ["role_id"], unique=False
    )
    op.create_index(
        op.f("ix_user_role_update_time"), "user_role", ["update_time"], unique=False
    )
    op.create_index(
        op.f("ix_user_role_user_id"), "user_role", ["user_id"], unique=False
    )
    op.create_table(
        "workspace_session",
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("agent", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("contexts", sa.JSON(), nullable=True),
        sa.Column("session_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "update_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "create_time",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )


def downgrade() -> None:
    op.drop_table("workspace_session")
    op.drop_index(op.f("ix_user_role_user_id"), table_name="user_role")
    op.drop_index(op.f("ix_user_role_update_time"), table_name="user_role")
    op.drop_index(op.f("ix_user_role_role_id"), table_name="user_role")
    op.drop_table("user_role")
    op.drop_index(op.f("ix_user_user_name"), table_name="user")
    op.drop_index(op.f("ix_user_create_time"), table_name="user")
    op.drop_table("user")
    op.drop_table("usage_stats")
    op.drop_table("tool")
    op.drop_index(op.f("ix_role_create_time"), table_name="role")
    op.drop_table("role")
    op.drop_table("message_like")
    op.drop_table("message_down")
    op.drop_index(
        op.f("ix_memory_task_summary_user_id"), table_name="memory_task_summary"
    )
    op.drop_index(
        op.f("ix_memory_task_summary_thread_id"), table_name="memory_task_summary"
    )
    op.drop_index(
        op.f("ix_memory_task_summary_project_id"), table_name="memory_task_summary"
    )
    op.drop_index(
        op.f("ix_memory_task_summary_layer"), table_name="memory_task_summary"
    )
    op.drop_index(
        op.f("ix_memory_task_summary_agent_id"), table_name="memory_task_summary"
    )
    op.drop_table("memory_task_summary")
    op.drop_index(
        op.f("ix_memory_review_decision_status"), table_name="memory_review_decision"
    )
    op.drop_index(
        op.f("ix_memory_review_decision_reviewer_id"),
        table_name="memory_review_decision",
    )
    op.drop_index(
        op.f("ix_memory_review_decision_candidate_id"),
        table_name="memory_review_decision",
    )
    op.drop_table("memory_review_decision")
    op.drop_index(op.f("ix_memory_raw_event_user_id"), table_name="memory_raw_event")
    op.drop_index(op.f("ix_memory_raw_event_trace_id"), table_name="memory_raw_event")
    op.drop_index(op.f("ix_memory_raw_event_thread_id"), table_name="memory_raw_event")
    op.drop_index(op.f("ix_memory_raw_event_task_id"), table_name="memory_raw_event")
    op.drop_index(op.f("ix_memory_raw_event_project_id"), table_name="memory_raw_event")
    op.drop_index(op.f("ix_memory_raw_event_layer"), table_name="memory_raw_event")
    op.drop_index(op.f("ix_memory_raw_event_event_type"), table_name="memory_raw_event")
    op.drop_index(op.f("ix_memory_raw_event_agent_id"), table_name="memory_raw_event")
    op.drop_table("memory_raw_event")
    op.drop_table("memory_history")
    op.drop_index(
        op.f("ix_memory_governance_ledger_user_id"),
        table_name="memory_governance_ledger",
    )
    op.drop_index(
        op.f("ix_memory_governance_ledger_trace_id"),
        table_name="memory_governance_ledger",
    )
    op.drop_index(
        op.f("ix_memory_governance_ledger_thread_id"),
        table_name="memory_governance_ledger",
    )
    op.drop_index(
        op.f("ix_memory_governance_ledger_task_id"),
        table_name="memory_governance_ledger",
    )
    op.drop_index(
        op.f("ix_memory_governance_ledger_project_id"),
        table_name="memory_governance_ledger",
    )
    op.drop_index(
        op.f("ix_memory_governance_ledger_agent_id"),
        table_name="memory_governance_ledger",
    )
    op.drop_index(
        op.f("ix_memory_governance_ledger_action"),
        table_name="memory_governance_ledger",
    )
    op.drop_table("memory_governance_ledger")
    op.drop_index(op.f("ix_memory_candidate_user_id"), table_name="memory_candidate")
    op.drop_index(op.f("ix_memory_candidate_thread_id"), table_name="memory_candidate")
    op.drop_index(
        op.f("ix_memory_candidate_review_status"), table_name="memory_candidate"
    )
    op.drop_index(
        op.f("ix_memory_candidate_requires_review"), table_name="memory_candidate"
    )
    op.drop_index(op.f("ix_memory_candidate_project_id"), table_name="memory_candidate")
    op.drop_index(op.f("ix_memory_candidate_layer"), table_name="memory_candidate")
    op.drop_index(op.f("ix_memory_candidate_dedupe_key"), table_name="memory_candidate")
    op.drop_index(op.f("ix_memory_candidate_agent_id"), table_name="memory_candidate")
    op.drop_table("memory_candidate")
    op.drop_table("mcp_user_config")
    op.drop_table("mcp_stdio_server")
    op.drop_table("mcp_server")
    op.drop_index(op.f("ix_mcp_agent_user_id"), table_name="mcp_agent")
    op.drop_table("mcp_agent")
    op.drop_table("llm")
    op.drop_index(
        op.f("ix_knowledge_task_event_task_id"), table_name="knowledge_task_event"
    )
    op.drop_index(
        op.f("ix_knowledge_task_event_status"), table_name="knowledge_task_event"
    )
    op.drop_index(
        op.f("ix_knowledge_task_event_stage"), table_name="knowledge_task_event"
    )
    op.drop_table("knowledge_task_event")
    op.drop_index(op.f("ix_knowledge_task_task_type"), table_name="knowledge_task")
    op.drop_index(op.f("ix_knowledge_task_status"), table_name="knowledge_task")
    op.drop_index(op.f("ix_knowledge_task_knowledge_id"), table_name="knowledge_task")
    op.drop_index(
        op.f("ix_knowledge_task_knowledge_file_id"), table_name="knowledge_task"
    )
    op.drop_index(op.f("ix_knowledge_task_current_stage"), table_name="knowledge_task")
    op.drop_table("knowledge_task")
    op.drop_index(op.f("ix_knowledge_file_user_id"), table_name="knowledge_file")
    op.drop_index(op.f("ix_knowledge_file_last_task_id"), table_name="knowledge_file")
    op.drop_index(op.f("ix_knowledge_file_knowledge_id"), table_name="knowledge_file")
    op.drop_index(op.f("ix_knowledge_file_file_name"), table_name="knowledge_file")
    op.drop_table("knowledge_file")
    op.drop_index(op.f("ix_knowledge_user_id"), table_name="knowledge")
    op.drop_index(op.f("ix_knowledge_name"), table_name="knowledge")
    op.drop_table("knowledge")
    op.drop_table("history")
    op.drop_table("dialog")
    op.drop_table("agent_skill")
    op.drop_index(
        op.f("ix_agent_runtime_runs_workspace_id"), table_name="agent_runtime_runs"
    )
    op.drop_index(
        op.f("ix_agent_runtime_runs_user_id"), table_name="agent_runtime_runs"
    )
    op.drop_index(
        op.f("ix_agent_runtime_runs_trace_id"), table_name="agent_runtime_runs"
    )
    op.drop_index(
        op.f("ix_agent_runtime_runs_thread_id"), table_name="agent_runtime_runs"
    )
    op.drop_index(op.f("ix_agent_runtime_runs_status"), table_name="agent_runtime_runs")
    op.drop_index(op.f("ix_agent_runtime_runs_run_id"), table_name="agent_runtime_runs")
    op.drop_index(
        op.f("ix_agent_runtime_runs_pending_interrupt_id"),
        table_name="agent_runtime_runs",
    )
    op.drop_index(
        op.f("ix_agent_runtime_runs_latest_checkpoint_id"),
        table_name="agent_runtime_runs",
    )
    op.drop_table("agent_runtime_runs")
    op.drop_index(
        op.f("ix_agent_runtime_interrupts_trace_id"),
        table_name="agent_runtime_interrupts",
    )
    op.drop_index(
        op.f("ix_agent_runtime_interrupts_thread_id"),
        table_name="agent_runtime_interrupts",
    )
    op.drop_index(
        op.f("ix_agent_runtime_interrupts_task_id"),
        table_name="agent_runtime_interrupts",
    )
    op.drop_index(
        op.f("ix_agent_runtime_interrupts_status"),
        table_name="agent_runtime_interrupts",
    )
    op.drop_index(
        op.f("ix_agent_runtime_interrupts_node"), table_name="agent_runtime_interrupts"
    )
    op.drop_table("agent_runtime_interrupts")
    op.drop_index(
        op.f("ix_agent_runtime_events_type"), table_name="agent_runtime_events"
    )
    op.drop_index(
        op.f("ix_agent_runtime_events_trace_id"), table_name="agent_runtime_events"
    )
    op.drop_index(
        op.f("ix_agent_runtime_events_timestamp"), table_name="agent_runtime_events"
    )
    op.drop_index(
        op.f("ix_agent_runtime_events_thread_id"), table_name="agent_runtime_events"
    )
    op.drop_index(
        op.f("ix_agent_runtime_events_task_id"), table_name="agent_runtime_events"
    )
    op.drop_index(
        op.f("ix_agent_runtime_events_status"), table_name="agent_runtime_events"
    )
    op.drop_index(
        op.f("ix_agent_runtime_events_sequence"), table_name="agent_runtime_events"
    )
    op.drop_index(
        op.f("ix_agent_runtime_events_node"), table_name="agent_runtime_events"
    )
    op.drop_table("agent_runtime_events")
    op.drop_index(
        op.f("ix_agent_runtime_checkpoints_trace_id"),
        table_name="agent_runtime_checkpoints",
    )
    op.drop_index(
        op.f("ix_agent_runtime_checkpoints_thread_id"),
        table_name="agent_runtime_checkpoints",
    )
    op.drop_index(
        op.f("ix_agent_runtime_checkpoints_task_id"),
        table_name="agent_runtime_checkpoints",
    )
    op.drop_index(
        op.f("ix_agent_runtime_checkpoints_node"),
        table_name="agent_runtime_checkpoints",
    )
    op.drop_table("agent_runtime_checkpoints")
    op.drop_index(op.f("ix_agent_user_id"), table_name="agent")
    op.drop_table("agent")
