from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260813_57_wave001_domain_mutation.py"
EXPECTED_TABLES = {
    "domain_aggregate_heads",
    "domain_mutation_records",
    "domain_state_versions",
}


def _load_migration_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wave001_domain_mutation_migration", MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _apply_revision_function(connection, schema: str, function_name: str) -> None:
    connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
    migration_context = MigrationContext.configure(connection)
    module = _load_migration_module()
    with Operations.context(migration_context):
        getattr(module, function_name)()


def _assert_upgraded_schema(engine, schema: str) -> None:
    inspector = inspect(engine)
    assert set(inspector.get_table_names(schema=schema)) == EXPECTED_TABLES

    mutation_unique_names = {
        item["name"]
        for item in inspector.get_unique_constraints("domain_mutation_records", schema=schema)
    }
    state_unique_names = {
        item["name"]
        for item in inspector.get_unique_constraints("domain_state_versions", schema=schema)
    }
    assert "uq_domain_mutation_idempotency" in mutation_unique_names
    assert "uq_domain_state_version" in state_unique_names


def test_wave001_migration_is_single_head_and_has_upgrade_downgrade() -> None:
    content = MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260813_57"' in content
    assert 'down_revision = "20260729_56"' in content
    assert "def upgrade()" in content
    assert "def downgrade()" in content
    for table in (
        '"domain_aggregate_heads"',
        '"domain_mutation_records"',
        '"domain_state_versions"',
    ):
        assert table in content
    assert "uq_domain_mutation_idempotency" in content
    assert "uq_domain_state_version" in content


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PostgreSQL migration probe is BLOCKED",
)
def test_wave001_revision_upgrade_downgrade_reupgrade_on_postgresql() -> None:
    """Exercise this revision's real PostgreSQL DDL without claiming full-chain migration proof."""

    engine = create_engine(os.environ["ZUNO_TEST_DATABASE_URL"])
    schema = f"wave001_revision_probe_{uuid4().hex[:12]}"

    try:
        with engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
            _apply_revision_function(connection, schema, "upgrade")

        _assert_upgraded_schema(engine, schema)

        with engine.begin() as connection:
            _apply_revision_function(connection, schema, "downgrade")

        assert inspect(engine).get_table_names(schema=schema) == []

        with engine.begin() as connection:
            _apply_revision_function(connection, schema, "upgrade")

        _assert_upgraded_schema(engine, schema)
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        engine.dispose()
