from __future__ import annotations

import pytest

from zuno.agent.runtime import (
    Phase08CutoverController,
    Phase08RuntimeRequest,
    Phase08RuntimeResponse,
    Phase08RunService,
    build_phase08_run_graph,
    build_phase08_test_checkpointer,
)


def _request() -> Phase08RuntimeRequest:
    return Phase08RuntimeRequest(
        request_id="request:p08:t08:1",
        workspace_id="workspace-a",
        user_id="user-a",
        task_id="task-p08-t08",
        trace_id="trace:p08:t08:1",
        goal="answer with deterministic phase08 runtime",
        idempotency_key="idem:p08:t08:1",
    )


def _legacy_runner(calls: list[tuple[str, bool]]):
    def _run(request: Phase08RuntimeRequest, allow_side_effect: bool) -> Phase08RuntimeResponse:
        calls.append((request.idempotency_key, allow_side_effect))
        return Phase08RuntimeResponse(
            runtime="legacy",
            request_hash=request.request_hash,
            output_ref=f"answer:{request.request_hash[:16]}",
            trace_ref=f"legacy-trace:{request.trace_id}",
            side_effect_ref=f"legacy-side-effect:{request.idempotency_key}" if allow_side_effect else None,
        )

    return _run


def _new_runtime() -> Phase08RunService:
    return Phase08RunService(graph=build_phase08_run_graph(checkpointer=build_phase08_test_checkpointer()))


class _UnavailableRuntime:
    def start(self, state):
        del state
        raise RuntimeError("runtime unavailable")


def test_shadow_mode_compares_same_request_hash_without_double_side_effect() -> None:
    calls: list[tuple[str, bool]] = []
    controller = Phase08CutoverController(mode="shadow", legacy_runner=_legacy_runner(calls), new_runtime=_new_runtime())
    request = _request()

    response = controller.handle(request)

    assert response.runtime == "legacy"
    assert response.request_hash == request.request_hash
    assert response.shadow_match is True
    assert calls == [(request.idempotency_key, True)]
    assert controller.side_effect_ledger.claimed_keys == set()


def test_canary_uses_new_runtime_once_and_keeps_legacy_shadow_dry() -> None:
    calls: list[tuple[str, bool]] = []
    controller = Phase08CutoverController(mode="canary", legacy_runner=_legacy_runner(calls), new_runtime=_new_runtime())
    request = _request()

    response = controller.handle(request)

    assert response.runtime == "phase08"
    assert response.side_effect_ref == f"side-effect:{request.idempotency_key}"
    assert response.shadow_match is True
    assert calls == [(request.idempotency_key, False)]
    assert controller.side_effect_ledger.claimed_keys == {request.idempotency_key}


def test_new_runtime_unavailable_falls_back_to_legacy_without_duplicate_claim() -> None:
    calls: list[tuple[str, bool]] = []
    controller = Phase08CutoverController(
        mode="new_default",
        legacy_runner=_legacy_runner(calls),
        new_runtime=_UnavailableRuntime(),  # type: ignore[arg-type]
    )
    request = _request()

    response = controller.handle(request)

    assert response.runtime == "legacy"
    assert response.rollback_reason == "new_runtime_unavailable:RuntimeError"
    assert response.side_effect_ref == f"legacy-side-effect:{request.idempotency_key}"
    assert controller.side_effect_ledger.claimed_keys == set()
    assert calls == [(request.idempotency_key, True)]


def test_rollback_mode_never_invokes_new_runtime() -> None:
    calls: list[tuple[str, bool]] = []
    controller = Phase08CutoverController(
        mode="rollback",
        legacy_runner=_legacy_runner(calls),
        new_runtime=_UnavailableRuntime(),  # type: ignore[arg-type]
    )
    request = _request()

    response = controller.handle(request)

    assert response.runtime == "legacy"
    assert response.shadow_trace_ref is None
    assert calls == [(request.idempotency_key, True)]


def test_new_default_rejects_duplicate_side_effect_claim() -> None:
    controller = Phase08CutoverController(mode="new_default", legacy_runner=_legacy_runner([]), new_runtime=_new_runtime())
    request = _request()

    controller.handle(request)
    with pytest.raises(Exception, match="duplicate side effect claim"):
        controller.handle(request)
