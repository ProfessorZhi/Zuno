from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest
import yaml
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; Alembic entrypoint probe is BLOCKED",
)
def test_formal_alembic_entrypoint_upgrades_fresh_postgres_to_head(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The production Alembic env must reach head without a legacy-module shim."""

    raw_url = os.environ["ZUNO_TEST_DATABASE_URL"]
    base_url = make_url(raw_url)
    database_name = f"zuno_alembic_entrypoint_{uuid4().hex[:12]}"
    admin_engine = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    database_url = base_url.set(database=database_name)
    engine = create_engine(database_url)
    try:
        config_path = tmp_path / "alembic-entrypoint-config.yaml"
        config_path.write_text(
            yaml.safe_dump(
                {"database": {"sync_endpoint": database_url.render_as_string(hide_password=False)}}
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("ZUNO_CONFIG", str(config_path))

        alembic_config = Config(str(REPO_ROOT / "infra/db/alembic.ini"))
        expected_head = ScriptDirectory.from_config(alembic_config).get_current_head()
        assert expected_head

        # Deliberately do not install a process-local `zuno.settings` alias.
        command.upgrade(alembic_config, "head")

        with engine.connect() as connection:
            actual_head = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            required_tables = connection.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' "
                    "AND table_name IN ('tool_effect_reconciliations', 'infra_mandatory_audit_events')"
                )
            ).scalars().all()
        assert actual_head == expected_head
        assert set(required_tables) == {"tool_effect_reconciliations", "infra_mandatory_audit_events"}
    finally:
        engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :database_name AND pid <> pg_backend_pid()"
                ),
                {"database_name": database_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
        admin_engine.dispose()
