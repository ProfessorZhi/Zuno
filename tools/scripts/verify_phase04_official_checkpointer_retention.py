from __future__ import annotations

from importlib.util import find_spec
from uuid import uuid4

import psycopg
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.postgres import PostgresSaver

POSTGRES_DSN = "postgresql://postgres:postgres@localhost:5432/zuno"


def _checkpoint(marker: str, *, version: str, generation: int) -> dict[str, object]:
    checkpoint = empty_checkpoint()
    checkpoint["channel_values"] = {
        "marker": marker,
        "generation": generation,
        "retention_scope": "phase04-official-checkpointer-retention",
    }
    checkpoint["channel_versions"] = {"marker": version}
    checkpoint["versions_seen"] = {"phase04": {"marker": version}}
    checkpoint["updated_channels"] = ["marker"]
    return checkpoint


def _thread_row_count(thread_id: str) -> dict[str, int]:
    with psycopg.connect(POSTGRES_DSN) as conn:
        with conn.cursor() as cur:
            counts: dict[str, int] = {}
            for table in ("checkpoints", "checkpoint_blobs", "checkpoint_writes"):
                cur.execute(
                    f"SELECT count(*) FROM {table} WHERE thread_id = %s",
                    (thread_id,),
                )
                counts[table] = int(cur.fetchone()[0])
            return counts


def _cleanup(thread_ids: list[str]) -> None:
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            for table in ["checkpoint_writes", "checkpoint_blobs", "checkpoints"]:
                cur.execute(
                    f"DELETE FROM {table} WHERE thread_id = ANY(%s)",
                    (thread_ids,),
                )


def verify_phase04_official_checkpointer_retention() -> list[str]:
    errors: list[str] = []
    if find_spec("langgraph.checkpoint.postgres") is None:
        return ["official LangGraph PostgreSQL Checkpointer package is not importable"]

    marker = uuid4().hex
    active_thread = f"phase04-official-retention-active-{marker}"
    expired_thread = f"phase04-official-retention-expired-{marker}"
    thread_ids = [active_thread, expired_thread]
    namespace = "phase04-retention"
    try:
        with PostgresSaver.from_conn_string(POSTGRES_DSN) as saver:
            saver.setup()
            active_config = {
                "configurable": {"thread_id": active_thread, "checkpoint_ns": namespace}
            }
            expired_config = {
                "configurable": {"thread_id": expired_thread, "checkpoint_ns": namespace}
            }
            version_1 = saver.get_next_version(None, None)
            version_2 = saver.get_next_version(version_1, None)

            active_saved_1 = saver.put(
                active_config,
                _checkpoint(active_thread, version=version_1, generation=1),
                {"source": "phase04-official-retention", "retention": "active"},
                {"marker": version_1},
            )
            active_saved_2 = saver.put(
                active_saved_1,
                _checkpoint(active_thread, version=version_2, generation=2),
                {"source": "phase04-official-retention", "retention": "active"},
                {"marker": version_2},
            )
            saver.put_writes(active_saved_2, [("retention", {"marker": active_thread})], "active-task")

            expired_saved = saver.put(
                expired_config,
                _checkpoint(expired_thread, version=version_1, generation=1),
                {"source": "phase04-official-retention", "retention": "expired"},
                {"marker": version_1},
            )
            saver.put_writes(expired_saved, [("retention", {"marker": expired_thread})], "expired-task")

            active_before = _thread_row_count(active_thread)
            expired_before = _thread_row_count(expired_thread)
            if active_before["checkpoints"] < 2:
                errors.append(f"active retention control thread was not seeded: {active_before!r}")
            if expired_before["checkpoints"] < 1 or expired_before["checkpoint_writes"] < 1:
                errors.append(f"expired retention target was not seeded: {expired_before!r}")

            try:
                saver.prune([active_thread], strategy="keep_latest")
                errors.append("official partial prune unexpectedly succeeded without explicit retention review")
            except NotImplementedError:
                pass

            try:
                saver.delete_for_runs(["active-task"])
                errors.append("official run-scoped delete unexpectedly succeeded without explicit retention review")
            except NotImplementedError:
                pass

            saver.delete_thread(expired_thread)
            expired_after = _thread_row_count(expired_thread)
            if any(expired_after.values()):
                errors.append(f"official delete_thread left expired thread rows: {expired_after!r}")

            active_after = _thread_row_count(active_thread)
            if active_after != active_before:
                errors.append(
                    "official expired-thread retention cleanup changed active thread rows: "
                    f"before={active_before!r} after={active_after!r}"
                )

            with PostgresSaver.from_conn_string(POSTGRES_DSN) as restarted:
                active_restored = restarted.get_tuple(active_saved_2)
                expired_restored = restarted.get_tuple(expired_config)
                active_history = list(
                    restarted.list(
                        {"configurable": {"thread_id": active_thread}},
                        limit=5,
                    )
                )
            if active_restored is None or active_restored.checkpoint["channel_values"].get("generation") != 2:
                errors.append("official active thread was not restorable after retention cleanup")
            if expired_restored is not None:
                errors.append("official expired thread was restorable after delete_thread cleanup")
            if len(active_history) != 2:
                errors.append(
                    f"official active thread history changed after expired cleanup: {len(active_history)}"
                )
    except Exception as exc:
        errors.append(
            "official Checkpointer retention verification failed: "
            f"{type(exc).__name__}: {exc}"
        )
    finally:
        _cleanup(thread_ids)
    return errors


def main() -> int:
    errors = verify_phase04_official_checkpointer_retention()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 official Checkpointer retention verification failed.")
        return 1
    print("PHASE04 official Checkpointer retention verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
