from __future__ import annotations

from importlib.util import find_spec
from uuid import uuid4

import psycopg
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.postgres import PostgresSaver

POSTGRES_DSN = "postgresql://postgres:postgres@localhost:5432/zuno"


def _checkpoint(marker: str) -> dict[str, object]:
    checkpoint = empty_checkpoint()
    version = "00000000000000000000000000000001.0"
    checkpoint["channel_values"] = {"marker": marker, "state_version": 1}
    checkpoint["channel_versions"] = {"marker": version}
    checkpoint["versions_seen"] = {"phase04": {"marker": version}}
    return checkpoint


def _cleanup(thread_ids: list[str]) -> None:
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            for table in ["checkpoint_writes", "checkpoint_blobs", "checkpoints"]:
                cur.execute(
                    f"DELETE FROM {table} WHERE thread_id = ANY(%s)",
                    (thread_ids,),
                )


def verify_phase04_official_langgraph_checkpointer() -> list[str]:
    errors: list[str] = []
    if find_spec("langgraph.checkpoint.postgres") is None:
        return ["official LangGraph PostgreSQL Checkpointer package is not importable"]

    marker = uuid4().hex
    thread_a = f"phase04-official-a-{marker}"
    thread_b = f"phase04-official-b-{marker}"
    namespace = "phase04-official"
    thread_ids = [thread_a, thread_b]
    try:
        with PostgresSaver.from_conn_string(POSTGRES_DSN) as saver:
            saver.setup()
            config_a = {"configurable": {"thread_id": thread_a, "checkpoint_ns": namespace}}
            config_b = {"configurable": {"thread_id": thread_b, "checkpoint_ns": namespace}}

            saved_a = saver.put(
                config_a,
                _checkpoint(thread_a),
                {"source": "phase04-official-checkpointer", "step": 1},
                {"marker": "00000000000000000000000000000001.0"},
            )
            saved_b = saver.put(
                config_b,
                _checkpoint(thread_b),
                {"source": "phase04-official-checkpointer", "step": 1},
                {"marker": "00000000000000000000000000000001.0"},
            )
            saver.put_writes(saved_a, [("observation", {"marker": thread_a})], "task-a")

        with PostgresSaver.from_conn_string(POSTGRES_DSN) as restarted:
            restored_a = restarted.get_tuple(saved_a)
            restored_b = restarted.get_tuple(saved_b)
            listed_a = list(restarted.list({"configurable": {"thread_id": thread_a}}, limit=5))
            listed_b = list(restarted.list({"configurable": {"thread_id": thread_b}}, limit=5))

        if restored_a is None or restored_a.checkpoint["channel_values"].get("marker") != thread_a:
            errors.append("official PostgresSaver did not restore thread A checkpoint")
        if restored_b is None or restored_b.checkpoint["channel_values"].get("marker") != thread_b:
            errors.append("official PostgresSaver did not restore thread B checkpoint")
        if len(listed_a) != 1 or len(listed_b) != 1:
            errors.append("official PostgresSaver list did not preserve thread isolation")
        if restored_a and restored_b and restored_a.checkpoint["id"] == restored_b.checkpoint["id"]:
            errors.append("official PostgresSaver reused checkpoint id across isolated threads")

        with psycopg.connect(POSTGRES_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name IN (
                        'checkpoint_migrations',
                        'checkpoints',
                        'checkpoint_blobs',
                        'checkpoint_writes'
                      )
                    """
                )
                tables = {row[0] for row in cur.fetchall()}
        expected = {"checkpoint_migrations", "checkpoints", "checkpoint_blobs", "checkpoint_writes"}
        if tables != expected:
            errors.append(f"official PostgresSaver schema setup missing tables: {sorted(expected - tables)}")
    except Exception as exc:
        errors.append(f"official LangGraph PostgreSQL Checkpointer smoke failed: {exc}")
    finally:
        _cleanup(thread_ids)
    return errors


def main() -> int:
    errors = verify_phase04_official_langgraph_checkpointer()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 official LangGraph PostgreSQL Checkpointer verification failed.")
        return 1
    print("PHASE04 official LangGraph PostgreSQL Checkpointer verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
