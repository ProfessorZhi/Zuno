from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable

from sqlalchemy import Engine

from zuno.knowledge.indexing import IndexJobManifest, IndexTarget, KnowledgeIndexRuntime
from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.knowledge import KnowledgeCutoverConflict, KnowledgeUnitOfWork
from zuno.platform.database.knowledge.domain import KnowledgeVersionDraft

from .contracts import CanonicalDocumentIR, ParseJobSnapshot
from .handoff import IndexableDocumentSnapshotV1
from .production_runtime import PackageAUploadReceipt, PackageAWorkerReceipt


class CanonicalIngestionState(StrEnum):
    ACCEPTED = "accepted"
    OBJECT_STAGED = "object_staged"
    OBJECT_COMMITTED = "object_committed"
    CANONICAL_IR_READY = "canonical_ir_ready"
    INDEXING = "indexing"
    INDEXES_VISIBLE = "indexes_visible"
    SNAPSHOT_ACTIVATED = "snapshot_activated"
    OBJECT_COMMIT_FAILED = "object_commit_failed"
    CANONICALIZATION_FAILED = "canonicalization_failed"
    INDEX_PARTIALLY_FAILED = "index_partially_failed"
    INDEX_VISIBILITY_FAILED = "index_visibility_failed"
    SNAPSHOT_ACTIVATION_BLOCKED = "snapshot_activation_blocked"
    CREDENTIAL_BLOCKED = "credential_blocked"
    SECURITY_DENIED = "security_denied"


@dataclass(frozen=True, slots=True)
class CanonicalIngestionReceipt:
    job_id: str
    tenant_id: str
    workspace_id: str
    knowledge_space_id: str
    state: CanonicalIngestionState
    state_transitions: tuple[CanonicalIngestionState, ...]
    source_object_id: str
    document_version_id: str
    indexable_snapshot_id: str | None = None
    knowledge_version_id: str | None = None
    snapshot_id: str | None = None
    cutover_id: str | None = None
    index_manifest: IndexJobManifest | None = None
    blocker: str | None = None
    activated: bool = False
    idempotency_key: str = ""


@dataclass(frozen=True, slots=True)
class CanonicalIngestionRuntimeInput:
    tenant_id: str
    workspace_id: str
    knowledge_space_id: str
    upload_receipt: PackageAUploadReceipt
    worker_receipt: PackageAWorkerReceipt
    document: CanonicalDocumentIR
    parse_snapshot: ParseJobSnapshot
    indexable_snapshot: IndexableDocumentSnapshotV1
    security_epoch_ref: str
    required_targets: tuple[IndexTarget, ...] = ("bm25", "vector", "graph")
    graph_project_id: str | None = None


class CanonicalIngestionSliceRuntime:
    """Strict PHASE22 canonical ingestion bridge from Package A handoff to Knowledge activation."""

    def __init__(
        self,
        *,
        engine: Engine,
        index_runtime: KnowledgeIndexRuntime | None = None,
        knowledge_uow_factory: Callable[[Engine], Any] = KnowledgeUnitOfWork,
    ) -> None:
        self.engine = engine
        self.index_runtime = index_runtime or KnowledgeIndexRuntime()
        self.knowledge_uow_factory = knowledge_uow_factory

    def activate_from_package_a_handoff(
        self,
        command: CanonicalIngestionRuntimeInput,
    ) -> CanonicalIngestionReceipt:
        transitions = [
            CanonicalIngestionState.ACCEPTED,
            CanonicalIngestionState.OBJECT_STAGED,
            CanonicalIngestionState.OBJECT_COMMITTED,
        ]
        if command.worker_receipt.status == "dead_letter":
            return self._blocked_receipt(
                command,
                transitions=tuple(transitions),
                state=CanonicalIngestionState.OBJECT_COMMIT_FAILED,
                blocker=command.worker_receipt.failure_code or "object_commit_failed",
            )
        if command.worker_receipt.status != "succeeded" or command.worker_receipt.indexable_snapshot_id is None:
            return self._blocked_receipt(
                command,
                transitions=tuple(transitions),
                state=CanonicalIngestionState.CANONICALIZATION_FAILED,
                blocker=f"package_a_worker_status:{command.worker_receipt.status}",
            )
        transitions.extend(
            [
                CanonicalIngestionState.CANONICAL_IR_READY,
                CanonicalIngestionState.INDEXING,
            ]
        )
        self.index_runtime.create_knowledge_space(
            command.knowledge_space_id,
            command.workspace_id,
            graph_project_id=command.graph_project_id,
        )
        try:
            manifest = self.index_runtime.index_document(
                command.knowledge_space_id,
                command.document,
                targets=list(command.required_targets),
                parse_job_snapshot=command.parse_snapshot,
            )
        except Exception as exc:
            return self._blocked_receipt(
                command,
                transitions=tuple(transitions),
                state=_index_exception_state(exc),
                blocker=f"{type(exc).__name__}:{exc}",
            )
        visibility_blocker = _visibility_blocker(manifest, required_targets=command.required_targets)
        if visibility_blocker is not None:
            state = (
                CanonicalIngestionState.INDEX_VISIBILITY_FAILED
                if all(target in manifest.adapter_visibility_receipts for target in command.required_targets)
                else CanonicalIngestionState.INDEX_PARTIALLY_FAILED
            )
            return self._blocked_receipt(
                command,
                transitions=tuple(transitions),
                state=state,
                blocker=visibility_blocker,
                manifest=manifest,
            )
        transitions.append(CanonicalIngestionState.INDEXES_VISIBLE)
        try:
            knowledge_version_id, snapshot_id, cutover_id = self._activate_snapshot(
                command=command,
                manifest=manifest,
            )
        except KnowledgeCutoverConflict as exc:
            return self._blocked_receipt(
                command,
                transitions=tuple(transitions),
                state=CanonicalIngestionState.SNAPSHOT_ACTIVATION_BLOCKED,
                blocker=f"{type(exc).__name__}:{exc}",
                manifest=manifest,
            )
        transitions.append(CanonicalIngestionState.SNAPSHOT_ACTIVATED)
        return CanonicalIngestionReceipt(
            job_id=_job_id(command),
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            knowledge_space_id=command.knowledge_space_id,
            state=CanonicalIngestionState.SNAPSHOT_ACTIVATED,
            state_transitions=tuple(transitions),
            source_object_id=command.upload_receipt.source_object_id,
            document_version_id=command.upload_receipt.document_version_id,
            indexable_snapshot_id=command.indexable_snapshot.indexable_snapshot_id,
            knowledge_version_id=knowledge_version_id,
            snapshot_id=snapshot_id,
            cutover_id=cutover_id,
            index_manifest=manifest,
            activated=True,
            idempotency_key=_idempotency_key(command),
        )

    def _activate_snapshot(
        self,
        *,
        command: CanonicalIngestionRuntimeInput,
        manifest: IndexJobManifest,
    ) -> tuple[str, str, str]:
        knowledge_version_id = _knowledge_version_id(command)
        snapshot_id = f"snapshot:{knowledge_version_id}"
        cutover_id = f"cutover:{knowledge_version_id}"
        with self.knowledge_uow_factory(self.engine) as repo:
            version_no = repo.next_version_no(
                tenant_id=command.tenant_id,
                workspace_id=command.workspace_id,
                knowledge_space_id=command.knowledge_space_id,
            )
            repo.create_version(
                KnowledgeVersionDraft(
                    knowledge_version_id=knowledge_version_id,
                    tenant_id=command.tenant_id,
                    workspace_id=command.workspace_id,
                    knowledge_space_id=command.knowledge_space_id,
                    version_no=version_no,
                    document_set={"documents": [command.upload_receipt.document_version_id]},
                    source_span_manifest={"source_span_refs": command.indexable_snapshot.source_span_refs},
                    index_spec=manifest.model_dump(mode="json"),
                    security_epoch_ref=command.security_epoch_ref,
                )
            )
            for block in command.document.blocks:
                source_span_ref = _source_span_ref(command=command, block_id=block.block_id)
                repo.append_chunk(
                    chunk_id=f"chunk:{knowledge_version_id}:{block.block_id}",
                    tenant_id=command.tenant_id,
                    knowledge_version_id=knowledge_version_id,
                    document_version_id=command.upload_receipt.document_version_id,
                    source_span_ref=source_span_ref,
                    chunk_payload=block.model_dump(mode="json"),
                    acl_ref=block.acl_scope,
                    authority_ref=command.security_epoch_ref,
                )
            for attempt, target in enumerate(command.required_targets, start=1):
                receipt = manifest.adapter_visibility_receipts[target]
                repo.record_index_visibility(
                    job_id=f"{manifest.job_id}:{target}",
                    tenant_id=command.tenant_id,
                    knowledge_version_id=knowledge_version_id,
                    index_kind=target.upper(),
                    lease_ref=f"lease:{manifest.job_id}:{target}",
                    fencing_token=1,
                    attempt_no=attempt,
                    write_batch={
                        "target": target,
                        "dispatch": manifest.adapter_dispatch_receipts.get(target),
                        "visibility": receipt,
                    },
                    visibility_receipt_ref=str(receipt["receipt_ref"]),
                )
            repo.mark_ready(knowledge_version_id=knowledge_version_id)
            repo.create_snapshot(
                snapshot_id=snapshot_id,
                tenant_id=command.tenant_id,
                knowledge_version_id=knowledge_version_id,
                snapshot_payload={
                    "indexable_snapshot_id": command.indexable_snapshot.indexable_snapshot_id,
                    "index_manifest": manifest.model_dump(mode="json"),
                },
                serving_watermark_ref=f"watermark:{manifest.job_id}",
            )
            repo.cutover(
                cutover_id=cutover_id,
                tenant_id=command.tenant_id,
                knowledge_space_id=command.knowledge_space_id,
                to_version_id=knowledge_version_id,
                expected_generation=repo.next_cutover_expected_generation(
                    tenant_id=command.tenant_id,
                    knowledge_space_id=command.knowledge_space_id,
                ),
                decision_payload={
                    "required_targets": list(command.required_targets),
                    "visibility_receipts": manifest.adapter_visibility_receipts,
                },
            )
        return knowledge_version_id, snapshot_id, cutover_id

    @staticmethod
    def _blocked_receipt(
        command: CanonicalIngestionRuntimeInput,
        *,
        transitions: tuple[CanonicalIngestionState, ...],
        state: CanonicalIngestionState,
        blocker: str,
        manifest: IndexJobManifest | None = None,
    ) -> CanonicalIngestionReceipt:
        return CanonicalIngestionReceipt(
            job_id=_job_id(command),
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            knowledge_space_id=command.knowledge_space_id,
            state=state,
            state_transitions=(*transitions, state),
            source_object_id=command.upload_receipt.source_object_id,
            document_version_id=command.upload_receipt.document_version_id,
            indexable_snapshot_id=command.indexable_snapshot.indexable_snapshot_id,
            index_manifest=manifest,
            blocker=blocker,
            idempotency_key=_idempotency_key(command),
        )


def _visibility_blocker(
    manifest: IndexJobManifest,
    *,
    required_targets: tuple[IndexTarget, ...],
) -> str | None:
    for target in required_targets:
        receipt = manifest.adapter_visibility_receipts.get(target)
        if receipt is None:
            return f"{target}:missing_visibility_receipt"
        if receipt.get("visibility") != "visible":
            return f"{target}:visibility:{receipt.get('visibility')}:{receipt.get('visibility_failure_reason')}"
        if manifest.target_status.get(target) != "ready":
            return f"{target}:target_status:{manifest.target_status.get(target)}"
    return None


def _index_exception_state(exc: Exception) -> CanonicalIngestionState:
    text = f"{type(exc).__name__}:{exc}".lower()
    if "credential" in text or "authentication" in text or "unauthorized" in text:
        return CanonicalIngestionState.CREDENTIAL_BLOCKED
    if "security" in text or "acl" in text or "tenant" in text:
        return CanonicalIngestionState.SECURITY_DENIED
    return CanonicalIngestionState.INDEX_PARTIALLY_FAILED


def _source_span_ref(*, command: CanonicalIngestionRuntimeInput, block_id: str) -> str:
    for ref in command.indexable_snapshot.source_span_refs:
        if str(ref.get("block_id")) == block_id and ref.get("source_span_ref"):
            return str(ref["source_span_ref"])
    return f"source-span:{command.parse_snapshot.parse_attempt_id}:{block_id}"


def _knowledge_version_id(command: CanonicalIngestionRuntimeInput) -> str:
    return f"knowledge-version:{canonical_sha256({'idempotency_key': _idempotency_key(command)})[:24]}"


def _job_id(command: CanonicalIngestionRuntimeInput) -> str:
    return f"canonical-ingestion:{canonical_sha256({'idempotency_key': _idempotency_key(command)})[:24]}"


def _idempotency_key(command: CanonicalIngestionRuntimeInput) -> str:
    return canonical_sha256(
        {
            "knowledge_space_id": command.knowledge_space_id,
            "indexable_snapshot_id": command.indexable_snapshot.indexable_snapshot_id,
            "canonical_hash": command.indexable_snapshot.canonical_hash,
            "required_targets": list(command.required_targets),
        }
    )


__all__ = [
    "CanonicalIngestionReceipt",
    "CanonicalIngestionRuntimeInput",
    "CanonicalIngestionSliceRuntime",
    "CanonicalIngestionState",
]
