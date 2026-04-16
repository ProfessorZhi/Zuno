from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path

import yaml
from alembic import context
from sqlalchemy import engine_from_config, pool

from agentchat.database.metadata import metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _load_database_url() -> str:
    config_path = Path(__file__).resolve().parents[1] / "agentchat" / "config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    database = data.get("database") or {}
    return database.get(
        "sync_endpoint",
        "postgresql+psycopg://postgres:postgres@localhost:5432/agentchat",
    )


config.set_main_option("sqlalchemy.url", _load_database_url())
target_metadata = metadata


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
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
