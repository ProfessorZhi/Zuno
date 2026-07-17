from __future__ import annotations

import hashlib
from dataclasses import dataclass

from sqlalchemy import Engine
from sqlmodel import Session

from zuno.platform.database.foundation import (
    InfrastructureConflictError,
    InfrastructureRepository,
    InfrastructureUnitOfWork,
    ObjectManifestRecord,
)
from zuno.platform.storage.object_store import (
    MinioObjectStore,
    ObjectHashMismatchError,
    ObjectStoreReceipt,
)


class ObjectNotCommittedError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ObjectCommitTicket:
    bucket: str
    committed_object_name: str
    staged_receipt: ObjectStoreReceipt

    @property
    def object_ref(self) -> str:
        return f"s3://{self.bucket}/{self.committed_object_name}"


class SessionObjectManifest:
    def __init__(self, session: Session) -> None:
        self.repository = InfrastructureRepository(session.connection())

    def record_staged(
        self,
        *,
        ticket: ObjectCommitTicket,
        owner: str,
    ) -> ObjectManifestRecord:
        return self._record(ticket=ticket, owner=owner, visibility="staged")

    def record_committed(
        self,
        *,
        ticket: ObjectCommitTicket,
        owner: str,
    ) -> ObjectManifestRecord:
        return self._record(ticket=ticket, owner=owner, visibility="visible")

    def _record(
        self,
        *,
        ticket: ObjectCommitTicket,
        owner: str,
        visibility: str,
    ) -> ObjectManifestRecord:
        return self.repository.record_object_manifest(
            object_ref=ticket.object_ref,
            content_hash=ticket.staged_receipt.content_hash,
            size_bytes=ticket.staged_receipt.size_bytes,
            owner=owner,
            visibility=visibility,
        )


class DurableMinioObjectStore:
    def __init__(
        self,
        *,
        store: MinioObjectStore,
        engine: Engine,
        owner: str,
    ) -> None:
        if not owner.strip():
            raise ValueError("object manifest owner must not be empty")
        self.store = store
        self.engine = engine
        self.owner = owner

    def stage(
        self,
        *,
        bucket: str,
        committed_object_name: str,
        content: bytes,
    ) -> ObjectCommitTicket:
        staged = self.store.stage_object(
            bucket=bucket,
            object_name=committed_object_name,
            content=content,
        )
        return ObjectCommitTicket(
            bucket=bucket,
            committed_object_name=committed_object_name,
            staged_receipt=staged,
        )

    def commit(self, ticket: ObjectCommitTicket) -> ObjectStoreReceipt:
        receipt = self.store.commit_object(
            bucket=ticket.bucket,
            staged_object_name=ticket.staged_receipt.object_name,
            committed_object_name=ticket.committed_object_name,
            expected_hash=ticket.staged_receipt.content_hash,
        )
        self._after_physical_commit(receipt)
        self._record_receipt(receipt=receipt, visibility="visible")
        return receipt

    def reconcile_committed(self, ticket: ObjectCommitTicket) -> ObjectStoreReceipt:
        manifest = self._manifest(ticket.object_ref)
        if manifest is None:
            raise ObjectNotCommittedError("object has no authoritative manifest")
        content = self.store.read_object(
            bucket=ticket.bucket,
            object_name=ticket.committed_object_name,
        )
        actual_hash = hashlib.sha256(content).hexdigest()
        if (
            actual_hash != manifest.content_hash
            or len(content) != manifest.size_bytes
            or manifest.owner != self.owner
        ):
            self._quarantine(
                object_ref=ticket.object_ref,
                content_hash=actual_hash,
                size_bytes=len(content),
            )
            raise ObjectHashMismatchError(
                "committed object does not match its PostgreSQL manifest"
            )
        receipt = ObjectStoreReceipt(
            bucket=ticket.bucket,
            object_name=ticket.committed_object_name,
            content_hash=actual_hash,
            size_bytes=len(content),
            visibility="visible",
        )
        self._record_receipt(receipt=receipt, visibility="visible")
        return receipt

    def read_committed(self, ticket: ObjectCommitTicket) -> bytes:
        manifest = self._manifest(ticket.object_ref)
        if manifest is None or manifest.visibility not in {"visible", "restored"}:
            raise ObjectNotCommittedError(
                "object manifest is not committed and visible"
            )
        content = self.store.read_object(
            bucket=ticket.bucket,
            object_name=ticket.committed_object_name,
        )
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != manifest.content_hash or len(content) != manifest.size_bytes:
            self._quarantine(
                object_ref=ticket.object_ref,
                content_hash=actual_hash,
                size_bytes=len(content),
            )
            raise ObjectHashMismatchError(
                "visible object does not match its PostgreSQL manifest"
            )
        return content

    def delete_committed(self, ticket: ObjectCommitTicket) -> ObjectStoreReceipt:
        manifest = self._required_committed_manifest(ticket.object_ref)
        self._record_manifest(
            object_ref=ticket.object_ref,
            content_hash=manifest.content_hash,
            size_bytes=manifest.size_bytes,
            visibility="deleted",
        )
        return self.store.delete_object(
            bucket=ticket.bucket,
            object_name=ticket.committed_object_name,
        )

    def restore(
        self,
        ticket: ObjectCommitTicket,
        *,
        restore_point_name: str,
    ) -> ObjectStoreReceipt:
        receipt = self.store.restore_object(
            bucket=ticket.bucket,
            restore_point_name=restore_point_name,
            restored_object_name=ticket.committed_object_name,
        )
        self._record_receipt(receipt=receipt, visibility="restored")
        return receipt

    def _required_committed_manifest(self, object_ref: str) -> ObjectManifestRecord:
        manifest = self._manifest(object_ref)
        if manifest is None or manifest.visibility not in {"visible", "restored"}:
            raise ObjectNotCommittedError(
                "object manifest is not committed and visible"
            )
        return manifest

    def _manifest(self, object_ref: str) -> ObjectManifestRecord | None:
        with InfrastructureUnitOfWork(self.engine) as repository:
            return repository.object_manifest(object_ref=object_ref)

    def _record_receipt(
        self,
        *,
        receipt: ObjectStoreReceipt,
        visibility: str,
    ) -> ObjectManifestRecord:
        return self._record_manifest(
            object_ref=f"s3://{receipt.bucket}/{receipt.object_name}",
            content_hash=receipt.content_hash,
            size_bytes=receipt.size_bytes,
            visibility=visibility,
        )

    def _record_manifest(
        self,
        *,
        object_ref: str,
        content_hash: str,
        size_bytes: int,
        visibility: str,
    ) -> ObjectManifestRecord:
        with InfrastructureUnitOfWork(self.engine) as repository:
            return repository.record_object_manifest(
                object_ref=object_ref,
                content_hash=content_hash,
                size_bytes=size_bytes,
                owner=self.owner,
                visibility=visibility,
            )

    def _quarantine(
        self,
        *,
        object_ref: str,
        content_hash: str,
        size_bytes: int,
    ) -> None:
        with InfrastructureUnitOfWork(self.engine) as repository:
            try:
                repository.record_object_manifest(
                    object_ref=object_ref,
                    content_hash=content_hash,
                    size_bytes=size_bytes,
                    owner=self.owner,
                    visibility="visible",
                )
            except InfrastructureConflictError:
                pass

    def _after_physical_commit(self, receipt: ObjectStoreReceipt) -> None:
        """Extension point used by fault tests after MinIO commit and before DB update."""


__all__ = [
    "DurableMinioObjectStore",
    "ObjectCommitTicket",
    "ObjectNotCommittedError",
    "SessionObjectManifest",
]
