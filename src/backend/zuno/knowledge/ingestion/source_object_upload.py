from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Protocol

from zuno.knowledge.ingestion.source_object_commit import (
    SourceObjectCommitError,
    SourceObjectCommitReceipt,
    SourceObjectCommitRuntime,
)
from zuno.platform.storage.durable import ObjectCommitTicket


class SourceObjectUploadError(ValueError):
    pass


class SourceObjectConflictError(SourceObjectUploadError):
    pass


class DurableObjectStore(Protocol):
    def stage(
        self,
        *,
        bucket: str,
        committed_object_name: str,
        content: bytes,
    ) -> ObjectCommitTicket:
        ...

    def commit(self, ticket: ObjectCommitTicket):
        ...


@dataclass(frozen=True, slots=True)
class SourceObjectUploadPlan:
    tenant_id: str
    workspace_id: str
    source_id: str
    upload_session_ref: str
    bucket: str
    committed_object_name: str
    expected_sha256: str
    expected_size_bytes: int
    filename: str
    mime_type: str
    owner_id: str | None
    object_manifest_ref: str
    classification_ref: str
    security_epoch_ref: str
    payload_storage: Literal["object_ref_only"] = "object_ref_only"
    status: Literal["initialized"] = "initialized"


@dataclass(frozen=True, slots=True)
class SourceObjectStagedUpload:
    plan: SourceObjectUploadPlan
    ticket: ObjectCommitTicket
    staged_size_bytes: int
    staged_sha256: str
    status: Literal["staged"] = "staged"


@dataclass(frozen=True, slots=True)
class SourceObjectUploadReceipt:
    plan: SourceObjectUploadPlan
    commit_receipt: SourceObjectCommitReceipt
    object_ref: str
    object_manifest_ref: str
    payload_storage: Literal["object_ref_only"]
    duplicate: bool = False
    status: Literal["committed", "deduplicated"] = "committed"


class SourceObjectUploadRuntime:
    def __init__(
        self,
        *,
        durable_object_store: DurableObjectStore,
        bucket: str,
        commit_runtime: SourceObjectCommitRuntime | None = None,
    ) -> None:
        if not bucket.strip():
            raise SourceObjectUploadError("bucket must not be empty")
        self.durable_object_store = durable_object_store
        self.bucket = bucket
        self.commit_runtime = commit_runtime or SourceObjectCommitRuntime()
        self._committed_by_source_id: dict[tuple[str, str, str], SourceObjectUploadReceipt] = {}
        self._committed_by_hash: dict[tuple[str, str, str], SourceObjectUploadReceipt] = {}

    def initialize_upload(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        source_id: str,
        filename: str,
        mime_type: str,
        owner_id: str | None,
        expected_sha256: str,
        expected_size_bytes: int,
        classification_ref: str,
        security_epoch_ref: str,
    ) -> SourceObjectUploadPlan:
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(workspace_id, "workspace_id")
        _require_non_empty(source_id, "source_id")
        _require_non_empty(filename, "filename")
        _require_non_empty(mime_type, "mime_type")
        _require_non_empty(classification_ref, "classification_ref")
        _require_non_empty(security_epoch_ref, "security_epoch_ref")
        _require_sha256(expected_sha256, "expected_sha256")
        if expected_size_bytes <= 0:
            raise SourceObjectUploadError("expected_size_bytes must be positive")

        committed_object_name = "/".join(
            [
                _safe_path_component(tenant_id),
                _safe_path_component(workspace_id),
                "source",
                _safe_path_component(source_id),
                _safe_filename(filename),
            ]
        )
        object_manifest_ref = (
            f"object-manifest:{tenant_id}:{workspace_id}:{source_id}:{expected_sha256}"
        )
        upload_session_ref = (
            f"source-upload:{tenant_id}:{workspace_id}:{source_id}:{expected_sha256}"
        )
        return SourceObjectUploadPlan(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_id=source_id,
            upload_session_ref=upload_session_ref,
            bucket=self.bucket,
            committed_object_name=committed_object_name,
            expected_sha256=expected_sha256,
            expected_size_bytes=expected_size_bytes,
            filename=filename,
            mime_type=mime_type,
            owner_id=owner_id,
            object_manifest_ref=object_manifest_ref,
            classification_ref=classification_ref,
            security_epoch_ref=security_epoch_ref,
        )

    def stage_upload(
        self,
        plan: SourceObjectUploadPlan,
        *,
        content: bytes,
    ) -> SourceObjectStagedUpload:
        if not content:
            raise SourceObjectUploadError("upload content must not be empty")
        actual_size = len(content)
        if actual_size != plan.expected_size_bytes:
            raise SourceObjectUploadError("partial upload size does not match upload plan")
        import hashlib

        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != plan.expected_sha256:
            raise SourceObjectUploadError("upload content hash does not match upload plan")
        ticket = self.durable_object_store.stage(
            bucket=plan.bucket,
            committed_object_name=plan.committed_object_name,
            content=content,
        )
        return SourceObjectStagedUpload(
            plan=plan,
            ticket=ticket,
            staged_size_bytes=actual_size,
            staged_sha256=actual_hash,
        )

    def commit_upload(self, staged: SourceObjectStagedUpload) -> SourceObjectUploadReceipt:
        plan = staged.plan
        source_key = (plan.tenant_id, plan.workspace_id, plan.source_id)
        hash_key = (plan.tenant_id, plan.workspace_id, plan.expected_sha256)
        existing = self._committed_by_source_id.get(source_key)
        if existing is not None:
            if existing.commit_receipt.source_object.source_sha256 != plan.expected_sha256:
                raise SourceObjectConflictError("immutable SourceObject cannot change content hash")
            return SourceObjectUploadReceipt(
                plan=plan,
                commit_receipt=existing.commit_receipt,
                object_ref=existing.object_ref,
                object_manifest_ref=existing.object_manifest_ref,
                payload_storage=plan.payload_storage,
                duplicate=True,
                status="deduplicated",
            )

        duplicate = self._committed_by_hash.get(hash_key)
        committed_receipt = self.durable_object_store.commit(staged.ticket)
        try:
            commit_receipt = self.commit_runtime.commit_from_physical_receipt(
                tenant_id=plan.tenant_id,
                workspace_id=plan.workspace_id,
                source_id=plan.source_id,
                filename=plan.filename,
                mime_type=plan.mime_type,
                owner_id=plan.owner_id,
                committed_receipt=committed_receipt,
                object_manifest_ref=plan.object_manifest_ref,
                classification_ref=plan.classification_ref,
                security_epoch_ref=plan.security_epoch_ref,
                expected_sha256=plan.expected_sha256,
                expected_size_bytes=plan.expected_size_bytes,
                expected_object_prefix=f"{plan.tenant_id}/{plan.workspace_id}/",
            )
        except SourceObjectCommitError as exc:
            raise SourceObjectUploadError(str(exc)) from exc

        receipt = SourceObjectUploadReceipt(
            plan=plan,
            commit_receipt=commit_receipt,
            object_ref=commit_receipt.object_ref,
            object_manifest_ref=commit_receipt.object_manifest_ref,
            payload_storage=plan.payload_storage,
            duplicate=duplicate is not None,
            status="deduplicated" if duplicate is not None else "committed",
        )
        self._committed_by_source_id[source_key] = receipt
        self._committed_by_hash.setdefault(hash_key, receipt)
        return receipt


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise SourceObjectUploadError(f"{field_name} must not be empty")


def _require_sha256(value: str, field_name: str) -> None:
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise SourceObjectUploadError(f"{field_name} must be a lowercase SHA-256 digest")


def _safe_path_component(value: str) -> str:
    raw = value.strip()
    if "/" in raw or "\\" in raw or ".." in raw:
        raise SourceObjectUploadError("path component must not contain path traversal syntax")
    component = re.sub(r"[^A-Za-z0-9._:-]+", "-", raw).strip(".-/")
    if not component:
        raise SourceObjectUploadError("path component must contain a safe character")
    return component


def _safe_filename(value: str) -> str:
    filename = value.replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not filename or filename in {".", ".."}:
        raise SourceObjectUploadError("filename must identify a file")
    return _safe_path_component(filename)


__all__ = [
    "SourceObjectConflictError",
    "SourceObjectStagedUpload",
    "SourceObjectUploadError",
    "SourceObjectUploadPlan",
    "SourceObjectUploadReceipt",
    "SourceObjectUploadRuntime",
]
