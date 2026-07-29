from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.services.product import ObservabilityQueryAuthorizationError
from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.v1 import observability


class FakeProjectionQueryService:
    def get_trace_projection(
        self,
        *,
        principal,
        tenant_id: str,
        workspace_id: str,
        trace_id: str,
        stream_id: str,
    ):
        if not principal.is_admin:
            raise ObservabilityQueryAuthorizationError("observability read scope is required")
        assert principal.is_admin is True
        assert tenant_id == "tenant-a"
        assert workspace_id == "workspace-a"
        assert trace_id == "trace-a"
        assert stream_id == "stream-a"
        return {
            "trace_id": trace_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "freshness": {"complete": True, "freshness_status": "fresh"},
            "timeline": [{"payload": {"safe": "kept"}}],
            "dead_letters": [],
        }


class FakeEvalQueryService:
    def get_eval_run_projection(
        self,
        *,
        principal,
        tenant_id: str,
        workspace_id: str,
        eval_run_id: str,
    ):
        if not principal.is_admin:
            raise ObservabilityQueryAuthorizationError("eval read scope is required")
        assert tenant_id == "tenant-a"
        assert workspace_id == "workspace-a"
        assert eval_run_id == "run-a"
        return {
            "run_id": eval_run_id,
            "measurement_status": "MEASURED",
            "projection_freshness": "fresh",
        }

    def get_release_gate_report(
        self,
        *,
        principal,
        tenant_id: str,
        workspace_id: str,
        gate_id: str,
    ):
        if not principal.is_admin:
            raise ObservabilityQueryAuthorizationError("eval read scope is required")
        assert tenant_id == "tenant-a"
        assert workspace_id == "workspace-a"
        assert gate_id == "gate-a"
        return {
            "gate_id": gate_id,
            "status": "PASSED",
            "projection_freshness": "fresh",
        }


def _client(monkeypatch, *, role: str | list[str]) -> TestClient:
    app = FastAPI()
    app.include_router(observability.router, prefix="/api/v1")

    async def fake_login_user():
        return UserPayload(user_id="user-a", user_name="User A", role=role)

    app.dependency_overrides[get_login_user] = fake_login_user
    monkeypatch.setattr(
        observability,
        "_build_projection_query_service",
        lambda: FakeProjectionQueryService(),
    )
    monkeypatch.setattr(
        observability,
        "_build_eval_query_service",
        lambda: FakeEvalQueryService(),
    )
    return TestClient(app)


def test_observability_trace_query_route_returns_authorized_projection(monkeypatch) -> None:
    client = _client(monkeypatch, role="admin")

    response = client.get(
        "/api/v1/observability/traces/trace-a",
        params={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "stream_id": "stream-a",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["freshness"]["complete"] is True
    assert payload["timeline"] == [{"payload": {"safe": "kept"}}]


def test_observability_trace_query_route_rejects_non_admin(monkeypatch) -> None:
    client = _client(monkeypatch, role=[])

    response = client.get(
        "/api/v1/observability/traces/trace-a",
        params={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "stream_id": "stream-a",
        },
    )

    assert response.status_code == 403


def test_eval_run_query_route_returns_authorized_projection(monkeypatch) -> None:
    client = _client(monkeypatch, role="admin")

    response = client.get(
        "/api/v1/eval/runs/run-a",
        params={"tenant_id": "tenant-a", "workspace_id": "workspace-a"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["run_id"] == "run-a"
    assert payload["measurement_status"] == "MEASURED"


def test_eval_release_gate_query_route_returns_authorized_report(monkeypatch) -> None:
    client = _client(monkeypatch, role="admin")

    response = client.get(
        "/api/v1/eval/release-gates/gate-a",
        params={"tenant_id": "tenant-a", "workspace_id": "workspace-a"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["gate_id"] == "gate-a"
    assert payload["status"] == "PASSED"


def test_eval_query_routes_reject_non_admin(monkeypatch) -> None:
    client = _client(monkeypatch, role=[])

    response = client.get(
        "/api/v1/eval/runs/run-a",
        params={"tenant_id": "tenant-a", "workspace_id": "workspace-a"},
    )

    assert response.status_code == 403
