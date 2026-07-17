from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Callable, Iterable

from minio import Minio
from minio.commonconfig import ENABLED, CopySource, Filter
from minio.datatypes import Part
from minio.deleteobjects import DeleteObject
from minio.error import S3Error
from minio.helpers import genheaders
from minio.lifecycleconfig import Expiration, LifecycleConfig, Rule
from minio.retention import GOVERNANCE, Retention


@dataclass(frozen=True, slots=True)
class ObjectStoreReceipt:
    bucket: str
    object_name: str
    content_hash: str
    size_bytes: int
    visibility: str
    version_id: str | None = None


@dataclass(frozen=True, slots=True)
class MultipartUploadSession:
    bucket: str
    object_name: str
    upload_id: str
    expected_content_hash: str
    expected_size_bytes: int


@dataclass(frozen=True, slots=True)
class MultipartPartReceipt:
    part_number: int
    etag: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class MultipartCleanupReceipt:
    bucket: str
    object_name: str
    upload_id: str
    status: str


@dataclass(frozen=True, slots=True)
class ObjectGovernanceReceipt:
    bucket: str
    object_name: str
    version_id: str | None
    retention_mode: str | None
    retain_until: datetime | None
    legal_hold: bool


@dataclass(frozen=True, slots=True)
class ObjectLifecycleReceipt:
    bucket: str
    rule_id: str
    prefix: str
    expire_after_days: int
    status: str


class ObjectHashMismatchError(RuntimeError):
    pass


class ObjectAuthorizationError(PermissionError):
    pass


class MinioObjectStore:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
        authorization_hook: Callable[[str, str, str | None], bool] | None = None,
    ) -> None:
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        self.authorization_hook = authorization_hook

    def ensure_bucket(self, bucket: str, *, object_lock: bool = False) -> None:
        self._authorize("bucket:ensure", bucket, None)
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket, object_lock=object_lock)

    def stage_object(self, *, bucket: str, object_name: str, content: bytes) -> ObjectStoreReceipt:
        self._authorize("object:stage", bucket, object_name)
        self.ensure_bucket(bucket)
        content_hash = _sha256(content)
        staged_name = _staged_name(object_name, content_hash)
        result = self.client.put_object(
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
            version_id=result.version_id,
        )

    def begin_multipart_upload(
        self,
        *,
        bucket: str,
        object_name: str,
        upload_session_ref: str,
        expected_content_hash: str,
        expected_size_bytes: int,
    ) -> MultipartUploadSession:
        self._authorize("multipart:begin", bucket, object_name)
        if expected_size_bytes < 0:
            raise ValueError("expected_size_bytes must be non-negative")
        if len(expected_content_hash) != 64 or any(
            char not in "0123456789abcdef" for char in expected_content_hash
        ):
            raise ValueError("expected_content_hash must be a lowercase SHA-256 digest")
        self.ensure_bucket(bucket)
        staged_name = _multipart_staged_name(object_name, upload_session_ref, expected_content_hash)
        for upload in self._list_incomplete_uploads(bucket=bucket, object_name=staged_name):
            if upload.object_name == staged_name and upload.upload_id:
                return MultipartUploadSession(
                    bucket=bucket,
                    object_name=staged_name,
                    upload_id=upload.upload_id,
                    expected_content_hash=expected_content_hash,
                    expected_size_bytes=expected_size_bytes,
                )

        metadata = genheaders(
            {
                "zuno-sha256": expected_content_hash,
                "zuno-visibility": "staged",
                "zuno-upload-session": upload_session_ref,
            },
            None,
            None,
            None,
            False,
        )
        # minio-py has no public API for a caller-managed resumable upload session.
        upload_id = self.client._create_multipart_upload(bucket, staged_name, metadata)
        listed_uploads = list(self._list_incomplete_uploads(bucket=bucket, object_name=staged_name))
        if listed_uploads and listed_uploads[0].upload_id:
            upload_id = listed_uploads[0].upload_id
        return MultipartUploadSession(
            bucket=bucket,
            object_name=staged_name,
            upload_id=upload_id,
            expected_content_hash=expected_content_hash,
            expected_size_bytes=expected_size_bytes,
        )

    def upload_multipart_part(
        self,
        session: MultipartUploadSession,
        *,
        part_number: int,
        content: bytes,
    ) -> MultipartPartReceipt:
        self._authorize("multipart:upload_part", session.bucket, session.object_name)
        if not 1 <= part_number <= 10_000:
            raise ValueError("part_number must be between 1 and 10000")
        if not content:
            raise ValueError("multipart part content must not be empty")
        etag = self.client._upload_part(
            session.bucket,
            session.object_name,
            content,
            None,
            session.upload_id,
            part_number,
        )
        return MultipartPartReceipt(part_number=part_number, etag=etag, size_bytes=len(content))

    def complete_multipart_upload(
        self,
        session: MultipartUploadSession,
        parts: Iterable[MultipartPartReceipt],
    ) -> ObjectStoreReceipt:
        self._authorize("multipart:complete", session.bucket, session.object_name)
        ordered_parts = sorted(parts, key=lambda item: item.part_number)
        if not ordered_parts or [part.part_number for part in ordered_parts] != list(
            range(1, len(ordered_parts) + 1)
        ):
            raise ValueError("multipart parts must be contiguous and start at part 1")
        sdk_parts = [Part(part.part_number, part.etag) for part in ordered_parts]
        try:
            self.client._complete_multipart_upload(
                session.bucket,
                session.object_name,
                session.upload_id,
                sdk_parts,
            )
        except Exception:
            recovered = self._recover_completed_multipart_upload(session)
            if recovered is not None:
                return recovered
            raise
        return self._verified_staged_receipt(session)

    def abort_multipart_upload(self, session: MultipartUploadSession) -> MultipartCleanupReceipt:
        self._authorize("multipart:abort", session.bucket, session.object_name)
        self.client._abort_multipart_upload(session.bucket, session.object_name, session.upload_id)
        return MultipartCleanupReceipt(
            bucket=session.bucket,
            object_name=session.object_name,
            upload_id=session.upload_id,
            status="aborted",
        )

    def reconcile_incomplete_uploads(
        self,
        *,
        sessions: Iterable[MultipartUploadSession],
        active_upload_ids: Iterable[str] = (),
    ) -> list[MultipartCleanupReceipt]:
        active = set(active_upload_ids)
        cleaned: list[MultipartCleanupReceipt] = []
        for session in sessions:
            self._authorize("multipart:reconcile", session.bucket, session.object_name)
            for upload in self._list_incomplete_uploads(
                bucket=session.bucket,
                object_name=session.object_name,
            ):
                if not upload.upload_id or upload.upload_id in active:
                    continue
                self.client._abort_multipart_upload(
                    session.bucket,
                    upload.object_name,
                    upload.upload_id,
                )
                cleaned.append(
                    MultipartCleanupReceipt(
                        bucket=session.bucket,
                        object_name=upload.object_name,
                        upload_id=upload.upload_id,
                        status="orphan_aborted",
                    )
                )
        return cleaned

    def incomplete_upload_ids(self, sessions: Iterable[MultipartUploadSession]) -> set[str]:
        upload_ids: set[str] = set()
        for session in sessions:
            upload_ids.update(
                upload.upload_id
                for upload in self._list_incomplete_uploads(
                    bucket=session.bucket,
                    object_name=session.object_name,
                )
                if upload.upload_id
            )
        return upload_ids

    def commit_object(
        self,
        *,
        bucket: str,
        staged_object_name: str,
        committed_object_name: str,
        expected_hash: str,
    ) -> ObjectStoreReceipt:
        self._authorize("object:commit", bucket, committed_object_name)
        content = self.read_object(bucket=bucket, object_name=staged_object_name)
        actual_hash = _sha256(content)
        if actual_hash != expected_hash:
            raise ObjectHashMismatchError("staged object hash does not match expected content hash")
        result = self.client.copy_object(bucket, committed_object_name, CopySource(bucket, staged_object_name))
        self.client.remove_object(bucket, staged_object_name)
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=committed_object_name,
            content_hash=actual_hash,
            size_bytes=len(content),
            visibility="visible",
            version_id=result.version_id,
        )

    def create_restore_point(self, *, bucket: str, object_name: str, restore_point_name: str) -> ObjectStoreReceipt:
        self._authorize("object:create_restore_point", bucket, object_name)
        content = self.read_object(bucket=bucket, object_name=object_name)
        content_hash = _sha256(content)
        result = self.client.copy_object(bucket, restore_point_name, CopySource(bucket, object_name))
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=restore_point_name,
            content_hash=content_hash,
            size_bytes=len(content),
            visibility="restore_point",
            version_id=result.version_id,
        )

    def delete_object(self, *, bucket: str, object_name: str) -> ObjectStoreReceipt:
        self._authorize("object:delete", bucket, object_name)
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
        self._authorize("object:restore", bucket, restored_object_name)
        content = self.read_object(bucket=bucket, object_name=restore_point_name)
        content_hash = _sha256(content)
        result = self.client.copy_object(bucket, restored_object_name, CopySource(bucket, restore_point_name))
        return ObjectStoreReceipt(
            bucket=bucket,
            object_name=restored_object_name,
            content_hash=content_hash,
            size_bytes=len(content),
            visibility="restored",
            version_id=result.version_id,
        )

    def read_object(self, *, bucket: str, object_name: str) -> bytes:
        self._authorize("object:read", bucket, object_name)
        response = self.client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def apply_object_governance(
        self,
        *,
        bucket: str,
        object_name: str,
        retain_until: datetime,
        legal_hold: bool,
        version_id: str | None = None,
        retention_mode: str = GOVERNANCE,
    ) -> ObjectGovernanceReceipt:
        self._authorize("object:governance_write", bucket, object_name)
        if retain_until.tzinfo is None:
            raise ValueError("retain_until must be timezone-aware")
        self.client.set_object_retention(
            bucket,
            object_name,
            Retention(retention_mode, retain_until),
            version_id=version_id,
        )
        if legal_hold:
            self.client.enable_object_legal_hold(bucket, object_name, version_id=version_id)
        else:
            self.client.disable_object_legal_hold(bucket, object_name, version_id=version_id)
        return self.object_governance(
            bucket=bucket,
            object_name=object_name,
            version_id=version_id,
        )

    def object_governance(
        self,
        *,
        bucket: str,
        object_name: str,
        version_id: str | None = None,
    ) -> ObjectGovernanceReceipt:
        self._authorize("object:governance_read", bucket, object_name)
        retention = self.client.get_object_retention(bucket, object_name, version_id=version_id)
        legal_hold = self.client.is_object_legal_hold_enabled(bucket, object_name, version_id=version_id)
        return ObjectGovernanceReceipt(
            bucket=bucket,
            object_name=object_name,
            version_id=version_id,
            retention_mode=None if retention is None else retention.mode,
            retain_until=None if retention is None else retention.retain_until_date,
            legal_hold=legal_hold,
        )

    def purge_object_version(self, *, bucket: str, object_name: str, version_id: str) -> None:
        self._authorize("object:purge", bucket, object_name)
        self.client.remove_object(bucket, object_name, version_id=version_id)

    def configure_staging_lifecycle(
        self,
        *,
        bucket: str,
        expire_after_days: int = 7,
    ) -> ObjectLifecycleReceipt:
        self._authorize("bucket:lifecycle_write", bucket, None)
        rule_id = "zuno-staging-lifecycle"
        config = LifecycleConfig(
            [
                Rule(
                    status=ENABLED,
                    rule_filter=Filter(prefix="_staging/"),
                    rule_id=rule_id,
                    expiration=Expiration(days=expire_after_days),
                )
            ]
        )
        self.client.set_bucket_lifecycle(bucket, config)
        return self.staging_lifecycle(bucket=bucket)

    def staging_lifecycle(self, *, bucket: str) -> ObjectLifecycleReceipt:
        self._authorize("bucket:lifecycle_read", bucket, None)
        config = self.client.get_bucket_lifecycle(bucket)
        if config is None:
            raise RuntimeError("staging lifecycle is not configured")
        for rule in config.rules:
            if rule.rule_id != "zuno-staging-lifecycle":
                continue
            prefix = "" if rule.rule_filter is None else rule.rule_filter.prefix or ""
            expiration_days = 0 if rule.expiration is None else rule.expiration.days or 0
            return ObjectLifecycleReceipt(
                bucket=bucket,
                rule_id=rule.rule_id,
                prefix=prefix,
                expire_after_days=expiration_days,
                status=rule.status,
            )
        raise RuntimeError("zuno staging lifecycle rule is missing")

    def remove_bucket_tree(self, bucket: str) -> None:
        self._authorize("bucket:purge", bucket, None)
        if not self.client.bucket_exists(bucket):
            return
        objects = list(self.client.list_objects(bucket, recursive=True, include_version=True))
        for obj in objects:
            if obj.version_id:
                try:
                    if self.client.is_object_legal_hold_enabled(
                        bucket,
                        obj.object_name,
                        version_id=obj.version_id,
                    ):
                        self.client.disable_object_legal_hold(
                            bucket,
                            obj.object_name,
                            version_id=obj.version_id,
                        )
                except S3Error:
                    pass
        delete_errors = list(
            self.client.remove_objects(
                bucket,
                [DeleteObject(obj.object_name, obj.version_id) for obj in objects],
                bypass_governance_mode=True,
            )
        )
        if delete_errors:
            raise RuntimeError(f"failed to clean object store test bucket: {delete_errors[0]}")
        self.client.remove_bucket(bucket)

    def _recover_completed_multipart_upload(self, session: MultipartUploadSession) -> ObjectStoreReceipt | None:
        try:
            return self._verified_staged_receipt(session)
        except Exception as exc:
            if getattr(exc, "code", None) in {"NoSuchKey", "NoSuchObject"}:
                return None
            raise

    def _verified_staged_receipt(self, session: MultipartUploadSession) -> ObjectStoreReceipt:
        content = self.read_object(bucket=session.bucket, object_name=session.object_name)
        actual_hash = _sha256(content)
        if actual_hash != session.expected_content_hash:
            self.client.remove_object(session.bucket, session.object_name)
            raise ObjectHashMismatchError("multipart object hash does not match expected content hash")
        if len(content) != session.expected_size_bytes:
            self.client.remove_object(session.bucket, session.object_name)
            raise ObjectHashMismatchError("multipart object size does not match expected size")
        return ObjectStoreReceipt(
            bucket=session.bucket,
            object_name=session.object_name,
            content_hash=actual_hash,
            size_bytes=len(content),
            visibility="staged",
        )

    def _list_incomplete_uploads(self, *, bucket: str, object_name: str):
        result = self.client._list_multipart_uploads(bucket, prefix=object_name)
        yield from (upload for upload in result.uploads if upload.object_name == object_name)

    def _authorize(self, action: str, bucket: str, object_name: str | None) -> None:
        if self.authorization_hook is None:
            return
        try:
            allowed = self.authorization_hook(action, bucket, object_name)
        except Exception as exc:
            raise ObjectAuthorizationError(f"authorization hook failed closed for {action}") from exc
        if allowed is not True:
            raise ObjectAuthorizationError(f"authorization denied for {action}")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _staged_name(object_name: str, content_hash: str) -> str:
    return f"_staging/{content_hash}/{object_name.lstrip('/')}"


def _multipart_staged_name(object_name: str, upload_session_ref: str, content_hash: str) -> str:
    session_component = upload_session_ref.strip("/")
    if not session_component or ".." in session_component.split("/"):
        raise ValueError("upload_session_ref must identify a safe relative object prefix")
    return f"_staging/{content_hash}/{session_component}/{object_name.lstrip('/')}"


__all__ = [
    "MinioObjectStore",
    "MultipartCleanupReceipt",
    "MultipartPartReceipt",
    "MultipartUploadSession",
    "ObjectAuthorizationError",
    "ObjectGovernanceReceipt",
    "ObjectHashMismatchError",
    "ObjectLifecycleReceipt",
    "ObjectStoreReceipt",
]
