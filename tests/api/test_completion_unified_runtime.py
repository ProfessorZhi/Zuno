from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.agent.runtime import SQLiteAgentRunStore
from zuno.api.services.completion import CompletionService
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


def test_completion_route_streams_unified_runtime_events(tmp_path) -> None:
    CompletionService.configure_unified_runtime_store_for_tests(
        SQLiteAgentRunStore(tmp_path / "completion_unified_runtime.db")
    )
    client = _client()

    with client.stream(
        "POST",
        "/api/v1/completion",
        json={
            "user_input": "Summarize the workspace evidence with citations.",
            "dialog_id": "dialog_phase11_completion",
            "product_mode": "unified_runtime",
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
    assert "runtime_started" in event_types
    assert "runtime_node" in event_types
    assert "runtime_completed" in event_types
    assert event_types[-1] == "response_chunk"
    assert {event["data"]["runtime_topology"] for event in streamed} == {"unified_agent_runtime"}
    assert streamed[-1]["data"]["finalization_status"] in {"finalized", "abstained"}
