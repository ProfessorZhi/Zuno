from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260725_35_wave_a_product_knowledge_capability.py"


def test_goal03_wave_a_migration_is_append_only_single_head_successor() -> None:
    text = MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260725_35"' in text
    assert 'down_revision = "20260724_34"' in text
    assert text.count("op.create_table(") == text.count("op.drop_table(")


def test_goal03_wave_a_migration_contains_owner_fact_tables_and_guards() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    required_fragments = (
        "product_agent_definitions",
        "product_commands",
        "product_command_receipts",
        "ck_product_receipts_not_domain_success",
        "product_projection_events",
        "product_action_tokens",
        "knowledge_domain_versions",
        "knowledge_snapshots",
        "knowledge_index_build_jobs",
        "knowledge_cutover_decisions",
        "ck_knowledge_cutovers_cas",
        "knowledge_query_runs",
        "knowledge_evidence_records",
        "knowledge_citation_lineage",
        "capability_definitions",
        "capability_versions",
        "skill_versions",
        "capability_provider_bindings",
        "ck_capability_bindings_model_not_active",
        "capability_conformance_records",
        "capability_availability_snapshots",
        "capability_selection_results",
        "capability_transition_events",
        "ck_capability_transition_cas",
    )

    for fragment in required_fragments:
        assert fragment in text
