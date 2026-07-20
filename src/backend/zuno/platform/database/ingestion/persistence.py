from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import Engine, bindparam, text
from sqlalchemy.engine import Connection

from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_json, canonical_sha256
from zuno.platform.database.foundation import InfrastructureRepository, InboxReceipt


class IngestionPersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class IngestionReceipt:
    ref: str
    tenant_id: str
    status: str
    payload_hash: str | None = None


class IngestionUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._active = False

    def __enter__(self) -> IngestionRepository:
        if self._active:
            raise RuntimeError("IngestionUnitOfWork cannot be nested")
        self._active = True
        self._context = self.engine.begin()
        try:
            self.connection = self._context.__enter__()
            return IngestionRepository(self.connection)
        except BaseException:
            self._active = False
            raise

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            self._context.__exit__(exc_type, exc, tb)
        finally:
            self._active = False


class IngestionRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def record_source_object(
        self,
        *,
        source_object_id: str,
        tenant_id: str,
        workspace_id: str,
        filename: str,
        mime_type: str,
        storage_uri: str,
        object_manifest_ref: str,
        source_sha256: str,
        size_bytes: int,
        classification_ref: str,
        security_epoch_ref: str,
        source_kind: str = "upload",
        declared_format: str = "unknown",
        status: str = "committed",
    ) -> IngestionReceipt:
        self._require_hash(source_sha256, "source_sha256")
        if size_bytes < 0:
            raise IngestionPersistenceError("source object size_bytes must be non-negative")
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_source_objects(
                    source_object_id, tenant_id, workspace_id, source_kind, filename,
                    mime_type, declared_format, storage_uri, object_manifest_ref,
                    source_sha256, size_bytes, classification_ref, security_epoch_ref, status
                ) VALUES (
                    :source_object_id, :tenant_id, :workspace_id, :source_kind, :filename,
                    :mime_type, :declared_format, :storage_uri, :object_manifest_ref,
                    :source_sha256, :size_bytes, :classification_ref, :security_epoch_ref, :status
                )
                """
            ),
            {
                "source_object_id": source_object_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "source_kind": source_kind,
                "filename": filename,
                "mime_type": mime_type,
                "declared_format": declared_format,
                "storage_uri": storage_uri,
                "object_manifest_ref": object_manifest_ref,
                "source_sha256": source_sha256,
                "size_bytes": size_bytes,
                "classification_ref": classification_ref,
                "security_epoch_ref": security_epoch_ref,
                "status": status,
            },
        )
        return IngestionReceipt(source_object_id, tenant_id, status, source_sha256)

    def record_document_version(
        self,
        *,
        document_version_id: str,
        tenant_id: str,
        workspace_id: str,
        source_object_id: str,
        version_no: int,
        content_hash: str,
        metadata: dict[str, Any],
        immutability_ref: str,
        status: str = "active",
    ) -> IngestionReceipt:
        self._require_hash(content_hash, "content_hash")
        if version_no <= 0:
            raise IngestionPersistenceError("document version_no must be positive")
        metadata_hash = canonical_sha256(metadata)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_document_versions(
                    document_version_id, tenant_id, workspace_id, source_object_id,
                    version_no, content_hash, metadata_hash, immutability_ref, status
                ) VALUES (
                    :document_version_id, :tenant_id, :workspace_id, :source_object_id,
                    :version_no, :content_hash, :metadata_hash, :immutability_ref, :status
                )
                """
            ),
            {
                "document_version_id": document_version_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "source_object_id": source_object_id,
                "version_no": version_no,
                "content_hash": content_hash,
                "metadata_hash": metadata_hash,
                "immutability_ref": immutability_ref,
                "status": status,
            },
        )
        return IngestionReceipt(document_version_id, tenant_id, status, metadata_hash)

    def record_parse_plan(
        self,
        *,
        parse_plan_id: str,
        tenant_id: str,
        document_version_id: str,
        parser_route: dict[str, Any],
        parser_policy_ref: str,
        parser_bundle: dict[str, Any],
        quality_policy_ref: str,
        security_decision_ref: str,
        status: str = "planned",
    ) -> IngestionReceipt:
        parser_bundle_hash = canonical_sha256(parser_bundle)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_plans(
                    parse_plan_id, tenant_id, document_version_id, parser_route,
                    parser_policy_ref, parser_bundle_hash, quality_policy_ref,
                    security_decision_ref, status
                ) VALUES (
                    :parse_plan_id, :tenant_id, :document_version_id, CAST(:parser_route AS jsonb),
                    :parser_policy_ref, :parser_bundle_hash, :quality_policy_ref,
                    :security_decision_ref, :status
                )
                """
            ),
            {
                "parse_plan_id": parse_plan_id,
                "tenant_id": tenant_id,
                "document_version_id": document_version_id,
                "parser_route": canonical_json(parser_route),
                "parser_policy_ref": parser_policy_ref,
                "parser_bundle_hash": parser_bundle_hash,
                "quality_policy_ref": quality_policy_ref,
                "security_decision_ref": security_decision_ref,
                "status": status,
            },
        )
        return IngestionReceipt(parse_plan_id, tenant_id, status, parser_bundle_hash)

    def record_parse_job(
        self,
        *,
        parse_job_id: str,
        tenant_id: str,
        parse_plan_id: str,
        document_version_id: str,
        idempotency_key: str,
        priority_class: str = "normal",
        status: str = "queued",
    ) -> IngestionReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_jobs(
                    parse_job_id, tenant_id, parse_plan_id, document_version_id,
                    idempotency_key, priority_class, status
                ) VALUES (
                    :parse_job_id, :tenant_id, :parse_plan_id, :document_version_id,
                    :idempotency_key, :priority_class, :status
                )
                """
            ),
            {
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "parse_plan_id": parse_plan_id,
                "document_version_id": document_version_id,
                "idempotency_key": idempotency_key,
                "priority_class": priority_class,
                "status": status,
            },
        )
        return IngestionReceipt(parse_job_id, tenant_id, status)

    def record_parse_attempt(
        self,
        *,
        parse_attempt_id: str,
        tenant_id: str,
        parse_job_id: str,
        attempt_no: int,
        worker_id: str,
        lease_ref: str,
        fencing_token: int,
        workspace_id: str | None = None,
        source_object_id: str | None = None,
        document_version_id: str | None = None,
        parse_plan_id: str | None = None,
        idempotency_key: str | None = None,
        security_epoch_ref: str | None = None,
        lease_expires_at: datetime | None = None,
        status: str = "created",
    ) -> IngestionReceipt:
        if attempt_no <= 0 or fencing_token <= 0:
            raise IngestionPersistenceError("parse attempt_no and fencing_token must be positive")
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_attempts(
                    parse_attempt_id, tenant_id, parse_job_id, attempt_no,
                    worker_id, lease_ref, fencing_token, workspace_id, source_object_id,
                    document_version_id, parse_plan_id, idempotency_key, security_epoch_ref,
                    lease_expires_at, heartbeat_at, status
                ) VALUES (
                    :parse_attempt_id, :tenant_id, :parse_job_id, :attempt_no,
                    :worker_id, :lease_ref, :fencing_token, :workspace_id, :source_object_id,
                    :document_version_id, :parse_plan_id, :idempotency_key, :security_epoch_ref,
                    :lease_expires_at, now(), :status
                )
                """
            ),
            {
                "parse_attempt_id": parse_attempt_id,
                "tenant_id": tenant_id,
                "parse_job_id": parse_job_id,
                "attempt_no": attempt_no,
                "worker_id": worker_id,
                "lease_ref": lease_ref,
                "fencing_token": fencing_token,
                "workspace_id": workspace_id,
                "source_object_id": source_object_id,
                "document_version_id": document_version_id,
                "parse_plan_id": parse_plan_id,
                "idempotency_key": idempotency_key,
                "security_epoch_ref": security_epoch_ref,
                "lease_expires_at": lease_expires_at,
                "status": status,
            },
        )
        return IngestionReceipt(parse_attempt_id, tenant_id, status)

    def enqueue_parse_requested(
        self,
        *,
        envelope: CrossModuleEnvelopeV1,
        topic: str = "ingestion.parse.requested",
    ) -> IngestionReceipt:
        event_id = InfrastructureRepository(self.connection).enqueue_outbox(
            event_id=envelope.message_id,
            aggregate_id=envelope.aggregate_id or envelope.message_id,
            topic=topic,
            payload=envelope.model_dump(mode="json"),
            idempotency_key=envelope.idempotency_key or envelope.message_id,
            tenant_id=envelope.tenant_id,
            ordering_key=envelope.aggregate_id,
        )
        return IngestionReceipt(event_id, envelope.tenant_id, "pending", envelope.payload_hash)

    def record_worker_inbox(
        self,
        *,
        consumer: str,
        message_id: str,
        payload: dict[str, Any],
        tenant_id: str,
    ) -> InboxReceipt:
        return InfrastructureRepository(self.connection).record_inbox_receipt(
            consumer=consumer,
            message_id=message_id,
            payload=payload,
            tenant_id=tenant_id,
        )

    def load_parse_job_context(self, *, parse_job_id: str, tenant_id: str) -> dict[str, Any]:
        row = self.connection.execute(
            text(
                """
                SELECT
                    job.parse_job_id, job.tenant_id, job.parse_plan_id, job.document_version_id,
                    job.idempotency_key, job.status, job.attempt_count,
                    plan.quality_policy_ref, plan.security_decision_ref,
                    document.workspace_id, document.source_object_id, document.content_hash,
                    source.filename, source.mime_type, source.storage_uri, source.object_manifest_ref,
                    source.source_sha256, source.size_bytes, source.classification_ref,
                    source.security_epoch_ref, source.status AS source_status
                FROM ingestion_parse_jobs AS job
                JOIN ingestion_parse_plans AS plan ON plan.parse_plan_id = job.parse_plan_id
                JOIN ingestion_document_versions AS document ON document.document_version_id = job.document_version_id
                JOIN ingestion_source_objects AS source ON source.source_object_id = document.source_object_id
                WHERE job.parse_job_id = :parse_job_id AND job.tenant_id = :tenant_id
                FOR UPDATE OF job
                """
            ),
            {"parse_job_id": parse_job_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row is None:
            raise IngestionPersistenceError(f"missing parse job: {parse_job_id}")
        return dict(row)

    def load_parse_job_replay_receipt(self, *, parse_job_id: str, tenant_id: str) -> dict[str, Any]:
        row = self.connection.execute(
            text(
                """
                SELECT
                    job.status AS job_status,
                    latest_attempt.parse_attempt_id,
                    latest_attempt.status AS attempt_status,
                    indexable.indexable_snapshot_id,
                    indexable.handoff_idempotency_key,
                    outbox.outbox_event_id,
                    outbox.idempotency_key AS outbox_idempotency_key,
                    dead_letter.dead_letter_id
                FROM ingestion_parse_jobs AS job
                LEFT JOIN LATERAL (
                    SELECT parse_attempt_id, status
                    FROM ingestion_parse_attempts
                    WHERE parse_job_id = job.parse_job_id
                    ORDER BY attempt_no DESC
                    LIMIT 1
                ) AS latest_attempt ON true
                LEFT JOIN ingestion_parse_snapshots AS snapshot
                  ON snapshot.parse_attempt_id = latest_attempt.parse_attempt_id
                LEFT JOIN ingestion_indexable_document_snapshots AS indexable
                  ON indexable.parse_snapshot_id = snapshot.parse_snapshot_id
                LEFT JOIN ingestion_outbox_events AS outbox
                  ON outbox.aggregate_ref = indexable.indexable_snapshot_id
                 AND outbox.event_type = 'ingestion.indexable_snapshot.ready'
                LEFT JOIN ingestion_dead_letters AS dead_letter
                  ON dead_letter.parse_attempt_id = latest_attempt.parse_attempt_id
                WHERE job.parse_job_id = :parse_job_id
                  AND job.tenant_id = :tenant_id
                """
            ),
            {"parse_job_id": parse_job_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row is None:
            raise IngestionPersistenceError(f"missing parse job replay receipt: {parse_job_id}")
        return dict(row)

    def load_snapshot_handoff_replay_receipt(
        self,
        *,
        tenant_id: str,
        handoff_idempotency_key: str,
    ) -> dict[str, Any]:
        row = self.connection.execute(
            text(
                """
                SELECT
                    indexable.indexable_snapshot_id,
                    indexable.parse_snapshot_id,
                    indexable.document_version_id,
                    indexable.quality_decision_id,
                    indexable.snapshot_hash,
                    indexable.handoff_envelope_hash,
                    indexable.visibility_ref,
                    indexable.handoff_idempotency_key,
                    indexable.knowledge_handoff_status,
                    outbox.outbox_event_id,
                    outbox.publish_status AS outbox_publish_status,
                    outbox.payload_hash AS outbox_payload_hash
                FROM ingestion_indexable_document_snapshots AS indexable
                LEFT JOIN ingestion_outbox_events AS outbox
                  ON outbox.tenant_id = indexable.tenant_id
                 AND outbox.event_type = 'ingestion.indexable_snapshot.ready'
                 AND outbox.idempotency_key = indexable.handoff_idempotency_key
                WHERE indexable.tenant_id = :tenant_id
                  AND indexable.handoff_idempotency_key = :handoff_idempotency_key
                """
            ),
            {"tenant_id": tenant_id, "handoff_idempotency_key": handoff_idempotency_key},
        ).mappings().first()
        if row is None:
            raise IngestionPersistenceError(
                f"missing snapshot handoff replay receipt: {handoff_idempotency_key}"
            )
        return dict(row)

    def claim_parse_attempt_lease(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        source_object_id: str,
        document_version_id: str,
        parse_plan_id: str,
        parse_job_id: str,
        worker_id: str,
        idempotency_key: str,
        security_epoch_ref: str,
        lease_ttl_seconds: int = 60,
    ) -> IngestionReceipt:
        if lease_ttl_seconds <= 0:
            raise IngestionPersistenceError("lease_ttl_seconds must be positive")
        row = self.connection.execute(
            text(
                """
                SELECT COALESCE(MAX(attempt_no), 0) + 1 AS attempt_no,
                       COALESCE(MAX(fencing_token), 0) + 1 AS fencing_token
                FROM ingestion_parse_attempts
                WHERE parse_job_id = :parse_job_id
                """
            ),
            {"parse_job_id": parse_job_id},
        ).mappings().one()
        attempt_no = int(row["attempt_no"])
        fencing_token = int(row["fencing_token"])
        parse_attempt_id = f"{parse_job_id}:attempt:{attempt_no}"
        lease_ref = f"{parse_attempt_id}:lease:{fencing_token}"
        lease_expires_at = datetime.now(timezone.utc) + timedelta(seconds=lease_ttl_seconds)
        self.record_parse_attempt(
            parse_attempt_id=parse_attempt_id,
            tenant_id=tenant_id,
            parse_job_id=parse_job_id,
            attempt_no=attempt_no,
            worker_id=worker_id,
            lease_ref=lease_ref,
            fencing_token=fencing_token,
            workspace_id=workspace_id,
            source_object_id=source_object_id,
            document_version_id=document_version_id,
            parse_plan_id=parse_plan_id,
            idempotency_key=idempotency_key,
            security_epoch_ref=security_epoch_ref,
            lease_expires_at=lease_expires_at,
            status="lease_claimed",
        )
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_leases(
                    lease_ref, tenant_id, workspace_id, parse_job_id, parse_attempt_id,
                    worker_id, fencing_token, state, lease_expires_at
                ) VALUES (
                    :lease_ref, :tenant_id, :workspace_id, :parse_job_id, :parse_attempt_id,
                    :worker_id, :fencing_token, 'claimed', :lease_expires_at
                )
                """
            ),
            {
                "lease_ref": lease_ref,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "parse_job_id": parse_job_id,
                "parse_attempt_id": parse_attempt_id,
                "worker_id": worker_id,
                "fencing_token": fencing_token,
                "lease_expires_at": lease_expires_at,
            },
        )
        self.update_parse_job_status(parse_job_id=parse_job_id, tenant_id=tenant_id, status="leased")
        return IngestionReceipt(parse_attempt_id, tenant_id, "lease_claimed", str(fencing_token))

    def mark_parse_attempt_running(
        self,
        *,
        parse_attempt_id: str,
        parse_job_id: str,
        tenant_id: str,
        worker_id: str,
        fencing_token: int,
    ) -> None:
        self._update_attempt_if_current(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            status="running",
            expected_statuses=("lease_claimed",),
        )
        self.update_parse_job_status(parse_job_id=parse_job_id, tenant_id=tenant_id, status="running")

    def renew_parse_attempt_lease(
        self,
        *,
        parse_attempt_id: str,
        parse_job_id: str,
        tenant_id: str,
        worker_id: str,
        fencing_token: int,
        lease_ttl_seconds: int = 60,
    ) -> IngestionReceipt:
        if lease_ttl_seconds <= 0:
            raise IngestionPersistenceError("lease_ttl_seconds must be positive")
        lease_expires_at = datetime.now(timezone.utc) + timedelta(seconds=lease_ttl_seconds)
        result = self.connection.execute(
            text(
                """
                UPDATE ingestion_parse_leases
                SET state = 'renewed',
                    heartbeat_at = now(),
                    lease_expires_at = :lease_expires_at
                WHERE parse_attempt_id = :parse_attempt_id
                  AND parse_job_id = :parse_job_id
                  AND worker_id = :worker_id
                  AND fencing_token = :fencing_token
                  AND state in ('claimed','renewed')
                  AND lease_expires_at > now()
                """
            ),
            {
                "parse_attempt_id": parse_attempt_id,
                "parse_job_id": parse_job_id,
                "worker_id": worker_id,
                "fencing_token": fencing_token,
                "lease_expires_at": lease_expires_at,
            },
        )
        if result.rowcount != 1:
            raise IngestionPersistenceError("parse lease renew rejected by fencing")
        self._update_attempt_if_current(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            status="running",
            lease_expires_at=lease_expires_at,
            expected_statuses=("running",),
        )
        return IngestionReceipt(parse_attempt_id, tenant_id, "lease_renewed", str(fencing_token))

    def heartbeat_parse_attempt_lease(
        self,
        *,
        parse_attempt_id: str,
        parse_job_id: str,
        tenant_id: str,
        worker_id: str,
        fencing_token: int,
    ) -> IngestionReceipt:
        result = self.connection.execute(
            text(
                """
                UPDATE ingestion_parse_leases
                SET heartbeat_at = now()
                WHERE parse_attempt_id = :parse_attempt_id
                  AND parse_job_id = :parse_job_id
                  AND tenant_id = :tenant_id
                  AND worker_id = :worker_id
                  AND fencing_token = :fencing_token
                  AND state in ('claimed','renewed')
                  AND lease_expires_at > now()
                """
            ),
            {
                "parse_attempt_id": parse_attempt_id,
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "worker_id": worker_id,
                "fencing_token": fencing_token,
            },
        )
        if result.rowcount != 1:
            raise IngestionPersistenceError("parse lease heartbeat rejected by fencing")
        self._update_attempt_if_current(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            status="running",
            expected_statuses=("running",),
        )
        return IngestionReceipt(parse_attempt_id, tenant_id, "lease_heartbeat", str(fencing_token))

    def reconcile_expired_parse_attempt_lease(
        self,
        *,
        parse_attempt_id: str,
        parse_job_id: str,
        tenant_id: str,
    ) -> IngestionReceipt:
        row = self.connection.execute(
            text(
                """
                UPDATE ingestion_parse_leases AS lease
                SET state = 'expired', heartbeat_at = now()
                FROM ingestion_parse_attempts AS attempt
                WHERE lease.parse_attempt_id = :parse_attempt_id
                  AND lease.parse_job_id = :parse_job_id
                  AND lease.tenant_id = :tenant_id
                  AND lease.parse_attempt_id = attempt.parse_attempt_id
                  AND attempt.parse_job_id = :parse_job_id
                  AND attempt.tenant_id = :tenant_id
                  AND lease.state in ('claimed','renewed')
                  AND lease.lease_expires_at <= now()
                RETURNING attempt.worker_id, attempt.fencing_token
                """
            ),
            {"parse_attempt_id": parse_attempt_id, "parse_job_id": parse_job_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row is None:
            raise IngestionPersistenceError("expired parse lease reconciliation found no expired lease")
        self._update_attempt_if_current(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=str(row["worker_id"]),
            fencing_token=int(row["fencing_token"]),
            status="lease_lost",
            require_unexpired_lease=False,
            expected_statuses=("lease_claimed", "running"),
        )
        self.update_parse_job_status(parse_job_id=parse_job_id, tenant_id=tenant_id, status="queued")
        return IngestionReceipt(parse_attempt_id, tenant_id, "lease_reconciled")

    def commit_parse_attempt_if_current(
        self,
        *,
        parse_attempt_id: str,
        parse_job_id: str,
        tenant_id: str,
        worker_id: str,
        fencing_token: int,
        domain_commit_ref: str,
    ) -> None:
        self._update_attempt_if_current(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            status="succeeded",
            domain_commit_ref=domain_commit_ref,
            expected_statuses=("running",),
        )
        result = self.connection.execute(
            text(
                """
                UPDATE ingestion_parse_leases
                SET state = 'committed', domain_commit_ref = :domain_commit_ref, heartbeat_at = now()
                WHERE parse_attempt_id = :parse_attempt_id
                  AND parse_job_id = :parse_job_id
                  AND worker_id = :worker_id
                  AND fencing_token = :fencing_token
                  AND state in ('claimed','renewed')
                  AND lease_expires_at > now()
                """
            ),
            {
                "parse_attempt_id": parse_attempt_id,
                "parse_job_id": parse_job_id,
                "worker_id": worker_id,
                "fencing_token": fencing_token,
                "domain_commit_ref": domain_commit_ref,
            },
        )
        if result.rowcount != 1:
            raise IngestionPersistenceError("parse lease commit rejected by fencing")
        self.update_parse_job_status(parse_job_id=parse_job_id, tenant_id=tenant_id, status="succeeded")

    def fail_parse_attempt(
        self,
        *,
        parse_attempt_id: str,
        parse_job_id: str,
        tenant_id: str,
        worker_id: str,
        fencing_token: int,
        status: str,
        failure_code: str,
    ) -> None:
        self._update_attempt_if_current(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            status=status,
            failure_code=failure_code,
            expected_statuses=("running",),
        )
        lease_state = "released" if status in {"failed", "cancelled", "dead_letter"} else "lost"
        result = self.connection.execute(
            text(
                """
                UPDATE ingestion_parse_leases
                SET state = :lease_state, heartbeat_at = now()
                WHERE parse_attempt_id = :parse_attempt_id
                  AND parse_job_id = :parse_job_id
                  AND worker_id = :worker_id
                  AND fencing_token = :fencing_token
                  AND state in ('claimed','renewed')
                """
            ),
            {
                "lease_state": lease_state,
                "parse_attempt_id": parse_attempt_id,
                "parse_job_id": parse_job_id,
                "worker_id": worker_id,
                "fencing_token": fencing_token,
            },
        )
        if result.rowcount != 1:
            raise IngestionPersistenceError("parse lease terminal update rejected by fencing")
        self.update_parse_job_status(parse_job_id=parse_job_id, tenant_id=tenant_id, status=status)

    def update_parse_job_status(self, *, parse_job_id: str, tenant_id: str, status: str) -> None:
        result = self.connection.execute(
            text(
                """
                UPDATE ingestion_parse_jobs
                SET status = :status,
                    attempt_count = (
                        SELECT count(*) FROM ingestion_parse_attempts
                        WHERE parse_job_id = :parse_job_id
                    )
                WHERE parse_job_id = :parse_job_id AND tenant_id = :tenant_id
                """
            ),
            {"parse_job_id": parse_job_id, "tenant_id": tenant_id, "status": status},
        )
        if result.rowcount != 1:
            raise IngestionPersistenceError("parse job status update failed")

    def record_dead_letter(
        self,
        *,
        dead_letter_id: str,
        tenant_id: str,
        parse_job_id: str,
        parse_attempt_id: str,
        source_ref: str,
        failure_code: str,
        retryable: bool,
        retry_count: int,
        rabbitmq_dead_letter_ref: str,
        payload: dict[str, Any],
    ) -> IngestionReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_dead_letters(
                    dead_letter_id, tenant_id, source_ref, failure_code, retryable,
                    payload, parse_job_id, parse_attempt_id, rabbitmq_dead_letter_ref, retry_count
                ) VALUES (
                    :dead_letter_id, :tenant_id, :source_ref, :failure_code, :retryable,
                    CAST(:payload AS jsonb), :parse_job_id, :parse_attempt_id,
                    :rabbitmq_dead_letter_ref, :retry_count
                )
                """
            ),
            {
                "dead_letter_id": dead_letter_id,
                "tenant_id": tenant_id,
                "source_ref": source_ref,
                "failure_code": failure_code,
                "retryable": retryable,
                "payload": canonical_json(payload),
                "parse_job_id": parse_job_id,
                "parse_attempt_id": parse_attempt_id,
                "rabbitmq_dead_letter_ref": rabbitmq_dead_letter_ref,
                "retry_count": retry_count,
            },
        )
        return IngestionReceipt(dead_letter_id, tenant_id, "dead_letter")

    def _update_attempt_if_current(
        self,
        *,
        parse_attempt_id: str,
        parse_job_id: str,
        tenant_id: str,
        worker_id: str,
        fencing_token: int,
        status: str,
        domain_commit_ref: str | None = None,
        failure_code: str | None = None,
        lease_expires_at: datetime | None = None,
        require_unexpired_lease: bool = True,
        expected_statuses: tuple[str, ...] = ("created", "lease_claimed", "running"),
    ) -> None:
        if not expected_statuses:
            raise IngestionPersistenceError("expected parse attempt status set must not be empty")
        result = self.connection.execute(
            text(
                """
                UPDATE ingestion_parse_attempts
                SET status = :status,
                    domain_commit_ref = COALESCE(:domain_commit_ref, domain_commit_ref),
                    failure_code = COALESCE(:failure_code, failure_code),
                    lease_expires_at = COALESCE(:lease_expires_at, lease_expires_at),
                    heartbeat_at = now(),
                    finished_at = CASE
                        WHEN :status in ('succeeded','failed','cancelled','lease_lost','dead_letter','fenced_out')
                        THEN now()
                        ELSE finished_at
                    END
                WHERE parse_attempt_id = :parse_attempt_id
                  AND parse_job_id = :parse_job_id
                  AND tenant_id = :tenant_id
                  AND worker_id = :worker_id
                  AND fencing_token = :fencing_token
                  AND fencing_token = (
                      SELECT max(current_attempt.fencing_token)
                      FROM ingestion_parse_attempts AS current_attempt
                      WHERE current_attempt.parse_job_id = :parse_job_id
                  )
                  AND (:require_unexpired_lease = false OR lease_expires_at > now())
                  AND status IN :expected_statuses
                  AND status not in ('succeeded','failed','cancelled','lease_lost','dead_letter','fenced_out')
                """
            ).bindparams(bindparam("expected_statuses", expanding=True)),
            {
                "parse_attempt_id": parse_attempt_id,
                "parse_job_id": parse_job_id,
                "tenant_id": tenant_id,
                "worker_id": worker_id,
                "fencing_token": fencing_token,
                "status": status,
                "domain_commit_ref": domain_commit_ref,
                "failure_code": failure_code,
                "lease_expires_at": lease_expires_at,
                "require_unexpired_lease": require_unexpired_lease,
                "expected_statuses": expected_statuses,
            },
        )
        if result.rowcount != 1:
            raise IngestionPersistenceError("parse attempt update rejected by fencing")

    def record_parse_snapshot(
        self,
        *,
        parse_snapshot_id: str,
        tenant_id: str,
        parse_job_id: str,
        parse_attempt_id: str,
        document_version_id: str,
        canonical_ir: dict[str, Any],
        canonical_ir_ref: str,
        canonical_ir_schema_ref: str,
        parser_id: str,
        parser_version: str,
        status: str = "succeeded",
        diagnostics: list[dict[str, Any]] | None = None,
    ) -> IngestionReceipt:
        snapshot_hash = canonical_sha256(canonical_ir)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_parse_snapshots(
                    parse_snapshot_id, tenant_id, parse_job_id, parse_attempt_id,
                    document_version_id, snapshot_hash, canonical_ir_ref,
                    canonical_ir_schema_ref, parser_id, parser_version, status, diagnostics
                ) VALUES (
                    :parse_snapshot_id, :tenant_id, :parse_job_id, :parse_attempt_id,
                    :document_version_id, :snapshot_hash, :canonical_ir_ref,
                    :canonical_ir_schema_ref, :parser_id, :parser_version, :status,
                    CAST(:diagnostics AS jsonb)
                )
                """
            ),
            {
                "parse_snapshot_id": parse_snapshot_id,
                "tenant_id": tenant_id,
                "parse_job_id": parse_job_id,
                "parse_attempt_id": parse_attempt_id,
                "document_version_id": document_version_id,
                "snapshot_hash": snapshot_hash,
                "canonical_ir_ref": canonical_ir_ref,
                "canonical_ir_schema_ref": canonical_ir_schema_ref,
                "parser_id": parser_id,
                "parser_version": parser_version,
                "status": status,
                "diagnostics": canonical_json(diagnostics or []),
            },
        )
        return IngestionReceipt(parse_snapshot_id, tenant_id, status, snapshot_hash)

    def record_source_span(
        self,
        *,
        source_span_id: str,
        tenant_id: str,
        parse_snapshot_id: str,
        document_version_id: str,
        block_id: str,
        coordinate_ref: dict[str, Any],
        page_no: int | None = None,
        region_ref: str | None = None,
    ) -> IngestionReceipt:
        span_hash = canonical_sha256(
            {
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "block_id": block_id,
                "page_no": page_no,
                "region_ref": region_ref,
                "coordinate_ref": coordinate_ref,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_source_spans(
                    source_span_id, tenant_id, parse_snapshot_id, document_version_id,
                    block_id, page_no, region_ref, coordinate_ref, span_hash
                ) VALUES (
                    :source_span_id, :tenant_id, :parse_snapshot_id, :document_version_id,
                    :block_id, :page_no, :region_ref, CAST(:coordinate_ref AS jsonb), :span_hash
                )
                """
            ),
            {
                "source_span_id": source_span_id,
                "tenant_id": tenant_id,
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "block_id": block_id,
                "page_no": page_no,
                "region_ref": region_ref,
                "coordinate_ref": canonical_json(coordinate_ref),
                "span_hash": span_hash,
            },
        )
        return IngestionReceipt(source_span_id, tenant_id, "recorded", span_hash)

    def record_quality_decision(
        self,
        *,
        quality_decision_id: str,
        tenant_id: str,
        parse_snapshot_id: str,
        coverage_score: float,
        confidence_score: float,
        decision: str,
        review_task_ref: str | None = None,
    ) -> IngestionReceipt:
        decision_hash = canonical_sha256(
            {
                "parse_snapshot_id": parse_snapshot_id,
                "coverage_score": coverage_score,
                "confidence_score": confidence_score,
                "decision": decision,
                "review_task_ref": review_task_ref,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_quality_gate_decisions(
                    quality_decision_id, tenant_id, parse_snapshot_id, coverage_score,
                    confidence_score, decision, review_task_ref, decision_hash
                ) VALUES (
                    :quality_decision_id, :tenant_id, :parse_snapshot_id, :coverage_score,
                    :confidence_score, :decision, :review_task_ref, :decision_hash
                )
                """
            ),
            {
                "quality_decision_id": quality_decision_id,
                "tenant_id": tenant_id,
                "parse_snapshot_id": parse_snapshot_id,
                "coverage_score": coverage_score,
                "confidence_score": confidence_score,
                "decision": decision,
                "review_task_ref": review_task_ref,
                "decision_hash": decision_hash,
            },
        )
        return IngestionReceipt(quality_decision_id, tenant_id, decision, decision_hash)

    def record_indexable_snapshot(
        self,
        *,
        indexable_snapshot_id: str,
        tenant_id: str,
        parse_snapshot_id: str,
        document_version_id: str,
        quality_decision_id: str,
        visibility_ref: str,
        payload: dict[str, Any],
        handoff_idempotency_key: str | None = None,
        knowledge_handoff_status: str = "pending",
    ) -> IngestionReceipt:
        snapshot_hash = canonical_sha256(payload)
        handoff_hash = canonical_sha256(
            {
                "indexable_snapshot_id": indexable_snapshot_id,
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "quality_decision_id": quality_decision_id,
                "payload": payload,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_indexable_document_snapshots(
                    indexable_snapshot_id, tenant_id, parse_snapshot_id, document_version_id,
                    quality_decision_id, snapshot_hash, handoff_envelope_hash,
                    visibility_ref, handoff_idempotency_key, knowledge_handoff_status
                ) VALUES (
                    :indexable_snapshot_id, :tenant_id, :parse_snapshot_id, :document_version_id,
                    :quality_decision_id, :snapshot_hash, :handoff_envelope_hash,
                    :visibility_ref, :handoff_idempotency_key, :knowledge_handoff_status
                )
                """
            ),
            {
                "indexable_snapshot_id": indexable_snapshot_id,
                "tenant_id": tenant_id,
                "parse_snapshot_id": parse_snapshot_id,
                "document_version_id": document_version_id,
                "quality_decision_id": quality_decision_id,
                "snapshot_hash": snapshot_hash,
                "handoff_envelope_hash": handoff_hash,
                "visibility_ref": visibility_ref,
                "handoff_idempotency_key": handoff_idempotency_key,
                "knowledge_handoff_status": knowledge_handoff_status,
            },
        )
        return IngestionReceipt(indexable_snapshot_id, tenant_id, knowledge_handoff_status, handoff_hash)

    def enqueue_outbox_event(
        self,
        *,
        outbox_event_id: str,
        tenant_id: str,
        aggregate_ref: str,
        event_type: str,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
        publish_status: str = "pending",
    ) -> IngestionReceipt:
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO ingestion_outbox_events(
                    outbox_event_id, tenant_id, aggregate_ref, event_type,
                    payload_hash, payload, idempotency_key, publish_status
                ) VALUES (
                    :outbox_event_id, :tenant_id, :aggregate_ref, :event_type,
                    :payload_hash, CAST(:payload AS jsonb), :idempotency_key, :publish_status
                )
                """
            ),
            {
                "outbox_event_id": outbox_event_id,
                "tenant_id": tenant_id,
                "aggregate_ref": aggregate_ref,
                "event_type": event_type,
                "payload_hash": payload_hash,
                "payload": canonical_json(payload),
                "idempotency_key": idempotency_key,
                "publish_status": publish_status,
            },
        )
        return IngestionReceipt(outbox_event_id, tenant_id, publish_status, payload_hash)

    def get_indexable_snapshot(self, indexable_snapshot_id: str) -> dict[str, Any]:
        row = self.connection.execute(
            text(
                """
                SELECT indexable_snapshot_id, parse_snapshot_id, document_version_id,
                       quality_decision_id, snapshot_hash, handoff_envelope_hash,
                       visibility_ref, handoff_idempotency_key, knowledge_handoff_status
                FROM ingestion_indexable_document_snapshots
                WHERE indexable_snapshot_id = :indexable_snapshot_id
                """
            ),
            {"indexable_snapshot_id": indexable_snapshot_id},
        ).mappings().first()
        if row is None:
            raise IngestionPersistenceError(f"missing indexable snapshot: {indexable_snapshot_id}")
        return dict(row)

    @staticmethod
    def _require_hash(value: str, field_name: str) -> None:
        if len(value) != 64:
            raise IngestionPersistenceError(f"{field_name} must be a 64-character sha256 hash")
