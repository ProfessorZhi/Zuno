from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zuno.agent.runtime import (
    PHASE08_RUN_SCHEMA,
    Phase08Conflict,
    Phase08RuntimeError,
    Phase08SignalRecord,
    append_signal,
    reconcile_generations,
)


def _state():
    return {
        "run_id": "run:p08:t07:1",
        "security_epoch_ref": "security-epoch:p08:t07:1",
        "signal_journal": [],
    }


def test_generation_reconciliation_detects_ahead_behind_orphan_and_stale_schema() -> None:
    assert reconcile_generations(domain_generation=2, checkpoint_generation=1, schema_version=PHASE08_RUN_SCHEMA)["status"] == "checkpoint_fail"
    assert reconcile_generations(domain_generation=1, checkpoint_generation=2, schema_version=PHASE08_RUN_SCHEMA)["status"] == "checkpoint_ahead"
    assert reconcile_generations(domain_generation=0, checkpoint_generation=0, schema_version=PHASE08_RUN_SCHEMA)["status"] == "orphan_run"
    assert reconcile_generations(domain_generation=1, checkpoint_generation=1, schema_version="stale")["status"] == "stale_schema"


def test_signal_journal_rejects_duplicates_wrong_scope_and_honors_deny() -> None:
    state = _state()
    signal = Phase08SignalRecord(
        signal_id="signal:p08:t07:1",
        run_id=state["run_id"],
        security_epoch_ref=state["security_epoch_ref"],
        decision="approve",
        observed_at=datetime(2026, 7, 23, 23, 0, tzinfo=timezone.utc),
    )

    recorded = append_signal(state, signal)
    denied = append_signal(
        recorded,
        Phase08SignalRecord(
            signal_id="signal:p08:t07:2",
            run_id=state["run_id"],
            security_epoch_ref=state["security_epoch_ref"],
            decision="deny",
        ),
    )

    assert len(recorded["signal_journal"]) == 1
    assert denied["cancel_requested"] is True
    assert denied["latest_control_decision_ref"] == "security-denied"

    with pytest.raises(Phase08Conflict, match="duplicate signal"):
        append_signal(recorded, signal)
    with pytest.raises(Phase08RuntimeError, match="wrong run"):
        append_signal(
            state,
            Phase08SignalRecord(
                signal_id="signal:p08:t07:3",
                run_id="other-run",
                security_epoch_ref=state["security_epoch_ref"],
                decision="approve",
            ),
        )
    with pytest.raises(Phase08RuntimeError, match="wrong security epoch"):
        append_signal(
            state,
            Phase08SignalRecord(
                signal_id="signal:p08:t07:4",
                run_id=state["run_id"],
                security_epoch_ref="security-epoch:new",
                decision="approve",
            ),
        )
