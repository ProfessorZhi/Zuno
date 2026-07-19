from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

import psycopg
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_BASE_DSN = "postgresql://postgres:postgres@localhost:5432"


class _UpgradeInterruptState(TypedDict):
    marker: str
    approval: str
    events: list[str]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _checkpoint(marker: str) -> dict[str, object]:
    checkpoint = empty_checkpoint()
    checkpoint["channel_values"] = {
        "marker": marker,
        "schema_upgrade": "pre-v9",
    }
    checkpoint["channel_versions"] = {"marker": "00000000000000000000000000000001.0"}
    checkpoint["versions_seen"] = {
        "phase04-schema-upgrade": {
            "marker": "00000000000000000000000000000001.0"
        }
    }
    checkpoint["updated_channels"] = ["marker"]
    return checkpoint


def _build_interrupt_resume_graph():
    def approval_node(state: _UpgradeInterruptState) -> dict[str, object]:
        resume_value = interrupt({"kind": "schema-upgrade-approval", "marker": state["marker"]})
        return {
            "approval": str(resume_value),
            "events": state.get("events", []) + [f"resumed:{resume_value}"],
        }

    def final_node(state: _UpgradeInterruptState) -> dict[str, object]:
        return {"events": state.get("events", []) + ["finalized-after-upgrade"]}

    builder = StateGraph(_UpgradeInterruptState)
    builder.add_node("approval", approval_node)
    builder.add_node("final", final_node)
    builder.add_edge(START, "approval")
    builder.add_edge("approval", "final")
    builder.add_edge("final", END)
    return builder


def _apply_old_official_schema(database_name: str, latest_version: int) -> list[str]:
    errors: list[str] = []
    dsn = f"{POSTGRES_BASE_DSN}/{database_name}"
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            for version, migration in enumerate(PostgresSaver.MIGRATIONS[: latest_version + 1]):
                cur.execute(migration)
                cur.execute(
                    "INSERT INTO checkpoint_migrations (v) VALUES (%s) ON CONFLICT DO NOTHING",
                    (version,),
                )
            cur.execute("SELECT max(v) FROM checkpoint_migrations")
            max_version = int(cur.fetchone()[0])
            if max_version != latest_version:
                errors.append(
                    f"old official schema migration version mismatch: {max_version}"
                )
            cur.execute(
                """
                SELECT EXISTS (
                  SELECT 1
                  FROM information_schema.columns
                  WHERE table_schema = 'public'
                    AND table_name = 'checkpoint_writes'
                    AND column_name = 'task_path'
                )
                """
            )
            if bool(cur.fetchone()[0]):
                errors.append("old official schema unexpectedly had task_path column")
    return errors


def _migration_state(database_name: str) -> tuple[int, bool, int]:
    dsn = f"{POSTGRES_BASE_DSN}/{database_name}"
    with psycopg.connect(dsn, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT max(v), count(*) FROM checkpoint_migrations")
            max_version, migration_count = cur.fetchone()
            cur.execute(
                """
                SELECT EXISTS (
                  SELECT 1
                  FROM information_schema.columns
                  WHERE table_schema = 'public'
                    AND table_name = 'checkpoint_writes'
                    AND column_name = 'task_path'
                )
                """
            )
            has_task_path = bool(cur.fetchone()[0])
    return int(max_version), has_task_path, int(migration_count)


def _verify_interrupt_resume_after_upgrade(dsn: str, marker: str) -> list[str]:
    errors: list[str] = []
    thread_id = f"phase04-upgrade-interrupt-{marker}"
    config = {"configurable": {"thread_id": thread_id}}
    graph_builder = _build_interrupt_resume_graph()
    with PostgresSaver.from_conn_string(dsn) as saver:
        graph = graph_builder.compile(checkpointer=saver)
        interrupted = graph.invoke({"marker": marker, "approval": "", "events": []}, config)
        interrupt_values = interrupted.get("__interrupt__") or []
        if not interrupt_values:
            errors.append("upgraded official graph did not emit interrupt")
        state_after_interrupt = graph.get_state(config)
        if state_after_interrupt.next != ("approval",):
            errors.append("upgraded official graph did not persist resumable node")

    with PostgresSaver.from_conn_string(dsn) as restarted:
        graph = graph_builder.compile(checkpointer=restarted)
        resumed = graph.invoke(Command(resume="approved-after-upgrade"), config)
        if resumed.get("approval") != "approved-after-upgrade":
            errors.append(f"upgraded official graph resumed with wrong approval: {resumed!r}")
        if resumed.get("events") != ["resumed:approved-after-upgrade", "finalized-after-upgrade"]:
            errors.append(f"upgraded official graph lost interrupt history: {resumed!r}")
        history = list(graph.get_state_history(config))
        if len(history) < 4:
            errors.append("upgraded official graph checkpoint history was not retained")
        if not any(snapshot.next == ("approval",) for snapshot in history):
            errors.append("upgraded official graph history lost interrupted node")
    return errors


def _verify_upgrade_failure_fail_closed(marker: str, old_version: int) -> list[str]:
    errors: list[str] = []
    broken_db = f"zuno_phase04_cp_upgrade_bad_{marker[:12]}"
    broken_dsn = f"{POSTGRES_BASE_DSN}/{broken_db}"
    create_db = _run(["docker", "exec", "zuno-postgres", "createdb", "-U", "postgres", broken_db])
    if create_db.returncode != 0:
        return [f"official Checkpointer broken schema database create failed: {create_db.stderr.strip()}"]
    try:
        errors.extend(_apply_old_official_schema(broken_db, old_version))
        if errors:
            return errors
        with psycopg.connect(broken_dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("ALTER TABLE checkpoints DROP COLUMN checkpoint")
        try:
            with PostgresSaver.from_conn_string(broken_dsn) as saver:
                saver.setup()
                saver.get_tuple(
                    {"configurable": {"thread_id": f"broken-{marker}", "checkpoint_ns": "phase04"}}
                )
        except Exception:
            return []
        errors.append("official Checkpointer broken schema upgrade did not fail closed")
    finally:
        _run(["docker", "exec", "zuno-postgres", "dropdb", "-U", "postgres", "--if-exists", broken_db])
    return errors


def verify_phase04_official_checkpointer_schema_upgrade() -> list[str]:
    marker = uuid4().hex
    database_name = f"zuno_phase04_cp_upgrade_{marker[:12]}"
    dsn = f"{POSTGRES_BASE_DSN}/{database_name}"
    thread_id = f"phase04-official-schema-upgrade-{marker}"
    namespace = "phase04-official-schema-upgrade"
    errors: list[str] = []
    latest_version = len(PostgresSaver.MIGRATIONS) - 1
    old_version = latest_version - 1

    create_db = _run(["docker", "exec", "zuno-postgres", "createdb", "-U", "postgres", database_name])
    if create_db.returncode != 0:
        return [f"official Checkpointer schema upgrade database create failed: {create_db.stderr.strip()}"]

    try:
        errors.extend(_apply_old_official_schema(database_name, old_version))
        if errors:
            return errors

        with PostgresSaver.from_conn_string(dsn) as old_saver:
            config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": namespace}}
            saved = old_saver.put(
                config,
                _checkpoint(marker),
                {"source": "phase04-official-schema-upgrade", "schema_version": old_version},
                {"marker": "00000000000000000000000000000001.0"},
            )

        before_version, before_task_path, before_count = _migration_state(database_name)
        if before_version != old_version or before_task_path:
            errors.append("official Checkpointer old schema was not preserved before setup")

        with PostgresSaver.from_conn_string(dsn) as upgraded_saver:
            upgraded_saver.setup()
            restored = upgraded_saver.get_tuple(saved)
            upgraded_saver.put_writes(
                saved,
                [("schema_upgrade_observation", {"marker": marker, "version": latest_version})],
                "schema-upgrade-task",
                task_path="phase04/schema-upgrade",
            )
            upgraded_saver.setup()

        after_version, after_task_path, after_count = _migration_state(database_name)
        if after_version != latest_version:
            errors.append(f"official Checkpointer setup did not advance schema: {after_version}")
        if not after_task_path:
            errors.append("official Checkpointer setup did not add task_path column")
        if after_count != latest_version + 1:
            errors.append("official Checkpointer setup did not record each migration exactly once")
        if before_count != old_version + 1:
            errors.append("old official schema migration count was not bounded")
        if restored is None:
            errors.append("official Checkpointer could not read pre-upgrade checkpoint")
        elif restored.checkpoint["channel_values"].get("marker") != marker:
            errors.append("official Checkpointer restored wrong marker after schema upgrade")
        elif restored.checkpoint["channel_values"].get("generation", 1) != 1:
            errors.append("official Checkpointer pre-upgrade generation regressed after upgrade")

        with psycopg.connect(dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT task_path
                    FROM checkpoint_writes
                    WHERE thread_id = %s
                      AND checkpoint_ns = %s
                      AND checkpoint_id = %s
                      AND task_id = %s
                    """,
                    (
                        thread_id,
                        namespace,
                        saved["configurable"]["checkpoint_id"],
                        "schema-upgrade-task",
                    ),
                )
                task_paths = [row[0] for row in cur.fetchall()]
        if task_paths != ["phase04/schema-upgrade"]:
            errors.append(f"official Checkpointer v9 write task_path mismatch: {task_paths!r}")
        errors.extend(_verify_interrupt_resume_after_upgrade(dsn, marker))
        errors.extend(_verify_upgrade_failure_fail_closed(marker, old_version))
    except Exception as exc:
        errors.append(
            "official Checkpointer schema upgrade verification failed: "
            f"{type(exc).__name__}: {exc}"
        )
    finally:
        _run(["docker", "exec", "zuno-postgres", "dropdb", "-U", "postgres", "--if-exists", database_name])
    return errors


def main() -> int:
    errors = verify_phase04_official_checkpointer_schema_upgrade()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 official Checkpointer schema upgrade verification failed.")
        return 1
    print("PHASE04 official Checkpointer schema upgrade verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
