from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from minio.error import S3Error
from minio.retention import GOVERNANCE

from zuno.platform.storage import MinioObjectStore, ObjectAuthorizationError, ObjectHashMismatchError

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"


def test_minio_object_store_stage_commit_delete_restore() -> None:
    store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    bucket = f"phase04-object-{uuid4().hex}"
    try:
        staged = store.stage_object(bucket=bucket, object_name="workspace/a.txt", content=b"phase04-object")
        assert staged.visibility == "staged"
        assert staged.size_bytes == len(b"phase04-object")

        with pytest.raises(ObjectHashMismatchError):
            store.commit_object(
                bucket=bucket,
                staged_object_name=staged.object_name,
                committed_object_name="committed/a.txt",
                expected_hash="0" * 64,
            )

        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name="committed/a.txt",
            expected_hash=staged.content_hash,
        )
        assert committed.visibility == "visible"
        assert store.read_object(bucket=bucket, object_name=committed.object_name) == b"phase04-object"
        with pytest.raises(S3Error):
            store.read_object(bucket=bucket, object_name=staged.object_name)

        restore_point = store.create_restore_point(
            bucket=bucket,
            object_name=committed.object_name,
            restore_point_name="_restore/a.txt",
        )
        deleted = store.delete_object(bucket=bucket, object_name=committed.object_name)
        assert deleted.visibility == "deleted"
        with pytest.raises(S3Error):
            store.read_object(bucket=bucket, object_name=committed.object_name)

        restored = store.restore_object(
            bucket=bucket,
            restore_point_name=restore_point.object_name,
            restored_object_name="restored/a.txt",
        )
        assert restored.visibility == "restored"
        assert restored.content_hash == committed.content_hash
        assert store.read_object(bucket=bucket, object_name=restored.object_name) == b"phase04-object"
    finally:
        store.remove_bucket_tree(bucket)


def test_minio_multipart_partial_abort_and_lost_response_reconciliation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    bucket = f"phase04-multipart-{uuid4().hex}"
    content = (b"a" * (5 * 1024 * 1024)) + b"-phase04-tail"
    content_hash = hashlib.sha256(content).hexdigest()
    try:
        partial = store.begin_multipart_upload(
            bucket=bucket,
            object_name="workspace/large.bin",
            upload_session_ref="partial-session",
            expected_content_hash=content_hash,
            expected_size_bytes=len(content),
        )
        store.upload_multipart_part(partial, part_number=1, content=content[: 5 * 1024 * 1024])
        with pytest.raises(S3Error):
            store.read_object(bucket=bucket, object_name=partial.object_name)
        assert partial.upload_id in store.incomplete_upload_ids([partial])
        assert store.reconcile_incomplete_uploads(
            sessions=[partial],
            active_upload_ids={partial.upload_id},
        ) == []
        cleanup = store.reconcile_incomplete_uploads(sessions=[partial])
        assert [receipt.upload_id for receipt in cleanup] == [partial.upload_id]
        assert partial.upload_id not in store.incomplete_upload_ids([partial])

        session = store.begin_multipart_upload(
            bucket=bucket,
            object_name="workspace/large.bin",
            upload_session_ref="lost-response-session",
            expected_content_hash=content_hash,
            expected_size_bytes=len(content),
        )
        first = store.upload_multipart_part(
            session,
            part_number=1,
            content=content[: 5 * 1024 * 1024],
        )
        second = store.upload_multipart_part(
            session,
            part_number=2,
            content=content[5 * 1024 * 1024 :],
        )
        complete = store.client._complete_multipart_upload

        def complete_then_lose_response(*args, **kwargs):
            complete(*args, **kwargs)
            raise TimeoutError("simulated response loss after MinIO committed the multipart upload")

        monkeypatch.setattr(store.client, "_complete_multipart_upload", complete_then_lose_response)
        staged = store.complete_multipart_upload(session, [first, second])
        assert staged.visibility == "staged"
        assert staged.content_hash == content_hash
        assert store.read_object(bucket=bucket, object_name=staged.object_name) == content

        monkeypatch.setattr(store.client, "_complete_multipart_upload", complete)
        duplicate = store.complete_multipart_upload(session, [first, second])
        assert duplicate == staged
        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name="committed/large.bin",
            expected_hash=content_hash,
        )
        assert committed.size_bytes == len(content)
        assert store.read_object(bucket=bucket, object_name=committed.object_name) == content
    finally:
        store.remove_bucket_tree(bucket)


def test_minio_authorization_retention_legal_hold_and_lifecycle() -> None:
    store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    bucket = f"phase04-governance-{uuid4().hex}"
    retain_until = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(hours=1)
    try:
        store.ensure_bucket(bucket, object_lock=True)
        staged = store.stage_object(
            bucket=bucket,
            object_name="workspace/governed.txt",
            content=b"phase04-governed-object",
        )
        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name="committed/governed.txt",
            expected_hash=staged.content_hash,
        )
        assert committed.version_id is not None

        governance = store.apply_object_governance(
            bucket=bucket,
            object_name=committed.object_name,
            version_id=committed.version_id,
            retain_until=retain_until,
            legal_hold=True,
        )
        assert governance.retention_mode == GOVERNANCE
        assert governance.retain_until == retain_until
        assert governance.legal_hold is True

        lifecycle = store.configure_staging_lifecycle(
            bucket=bucket,
            expire_after_days=7,
        )
        assert lifecycle.prefix == "_staging/"
        assert lifecycle.expire_after_days == 7
        assert store.staging_lifecycle(bucket=bucket) == lifecycle

        denied_store = MinioObjectStore(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            authorization_hook=lambda action, _bucket, _object_name: action != "object:read",
        )
        with pytest.raises(ObjectAuthorizationError):
            denied_store.read_object(bucket=bucket, object_name=committed.object_name)

        def broken_authorization_hook(_action: str, _bucket: str, _object_name: str | None) -> bool:
            raise RuntimeError("authorization dependency unavailable")

        broken_auth_store = MinioObjectStore(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            authorization_hook=broken_authorization_hook,
        )
        with pytest.raises(ObjectAuthorizationError):
            broken_auth_store.read_object(bucket=bucket, object_name=committed.object_name)

        with pytest.raises(S3Error):
            store.purge_object_version(
                bucket=bucket,
                object_name=committed.object_name,
                version_id=committed.version_id,
            )
        governance = store.apply_object_governance(
            bucket=bucket,
            object_name=committed.object_name,
            version_id=committed.version_id,
            retain_until=retain_until,
            legal_hold=False,
        )
        assert governance.legal_hold is False
        with pytest.raises(S3Error):
            store.purge_object_version(
                bucket=bucket,
                object_name=committed.object_name,
                version_id=committed.version_id,
            )
        assert store.read_object(bucket=bucket, object_name=committed.object_name) == b"phase04-governed-object"
    finally:
        store.remove_bucket_tree(bucket)
