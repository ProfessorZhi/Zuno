from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import MetaData, Table, create_engine, inspect, select
from sqlalchemy.dialects.postgresql import insert as pg_insert


CORE_TABLES = [
    "user",
    "dialog",
    "history",
    "workspace_session",
]


def load_postgres_url() -> str:
    config_path = Path(__file__).resolve().parents[1] / "src" / "backend" / "agentchat" / "config.yaml"
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}
    database = config.get("database") or {}
    endpoint = database.get("sync_endpoint")
    if not endpoint:
        raise RuntimeError("PostgreSQL sync_endpoint 未配置，无法执行迁移。")
    return endpoint


def reflect_table(engine, table_name: str) -> Table | None:
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return None
    metadata = MetaData()
    return Table(table_name, metadata, autoload_with=engine)


def normalize_row(table_name: str, row: dict[str, Any]) -> dict[str, Any]:
    payload = dict(row)
    if table_name == "user" and "delete" in payload:
        payload["delete"] = bool(payload["delete"])
    return payload


def copy_rows(mysql_table: Table, postgres_table: Table, mysql_engine, postgres_engine) -> int:
    common_columns = [
        column.name
        for column in postgres_table.columns
        if column.name in mysql_table.columns.keys()
    ]
    if not common_columns:
        return 0

    with mysql_engine.connect() as mysql_conn:
        raw_rows = mysql_conn.execute(
            select(*[mysql_table.c[name] for name in common_columns])
        ).mappings()
        rows = [normalize_row(mysql_table.name, dict(row)) for row in raw_rows]

    if not rows:
        return 0

    primary_keys = [column.name for column in postgres_table.primary_key.columns]
    if not primary_keys:
        raise RuntimeError(f"表 {postgres_table.name} 没有主键，无法安全执行 upsert。")

    insert_stmt = pg_insert(postgres_table).values(rows)
    update_columns = {
        name: getattr(insert_stmt.excluded, name)
        for name in common_columns
        if name not in primary_keys
    }

    statement = insert_stmt.on_conflict_do_update(
        index_elements=primary_keys,
        set_=update_columns,
    )

    with postgres_engine.begin() as postgres_conn:
        postgres_conn.execute(statement)

    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="将旧 MySQL 核心数据迁移到当前 PostgreSQL。")
    parser.add_argument(
        "--mysql-url",
        required=True,
        help="旧 MySQL 连接串，例如 mysql+pymysql://root:password@127.0.0.1:3306/agentchat",
    )
    parser.add_argument(
        "--postgres-url",
        default=load_postgres_url(),
        help="目标 PostgreSQL 连接串，默认读取 src/backend/agentchat/config.yaml",
    )
    args = parser.parse_args()

    mysql_engine = create_engine(args.mysql_url)
    postgres_engine = create_engine(args.postgres_url)

    migrated_counts: dict[str, int] = {}
    for table_name in CORE_TABLES:
        mysql_table = reflect_table(mysql_engine, table_name)
        postgres_table = reflect_table(postgres_engine, table_name)
        if mysql_table is None:
            print(f"[skip] MySQL 中不存在表 {table_name}")
            continue
        if postgres_table is None:
            print(f"[skip] PostgreSQL 中不存在表 {table_name}")
            continue

        row_count = copy_rows(mysql_table, postgres_table, mysql_engine, postgres_engine)
        migrated_counts[table_name] = row_count
        print(f"[ok] {table_name}: migrated {row_count} rows")

    if not migrated_counts:
        print("没有迁移任何表，请确认旧 MySQL 连接串是否正确。")
        return

    print("迁移完成：")
    for table_name, row_count in migrated_counts.items():
        print(f"  - {table_name}: {row_count}")


if __name__ == "__main__":
    main()
