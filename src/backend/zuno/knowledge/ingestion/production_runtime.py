from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import Any, Protocol
from urllib.parse import urlparse

from sqlalchemy import Engine

from zuno.knowledge.ingestion.contracts import ParseDocumentRequest
from zuno.knowledge.ingestion.gateway import ParseGateway
from zuno.knowledge.ingestion.handoff import SnapshotHandoffRuntime
from zuno.knowledge.ingestion.review import HumanReviewRuntime
from zuno.knowledge.ingestion.source_object_commit import SourceObjectCommitRuntime
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.queue.domain import CanonicalOutboxDeliveryV1
from zuno.platform.queue.rabbitmq import RabbitMQDelivery
from zuno.platform.storage.durable import DurableMinioObjectStore


class AckableDelivery(Protocol):
    message_id: str
    payload: dict[str, Any]
    headers: dict[str, Any]
    redelivered: bool

    async def ack(self) -> None: ...

    async def nack(self, *, requeue: bool) -> None: ...

    async def reject(self, *, requeue: bool = False) -> None: ...


@dataclass(frozen=True, slots=True)
class PackageAUploadCommand:
    tenant_id: str
    workspace_id: str
    principal_id: str
    filename: str
    mime_type: str
    content: bytes
    bucket: str
    source_object_id: str
    classification_ref: str
    security_epoch_ref: str
    trace_id: str
    parser_policy_ref: str = "parser-policy:phase11-package-a"
    quality_policy_ref: str = "quality-policy:phase11-package-a"
    security_decision_ref: str = "security-decision:phase11-package-a"


@dataclass(frozen=True, slots=True)
class PackageAUploadReceipt:
    source_object_id: str
    document_version_id: str
    parse_plan_id: str
    parse_job_id: str
    outbox_event_id: str
    object_ref: str
    status: str = "accepted"


@dataclass(frozen=True, slots=True)
class PackageAWorkerReceipt:
    parse_job_id: str
    parse_attempt_id: str | None
    status: str
    acked_after_domain_commit: bool
    retry_enqueued_after_domain_commit: bool = False
    indexable_snapshot_id: str | None = None
    outbox_event_id: str | None = None
    dead_letter_id: str | None = None
    duplicate_delivery: bool = False


class PackageAProductionIngestionRuntime:
    def __init__(
        self,
        *,
        engine: Engine,
        object_store: DurableMinioObjectStore,
        worker_id: str,
        max_attempts: int = 2,
        lease_ttl_seconds: int = 60,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts includes the first execution and must be positive")
        self.engine = engine
        self.object_store = object_store
        self.worker_id = worker_id
        self.max_attempts = max_attempts
        self.lease_ttl_seconds = lease_ttl_seconds
        self.review_runtime = HumanReviewRuntime()
        self.handoff_runtime = SnapshotHandoffRuntime()
        self.commit_runtime = SourceObjectCommitRuntime()

    def accept_workspace_upload(self, command: PackageAUploadCommand) -> PackageAUploadReceipt:
        content_hash = hashlib.sha256(command.content).hexdigest()
        committed_name = self._object_name(command)
        ticket = self.object_store.stage(
            bucket=command.bucket,
            committed_object_name=committed_name,
            content=command.content,
        )
        receipt = self.object_store.commit(ticket)
        source_commit = self.commit_runtime.commit_from_physical_receipt(
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            source_id=command.source_object_id,
            filename=command.filename,
            mime_type=command.mime_type,
            owner_id=command.principal_id,
            classification_ref=command.classification_ref,
            security_epoch_ref=command.security_epoch_ref,
            committed_receipt=receipt,
            object_manifest_ref=f"object-manifest:s3://{receipt.bucket}/{receipt.object_name}",
            expected_sha256=content_hash,
            expected_size_bytes=len(command.content),
            expected_object_prefix=f"{command.tenant_id}/{command.workspace_id}/",
        )
        document_version_id = f"document-version:{command.source_object_id}:1"
        parse_plan_id = f"parse-plan:{command.source_object_id}:1"
        parse_job_id = f"parse-job:{command.source_object_id}:1"
        idempotency_key = f"parse:{command.tenant_id}:{command.workspace_id}:{content_hash}:1"
        envelope = self._parse_requested_envelope(
            command=command,
            document_version_id=document_version_id,
            parse_plan_id=parse_plan_id,
            parse_job_id=parse_job_id,
            object_ref=source_commit.object_ref,
            object_manifest_ref=source_commit.object_manifest_ref,
            content_hash=content_hash,
            size_bytes=len(command.content),
            idempotency_key=idempotency_key,
        )
        with IngestionUnitOfWork(self.engine) as repo:
            source = repo.record_source_object(
                source_object_id=command.source_object_id,
                tenant_id=command.tenant_id,
                workspace_id=command.workspace_id,
                filename=command.filename,
                mime_type=command.mime_type,
                declared_format=self._declared_format(command.mime_type, command.filename),
                storage_uri=source_commit.object_ref,
                object_manifest_ref=source_commit.object_manifest_ref,
                source_sha256=content_hash,
                size_bytes=len(command.content),
                classification_ref=command.classification_ref,
                security_epoch_ref=command.security_epoch_ref,
            )
            document = repo.record_document_version(
                document_version_id=document_version_id,
                tenant_id=command.tenant_id,
                workspace_id=command.workspace_id,
                source_object_id=source.ref,
                version_no=1,
                content_hash=content_hash,
                metadata={"filename": command.filename, "mime_type": command.mime_type},
                immutability_ref=f"immutability:{document_version_id}",
            )
            plan = repo.record_parse_plan(
                parse_plan_id=parse_plan_id,
                tenant_id=command.tenant_id,
                document_version_id=document.ref,
                parser_route={"primary": "native_markdown"},
                parser_policy_ref=command.parser_policy_ref,
                parser_bundle={"parser": "native_markdown", "version": "phase11-package-a-v1"},
                quality_policy_ref=command.quality_policy_ref,
                security_decision_ref=command.security_decision_ref,
            )
            job = repo.record_parse_job(
                parse_job_id=parse_job_id,
                tenant_id=command.tenant_id,
                parse_plan_id=plan.ref,
                document_version_id=document.ref,
                idempotency_key=idempotency_key,
                status="queued",
            )
            outbox = repo.enqueue_parse_requested(envelope=envelope)
        return PackageAUploadReceipt(
            source_object_id=source.ref,
            document_version_id=document.ref,
            parse_plan_id=plan.ref,
            parse_job_id=job.ref,
            outbox_event_id=outbox.ref,
            object_ref=source_commit.object_ref,
        )

    async def process_rabbitmq_delivery(self, delivery: RabbitMQDelivery | AckableDelivery) -> PackageAWorkerReceipt:
        parsed_delivery = CanonicalOutboxDeliveryV1.model_validate(delivery.payload)
        envelope = parsed_delivery.verified_envelope()
        if envelope.tenant_id != delivery.headers.get("tenant_id"):
            await delivery.reject(requeue=False)
            raise IngestionPersistenceError("delivery tenant header does not match envelope")
        payload = envelope.payload or {}
        parse_job_id = str(payload["parse_job_id"])
        tenant_id = envelope.tenant_id
        with IngestionUnitOfWork(self.engine) as repo:
            inbox = repo.record_worker_inbox(
                consumer="phase11-package-a-parser-worker",
                message_id=envelope.message_id,
                payload=delivery.payload,
                tenant_id=tenant_id,
            )
            if not inbox.processable:
                worker_receipt = PackageAWorkerReceipt(
                    parse_job_id=parse_job_id,
                    parse_attempt_id=None,
                    status="duplicate",
                    acked_after_domain_commit=True,
                    duplicate_delivery=True,
                )
            else:
                worker_receipt = self._process_first_seen_delivery(
                    repo=repo,
                    payload=payload,
                    envelope=envelope,
                    parse_job_id=parse_job_id,
                    tenant_id=tenant_id,
                )
        await delivery.ack()
        return worker_receipt

    def _process_first_seen_delivery(
        self,
        *,
        repo,
        payload: dict[str, Any],
        envelope: CrossModuleEnvelopeV1,
        parse_job_id: str,
        tenant_id: str,
    ) -> PackageAWorkerReceipt:
        context = repo.load_parse_job_context(parse_job_id=parse_job_id, tenant_id=tenant_id)
        attempt = repo.claim_parse_attempt_lease(
            tenant_id=tenant_id,
            workspace_id=str(context["workspace_id"]),
            source_object_id=str(context["source_object_id"]),
            document_version_id=str(context["document_version_id"]),
            parse_plan_id=str(context["parse_plan_id"]),
            parse_job_id=parse_job_id,
            worker_id=self.worker_id,
            idempotency_key=f"{context['idempotency_key']}:attempt:{int(context['attempt_count']) + 1}",
            security_epoch_ref=str(context["security_epoch_ref"]),
            lease_ttl_seconds=self.lease_ttl_seconds,
        )
        parse_attempt_id = attempt.ref
        fencing_token = int(attempt.payload_hash or "0")
        repo.mark_parse_attempt_running(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=self.worker_id,
            fencing_token=fencing_token,
        )
        source_bytes = self._read_and_verify_object(context)
        request = ParseDocumentRequest(
            document_id=str(context["source_object_id"]),
            source_id=str(context["source_object_id"]),
            document_version_id=str(context["document_version_id"]),
            parse_plan_id=str(context["parse_plan_id"]),
            parse_job_id=parse_job_id,
            parse_attempt_id=parse_attempt_id,
            parse_idempotency_key=str(context["idempotency_key"]),
            source_object_ref=str(context["storage_uri"]),
            source_object_manifest={
                "object_manifest_ref": context["object_manifest_ref"],
                "content_hash": context["source_sha256"],
                "size_bytes": context["size_bytes"],
                "parser_policy_ref": payload.get("parser_policy_ref"),
                "lineage_ref": f"lineage:{context['source_object_id']}:{context['document_version_id']}",
                "workspace_id": context["workspace_id"],
                "classification_ref": context["classification_ref"],
                "security_epoch_ref": context["security_epoch_ref"],
            },
            workspace_id=str(context["workspace_id"]),
            source_uri=str(context["storage_uri"]),
            mime_type=str(context["mime_type"]),
            source_bytes=source_bytes,
            hash=str(context["source_sha256"]),
            security_policy_ref=payload.get("security_decision_ref"),
            security_epoch_ref=str(context["security_epoch_ref"]),
        )
        result = ParseGateway.submit_parse_job(request)
        snapshot = ParseGateway.get_job_snapshot(result.job_id)
        if result.status != "succeeded" or result.document is None:
            retryable = bool(result.failure and result.failure.retryable)
            exhausted = int(context["attempt_count"]) + 1 >= self.max_attempts
            terminal_status = "failed" if retryable and not exhausted else "dead_letter"
            repo.fail_parse_attempt(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                status=terminal_status,
                failure_code=result.failure.failure_classification if result.failure else result.status,
            )
            dead_letter_id = None
            if terminal_status == "dead_letter":
                dead_letter = repo.record_dead_letter(
                    dead_letter_id=f"dead-letter:{parse_attempt_id}",
                    tenant_id=tenant_id,
                    parse_job_id=parse_job_id,
                    parse_attempt_id=parse_attempt_id,
                    source_ref=str(context["storage_uri"]),
                    failure_code=result.failure.failure_classification if result.failure else result.status,
                    retryable=retryable,
                    retry_count=int(context["attempt_count"]) + 1,
                    rabbitmq_dead_letter_ref=f"rabbitmq-dlq:{envelope.message_id}",
                    payload={"parse_job_id": parse_job_id, "status": result.status},
                )
                dead_letter_id = dead_letter.ref
            retry_outbox_id = None
            if terminal_status == "failed":
                retry_envelope = self._retry_parse_requested_envelope(
                    envelope=envelope,
                    context=context,
                    next_attempt_no=int(context["attempt_count"]) + 2,
                )
                retry_outbox = repo.enqueue_parse_requested(envelope=retry_envelope)
                retry_outbox_id = retry_outbox.ref
                repo.update_parse_job_status(parse_job_id=parse_job_id, tenant_id=tenant_id, status="queued")
            return PackageAWorkerReceipt(
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                status=terminal_status,
                acked_after_domain_commit=True,
                retry_enqueued_after_domain_commit=terminal_status == "failed",
                outbox_event_id=retry_outbox_id,
                dead_letter_id=dead_letter_id,
            )

        quality_gate, _review_task = self.review_runtime.evaluate(
            document=result.document,
            parse_snapshot=snapshot,
            security_epoch_ref=str(context["security_epoch_ref"]),
        )
        if not HumanReviewRuntime.can_publish_snapshot(gate=quality_gate):
            raise IngestionPersistenceError("Package A text/markdown path must pass quality gate")
        indexable_snapshot, snapshot_outbox = self.handoff_runtime.create_snapshot(
            document=result.document,
            parse_snapshot=snapshot,
            quality_gate=quality_gate,
            visibility_ref=f"visibility:{context['workspace_id']}:{context['source_object_id']}",
        )
        parse_snapshot_id = f"parse-snapshot:{parse_attempt_id}"
        snapshot_receipt = repo.record_parse_snapshot(
            parse_snapshot_id=parse_snapshot_id,
            tenant_id=tenant_id,
            parse_job_id=parse_job_id,
            parse_attempt_id=parse_attempt_id,
            document_version_id=str(context["document_version_id"]),
            canonical_ir=result.document.model_dump(mode="json"),
            canonical_ir_ref=f"canonical-ir:{parse_attempt_id}",
            canonical_ir_schema_ref=result.document.metadata.ir_schema_version,
            parser_id=result.document.metadata.parser_id,
            parser_version=result.document.metadata.parser_version,
        )
        for index, block in enumerate(result.document.blocks, start=1):
            repo.record_source_span(
                source_span_id=f"source-span:{parse_attempt_id}:{index}",
                tenant_id=tenant_id,
                parse_snapshot_id=snapshot_receipt.ref,
                document_version_id=str(context["document_version_id"]),
                block_id=block.block_id,
                page_no=block.source_span.page or block.source_span.page_number or 1,
                coordinate_ref=block.source_span.model_dump(),
            )
        quality = repo.record_quality_decision(
            quality_decision_id=f"quality:{parse_attempt_id}",
            tenant_id=tenant_id,
            parse_snapshot_id=snapshot_receipt.ref,
            coverage_score=self._quality_metric(quality_gate, "coverage"),
            confidence_score=self._quality_metric(quality_gate, "confidence"),
            decision="publish",
        )
        handoff_payload = {
            "indexable_snapshot_id": indexable_snapshot.indexable_snapshot_id,
            "document_version_id": indexable_snapshot.document_version_id,
            "quality_decision_id": indexable_snapshot.quality_decision_id,
            "canonical_hash": indexable_snapshot.canonical_hash,
            "idempotency_key": indexable_snapshot.idempotency_key,
        }
        indexable = repo.record_indexable_snapshot(
            indexable_snapshot_id=indexable_snapshot.indexable_snapshot_id,
            tenant_id=tenant_id,
            parse_snapshot_id=snapshot_receipt.ref,
            document_version_id=str(context["document_version_id"]),
            quality_decision_id=quality.ref,
            visibility_ref=indexable_snapshot.visibility_ref,
            payload=indexable_snapshot.payload,
        )
        outbox = repo.enqueue_outbox_event(
            outbox_event_id=snapshot_outbox.outbox_event_id,
            tenant_id=tenant_id,
            aggregate_ref=indexable.ref,
            event_type="ingestion.indexable_snapshot.ready",
            payload=handoff_payload,
        )
        domain_commit_ref = f"domain-commit:{parse_attempt_id}:{snapshot_receipt.ref}:{outbox.ref}"
        repo.commit_parse_attempt_if_current(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=self.worker_id,
            fencing_token=fencing_token,
            domain_commit_ref=domain_commit_ref,
        )
        return PackageAWorkerReceipt(
            parse_job_id=parse_job_id,
            parse_attempt_id=parse_attempt_id,
            status="succeeded",
            acked_after_domain_commit=True,
            indexable_snapshot_id=indexable.ref,
            outbox_event_id=outbox.ref,
        )

    def _parse_requested_envelope(
        self,
        *,
        command: PackageAUploadCommand,
        document_version_id: str,
        parse_plan_id: str,
        parse_job_id: str,
        object_ref: str,
        object_manifest_ref: str,
        content_hash: str,
        size_bytes: int,
        idempotency_key: str,
    ) -> CrossModuleEnvelopeV1:
        payload = {
            "tenant_id": command.tenant_id,
            "workspace_id": command.workspace_id,
            "source_object_id": command.source_object_id,
            "document_version_id": document_version_id,
            "parse_plan_id": parse_plan_id,
            "parse_job_id": parse_job_id,
            "object_ref": object_ref,
            "object_manifest_ref": object_manifest_ref,
            "content_hash": content_hash,
            "size_bytes": size_bytes,
            "mime_type": command.mime_type,
            "parser_policy_ref": command.parser_policy_ref,
            "quality_policy_ref": command.quality_policy_ref,
            "security_decision_ref": command.security_decision_ref,
            "security_epoch_ref": command.security_epoch_ref,
            "max_attempts": self.max_attempts,
        }
        now = datetime.now(timezone.utc)
        return CrossModuleEnvelopeV1(
            contract_name="zuno.ingestion.parse.requested",
            contract_version="v1",
            contract_bundle_version="wave1",
            message_id=f"outbox:{parse_job_id}",
            producer_module="workspace.file_upload",
            consumer_module="ingestion.parser_worker",
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            correlation_id=command.trace_id,
            idempotency_key=idempotency_key,
            aggregate_type="ParseJob",
            aggregate_id=parse_job_id,
            effective_security_epoch_ref=command.security_epoch_ref,
            trace_id=command.trace_id,
            data_classification=command.classification_ref,
            occurred_at=now,
            created_at=now,
            payload=payload,
            payload_hash=canonical_sha256(payload),
            payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
        )

    def _retry_parse_requested_envelope(
        self,
        *,
        envelope: CrossModuleEnvelopeV1,
        context: dict[str, Any],
        next_attempt_no: int,
    ) -> CrossModuleEnvelopeV1:
        now = datetime.now(timezone.utc)
        return envelope.model_copy(
            update={
                "message_id": f"outbox:{context['parse_job_id']}:retry:{next_attempt_no}",
                "producer_module": "ingestion.parser_worker",
                "consumer_module": "ingestion.parser_worker",
                "causation_id": envelope.message_id,
                "idempotency_key": f"{envelope.idempotency_key}:retry:{next_attempt_no}",
                "occurred_at": now,
                "created_at": now,
            }
        )

    def _read_and_verify_object(self, context: dict[str, Any]) -> bytes:
        parsed = urlparse(str(context["storage_uri"]))
        if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
            raise IngestionPersistenceError("Package A worker requires s3:// ObjectRef")
        content = self.object_store.store.read_object(bucket=parsed.netloc, object_name=parsed.path.lstrip("/"))
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != context["source_sha256"] or len(content) != int(context["size_bytes"]):
            raise IngestionPersistenceError("SourceObject bytes do not match PostgreSQL lineage facts")
        if context["source_status"] not in {"committed"}:
            raise IngestionPersistenceError("SourceObject is not visible for parsing")
        return content

    @staticmethod
    def _object_name(command: PackageAUploadCommand) -> str:
        safe_name = command.filename.replace("\\", "/").split("/")[-1]
        return f"{command.tenant_id}/{command.workspace_id}/source/{command.source_object_id}/{safe_name}"

    @staticmethod
    def _declared_format(mime_type: str, filename: str) -> str:
        lowered = filename.lower()
        if mime_type == "text/markdown" or lowered.endswith(".md"):
            return "markdown"
        if mime_type.startswith("text/"):
            return "text"
        return "unknown"

    @staticmethod
    def _quality_metric(quality_gate, name: str) -> float:
        for metric in quality_gate.metrics:
            if metric.name == name:
                return float(metric.value)
        return 1.0 if quality_gate.verdict == "PASS" else 0.0


__all__ = [
    "PackageAProductionIngestionRuntime",
    "PackageAUploadCommand",
    "PackageAUploadReceipt",
    "PackageAWorkerReceipt",
]
