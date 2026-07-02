from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.api.v1.workspace import router as workspace_router


def _client() -> TestClient:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    app = FastAPI()
    app.include_router(workspace_router, prefix="/api/v1")
    app.dependency_overrides[get_login_user] = lambda: UserPayload(
        user_id="user_retrieval_observability",
        user_name="Retrieval Observability User",
        role="admin",
    )
    return TestClient(app)


def _seed_index(client: TestClient, *, workspace_id: str, knowledge_space_id: str) -> None:
    file_id = f"file_{knowledge_space_id}"
    file_response = client.post(
        "/api/v1/workspace/file",
        json={
            "workspace_id": workspace_id,
            "file_id": file_id,
            "name": "renewal-observability.md",
            "mime_type": "text/markdown",
            "content": "Renewal notice must be sent 30 days before the contract anniversary.",
        },
    )
    assert file_response.status_code == 200

    ingest_response = client.post(
        "/api/v1/workspace/ingest",
        json={
            "workspace_id": workspace_id,
            "file_id": file_id,
            "knowledge_space_id": knowledge_space_id,
        },
    )
    assert ingest_response.status_code == 200


def _create_task(
    client: TestClient,
    *,
    task_id: str,
    workspace_id: str,
    knowledge_space_id: str,
    profile: str,
) -> dict:
    response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "What is the renewal notice requirement?",
            "model_id": "model-local",
            "session_id": f"session_{task_id}",
            "workspace_id": workspace_id,
            "task_id": task_id,
            "trace_id": f"trace_{task_id}",
            "goal": "retrieval observability answer",
            "product_mode": "contract_review",
            "knowledge_space_ids": [knowledge_space_id],
            "knowledge_space_profiles": [
                {
                    "knowledge_space_id": knowledge_space_id,
                    "retrieval_profile": profile,
                }
            ],
            "uploaded_file_ids": [f"file_{knowledge_space_id}"],
            "plugins": [],
            "mcp_servers": [],
        },
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_workspace_retrieval_observability_summary_compares_standard_and_deep_runs() -> None:
    client = _client()
    _seed_index(client, workspace_id="workspace_retrieval_obs", knowledge_space_id="ks_retrieval_obs")
    _create_task(
        client,
        task_id="task_retrieval_obs_standard",
        workspace_id="workspace_retrieval_obs",
        knowledge_space_id="ks_retrieval_obs",
        profile="standard",
    )
    _create_task(
        client,
        task_id="task_retrieval_obs_deep",
        workspace_id="workspace_retrieval_obs",
        knowledge_space_id="ks_retrieval_obs",
        profile="deep",
    )

    response = client.get("/api/v1/workspace/retrieval-observability")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["summary"]["total_runs"] == 2
    assert payload["summary"]["requested_standard_runs"] == 1
    assert payload["summary"]["requested_deep_runs"] == 1
    assert payload["summary"]["deep_without_graph_runs"] >= 0
    assert payload["summary"]["avg_citation_coverage"] >= 0
    assert payload["summary"]["avg_estimated_cost"] >= 0
    assert payload["profiles"]["standard"]["runs"] >= 1
    assert "deep" in payload["profiles"]
    assert "deep_without_graph" in payload["profiles"]
    assert "deep_vs_standard" in payload["comparison"]

    recent = {run["task_id"]: run for run in payload["recent_runs"]}
    assert recent["task_retrieval_obs_standard"]["requested_profile"] == "standard"
    assert recent["task_retrieval_obs_deep"]["requested_profile"] == "deep"
    assert recent["task_retrieval_obs_deep"]["effective_profile"] in {"deep", "deep_without_graph"}
    assert "citation_coverage" in recent["task_retrieval_obs_deep"]
    assert "graph_used" in recent["task_retrieval_obs_deep"]
    assert "estimated_cost" in recent["task_retrieval_obs_deep"]
    assert "eval_status" in recent["task_retrieval_obs_deep"]


def test_workspace_retrieval_observability_exposes_benchmark_metrics_without_faking_dataset() -> None:
    client = _client()
    _seed_index(client, workspace_id="workspace_benchmark_obs", knowledge_space_id="ks_benchmark_obs")
    _create_task(
        client,
        task_id="task_benchmark_obs_standard",
        workspace_id="workspace_benchmark_obs",
        knowledge_space_id="ks_benchmark_obs",
        profile="standard",
    )
    _create_task(
        client,
        task_id="task_benchmark_obs_deep",
        workspace_id="workspace_benchmark_obs",
        knowledge_space_id="ks_benchmark_obs",
        profile="deep",
    )
    WorkspaceTaskRuntimeService._release_evals["task_benchmark_obs_deep"] = {
        "status": "pass",
        "dataset_version": "internal_kb_v1",
        "case_count": 4,
        "metric_results": {
            "retrieval_recall_at_k": {"value": 0.75, "passed": True},
            "context_precision_at_k": {"value": 0.5, "passed": True},
            "mrr_at_k": {"value": 0.8, "passed": True},
            "ndcg_at_k": {"value": 0.7, "passed": True},
            "answer_correctness": {"value": 0.9, "passed": True},
            "source_span_accuracy": {"value": 0.6, "passed": True},
            "unsupported_claim_rate": {"value": 0.05, "passed": True},
        },
    }

    response = client.get("/api/v1/workspace/retrieval-observability")

    assert response.status_code == 200
    benchmark = response.json()["data"]["benchmark"]
    assert benchmark["status"] == "measured"
    assert benchmark["dataset_version"] == "internal_kb_v1"
    assert benchmark["sample_count"] == 4
    metrics = {metric["key"]: metric for metric in benchmark["metrics"]}
    for required_metric in (
        "retrieval_recall_at_k",
        "context_precision_at_k",
        "mrr_at_k",
        "ndcg_at_k",
        "answer_correctness",
        "citation_coverage",
        "source_span_accuracy",
        "unsupported_claim_rate",
        "latency_p50_ms",
        "latency_p95_ms",
        "estimated_cost",
    ):
        assert required_metric in metrics
    assert metrics["retrieval_recall_at_k"]["label"] == "Recall@5"
    assert metrics["context_precision_at_k"]["label"] == "Precision@5"
    assert metrics["source_span_accuracy"]["value"] == 0.6
    assert metrics["source_span_accuracy"]["status"] == "measured"
    assert metrics["citation_coverage"]["status"] == "runtime_observed"
    assert metrics["latency_p95_ms"]["status"] == "runtime_observed"


def test_frontend_dashboard_declares_agentic_retrieval_observability_panel() -> None:
    root = Path(__file__).resolve().parents[2]
    workspace_api = (root / "apps/web/src/apis/workspace.ts").read_text(encoding="utf-8")
    dashboard = (root / "apps/web/src/pages/dashboard/dashboard.vue").read_text(encoding="utf-8")

    assert "getWorkspaceRetrievalObservabilityAPI" in workspace_api
    assert "WorkspaceRetrievalObservabilitySummary" in workspace_api
    assert "getWorkspaceRetrievalObservabilityAPI" in dashboard
    assert "Agentic Retrieval" in dashboard
    for required_copy in (
        "standard",
        "deep",
        "deep_without_graph",
        "citation_coverage",
        "graph_used_rate",
        "cost_delta",
        "Benchmark Metrics",
        "Recall@5",
        "Precision@5",
        "MRR",
        "NDCG",
        "Answer Correctness",
        "Source Span Accuracy",
        "Unsupported Claim Rate",
        "Latency p50",
        "Latency p95",
        "Estimated Cost",
    ):
        assert required_copy in dashboard
