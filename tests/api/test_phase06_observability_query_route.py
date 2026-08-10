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

    def get_eval_metrics_projection(self, *, principal, tenant_id: str, workspace_id: str, eval_run_id: str):
        if not principal.is_admin:
            raise ObservabilityQueryAuthorizationError("eval read scope is required")
        return {"run_id": eval_run_id, "metric_status_counts": {"MEASURED": 5}}

    def get_eval_failures_projection(self, *, principal, tenant_id: str, workspace_id: str, eval_run_id: str):
        if not principal.is_admin:
            raise ObservabilityQueryAuthorizationError("eval read scope is required")
        return {"run_id": eval_run_id, "failure_buckets": []}

    def get_comparison_report(self, *, principal, tenant_id: str, workspace_id: str, comparison_hash: str):
        if not principal.is_admin:
            raise ObservabilityQueryAuthorizationError("eval read scope is required")
        return {"comparison_hash": comparison_hash, "status": "PASSED"}

    def get_evidence_report(self, *, principal, tenant_id: str, workspace_id: str, evidence_id: str):
        if not principal.is_admin:
            raise ObservabilityQueryAuthorizationError("eval read scope is required")
        return {"evidence_id": evidence_id, "artifact_hash": "a" * 64}


def _client(monkeypatch, *, role: str | list[str]) -> TestClient:
    app = FastAPI()
    app.include_router(observability.router, prefix="/api/v1")

    # The route contract supplies its own authenticated payload. Keep the
    # role lookup at the auth boundary in-memory so non-admin cases do not
    # open a real PostgreSQL connection while exercising authorization.
    monkeypatch.setattr(
        "zuno.api.services.user.UserRoleDao.get_user_roles",
        lambda _user_id: [],
    )

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


def test_eval_metrics_failures_comparison_and_evidence_routes_return_authorized_reports(monkeypatch) -> None:
    client = _client(monkeypatch, role="admin")
    params = {"tenant_id": "tenant-a", "workspace_id": "workspace-a"}

    metrics = client.get("/api/v1/eval/runs/run-a/metrics", params=params)
    failures = client.get("/api/v1/eval/runs/run-a/failures", params=params)
    comparison = client.get("/api/v1/eval/comparisons/comparison-a", params=params)
    evidence = client.get("/api/v1/evidence/evidence-a", params=params)

    assert metrics.status_code == 200
    assert metrics.json()["data"]["metric_status_counts"] == {"MEASURED": 5}
    assert failures.status_code == 200
    assert failures.json()["data"]["failure_buckets"] == []
    assert comparison.status_code == 200
    assert comparison.json()["data"]["comparison_hash"] == "comparison-a"
    assert evidence.status_code == 200
    assert evidence.json()["data"]["evidence_id"] == "evidence-a"
