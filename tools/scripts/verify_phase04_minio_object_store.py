from __future__ import annotations

import hashlib
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
        duplicate_staged = store.stage_object(bucket=bucket, object_name="workspace/a.txt", content=b"phase04-object")
        if duplicate_staged.object_name != staged.object_name:
            errors.append("MinIO duplicate stage did not converge on deterministic staged object name")
        if duplicate_staged.content_hash != staged.content_hash:
            errors.append("MinIO duplicate stage did not preserve content hash")
        try:
            store.read_object(bucket=bucket, object_name="committed/a.txt")
            errors.append("MinIO visible object was readable before commit")
        except S3Error:
            pass
        try:
            store.read_object(bucket=bucket, object_name="missing/a.txt")
            errors.append("MinIO missing object read did not fail closed")
        except S3Error:
            pass
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

        multipart_content = (b"m" * (5 * 1024 * 1024)) + b"-phase04-tail"
        multipart_hash = hashlib.sha256(multipart_content).hexdigest()
        partial = store.begin_multipart_upload(
            bucket=bucket,
            object_name="workspace/large.bin",
            upload_session_ref="partial-session",
            expected_content_hash=multipart_hash,
            expected_size_bytes=len(multipart_content),
        )
        store.upload_multipart_part(
            partial,
            part_number=1,
            content=multipart_content[: 5 * 1024 * 1024],
        )
        try:
            store.read_object(bucket=bucket, object_name=partial.object_name)
            errors.append("MinIO partial multipart upload became visible before completion")
        except S3Error:
            pass
        if partial.upload_id not in store.incomplete_upload_ids([partial]):
            errors.append("MinIO did not report the partial multipart upload")
        if store.reconcile_incomplete_uploads(
            sessions=[partial],
            active_upload_ids={partial.upload_id},
        ):
            errors.append("MinIO reconciliation aborted an active multipart upload")
        cleanup = store.reconcile_incomplete_uploads(sessions=[partial])
        if len(cleanup) != 1 or cleanup[0].upload_id != partial.upload_id:
            errors.append("MinIO reconciliation did not abort the orphan multipart upload")

        session = store.begin_multipart_upload(
            bucket=bucket,
            object_name="workspace/large.bin",
            upload_session_ref="lost-response-session",
            expected_content_hash=multipart_hash,
            expected_size_bytes=len(multipart_content),
        )
        first = store.upload_multipart_part(
            session,
            part_number=1,
            content=multipart_content[: 5 * 1024 * 1024],
        )
        second = store.upload_multipart_part(
            session,
            part_number=2,
            content=multipart_content[5 * 1024 * 1024 :],
        )
        complete = store.client._complete_multipart_upload

        def complete_then_lose_response(*args, **kwargs):
            complete(*args, **kwargs)
            raise TimeoutError("simulated response loss after MinIO committed the multipart upload")

        store.client._complete_multipart_upload = complete_then_lose_response
        try:
            multipart_staged = store.complete_multipart_upload(session, [first, second])
        finally:
            store.client._complete_multipart_upload = complete
        if multipart_staged.content_hash != multipart_hash:
            errors.append("MinIO lost-response reconciliation returned the wrong content hash")
        duplicate_complete = store.complete_multipart_upload(session, [first, second])
        if duplicate_complete != multipart_staged:
            errors.append("MinIO duplicate multipart completion did not converge on the staged receipt")
        multipart_committed = store.commit_object(
            bucket=bucket,
            staged_object_name=multipart_staged.object_name,
            committed_object_name="committed/large.bin",
            expected_hash=multipart_hash,
        )
        if store.read_object(bucket=bucket, object_name=multipart_committed.object_name) != multipart_content:
            errors.append("MinIO multipart committed object returned unexpected bytes")
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
