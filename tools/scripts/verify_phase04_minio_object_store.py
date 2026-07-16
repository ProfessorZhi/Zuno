from __future__ import annotations

from uuid import uuid4

from minio.error import S3Error

from zuno.platform.storage import MinioObjectStore, ObjectHashMismatchError

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"


def verify_phase04_minio_object_store() -> list[str]:
    errors: list[str] = []
    store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    bucket = f"phase04-verify-object-{uuid4().hex}"
    try:
        staged = store.stage_object(bucket=bucket, object_name="workspace/a.txt", content=b"phase04-object")
        try:
            store.commit_object(
                bucket=bucket,
                staged_object_name=staged.object_name,
                committed_object_name="committed/a.txt",
                expected_hash="0" * 64,
            )
            errors.append("MinIO hash mismatch did not fail closed")
        except ObjectHashMismatchError:
            pass

        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name="committed/a.txt",
            expected_hash=staged.content_hash,
        )
        if store.read_object(bucket=bucket, object_name=committed.object_name) != b"phase04-object":
            errors.append("MinIO committed object read returned unexpected bytes")
        try:
            store.read_object(bucket=bucket, object_name=staged.object_name)
            errors.append("MinIO staged object remained readable after commit cleanup")
        except S3Error:
            pass

        restore_point = store.create_restore_point(
            bucket=bucket,
            object_name=committed.object_name,
            restore_point_name="_restore/a.txt",
        )
        store.delete_object(bucket=bucket, object_name=committed.object_name)
        try:
            store.read_object(bucket=bucket, object_name=committed.object_name)
            errors.append("MinIO deleted object remained readable")
        except S3Error:
            pass

        restored = store.restore_object(
            bucket=bucket,
            restore_point_name=restore_point.object_name,
            restored_object_name="restored/a.txt",
        )
        if restored.content_hash != committed.content_hash:
            errors.append("MinIO restored object hash changed")
        if store.read_object(bucket=bucket, object_name=restored.object_name) != b"phase04-object":
            errors.append("MinIO restored object read returned unexpected bytes")
    finally:
        store.remove_bucket_tree(bucket)
    return errors


def main() -> int:
    errors = verify_phase04_minio_object_store()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 MinIO object store verification failed.")
        return 1
    print("PHASE04 MinIO object store verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
