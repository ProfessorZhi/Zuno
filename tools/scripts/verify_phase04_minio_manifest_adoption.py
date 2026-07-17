from __future__ import annotations

import hashlib
from uuid import uuid4

from sqlalchemy import text
from sqlmodel import select

from zuno.database.models.knowledge_file import KnowledgeFileTable, Status
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.session import domain_uow
from zuno.platform.storage import (
    DurableMinioObjectStore,
    MinioObjectStore,
    ObjectHashMismatchError,
    ObjectNotCommittedError,
    SessionObjectManifest,
)
from zuno.platform.storage.object_store import ObjectStoreReceipt

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
OWNER = "Input / Document Ingestion"


class _CrashAfterPhysicalCommit(DurableMinioObjectStore):
    def _after_physical_commit(self, receipt: ObjectStoreReceipt) -> None:
        raise RuntimeError("simulated crash after physical object commit")


def _manifest_row(engine, object_ref: str):
    with engine.connect() as connection:
        return connection.execute(
            text("""
                SELECT owner, content_hash, size_bytes, visibility, conflict_hash
                FROM infra_object_manifests
                WHERE object_ref = :object_ref
                """),
            {"object_ref": object_ref},
        ).one_or_none()


def verify_phase04_minio_manifest_adoption() -> list[str]:
    errors: list[str] = []
    marker = uuid4().hex
    tenant_id = f"tenant-minio-manifest-{marker}"
    workspace_id = f"workspace-minio-manifest-{marker}"
    source_id = f"source-minio-manifest-{marker}"
    bucket = f"zuno-phase04-manifest-{marker}"
    object_name = f"workspaces/{workspace_id}/sources/{source_id}/source.txt"
    content = f"durable-minio-manifest-{marker}".encode()
    content_hash = hashlib.sha256(content).hexdigest()
    restore_point_name = f"_restore/{marker}/source.txt"
    engine = create_foundation_engine(DATABASE_URL)
    store = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )
    durable = DurableMinioObjectStore(store=store, engine=engine, owner=OWNER)
    ticket = durable.stage(
        bucket=bucket,
        committed_object_name=object_name,
        content=content,
    )
    try:
        try:
            with domain_uow(tenant_id=tenant_id) as session:
                session.add(
                    KnowledgeFileTable(
                        id=source_id,
                        file_name="source.txt",
                        knowledge_id=workspace_id,
                        status=Status.process,
                        user_id=f"principal:{marker}",
                        oss_url=ticket.object_ref,
                        file_size=len(content),
                    )
                )
                SessionObjectManifest(session).record_staged(
                    ticket=ticket,
                    owner=OWNER,
                )
                session.flush()
                raise RuntimeError("simulated crash before domain transaction commit")
        except RuntimeError as exc:
            if "simulated crash before domain" not in str(exc):
                raise

        with engine.connect() as connection:
            rolled_back_domain = int(
                connection.execute(
                    text("SELECT count(*) FROM knowledge_file WHERE id = :source_id"),
                    {"source_id": source_id},
                ).scalar_one()
            )
        if (
            rolled_back_domain != 0
            or _manifest_row(engine, ticket.object_ref) is not None
        ):
            errors.append(
                "domain source and staged manifest did not roll back atomically"
            )

        with domain_uow(tenant_id=tenant_id) as session:
            session.add(
                KnowledgeFileTable(
                    id=source_id,
                    file_name="source.txt",
                    knowledge_id=workspace_id,
                    status=Status.process,
                    user_id=f"principal:{marker}",
                    oss_url=ticket.object_ref,
                    file_size=len(content),
                )
            )
            staged_manifest = SessionObjectManifest(session).record_staged(
                ticket=ticket,
                owner=OWNER,
            )
        if (
            staged_manifest.content_hash != content_hash
            or staged_manifest.size_bytes != len(content)
            or staged_manifest.visibility != "staged"
        ):
            errors.append("PostgreSQL staged manifest did not preserve MinIO receipt")

        try:
            durable.read_committed(ticket)
            errors.append(
                "staged object was readable through the committed-object gate"
            )
        except ObjectNotCommittedError:
            pass

        crashing = _CrashAfterPhysicalCommit(store=store, engine=engine, owner=OWNER)
        try:
            crashing.commit(ticket)
            errors.append("post-MinIO pre-database crash simulation did not raise")
        except RuntimeError as exc:
            if "simulated crash after physical object commit" not in str(exc):
                raise

        row_after_crash = _manifest_row(engine, ticket.object_ref)
        if row_after_crash is None or row_after_crash.visibility != "staged":
            errors.append("physical commit crash incorrectly advanced the DB manifest")
        if store.read_object(bucket=bucket, object_name=object_name) != content:
            errors.append("physical object was not committed before crash simulation")
        try:
            durable.read_committed(ticket)
            errors.append("physical object bypassed the staged PostgreSQL manifest")
        except ObjectNotCommittedError:
            pass

        try:
            with domain_uow(tenant_id=tenant_id) as session:
                source = session.exec(
                    select(KnowledgeFileTable).where(KnowledgeFileTable.id == source_id)
                ).one()
                source.status = Status.success
                SessionObjectManifest(session).record_committed(
                    ticket=ticket,
                    owner=OWNER,
                )
                session.flush()
                raise RuntimeError("simulated crash before domain success commit")
        except RuntimeError as exc:
            if "simulated crash before domain success" not in str(exc):
                raise

        row_after_domain_crash = _manifest_row(engine, ticket.object_ref)
        with domain_uow(tenant_id=tenant_id) as session:
            source_after_crash = session.exec(
                select(KnowledgeFileTable).where(KnowledgeFileTable.id == source_id)
            ).one()
            if (
                source_after_crash.status != Status.process
                or row_after_domain_crash is None
                or row_after_domain_crash.visibility != "staged"
            ):
                errors.append(
                    "domain success and visible manifest did not roll back together"
                )

        reconciled = durable.reconcile_committed(ticket)
        if reconciled.content_hash != content_hash:
            errors.append("reconciler did not recover the canonical content hash")
        with domain_uow(tenant_id=tenant_id) as session:
            source_after_reconcile = session.exec(
                select(KnowledgeFileTable).where(KnowledgeFileTable.id == source_id)
            ).one()
            if source_after_reconcile.status != Status.process:
                errors.append(
                    "object receipt was incorrectly interpreted as domain success"
                )
            source_after_reconcile.status = Status.success
            SessionObjectManifest(session).record_committed(
                ticket=ticket,
                owner=OWNER,
            )

        if durable.read_committed(ticket) != content:
            errors.append("committed-object gate did not return verified bytes")

        restore_point = store.create_restore_point(
            bucket=bucket,
            object_name=object_name,
            restore_point_name=restore_point_name,
        )
        deleted = durable.delete_committed(ticket)
        if deleted.content_hash != content_hash:
            errors.append("logical-first delete returned the wrong content hash")
        try:
            durable.read_committed(ticket)
            errors.append("deleted manifest remained readable")
        except ObjectNotCommittedError:
            pass

        restored = durable.restore(
            ticket,
            restore_point_name=restore_point.object_name,
        )
        if (
            restored.content_hash != content_hash
            or durable.read_committed(ticket) != content
        ):
            errors.append("restored object did not reconcile to the original manifest")

        tampered_content = content + b"-tampered"
        tampered = store.stage_object(
            bucket=bucket,
            object_name=object_name,
            content=tampered_content,
        )
        store.commit_object(
            bucket=bucket,
            staged_object_name=tampered.object_name,
            committed_object_name=object_name,
            expected_hash=tampered.content_hash,
        )
        try:
            durable.read_committed(ticket)
            errors.append("tampered visible object passed manifest verification")
        except ObjectHashMismatchError:
            pass
        quarantined = _manifest_row(engine, ticket.object_ref)
        if quarantined is None or quarantined.visibility != "quarantined":
            errors.append("object hash mismatch was not durably quarantined")
    finally:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM knowledge_file WHERE id = :source_id"),
                {"source_id": source_id},
            )
            connection.execute(
                text(
                    "DELETE FROM infra_object_manifests WHERE object_ref = :object_ref"
                ),
                {"object_ref": ticket.object_ref},
            )
        store.remove_bucket_tree(bucket)
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_minio_manifest_adoption()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 MinIO manifest adoption verification failed.")
        return 1
    print("PHASE04 MinIO manifest adoption verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
