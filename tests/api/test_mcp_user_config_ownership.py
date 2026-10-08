"""MCP user config 的归属（IDOR）回归测试。

Round 020 的 IMP-020-02 记录了：`GET /mcp_user_config/{config_id}` 与
`DELETE /mcp_user_config/delete` 两条路由拿到了 `login_user` 却从不使用，
DAO/Service 也只按 `config_id` 过滤，因此任意登录用户可以凭 id 读取或删除
他人的 MCP 用户配置。

这里锁三件事：
1. DAO 的按 id 查询 / 删除必须同时按 `user_id` 过滤（静态断言，因为下面的
   路由测试会 monkeypatch DAO，绕开真实 SQL）。
2. 路由必须把登录用户的 `user_id` 透传到 Service。
3. 他人记录与不存在的记录返回同一个错误，不泄漏「该 id 是否存在」。
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class _Record:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def to_dict(self) -> dict:
        return dict(self._payload)


class _FakeDao:
    """按 (config_id, user_id) 成对命中的 DAO 替身。

    真实 DAO 的作用域在下面由静态测试锁定；这里只负责证明「路由确实把登录
    用户的 user_id 传下来了」——若路由漏传，成对查询必然落空，测试即红。
    """

    records: dict = {}

    def __init__(self) -> None:
        self.lookups: list = []
        self.deletes: list = []

    async def get_mcp_user_config_from_id(self, config_id, user_id):
        self.lookups.append((config_id, user_id))
        return self.records.get((config_id, user_id))

    async def delete_mcp_user_config(self, config_id, user_id):
        self.deletes.append((config_id, user_id))
        self.records.pop((config_id, user_id), None)


def _client(monkeypatch, user_id: str, records: dict) -> tuple[TestClient, _FakeDao]:
    from zuno.api.services.user import UserPayload, get_login_user
    from zuno.api.v1.mcp_user_config import router

    dao = _FakeDao()
    dao.records = dict(records)
    monkeypatch.setattr("zuno.api.services.mcp_user_config.MCPUserConfigDao", dao)

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_login_user] = lambda: UserPayload(
        user_id=user_id,
        role="admin",
        user_name=user_id,
    )
    return TestClient(app), dao


def test_dao_id_lookups_are_scoped_by_user_id() -> None:
    source = " ".join(_read("src/backend/zuno/platform/database/dao/mcp_user_config.py").split())

    for method in ("get_mcp_user_config_from_id", "delete_mcp_user_config"):
        body = source.split(f"async def {method}", 1)[1].split("async def ", 1)[0]
        assert "MCPUserConfigTable.id == config_id" in body, f"{method} 必须按 id 过滤"
        assert "MCPUserConfigTable.user_id == user_id" in body, f"{method} 必须同时按 user_id 过滤"


def test_get_route_passes_login_user_id_to_service(monkeypatch) -> None:
    client, dao = _client(
        monkeypatch,
        user_id="user-a",
        records={("cfg-a", "user-a"): _Record({"id": "cfg-a", "config": []})},
    )

    response = client.get("/mcp_user_config/cfg-a")

    assert response.status_code == 200
    body = response.json()
    assert body["status_code"] == 200
    assert body["data"]["id"] == "cfg-a"
    assert dao.lookups == [("cfg-a", "user-a")]


def test_get_route_denies_foreign_config(monkeypatch) -> None:
    client, _ = _client(
        monkeypatch,
        user_id="user-b",
        records={("cfg-a", "user-a"): _Record({"id": "cfg-a", "config": [{"key": "token", "value": "secret"}]})},
    )

    response = client.get("/mcp_user_config/cfg-a")

    body = response.json()
    assert body["status_code"] == 500
    assert body["status_message"] == "No permission to access this MCP user config."
    assert body["data"] is None


def test_delete_route_denies_foreign_config_without_touching_dao(monkeypatch) -> None:
    records = {("cfg-a", "user-a"): _Record({"id": "cfg-a", "config": []})}
    client, dao = _client(monkeypatch, user_id="user-b", records=records)

    response = client.request("DELETE", "/mcp_user_config/delete", json={"config_id": "cfg-a"})

    body = response.json()
    assert body["status_code"] == 500
    assert body["status_message"] == "No permission to access this MCP user config."
    assert dao.deletes == []
    assert ("cfg-a", "user-a") in dao.records


def test_delete_route_deletes_own_config(monkeypatch) -> None:
    records = {("cfg-a", "user-a"): _Record({"id": "cfg-a", "config": []})}
    client, dao = _client(monkeypatch, user_id="user-a", records=records)

    response = client.request("DELETE", "/mcp_user_config/delete", json={"config_id": "cfg-a"})

    assert response.json()["status_code"] == 200
    assert dao.lookups == [("cfg-a", "user-a")]
    assert dao.deletes == [("cfg-a", "user-a")]


def test_missing_config_and_foreign_config_share_one_error(monkeypatch) -> None:
    """不区分「不存在」与「属于他人」，避免用 id 探测他人记录是否存在。"""

    client, _ = _client(monkeypatch, user_id="user-b", records={})

    response = client.get("/mcp_user_config/cfg-does-not-exist")

    assert response.json()["status_message"] == "No permission to access this MCP user config."
