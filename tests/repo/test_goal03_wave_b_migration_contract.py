from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260725_36_wave_b_memory_tool_runtime.py"


def test_goal03_wave_b_migration_is_append_only_single_head_successor() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260725_36"' in text
    assert 'down_revision = "20260725_35"' in text
    assert text.count("op.create_table(") == text.count("op.drop_table(")


def test_goal03_wave_b_migration_contains_memory_and_tool_owner_fact_tables() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "memory_versions",
        "memory_snapshots",
        "memory_manifest_snapshots",
        "context_pack_versions",
        "memory_deletion_requests",
        "memory_deletion_receipts",
        "memory_reconciliation_decisions",
        "ck_memory_versions_status",
        "ck_context_pack_budget_positive",
        "tool_providers",
        "tool_definitions",
        "tool_versions",
        "tool_operations",
        "tool_installations",
        "tool_activations",
        "prepared_tool_actions",
        "tool_attempts",
        "tool_observations",
        "tool_execution_receipts",
        "ck_tool_activations_cas",
        "uq_prepared_actions_idempotency",
    )

    for fragment in required_fragments:
        assert fragment in text
