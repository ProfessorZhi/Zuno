from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.router import router as api_router
from zuno.api.services import user as user_service
from zuno.api.services.product import (
    ProductAvailableActionResult,
    ProductProjectionResult,
    ProductRuntimeRequestResult,
    ProductService,
    ProductStreamEventResult,
)


class _LoginUser:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


def test_goal03_product_runtime_request_route_is_exposed_and_returns_receipt(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    monkeypatch.setattr(
        ProductService,
        "submit_runtime_request",
        staticmethod(
            lambda **kwargs: ProductRuntimeRequestResult(
                command_id="command:client:1",
                receipt_id="command:client:1:receipt:1",
                status="ACCEPTED",
                projection=ProductProjectionResult(
                    projection_event_id="projection:command:client:1:accepted",
                    stream_cursor_id="cursor:command:client:1:1",
                    stream_sequence_no=1,
                    freshness="current",
                ),
                available_actions=(
                    ProductAvailableActionResult(
                        action="cancel",
                        action_token_id="action-token:command:client:1:cancel",
                        target_ref="runtime-request:1",
                        expires_at="2026-07-26T00:00:00+00:00",
                    ),
                ),
            )
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/product/runtime-requests",
        json={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "conversation_id": "conversation-a",
            "client_request_id": "client:1",
            "runtime_request_ref": "runtime-request:1",
            "raw_intent_ref": "intent:1",
            "command_kind": "CREATE_RUNTIME_REQUEST",
            "active_agent_version_id": "agent-version:1",
            "payload": {"query": "renewal"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert body["data"]["receipt_id"] == "command:client:1:receipt:1"
    assert body["data"]["status"] == "ACCEPTED"
    assert body["data"]["projection"] == {
        "projection_event_id": "projection:command:client:1:accepted",
        "stream_cursor_id": "cursor:command:client:1:1",
        "stream_sequence_no": 1,
        "freshness": "current",
    }
    assert body["data"]["available_actions"][0]["action"] == "cancel"
    assert body["data"]["available_actions"][0]["action_token_id"] == "action-token:command:client:1:cancel"


def test_goal03_product_stream_events_route_uses_last_event_id(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    captured = {}

    def fake_events(**kwargs):
        captured.update(kwargs)
        return (
            ProductStreamEventResult(
                event_id="projection:1",
                event_type="DELTA",
                sequence_no=2,
                redaction_decision_ref="redaction:1",
                resync_required=False,
            ),
        )

    monkeypatch.setattr(ProductService, "list_stream_events", staticmethod(fake_events))

    client = TestClient(app)
    response = client.get(
        "/api/v1/product/stream-events?tenant_id=tenant-a&workspace_id=workspace-a",
        headers={"Last-Event-ID": "cursor:previous"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert captured == {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "principal_id": "principal-a",
        "last_event_id": "cursor:previous",
    }
    assert body["data"]["events"][0]["event_id"] == "projection:1"
    assert body["data"]["events"][0]["event_type"] == "DELTA"


def test_goal03_product_stream_route_returns_sse_projection_events(monkeypatch) -> None:
    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    captured = {}

    def fake_events(**kwargs):
        captured.update(kwargs)
        return (
            ProductStreamEventResult(
                event_id="projection:1",
                event_type="RESYNC_REQUIRED",
                sequence_no=2,
                redaction_decision_ref="redaction:resync-required",
                resync_required=True,
            ),
        )

    monkeypatch.setattr(ProductService, "list_stream_events", staticmethod(fake_events))

    client = TestClient(app)
    response = client.get(
        "/api/v1/product/stream?tenant_id=tenant-a&workspace_id=workspace-a",
        headers={"Last-Event-ID": "cursor:expired"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["connection"] == "keep-alive"
    assert response.headers["x-accel-buffering"] == "no"
    assert captured["last_event_id"] == "cursor:expired"
    assert "retry: 1000" in response.text
    assert "id: projection:1" in response.text
    assert "event: RESYNC_REQUIRED" in response.text
    assert '"resync_required": true' in response.text
    assert "event: HEARTBEAT" in response.text
    assert '"event_type":"HEARTBEAT"' in response.text


def test_goal03_product_router_is_registered_in_main_api_router() -> None:
    router_text = (
        __import__("pathlib").Path("src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    )
    assert "product," in router_text
    assert "router.include_router(product.router)" in router_text
