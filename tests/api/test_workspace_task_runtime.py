from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.v1.workspace import router as workspace_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(workspace_router, prefix="/api/v1")
    app.dependency_overrides[get_login_user] = lambda: UserPayload(
        user_id="user_phase03",
        user_name="Phase03 User",
        role="admin",
    )
    return TestClient(app)


def test_workspace_task_runtime_links_task_events_artifact_and_feedback() -> None:
    client = _client()

    create_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Summarize the supplier contract and create a cited report",
            "model_id": "model-local",
            "session_id": "session_phase03",
            "workspace_id": "workspace_phase03",
            "goal": "contract review",
            "product_mode": "contract_review",
            "uploaded_file_ids": ["file_contract"],
            "knowledge_space_ids": ["ks_contracts"],
            "output_contract": {
                "artifact_kinds": ["markdown"],
                "citation_required": True,
                "trace_required": True,
                "format": "markdown",
            },
            "plugins": [],
            "mcp_servers": [],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["data"]
    task = created["task"]
    artifact = created["artifacts"][0]
    task_id = task["task_id"]
    trace_id = task["trace_id"]

    assert task["workspace_id"] == "workspace_phase03"
    assert task["session_id"] == "session_phase03"
    assert task["status"] == "completed"
    assert task_id.startswith("task_")
    assert trace_id.startswith("trace_")
    assert artifact["task_id"] == task_id
    assert artifact["workspace_id"] == "workspace_phase03"
    assert artifact["kind"] == "markdown"
    assert artifact["trace_id"] == trace_id

    task_response = client.get(f"/api/v1/workspace/task/{task_id}")
    assert task_response.status_code == 200
    task_payload = task_response.json()["data"]
    assert task_payload["task"]["task_id"] == task_id
    assert task_payload["task"]["trace_id"] == trace_id
    assert task_payload["artifact_ids"] == [artifact["artifact_id"]]

    events_response = client.get(f"/api/v1/workspace/task/{task_id}/events")
    assert events_response.status_code == 200
    events = events_response.json()["data"]
    event_types = [event["type"] for event in events]
    assert event_types == [
        "task_started",
        "planning",
        "retrieval",
        "answer",
        "artifact_created",
        "eval_diagnostic",
        "task_completed",
    ]
    assert {event["task_id"] for event in events} == {task_id}
    assert {event["trace_id"] for event in events} == {trace_id}

    artifact_response = client.get(f"/api/v1/workspace/artifact/{artifact['artifact_id']}")
    assert artifact_response.status_code == 200
    artifact_payload = artifact_response.json()["data"]
    assert artifact_payload["artifact"]["artifact_id"] == artifact["artifact_id"]
    assert artifact_payload["artifact"]["task_id"] == task_id
    assert artifact_payload["content"].startswith("# contract review")

    feedback_response = client.post(
        "/api/v1/workspace/feedback",
        json={
            "task_id": task_id,
            "rating": 5,
            "label": "useful",
            "comment": "Traceable enough for PHASE03.",
            "dataset_candidate": True,
        },
    )
    assert feedback_response.status_code == 200
    feedback = feedback_response.json()["data"]
    assert feedback["task_id"] == task_id
    assert feedback["feedback_id"].startswith("feedback_")

    events_after_feedback = client.get(f"/api/v1/workspace/task/{task_id}/events").json()["data"]
    assert events_after_feedback[-1]["type"] == "feedback_received"
    assert events_after_feedback[-1]["payload"]["feedback_id"] == feedback["feedback_id"]


def test_workspace_task_event_stream_emits_frontend_trace_payloads() -> None:
    client = _client()

    created = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Find the renewal risk in the contract",
            "model_id": "model-local",
            "session_id": "session_stream",
            "workspace_id": "workspace_stream",
            "goal": "contract review",
            "product_mode": "contract_review",
            "knowledge_space_ids": ["ks_contracts"],
            "uploaded_file_ids": ["file_contract"],
            "plugins": [],
            "mcp_servers": [],
        },
    ).json()["data"]
    task_id = created["task"]["task_id"]
    trace_id = created["task"]["trace_id"]
    artifact_id = created["artifact_ids"][0]

    with client.stream("GET", f"/api/v1/workspace/task/{task_id}/events/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        raw_lines = list(response.iter_lines())

    streamed_payloads = [
        json.loads(line.removeprefix("data: ").strip())
        for line in raw_lines
        if line.startswith("data: ")
    ]
    streamed_events = [payload["event"] for payload in streamed_payloads]
    assert streamed_events == [
        "task_started",
        "planning",
        "retrieval",
        "answer",
        "artifact_created",
        "eval_diagnostic",
        "task_completed",
    ]
    assert {payload["data"]["task_id"] for payload in streamed_payloads} == {task_id}
    assert {payload["data"]["trace_id"] for payload in streamed_payloads} == {trace_id}
    artifact_event = next(payload for payload in streamed_payloads if payload["event"] == "artifact_created")
    assert artifact_event["data"]["artifact_id"] == artifact_id
    assert artifact_event["data"]["status"] == "finalizing"
