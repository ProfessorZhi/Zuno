from __future__ import annotations

import json
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage
import pytest

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
        "record_product_runtime_request",
        staticmethod(
            lambda **kwargs: {
                "status": "ACCEPTED",
                "route": "/completion",
                "mode": "new_default",
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
    assert event_types[0] == "product_runtime_record"
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
        event for event in streamed if event["type"] != "product_runtime_record"
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

    result = CompletionService.record_product_runtime_request(
        req=CompletionReq(
            user_input="Summarize the workspace evidence with citations.",
            dialog_id="dialog_phase09",
            product_mode="auto",
        ),
        login_user_id="principal-a",
    )

    assert result["status"] == "ACCEPTED"
    assert result["mode"] == "new_default"
    assert result["cutover_mode"] == "new_default"
    assert result["product_runtime_recorded"] is True
    assert result["product_shadow_recorded"] is False
    assert result["request_hash"]
    assert result["projection_event_id"] == "projection:completion-shadow"
    assert result["available_action_tokens"] == ["action-token:completion-shadow:cancel"]
    assert captured["tenant_id"] == "user:principal-a"
    assert captured["workspace_id"] == "completion"
    assert captured["conversation_id"] == "dialog_phase09"
    assert captured["principal_id"] == "principal-a"
    assert captured["active_agent_version_id"] == "completion:unified-runtime"
    assert captured["command_kind"] == "COMPLETION_RUNTIME_REQUEST"
    assert captured["payload"]["legacy_route"] == "/completion"
    assert captured["payload"]["cutover_mode"] == "new_default"
    assert "user_input" not in captured["payload"]


def test_completion_product_runtime_shadow_fail_closed(monkeypatch) -> None:
    def fail_submit(**kwargs):
        raise RuntimeError("product persistence unavailable")

    monkeypatch.setattr(ProductService, "submit_runtime_request", staticmethod(fail_submit))

    from zuno.schema.completion import CompletionReq

    result = CompletionService.record_product_runtime_request(
        req=CompletionReq(
            user_input="hello",
            dialog_id="dialog_phase09",
            product_mode="auto",
        ),
        login_user_id="principal-a",
    )

    assert result["status"] == "blocked"
    assert result["route"] == "/completion"
    assert result["mode"] == "new_default"
    assert result["cutover_mode"] == "new_default"
    assert result["product_runtime_recorded"] is False
    assert result["product_shadow_recorded"] is False
    assert result["failure_type"] == "RuntimeError"
    assert result["reason"] == "product persistence unavailable"
    assert result["request_hash"]


def test_completion_route_continues_unified_runtime_when_product_shadow_fails(tmp_path, monkeypatch) -> None:
    CompletionService.configure_unified_runtime_store_for_tests(
        SQLiteAgentRunStore(tmp_path / "completion_shadow_fail_runtime.db")
    )

    def fail_submit(**kwargs):
        del kwargs
        raise RuntimeError("product persistence unavailable")

    monkeypatch.setattr(ProductService, "submit_runtime_request", staticmethod(fail_submit))
    client = _client()

    with client.stream(
        "POST",
        "/api/v1/completion",
        json={
            "user_input": "Summarize the workspace evidence with citations.",
            "dialog_id": "dialog_phase09_shadow_failure",
            "product_mode": "auto",
        },
    ) as response:
        assert response.status_code == 200
        lines = list(response.iter_lines())

    streamed = [
        json.loads(line.removeprefix("data: ").strip())
        for line in lines
        if line.startswith("data: ")
    ]
    assert streamed[0]["type"] == "product_runtime_record"
    assert streamed[0]["data"]["status"] == "blocked"
    assert streamed[0]["data"]["product_runtime_recorded"] is False
    assert streamed[0]["data"]["product_shadow_recorded"] is False
    assert streamed[0]["data"]["failure_type"] == "RuntimeError"
    assert streamed[0]["data"]["request_hash"]
    assert "user_input" not in streamed[0]["data"]
    assert "runtime_started" in [event["type"] for event in streamed]
    assert streamed[-1]["type"] == "response_chunk"
    assert streamed[-1]["data"]["runtime_topology"] == "unified_agent_runtime"


def test_completion_cutover_mode_resolution_supports_explicit_modes(monkeypatch) -> None:
    monkeypatch.delenv("ZUNO_AGENT_RUNTIME", raising=False)
    monkeypatch.delenv("ZUNO_COMPLETION_CUTOVER_MODE", raising=False)
    assert CompletionService.resolve_cutover_mode() == "new_default"

    monkeypatch.setenv("ZUNO_COMPLETION_CUTOVER_MODE", "canary")
    assert CompletionService.resolve_cutover_mode() == "canary"

    monkeypatch.setenv("ZUNO_COMPLETION_CUTOVER_MODE", "rollback")
    assert CompletionService.resolve_cutover_mode() == "rollback"

    monkeypatch.delenv("ZUNO_COMPLETION_CUTOVER_MODE", raising=False)
    monkeypatch.setenv("ZUNO_AGENT_RUNTIME", "legacy_general_agent")
    assert CompletionService.resolve_cutover_mode() == "rollback"


def test_completion_cutover_mode_resolution_rejects_unknown_mode(monkeypatch) -> None:
    monkeypatch.setenv("ZUNO_COMPLETION_CUTOVER_MODE", "surprise")

    with pytest.raises(ValueError, match="unsupported completion cutover mode"):
        CompletionService.resolve_cutover_mode()


def test_completion_product_command_kind_tracks_cutover_mode() -> None:
    assert CompletionService._completion_product_command_kind("shadow") == (
        "SHADOW_COMPLETION_RUNTIME_REQUEST"
    )
    assert CompletionService._completion_product_command_kind("canary") == (
        "CANARY_COMPLETION_RUNTIME_REQUEST"
    )
    assert CompletionService._completion_product_command_kind("new_default") == (
        "COMPLETION_RUNTIME_REQUEST"
    )


@pytest.mark.parametrize("cutover_mode", ["shadow", "canary", "new_default"])
def test_completion_route_forwards_explicit_cutover_mode(monkeypatch, cutover_mode) -> None:
    captured = {}

    def fake_shadow(**kwargs):
        captured.update(kwargs)
        return {
            "status": "ACCEPTED",
            "route": "/completion",
            "mode": kwargs["cutover_mode"],
            "cutover_mode": kwargs["cutover_mode"],
            "command_id": "command:completion-shadow",
        }

    monkeypatch.setenv("ZUNO_COMPLETION_CUTOVER_MODE", cutover_mode)
    monkeypatch.setattr(CompletionService, "record_product_runtime_request", staticmethod(fake_shadow))

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

    assert captured["cutover_mode"] == cutover_mode


def test_completion_route_uses_legacy_runtime_in_rollback_window(monkeypatch) -> None:
    class FakeChatAgent:
        def __init__(self) -> None:
            self.stopped = False

        async def astream(self, messages):
            del messages
            yield {"type": "planning", "data": {"status": "ok"}}
            yield {"type": "response_chunk", "data": {"chunk": "legacy answer"}}

        def stop_streaming_callback(self) -> None:
            self.stopped = True

    fake_agent = FakeChatAgent()

    async def fake_create_chat_agent(req, login_user_id):
        del req, login_user_id
        return fake_agent, SimpleNamespace(
            name="legacy-agent",
            enable_memory=False,
            system_prompt="",
            product_mode="auto",
            query_method="direct",
        )

    async def fake_prepare_messages(*, req, agent_config):
        del agent_config
        return req.user_input, [HumanMessage(content=req.user_input)]

    async def fake_save_chat_history(**kwargs):
        del kwargs

    monkeypatch.setenv("ZUNO_COMPLETION_CUTOVER_MODE", "rollback")
    monkeypatch.setattr("zuno.api.v1.completion._create_chat_agent", fake_create_chat_agent)
    monkeypatch.setattr(CompletionService, "prepare_messages", fake_prepare_messages)
    monkeypatch.setattr(CompletionService, "save_memory_turn", fake_save_chat_history)
    monkeypatch.setattr("zuno.api.services.history.HistoryService.save_chat_history", fake_save_chat_history)
    monkeypatch.setattr(
        CompletionService,
        "record_product_runtime_request",
        staticmethod(lambda **kwargs: {"status": "ACCEPTED", "route": "/completion", "mode": "shadow"}),
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
        lines = list(response.iter_lines())

    streamed = [
        json.loads(line.removeprefix("data: ").strip())
        for line in lines
        if line.startswith("data: ")
    ]
    assert streamed[0]["type"] == "planning"
    assert streamed[-1]["type"] == "response_chunk"
    assert streamed[-1]["data"]["chunk"] == "legacy answer"
