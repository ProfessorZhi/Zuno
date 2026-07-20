from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from zuno.platform.storage.object_store import ObjectStoreReceipt

if TYPE_CHECKING:
    from zuno.knowledge.storage.contracts import SourceObjectRecord


class SourceObjectCommitError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class SourceObjectCommitReceipt:
    source_object: SourceObjectRecord
    object_manifest_ref: str
    object_ref: str
    classification_ref: str
    security_epoch_ref: str
    status: Literal["committed"] = "committed"


class SourceObjectCommitRuntime:
    def commit_from_physical_receipt(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        source_id: str,
        filename: str,
        mime_type: str,
        owner_id: str | None,
        committed_receipt: ObjectStoreReceipt,
        object_manifest_ref: str,
        classification_ref: str,
        security_epoch_ref: str,
        expected_sha256: str | None = None,
        expected_size_bytes: int | None = None,
        expected_object_prefix: str | None = None,
        allowed_mime_types: set[str] | None = None,
        sensitivity_tags: list[str] | None = None,
    ) -> SourceObjectCommitReceipt:
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(workspace_id, "workspace_id")
        _require_non_empty(source_id, "source_id")
        _require_non_empty(filename, "filename")
        _require_non_empty(mime_type, "mime_type")
        _require_non_empty(object_manifest_ref, "object_manifest_ref")
        _require_non_empty(classification_ref, "classification_ref")
        _require_non_empty(security_epoch_ref, "security_epoch_ref")
        if committed_receipt.visibility != "visible":
            raise SourceObjectCommitError("SourceObject commit requires visible PHASE04 object receipt")
        if committed_receipt.size_bytes <= 0:
            raise SourceObjectCommitError("SourceObject commit requires non-empty object bytes")
        _require_sha256(committed_receipt.content_hash, "object content hash")
        if expected_sha256 is not None and expected_sha256 != committed_receipt.content_hash:
            raise SourceObjectCommitError("SourceObject expected hash does not match PHASE04 object receipt")
        if expected_size_bytes is not None and expected_size_bytes != committed_receipt.size_bytes:
            raise SourceObjectCommitError("SourceObject expected size does not match PHASE04 object receipt")
        if allowed_mime_types is not None and mime_type not in allowed_mime_types:
            raise SourceObjectCommitError("SourceObject mime type is not allowed by parser policy")
        expected_prefix = expected_object_prefix or f"{tenant_id}/{workspace_id}/"
        if not committed_receipt.object_name.startswith(expected_prefix):
            raise SourceObjectCommitError("SourceObject object path is outside tenant/workspace prefix")
        object_ref = f"s3://{committed_receipt.bucket}/{committed_receipt.object_name}"
        from zuno.knowledge.storage import SourceObjectRecord

        source_object = SourceObjectRecord(
            source_id=source_id,
            workspace_id=workspace_id,
            owner_id=owner_id,
            source_uri=object_ref,
            storage_uri=object_ref,
            source_sha256=committed_receipt.content_hash,
            mime_type=mime_type,
            filename=filename,
            size_bytes=committed_receipt.size_bytes,
            acl_scope="workspace",
            sensitivity_tags=list(sensitivity_tags or []),
        )
        return SourceObjectCommitReceipt(
            source_object=source_object,
            object_manifest_ref=object_manifest_ref,
            object_ref=object_ref,
            classification_ref=classification_ref,
            security_epoch_ref=security_epoch_ref,
        )


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise SourceObjectCommitError(f"{field_name} must not be empty")


def _require_sha256(value: str, field_name: str) -> None:
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise SourceObjectCommitError(f"{field_name} must be a lowercase SHA-256 digest")


__all__ = [
    "SourceObjectCommitError",
    "SourceObjectCommitReceipt",
    "SourceObjectCommitRuntime",
]
