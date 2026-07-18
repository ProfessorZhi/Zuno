from __future__ import annotations

from importlib.util import find_spec
from uuid import uuid4

import psycopg
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.postgres import PostgresSaver

from zuno.platform.database.foundation import (
    InfrastructureConflictError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

POSTGRES_DSN = "postgresql://postgres:postgres@localhost:5432/zuno"
SQLALCHEMY_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


def _checkpoint(marker: str, *, version: str, generation: int, parent_ref: str | None = None) -> dict[str, object]:
    checkpoint = empty_checkpoint()
    checkpoint["channel_values"] = {
        "marker": marker,
        "state_version": 1,
        "generation": generation,
        "parent_ref": parent_ref,
    }
    checkpoint["channel_versions"] = {"marker": version}
    checkpoint["versions_seen"] = {"phase04": {"marker": version}}
    checkpoint["updated_channels"] = ["marker"]
    return checkpoint


def _cleanup(thread_ids: list[str]) -> None:
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            for table in ["checkpoint_writes", "checkpoint_blobs", "checkpoints"]:
                cur.execute(
                    f"DELETE FROM {table} WHERE thread_id = ANY(%s)",
                    (thread_ids,),
                )
            cur.execute(
                "DELETE FROM infra_checkpoints WHERE thread_id = ANY(%s)",
                (thread_ids,),
            )


def verify_phase04_official_langgraph_checkpointer() -> list[str]:
    errors: list[str] = []
    if find_spec("langgraph.checkpoint.postgres") is None:
        return ["official LangGraph PostgreSQL Checkpointer package is not importable"]

    marker = uuid4().hex
    thread_a = f"phase04-official-a-{marker}"
    thread_b = f"phase04-official-b-{marker}"
    thread_delete = f"phase04-official-delete-{marker}"
    namespace = "phase04-official"
    thread_ids = [thread_a, thread_b, thread_delete]
    engine = create_foundation_engine(SQLALCHEMY_URL)
    try:
        with PostgresSaver.from_conn_string(POSTGRES_DSN) as saver:
            saver.setup()
            config_a = {"configurable": {"thread_id": thread_a, "checkpoint_ns": namespace}}
            config_b = {"configurable": {"thread_id": thread_b, "checkpoint_ns": namespace}}
            config_delete = {"configurable": {"thread_id": thread_delete, "checkpoint_ns": namespace}}
            version_1 = saver.get_next_version(None, None)
            version_2 = saver.get_next_version(version_1, None)

            saved_a = saver.put(
                config_a,
                _checkpoint(thread_a, version=version_1, generation=1),
                {"source": "phase04-official-checkpointer", "step": 1},
                {"marker": version_1},
            )
            saved_a2 = saver.put(
                saved_a,
                _checkpoint(
                    thread_a,
                    version=version_2,
                    generation=2,
                    parent_ref=str(saved_a["configurable"]["checkpoint_id"]),
                ),
                {"source": "phase04-official-checkpointer", "step": 2},
                {"marker": version_2},
            )
            saved_b = saver.put(
                config_b,
                _checkpoint(thread_b, version=version_1, generation=1),
                {"source": "phase04-official-checkpointer", "step": 1},
                {"marker": version_1},
            )
            saved_delete = saver.put(
                config_delete,
                _checkpoint(thread_delete, version=version_1, generation=1),
                {"source": "phase04-official-checkpointer", "step": 1},
                {"marker": version_1},
            )
            saver.put_writes(saved_a2, [("observation", {"marker": thread_a})], "task-a")

        with PostgresSaver.from_conn_string(POSTGRES_DSN) as restarted:
            restored_a = restarted.get_tuple(saved_a2)
            restored_b = restarted.get_tuple(saved_b)
            restored_delete = restarted.get_tuple(saved_delete)
            listed_a = list(restarted.list({"configurable": {"thread_id": thread_a}}, limit=5))
            listed_b = list(restarted.list({"configurable": {"thread_id": thread_b}}, limit=5))
            delta_history = restarted.get_delta_channel_history(
                config=saved_a2,
                channels=["marker"],
            )
            restarted.delete_thread(thread_delete)
            deleted_copy = restarted.get_tuple(
                {"configurable": {"thread_id": thread_delete, "checkpoint_ns": namespace}}
            )

        if restored_a is None or restored_a.checkpoint["channel_values"].get("generation") != 2:
            errors.append("official PostgresSaver did not restore latest thread A generation")
        if restored_b is None or restored_b.checkpoint["channel_values"].get("marker") != thread_b:
            errors.append("official PostgresSaver did not restore thread B checkpoint")
        if restored_delete is None:
            errors.append("official PostgresSaver did not restore thread before cleanup")
        if deleted_copy is not None:
            errors.append("official PostgresSaver delete_thread did not remove checkpoint thread")
        if len(listed_a) != 2 or len(listed_b) != 1:
            errors.append("official PostgresSaver list did not preserve thread isolation")
        if restored_a and restored_b and restored_a.checkpoint["id"] == restored_b.checkpoint["id"]:
            errors.append("official PostgresSaver reused checkpoint id across isolated threads")
        if "marker" not in delta_history:
            errors.append("official PostgresSaver delta channel history did not include marker channel")

        with InfrastructureUnitOfWork(engine) as repo:
            repo.save_checkpoint(
                thread_id=thread_a,
                checkpoint_id=str(saved_a2["configurable"]["checkpoint_id"]),
                generation=2,
                owner="official-langgraph-postgres-checkpointer",
                state={
                    "official_checkpoint_id": str(saved_a2["configurable"]["checkpoint_id"]),
                    "thread_id": thread_a,
                    "generation": 2,
                },
            )
        with InfrastructureUnitOfWork(engine) as repo:
            latest = repo.latest_checkpoint(thread_id=thread_a)
            try:
                repo.save_checkpoint(
                    thread_id=thread_a,
                    checkpoint_id="stale-generation",
                    generation=2,
                    owner="late-official-checkpointer-writer",
                    state={"thread_id": thread_a, "generation": 2, "late": True},
                )
                errors.append("infrastructure checkpoint generation accepted a stale writer")
            except InfrastructureConflictError:
                pass
        if latest is None or latest["checkpoint_id"] != str(saved_a2["configurable"]["checkpoint_id"]):
            errors.append("official checkpoint id did not reconcile with infrastructure checkpoint receipt")

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
        errors.append(
            "official LangGraph PostgreSQL Checkpointer smoke failed: "
            f"{type(exc).__name__}: {exc}"
        )
    finally:
        engine.dispose()
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
