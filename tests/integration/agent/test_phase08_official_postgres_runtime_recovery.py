from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

from zuno.agent.runtime import Phase08RunService, build_phase08_run_graph


POSTGRES_DSN = os.environ.get(
    "ZUNO_TEST_POSTGRES_DSN",
    "postgresql://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)


def _state(thread_id: str) -> dict[str, object]:
    return {
        "run_id": f"run:p08:t04:pg:{thread_id}",
        "thread_id": thread_id,
        "trace_id": f"trace:p08:t04:pg:{thread_id}",
        "task_contract_id": f"task-contract:p08:t04:pg:{thread_id}",
        "active_goal_version_id": f"goal:p08:t04:pg:{thread_id}",
        "security_epoch_ref": "security-epoch:p08:t04:pg",
        "current_security_epoch_ref": "security-epoch:p08:t04:pg",
        "deadline_at": datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc),
        "budget_requested_units": 10,
        "budget_available_units": 100,
        "interrupt_requested": True,
    }


def test_phase08_run_graph_resumes_from_official_postgres_checkpoint_after_restart() -> None:
    thread_id = f"phase08-runtime-recovery-{uuid4()}"
    try:
        with PostgresSaver.from_conn_string(POSTGRES_DSN) as saver:
            saver.setup()
            service = Phase08RunService(graph=build_phase08_run_graph(checkpointer=saver))
            interrupted = service.start(_state(thread_id))
            snapshot = service.graph.get_state({"configurable": {"thread_id": thread_id}})

            assert interrupted["finalization_status"] == "interrupted"
            assert snapshot.next == ("execute",)
            assert snapshot.tasks and snapshot.tasks[0].interrupts

        with PostgresSaver.from_conn_string(POSTGRES_DSN) as restarted_saver:
            restarted_service = Phase08RunService(
                graph=build_phase08_run_graph(checkpointer=restarted_saver)
            )
            resumed = restarted_service.resume({"thread_id": thread_id})
            final_snapshot = restarted_service.graph.get_state(
                {"configurable": {"thread_id": thread_id}}
            )

            assert resumed["finalization_status"] == "finalized"
            assert resumed["plan_created_count"] == 1
            assert resumed["publication_ref"].startswith("agent-domain:publication:")
            assert final_snapshot.next == ()
    finally:
        _cleanup_checkpoints(thread_id)


def _cleanup_checkpoints(thread_id: str) -> None:
    with psycopg.connect(POSTGRES_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            for table in ("checkpoint_writes", "checkpoint_blobs", "checkpoints"):
                cur.execute(f"DELETE FROM {table} WHERE thread_id = %s", (thread_id,))
