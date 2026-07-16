from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
DB_URL_TEMPLATE = "postgresql+psycopg://postgres:postgres@localhost:5432/{database}"
REQUIRED_INFRA_TABLES = {
    "infra_outbox_events",
    "infra_inbox_messages",
    "infra_idempotency_claims",
    "infra_worker_leases",
    "infra_object_manifests",
    "infra_checkpoints",
}


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


def _create_database(database: str) -> None:
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT", future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{database}"'))
    finally:
        engine.dispose()


def _drop_database(database: str) -> None:
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT", future=True)
    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :database AND pid <> pg_backend_pid()
                    """
                ),
                {"database": database},
            )
            conn.execute(text(f'DROP DATABASE IF EXISTS "{database}"'))
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


def _current_revision(database_url: str) -> str | None:
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT to_regclass('public.alembic_version') IS NOT NULL")
            ).scalar_one()
            if not exists:
                return None
            return conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
    finally:
        engine.dispose()


def _table_names(database_url: str) -> set[str]:
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    """
                )
            ).all()
            return {str(row.tablename) for row in rows}
    finally:
        engine.dispose()


def verify_phase04_alembic_migration() -> list[str]:
    errors: list[str] = []
    database = f"zuno_phase04_alembic_{uuid4().hex}"
    database_url = DB_URL_TEMPLATE.format(database=database)
    _create_database(database)
    try:
        with tempfile.TemporaryDirectory(prefix="zuno-phase04-alembic-") as tmp:
            config_path = Path(tmp) / "config.yaml"
            _write_config(config_path, database_url)

            upgrade = _run_alembic(config_path, "upgrade", "head")
            if upgrade.returncode != 0:
                errors.append("alembic upgrade head failed: " + (upgrade.stderr or upgrade.stdout).strip())
                return errors
            if _current_revision(database_url) != "20260715_04":
                errors.append(f"unexpected head revision after upgrade: {_current_revision(database_url)!r}")
            missing_tables = REQUIRED_INFRA_TABLES - _table_names(database_url)
            if missing_tables:
                errors.append(f"missing infra tables after upgrade: {sorted(missing_tables)!r}")

            repeated = _run_alembic(config_path, "upgrade", "head")
            if repeated.returncode != 0:
                errors.append("repeated alembic upgrade head failed: " + (repeated.stderr or repeated.stdout).strip())
            if _current_revision(database_url) != "20260715_04":
                errors.append(f"unexpected head revision after repeated upgrade: {_current_revision(database_url)!r}")

            downgrade = _run_alembic(config_path, "downgrade", "base")
            if downgrade.returncode != 0:
                errors.append("alembic downgrade base failed: " + (downgrade.stderr or downgrade.stdout).strip())
            remaining_after_downgrade = REQUIRED_INFRA_TABLES & _table_names(database_url)
            if remaining_after_downgrade:
                errors.append(f"infra tables remained after downgrade base: {sorted(remaining_after_downgrade)!r}")

            reupgrade = _run_alembic(config_path, "upgrade", "head")
            if reupgrade.returncode != 0:
                errors.append("alembic re-upgrade head failed: " + (reupgrade.stderr or reupgrade.stdout).strip())
            if _current_revision(database_url) != "20260715_04":
                errors.append(f"unexpected head revision after re-upgrade: {_current_revision(database_url)!r}")
            missing_after_reupgrade = REQUIRED_INFRA_TABLES - _table_names(database_url)
            if missing_after_reupgrade:
                errors.append(f"missing infra tables after re-upgrade: {sorted(missing_after_reupgrade)!r}")
    finally:
        _drop_database(database)
    return errors


def main() -> int:
    errors = verify_phase04_alembic_migration()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 Alembic migration verification failed.")
        return 1
    print("PHASE04 Alembic migration verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
