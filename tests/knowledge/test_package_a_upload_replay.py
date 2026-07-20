import hashlib
from datetime import datetime, timezone

import pytest

from zuno.knowledge.ingestion.production_runtime import (
    PackageAProductionIngestionRuntime,
    PackageAUploadCommand,
)
from zuno.platform.database.ingestion import IngestionPersistenceError


def test_package_a_upload_replays_existing_parse_job_before_object_write(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    content = b"# Replay\nsame content\n"
    content_hash = hashlib.sha256(content).hexdigest()
    replay = {
        "source_object_id": "source-existing",
        "document_version_id": "document-version:source-existing:1",
        "parse_plan_id": "parse-plan:source-existing:1",
        "parse_job_id": "parse-job:source-existing:1",
        "outbox_event_id": "outbox:parse-job:source-existing:1",
        "object_ref": "s3://bucket/tenant-a/workspace-a/source/source-existing/file.md",
        "workspace_id": "workspace-a",
        "source_sha256": content_hash,
        "size_bytes": len(content),
        "classification_ref": "internal",
        "security_epoch_ref": "security-epoch-a",
    }
    monkeypatch.setattr(production_runtime, "IngestionUnitOfWork", _unit_of_work_factory(replay))
    runtime = PackageAProductionIngestionRuntime(
        engine=object(),
        object_store=_FailingObjectStore(),
        worker_id="worker-a",
    )

    receipt = runtime.accept_workspace_upload(
        _command(content=content, source_object_id="source-duplicate")
    )

    assert receipt.source_object_id == "source-existing"
    assert receipt.parse_job_id == "parse-job:source-existing:1"
    assert receipt.outbox_event_id == "outbox:parse-job:source-existing:1"
    assert receipt.object_ref == "s3://bucket/tenant-a/workspace-a/source/source-existing/file.md"


def test_package_a_upload_replay_rejects_conflicting_source_facts(monkeypatch) -> None:
    import zuno.knowledge.ingestion.production_runtime as production_runtime

    content = b"# Replay\nsame content\n"
    content_hash = hashlib.sha256(content).hexdigest()
    replay = {
        "source_object_id": "source-existing",
        "document_version_id": "document-version:source-existing:1",
        "parse_plan_id": "parse-plan:source-existing:1",
        "parse_job_id": "parse-job:source-existing:1",
        "outbox_event_id": "outbox:parse-job:source-existing:1",
        "object_ref": "s3://bucket/tenant-a/workspace-a/source/source-existing/file.md",
        "workspace_id": "workspace-b",
        "source_sha256": content_hash,
        "size_bytes": len(content),
        "classification_ref": "internal",
        "security_epoch_ref": "security-epoch-a",
    }
    monkeypatch.setattr(production_runtime, "IngestionUnitOfWork", _unit_of_work_factory(replay))
    runtime = PackageAProductionIngestionRuntime(
        engine=object(),
        object_store=_FailingObjectStore(),
        worker_id="worker-a",
    )

    with pytest.raises(IngestionPersistenceError, match="workspace_id"):
        runtime.accept_workspace_upload(_command(content=content))


def test_package_a_upload_parse_request_preserves_deadline_at() -> None:
    deadline = datetime(2026, 7, 20, 12, 30, tzinfo=timezone.utc)
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = 2

    envelope = runtime._parse_requested_envelope(
        command=_command(content=b"# Deadline\n", deadline_at=deadline),
        document_version_id="document-version:source-a:1",
        parse_plan_id="parse-plan:source-a:1",
        parse_job_id="parse-job:source-a:1",
        object_ref="s3://bucket/tenant-a/workspace-a/source/source-a/file.md",
        object_manifest_ref="manifest:source-a",
        content_hash="a" * 64,
        size_bytes=11,
        idempotency_key="parse:tenant-a:workspace-a:hash:deadline",
    )

    assert envelope.deadline_at == deadline
    assert envelope.aggregate_type == "ParseJob"
    assert envelope.aggregate_id == "parse-job:source-a:1"
    assert envelope.payload["filename"] == "file.md"


def _command(
    *,
    content: bytes,
    source_object_id: str = "source-a",
    deadline_at: datetime | None = None,
) -> PackageAUploadCommand:
    return PackageAUploadCommand(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        filename="file.md",
        mime_type="text/markdown",
        content=content,
        bucket="bucket",
        source_object_id=source_object_id,
        classification_ref="internal",
        security_epoch_ref="security-epoch-a",
        trace_id="trace-a",
        deadline_at=deadline_at,
    )


def _unit_of_work_factory(replay):
    class _Repo:
        def load_workspace_upload_replay_receipt(self, **kwargs):
            return replay

    class _UnitOfWork:
        def __init__(self, engine):
            self.repo = _Repo()

        def __enter__(self):
            return self.repo

        def __exit__(self, exc_type, exc, tb):
            return None

    return _UnitOfWork


class _FailingObjectStore:
    def stage(self, **kwargs):
        raise AssertionError("duplicate upload replay must happen before object write")
