import hashlib

import pytest
from fastapi import HTTPException

from zuno.api.services.user import UserPayload
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService


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
    WorkspaceTaskRuntimeService.configure_package_a_production_ingestion(runtime)
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
    assert runtime.commands[0].content == content.encode("utf-8")
    assert payload["file"]["hash"] == content_hash
    assert payload["file_status"]["source_sha256"] == content_hash
    assert payload["durable_status"] == "production_accepted"


def _user() -> UserPayload:
    return UserPayload(user_id="user-a", user_name="User A", role="admin")
