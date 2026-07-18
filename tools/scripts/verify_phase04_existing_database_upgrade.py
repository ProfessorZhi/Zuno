from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, text

from zuno.platform.database.metadata import metadata
from zuno.platform.database.schema_registry import (
    DOMAIN_TABLE_OWNERS,
    ONLINE_SCHEMA_OBJECTS,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
DB_URL_TEMPLATE = "postgresql+psycopg://postgres:postgres@localhost:5432/{database}"
BASE_REVISION = "20260417_01"
HEAD_REVISION = "20260718_11"


def _create_database(database: str) -> None:
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT", future=True)
    try:
        with engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database}"'))
    finally:
        engine.dispose()


def _drop_database(database: str) -> None:
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT", future=True)
    try:
        with engine.connect() as connection:
            connection.execute(
                text("""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :database AND pid <> pg_backend_pid()
                    """),
                {"database": database},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database}"'))
    finally:
        engine.dispose()


def _write_config(path: Path, database_url: str) -> None:
    path.write_text(
        "\n".join(
            [
                "database:",
                f'  sync_endpoint: "{database_url}"',
                f'  async_endpoint: "{database_url.replace("+psycopg://", "+asyncpg://")}"',
                "  echo: false",
                "  pool_size: 2",
                "  max_overflow: 2",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _run_alembic(config_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["ZUNO_CONFIG"] = str(config_path)
    return subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )


def _domain_drift(database_url: str) -> list[object]:
    domain_tables = set(DOMAIN_TABLE_OWNERS)

    def include_object(obj, name, type_, reflected, compare_to):
        if type_ == "table":
            return name in domain_tables
        table_name = getattr(getattr(obj, "table", None), "name", None)
        if table_name not in domain_tables:
            return False
        if type_ in {"index", "unique_constraint", "check_constraint"}:
            return name not in ONLINE_SCHEMA_OBJECTS
        return True

    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(
                connection,
                opts={
                    "compare_type": True,
                    "compare_server_default": True,
                    "include_object": include_object,
                },
            )
            return list(compare_metadata(context, metadata))
    finally:
        engine.dispose()


def _revision(database_url: str) -> str | None:
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as connection:
            if not connection.execute(
                text("SELECT to_regclass('public.alembic_version') IS NOT NULL")
            ).scalar_one():
                return None
            return connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
    finally:
        engine.dispose()


def verify_phase04_existing_database_upgrade() -> list[str]:
    errors: list[str] = []
    database = f"zuno_phase04_existing_{uuid4().hex}"
    database_url = DB_URL_TEMPLATE.format(database=database)
    marker = uuid4().hex
    _create_database(database)
    try:
        engine = create_engine(database_url, future=True)
        try:
            # This is the only allowed create_all use: constructing the legacy test fixture.
            metadata.create_all(engine)
            with engine.begin() as connection:
                connection.execute(
                    text("""
                        INSERT INTO message_like(id, user_input, agent_output)
                        VALUES (:id, :user_input, 'preserve-me')
                        """),
                    {"id": marker, "user_input": f"existing-upgrade-{marker}"},
                )
                connection.execute(
                    text("""
                        INSERT INTO workspace_session(
                            session_id, title, agent, user_id, contexts
                        ) VALUES (
                            :session_id, 'existing upgrade', 'normal',
                            'phase04-existing-upgrade', CAST('[]' AS json)
                        )
                        """),
                    {"session_id": marker},
                )
        finally:
            engine.dispose()

        if _revision(database_url) is not None:
            errors.append(
                "legacy existing database unexpectedly had an Alembic revision"
            )
        initial_drift = _domain_drift(database_url)
        if initial_drift:
            errors.append(
                f"legacy baseline does not match frozen base revision: {initial_drift!r}"
            )

        with tempfile.TemporaryDirectory(prefix="zuno-existing-upgrade-") as temporary:
            config_path = Path(temporary) / "config.yaml"
            _write_config(config_path, database_url)
            stamp = _run_alembic(config_path, "stamp", BASE_REVISION)
            if stamp.returncode != 0:
                errors.append(
                    "existing database stamp failed: "
                    + (stamp.stderr or stamp.stdout).strip()
                )
                return errors
            if _revision(database_url) != BASE_REVISION:
                errors.append(
                    "existing database did not reach the reviewed base revision"
                )
            upgrade = _run_alembic(config_path, "upgrade", "head")
            if upgrade.returncode != 0:
                errors.append(
                    "existing database upgrade failed: "
                    + (upgrade.stderr or upgrade.stdout).strip()
                )
                return errors
            repeated = _run_alembic(config_path, "upgrade", "head")
            if repeated.returncode != 0:
                errors.append(
                    "existing database repeated upgrade failed: "
                    + (repeated.stderr or repeated.stdout).strip()
                )

        if _revision(database_url) != HEAD_REVISION:
            errors.append("existing database did not reach the single Alembic head")
        final_drift = _domain_drift(database_url)
        if final_drift:
            errors.append(
                f"existing database has domain schema drift after upgrade: {final_drift!r}"
            )
        engine = create_engine(database_url, future=True)
        try:
            with engine.connect() as connection:
                preserved = connection.execute(
                    text("""
                        SELECT count(*)
                        FROM message_like
                        WHERE id = :marker AND agent_output = 'preserve-me'
                        """),
                    {"marker": marker},
                ).scalar_one()
                workspace_preserved = connection.execute(
                    text(
                        "SELECT count(*) FROM workspace_session WHERE session_id = :marker"
                    ),
                    {"marker": marker},
                ).scalar_one()
                infra_ready = connection.execute(text("""
                        SELECT to_regclass('public.infra_migration_backfills') IS NOT NULL
                           AND to_regclass('public.infra_outbox_events') IS NOT NULL
                        """)).scalar_one()
            if preserved != 1 or workspace_preserved != 1:
                errors.append("existing domain data was not preserved by the upgrade")
            if not infra_ready:
                errors.append(
                    "existing database upgrade did not install PHASE04 infrastructure tables"
                )
        finally:
            engine.dispose()
    finally:
        _drop_database(database)
    return errors


def main() -> int:
    errors = verify_phase04_existing_database_upgrade()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 existing database upgrade verification failed.")
        return 1
    print("PHASE04 existing database upgrade verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
