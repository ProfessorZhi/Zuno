from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Protocol


class GraphSession(Protocol):
    def run(self, query: str, **kwargs: Any) -> Any:
        ...


def _first_count(rows: Any) -> int:
    for row in rows:
        if isinstance(row, dict):
            return int(row.get("count") or 0)
        return int(row["count"])
    return 0


@dataclass
class GraphProjectIdMigration:
    session: GraphSession

    async def run(self, *, dry_run: bool = True) -> dict[str, int | bool]:
        entities_to_backfill = _first_count(
            self.session.run(
                """
                MATCH (e)
                WHERE e.domain_pack_id IS NOT NULL
                  AND e.graphrag_project_id IS NULL
                RETURN count(e) AS count
                """
            )
        )
        relations_to_backfill = _first_count(
            self.session.run(
                """
                MATCH ()-[r]->()
                WHERE r.domain_pack_id IS NOT NULL
                  AND r.graphrag_project_id IS NULL
                RETURN count(r) AS count
                """
            )
        )

        result: dict[str, int | bool] = {
            "dry_run": dry_run,
            "entities_to_backfill": entities_to_backfill,
            "relations_to_backfill": relations_to_backfill,
            "entities_backfilled": 0,
            "relations_backfilled": 0,
        }
        if dry_run:
            return result

        result["entities_backfilled"] = _first_count(
            self.session.run(
                """
                MATCH (e)
                WHERE e.domain_pack_id IS NOT NULL
                  AND e.graphrag_project_id IS NULL
                SET e.graphrag_project_id = e.domain_pack_id
                RETURN count(e) AS count
                """
            )
        )
        result["relations_backfilled"] = _first_count(
            self.session.run(
                """
                MATCH ()-[r]->()
                WHERE r.domain_pack_id IS NOT NULL
                  AND r.graphrag_project_id IS NULL
                SET r.graphrag_project_id = r.domain_pack_id
                RETURN count(r) AS count
                """
            )
        )
        return result


async def _run_cli(args: argparse.Namespace) -> dict[str, int | bool]:
    from neo4j import GraphDatabase

    uri = args.uri or os.environ.get("NEO4J_URI")
    user = args.user or os.environ.get("NEO4J_USER")
    password = args.password or os.environ.get("NEO4J_PASSWORD")
    database = args.database or os.environ.get("NEO4J_DATABASE")
    if not uri or not user or not password:
        raise SystemExit("NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD are required")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session(database=database) as session:
            return await GraphProjectIdMigration(session).run(dry_run=not args.apply)
    finally:
        driver.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill Neo4j graphrag_project_id from legacy domain_pack_id."
    )
    parser.add_argument("--uri", default=None)
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--database", default=None)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the idempotent backfill. Omit for dry-run counts.",
    )
    args = parser.parse_args()
    print(json.dumps(asyncio.run(_run_cli(args)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
