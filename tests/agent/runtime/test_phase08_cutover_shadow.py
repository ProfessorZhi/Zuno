from __future__ import annotations

import pytest

import zuno.agent.runtime as runtime_package
from zuno.agent.runtime import (
    Phase08CutoverError,
    Phase08RetiredController,
    Phase08RuntimeRequest,
    Phase08RuntimeResponse,
    Phase08RunService,
    Phase08SideEffectClaimError,
    SideEffectLedger,
    build_phase08_run_graph,
    build_phase08_test_checkpointer,
)


def _request() -> Phase08RuntimeRequest:
    return Phase08RuntimeRequest(
        request_id="request:p08:t08:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        user_id="user-a",
        task_id="task-p08-t08",
        trace_id="trace:p08:t08:1",
        goal="answer with deterministic phase08 runtime",
        idempotency_key="idem:p08:t08:1",
    )


def _retired() -> Phase08RetiredController:
    return Phase08RetiredController()


def _new_runtime() -> Phase08RunService:
    return Phase08RunService(graph=build_phase08_run_graph(checkpointer=build_phase08_test_checkpointer()))


class _UnavailableRuntime:
    def start(self, state):
        del state
        raise RuntimeError("runtime unavailable")


def test_shadow_mode_is_rejected_by_retired_surface() -> None:
    with pytest.raises(TypeError, match="takes no arguments"):
        Phase08RetiredController(mode="shadow")
    with pytest.raises(Phase08CutoverError, match="retired"):
        _retired().handle(_request())


def test_shadow_mode_cannot_fallback_when_runtime_unavailable() -> None:
    # The retired surface holds no runtime and no runner, so an unavailable
    # runtime cannot be routed around: the request is refused outright.
    _ = _UnavailableRuntime()
    with pytest.raises(Phase08CutoverError, match="retired"):
        _retired().handle(_request())


def test_canary_mode_is_rejected_by_retired_surface() -> None:
    with pytest.raises(TypeError, match="takes no arguments"):
        Phase08RetiredController(mode="canary")
    with pytest.raises(Phase08CutoverError, match="retired"):
        _retired().handle(_request())


def test_new_runtime_exception_never_invokes_legacy_runtime() -> None:
    class _ExplodingOwnerPort:
        def execute(self, state):
            del state
            raise RuntimeError("owner port failed")

    service = Phase08RunService(
        graph=build_phase08_run_graph(
            checkpointer=build_phase08_test_checkpointer(),
            owner_port=_ExplodingOwnerPort(),  # type: ignore[arg-type]
        )
    )
    with pytest.raises(RuntimeError, match="owner port failed"):
        service.start(
            {
                "run_id": "run:p08:t08:1",
                "thread_id": "thread:p08:t08:1",
                "trace_id": "trace:p08:t08:1",
                "tenant_id": "tenant-a",
                "security_epoch_ref": "security-epoch:phase08",
                "current_security_epoch_ref": "security-epoch:phase08",
                "budget_requested_units": 1,
                "budget_available_units": 10,
                "step_run_id": "step-run:p08:t08:1",
            }
        )
    # There is no cutover controller left to fall back to: the exception is the
    # terminal behavior and the package exposes no dual-path symbols.
    assert not hasattr(runtime_package, "Phase08CutoverController")
    assert not hasattr(runtime_package, "LegacyRunner")


def test_rollback_mode_is_rejected_by_retired_surface() -> None:
    with pytest.raises(TypeError, match="takes no arguments"):
        Phase08RetiredController(mode="rollback")
    with pytest.raises(Phase08CutoverError, match="retired"):
        _retired().handle(_request())


def test_retry_rejects_duplicate_side_effect_claim() -> None:
    ledger = SideEffectLedger()
    request = _request()

    ledger.claim(request, runtime="phase08")
    with pytest.raises(Phase08SideEffectClaimError, match="duplicate side effect claim"):
        ledger.claim(request, runtime="phase08")
    assert ledger.claimed_keys == {request.idempotency_key}


def test_effect_committed_blocks_any_second_runtime() -> None:
    ledger = SideEffectLedger()
    request = _request()
    ledger.claim(request, runtime="phase08")

    # Once the effect is committed no second runtime may execute: the retired
    # controller refuses and a duplicate claim is rejected.
    assert ledger.has_claim(request) is True
    with pytest.raises(Phase08CutoverError, match="retired"):
        _retired().handle(request)
    with pytest.raises(Phase08SideEffectClaimError, match="duplicate side effect claim"):
        ledger.claim(request, runtime="phase08")
    assert ledger.claimed_keys == {request.idempotency_key}


def test_cutover_response_dto_still_round_trips_for_ledger_fixtures() -> None:
    # The response DTO remains part of the persistent ledger fixture surface;
    # it is not used by any runtime dispatch anymore.
    response = Phase08RuntimeResponse(
        runtime="phase08",
        request_hash=_request().request_hash,
        output_ref="answer:fixture",
        trace_ref="trace:fixture",
        side_effect_ref="side-effect:fixture",
    )
    assert response.runtime == "phase08"
    assert response.rollback_reason is None
