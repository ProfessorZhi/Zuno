from __future__ import annotations

from uuid import uuid4

import pytest
from minio.error import S3Error

from zuno.platform.storage import MinioObjectStore, ObjectHashMismatchError

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
