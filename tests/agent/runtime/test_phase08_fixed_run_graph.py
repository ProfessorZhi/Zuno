from __future__ import annotations

from datetime import datetime, timezone

from zuno.agent.runtime import PHASE08_RUN_SCHEMA, Phase08RunService, build_phase08_run_graph


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
    graph = build_phase08_run_graph()
    service = Phase08RunService(graph=graph)

    final_state = service.start(_state())
    checkpoint_state = service.get_state(_state())

    assert final_state["schema_version"] == PHASE08_RUN_SCHEMA
    assert final_state["publication_ref"] == "publication:run:p08:t04:1"
    assert final_state["finalization_status"] == "finalized"
    assert checkpoint_state["execution_snapshot_id"] == "execution-snapshot:run:p08:t04:1"


def test_run_graph_handles_interrupt_resume_cancel_and_deadline() -> None:
    service = Phase08RunService()

    interrupted = service.start(_state(interrupt_requested=True))
    resumed = service.resume(interrupted)
    cancelled = service.cancel(_state(interrupt_requested=True), reason="user_cancelled")
    expired = service.start(
        _state(
            deadline_at=datetime(2026, 7, 23, 23, 0, tzinfo=timezone.utc),
            observed_at=datetime(2026, 7, 24, 0, 0, tzinfo=timezone.utc),
        )
    )

    assert interrupted["finalization_status"] == "interrupted"
    assert interrupted["pending_interrupt_refs"]
    assert resumed["finalization_status"] == "finalized"
    assert resumed["pending_interrupt_refs"] == []
    assert cancelled["finalization_status"] == "cancelled"
    assert expired["finalization_status"] == "failed"
    assert expired["latest_control_decision_ref"] == "deadline_expired"
