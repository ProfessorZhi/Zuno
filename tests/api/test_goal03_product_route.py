from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.router import router as api_router
from zuno.api.services import user as user_service
from zuno.api.services.product import ProductRuntimeRequestResult, ProductService


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


def test_goal03_product_router_is_registered_in_main_api_router() -> None:
    router_text = (
        __import__("pathlib").Path("src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    )
    assert "product," in router_text
    assert "router.include_router(product.router)" in router_text
