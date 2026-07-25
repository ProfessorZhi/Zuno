from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.router import router as api_router
from zuno.api.services import user as user_service
from zuno.api.services.capability import CapabilityService
from zuno.platform.services.capability_registry import CapabilityRegistryService


class _LoginUser:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


def test_goal03_capability_search_records_availability_selection(monkeypatch) -> None:
    async def _search(query: str, *, user_id: str, kind: str, limit: int) -> list[dict]:
        assert query == "read files"
        assert user_id == "principal-a"
        assert kind == "tool"
        assert limit == 2
        return [
            {
                "id": "tool:filesystem",
                "name": "filesystem",
                "kind": "tool",
                "status": "ready",
            }
        ]

    recorded: list[dict] = []

    monkeypatch.setattr(CapabilityRegistryService, "search", staticmethod(_search))
    monkeypatch.setattr(
        CapabilityService,
        "record_search_selection",
        staticmethod(lambda **kwargs: recorded.append(kwargs)),
    )

    app = FastAPI()
    app.include_router(api_router)
    app.dependency_overrides[user_service.get_login_user] = lambda: _LoginUser("principal-a")

    client = TestClient(app)
    response = client.post(
        "/api/v1/capability/search",
        json={"query": "read files", "kind": "tool", "limit": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert body["data"][0]["id"] == "tool:filesystem"
    assert recorded == [
        {
            "user_id": "principal-a",
            "query": "read files",
            "kind": "tool",
            "limit": 2,
            "results": body["data"],
        }
    ]


def test_goal03_capability_router_is_registered_in_main_api_router() -> None:
    router_text = (
        __import__("pathlib").Path("src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    )
    assert "capability," in router_text
    assert "router.include_router(capability.router)" in router_text
