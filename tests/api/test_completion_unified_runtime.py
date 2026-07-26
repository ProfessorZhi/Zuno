from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.agent.runtime import SQLiteAgentRunStore
from zuno.api.services.completion import CompletionService
from zuno.api.services.product import (
    ProductAvailableActionResult,
    ProductProjectionResult,
    ProductRuntimeRequestResult,
    ProductService,
)
from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.v1.completion import router as completion_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(completion_router, prefix="/api/v1")
    app.dependency_overrides[get_login_user] = lambda: UserPayload(
        user_id="user_phase11_completion",
        user_name="Phase11 Completion User",
        role="admin",
    )
    return TestClient(app)


def test_completion_route_streams_unified_runtime_events(tmp_path, monkeypatch) -> None:
    CompletionService.configure_unified_runtime_store_for_tests(
        SQLiteAgentRunStore(tmp_path / "completion_unified_runtime.db")
    )
    monkeypatch.setattr(
        CompletionService,
        "record_product_runtime_shadow",
        staticmethod(
            lambda **kwargs: {
                "status": "ACCEPTED",
                "route": "/completion",
                "mode": "shadow",
                "command_id": "command:completion-shadow",
            }
        ),
    )
    client = _client()

    with client.stream(
        "POST",
        "/api/v1/completion",
        json={
            "user_input": "Summarize the workspace evidence with citations.",
            "dialog_id": "dialog_phase11_completion",
            "product_mode": "auto",
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        lines = list(response.iter_lines())

    streamed = [
        json.loads(line.removeprefix("data: ").strip())
        for line in lines
        if line.startswith("data: ")
    ]
    event_types = [event["type"] for event in streamed]
    assert event_types[0] == "product_runtime_shadow"
    assert streamed[0]["data"]["command_id"] == "command:completion-shadow"
    assert "runtime_started" in event_types
    assert "node_started" in event_types
    assert "model_call" in event_types
    assert "reflection" in event_types
    assert "answer_chunk" in event_types
    assert "runtime_node" in event_types
    assert "runtime_completed" in event_types
    assert event_types[-1] == "response_chunk"
    runtime_events = [
        event for event in streamed if event["type"] != "product_runtime_shadow"
    ]
    assert {event["data"]["runtime_topology"] for event in runtime_events} == {"unified_agent_runtime"}
    assert streamed[-1]["data"]["finalization_status"] in {"finalized", "abstained"}
    assert streamed[-1]["data"]["chunk"] != "Unified runtime completed."
    assert streamed[-1]["data"]["chunk"]


def test_completion_product_runtime_shadow_records_product_command(monkeypatch) -> None:
    captured = {}

    def fake_submit(**kwargs):
        captured.update(kwargs)
        return ProductRuntimeRequestResult(
            command_id="command:completion-shadow",
            receipt_id="receipt:completion-shadow",
            status="ACCEPTED",
            projection=ProductProjectionResult(
                projection_event_id="projection:completion-shadow",
                stream_cursor_id="cursor:completion-shadow",
                stream_sequence_no=1,
                freshness="current",
            ),
            available_actions=(
                ProductAvailableActionResult(
                    action="cancel",
                    action_token_id="action-token:completion-shadow:cancel",
                    target_ref="completion-runtime-request:dialog_phase09:shadow",
                    expires_at="2026-07-26T00:00:00+00:00",
                ),
            ),
        )

    monkeypatch.setattr(ProductService, "submit_runtime_request", staticmethod(fake_submit))

    from zuno.schema.completion import CompletionReq

    result = CompletionService.record_product_runtime_shadow(
        req=CompletionReq(
            user_input="Summarize the workspace evidence with citations.",
            dialog_id="dialog_phase09",
            product_mode="auto",
        ),
        login_user_id="principal-a",
    )

    assert result["status"] == "ACCEPTED"
    assert result["mode"] == "shadow"
    assert result["projection_event_id"] == "projection:completion-shadow"
    assert result["available_action_tokens"] == ["action-token:completion-shadow:cancel"]
    assert captured["tenant_id"] == "user:principal-a"
    assert captured["workspace_id"] == "completion"
    assert captured["conversation_id"] == "dialog_phase09"
    assert captured["principal_id"] == "principal-a"
    assert captured["active_agent_version_id"] == "completion:unified-runtime"
    assert captured["command_kind"] == "SHADOW_COMPLETION_RUNTIME_REQUEST"
    assert captured["payload"]["legacy_route"] == "/completion"
    assert "user_input" not in captured["payload"]


def test_completion_product_runtime_shadow_fail_closed(monkeypatch) -> None:
    def fail_submit(**kwargs):
        raise RuntimeError("product persistence unavailable")

    monkeypatch.setattr(ProductService, "submit_runtime_request", staticmethod(fail_submit))

    from zuno.schema.completion import CompletionReq

    result = CompletionService.record_product_runtime_shadow(
        req=CompletionReq(
            user_input="hello",
            dialog_id="dialog_phase09",
            product_mode="auto",
        ),
        login_user_id="principal-a",
    )

    assert result == {
        "status": "blocked",
        "route": "/completion",
        "mode": "shadow",
        "reason": "product persistence unavailable",
    }
