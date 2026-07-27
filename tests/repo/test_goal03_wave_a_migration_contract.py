from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260725_35_wave_a_product_knowledge_capability.py"
REPAIR_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260725_37_wave_a_product_runtime_dispatch.py"
PRODUCT_AGENT_ASSET_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260726_38_goal03_product_agent_publication_installation.py"
PRODUCT_AGENT_EDITOR_PAYLOAD_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260727_42_goal04_product_agent_editor_payloads.py"
CAPABILITY_SUPPLY_CHAIN_MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260726_39_capability_version_supply_chain.py"
PRODUCT_LATE_OWNER_RECEIPT_MIGRATION = (
    REPO_ROOT / "infra/db/alembic/versions/20260726_40_product_late_owner_receipt.py"
)


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


def test_goal03_wave_a_repair_migration_adds_product_message_fact() -> None:
    text = REPAIR_MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260725_37"' in text
    assert 'down_revision = "20260725_36"' in text
    assert "product_messages" in text
    assert "fk_product_messages_submission" in text
    assert "ck_product_messages_publication_boundary" in text


def test_goal03_wave_a_product_agent_asset_migration_adds_publication_installation_catalog() -> None:
    text = PRODUCT_AGENT_ASSET_MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260726_38"' in text
    assert 'down_revision = "20260725_37"' in text
    assert text.count("op.create_table(") == text.count("op.drop_table(")
    for fragment in (
        "product_agent_drafts",
        "product_agent_publications",
        "product_agent_installations",
        "product_agent_catalog_entries",
        "fk_product_agent_publications_version",
        "fk_product_agent_installations_version",
        "fk_product_agent_catalog_version",
        "ck_product_agent_publications_status",
        "ck_product_agent_installations_status",
        "ck_product_agent_catalog_status",
    ):
        assert fragment in text


def test_goal04_product_agent_editor_payload_migration_adds_json_snapshots() -> None:
    text = PRODUCT_AGENT_EDITOR_PAYLOAD_MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260727_42"' in text
    assert 'down_revision = "20260727_41"' in text
    assert "draft_payload_json" in text
    assert "configuration_json" in text


def test_goal03_wave_a_capability_version_supply_chain_migration_adds_verified_refs() -> None:
    text = CAPABILITY_SUPPLY_CHAIN_MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260726_39"' in text
    assert 'down_revision = "20260726_38"' in text
    for fragment in (
        "source_ref",
        "license_ref",
        "dependency_refs_hash",
        "runtime_requirement_refs_hash",
        "signature_ref",
        "verification_ref",
        "supply_chain_hash",
        "supply_chain_verified",
        "ck_capability_versions_verified_refs",
    ):
        assert fragment in text


def test_goal03_wave_a_product_late_owner_receipt_migration_extends_receipt_status() -> None:
    text = PRODUCT_LATE_OWNER_RECEIPT_MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260726_40"' in text
    assert 'down_revision = "20260726_39"' in text
    assert "ck_product_receipts_status" in text
    assert "LATE_OWNER_RECEIPT" in text
