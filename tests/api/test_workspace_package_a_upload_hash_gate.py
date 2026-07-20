import hashlib
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient

from zuno.api.services.user import UserPayload
from zuno.api.services.user import get_login_user
from zuno.api.v1.workspace import router as workspace_router
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.knowledge.storage import LocalObjectStore, SQLiteDurableIngestionStore


class _RecordingPackageARuntime:
    def __init__(self) -> None:
        self.commands = []

    def accept_workspace_upload(self, command):
        self.commands.append(command)

        class _Receipt:
            source_object_id = command.source_object_id
            document_version_id = f"document-version:{command.source_object_id}:1"
            parse_plan_id = f"parse-plan:{command.source_object_id}:1"
            parse_job_id = f"parse-job:{command.source_object_id}:1"
            outbox_event_id = f"outbox:parse-job:{command.source_object_id}:1"
            object_ref = f"s3://zuno-ingestion/{command.tenant_id}/{command.workspace_id}/file.md"

        return _Receipt()


def test_workspace_package_a_upload_rejects_client_hash_mismatch() -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    runtime = _RecordingPackageARuntime()
    WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(runtime)

    with pytest.raises(HTTPException) as exc:
        WorkspaceTaskRuntimeService.register_file(
            workspace_id="workspace-a",
            login_user=_user(),
            file_id="file-a",
            mime_type="text/markdown",
            file_hash="0" * 64,
            name="file.md",
            uri=None,
            trace_id="trace-a",
            security_label="internal",
            content="# Package A\nActual content.",
        )

    assert exc.value.status_code == 400
    assert "hash does not match" in str(exc.value.detail)
    assert runtime.commands == []
    assert "file-a" not in WorkspaceTaskRuntimeService._files


def test_workspace_package_a_upload_accepts_matching_hash_and_uses_content_hash() -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    runtime = _RecordingPackageARuntime()
    WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(
        runtime,
        upload_bucket="zuno-prod-ingestion",
    )
    content = "# Package A\nActual content."
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    payload = WorkspaceTaskRuntimeService.register_file(
        workspace_id="workspace-a",
        login_user=_user(),
        file_id="file-a",
        mime_type="text/markdown",
        file_hash=content_hash,
        name="file.md",
        uri=None,
        trace_id="trace-a",
        security_label="internal",
        content=content,
    )

    assert len(runtime.commands) == 1
    assert runtime.commands[0].bucket == "zuno-prod-ingestion"
    assert runtime.commands[0].content == content.encode("utf-8")
    assert payload["file"]["hash"] == content_hash
    assert payload["file_status"]["source_sha256"] == content_hash
    assert payload["durable_status"] == "production_accepted"


def test_workspace_package_a_upload_forwards_deadline_to_production_command() -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    runtime = _RecordingPackageARuntime()
    WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(runtime)
    deadline = datetime(2026, 7, 20, 12, 30, tzinfo=timezone.utc)

    WorkspaceTaskRuntimeService.register_file(
        workspace_id="workspace-a",
        login_user=_user(),
        file_id="file-a",
        mime_type="text/markdown",
        file_hash=None,
        name="file.md",
        uri=None,
        trace_id="trace-a",
        security_label="internal",
        content="# Package A\nDeadline.",
        deadline_at=deadline,
    )

    assert len(runtime.commands) == 1
    assert runtime.commands[0].deadline_at == deadline


def test_workspace_file_api_forwards_deadline_to_package_a_default_path() -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    runtime = _RecordingPackageARuntime()
    WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(runtime)
    app = FastAPI()
    app.include_router(workspace_router, prefix="/api/v1")
    app.dependency_overrides[get_login_user] = _user
    client = TestClient(app)

    response = client.post(
        "/api/v1/workspace/file",
        json={
            "workspace_id": "workspace-a",
            "file_id": "file-a",
            "mime_type": "text/markdown",
            "name": "file.md",
            "content": "# Package A\nDeadline.",
            "security_label": "internal",
            "deadline_at": "2026-07-20T12:30:00Z",
        },
    )

    assert response.status_code == 200
    assert len(runtime.commands) == 1
    assert runtime.commands[0].deadline_at == datetime(2026, 7, 20, 12, 30, tzinfo=timezone.utc)


def test_workspace_package_a_upload_does_not_fallback_when_production_default_is_unavailable(tmp_path) -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    WorkspaceTaskRuntimeService.configure_durable_ingestion(
        store=SQLiteDurableIngestionStore(tmp_path / "legacy.db"),
        object_store=LocalObjectStore(tmp_path / "objects"),
    )
    WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(None)

    try:
        with pytest.raises(HTTPException) as exc:
            WorkspaceTaskRuntimeService.register_file(
                workspace_id="workspace-a",
                login_user=_user(),
                file_id="file-a",
                mime_type="text/markdown",
                file_hash=None,
                name="file.md",
                uri=None,
                trace_id="trace-a",
                security_label="internal",
                content="# Package A\nNo local fallback.",
            )

        assert exc.value.status_code == 503
        assert "production ingestion is configured but unavailable" in str(exc.value.detail)
        assert "file-a" not in WorkspaceTaskRuntimeService._files
        with pytest.raises(KeyError):
            WorkspaceTaskRuntimeService._durable_ingestion_store.get_workspace_file("file-a")
    finally:
        WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()


def _user() -> UserPayload:
    return UserPayload(user_id="user-a", user_name="User A", role="admin")
