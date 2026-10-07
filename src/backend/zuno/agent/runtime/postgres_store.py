from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any

from sqlalchemy import Engine, text

from zuno.agent.harness import ControllerRuntimeState, RuntimeCheckpoint, RuntimeInterrupt


RUNTIME_STORE_SCHEMA_VERSION = "agent-runtime-store-v1"


@dataclass(slots=True)
class PostgresDurableRuntimeRecord:
    state: ControllerRuntimeState
    status: str = "created"
    checkpoint_ids: list[str] | None = None
    latest_checkpoint_id: str | None = None
    pending_interrupt_id: str | None = None
    failure: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.checkpoint_ids is None:
            self.checkpoint_ids = []


class PostgresAgentRunStore:
    """PostgreSQL-backed AgentRunStore using the existing agent_runtime_* tables."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create_task(
        self,
        state: ControllerRuntimeState,
        *,
        status: str = "running",
        run_id: str | None = None,
    ) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO agent_runtime_runs(
                        task_id, run_id, trace_id, thread_id, workspace_id, user_id,
                        status, state_version, state_json, checkpoint_ids_json,
                        latest_checkpoint_id, pending_interrupt_id, failure_json
                    ) VALUES (
                        :task_id, :run_id, :trace_id, :thread_id, :workspace_id, :user_id,
                        :status, :state_version, CAST(:state_json AS json), CAST(:checkpoint_ids_json AS json),
                        NULL, NULL, NULL
                    )
                    """
                ),
                {
                    "task_id": state.task_id,
                    "run_id": run_id or state.task_id,
                    "trace_id": state.trace_id,
                    "thread_id": state.thread_id,
                    "workspace_id": state.workspace_id,
                    "user_id": state.user_id,
                    "status": status,
                    "state_version": RUNTIME_STORE_SCHEMA_VERSION,
                    "state_json": _json_text(state.to_dict()),
                    "checkpoint_ids_json": _json_text([]),
                },
            )

    def has_task(self, task_id: str) -> bool:
        with self.engine.connect() as connection:
            row = connection.execute(
                text("SELECT 1 FROM agent_runtime_runs WHERE task_id = :task_id"),
                {"task_id": task_id},
            ).first()
        return row is not None

    def get_record(self, task_id: str) -> PostgresDurableRuntimeRecord:
        row = self._run_row(task_id)
        return PostgresDurableRuntimeRecord(
            state=ControllerRuntimeState.from_dict(dict(row["state_json"] or {})),
            status=str(row["status"]),
            checkpoint_ids=[str(value) for value in (row["checkpoint_ids_json"] or [])],
            latest_checkpoint_id=None if row["latest_checkpoint_id"] is None else str(row["latest_checkpoint_id"]),
            pending_interrupt_id=None if row["pending_interrupt_id"] is None else str(row["pending_interrupt_id"]),
            failure=None if row["failure_json"] is None else dict(row["failure_json"]),
        )

    def update_state(self, state: ControllerRuntimeState) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE agent_runtime_runs
                    SET state_json = CAST(:state_json AS json), trace_id = :trace_id,
                        thread_id = :thread_id, workspace_id = :workspace_id, user_id = :user_id
                    WHERE task_id = :task_id
                    """
                ),
                {
                    "state_json": _json_text(state.to_dict()),
                    "trace_id": state.trace_id,
                    "thread_id": state.thread_id,
                    "workspace_id": state.workspace_id,
                    "user_id": state.user_id,
                    "task_id": state.task_id,
                },
            )

    def update_status(self, task_id: str, status: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text("UPDATE agent_runtime_runs SET status = :status WHERE task_id = :task_id"),
                {"status": status, "task_id": task_id},
            )

    def save_checkpoint(self, checkpoint: RuntimeCheckpoint) -> None:
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT checkpoint_ids_json
                    FROM agent_runtime_runs
                    WHERE task_id = :task_id
                    FOR UPDATE
                    """
                ),
                {"task_id": checkpoint.task_id},
            ).mappings().first()
            if row is None:
                raise KeyError(f"unknown durable runtime task: {checkpoint.task_id}")
            checkpoint_ids = [str(value) for value in (row["checkpoint_ids_json"] or [])]
            if checkpoint.checkpoint_id not in checkpoint_ids:
                checkpoint_ids.append(checkpoint.checkpoint_id)
            connection.execute(
                text(
                    """
                    INSERT INTO agent_runtime_checkpoints(
                        checkpoint_id, task_id, trace_id, thread_id, node, route,
                        state_version, state_json, payload_json
                    ) VALUES (
                        :checkpoint_id, :task_id, :trace_id, :thread_id, :node, :route,
                        :state_version, CAST(:state_json AS json), CAST(:payload_json AS json)
                    )
                    ON CONFLICT (checkpoint_id) DO UPDATE
                    SET task_id = EXCLUDED.task_id,
                        trace_id = EXCLUDED.trace_id,
                        thread_id = EXCLUDED.thread_id,
                        node = EXCLUDED.node,
                        route = EXCLUDED.route,
                        state_version = EXCLUDED.state_version,
                        state_json = EXCLUDED.state_json,
                        payload_json = EXCLUDED.payload_json
                    """
                ),
                {
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "task_id": checkpoint.task_id,
                    "trace_id": checkpoint.trace_id,
                    "thread_id": checkpoint.thread_id,
                    "node": checkpoint.node,
                    "route": str(checkpoint.payload.get("route") or ""),
                    "state_version": checkpoint.state_version,
                    "state_json": _json_text(checkpoint.state),
                    "payload_json": _json_text(checkpoint.payload),
                },
            )
            connection.execute(
                text(
                    """
                    UPDATE agent_runtime_runs
                    SET checkpoint_ids_json = CAST(:checkpoint_ids_json AS json),
                        latest_checkpoint_id = :checkpoint_id
                    WHERE task_id = :task_id
                    """
                ),
                {
                    "checkpoint_ids_json": _json_text(checkpoint_ids),
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "task_id": checkpoint.task_id,
                },
            )

    def latest_checkpoint(self, task_id: str) -> RuntimeCheckpoint | None:
        row = self._run_row(task_id)
        checkpoint_id = row["latest_checkpoint_id"]
        if not checkpoint_id:
            return None
        return self._checkpoint(str(checkpoint_id))

    def save_interrupt(self, interrupt: RuntimeInterrupt) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO agent_runtime_interrupts(
                        interrupt_id, task_id, trace_id, thread_id, node, status,
                        reason, required_approval, payload_json, resumable
                    ) VALUES (
                        :interrupt_id, :task_id, :trace_id, :thread_id, :node, 'pending',
                        :reason, :required_approval, CAST(:payload_json AS json), :resumable
                    )
                    ON CONFLICT (interrupt_id) DO UPDATE
                    SET task_id = EXCLUDED.task_id,
                        trace_id = EXCLUDED.trace_id,
                        thread_id = EXCLUDED.thread_id,
                        node = EXCLUDED.node,
                        status = EXCLUDED.status,
                        reason = EXCLUDED.reason,
                        required_approval = EXCLUDED.required_approval,
                        payload_json = EXCLUDED.payload_json,
                        resumable = EXCLUDED.resumable
                    """
                ),
                {
                    "interrupt_id": interrupt.interrupt_id,
                    "task_id": interrupt.task_id,
                    "trace_id": interrupt.trace_id,
                    "thread_id": interrupt.thread_id,
                    "node": interrupt.node,
                    "reason": interrupt.reason,
                    "required_approval": interrupt.required_approval,
                    "payload_json": _json_text(interrupt.payload),
                    "resumable": interrupt.resumable,
                },
            )
            connection.execute(
                text(
                    """
                    UPDATE agent_runtime_runs
                    SET pending_interrupt_id = :interrupt_id
                    WHERE task_id = :task_id
                    """
                ),
                {"interrupt_id": interrupt.interrupt_id, "task_id": interrupt.task_id},
            )

    def pending_interrupt(self, task_id: str) -> RuntimeInterrupt | None:
        row = self._run_row(task_id)
        interrupt_id = row["pending_interrupt_id"]
        if not interrupt_id:
            return None
        with self.engine.connect() as connection:
            interrupt = connection.execute(
                text(
                    """
                    SELECT * FROM agent_runtime_interrupts
                    WHERE interrupt_id = :interrupt_id AND status = 'pending'
                    """
                ),
                {"interrupt_id": interrupt_id},
            ).mappings().first()
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
            payload=dict(interrupt["payload_json"] or {}),
            resumable=bool(interrupt["resumable"]),
        )

    def clear_interrupt(self, task_id: str) -> None:
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT pending_interrupt_id FROM agent_runtime_runs
                    WHERE task_id = :task_id
                    FOR UPDATE
                    """
                ),
                {"task_id": task_id},
            ).mappings().first()
            if row is None:
                raise KeyError(f"unknown durable runtime task: {task_id}")
            interrupt_id = row["pending_interrupt_id"]
            if interrupt_id:
                connection.execute(
                    text(
                        """
                        UPDATE agent_runtime_interrupts
                        SET status = 'consumed'
                        WHERE interrupt_id = :interrupt_id
                        """
                    ),
                    {"interrupt_id": interrupt_id},
                )
            connection.execute(
                text(
                    """
                    UPDATE agent_runtime_runs
                    SET pending_interrupt_id = NULL
                    WHERE task_id = :task_id
                    """
                ),
                {"task_id": task_id},
            )

    def mark_failure(self, task_id: str, failure: dict[str, Any]) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE agent_runtime_runs
                    SET status = 'failed', failure_json = CAST(:failure_json AS json)
                    WHERE task_id = :task_id
                    """
                ),
                {"failure_json": _json_text(failure), "task_id": task_id},
            )

    def append_event(self, event: Any) -> None:
        payload = event.to_dict()
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO agent_runtime_events(
                        event_id, task_id, trace_id, thread_id, sequence, type,
                        status, node, payload_json, timestamp
                    ) VALUES (
                        :event_id, :task_id, :trace_id, :thread_id, :sequence, :type,
                        :status, :node, CAST(:payload_json AS json), :timestamp
                    )
                    """
                ),
                {
                    "event_id": payload["event_id"],
                    "task_id": payload["task_id"],
                    "trace_id": payload["trace_id"],
                    "thread_id": payload["thread_id"],
                    "sequence": _event_sequence(str(payload["event_id"])),
                    "type": payload["type"],
                    "status": payload["status"],
                    "node": payload.get("node") or "",
                    "payload_json": _json_text(payload.get("payload") or {}),
                    "timestamp": float(payload.get("timestamp") or 0.0),
                },
            )

    def events(self, task_id: str) -> tuple[Any, ...]:
        from zuno.agent.durable_runtime import DurableRuntimeEvent

        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    """
                    SELECT * FROM agent_runtime_events
                    WHERE task_id = :task_id
                    ORDER BY sequence, event_id
                    """
                ),
                {"task_id": task_id},
            ).mappings().all()
        return tuple(
            DurableRuntimeEvent(
                event_id=str(row["event_id"]),
                task_id=str(row["task_id"]),
                trace_id=str(row["trace_id"]),
                thread_id=str(row["thread_id"]),
                type=str(row["type"]),
                status=str(row["status"]),
                node=str(row["node"] or ""),
                payload=dict(row["payload_json"] or {}),
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
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT task_id FROM agent_runtime_runs
                    WHERE run_id = :run_id AND workspace_id = :workspace_id AND user_id = :user_id
                    """
                ),
                {"run_id": run_id, "workspace_id": workspace_id, "user_id": user_id},
            ).first()
        if row is None:
            raise KeyError(f"runtime run not found in scope: {run_id}")
        return self.snapshot(str(row.task_id))

    def _checkpoint(self, checkpoint_id: str) -> RuntimeCheckpoint:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT * FROM agent_runtime_checkpoints
                    WHERE checkpoint_id = :checkpoint_id
                    """
                ),
                {"checkpoint_id": checkpoint_id},
            ).mappings().first()
        if row is None:
            raise KeyError(f"runtime checkpoint not found: {checkpoint_id}")
        return RuntimeCheckpoint(
            checkpoint_id=str(row["checkpoint_id"]),
            thread_id=str(row["thread_id"]),
            task_id=str(row["task_id"]),
            trace_id=str(row["trace_id"]),
            node=str(row["node"]),
            state=dict(row["state_json"] or {}),
            payload=dict(row["payload_json"] or {}),
            state_version=str(row["state_version"]),
        )

    def _run_row(self, task_id: str) -> dict[str, Any]:
        with self.engine.connect() as connection:
            row = connection.execute(
                text("SELECT * FROM agent_runtime_runs WHERE task_id = :task_id"),
                {"task_id": task_id},
            ).mappings().first()
        if row is None:
            raise KeyError(f"unknown durable runtime task: {task_id}")
        return dict(row)


def _json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def _event_sequence(event_id: str) -> int:
    try:
        return int(str(event_id).rsplit(":", 1)[1])
    except (IndexError, ValueError):
        return 1


__all__ = [
    "PostgresAgentRunStore",
    "PostgresDurableRuntimeRecord",
    "RUNTIME_STORE_SCHEMA_VERSION",
]
