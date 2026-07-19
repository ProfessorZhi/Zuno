from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
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
    product_event_types = [
        event["type"]
        for event in events
        if event["payload"].get("runtime_topology") != "unified_agent_runtime"
    ]
    assert product_event_types == [
        "task_started",
        "planning",
        "retrieval",
        "answer",
        "artifact_created",
        "eval_diagnostic",
        "task_completed",
    ]
    assert "runtime_started" in event_types
    assert "runtime_node" in event_types
    assert "runtime_completed" in event_types
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
    product_streamed_events = [
        payload["event"]
        for payload in streamed_payloads
        if payload["data"].get("runtime_topology") != "unified_agent_runtime"
    ]
    assert product_streamed_events == [
        "task_started",
        "planning",
        "retrieval",
        "answer",
        "artifact_created",
        "eval_diagnostic",
        "task_completed",
    ]
    assert "runtime_started" in streamed_events
    assert "runtime_node" in streamed_events
    assert "runtime_completed" in streamed_events
    assert {payload["data"]["task_id"] for payload in streamed_payloads} == {task_id}
    assert {payload["data"]["trace_id"] for payload in streamed_payloads} == {trace_id}
    artifact_event = next(payload for payload in streamed_payloads if payload["event"] == "artifact_created")
    assert artifact_event["data"]["artifact_id"] == artifact_id
    assert artifact_event["data"]["status"] == "finalizing"


def test_workspace_task_runtime_exposes_phase06_lifecycle_download_and_recovery() -> None:
    client = _client()

    lifecycle_response = client.get("/api/v1/workspace/task-lifecycle")
    assert lifecycle_response.status_code == 200
    lifecycle = lifecycle_response.json()["data"]
    assert lifecycle["states"] == [
        "pending",
        "running",
        "approval_required",
        "recoverable_failed",
        "cancelled",
        "completed",
    ]
    assert lifecycle["status_mapping"]["approval_waiting"] == "approval_required"
    assert lifecycle["recovery_actions"]["recoverable_failed"] == [
        "retry_task",
        "download_trace",
        "send_feedback",
    ]

    completed_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Create a downloadable workspace report",
            "model_id": "model-local",
            "session_id": "session_phase06_download",
            "workspace_id": "workspace_phase06_download",
            "task_id": "task_phase06_download",
            "trace_id": "trace_phase06_download",
            "goal": "downloadable report",
            "product_mode": "general_agent",
            "plugins": [],
            "mcp_servers": [],
        },
    )
    assert completed_response.status_code == 200
    completed = completed_response.json()["data"]
    artifact = completed["artifacts"][0]
    artifact_id = artifact["artifact_id"]
    assert completed["lifecycle"]["state"] == "completed"
    assert completed["lifecycle"]["downloadable_artifact_ids"] == [artifact_id]

    download_response = client.get(f"/api/v1/workspace/artifact/{artifact_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-disposition"].startswith("attachment;")
    assert "downloadable-report" in download_response.headers["content-disposition"]
    assert download_response.text.startswith("# downloadable report")

    feedback_response = client.post(
        "/api/v1/workspace/feedback",
        json={
            "task_id": "task_phase06_download",
            "rating": 5,
            "label": "helpful",
            "dataset_candidate": True,
        },
    )
    assert feedback_response.status_code == 200
    feedback = feedback_response.json()["data"]
    linked_snapshot = client.get("/api/v1/workspace/task/task_phase06_download").json()["data"]
    feedback_event = client.get("/api/v1/workspace/task/task_phase06_download/events").json()["data"][-1]
    assert linked_snapshot["feedback_ids"] == [feedback["feedback_id"]]
    assert linked_snapshot["task"]["trace_id"] == artifact["trace_id"] == feedback_event["trace_id"]

    client.post(
        "/api/v1/workspace/file",
        json={
            "workspace_id": "workspace_phase06_recover",
            "file_id": "file_phase06_recover",
            "name": "security.md",
            "mime_type": "text/markdown",
            "content": "Security incidents require notice within 24 hours.",
        },
    )
    client.post(
        "/api/v1/workspace/ingest",
        json={
            "workspace_id": "workspace_phase06_recover",
            "file_id": "file_phase06_recover",
            "knowledge_space_id": "ks_phase06_recover",
        },
    )
    failure_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Which indemnity waiver exists?",
            "model_id": "model-local",
            "session_id": "session_phase06_recover",
            "workspace_id": "workspace_phase06_recover",
            "task_id": "task_phase06_recover",
            "trace_id": "trace_phase06_recover",
            "goal": "recoverable missing citation",
            "product_mode": "contract_review",
            "knowledge_space_ids": ["ks_phase06_recover"],
            "plugins": [],
            "mcp_servers": [],
        },
    )
    assert failure_response.status_code == 200
    failed = failure_response.json()["data"]
    assert failed["task"]["status"] == "failed"
    assert failed["lifecycle"]["state"] == "recoverable_failed"
    assert failed["lifecycle"]["recoverable"] is True
    assert failed["lifecycle"]["recovery_actions"] == [
        "retry_task",
        "download_trace",
        "send_feedback",
    ]
    assert failed["runtime"]["status"] == "failed"
    assert failed["runtime"]["failure"]["task_id"] == "task_phase06_recover"
    assert failed["runtime"]["failure"]["trace_id"] == "trace_phase06_recover"
    assert failed["runtime"]["failure"]["recoverable"] is True
    assert failed["runtime"]["failure"]["error"] == "output_security_block"
    failed_events = client.get("/api/v1/workspace/task/task_phase06_recover/events").json()["data"]
    assert failed_events[-1]["payload"]["lifecycle_state"] == "recoverable_failed"


def test_workspace_file_ingest_and_approval_runtime_closes_phase03_surface(monkeypatch) -> None:
    async def fake_create_workspace_session(payload):
        return {
            "session_id": payload.session_id,
            "user_id": payload.user_id,
            "agent": payload.agent,
            "contexts": payload.contexts,
        }

    monkeypatch.setattr(
        "zuno.api.v1.workspace.WorkSpaceSessionService.create_workspace_session",
        fake_create_workspace_session,
    )

    client = _client()

    session_response = client.post(
        "/api/v1/workspace/session",
        json={
            "title": "PHASE03 product loop",
            "session_id": "session_phase03_full",
            "agent": "simple",
            "workspace_mode": "normal",
            "contexts": [],
        },
    )
    assert session_response.status_code == 200
    session = session_response.json()["data"]
    assert session["session_id"] == "session_phase03_full"
    assert session["user_id"] == "user_phase03"

    file_response = client.post(
        "/api/v1/workspace/file",
        json={
            "workspace_id": "workspace_phase03_full",
            "file_id": "file_contract_full",
            "name": "supplier-contract.md",
            "mime_type": "text/markdown",
            "hash": "sha256-contract-full",
            "uri": "memory://workspace/workspace_phase03_full/files/file_contract_full",
            "content": "Create a cited risk memo after approval using renewal and liability evidence.",
        },
    )
    assert file_response.status_code == 200
    registered_file = file_response.json()["data"]["file"]
    assert registered_file["file_id"] == "file_contract_full"
    assert registered_file["parse_status"] == "uploaded"

    ingest_response = client.post(
        "/api/v1/workspace/ingest",
        json={
            "workspace_id": "workspace_phase03_full",
            "file_id": "file_contract_full",
            "knowledge_space_id": "ks_contracts_full",
            "session_id": "session_phase03_full",
        },
    )
    assert ingest_response.status_code == 200
    ingest_payload = ingest_response.json()["data"]
    assert ingest_payload["file"]["parse_status"] == "indexed"
    assert ingest_payload["ingest_task_id"].startswith("ingest_")
    assert ingest_payload["trace_id"].startswith("trace_")
    assert ingest_payload["index_job"]["status"] == "succeeded"
    assert ingest_payload["index_job"]["target_status"] == {
        "bm25": "ready",
        "vector": "ready",
        "graph": "ready",
    }

    create_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Create a cited risk memo after approval",
            "model_id": "model-local",
            "session_id": "session_phase03_full",
            "workspace_id": "workspace_phase03_full",
            "goal": "approved contract memo",
            "product_mode": "contract_review",
            "uploaded_file_ids": ["file_contract_full"],
            "knowledge_space_ids": ["ks_contracts_full"],
            "approval_mode": "manual",
            "plugins": ["filesystem.read"],
            "mcp_servers": [],
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()["data"]
    task = created["task"]
    task_id = task["task_id"]
    trace_id = task["trace_id"]
    assert task["status"] == "approval_waiting"
    assert created["artifact_ids"] == []

    waiting_events = client.get(f"/api/v1/workspace/task/{task_id}/events").json()["data"]
    assert [event["type"] for event in waiting_events] == [
        "task_started",
        "planning",
        "retrieval",
        "approval_required",
    ]
    assert waiting_events[-1]["payload"]["approval_mode"] == "manual"
    assert waiting_events[-1]["trace_id"] == trace_id

    approve_response = client.post(
        f"/api/v1/workspace/task/{task_id}/approve",
        json={
            "decision": "approved",
            "comment": "Approved for PHASE03 runtime closure.",
        },
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()["data"]
    approved_task = approved["task"]
    artifact = approved["artifacts"][0]
    assert approved_task["status"] == "completed"
    assert approved_task["trace_id"] == trace_id
    assert artifact["task_id"] == task_id
    assert artifact["trace_id"] == trace_id

    approved_events = client.get(f"/api/v1/workspace/task/{task_id}/events").json()["data"]
    approved_event_types = [event["type"] for event in approved_events]
    assert approved_event_types == [
        "task_started",
        "planning",
        "retrieval",
        "approval_required",
        "approval_decision",
        "resuming",
        "retrieval",
        "answer",
        "artifact_created",
        "eval_diagnostic",
        "task_completed",
    ]
    assert {event["trace_id"] for event in approved_events} == {trace_id}

    rejected_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Try a risky write without approval",
            "model_id": "model-local",
            "session_id": "session_phase03_reject",
            "workspace_id": "workspace_phase03_full",
            "goal": "rejected risky task",
            "product_mode": "general_agent",
            "approval_mode": "manual",
            "plugins": ["filesystem.write"],
            "mcp_servers": [],
        },
    )
    rejected_task = rejected_response.json()["data"]["task"]
    reject_approval = client.post(
        f"/api/v1/workspace/task/{rejected_task['task_id']}/approve",
        json={"decision": "rejected", "comment": "Risk not approved."},
    )
    assert reject_approval.status_code == 200
    failed_snapshot = reject_approval.json()["data"]
    assert failed_snapshot["task"]["status"] == "failed"

    failed_events = client.get(f"/api/v1/workspace/task/{rejected_task['task_id']}/events").json()["data"]
    assert failed_events[-1]["type"] == "failure"
    assert failed_events[-1]["payload"]["status"] == "failed"
    assert "Risk not approved" in failed_events[-1]["payload"]["error"]


def test_workspace_task_runtime_exposes_durable_runtime_resume_and_cancel(monkeypatch) -> None:
    async def fake_create_workspace_session(payload):
        return {
            "session_id": payload.session_id,
            "user_id": payload.user_id,
            "agent": payload.agent,
            "contexts": payload.contexts,
        }

    monkeypatch.setattr(
        "zuno.api.v1.workspace.WorkSpaceSessionService.create_workspace_session",
        fake_create_workspace_session,
    )

    client = _client()
    session_response = client.post(
        "/api/v1/workspace/session",
        json={
            "title": "PHASE06 durable runtime",
            "session_id": "session_phase06_runtime",
            "agent": "simple",
            "workspace_mode": "normal",
            "contexts": [],
        },
    )
    assert session_response.status_code == 200

    create_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Pause for durable approval",
            "model_id": "model-local",
            "session_id": "session_phase06_runtime",
            "workspace_id": "workspace_phase06",
            "task_id": "task_phase06_runtime",
            "trace_id": "trace_phase06_runtime",
            "goal": "durable approved task",
            "product_mode": "general_agent",
            "approval_mode": "manual",
            "plugins": ["mail.send"],
            "mcp_servers": [],
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()["data"]
    runtime = created["runtime"]
    assert created["task"]["status"] == "approval_waiting"
    assert runtime["status"] == "approval_waiting"
    assert runtime["task_id"] == "task_phase06_runtime"
    assert runtime["trace_id"] == "trace_phase06_runtime"
    assert runtime["pending_interrupt"]["node"] == "act_react_loop"
    assert runtime["latest_checkpoint"]["node"] == "act_react_loop"

    approve_response = client.post(
        "/api/v1/workspace/task/task_phase06_runtime/approve",
        json={"decision": "approved", "comment": "Resume from PHASE06 checkpoint."},
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()["data"]
    approved_runtime = approved["runtime"]
    assert approved["task"]["status"] == "completed"
    assert approved_runtime["status"] == "completed"
    assert approved_runtime["pending_interrupt"] is None
    assert approved_runtime["latest_checkpoint"]["node"] == "post_turn_commit"
    assert approved_runtime["trace_id"] == "trace_phase06_runtime"
    assert "runtime_resumed" in [event["type"] for event in approved_runtime["events"]]

    stream_response = client.get("/api/v1/workspace/task/task_phase06_runtime/events/stream")
    assert stream_response.status_code == 200
    streamed_payloads = [
        json.loads(line.removeprefix("data: "))
        for line in stream_response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert {payload["data"]["trace_id"] for payload in streamed_payloads} == {
        "trace_phase06_runtime"
    }
    assert "resuming" in [payload["event"] for payload in streamed_payloads]

    cancel_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Pause then cancel",
            "model_id": "model-local",
            "session_id": "session_phase06_runtime",
            "workspace_id": "workspace_phase06",
            "task_id": "task_phase06_cancel",
            "trace_id": "trace_phase06_cancel",
            "goal": "durable cancelled task",
            "product_mode": "general_agent",
            "approval_mode": "manual",
            "plugins": ["filesystem.write"],
            "mcp_servers": [],
        },
    )
    assert cancel_response.status_code == 200

    cancelled_response = client.post(
        "/api/v1/workspace/task/task_phase06_cancel/cancel",
        json={"reason": "user_cancelled"},
    )
    assert cancelled_response.status_code == 200
    cancelled = cancelled_response.json()["data"]
    assert cancelled["task"]["status"] == "cancelled"
    assert cancelled["runtime"]["status"] == "cancelled"
    assert cancelled["runtime"]["events"][-1]["type"] == "runtime_cancelled"

    cancelled_events = client.get("/api/v1/workspace/task/task_phase06_cancel/events").json()["data"]
    assert cancelled_events[-1]["type"] == "task_cancelled"
    assert cancelled_events[-1]["payload"]["reason"] == "user_cancelled"

    cancelled_stream = client.get("/api/v1/workspace/task/task_phase06_cancel/events/stream")
    assert cancelled_stream.status_code == 200
    cancel_payloads = [
        json.loads(line.removeprefix("data: "))
        for line in cancelled_stream.text.splitlines()
        if line.startswith("data: ")
    ]
    assert {payload["data"]["trace_id"] for payload in cancel_payloads} == {
        "trace_phase06_cancel"
    }
    assert cancel_payloads[-1]["event"] == "task_cancelled"


def test_workspace_task_runtime_runs_read_only_tool_and_streams_audit_events() -> None:
    client = _client()

    create_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Read the uploaded workspace note",
            "model_id": "model-local",
            "session_id": "session_phase08_read",
            "workspace_id": "workspace_phase08",
            "task_id": "task_phase08_read",
            "trace_id": "trace_phase08_read",
            "goal": "tool read closure",
            "product_mode": "general_agent",
            "plugins": ["filesystem.read"],
            "mcp_servers": [],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["data"]
    assert created["task"]["status"] == "completed"

    events = client.get("/api/v1/workspace/task/task_phase08_read/events").json()["data"]
    event_types = [event["type"] for event in events]
    assert "tool_call" in event_types
    assert "sandbox_audit" in event_types
    assert "tool_result" in event_types
    tool_result = next(event for event in events if event["type"] == "tool_result")
    assert tool_result["payload"]["tool_id"] == "filesystem.read"
    assert tool_result["payload"]["result"]["audit_ref"].startswith("audit_")
    audit_event = next(event for event in events if event["type"] == "sandbox_audit")
    assert audit_event["payload"]["audit"]["sandbox_profile"] == "workspace_ro"
    assert audit_event["payload"]["audit"]["policy_decision"] == "allow"

    stream_response = client.get("/api/v1/workspace/task/task_phase08_read/events/stream")
    assert stream_response.status_code == 200
    streamed_payloads = [
        json.loads(line.removeprefix("data: "))
        for line in stream_response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert "tool_result" in [payload["event"] for payload in streamed_payloads]
    streamed_tool = next(payload for payload in streamed_payloads if payload["event"] == "tool_result")
    assert streamed_tool["data"]["tool_id"] == "filesystem.read"
    assert streamed_tool["data"]["audit_ref"].startswith("audit_")


def test_workspace_task_runtime_requires_tool_approval_then_executes_brokered_tool() -> None:
    client = _client()

    create_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "Send the approved project email",
            "model_id": "model-local",
            "session_id": "session_phase08_mail",
            "workspace_id": "workspace_phase08",
            "task_id": "task_phase08_mail",
            "trace_id": "trace_phase08_mail",
            "goal": "tool approval closure",
            "product_mode": "general_agent",
            "plugins": ["mail.send"],
            "mcp_servers": [],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["data"]
    assert created["task"]["status"] == "approval_waiting"
    assert created["artifact_ids"] == []
    assert created["runtime"]["pending_interrupt"]["required_approval"] == "tool:mail.send"

    waiting_events = client.get("/api/v1/workspace/task/task_phase08_mail/events").json()["data"]
    assert [event["type"] for event in waiting_events] == [
        "task_started",
        "planning",
        "retrieval",
        "tool_call",
        "sandbox_audit",
        "approval_required",
    ]
    approval_event = waiting_events[-1]
    assert approval_event["payload"]["required_approval"] == "tool:mail.send"
    assert approval_event["payload"]["tool_id"] == "mail.send"
    assert approval_event["payload"]["tool_request_id"].startswith("toolreq_")
    assert approval_event["payload"]["approval_id"].startswith("approval_")
    assert "raw-secret" not in repr(waiting_events)

    approve_response = client.post(
        "/api/v1/workspace/task/task_phase08_mail/approve",
        json={"decision": "approved", "comment": "Approve PHASE08 tool execution."},
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()["data"]
    assert approved["task"]["status"] == "completed"
    assert approved["artifacts"][0]["task_id"] == "task_phase08_mail"

    approved_events = client.get("/api/v1/workspace/task/task_phase08_mail/events").json()["data"]
    approved_types = [event["type"] for event in approved_events]
    assert approved_types == [
        "task_started",
        "planning",
        "retrieval",
        "tool_call",
        "sandbox_audit",
        "approval_required",
        "approval_decision",
        "resuming",
        "tool_call",
        "sandbox_audit",
        "tool_result",
        "answer",
        "artifact_created",
        "eval_diagnostic",
        "task_completed",
    ]
    tool_result = next(event for event in approved_events if event["type"] == "tool_result")
    assert tool_result["payload"]["tool_id"] == "mail.send"
    assert tool_result["payload"]["tool_request_id"] == approval_event["payload"]["tool_request_id"]
    assert tool_result["payload"]["approval_id"] == approval_event["payload"]["approval_id"]
    assert tool_result["payload"]["tool_execution_id"].startswith("toolexec_")
    assert tool_result["payload"]["tool_result_id"].startswith("toolres_")
    assert len(
        {
            event["payload"].get("tool_execution_id")
            for event in approved_events
            if event["type"] == "tool_result"
        }
    ) == 1
    assert tool_result["payload"]["result"]["data"]["message_id"].startswith("msg_")
    assert tool_result["payload"]["credential_refs"] == ["credref://workspace_phase08/mail.send"]
    assert "raw-secret" not in repr(approved_events)


def test_workspace_task_runtime_emits_security_approval_facts_from_active_tool_path() -> None:
    facts: list[dict] = []

    class SecurityFactSink:
        def record_tool_approval_fact(self, fact: dict) -> None:
            facts.append(fact)

    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    WorkspaceTaskRuntimeService.configure_security_approval_sink(SecurityFactSink())
    try:
        client = _client()

        create_response = client.post(
            "/api/v1/workspace/task",
            json={
                "query": "Send the approved project email",
                "model_id": "model-local",
                "session_id": "session_phase05_mail",
                "workspace_id": "workspace_phase05",
                "task_id": "task_phase05_mail_api",
                "trace_id": "trace_phase05_mail_api",
                "goal": "security approval fact closure",
                "product_mode": "general_agent",
                "plugins": ["mail.send"],
                "mcp_servers": [],
            },
        )

        assert create_response.status_code == 200
        assert facts[0]["status"] == "approval_waiting"
        assert facts[0]["prepared_action_hash"]
        assert "raw-secret" not in repr(facts)

        approve_response = client.post(
            "/api/v1/workspace/task/task_phase05_mail_api/approve",
            json={"decision": "approved", "comment": "Approved by product user."},
        )
        assert approve_response.status_code == 200
        assert [fact["status"] for fact in facts] == [
            "approval_waiting",
            "approved_before_effect",
        ]
        assert facts[-1]["credential_refs"] == ["credref://workspace_phase05/mail.send"]
    finally:
        WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()


def test_workspace_task_runtime_answers_from_ingested_index_with_citations() -> None:
    client = _client()

    file_response = client.post(
        "/api/v1/workspace/file",
        json={
            "workspace_id": "workspace_phase09",
            "file_id": "file_contract_phase09",
            "name": "renewal-contract.md",
            "mime_type": "text/markdown",
            "hash": "sha256-phase09",
            "uri": "memory://workspace/workspace_phase09/files/file_contract_phase09",
            "content": "Renewal notice must be sent 30 days before the contract anniversary.",
        },
    )
    assert file_response.status_code == 200

    ingest_response = client.post(
        "/api/v1/workspace/ingest",
        json={
            "workspace_id": "workspace_phase09",
            "file_id": "file_contract_phase09",
            "knowledge_space_id": "ks_phase09_contracts",
            "trace_id": "trace_phase09_ingest",
        },
    )
    assert ingest_response.status_code == 200
    ingest = ingest_response.json()["data"]
    assert ingest["index_job"]["status"] == "succeeded"
    assert ingest["index_job"]["target_status"] == {
        "bm25": "ready",
        "vector": "ready",
        "graph": "ready",
    }
    assert ingest["parse_job"]["status"] == "succeeded"
    assert ingest["parse_snapshot"]["status"] == "succeeded"
    assert ingest["parse_job"]["job_id"] == ingest["parse_snapshot"]["job_id"]
    assert ingest["parse_snapshot"]["parser_id"] != "workspace_text_runtime"
    assert ingest["index_job"]["parse_job_id"] == ingest["parse_job"]["job_id"]
    assert ingest["index_job"]["parse_attempt_id"] == ingest["parse_snapshot"]["parse_attempt_id"]
    assert ingest["index_job"]["document_version_id"] == ingest["parse_snapshot"]["source_provenance"]["document_version_id"]
    assert ingest["index_job"]["source_sha256"] == ingest["parse_snapshot"]["source_provenance"]["source_sha256"]

    create_response = client.post(
        "/api/v1/workspace/task",
        json={
            "query": "What is the renewal notice requirement?",
            "model_id": "model-local",
            "session_id": "session_phase09",
            "workspace_id": "workspace_phase09",
            "task_id": "task_phase09_retrieval",
            "trace_id": "trace_phase09_retrieval",
            "goal": "cited renewal answer",
            "product_mode": "contract_review",
            "knowledge_space_ids": ["ks_phase09_contracts"],
            "uploaded_file_ids": ["file_contract_phase09"],
            "plugins": [],
            "mcp_servers": [],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["data"]
    artifact = created["artifacts"][0]
    assert created["task"]["status"] == "completed"

    events = client.get("/api/v1/workspace/task/task_phase09_retrieval/events").json()["data"]
    retrieval_events = [event for event in events if event["type"] == "retrieval"]
    assert retrieval_events[-1]["payload"]["citation_ids"] == ["[1]"]
    assert retrieval_events[-1]["payload"]["resolved_methods"] == ["local", "basic"]
    assert retrieval_events[-1]["payload"]["evidence_coverage"] == 1.0
    assert retrieval_events[-1]["payload"]["citation_coverage"] == 1.0

    artifact_response = client.get(f"/api/v1/workspace/artifact/{artifact['artifact_id']}")
    assert artifact_response.status_code == 200
    content = artifact_response.json()["data"]["content"]
    assert "Renewal notice must be sent 30 days" in content
    assert "[1]" in content
