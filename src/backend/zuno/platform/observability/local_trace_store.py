from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any


class SQLiteLocalTraceStore:
    """Small local trace store for PHASE04 runtime event inspection."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS local_runtime_trace_events (
                    event_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    trace_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    UNIQUE(trace_id, sequence)
                )
                """
            )

    def append(
        self,
        *,
        event_id: str,
        task_id: str,
        trace_id: str,
        sequence: int,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO local_runtime_trace_events(
                    event_id, task_id, trace_id, sequence, event_type, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    task_id,
                    trace_id,
                    sequence,
                    event_type,
                    json.dumps(payload, ensure_ascii=True, sort_keys=True),
                ),
            )

    def list_by_trace(self, trace_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT event_id, task_id, trace_id, sequence, event_type, payload_json
                FROM local_runtime_trace_events
                WHERE trace_id = ?
                ORDER BY sequence
                """,
                (trace_id,),
            ).fetchall()
        return [
            {
                "event_id": str(row["event_id"]),
                "task_id": str(row["task_id"]),
                "trace_id": str(row["trace_id"]),
                "sequence": int(row["sequence"]),
                "event_type": str(row["event_type"]),
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


__all__ = ["SQLiteLocalTraceStore"]
