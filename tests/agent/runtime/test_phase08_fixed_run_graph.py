from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zuno.agent.runtime import (
    PHASE08_RUN_SCHEMA,
    Phase08RunService,
    Phase08RuntimeError,
    build_phase08_run_graph,
    build_phase08_test_checkpointer,
)


def _state(**overrides):
    state = {
        "run_id": "run:p08:t04:1",
        "thread_id": "thread:p08:t04:1",
        "trace_id": "trace:p08:t04:1",
        "task_contract_id": "task-contract:p08:t04:1",
        "active_goal_version_id": "goal:p08:t04:1",
        "security_epoch_ref": "security-epoch:p08:t04:1",
        "current_security_epoch_ref": "security-epoch:p08:t04:1",
        "deadline_at": datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc),
        "budget_requested_units": 10,
        "budget_available_units": 100,
    }
    state.update(overrides)
    return state


def test_fixed_run_graph_compiles_and_produces_native_checkpoints() -> None:
    graph = build_phase08_run_graph(checkpointer=build_phase08_test_checkpointer())
    service = Phase08RunService(graph=graph)

    final_state = service.start(_state())
    checkpoint_state = service.get_state(_state())

    assert final_state["schema_version"] == PHASE08_RUN_SCHEMA
    assert final_state["phase"] == "finalize"
    assert final_state["final_gate_receipt_ref"].startswith("agent-domain:final-gate:")
    assert final_state["publication_ref"].startswith("agent-domain:publication:")
    assert final_state["outcome_ref"].startswith("agent-domain:run-outcome:")
    assert final_state["finalization_status"] == "finalized"
    assert checkpoint_state["execution_snapshot_id"] == "execution-snapshot:run:p08:t04:1"
    assert checkpoint_state["final_gate_receipt_ref"] == final_state["final_gate_receipt_ref"]


def test_run_graph_requires_explicit_checkpointer_boundary() -> None:
    with pytest.raises(Phase08RuntimeError, match="explicit durable checkpointer"):
        build_phase08_run_graph()


def test_run_graph_handles_interrupt_resume_cancel_and_deadline() -> None:
    service = Phase08RunService(graph=build_phase08_run_graph(checkpointer=build_phase08_test_checkpointer()))

    interrupted = service.start(_state(interrupt_requested=True))
    resumed = service.resume(interrupted)
    cancelled = service.cancel(_state(thread_id="thread:p08:t04:cancel", interrupt_requested=True), reason="user_cancelled")
    expired = service.start(
        _state(
            thread_id="thread:p08:t04:deadline",
            deadline_at=datetime(2026, 7, 23, 23, 0, tzinfo=timezone.utc),
            observed_at=datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc),
        )
    )

    assert interrupted["finalization_status"] == "interrupted"
    assert interrupted["phase"] == "execute"
    assert interrupted["pending_interrupt_refs"]
    assert resumed["finalization_status"] == "finalized"
    assert resumed["pending_interrupt_refs"] == []
    assert resumed["plan_created_count"] == 1
    assert cancelled["finalization_status"] == "cancelled"
    assert expired["finalization_status"] == "failed"
    assert expired["latest_control_decision_ref"] == "deadline_expired"
