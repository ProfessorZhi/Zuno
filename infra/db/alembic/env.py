from __future__ import annotations

import os
import time
from logging.config import fileConfig

import yaml
from alembic import context
from sqlalchemy import engine_from_config, pool, text

from zuno.database.metadata import metadata
from zuno.settings import resolve_app_config_path

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _load_database_url() -> str:
    config_path = resolve_app_config_path()
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    database = data.get("database") or {}
    return database.get(
        "sync_endpoint",
        "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
    )


config.set_main_option("sqlalchemy.url", _load_database_url())
target_metadata = metadata
MIGRATION_LOCK_NAMESPACE = "zuno:alembic:migration:v1"


def _migration_lock_timeout_seconds() -> float:
    raw = os.environ.get("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS", "30")
    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS must be numeric") from exc
    if value <= 0:
        raise RuntimeError("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS must be positive")
    return value


def _acquire_migration_lock(connection) -> None:
    timeout_seconds = _migration_lock_timeout_seconds()
    deadline = time.monotonic() + timeout_seconds
    while True:
        acquired = connection.execute(
            text("SELECT pg_try_advisory_lock(hashtext(:namespace))"),
            {"namespace": MIGRATION_LOCK_NAMESPACE},
        ).scalar_one()
        if acquired:
            return
        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"Alembic migration advisory lock timed out after {timeout_seconds:g} seconds"
            )
        time.sleep(min(0.1, max(0.01, deadline - time.monotonic())))


def _release_migration_lock(connection) -> None:
    released = connection.execute(
        text("SELECT pg_advisory_unlock(hashtext(:namespace))"),
        {"namespace": MIGRATION_LOCK_NAMESPACE},
    ).scalar_one()
    if not released:
        raise RuntimeError("Alembic migration advisory lock ownership was lost")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _acquire_migration_lock(connection)
        connection.commit()
        try:
            context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

            with context.begin_transaction():
                context.run_migrations()
        finally:
            if connection.in_transaction():
                connection.rollback()
            _release_migration_lock(connection)
            connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
