from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any

from zuno.agent.harness import ControllerRuntimeState, RuntimeCheckpoint, RuntimeInterrupt


RUNTIME_STORE_SCHEMA_VERSION = "agent-runtime-store-v1"


class RuntimeStoreError(RuntimeError):
    pass


class RuntimeStateCorruptError(RuntimeStoreError):
    pass


@dataclass(slots=True)
class SQLiteDurableRuntimeRecord:
    state: ControllerRuntimeState
    status: str = "created"
    checkpoint_ids: list[str] | None = None
    latest_checkpoint_id: str | None = None
    pending_interrupt_id: str | None = None
    failure: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.checkpoint_ids is None:
            self.checkpoint_ids = []


class SQLiteAgentRunStore:
    """SQLite-backed durable store for PHASE04 runtime facts."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def create_task(self, state: ControllerRuntimeState, *, status: str = "running") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_runtime_runs(
                    task_id, run_id, trace_id, thread_id, workspace_id, user_id,
                    status, state_version, state_json, checkpoint_ids_json,
                    latest_checkpoint_id, pending_interrupt_id, failure_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
                """,
                (
                    state.task_id,
                    state.task_id,
                    state.trace_id,
                    state.thread_id,
                    state.workspace_id,
                    state.user_id,
                    status,
                    RUNTIME_STORE_SCHEMA_VERSION,
                    _json_dump(state.to_dict()),
                    _json_dump([]),
                ),
            )

    def has_task(self, task_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM agent_runtime_runs WHERE task_id = ?",
                (task_id,),
            ).fetchone()
        return row is not None

    def get_record(self, task_id: str) -> SQLiteDurableRuntimeRecord:
        row = self._run_row(task_id)
        return SQLiteDurableRuntimeRecord(
            state=_controller_state_from_json(row["state_json"]),
            status=str(row["status"]),
            checkpoint_ids=list(_json_load(row["checkpoint_ids_json"], [])),
            latest_checkpoint_id=row["latest_checkpoint_id"],
            pending_interrupt_id=row["pending_interrupt_id"],
            failure=_json_load(row["failure_json"], None),
        )

    def update_state(self, state: ControllerRuntimeState) -> None:
        self._execute(
            """
            UPDATE agent_runtime_runs
            SET state_json = ?, trace_id = ?, thread_id = ?, workspace_id = ?, user_id = ?
            WHERE task_id = ?
            """,
            (
                _json_dump(state.to_dict()),
                state.trace_id,
                state.thread_id,
                state.workspace_id,
                state.user_id,
                state.task_id,
            ),
        )

    def update_status(self, task_id: str, status: str) -> None:
        self._execute(
            "UPDATE agent_runtime_runs SET status = ? WHERE task_id = ?",
            (status, task_id),
        )

    def save_checkpoint(self, checkpoint: RuntimeCheckpoint) -> None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT checkpoint_ids_json FROM agent_runtime_runs WHERE task_id = ?",
                (checkpoint.task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"unknown durable runtime task: {checkpoint.task_id}")
            checkpoint_ids = list(_json_load(row["checkpoint_ids_json"], []))
            if checkpoint.checkpoint_id not in checkpoint_ids:
                checkpoint_ids.append(checkpoint.checkpoint_id)
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_runtime_checkpoints(
                    checkpoint_id, task_id, trace_id, thread_id, node, route,
                    state_version, state_json, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checkpoint.checkpoint_id,
                    checkpoint.task_id,
                    checkpoint.trace_id,
                    checkpoint.thread_id,
                    checkpoint.node,
                    str(checkpoint.payload.get("route") or ""),
                    checkpoint.state_version,
                    _json_dump(checkpoint.state),
                    _json_dump(checkpoint.payload),
                ),
            )
            conn.execute(
                """
                UPDATE agent_runtime_runs
                SET checkpoint_ids_json = ?, latest_checkpoint_id = ?
                WHERE task_id = ?
                """,
                (_json_dump(checkpoint_ids), checkpoint.checkpoint_id, checkpoint.task_id),
            )

    def latest_checkpoint(self, task_id: str) -> RuntimeCheckpoint | None:
        row = self._run_row(task_id)
        checkpoint_id = row["latest_checkpoint_id"]
        if not checkpoint_id:
            return None
        return self._checkpoint(checkpoint_id)

    def save_interrupt(self, interrupt: RuntimeInterrupt) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_runtime_interrupts(
                    interrupt_id, task_id, trace_id, thread_id, node, status,
                    reason, required_approval, payload_json, resumable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interrupt.interrupt_id,
                    interrupt.task_id,
                    interrupt.trace_id,
                    interrupt.thread_id,
                    interrupt.node,
                    "pending",
                    interrupt.reason,
                    interrupt.required_approval,
                    _json_dump(interrupt.payload),
                    int(interrupt.resumable),
                ),
            )
            conn.execute(
                "UPDATE agent_runtime_runs SET pending_interrupt_id = ? WHERE task_id = ?",
                (interrupt.interrupt_id, interrupt.task_id),
            )

    def pending_interrupt(self, task_id: str) -> RuntimeInterrupt | None:
        row = self._run_row(task_id)
        interrupt_id = row["pending_interrupt_id"]
        if not interrupt_id:
            return None
        with self._connect() as conn:
            interrupt = conn.execute(
                "SELECT * FROM agent_runtime_interrupts WHERE interrupt_id = ? AND status = 'pending'",
                (interrupt_id,),
            ).fetchone()
        if interrupt is None:
            return None
        return RuntimeInterrupt(
            interrupt_id=str(interrupt["interrupt_id"]),
            thread_id=str(interrupt["thread_id"]),
            task_id=str(interrupt["task_id"]),
            trace_id=str(interrupt["trace_id"]),
            node=str(interrupt["node"]),
            reason=str(interrupt["reason"]),
            required_approval=str(interrupt["required_approval"] or ""),
            payload=dict(_json_load(interrupt["payload_json"], {})),
            resumable=bool(interrupt["resumable"]),
        )

    def clear_interrupt(self, task_id: str) -> None:
        row = self._run_row(task_id)
        interrupt_id = row["pending_interrupt_id"]
        with self._connect() as conn:
            if interrupt_id:
                conn.execute(
                    "UPDATE agent_runtime_interrupts SET status = 'consumed' WHERE interrupt_id = ?",
                    (interrupt_id,),
                )
            conn.execute(
                "UPDATE agent_runtime_runs SET pending_interrupt_id = NULL WHERE task_id = ?",
                (task_id,),
            )

    def mark_failure(self, task_id: str, failure: dict[str, Any]) -> None:
        self._execute(
            """
            UPDATE agent_runtime_runs
            SET status = 'failed', failure_json = ?
            WHERE task_id = ?
            """,
            (_json_dump(failure), task_id),
        )

    def append_event(self, event: Any) -> None:
        payload = event.to_dict()
        event_index = _event_sequence(payload["event_id"])
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_runtime_events(
                    event_id, task_id, trace_id, thread_id, sequence, type,
                    status, node, payload_json, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["event_id"],
                    payload["task_id"],
                    payload["trace_id"],
                    payload["thread_id"],
                    event_index,
                    payload["type"],
                    payload["status"],
                    payload.get("node") or "",
                    _json_dump(payload.get("payload") or {}),
                    float(payload.get("timestamp") or 0.0),
                ),
            )

    def events(self, task_id: str) -> tuple[Any, ...]:
        from zuno.agent.durable_runtime import DurableRuntimeEvent

        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM agent_runtime_events WHERE task_id = ? ORDER BY sequence",
                (task_id,),
            ).fetchall()
        return tuple(
            DurableRuntimeEvent(
                event_id=str(row["event_id"]),
                task_id=str(row["task_id"]),
                trace_id=str(row["trace_id"]),
                thread_id=str(row["thread_id"]),
                type=str(row["type"]),
                status=str(row["status"]),
                node=str(row["node"] or ""),
                payload=dict(_json_load(row["payload_json"], {})),
                timestamp=float(row["timestamp"]),
            )
            for row in rows
        )

    def snapshot(self, task_id: str) -> Any:
        from zuno.agent.durable_runtime import DurableRuntimeTaskSnapshot

        record = self.get_record(task_id)
        return DurableRuntimeTaskSnapshot(
            task_id=record.state.task_id,
            trace_id=record.state.trace_id,
            thread_id=record.state.thread_id,
            workspace_id=record.state.workspace_id,
            status=record.status,
            state=record.state,
            checkpoint_ids=tuple(record.checkpoint_ids or []),
            latest_checkpoint=self.latest_checkpoint(task_id),
            pending_interrupt=self.pending_interrupt(task_id),
            failure=deepcopy(record.failure),
            events=self.events(task_id),
        )

    def load_latest(self, *, run_id: str, workspace_id: str, user_id: str) -> Any:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT task_id FROM agent_runtime_runs
                WHERE run_id = ? AND workspace_id = ? AND user_id = ?
                """,
                (run_id, workspace_id, user_id),
            ).fetchone()
        if row is None:
            raise KeyError(f"runtime run not found in scope: {run_id}")
        return self.snapshot(str(row["task_id"]))

    def append_plan_version(self, *, task_id: str, plan_version: int, plan_state: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO agent_runtime_plan_versions(task_id, plan_version, plan_json)
            VALUES (?, ?, ?)
            """,
            (task_id, plan_version, _json_dump(plan_state)),
        )

    def append_observation(self, *, task_id: str, observation_id: str, observation: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO agent_runtime_observations(task_id, observation_id, observation_json)
            VALUES (?, ?, ?)
            """,
            (task_id, observation_id, _json_dump(observation)),
        )

    def claim_tool_execution(
        self,
        *,
        task_id: str,
        workspace_id: str,
        user_id: str,
        idempotency_key: str,
        tool_name: str,
        payload: dict[str, Any] | None = None,
    ) -> bool:
        try:
            self._execute(
                """
                INSERT INTO agent_runtime_tool_claims(
                    idempotency_key, task_id, workspace_id, user_id, tool_name, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    idempotency_key,
                    task_id,
                    workspace_id,
                    user_id,
                    tool_name,
                    _json_dump(payload or {}),
                ),
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def _checkpoint(self, checkpoint_id: str) -> RuntimeCheckpoint:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM agent_runtime_checkpoints WHERE checkpoint_id = ?",
                (checkpoint_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"runtime checkpoint not found: {checkpoint_id}")
        return RuntimeCheckpoint(
            checkpoint_id=str(row["checkpoint_id"]),
            thread_id=str(row["thread_id"]),
            task_id=str(row["task_id"]),
            trace_id=str(row["trace_id"]),
            node=str(row["node"]),
            state=dict(_json_load(row["state_json"], {})),
            payload=dict(_json_load(row["payload_json"], {})),
            state_version=str(row["state_version"]),
        )

    def _run_row(self, task_id: str) -> sqlite3.Row:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM agent_runtime_runs WHERE task_id = ?",
                (task_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown durable runtime task: {task_id}")
        return row

    def _execute(self, sql: str, params: tuple[Any, ...]) -> None:
        with self._connect() as conn:
            conn.execute(sql, params)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS agent_runtime_runs (
                    task_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    state_version TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    checkpoint_ids_json TEXT NOT NULL,
                    latest_checkpoint_id TEXT,
                    pending_interrupt_id TEXT,
                    failure_json TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_agent_runtime_runs_scope
                    ON agent_runtime_runs(run_id, workspace_id, user_id);

                CREATE TABLE IF NOT EXISTS agent_runtime_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    node TEXT NOT NULL,
                    route TEXT NOT NULL,
                    state_version TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES agent_runtime_runs(task_id)
                );

                CREATE TABLE IF NOT EXISTS agent_runtime_events (
                    event_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    node TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    UNIQUE(task_id, sequence),
                    FOREIGN KEY(task_id) REFERENCES agent_runtime_runs(task_id)
                );

                CREATE TABLE IF NOT EXISTS agent_runtime_interrupts (
                    interrupt_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    node TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    required_approval TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    resumable INTEGER NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES agent_runtime_runs(task_id)
                );

                CREATE TABLE IF NOT EXISTS agent_runtime_plan_versions (
                    task_id TEXT NOT NULL,
                    plan_version INTEGER NOT NULL,
                    plan_json TEXT NOT NULL,
                    PRIMARY KEY(task_id, plan_version),
                    FOREIGN KEY(task_id) REFERENCES agent_runtime_runs(task_id)
                );

                CREATE TABLE IF NOT EXISTS agent_runtime_observations (
                    task_id TEXT NOT NULL,
                    observation_id TEXT NOT NULL,
                    observation_json TEXT NOT NULL,
                    PRIMARY KEY(task_id, observation_id),
                    FOREIGN KEY(task_id) REFERENCES agent_runtime_runs(task_id)
                );

                CREATE TABLE IF NOT EXISTS agent_runtime_tool_claims (
                    idempotency_key TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES agent_runtime_runs(task_id)
                );
                """
            )


def _controller_state_from_json(value: str) -> ControllerRuntimeState:
    payload = _json_load(value, None)
    if not isinstance(payload, dict):
        raise RuntimeStateCorruptError("runtime state snapshot is not a JSON object")
    return ControllerRuntimeState.from_dict(payload)


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _json_load(value: str | None, default: Any) -> Any:
    if value is None:
        return deepcopy(default)
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise RuntimeStateCorruptError("runtime store JSON payload is corrupt") from exc


def _event_sequence(event_id: str) -> int:
    try:
        return int(str(event_id).rsplit(":", 1)[1])
    except (IndexError, ValueError):
        return 1


__all__ = [
    "RUNTIME_STORE_SCHEMA_VERSION",
    "RuntimeStateCorruptError",
    "RuntimeStoreError",
    "SQLiteAgentRunStore",
    "SQLiteDurableRuntimeRecord",
]
