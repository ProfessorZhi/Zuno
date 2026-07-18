from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import uuid4

import psycopg
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.postgres import PostgresSaver

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_BASE_DSN = "postgresql://postgres:postgres@localhost:5432"
SOURCE_DSN = f"{POSTGRES_BASE_DSN}/zuno"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _checkpoint(marker: str, generation: int) -> dict[str, object]:
    checkpoint = empty_checkpoint()
    version = f"{generation:032d}.0"
    checkpoint["channel_values"] = {
        "marker": marker,
        "generation": generation,
        "restored_by": "official-postgres-saver",
    }
    checkpoint["channel_versions"] = {"marker": version}
    checkpoint["versions_seen"] = {"phase04-restore": {"marker": version}}
    checkpoint["updated_channels"] = ["marker"]
    return checkpoint


def _cleanup_source_thread(thread_id: str) -> None:
    with PostgresSaver.from_conn_string(SOURCE_DSN) as saver:
        saver.delete_thread(thread_id)


def _query_official_tables(database_name: str, thread_id: str) -> list[str]:
    errors: list[str] = []
    with psycopg.connect(f"{POSTGRES_BASE_DSN}/{database_name}", connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(*)
                FROM checkpoints
                WHERE thread_id = %s
                """,
                (thread_id,),
            )
            checkpoint_count = int(cur.fetchone()[0])
            cur.execute(
                """
                SELECT EXISTS (
                  SELECT 1
                  FROM information_schema.tables
                  WHERE table_schema = 'public'
                    AND table_name = 'checkpoint_blobs'
                )
                """,
            )
            blob_table_exists = bool(cur.fetchone()[0])
            cur.execute(
                """
                SELECT count(*)
                FROM checkpoint_writes
                WHERE thread_id = %s
                """,
                (thread_id,),
            )
            write_count = int(cur.fetchone()[0])
    if checkpoint_count != 2:
        errors.append(f"restored official checkpoints row count mismatch: {checkpoint_count}")
    if not blob_table_exists:
        errors.append("restored official checkpoint_blobs table is missing")
    if write_count < 1:
        errors.append("restored official checkpoint writes are missing")
    return errors


def verify_phase04_official_checkpointer_backup_restore() -> list[str]:
    marker = uuid4().hex
    thread_id = f"phase04-official-restore-{marker}"
    namespace = "phase04-official-restore"
    database_name = f"zuno_phase04_cp_restore_{marker[:12]}"
    dump_path = f"/tmp/{database_name}.dump"
    errors: list[str] = []
    source_saved: dict[str, object] | None = None

    try:
        with PostgresSaver.from_conn_string(SOURCE_DSN) as saver:
            saver.setup()
            config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": namespace}}
            source_saved = saver.put(
                config,
                _checkpoint(marker, 1),
                {"source": "phase04-official-checkpointer-restore", "step": 1},
                {"marker": "00000000000000000000000000000001.0"},
            )
            latest_saved = saver.put(
                source_saved,
                _checkpoint(marker, 2),
                {"source": "phase04-official-checkpointer-restore", "step": 2},
                {"marker": "00000000000000000000000000000002.0"},
            )
            saver.put_writes(
                latest_saved,
                [("restore_observation", {"marker": marker, "generation": 2})],
                "restore-task",
            )
            source_saved = latest_saved

        dump = _run(
            [
                "docker",
                "exec",
                "zuno-postgres",
                "pg_dump",
                "-U",
                "postgres",
                "-d",
                "zuno",
                "-Fc",
                "-f",
                dump_path,
            ]
        )
        if dump.returncode != 0:
            return [f"official Checkpointer pg_dump failed: {dump.stderr.strip()}"]

        create_db = _run(["docker", "exec", "zuno-postgres", "createdb", "-U", "postgres", database_name])
        if create_db.returncode != 0:
            return [f"official Checkpointer restore database create failed: {create_db.stderr.strip()}"]

        restore = _run(
            [
                "docker",
                "exec",
                "zuno-postgres",
                "pg_restore",
                "-U",
                "postgres",
                "-d",
                database_name,
                dump_path,
            ]
        )
        if restore.returncode != 0:
            errors.append(f"official Checkpointer pg_restore failed: {restore.stderr.strip()}")
        else:
            errors.extend(_query_official_tables(database_name, thread_id))
            with PostgresSaver.from_conn_string(f"{POSTGRES_BASE_DSN}/{database_name}") as restored:
                restored_tuple = restored.get_tuple(source_saved)
                listed = list(
                    restored.list(
                        {"configurable": {"thread_id": thread_id, "checkpoint_ns": namespace}},
                        limit=5,
                    )
                )
            if restored_tuple is None:
                errors.append("official PostgresSaver could not read checkpoint from restored database")
            elif restored_tuple.checkpoint["channel_values"].get("generation") != 2:
                errors.append("official PostgresSaver restored the wrong checkpoint generation")
            if len(listed) != 2:
                errors.append(f"official PostgresSaver restored list count mismatch: {len(listed)}")
    except Exception as exc:
        errors.append(
            "official Checkpointer backup/restore verification failed: "
            f"{type(exc).__name__}: {exc}"
        )
    finally:
        if source_saved is not None:
            _cleanup_source_thread(thread_id)
        _run(["docker", "exec", "zuno-postgres", "dropdb", "-U", "postgres", "--if-exists", database_name])
        _run(["docker", "exec", "zuno-postgres", "rm", "-f", dump_path])
    return errors


def main() -> int:
    errors = verify_phase04_official_checkpointer_backup_restore()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 official Checkpointer backup/restore verification failed.")
        return 1
    print("PHASE04 official Checkpointer backup/restore verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
