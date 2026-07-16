from __future__ import annotations

import hashlib
from dataclasses import dataclass
from io import BytesIO

from minio import Minio
from minio.commonconfig import CopySource


@dataclass(frozen=True, slots=True)
class ObjectStoreReceipt:
    bucket: str
    object_name: str
    content_hash: str
    size_bytes: int
    visibility: str


class ObjectHashMismatchError(RuntimeError):
    pass


class MinioObjectStore:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
    ) -> None:
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    def ensure_bucket(self, bucket: str) -> None:
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    def stage_object(self, *, bucket: str, object_name: str, content: bytes) -> ObjectStoreReceipt:
        self.ensure_bucket(bucket)
        content_hash = _sha256(content)
        staged_name = _staged_name(object_name, content_hash)
        self.client.put_object(
            bucket,
            staged_name,
            BytesIO(content),
            length=len(content),
            metadata={"x-amz-meta-zuno-sha256": content_hash, "x-amz-meta-zuno-visibility": "staged"},
        )
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=staged_name,
            content_hash=content_hash,
            size_bytes=len(content),
            visibility="staged",
        )

    def commit_object(
        self,
        *,
        bucket: str,
        staged_object_name: str,
        committed_object_name: str,
        expected_hash: str,
    ) -> ObjectStoreReceipt:
        content = self.read_object(bucket=bucket, object_name=staged_object_name)
        actual_hash = _sha256(content)
        if actual_hash != expected_hash:
            raise ObjectHashMismatchError("staged object hash does not match expected content hash")
        self.client.copy_object(bucket, committed_object_name, CopySource(bucket, staged_object_name))
        self.client.remove_object(bucket, staged_object_name)
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=committed_object_name,
            content_hash=actual_hash,
            size_bytes=len(content),
            visibility="visible",
        )

    def create_restore_point(self, *, bucket: str, object_name: str, restore_point_name: str) -> ObjectStoreReceipt:
        content = self.read_object(bucket=bucket, object_name=object_name)
        content_hash = _sha256(content)
        self.client.copy_object(bucket, restore_point_name, CopySource(bucket, object_name))
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=restore_point_name,
            content_hash=content_hash,
            size_bytes=len(content),
            visibility="restore_point",
        )

    def delete_object(self, *, bucket: str, object_name: str) -> ObjectStoreReceipt:
        content = self.read_object(bucket=bucket, object_name=object_name)
        self.client.remove_object(bucket, object_name)
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=object_name,
            content_hash=_sha256(content),
            size_bytes=len(content),
            visibility="deleted",
        )

    def restore_object(
        self,
        *,
        bucket: str,
        restore_point_name: str,
        restored_object_name: str,
    ) -> ObjectStoreReceipt:
        content = self.read_object(bucket=bucket, object_name=restore_point_name)
        content_hash = _sha256(content)
        self.client.copy_object(bucket, restored_object_name, CopySource(bucket, restore_point_name))
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=restored_object_name,
            content_hash=content_hash,
            size_bytes=len(content),
            visibility="restored",
        )

    def read_object(self, *, bucket: str, object_name: str) -> bytes:
        response = self.client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def remove_bucket_tree(self, bucket: str) -> None:
        if not self.client.bucket_exists(bucket):
            return
        for obj in self.client.list_objects(bucket, recursive=True):
            self.client.remove_object(bucket, obj.object_name)
        self.client.remove_bucket(bucket)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _staged_name(object_name: str, content_hash: str) -> str:
    return f"_staging/{content_hash}/{object_name.lstrip('/')}"


__all__ = [
    "MinioObjectStore",
    "ObjectHashMismatchError",
    "ObjectStoreReceipt",
]
