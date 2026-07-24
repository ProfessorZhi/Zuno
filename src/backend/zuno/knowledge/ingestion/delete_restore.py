from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Literal, Protocol
from urllib.parse import urlparse

from minio.error import S3Error
from pydantic import BaseModel, Field
from sqlalchemy import Engine

from zuno.platform.storage.durable import DurableMinioObjectStore, ObjectCommitTicket
from zuno.platform.storage.object_store import ObjectStoreReceipt


DeleteState = Literal[
    "visibility_revoked",
    "cleanup_requested",
    "physically_deleted",
    "verified",
    "legal_hold",
    "restored",
]


class DeleteLifecycleReceipt(BaseModel):
    delete_ref: str
    snapshot_ref: str
    state: DeleteState
    visibility_ref: str
    object_ref: str | None = None
    restore_point_name: str | None = None
    indexable_snapshot_id: str | None = None
    handoff_outbox_event_id: str | None = None
    parse_job_id: str | None = None
    parse_attempt_id: str | None = None
    fencing_token: int | None = None
    cleanup_ref: str | None = None
    projection_cleanup_ref: str | None = None
    physical_delete_ref: str | None = None
    verification_ref: str | None = None
    cleanup_verified: bool = False
    physical_delete_verified: bool = False
    legal_hold_ref: str | None = None
    restored_authorization: bool = False
    restore_authorization_ref: str | None = None
    duplicate: bool = False
    late_worker_result_rejected: bool = False
    receipt_hash: str
    history: list[str] = Field(default_factory=list)


class RestoreAuthorizationPort(Protocol):
    def authorize_restore(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        restore_authorization_ref: str,
    ) -> "RestoreAuthorizationReceipt":
        ...


class RestoreAuthorizationReceipt(BaseModel):
    tenant_id: str
    delete_ref: str
    restore_authorization_ref: str
    authorized: bool
    reason: str
    security_epoch_ref: str | None = None


class VisibilityRevocationPort(Protocol):
    def revoke_visibility(
        self,
        *,
        tenant_id: str,
        receipt: DeleteLifecycleReceipt,
    ) -> "VisibilityRevocationReceipt":
        ...


class VisibilityRevocationReceipt(BaseModel):
    tenant_id: str
    delete_ref: str
    visibility_ref: str
    revoked: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ReceiptVisibilityRevocationPort:
    def revoke_visibility(
        self,
        *,
        tenant_id: str,
        receipt: DeleteLifecycleReceipt,
    ) -> VisibilityRevocationReceipt:
        return VisibilityRevocationReceipt(
            tenant_id=tenant_id,
            delete_ref=receipt.delete_ref,
            visibility_ref=receipt.visibility_ref,
            revoked=True,
            reason="visibility_revoked_by_delete_lifecycle",
        )


class KnowledgeCleanupPort(Protocol):
    def require_cleanup_confirmed(self, receipt: DeleteLifecycleReceipt) -> "KnowledgeCleanupReceipt":
        ...


class KnowledgeCleanupReceipt(BaseModel):
    delete_ref: str
    cleanup_ref: str | None
    confirmed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ReceiptKnowledgeCleanupPort:
    def require_cleanup_confirmed(self, receipt: DeleteLifecycleReceipt) -> KnowledgeCleanupReceipt:
        if not receipt.cleanup_verified:
            return KnowledgeCleanupReceipt(
                delete_ref=receipt.delete_ref,
                cleanup_ref=receipt.cleanup_ref,
                confirmed=False,
                reason="knowledge_cleanup_confirmation_missing",
            )
        return KnowledgeCleanupReceipt(
            delete_ref=receipt.delete_ref,
            cleanup_ref=receipt.cleanup_ref,
            confirmed=True,
            reason="knowledge_cleanup_confirmed",
        )


class ObjectDeletePort(Protocol):
    def delete_object(
        self,
        *,
        repo: Any,
        receipt: DeleteLifecycleReceipt,
        ticket: ObjectCommitTicket,
    ) -> "ObjectDeletePortReceipt":
        ...


class ObjectDeletePortReceipt(BaseModel):
    delete_ref: str
    physical_delete_ref: str
    deleted: bool
    reason: str


@dataclass(frozen=True, slots=True)
class DurableObjectDeletePort:
    object_store: DurableMinioObjectStore

    def delete_object(
        self,
        *,
        repo: Any,
        receipt: DeleteLifecycleReceipt,
        ticket: ObjectCommitTicket,
    ) -> ObjectDeletePortReceipt:
        from zuno.platform.database.foundation import InfrastructureRepository

        if not receipt.object_ref or not receipt.restore_point_name:
            raise ValueError("delete cleanup requires object_ref and restore_point_name")
        if ticket.staged_receipt.visibility == "deleted":
            return ObjectDeletePortReceipt(
                delete_ref=receipt.delete_ref,
                physical_delete_ref=receipt.object_ref,
                deleted=True,
                reason="object_manifest_already_deleted",
            )
        try:
            self.object_store.store.create_restore_point(
                bucket=ticket.bucket,
                object_name=ticket.committed_object_name,
                restore_point_name=receipt.restore_point_name,
            )
        except S3Error as exc:
            if exc.code not in {"NoSuchKey", "NoSuchObject"}:
                raise
        try:
            deleted = self.object_store.delete_committed(ticket)
            physical_delete_ref = f"s3://{deleted.bucket}/{deleted.object_name}"
        except S3Error as exc:
            if exc.code not in {"NoSuchKey", "NoSuchObject"}:
                raise
            manifest = InfrastructureRepository(repo.connection).object_manifest(
                object_ref=receipt.object_ref
            )
            if manifest is None:
                raise
            InfrastructureRepository(repo.connection).record_object_manifest(
                object_ref=receipt.object_ref,
                content_hash=manifest.content_hash,
                size_bytes=manifest.size_bytes,
                owner=self.object_store.owner,
                visibility="deleted",
            )
            physical_delete_ref = receipt.object_ref
        return ObjectDeletePortReceipt(
            delete_ref=receipt.delete_ref,
            physical_delete_ref=physical_delete_ref,
            deleted=True,
            reason="minio_object_deleted",
        )


class ObjectVerificationPort(Protocol):
    def verify_absent(
        self,
        *,
        receipt: DeleteLifecycleReceipt,
        ticket: ObjectCommitTicket,
    ) -> "ObjectVerificationReceipt":
        ...


class ObjectVerificationReceipt(BaseModel):
    delete_ref: str
    verification_ref: str
    absent: bool
    reason: str


@dataclass(frozen=True, slots=True)
class DurableObjectVerificationPort:
    object_store: DurableMinioObjectStore

    def verify_absent(
        self,
        *,
        receipt: DeleteLifecycleReceipt,
        ticket: ObjectCommitTicket,
    ) -> ObjectVerificationReceipt:
        try:
            self.object_store.store.read_object(
                bucket=ticket.bucket,
                object_name=ticket.committed_object_name,
            )
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchObject"}:
                return ObjectVerificationReceipt(
                    delete_ref=receipt.delete_ref,
                    verification_ref=f"verify_{receipt.delete_ref}",
                    absent=True,
                    reason="minio_absence_verified",
                )
            raise
        raise ValueError("physical delete verification failed: object still exists")


class AuditPort(Protocol):
    def record_delete_event(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> "AuditReceipt":
        ...


class AuditReceipt(BaseModel):
    tenant_id: str
    delete_ref: str
    event_type: str
    recorded: bool


@dataclass(frozen=True, slots=True)
class ReceiptAuditPort:
    def record_delete_event(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> AuditReceipt:
        return AuditReceipt(
            tenant_id=tenant_id,
            delete_ref=delete_ref,
            event_type=event_type,
            recorded=True,
        )


@dataclass(frozen=True, slots=True)
class StaticRestoreAuthorizationPort:
    revoked_refs: frozenset[str] = frozenset()
    security_epoch_ref: str | None = None

    def authorize_restore(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        restore_authorization_ref: str,
    ) -> RestoreAuthorizationReceipt:
        if restore_authorization_ref in self.revoked_refs:
            return RestoreAuthorizationReceipt(
                tenant_id=tenant_id,
                delete_ref=delete_ref,
                restore_authorization_ref=restore_authorization_ref,
                authorized=False,
                reason="restore_authorization_revoked",
                security_epoch_ref=self.security_epoch_ref,
            )
        return RestoreAuthorizationReceipt(
            tenant_id=tenant_id,
            delete_ref=delete_ref,
            restore_authorization_ref=restore_authorization_ref,
            authorized=True,
            reason="restore_authorization_accepted",
            security_epoch_ref=self.security_epoch_ref,
        )


class DeleteRestoreRuntime:
    def request_delete(
        self,
        *,
        snapshot_ref: str,
        visibility_ref: str,
        object_ref: str | None = None,
        restore_point_name: str | None = None,
        legal_hold_ref: str | None = None,
        existing: DeleteLifecycleReceipt | None = None,
    ) -> DeleteLifecycleReceipt:
        if existing is not None:
            return existing.model_copy(update={"duplicate": True})
        delete_ref = f"delete_{_hash({'snapshot_ref': snapshot_ref, 'visibility_ref': visibility_ref})[:24]}"
        state: DeleteState = "legal_hold" if legal_hold_ref else "visibility_revoked"
        history = ["visibility_revoked"]
        if legal_hold_ref:
            history.append("legal_hold")
        return DeleteLifecycleReceipt(
            delete_ref=delete_ref,
            snapshot_ref=snapshot_ref,
            state=state,
            visibility_ref=visibility_ref,
            object_ref=object_ref,
            restore_point_name=restore_point_name,
            cleanup_ref=None if legal_hold_ref else f"cleanup_{delete_ref}",
            legal_hold_ref=legal_hold_ref,
            receipt_hash=_hash(
                {
                    "delete_ref": delete_ref,
                    "snapshot_ref": snapshot_ref,
                    "visibility_ref": visibility_ref,
                    "object_ref": object_ref,
                    "restore_point_name": restore_point_name,
                    "state": state,
                    "legal_hold_ref": legal_hold_ref,
                }
            ),
            history=history,
        )

    def request_delete_during_parse(
        self,
        *,
        parse_job_id: str,
        parse_attempt_id: str,
        fencing_token: int,
        visibility_ref: str,
        snapshot_ref: str | None = None,
        object_ref: str | None = None,
        restore_point_name: str | None = None,
        legal_hold_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        if fencing_token <= 0:
            raise ValueError("fencing_token must be positive")
        requested = self.request_delete(
            snapshot_ref=snapshot_ref or f"parse_inflight:{parse_job_id}",
            visibility_ref=visibility_ref,
            object_ref=object_ref,
            restore_point_name=restore_point_name,
            legal_hold_ref=legal_hold_ref,
        )
        return requested.model_copy(
            update={
                "parse_job_id": parse_job_id,
                "parse_attempt_id": parse_attempt_id,
                "fencing_token": fencing_token,
                "history": [*requested.history, "parse_inflight_delete_requested"],
                "receipt_hash": _hash(
                    {
                        "delete_ref": requested.delete_ref,
                        "parse_job_id": parse_job_id,
                        "parse_attempt_id": parse_attempt_id,
                        "fencing_token": fencing_token,
                        "visibility_ref": visibility_ref,
                        "state": requested.state,
                    }
                ),
            }
        )

    def request_delete_after_snapshot(
        self,
        *,
        indexable_snapshot_id: str,
        handoff_outbox_event_id: str,
        visibility_ref: str,
        projection_cleanup_ref: str,
        object_ref: str | None = None,
        restore_point_name: str | None = None,
        legal_hold_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        requested = self.request_delete(
            snapshot_ref=indexable_snapshot_id,
            visibility_ref=visibility_ref,
            object_ref=object_ref,
            restore_point_name=restore_point_name,
            legal_hold_ref=legal_hold_ref,
        )
        return requested.model_copy(
            update={
                "indexable_snapshot_id": indexable_snapshot_id,
                "handoff_outbox_event_id": handoff_outbox_event_id,
                "projection_cleanup_ref": projection_cleanup_ref,
                "history": [*requested.history, "snapshot_delete_requested"],
                "receipt_hash": _hash(
                    {
                        "delete_ref": requested.delete_ref,
                        "indexable_snapshot_id": indexable_snapshot_id,
                        "handoff_outbox_event_id": handoff_outbox_event_id,
                        "projection_cleanup_ref": projection_cleanup_ref,
                        "visibility_ref": visibility_ref,
                        "object_ref": object_ref,
                        "restore_point_name": restore_point_name,
                        "state": requested.state,
                    }
                ),
            }
        )

    def request_cleanup(self, receipt: DeleteLifecycleReceipt) -> DeleteLifecycleReceipt:
        if receipt.legal_hold_ref:
            return receipt
        return receipt.model_copy(
            update={
                "state": "cleanup_requested",
                "cleanup_ref": receipt.cleanup_ref or f"cleanup_{receipt.delete_ref}",
                "history": [*receipt.history, "cleanup_requested"],
            }
        )

    def confirm_knowledge_cleanup(
        self,
        receipt: DeleteLifecycleReceipt,
        *,
        cleanup_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        expected_cleanup_ref = receipt.cleanup_ref or f"cleanup_{receipt.delete_ref}"
        if cleanup_ref is not None and cleanup_ref != expected_cleanup_ref:
            raise ValueError("knowledge cleanup confirmation does not match delete receipt")
        if receipt.legal_hold_ref:
            return receipt
        if receipt.state == "verified":
            return receipt
        history = list(receipt.history)
        if "cleanup_requested" not in history:
            history.append("cleanup_requested")
        if "knowledge_cleanup_confirmed" not in history:
            history.append("knowledge_cleanup_confirmed")
        return receipt.model_copy(
            update={
                "state": "cleanup_requested",
                "cleanup_ref": expected_cleanup_ref,
                "cleanup_verified": True,
                "history": history,
            }
        )

    def mark_physical_delete(self, receipt: DeleteLifecycleReceipt) -> DeleteLifecycleReceipt:
        if receipt.legal_hold_ref:
            return receipt
        if not receipt.cleanup_verified:
            raise ValueError("physical delete requires knowledge cleanup confirmation")
        physical_delete_ref = f"physical_{receipt.delete_ref}"
        return receipt.model_copy(
            update={
                "state": "physically_deleted",
                "physical_delete_ref": physical_delete_ref,
                "history": [*receipt.history, "physically_deleted"],
            }
        )

    def verify_delete(
        self,
        receipt: DeleteLifecycleReceipt,
        *,
        cleanup_verified: bool = True,
        physical_delete_verified: bool = True,
    ) -> DeleteLifecycleReceipt:
        if receipt.legal_hold_ref:
            return receipt
        if not cleanup_verified:
            raise ValueError("delete verification requires knowledge cleanup confirmation")
        if not physical_delete_verified:
            raise ValueError("delete verification requires physical delete confirmation")
        verification_ref = receipt.verification_ref or f"verify_{receipt.delete_ref}"
        return receipt.model_copy(
            update={
                "state": "verified",
                "verification_ref": verification_ref,
                "cleanup_verified": True,
                "physical_delete_verified": True,
                "history": [*receipt.history, "verified"],
            }
        )

    def reject_late_worker_result(
        self,
        receipt: DeleteLifecycleReceipt,
        *,
        parse_attempt_id: str | None = None,
        fencing_token: int | None = None,
    ) -> DeleteLifecycleReceipt:
        if parse_attempt_id is not None and parse_attempt_id != receipt.parse_attempt_id:
            return _mark_late_worker_rejected(receipt)
        if fencing_token is not None and receipt.fencing_token is not None and fencing_token != receipt.fencing_token:
            return _mark_late_worker_rejected(receipt)
        if receipt.state in {"visibility_revoked", "cleanup_requested", "physically_deleted", "verified", "restored"}:
            return _mark_late_worker_rejected(receipt)
        return receipt

    def restore(
        self,
        receipt: DeleteLifecycleReceipt,
        *,
        restore_authorization_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        if receipt.state == "restored":
            if restore_authorization_ref is not None and receipt.restore_authorization_ref not in {
                None,
                restore_authorization_ref,
            }:
                raise ValueError("conflicting restore authorization")
            return receipt.model_copy(update={"duplicate": True})
        if not restore_authorization_ref:
            raise ValueError("restore requires fresh authorization")
        history = list(receipt.history)
        authorization_marker = f"restore_authorized:{restore_authorization_ref}"
        if authorization_marker not in history:
            history.append(authorization_marker)
        history.append("restored")
        return receipt.model_copy(
            update={
                "state": "restored",
                "restored_authorization": True,
                "restore_authorization_ref": restore_authorization_ref,
                "history": history,
            }
        )


@dataclass(frozen=True, slots=True)
class DeleteLifecycleCommand:
    tenant_id: str
    snapshot_ref: str
    visibility_ref: str
    object_ref: str
    restore_point_name: str
    indexable_snapshot_id: str | None = None
    handoff_outbox_event_id: str | None = None
    projection_cleanup_ref: str | None = None
    legal_hold_ref: str | None = None


@dataclass
class PersistentDeleteRestoreCoordinator:
    engine: Engine
    object_store: DurableMinioObjectStore
    runtime: DeleteRestoreRuntime = field(default_factory=DeleteRestoreRuntime)
    visibility_port: VisibilityRevocationPort = field(default_factory=ReceiptVisibilityRevocationPort)
    knowledge_cleanup_port: KnowledgeCleanupPort = field(default_factory=ReceiptKnowledgeCleanupPort)
    object_delete_port: ObjectDeletePort | None = None
    object_verification_port: ObjectVerificationPort | None = None
    authorization_port: RestoreAuthorizationPort = field(default_factory=StaticRestoreAuthorizationPort)
    audit_port: AuditPort = field(default_factory=ReceiptAuditPort)

    cleanup_topic = "ingestion.delete.cleanup.requested"

    def __post_init__(self) -> None:
        if self.object_delete_port is None:
            self.object_delete_port = DurableObjectDeletePort(self.object_store)
        if self.object_verification_port is None:
            self.object_verification_port = DurableObjectVerificationPort(self.object_store)

    def request_delete_after_snapshot(self, command: DeleteLifecycleCommand) -> DeleteLifecycleReceipt:
        indexable_snapshot_id = command.indexable_snapshot_id or command.snapshot_ref
        projection_cleanup_ref = command.projection_cleanup_ref or f"projection-cleanup:{indexable_snapshot_id}"
        handoff_outbox_event_id = command.handoff_outbox_event_id or f"handoff-outbox:{indexable_snapshot_id}"
        receipt = self.runtime.request_delete_after_snapshot(
            indexable_snapshot_id=indexable_snapshot_id,
            handoff_outbox_event_id=handoff_outbox_event_id,
            visibility_ref=command.visibility_ref,
            projection_cleanup_ref=projection_cleanup_ref,
            object_ref=command.object_ref,
            restore_point_name=command.restore_point_name,
            legal_hold_ref=command.legal_hold_ref,
        )
        from zuno.platform.database.foundation import InfrastructureRepository
        from zuno.platform.database.ingestion.persistence import (
            IngestionPersistenceError,
            IngestionUnitOfWork,
        )

        with IngestionUnitOfWork(self.engine) as repo:
            try:
                existing_row = repo.get_delete_lifecycle(receipt.delete_ref)
            except IngestionPersistenceError as exc:
                if "missing delete lifecycle" not in str(exc):
                    raise
            else:
                if str(existing_row["tenant_id"]) != str(command.tenant_id):
                    raise IngestionPersistenceError(f"conflicting delete lifecycle tenant: {receipt.delete_ref}")
                if existing_row["receipt_hash"] != receipt.receipt_hash:
                    raise IngestionPersistenceError(f"conflicting delete lifecycle: {receipt.delete_ref}")
                return DeleteLifecycleReceipt.model_validate(existing_row).model_copy(update={"duplicate": True})
            visibility = self.visibility_port.revoke_visibility(
                tenant_id=command.tenant_id,
                receipt=receipt,
            )
            if not visibility.revoked:
                raise ValueError(visibility.reason)
            repo.record_delete_lifecycle(tenant_id=command.tenant_id, **receipt.model_dump())
            InfrastructureRepository(repo.connection).enqueue_outbox(
                event_id=f"outbox:{receipt.delete_ref}:cleanup",
                aggregate_id=receipt.delete_ref,
                topic=self.cleanup_topic,
                payload={
                    "delete_ref": receipt.delete_ref,
                    "snapshot_ref": receipt.snapshot_ref,
                    "visibility_ref": receipt.visibility_ref,
                    "object_ref": receipt.object_ref,
                    "restore_point_name": receipt.restore_point_name,
                    "projection_cleanup_ref": receipt.projection_cleanup_ref,
                },
                idempotency_key=f"cleanup:{receipt.delete_ref}",
                tenant_id=command.tenant_id,
                ordering_key=receipt.delete_ref,
            )
            self.audit_port.record_delete_event(
                tenant_id=command.tenant_id,
                delete_ref=receipt.delete_ref,
                event_type="delete_visibility_revoked_cleanup_outbox_committed",
                payload={"visibility_ref": receipt.visibility_ref, "cleanup_ref": receipt.cleanup_ref},
            )
        return receipt

    def execute_cleanup(self, *, tenant_id: str, delete_ref: str) -> DeleteLifecycleReceipt:
        from zuno.platform.database.ingestion.persistence import IngestionUnitOfWork

        with IngestionUnitOfWork(self.engine) as repo:
            current_row = repo.get_delete_lifecycle(delete_ref)
            if str(current_row["tenant_id"]) != str(tenant_id):
                raise ValueError("delete cleanup tenant mismatch")
            current = DeleteLifecycleReceipt.model_validate(current_row)
            if current.legal_hold_ref:
                return current
            if current.state == "verified":
                return current
            cleanup_confirmation = self.knowledge_cleanup_port.require_cleanup_confirmed(current)
            if not cleanup_confirmation.confirmed:
                raise ValueError("physical delete requires knowledge cleanup confirmation")
            if not current.object_ref or not current.restore_point_name:
                raise ValueError("delete cleanup requires object_ref and restore_point_name")
            ticket = self._ticket(repo, current.object_ref)
            cleanup = self.runtime.confirm_knowledge_cleanup(current)
            delete_result = self._object_delete_port().delete_object(
                repo=repo,
                receipt=current,
                ticket=ticket,
            )
            verification_result = self._object_verification_port().verify_absent(
                receipt=current,
                ticket=ticket,
            )
            if not verification_result.absent:
                raise ValueError(verification_result.reason)
            verified = self.runtime.verify_delete(
                self.runtime.mark_physical_delete(cleanup).model_copy(
                    update={
                        "physical_delete_ref": delete_result.physical_delete_ref,
                        "verification_ref": verification_result.verification_ref,
                    }
                ),
                cleanup_verified=True,
                physical_delete_verified=True,
            )
            repo.reconcile_delete_lifecycle(verified)
            self.audit_port.record_delete_event(
                tenant_id=tenant_id,
                delete_ref=delete_ref,
                event_type="delete_physical_absence_verified",
                payload={"physical_delete_ref": verified.physical_delete_ref},
            )
            return verified

    def confirm_knowledge_cleanup(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        cleanup_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        from zuno.platform.database.ingestion.persistence import IngestionUnitOfWork

        with IngestionUnitOfWork(self.engine) as repo:
            current_row = repo.get_delete_lifecycle(delete_ref)
            if str(current_row["tenant_id"]) != str(tenant_id):
                raise ValueError("delete cleanup confirmation tenant mismatch")
            current = DeleteLifecycleReceipt.model_validate(current_row)
            confirmed = self.runtime.confirm_knowledge_cleanup(current, cleanup_ref=cleanup_ref)
            repo.reconcile_delete_lifecycle(confirmed)
            return confirmed

    def restore_deleted(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        restore_authorization_ref: str | None = None,
    ) -> DeleteLifecycleReceipt:
        from zuno.platform.database.ingestion.persistence import IngestionUnitOfWork

        with IngestionUnitOfWork(self.engine) as repo:
            current_row = repo.get_delete_lifecycle(delete_ref)
            if str(current_row["tenant_id"]) != str(tenant_id):
                raise ValueError("delete restore tenant mismatch")
            current = DeleteLifecycleReceipt.model_validate(current_row)
            if current.state == "restored":
                if restore_authorization_ref is not None:
                    self._authorize_restore(
                        tenant_id=tenant_id,
                        delete_ref=delete_ref,
                        restore_authorization_ref=restore_authorization_ref,
                    )
                restored = self.runtime.restore(
                    current,
                    restore_authorization_ref=restore_authorization_ref,
                )
                repo.reconcile_delete_lifecycle(restored)
                return restored
            if not restore_authorization_ref:
                raise ValueError("restore requires fresh authorization")
            self._authorize_restore(
                tenant_id=tenant_id,
                delete_ref=delete_ref,
                restore_authorization_ref=restore_authorization_ref,
            )
            if not current.object_ref or not current.restore_point_name:
                raise ValueError("restore requires object_ref and restore_point_name")
            ticket = self._ticket(repo, current.object_ref)
            self.object_store.restore(ticket, restore_point_name=current.restore_point_name)
            restored = self.runtime.restore(
                current,
                restore_authorization_ref=restore_authorization_ref,
            )
            repo.reconcile_delete_lifecycle(restored)
            return restored

    def reject_late_worker_result(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        parse_attempt_id: str | None = None,
        fencing_token: int | None = None,
    ) -> DeleteLifecycleReceipt:
        from zuno.platform.database.ingestion.persistence import IngestionUnitOfWork

        with IngestionUnitOfWork(self.engine) as repo:
            current_row = repo.get_delete_lifecycle(delete_ref)
            if str(current_row["tenant_id"]) != str(tenant_id):
                raise ValueError("late worker rejection tenant mismatch")
            current = DeleteLifecycleReceipt.model_validate(current_row)
            rejected = self.runtime.reject_late_worker_result(
                current,
                parse_attempt_id=parse_attempt_id,
                fencing_token=fencing_token,
            )
            repo.reconcile_delete_lifecycle(rejected)
            return rejected

    def _ticket(self, repo: Any, object_ref: str) -> ObjectCommitTicket:
        from zuno.platform.database.foundation import InfrastructureRepository

        bucket, object_name = _parse_s3_object_ref(object_ref)
        manifest = InfrastructureRepository(repo.connection).object_manifest(object_ref=object_ref)
        if manifest is None:
            raise ValueError(f"missing object manifest: {object_ref}")
        return ObjectCommitTicket(
            bucket=bucket,
            committed_object_name=object_name,
            staged_receipt=ObjectStoreReceipt(
                bucket=bucket,
                object_name=object_name,
                content_hash=manifest.content_hash,
                size_bytes=manifest.size_bytes,
                visibility=manifest.visibility,
            ),
        )

    def _object_delete_port(self) -> ObjectDeletePort:
        if self.object_delete_port is None:
            self.object_delete_port = DurableObjectDeletePort(self.object_store)
        return self.object_delete_port

    def _object_verification_port(self) -> ObjectVerificationPort:
        if self.object_verification_port is None:
            self.object_verification_port = DurableObjectVerificationPort(self.object_store)
        return self.object_verification_port

    def _authorize_restore(
        self,
        *,
        tenant_id: str,
        delete_ref: str,
        restore_authorization_ref: str,
    ) -> RestoreAuthorizationReceipt:
        authorization = self.authorization_port.authorize_restore(
            tenant_id=tenant_id,
            delete_ref=delete_ref,
            restore_authorization_ref=restore_authorization_ref,
        )
        if (
            str(authorization.tenant_id) != str(tenant_id)
            or str(authorization.delete_ref) != str(delete_ref)
            or authorization.restore_authorization_ref != restore_authorization_ref
        ):
            raise ValueError("restore authorization receipt mismatch")
        if not authorization.authorized:
            raise ValueError(authorization.reason)
        return authorization


def _parse_s3_object_ref(object_ref: str) -> tuple[str, str]:
    parsed = urlparse(object_ref)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.strip("/"):
        raise ValueError("object_ref must be an s3://bucket/object reference")
    return parsed.netloc, parsed.path.lstrip("/")


def _mark_late_worker_rejected(receipt: DeleteLifecycleReceipt) -> DeleteLifecycleReceipt:
    history = list(receipt.history)
    if "late_worker_result_rejected" not in history:
        history.append("late_worker_result_rejected")
    return receipt.model_copy(
        update={
            "late_worker_result_rejected": True,
            "history": history,
        }
    )


def _hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "AuditPort",
    "AuditReceipt",
    "DeleteLifecycleCommand",
    "DeleteLifecycleReceipt",
    "DeleteRestoreRuntime",
    "DurableObjectDeletePort",
    "DurableObjectVerificationPort",
    "KnowledgeCleanupPort",
    "KnowledgeCleanupReceipt",
    "ObjectDeletePort",
    "ObjectDeletePortReceipt",
    "ObjectVerificationPort",
    "ObjectVerificationReceipt",
    "PersistentDeleteRestoreCoordinator",
    "ReceiptAuditPort",
    "ReceiptKnowledgeCleanupPort",
    "ReceiptVisibilityRevocationPort",
    "RestoreAuthorizationPort",
    "RestoreAuthorizationReceipt",
    "StaticRestoreAuthorizationPort",
    "VisibilityRevocationPort",
    "VisibilityRevocationReceipt",
]
