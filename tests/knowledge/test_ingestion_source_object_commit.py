from __future__ import annotations

import pytest

from zuno.platform.storage.object_store import ObjectStoreReceipt


HEX_64 = "c" * 64


def _receipt(**overrides) -> ObjectStoreReceipt:
    payload = {
        "bucket": "zuno-input",
        "object_name": "tenant-a/workspace-a/source/policy.md",
        "content_hash": HEX_64,
        "size_bytes": 42,
        "visibility": "visible",
        "version_id": "version:1",
    }
    payload.update(overrides)
    return ObjectStoreReceipt(**payload)


def _commit(**overrides):
    from zuno.knowledge.ingestion import SourceObjectCommitRuntime

    payload = {
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "source_id": "source:policy",
        "filename": "policy.md",
        "mime_type": "text/markdown",
        "owner_id": "user-a",
        "committed_receipt": _receipt(),
        "object_manifest_ref": "manifest:source:policy",
        "classification_ref": "classification:internal",
        "security_epoch_ref": "security-epoch:workspace-a:1",
        "expected_sha256": HEX_64,
        "expected_size_bytes": 42,
        "allowed_mime_types": {"text/markdown"},
        "sensitivity_tags": ["internal"],
    }
    payload.update(overrides)
    return SourceObjectCommitRuntime().commit_from_physical_receipt(**payload)


def test_source_object_commit_consumes_phase04_visible_object_receipt() -> None:
    receipt = _commit()

    assert receipt.status == "committed"
    assert receipt.object_manifest_ref == "manifest:source:policy"
    assert receipt.object_ref == "s3://zuno-input/tenant-a/workspace-a/source/policy.md"
    assert receipt.source_object.source_sha256 == HEX_64
    assert receipt.source_object.storage_uri == receipt.object_ref
    assert receipt.source_object.size_bytes == 42
    assert receipt.source_object.mime_type == "text/markdown"
    assert receipt.source_object.sensitivity_tags == ["internal"]


@pytest.mark.parametrize(
    ("field", "committed_receipt"),
    [
        ("visibility", _receipt(visibility="staged")),
        ("content_hash", _receipt(content_hash="bad")),
        ("size_bytes", _receipt(size_bytes=0)),
        ("object_name", _receipt(object_name="tenant-b/workspace-a/source/policy.md")),
    ],
)
def test_source_object_commit_rejects_invalid_phase04_receipt(
    field: str,
    committed_receipt: ObjectStoreReceipt,
) -> None:
    from zuno.knowledge.ingestion import SourceObjectCommitError

    with pytest.raises(SourceObjectCommitError):
        _commit(committed_receipt=committed_receipt)


def test_source_object_commit_rejects_policy_mismatch() -> None:
    from zuno.knowledge.ingestion import SourceObjectCommitError

    with pytest.raises(SourceObjectCommitError, match="expected hash"):
        _commit(expected_sha256="d" * 64)
    with pytest.raises(SourceObjectCommitError, match="expected size"):
        _commit(expected_size_bytes=43)
    with pytest.raises(SourceObjectCommitError, match="mime type"):
        _commit(mime_type="application/x-msdownload", allowed_mime_types={"text/markdown"})
