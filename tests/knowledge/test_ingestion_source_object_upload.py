from __future__ import annotations

import hashlib

import pytest

from zuno.platform.storage.durable import ObjectCommitTicket
from zuno.platform.storage.object_store import ObjectStoreReceipt


class FakeDurableObjectStore:
    def __init__(self) -> None:
        self.staged: list[ObjectCommitTicket] = []
        self.committed: list[ObjectCommitTicket] = []

    def stage(
        self,
        *,
        bucket: str,
        committed_object_name: str,
        content: bytes,
    ) -> ObjectCommitTicket:
        content_hash = hashlib.sha256(content).hexdigest()
        ticket = ObjectCommitTicket(
            bucket=bucket,
            committed_object_name=committed_object_name,
            staged_receipt=ObjectStoreReceipt(
                bucket=bucket,
                object_name=f"_staging/{content_hash}/{committed_object_name}",
                content_hash=content_hash,
                size_bytes=len(content),
                visibility="staged",
            ),
        )
        self.staged.append(ticket)
        return ticket

    def commit(self, ticket: ObjectCommitTicket) -> ObjectStoreReceipt:
        self.committed.append(ticket)
        return ObjectStoreReceipt(
            bucket=ticket.bucket,
            object_name=ticket.committed_object_name,
            content_hash=ticket.staged_receipt.content_hash,
            size_bytes=ticket.staged_receipt.size_bytes,
            visibility="visible",
        )


def _runtime():
    from zuno.knowledge.ingestion import SourceObjectUploadRuntime

    store = FakeDurableObjectStore()
    return SourceObjectUploadRuntime(durable_object_store=store, bucket="zuno-input"), store


def _plan(runtime, *, content: bytes = b"# Policy\nInternal"):
    return runtime.initialize_upload(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        source_id="source-policy",
        filename="../policy.md",
        mime_type="text/markdown",
        owner_id="user-a",
        expected_sha256=hashlib.sha256(content).hexdigest(),
        expected_size_bytes=len(content),
        classification_ref="classification:internal",
        security_epoch_ref="security-epoch:workspace-a:1",
    )


def test_source_object_upload_init_stage_commit_uses_phase04_object_ref_only() -> None:
    content = b"# Policy\nInternal"
    runtime, store = _runtime()
    plan = _plan(runtime, content=content)

    staged = runtime.stage_upload(plan, content=content)
    receipt = runtime.commit_upload(staged)

    assert plan.status == "initialized"
    assert plan.payload_storage == "object_ref_only"
    assert plan.committed_object_name == "tenant-a/workspace-a/source/source-policy/policy.md"
    assert staged.status == "staged"
    assert store.staged == [staged.ticket]
    assert store.committed == [staged.ticket]
    assert receipt.status == "committed"
    assert receipt.payload_storage == "object_ref_only"
    assert receipt.object_ref == "s3://zuno-input/tenant-a/workspace-a/source/source-policy/policy.md"
    assert receipt.commit_receipt.source_object.storage_uri == receipt.object_ref
    assert receipt.commit_receipt.source_object.source_sha256 == plan.expected_sha256
    assert not hasattr(receipt.commit_receipt.source_object, "content")


def test_source_object_upload_rejects_partial_upload_and_hash_mismatch_before_stage() -> None:
    from zuno.knowledge.ingestion import SourceObjectUploadError

    content = b"complete upload"
    runtime, store = _runtime()
    plan = _plan(runtime, content=content)

    with pytest.raises(SourceObjectUploadError, match="partial upload"):
        runtime.stage_upload(plan, content=b"partial")
    with pytest.raises(SourceObjectUploadError, match="hash"):
        runtime.stage_upload(
            runtime.initialize_upload(
                tenant_id=plan.tenant_id,
                workspace_id=plan.workspace_id,
                source_id=plan.source_id,
                filename=plan.filename,
                mime_type=plan.mime_type,
                owner_id=plan.owner_id,
                expected_sha256="0" * 64,
                expected_size_bytes=len(content),
                classification_ref=plan.classification_ref,
                security_epoch_ref=plan.security_epoch_ref,
            ),
            content=content,
        )

    assert store.staged == []
    assert store.committed == []


def test_source_object_upload_enforces_tenant_scope_dedup_and_immutability() -> None:
    from zuno.knowledge.ingestion import SourceObjectConflictError, SourceObjectUploadError

    content = b"same bytes"
    runtime, store = _runtime()
    plan = _plan(runtime, content=content)
    first = runtime.commit_upload(runtime.stage_upload(plan, content=content))
    duplicate_source = runtime.commit_upload(runtime.stage_upload(plan, content=content))
    second_plan = runtime.initialize_upload(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        source_id="source-policy-copy",
        filename="policy-copy.md",
        mime_type="text/markdown",
        owner_id="user-a",
        expected_sha256=plan.expected_sha256,
        expected_size_bytes=len(content),
        classification_ref=plan.classification_ref,
        security_epoch_ref=plan.security_epoch_ref,
    )
    duplicate_hash = runtime.commit_upload(runtime.stage_upload(second_plan, content=content))

    assert first.status == "committed"
    assert duplicate_source.status == "deduplicated"
    assert duplicate_source.duplicate is True
    assert duplicate_source.object_ref == first.object_ref
    assert duplicate_hash.status == "deduplicated"
    assert duplicate_hash.duplicate is True
    assert duplicate_hash.object_ref != first.object_ref
    assert len(store.committed) == 2

    changed = b"different bytes"
    with pytest.raises(SourceObjectConflictError, match="immutable SourceObject"):
        runtime.commit_upload(runtime.stage_upload(_plan(runtime, content=changed), content=changed))
    with pytest.raises(SourceObjectUploadError):
        runtime.initialize_upload(
            tenant_id="tenant-a/../tenant-b",
            workspace_id="workspace-a",
            source_id="source-policy",
            filename="policy.md",
            mime_type="text/markdown",
            owner_id="user-a",
            expected_sha256=plan.expected_sha256,
            expected_size_bytes=len(content),
            classification_ref=plan.classification_ref,
            security_epoch_ref=plan.security_epoch_ref,
        )
