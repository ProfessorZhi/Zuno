from __future__ import annotations

from pathlib import Path
import re

import pytest

import zuno.agent.runtime as runtime_package
from zuno.agent.runtime import (
    PHASE08_RUN_SCHEMA,
    Phase08CutoverError,
    Phase08RetiredController,
    Phase08RuntimeRequest,
    Phase08RunService,
    Phase08SideEffectClaimError,
    SideEffectLedger,
    build_phase08_run_graph,
    build_phase08_test_checkpointer,
    classify_phase08_final_state,
    reconcile_generations,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "src" / "backend" / "zuno"


def _request() -> Phase08RuntimeRequest:
    return Phase08RuntimeRequest(
        request_id="request:p08:retired:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        user_id="user-a",
        task_id="task-p08-retired",
        trace_id="trace:p08:retired:1",
        goal="canonical runtime only",
        idempotency_key="idem:p08:retired:1",
    )


def _service() -> Phase08RunService:
    return Phase08RunService(graph=build_phase08_run_graph(checkpointer=build_phase08_test_checkpointer()))


def _run_state(**overrides: object) -> dict:
    state: dict = {
        "run_id": "run:p08:retired:1",
        "thread_id": "thread:p08:retired:1",
        "trace_id": "trace:p08:retired:1",
        "tenant_id": "tenant-a",
        "security_epoch_ref": "security-epoch:phase08",
        "current_security_epoch_ref": "security-epoch:phase08",
        "budget_requested_units": 1,
        "budget_available_units": 10,
    }
    state.update(overrides)
    return state


# ---------------------------------------------------------------------------
# Failure semantics: security / budget denials propagate; no fallback exists.
# ---------------------------------------------------------------------------


def test_security_denial_propagates_without_fallback() -> None:
    state = _service().start(
        _run_state(current_security_epoch_ref="security-epoch:stale")
    )
    assert state["finalization_status"] == "failed"
    assert state["latest_control_decision_ref"] == "stale_security_epoch"
    assert classify_phase08_final_state(state) == "FAILED/BLOCKED"
    assert not hasattr(runtime_package, "LegacyRunner")


def test_budget_denial_propagates_without_fallback() -> None:
    state = _service().start(
        _run_state(budget_requested_units=10, budget_available_units=1)
    )
    # The canonical graph blocks before creating the plan when the budget is
    # insufficient, so the run fails with no plan and no side effect claim.
    assert state.get("active_plan_version_id") is None
    assert state.get("effect_claim_ref") is None
    assert state["finalization_status"] in {"blocked", "failed"}
    assert classify_phase08_final_state(state) == "FAILED/BLOCKED"
    assert not hasattr(runtime_package, "LegacyRunner")


# ---------------------------------------------------------------------------
# Side-effect / reconciliation semantics.
# ---------------------------------------------------------------------------


def test_effect_committed_classifies_as_committed_and_blocks_second_runtime() -> None:
    state = _service().start(_run_state())
    state["effect_claim_ref"] = "effect-claim:run:p08:retired:1:knowledge"
    assert classify_phase08_final_state(state) == "EFFECT_COMMITTED"

    ledger = SideEffectLedger()
    ledger.claim(_request(), runtime="phase08")
    assert ledger.has_claim(_request()) is True
    with pytest.raises(Phase08SideEffectClaimError, match="duplicate side effect claim"):
        ledger.claim(_request(), runtime="phase08")


def test_unknown_effect_enters_reconciliation() -> None:
    decision = reconcile_generations(
        domain_generation=2,
        checkpoint_generation=1,
        schema_version=PHASE08_RUN_SCHEMA,
    )
    assert decision["status"] == "domain_ahead"
    assert decision["auto_repair"] is True
    assert decision["replay_allowed"] is False
    assert decision["terminate_run"] is False

    # A state without a recognized terminal shape is an unknown effect state.
    assert (
        classify_phase08_final_state(
            {"domain_generation": 2, "checkpoint_generation": 1}
        )
        == "RECONCILIATION_REQUIRED"
    )


def test_completed_run_returns_original_facts() -> None:
    state = _service().start(_run_state())
    assert state["finalization_status"] == "finalized"
    assert classify_phase08_final_state(state) == "COMPLETED"


def test_retry_does_not_repeat_plan() -> None:
    first = _service().start(_run_state())
    second = _service().start(_run_state())
    assert first["active_plan_version_id"] == "plan:run:p08:retired:1"
    assert second["active_plan_version_id"] == first["active_plan_version_id"]
    assert first["plan_created_count"] == 1
    assert second["plan_created_count"] == 1


def test_retry_does_not_repeat_side_effect() -> None:
    ledger = SideEffectLedger()
    request = _request()
    ledger.claim(request, runtime="phase08")
    with pytest.raises(Phase08SideEffectClaimError, match="duplicate side effect claim"):
        ledger.claim(request, runtime="phase08")
    assert ledger.claimed_keys == {request.idempotency_key}


# ---------------------------------------------------------------------------
# Retired surface invariants.
# ---------------------------------------------------------------------------


def test_environment_variable_cannot_restore_retired_path(monkeypatch) -> None:
    monkeypatch.setenv("ZUNO_PHASE08_CUTOVER_MODE", "canary")
    monkeypatch.setenv("ZUNO_WORKSPACE_PHASE08_CUTOVER", "shadow")
    with pytest.raises(Phase08CutoverError, match="retired"):
        Phase08RetiredController().handle(_request())


def test_restart_never_selects_legacy() -> None:
    first = Phase08RetiredController()
    with pytest.raises(Phase08CutoverError, match="retired"):
        first.handle(_request())
    # A fresh controller instance (process restart) behaves identically.
    second = Phase08RetiredController()
    with pytest.raises(Phase08CutoverError, match="retired"):
        second.handle(_request())


def test_package_exports_no_legacy_runner_or_cutover_controller() -> None:
    assert "LegacyRunner" not in runtime_package.__all__
    assert "Phase08CutoverController" not in runtime_package.__all__
    assert not hasattr(runtime_package, "LegacyRunner")
    assert not hasattr(runtime_package, "Phase08CutoverController")


# ---------------------------------------------------------------------------
# Static repository gates.
# ---------------------------------------------------------------------------


def _python_files_under(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py"))


def test_no_fallback_symbol_in_production_source() -> None:
    forbidden = re.compile(
        r"_fallback_to_legacy|legacy_runner|_run_legacy|fallback_allowed=True|Phase08CutoverController"
    )
    hits = [
        str(path.relative_to(REPO_ROOT))
        for path in _python_files_under(BACKEND_ROOT)
        if forbidden.search(path.read_text(encoding="utf-8"))
    ]
    assert hits == []


def test_no_cutover_mode_dispatch_in_runtime_and_workspace_service() -> None:
    forbidden = re.compile(r'mode == "(rollback|shadow|canary)"')
    roots = [
        BACKEND_ROOT / "agent" / "runtime",
        BACKEND_ROOT / "api" / "services" / "workspace_task_runtime.py",
    ]
    hits = []
    for root in roots:
        if root.is_dir():
            for path in _python_files_under(root):
                if forbidden.search(path.read_text(encoding="utf-8")):
                    hits.append(str(path.relative_to(REPO_ROOT)))
        else:
            if forbidden.search(root.read_text(encoding="utf-8")):
                hits.append(str(root.relative_to(REPO_ROOT)))
    assert hits == []


def test_audit_events_never_record_fallback_allowed_true() -> None:
    hits = [
        str(path.relative_to(REPO_ROOT))
        for path in _python_files_under(BACKEND_ROOT)
        if "fallback_allowed=True" in path.read_text(encoding="utf-8")
    ]
    assert hits == []


def test_product_api_reaches_only_canonical_runtime() -> None:
    source = (BACKEND_ROOT / "api" / "services" / "workspace_task_runtime.py").read_text(
        encoding="utf-8"
    )
    for token in ("phase08_cutover", "Phase08CutoverController", "legacy_runner"):
        assert token not in source


def test_queue_worker_reaches_only_canonical_runtime() -> None:
    queue_roots = [
        BACKEND_ROOT / "platform" / "services" / "queue" / "runner.py",
        BACKEND_ROOT / "platform" / "services" / "queue" / "workers.py",
    ]
    for path in queue_roots:
        source = path.read_text(encoding="utf-8")
        for token in ("phase08_cutover", "Phase08CutoverController", "legacy_runner", "_fallback_to_legacy"):
            assert token not in source
