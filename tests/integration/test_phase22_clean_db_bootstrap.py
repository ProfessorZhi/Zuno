from __future__ import annotations

"""PHASE22 clean-database alembic bootstrap regression (Task A).

Proves that a completely empty PostgreSQL database can reach the single
migration head through ``alembic upgrade head``, that ``alembic heads``
reports exactly one head, and that downgrade to base and re-upgrade both
succeed. Skips with BLOCKED_WITH_EXACT_GAPS when PostgreSQL is unreachable.
"""

import os
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_HEAD = "20260803_58"
POSTGRES_ADMIN_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_ADMIN_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres?connect_timeout=5",
)


def _admin_available() -> bool:
    try:
        engine = create_engine(POSTGRES_ADMIN_URL)
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        engine.dispose()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _admin_available(),
    reason=(
        "BLOCKED_WITH_EXACT_GAPS: PostgreSQL admin connection unreachable at "
        f"{POSTGRES_ADMIN_URL}; clean-DB bootstrap tests skipped"
    ),
)


def _run_alembic(*args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def _scratch_database_url(database_name: str) -> str:
    return (
        f"postgresql+psycopg://postgres:postgres@localhost:5432/"
        f"{database_name}?connect_timeout=5"
    )


def _drop_database(database_name: str) -> None:
    engine = create_engine(POSTGRES_ADMIN_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :name AND pid <> pg_backend_pid()"
            ),
            {"name": database_name},
        )
        connection.execute(
            text(f'DROP DATABASE IF EXISTS "{database_name}"')
        )
    engine.dispose()


@pytest.fixture()
def scratch_database(tmp_path: Path):
    database_name = f"zuno_phase22_bootstrap_{uuid4().hex[:12]}"
    engine = create_engine(POSTGRES_ADMIN_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    engine.dispose()
    config_file = tmp_path / "phase22-bootstrap-config.yaml"
    async_url = (
        f"postgresql+asyncpg://postgres:postgres@localhost:5432/"
        f"{database_name}?connect_timeout=5"
    )
    config_file.write_text(
        "database:\n"
        f"  sync_endpoint: {_scratch_database_url(database_name)}\n"
        f"  async_endpoint: {async_url}\n",
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "ZUNO_CONFIG": str(config_file),
        "ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS": "10",
        "PGCONNECT_TIMEOUT": "5",
    }
    try:
        yield env, database_name
    finally:
        _drop_database(database_name)


class TestPhase22CleanDbBootstrap:
    def test_empty_database_upgrades_to_single_head(self, scratch_database) -> None:
        env, database_name = scratch_database
        # empty database has no alembic_version table yet
        engine = create_engine(_scratch_database_url(database_name))
        with engine.connect() as connection:
            has_version = connection.execute(
                text(
                    "select exists(select 1 from information_schema.tables "
                    "where table_name = 'alembic_version')"
                )
            ).scalar()
        engine.dispose()
        assert has_version is False

        upgraded = _run_alembic("upgrade", "head", env=env)
        assert upgraded.returncode == 0, upgraded.stderr

        current = _run_alembic("current", env=env)
        assert current.returncode == 0, current.stderr
        assert MIGRATION_HEAD in current.stdout

        heads = _run_alembic("heads", env=env)
        assert heads.returncode == 0, heads.stderr
        assert heads.stdout.count("(head)") == 1
        assert MIGRATION_HEAD in heads.stdout

    def test_downgrade_to_base_then_reupgrade(self, scratch_database) -> None:
        env, database_name = scratch_database
        assert _run_alembic("upgrade", "head", env=env).returncode == 0

        downgraded = _run_alembic("downgrade", "base", env=env)
        assert downgraded.returncode == 0, downgraded.stderr
        # base leaves no migration version
        current = _run_alembic("current", env=env)
        assert current.returncode == 0, current.stderr
        assert MIGRATION_HEAD not in current.stdout

        re_upgraded = _run_alembic("upgrade", "head", env=env)
        assert re_upgraded.returncode == 0, re_upgraded.stderr
        current = _run_alembic("current", env=env)
        assert MIGRATION_HEAD in current.stdout

    def test_run_state_tables_created_by_migration(self, scratch_database) -> None:
        env, database_name = scratch_database
        assert _run_alembic("upgrade", "head", env=env).returncode == 0
        engine = create_engine(_scratch_database_url(database_name))
        with engine.connect() as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    text(
                        "select tablename from pg_tables "
                        "where schemaname = 'public' "
                        "and tablename in "
                        "('canonical_ingestion_runs', "
                        "'canonical_ingestion_run_history', "
                        "'knowledge_entities', 'knowledge_relations')"
                    )
                ).all()
            }
        engine.dispose()
        assert tables == {
            "canonical_ingestion_runs",
            "canonical_ingestion_run_history",
            "knowledge_entities",
            "knowledge_relations",
        }
