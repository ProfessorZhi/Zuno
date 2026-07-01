from __future__ import annotations

import hashlib

from fastapi import FastAPI
from fastapi.testclient import TestClient

from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.api.v1.workspace import router as workspace_router
from zuno.knowledge.storage import LocalObjectStore, SQLiteDurableIngestionStore


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(workspace_router, prefix="/api/v1")
    app.dependency_overrides[get_login_user] = lambda: UserPayload(
        user_id="user_durable_ingest",
        user_name="Durable Ingest User",
        role="admin",
    )
    return TestClient(app)


def test_workspace_file_register_persists_source_object_and_content_ref(tmp_path) -> None:
    db_path = tmp_path / "zuno.db"
    object_root = tmp_path / "objects"
    WorkspaceTaskRuntimeService.configure_durable_ingestion(
        store=SQLiteDurableIngestionStore(db_path),
        object_store=LocalObjectStore(object_root),
    )
    try:
        client = _client()
        content = "Retention policy requires deletion review within 7 days."

        response = client.post(
            "/api/v1/workspace/file",
            json={
                "workspace_id": "workspace_phase03_durable",
                "file_id": "file_policy_phase03",
                "name": "policy.md",
                "mime_type": "text/markdown",
                "content": content,
                "security_label": "confidential",
                "trace_id": "trace_phase03_durable",
            },
        )

        assert response.status_code == 200
        payload = response.json()["data"]
        registered_file = payload["file"]
        expected_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()

        assert registered_file["file_id"] == "file_policy_phase03"
        assert registered_file["hash"] == expected_sha
        assert registered_file["parse_status"] == "uploaded"
        assert payload["source_id"] == "source_file_policy_phase03"
        assert payload["source_sha256"] == expected_sha
        assert payload["storage_uri"].startswith("file:")
        assert payload["durable_status"] == "persisted"

        restored = SQLiteDurableIngestionStore(db_path)
        restored_file = restored.get_workspace_file("file_policy_phase03")
        restored_source = restored.get_source_object("source_file_policy_phase03")
        object_path = (
            object_root
            / "workspaces"
            / "workspace_phase03_durable"
            / "sources"
            / "source_file_policy_phase03"
            / "policy.md"
        )

        assert restored_file.source_id == restored_source.source_id
        assert restored_file.source_sha256 == expected_sha
        assert restored_source.storage_uri == payload["storage_uri"]
        assert object_path.read_text(encoding="utf-8") == content
    finally:
        WorkspaceTaskRuntimeService.configure_durable_ingestion(store=None, object_store=None)


def test_workspace_ingest_persists_parse_document_index_and_chunks(tmp_path) -> None:
    db_path = tmp_path / "zuno.db"
    WorkspaceTaskRuntimeService.configure_durable_ingestion(
        store=SQLiteDurableIngestionStore(db_path),
        object_store=LocalObjectStore(tmp_path / "objects"),
    )
    try:
        client = _client()
        content = "SOC 2 evidence must include owner, control id, and review date."

        client.post(
            "/api/v1/workspace/file",
            json={
                "workspace_id": "workspace_phase04_durable",
                "file_id": "file_controls_phase04",
                "name": "controls.md",
                "mime_type": "text/markdown",
                "content": content,
                "security_label": "internal",
            },
        )
        ingest_response = client.post(
            "/api/v1/workspace/ingest",
            json={
                "workspace_id": "workspace_phase04_durable",
                "file_id": "file_controls_phase04",
                "knowledge_space_id": "ks_phase04_controls",
                "trace_id": "trace_phase04_ingest",
            },
        )

        assert ingest_response.status_code == 200
        ingest = ingest_response.json()["data"]
        assert ingest["parse_snapshot"]["parser_id"] != "workspace_text_runtime"
        assert ingest["index_job"]["status"] == "succeeded"
        assert ingest["durable_status"] == "persisted"
        assert ingest["document_version"]["document_version_id"] == ingest["index_job"]["document_version_id"]
        assert ingest["index_manifest_ref"]["index_job_id"] == ingest["index_job"]["job_id"]

        restored = SQLiteDurableIngestionStore(db_path)
        restored_file = restored.get_workspace_file("file_controls_phase04")
        restored_parse_job = restored.get_parse_job(ingest["parse_job"]["job_id"])
        restored_snapshot = restored.get_parse_snapshot(ingest["parse_job"]["job_id"])
        restored_document = restored.get_document_version(ingest["index_job"]["document_version_id"])
        restored_blocks = restored.list_document_blocks(ingest["index_job"]["document_version_id"])
        restored_manifest = restored.get_index_manifest(ingest["index_job"]["job_id"])
        restored_chunks = restored.list_index_chunks(ingest["index_job"]["job_id"])

        assert restored_file.latest_parse_job_id == ingest["parse_job"]["job_id"]
        assert restored_file.latest_document_version_id == ingest["index_job"]["document_version_id"]
        assert restored_parse_job.status == "succeeded"
        assert restored_snapshot.parse_attempt_id == ingest["parse_snapshot"]["parse_attempt_id"]
        assert restored_document.block_count >= 1
        assert restored_blocks[0].text.startswith("SOC 2 evidence")
        assert restored_manifest.source_sha256 == restored_file.source_sha256
        assert any("SOC 2 evidence" in chunk.content for chunk in restored_chunks)
        assert restored_chunks[0].citation_lineage["parse_job_id"] == ingest["parse_job"]["job_id"]
    finally:
        WorkspaceTaskRuntimeService.configure_durable_ingestion(store=None, object_store=None)


def test_workspace_restart_rehydrates_cited_artifact_and_feedback(tmp_path) -> None:
    db_path = tmp_path / "zuno.db"
    object_root = tmp_path / "objects"
    WorkspaceTaskRuntimeService.configure_durable_ingestion(
        store=SQLiteDurableIngestionStore(db_path),
        object_store=LocalObjectStore(object_root),
    )
    try:
        client = _client()
        client.post(
            "/api/v1/workspace/file",
            json={
                "workspace_id": "workspace_phase07_recovery",
                "file_id": "file_recovery_phase07",
                "name": "recovery.md",
                "mime_type": "text/markdown",
                "content": "Restart recovery keeps artifact, feedback, and renewal citations durable.",
                "security_label": "internal",
            },
        )
        ingest = client.post(
            "/api/v1/workspace/ingest",
            json={
                "workspace_id": "workspace_phase07_recovery",
                "file_id": "file_recovery_phase07",
                "knowledge_space_id": "ks_phase07_recovery",
            },
        ).json()["data"]
        assert ingest["index_job"]["status"] == "succeeded"

        created = client.post(
            "/api/v1/workspace/task",
            json={
                "query": "What remains durable after restart recovery?",
                "model_id": "model-local",
                "session_id": "session_phase07_recovery",
                "workspace_id": "workspace_phase07_recovery",
                "task_id": "task_phase07_recovery",
                "trace_id": "trace_phase07_recovery",
                "goal": "restart recovery memo",
                "product_mode": "contract_review",
                "knowledge_space_ids": ["ks_phase07_recovery"],
                "uploaded_file_ids": ["file_recovery_phase07"],
                "plugins": [],
                "mcp_servers": [],
            },
        ).json()["data"]
        artifact_id = created["artifact_ids"][0]
        feedback = client.post(
            "/api/v1/workspace/feedback",
            json={
                "task_id": "task_phase07_recovery",
                "rating": 5,
                "label": "durable",
                "comment": "Restart evidence is intact.",
                "dataset_candidate": True,
            },
        ).json()["data"]

        WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
        WorkspaceTaskRuntimeService.configure_durable_ingestion(
            store=SQLiteDurableIngestionStore(db_path),
            object_store=LocalObjectStore(object_root),
            rehydrate=True,
        )
        restarted_client = _client()

        restored_task = restarted_client.get("/api/v1/workspace/task/task_phase07_recovery")
        assert restored_task.status_code == 200
        restored_snapshot = restored_task.json()["data"]
        assert restored_snapshot["task"]["status"] == "completed"
        assert restored_snapshot["artifact_ids"] == [artifact_id]
        assert restored_snapshot["feedback_ids"] == [feedback["feedback_id"]]

        restored_events = restarted_client.get(
            "/api/v1/workspace/task/task_phase07_recovery/events"
        ).json()["data"]
        assert restored_events[-1]["type"] == "feedback_received"

        restored_artifact = restarted_client.get(f"/api/v1/workspace/artifact/{artifact_id}")
        assert restored_artifact.status_code == 200
        assert "Restart recovery keeps artifact" in restored_artifact.json()["data"]["content"]

        cited_after_restart = restarted_client.post(
            "/api/v1/workspace/task",
            json={
                "query": "What does restart recovery keep durable?",
                "model_id": "model-local",
                "session_id": "session_phase07_recovery_2",
                "workspace_id": "workspace_phase07_recovery",
                "task_id": "task_phase07_recovery_cited",
                "trace_id": "trace_phase07_recovery_cited",
                "goal": "post restart cited answer",
                "product_mode": "contract_review",
                "knowledge_space_ids": ["ks_phase07_recovery"],
                "uploaded_file_ids": ["file_recovery_phase07"],
                "plugins": [],
                "mcp_servers": [],
            },
        )
        assert cited_after_restart.status_code == 200
        cited = cited_after_restart.json()["data"]
        assert cited["task"]["status"] == "completed"
        cited_content = restarted_client.get(
            f"/api/v1/workspace/artifact/{cited['artifact_ids'][0]}"
        ).json()["data"]["content"]
        assert "Restart recovery keeps artifact" in cited_content
        assert "[1]" in cited_content
    finally:
        WorkspaceTaskRuntimeService.configure_durable_ingestion(store=None, object_store=None)


def test_target_blocked_parser_diagnostics_are_persisted_without_fake_index(tmp_path) -> None:
    db_path = tmp_path / "zuno.db"
    WorkspaceTaskRuntimeService.configure_durable_ingestion(
        store=SQLiteDurableIngestionStore(db_path),
        object_store=LocalObjectStore(tmp_path / "objects"),
    )
    try:
        client = _client()
        client.post(
            "/api/v1/workspace/file",
            json={
                "workspace_id": "workspace_phase05_blocked",
                "file_id": "file_scan_phase05.png",
                "name": "scan.png",
                "mime_type": "image/png",
                "content": "fake image bytes for blocked OCR boundary",
                "security_label": "internal",
            },
        )

        ingest_response = client.post(
            "/api/v1/workspace/ingest",
            json={
                "workspace_id": "workspace_phase05_blocked",
                "file_id": "file_scan_phase05.png",
                "knowledge_space_id": "ks_phase05_blocked",
            },
        )

        assert ingest_response.status_code == 200
        ingest = ingest_response.json()["data"]
        assert ingest["status"] == "blocked"
        assert ingest["index_job"] is None
        assert "index_manifest_ref" not in ingest
        assert ingest["durable_status"] == "persisted"

        restored = SQLiteDurableIngestionStore(db_path)
        restored_file = restored.get_workspace_file("file_scan_phase05.png")
        restored_parse_job = restored.get_parse_job(ingest["parse_job"]["job_id"])
        restored_snapshot = restored.get_parse_snapshot(ingest["parse_job"]["job_id"])

        assert restored_file.parse_status == "blocked"
        assert restored_parse_job.status == "blocked"
        assert restored_parse_job.blocked_reason
        assert restored_snapshot.blocked_reason == restored_parse_job.blocked_reason
        assert restored_snapshot.parser_diagnostics[0]["code"] == "target_blocked_adapter"
    finally:
        WorkspaceTaskRuntimeService.configure_durable_ingestion(store=None, object_store=None)
