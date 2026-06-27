import asyncio
import importlib.util
import sys
from pathlib import Path


def _load_migration_class():
    path = (
        Path(__file__).resolve().parents[2]
        / "tools/migrations/migrate_domain_pack_id_to_graphrag_project_id.py"
    )
    spec = importlib.util.spec_from_file_location("graph_project_id_migration", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.GraphProjectIdMigration


def test_graph_store_project_id_migration_dry_run_counts_without_writes():
    GraphProjectIdMigration = _load_migration_class()

    calls = []

    class FakeSession:
        def run(self, query, **kwargs):
            calls.append((query, kwargs))
            if "count(e)" in query:
                return [{"count": 2}]
            if "count(r)" in query:
                return [{"count": 3}]
            raise AssertionError("dry-run should not execute write queries")

    result = asyncio.run(GraphProjectIdMigration(FakeSession()).run(dry_run=True))

    assert result == {
        "dry_run": True,
        "entities_to_backfill": 2,
        "relations_to_backfill": 3,
        "entities_backfilled": 0,
        "relations_backfilled": 0,
    }
    assert len(calls) == 2


def test_graph_store_project_id_migration_apply_backfills_missing_project_id():
    GraphProjectIdMigration = _load_migration_class()

    calls = []

    class FakeSession:
        def run(self, query, **kwargs):
            calls.append((query, kwargs))
            if "count(e)" in query:
                return [{"count": 2}]
            if "count(r)" in query:
                return [{"count": 3}]
            if "SET e.graphrag_project_id = e.domain_pack_id" in query:
                return [{"count": 2}]
            if "SET r.graphrag_project_id = r.domain_pack_id" in query:
                return [{"count": 3}]
            raise AssertionError(f"unexpected query: {query}")

    result = asyncio.run(GraphProjectIdMigration(FakeSession()).run(dry_run=False))

    assert result["dry_run"] is False
    assert result["entities_backfilled"] == 2
    assert result["relations_backfilled"] == 3
    assert any("MATCH (e)" in query for query, _ in calls)
    assert any("MATCH ()-[r]->()" in query for query, _ in calls)
