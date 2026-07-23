from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import Any, Protocol
from urllib.parse import urlparse

from sqlalchemy import Engine

from zuno.knowledge.ingestion.contracts import CanonicalDocumentIR, ParseDocumentRequest, ParseJobSnapshot
from zuno.knowledge.ingestion.gateway import ParseGateway
from zuno.knowledge.ingestion.handoff import SnapshotHandoffRuntime
from zuno.knowledge.ingestion.review import HumanReviewRuntime, QualityGateResult, QualityMetric, ReviewDecisionReceipt, ReviewTask
from zuno.knowledge.ingestion.source_object_commit import SourceObjectCommitRuntime
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.queue.domain import CanonicalOutboxDeliveryV1
from zuno.platform.queue.rabbitmq import RabbitMQDelivery
from zuno.platform.storage.durable import DurableMinioObjectStore

PACKAGE_A_PARSE_CONTRACT_NAME = "zuno.ingestion.parse.requested"
PACKAGE_A_PARSE_CONSUMER_MODULE = "ingestion.parser_worker"
PACKAGE_A_PARSE_INITIAL_PRODUCER_MODULE = "workspace.file_upload"
PACKAGE_A_PARSE_RETRY_PRODUCER_MODULE = "ingestion.parser_worker"
PACKAGE_A_PARSE_REQUESTED_TOPIC = "ingestion.parse.requested"


class PackageARejectDeliveryError(IngestionPersistenceError):
    pass


class PackageAObjectVerificationError(IngestionPersistenceError):
    def __init__(self, message: str, *, failure_code: str) -> None:
        super().__init__(message)
        self.failure_code = failure_code


class PackageAParserIdentityError(IngestionPersistenceError):
    def __init__(self, message: str, *, failure_code: str) -> None:
        super().__init__(message)
        self.failure_code = failure_code


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
    deadline_at: datetime | None = None


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
    handoff_idempotency_key: str | None = None
    outbox_idempotency_key: str | None = None
    dead_letter_id: str | None = None
    failure_code: str | None = None
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
        idempotency_key = f"parse:{command.tenant_id}:{command.workspace_id}:{content_hash}:1"
        replay_receipt = self._load_workspace_upload_replay_receipt(
            command=command,
            content_hash=content_hash,
            idempotency_key=idempotency_key,
        )
        if replay_receipt is not None:
            return replay_receipt
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

    def resume_approved_review(
        self,
        *,
        tenant_id: str,
        review_task_id: str,
        decision_id: str,
    ) -> PackageAWorkerReceipt:
        with IngestionUnitOfWork(self.engine) as repo:
            review_task_row = repo.get_review_task(review_task_id)
            if str(review_task_row["tenant_id"]) != str(tenant_id):
                raise IngestionPersistenceError("approved review resume tenant mismatch")
            decision_row = repo.get_review_decision_receipt(decision_id)
            if str(decision_row["review_task_id"]) != str(review_task_id):
                raise IngestionPersistenceError("approved review resume decision mismatch")
            review_task_data = dict(review_task_row)
            if hasattr(review_task_data.get("expires_at"), "timestamp"):
                review_task_data["expires_at"] = review_task_data["expires_at"].timestamp()
            review_receipt_data = dict(decision_row)
            if hasattr(review_receipt_data.get("decided_at"), "timestamp"):
                review_receipt_data["decided_at"] = review_receipt_data["decided_at"].timestamp()
            review_task = ReviewTask.model_validate(review_task_data)
            review_receipt = ReviewDecisionReceipt.model_validate(review_receipt_data)
            if review_receipt.status != "approved":
                raise IngestionPersistenceError("approved review resume requires approved decision")
            parse_snapshot_row = repo.get_parse_snapshot(str(review_task_row["parse_snapshot_id"]))
            quality_row = repo.get_quality_decision(str(review_task_row["quality_decision_id"]))
            document_row = repo.get_document_version(str(review_task_row["document_version_id"]))
            context = repo.load_parse_job_context(
                parse_job_id=str(parse_snapshot_row["parse_job_id"]),
                tenant_id=str(tenant_id),
            )
            document = CanonicalDocumentIR.model_validate(parse_snapshot_row["canonical_ir_json"])
            parse_snapshot = self._build_review_resume_snapshot(
                parse_snapshot_row=parse_snapshot_row,
                context=context,
            )
            quality_gate = self._build_quality_gate_result(
                quality_row=quality_row,
                review_task=review_task,
            )
            if not HumanReviewRuntime.can_publish_snapshot(gate=quality_gate, receipt=review_receipt):
                raise IngestionPersistenceError("approved review resume is not publishable")
            visibility_ref = f"visibility:{context['workspace_id']}:{context['source_object_id']}"
            indexable_snapshot, snapshot_outbox = self.handoff_runtime.create_snapshot(
                document=document,
                parse_snapshot=parse_snapshot,
                quality_gate=quality_gate,
                visibility_ref=visibility_ref,
                review_receipt=review_receipt,
            )
            replay = None
            try:
                replay = repo.load_snapshot_handoff_replay_receipt(
                    tenant_id=tenant_id,
                    handoff_idempotency_key=indexable_snapshot.idempotency_key,
                )
            except IngestionPersistenceError:
                replay = None
            if replay is not None:
                self._validate_snapshot_handoff_replay_receipt(
                    replay={
                        "parse_snapshot_id": parse_snapshot_row["parse_snapshot_id"],
                        "document_version_id": document_row["document_version_id"],
                        "quality_decision_id": quality_gate.quality_decision_id,
                        "workspace_id": context["workspace_id"],
                        "source_object_id": context["source_object_id"],
                        "handoff_idempotency_key": indexable_snapshot.idempotency_key,
                        "indexable_snapshot_id": replay["indexable_snapshot_id"],
                        "outbox_event_id": replay["outbox_event_id"],
                        "outbox_idempotency_key": replay["outbox_payload_idempotency_key"],
                        "handoff_envelope_hash": replay["handoff_envelope_hash"],
                        "visibility_ref": replay["visibility_ref"],
                        "knowledge_handoff_status": replay["knowledge_handoff_status"],
                        "outbox_publish_status": replay["outbox_publish_status"],
                    },
                    handoff_replay=replay,
                )
                return PackageAWorkerReceipt(
                    parse_job_id=str(parse_snapshot_row["parse_job_id"]),
                    parse_attempt_id=str(parse_snapshot_row["parse_attempt_id"]),
                    status="succeeded",
                    acked_after_domain_commit=True,
                    indexable_snapshot_id=str(replay["indexable_snapshot_id"]),
                    outbox_event_id=str(replay["outbox_event_id"]),
                    handoff_idempotency_key=str(replay["handoff_idempotency_key"]),
                    outbox_idempotency_key=str(replay["outbox_payload_idempotency_key"]),
                )
            indexable = repo.record_indexable_snapshot(
                indexable_snapshot_id=indexable_snapshot.indexable_snapshot_id,
                tenant_id=tenant_id,
                parse_snapshot_id=str(parse_snapshot_row["parse_snapshot_id"]),
                document_version_id=str(document_row["document_version_id"]),
                quality_decision_id=quality_gate.quality_decision_id,
                visibility_ref=visibility_ref,
                payload=indexable_snapshot.payload,
                handoff_idempotency_key=indexable_snapshot.idempotency_key,
            )
            outbox = repo.enqueue_outbox_event(
                outbox_event_id=snapshot_outbox.outbox_event_id,
                tenant_id=tenant_id,
                aggregate_ref=indexable.ref,
                event_type="ingestion.indexable_snapshot.ready",
                payload={
                    "indexable_snapshot_id": indexable_snapshot.indexable_snapshot_id,
                    "document_version_id": indexable_snapshot.document_version_id,
                    "quality_decision_id": indexable_snapshot.quality_decision_id,
                    "canonical_hash": indexable_snapshot.canonical_hash,
                    "idempotency_key": indexable_snapshot.idempotency_key,
                },
                idempotency_key=snapshot_outbox.idempotency_key,
            )
            return PackageAWorkerReceipt(
                parse_job_id=str(parse_snapshot_row["parse_job_id"]),
                parse_attempt_id=str(parse_snapshot_row["parse_attempt_id"]),
                status="succeeded",
                acked_after_domain_commit=True,
                indexable_snapshot_id=indexable.ref,
                outbox_event_id=outbox.ref,
                handoff_idempotency_key=indexable_snapshot.idempotency_key,
                outbox_idempotency_key=snapshot_outbox.idempotency_key,
            )

    def _load_workspace_upload_replay_receipt(
        self,
        *,
        command: PackageAUploadCommand,
        content_hash: str,
        idempotency_key: str,
    ) -> PackageAUploadReceipt | None:
        with IngestionUnitOfWork(self.engine) as repo:
            replay = repo.load_workspace_upload_replay_receipt(
                tenant_id=command.tenant_id,
                idempotency_key=idempotency_key,
            )
        if replay is None:
            return None
        self._validate_workspace_upload_replay(
            command=command,
            replay=replay,
            content_hash=content_hash,
        )
        return PackageAUploadReceipt(
            source_object_id=str(replay["source_object_id"]),
            document_version_id=str(replay["document_version_id"]),
            parse_plan_id=str(replay["parse_plan_id"]),
            parse_job_id=str(replay["parse_job_id"]),
            outbox_event_id=str(replay["outbox_event_id"]),
            object_ref=str(replay["object_ref"]),
        )

    @staticmethod
    def _validate_workspace_upload_replay(
        *,
        command: PackageAUploadCommand,
        replay: dict[str, Any],
        content_hash: str,
    ) -> None:
        expected = {
            "workspace_id": command.workspace_id,
            "source_sha256": content_hash,
            "size_bytes": len(command.content),
            "filename": command.filename,
            "mime_type": command.mime_type,
            "declared_format": PackageAProductionIngestionRuntime._declared_format(
                command.mime_type,
                command.filename,
            ),
            "classification_ref": command.classification_ref,
            "security_epoch_ref": command.security_epoch_ref,
        }
        for field_name, expected_value in expected.items():
            if str(replay.get(field_name)) != str(expected_value):
                raise IngestionPersistenceError(f"workspace upload replay conflict: {field_name}")
        parsed = urlparse(str(replay.get("object_ref", "")))
        expected_prefix = f"{command.tenant_id}/{command.workspace_id}/"
        if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.lstrip("/").startswith(expected_prefix):
            raise IngestionPersistenceError("workspace upload replay conflict: object_ref")
        if not replay.get("outbox_event_id"):
            raise IngestionPersistenceError("workspace upload replay missing parse-request outbox")

    async def process_rabbitmq_delivery(self, delivery: RabbitMQDelivery | AckableDelivery) -> PackageAWorkerReceipt:
        try:
            parsed_delivery = CanonicalOutboxDeliveryV1.model_validate(delivery.payload)
            envelope = parsed_delivery.verified_envelope()
        except Exception as exc:
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("invalid Package A parse delivery envelope") from exc
        if str(delivery.message_id) != str(envelope.message_id):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery message_id does not match envelope")
        if (
            parsed_delivery.topic != PACKAGE_A_PARSE_REQUESTED_TOPIC
            or envelope.contract_name != PACKAGE_A_PARSE_CONTRACT_NAME
            or envelope.consumer_module != PACKAGE_A_PARSE_CONSUMER_MODULE
        ):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery is not a Package A parse request")
        payload = envelope.payload or {}
        if (
            envelope.aggregate_type != "ParseJob"
            or payload.get("parse_job_id") is None
            or str(payload.get("parse_job_id")) != str(envelope.aggregate_id)
        ):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery parse job identity mismatch")
        if (
            envelope.tenant_id != delivery.headers.get("tenant_id")
            or str(payload.get("tenant_id")) != str(envelope.tenant_id)
        ):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery tenant header does not match envelope")
        header_workspace_id = delivery.headers.get("workspace_id")
        if (
            header_workspace_id is None
            or str(header_workspace_id) != str(envelope.workspace_id)
            or str(payload.get("workspace_id")) != str(envelope.workspace_id)
        ):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery workspace header does not match envelope")
        header_trace_id = delivery.headers.get("trace_id")
        if header_trace_id is None or str(header_trace_id) != str(envelope.trace_id):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery trace header does not match envelope")
        header_data_classification = delivery.headers.get("data_classification")
        if (
            header_data_classification is None
            or str(header_data_classification) != str(envelope.data_classification)
        ):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery data classification header does not match envelope")
        header_message_version = delivery.headers.get("message_version")
        if header_message_version is None or str(header_message_version) != str(envelope.contract_version):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery message version header does not match envelope")
        try:
            self._validate_delivery_retry_policy(payload=payload, max_attempts=self.max_attempts)
            self._validate_delivery_retry_envelope(payload=payload, envelope=envelope)
            self._validate_delivery_producer_lineage(payload=payload, envelope=envelope)
        except PackageARejectDeliveryError:
            await delivery.reject(requeue=False)
            raise
        header_security_epoch_ref = delivery.headers.get("security_epoch_ref")
        envelope_security_epoch_ref = envelope.effective_security_epoch_ref
        payload_security_epoch_ref = payload.get("security_epoch_ref")
        if (
            header_security_epoch_ref is None
            or envelope_security_epoch_ref is None
            or str(header_security_epoch_ref) != str(envelope_security_epoch_ref)
            or str(payload_security_epoch_ref) != str(envelope_security_epoch_ref)
        ):
            await delivery.reject(requeue=False)
            raise PackageARejectDeliveryError("delivery security epoch header does not match envelope")
        try:
            self._validate_delivery_outbox_headers(headers=delivery.headers, envelope=envelope, payload=payload)
        except PackageARejectDeliveryError:
            await delivery.reject(requeue=False)
            raise
        parse_job_id = str(payload["parse_job_id"])
        tenant_id = envelope.tenant_id
        deferred_inbox_error: IngestionPersistenceError | None = None
        try:
            with IngestionUnitOfWork(self.engine) as repo:
                inbox = repo.record_worker_inbox(
                    consumer=self.worker_id,
                    message_id=envelope.message_id,
                    payload=delivery.payload,
                    tenant_id=tenant_id,
                    ordering_key=str(delivery.headers["ordering_key"]),
                    ordering_sequence=int(delivery.headers["ordering_sequence"]),
                )
                if not inbox.processable:
                    if inbox.status != "received":
                        deferred_inbox_error = IngestionPersistenceError(
                            f"Package A inbox delivery is not processable: {inbox.status}"
                        )
                    else:
                        replay = repo.load_parse_job_replay_receipt(parse_job_id=parse_job_id, tenant_id=tenant_id)
                        self._validate_parse_job_replay_receipt(
                            replay=replay,
                            parse_job_id=parse_job_id,
                            tenant_id=tenant_id,
                        )
                        status = self._replay_receipt_status(replay)
                        if status not in {"succeeded", "failed", "cancelled", "dead_letter"}:
                            status = "duplicate"
                        if status == "succeeded":
                            handoff_replay = repo.load_snapshot_handoff_replay_receipt(
                                tenant_id=tenant_id,
                                handoff_idempotency_key=str(replay["handoff_idempotency_key"]),
                            )
                            self._validate_snapshot_handoff_replay_receipt(
                                replay=replay,
                                handoff_replay=handoff_replay,
                            )
                        retry_outbox_event_id = replay.get("outbox_event_id")
                        retry_enqueued_after_domain_commit = False
                        retry_consistency_dead_letter_id = None
                        retry_consistency_failure_code = None
                        if status == "failed":
                            (
                                retry_outbox_event_id,
                                retry_enqueued_after_domain_commit,
                                retry_consistency_dead_letter_id,
                                retry_consistency_failure_code,
                            ) = self._resolve_failed_replay_retry_outbox(
                                repo=repo,
                                replay=replay,
                                envelope=envelope,
                                parse_job_id=parse_job_id,
                                tenant_id=tenant_id,
                            )
                        if retry_consistency_dead_letter_id is not None:
                            worker_receipt = PackageAWorkerReceipt(
                                parse_job_id=parse_job_id,
                                parse_attempt_id=replay.get("parse_attempt_id"),
                                status="dead_letter",
                                acked_after_domain_commit=False,
                                dead_letter_id=retry_consistency_dead_letter_id,
                                failure_code=retry_consistency_failure_code,
                                duplicate_delivery=True,
                            )
                        else:
                            worker_receipt = PackageAWorkerReceipt(
                                parse_job_id=parse_job_id,
                                parse_attempt_id=replay.get("parse_attempt_id"),
                                status=status,
                                acked_after_domain_commit=True,
                                retry_enqueued_after_domain_commit=retry_enqueued_after_domain_commit,
                                indexable_snapshot_id=replay.get("indexable_snapshot_id"),
                                outbox_event_id=retry_outbox_event_id,
                                handoff_idempotency_key=replay.get("handoff_idempotency_key"),
                                outbox_idempotency_key=replay.get("outbox_idempotency_key"),
                                dead_letter_id=replay.get("dead_letter_id"),
                                failure_code=replay.get("failure_code"),
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
        except PackageARejectDeliveryError:
            await delivery.reject(requeue=False)
            raise
        if deferred_inbox_error is not None:
            raise deferred_inbox_error
        await self._settle_delivery_after_domain_commit(
            delivery=delivery,
            worker_receipt=worker_receipt,
        )
        return worker_receipt

    @staticmethod
    def _validate_parse_job_replay_receipt(
        *,
        replay: dict[str, Any],
        parse_job_id: str,
        tenant_id: str,
    ) -> None:
        if str(replay.get("parse_job_id")) != str(parse_job_id):
            raise IngestionPersistenceError("Package A replay receipt mismatch: parse_job_id")
        if str(replay.get("tenant_id")) != str(tenant_id):
            raise IngestionPersistenceError("Package A replay receipt mismatch: tenant_id")
        status = PackageAProductionIngestionRuntime._replay_receipt_status(replay)
        if status not in {"succeeded", "failed", "cancelled", "dead_letter"}:
            return
        if str(replay.get("attempt_status")) != status:
            raise IngestionPersistenceError(
                f"Package A replay receipt mismatch: attempt_status for {status}"
            )
        PackageAProductionIngestionRuntime._require_replay_fields(
            replay,
            ("parse_attempt_id",),
            status=status,
        )
        if status == "succeeded":
            PackageAProductionIngestionRuntime._require_replay_fields(
                replay,
                (
                    "indexable_snapshot_id",
                    "parse_snapshot_id",
                    "document_version_id",
                    "workspace_id",
                    "source_object_id",
                    "quality_decision_id",
                    "outbox_event_id",
                    "handoff_idempotency_key",
                    "outbox_idempotency_key",
                ),
                status=status,
            )
        elif status == "dead_letter":
            PackageAProductionIngestionRuntime._require_replay_fields(
                replay,
                ("dead_letter_id", "failure_code"),
                status=status,
            )
        elif status == "failed":
            PackageAProductionIngestionRuntime._require_replay_fields(
                replay,
                ("failure_code", "attempt_no"),
                status=status,
            )
        else:
            PackageAProductionIngestionRuntime._require_replay_fields(
                replay,
                ("failure_code",),
                status=status,
            )
        if status != "succeeded":
            PackageAProductionIngestionRuntime._forbid_replay_fields(
                replay,
                (
                    "indexable_snapshot_id",
                    "outbox_event_id",
                    "handoff_idempotency_key",
                    "outbox_idempotency_key",
                ),
                status=status,
            )

    @staticmethod
    def _require_replay_fields(
        replay: dict[str, Any],
        field_names: tuple[str, ...],
        *,
        status: str,
    ) -> None:
        for field_name in field_names:
            if replay.get(field_name) in {None, ""}:
                raise IngestionPersistenceError(
                    f"Package A replay receipt incomplete for {status}: {field_name}"
                )

    @staticmethod
    def _forbid_replay_fields(
        replay: dict[str, Any],
        field_names: tuple[str, ...],
        *,
        status: str,
    ) -> None:
        for field_name in field_names:
            if replay.get(field_name) not in {None, ""}:
                raise IngestionPersistenceError(
                    f"Package A replay receipt conflict for {status}: {field_name}"
                )

    @staticmethod
    def _replay_receipt_status(replay: dict[str, Any]) -> str:
        job_status = str(replay.get("job_status"))
        attempt_status = str(replay.get("attempt_status"))
        if job_status not in {"succeeded", "failed", "cancelled", "dead_letter"} and attempt_status == "failed":
            return "failed"
        return job_status

    @staticmethod
    def _validate_snapshot_handoff_replay_receipt(
        *,
        replay: dict[str, Any],
        handoff_replay: dict[str, Any],
    ) -> None:
        PackageAProductionIngestionRuntime._require_replay_fields(
            handoff_replay,
            (
                "snapshot_hash",
                "handoff_envelope_hash",
                "visibility_ref",
                "quality_decision_id",
                "knowledge_handoff_status",
                "outbox_publish_status",
                "outbox_payload_hash",
                "outbox_payload_indexable_snapshot_id",
                "outbox_payload_document_version_id",
                "outbox_payload_quality_decision_id",
                "outbox_payload_idempotency_key",
            ),
            status="snapshot_handoff",
        )
        for field_name in ("indexable_snapshot_id", "outbox_event_id", "handoff_idempotency_key"):
            if str(handoff_replay.get(field_name)) != str(replay.get(field_name)):
                raise IngestionPersistenceError(
                    f"Package A snapshot handoff replay mismatch: {field_name}"
                )
        for field_name in ("parse_snapshot_id", "document_version_id", "quality_decision_id"):
            if str(handoff_replay.get(field_name)) != str(replay.get(field_name)):
                raise IngestionPersistenceError(
                    f"Package A snapshot handoff replay lineage mismatch: {field_name}"
                )
        expected_visibility_ref = f"visibility:{replay['workspace_id']}:{replay['source_object_id']}"
        if str(handoff_replay.get("visibility_ref")) != expected_visibility_ref:
            raise IngestionPersistenceError(
                "Package A snapshot handoff replay lineage mismatch: visibility_ref"
            )
        outbox_payload_fields = {
            "outbox_payload_indexable_snapshot_id": "indexable_snapshot_id",
            "outbox_payload_document_version_id": "document_version_id",
            "outbox_payload_quality_decision_id": "quality_decision_id",
            "outbox_payload_idempotency_key": "handoff_idempotency_key",
        }
        for outbox_field_name, replay_field_name in outbox_payload_fields.items():
            if str(handoff_replay.get(outbox_field_name)) != str(replay.get(replay_field_name)):
                raise IngestionPersistenceError(
                    f"Package A snapshot handoff replay outbox mismatch: {outbox_field_name}"
                )
        if str(handoff_replay.get("knowledge_handoff_status")) in {"blocked", "dead_letter"}:
            raise IngestionPersistenceError(
                "Package A snapshot handoff replay conflict: knowledge_handoff_status"
            )
        if str(handoff_replay.get("outbox_publish_status")) == "dead_letter":
            raise IngestionPersistenceError(
                "Package A snapshot handoff replay conflict: outbox_publish_status"
            )

    def _resolve_failed_replay_retry_outbox(
        self,
        *,
        repo,
        replay: dict[str, Any],
        envelope: CrossModuleEnvelopeV1,
        parse_job_id: str,
        tenant_id: str,
    ) -> tuple[str | None, bool, str | None, str | None]:
        try:
            failed_attempt_no = int(replay["attempt_no"])
        except (TypeError, ValueError) as exc:
            raise IngestionPersistenceError("Package A failed replay receipt invalid: attempt_no") from exc
        next_attempt_no = failed_attempt_no + 1
        retry_outbox_event_id = replay.get("retry_outbox_event_id")
        if retry_outbox_event_id in {None, ""}:
            retry_envelope = self._retry_parse_requested_envelope(
                envelope=envelope,
                context={"parse_job_id": parse_job_id},
                retry_parent_attempt_id=str(replay["parse_attempt_id"]),
                next_attempt_no=next_attempt_no,
            )
            retry_outbox = repo.enqueue_parse_requested(envelope=retry_envelope)
            return retry_outbox.ref, True, None, None
        if self._failed_replay_retry_outbox_matches(
            replay=replay,
            envelope=envelope,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            next_attempt_no=next_attempt_no,
        ):
            return str(retry_outbox_event_id), True, None, None
        failure_code = "retry_outbox_lineage_conflict"
        dead_letter = repo.record_dead_letter(
            dead_letter_id=f"dead-letter:retry-outbox:{replay['parse_attempt_id']}",
            tenant_id=tenant_id,
            parse_job_id=parse_job_id,
            parse_attempt_id=str(replay["parse_attempt_id"]),
            source_ref=parse_job_id,
            failure_code=failure_code,
            retryable=False,
            retry_count=next_attempt_no - 1,
            rabbitmq_dead_letter_ref=f"rabbitmq-dlq:{envelope.message_id}",
            payload={
                "parse_job_id": parse_job_id,
                "parse_attempt_id": replay["parse_attempt_id"],
                "retry_outbox_event_id": retry_outbox_event_id,
                "status": failure_code,
            },
        )
        return None, False, dead_letter.ref, failure_code

    @staticmethod
    def _failed_replay_retry_outbox_matches(
        *,
        replay: dict[str, Any],
        envelope: CrossModuleEnvelopeV1,
        parse_job_id: str,
        tenant_id: str,
        next_attempt_no: int,
    ) -> bool:
        expected_fields = {
            "retry_outbox_event_id": f"outbox:{parse_job_id}:retry:{next_attempt_no}",
            "retry_outbox_tenant_id": tenant_id,
            "retry_outbox_aggregate_id": parse_job_id,
            "retry_outbox_idempotency_key": f"{envelope.idempotency_key}:retry:{next_attempt_no}",
            "retry_outbox_payload_retry_attempt_no": next_attempt_no,
            "retry_outbox_payload_retry_parent_attempt_id": replay["parse_attempt_id"],
            "retry_outbox_payload_retry_parent_message_id": envelope.message_id,
            "retry_outbox_payload_retry_parent_idempotency_key": envelope.idempotency_key,
            "retry_outbox_payload_parse_job_id": parse_job_id,
        }
        if int(replay.get("retry_outbox_count") or 1) != 1:
            return False
        return all(str(replay.get(field_name)) == str(expected) for field_name, expected in expected_fields.items())

    @staticmethod
    async def _settle_delivery_after_domain_commit(
        *,
        delivery: RabbitMQDelivery | AckableDelivery,
        worker_receipt: PackageAWorkerReceipt,
    ) -> None:
        if worker_receipt.status == "dead_letter":
            await delivery.reject(requeue=False)
            return
        if not worker_receipt.acked_after_domain_commit:
            raise IngestionPersistenceError("Package A delivery cannot ACK before domain commit receipt")
        await delivery.ack()

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
        self._validate_delivery_lineage(payload=payload, context=context)
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
        cancel_reason = self._cancel_reason(payload=payload, envelope=envelope)
        if cancel_reason is not None:
            repo.fail_parse_attempt(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                status="cancelled",
                failure_code=cancel_reason,
            )
            return PackageAWorkerReceipt(
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                status="cancelled",
                acked_after_domain_commit=True,
                failure_code=cancel_reason,
            )
        repo.renew_parse_attempt_lease(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=self.worker_id,
            fencing_token=fencing_token,
            lease_ttl_seconds=self.lease_ttl_seconds,
        )
        try:
            source_bytes = self._read_and_verify_object(context)
        except PackageAObjectVerificationError as exc:
            repo.fail_parse_attempt(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                status="dead_letter",
                failure_code=exc.failure_code,
            )
            dead_letter = repo.record_dead_letter(
                dead_letter_id=f"dead-letter:{parse_attempt_id}",
                tenant_id=tenant_id,
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                source_ref=str(context["storage_uri"]),
                failure_code=exc.failure_code,
                retryable=False,
                retry_count=int(context["attempt_count"]) + 1,
                rabbitmq_dead_letter_ref=f"rabbitmq-dlq:{envelope.message_id}",
                payload={"parse_job_id": parse_job_id, "status": "object_verification_failed"},
            )
            return PackageAWorkerReceipt(
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                status="dead_letter",
                acked_after_domain_commit=False,
                dead_letter_id=dead_letter.ref,
                failure_code=exc.failure_code,
            )
        repo.heartbeat_parse_attempt_lease(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=self.worker_id,
            fencing_token=fencing_token,
        )
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
        repo.heartbeat_parse_attempt_lease(
            parse_attempt_id=parse_attempt_id,
            parse_job_id=parse_job_id,
            tenant_id=tenant_id,
            worker_id=self.worker_id,
            fencing_token=fencing_token,
        )
        try:
            self._validate_parser_identity(
                result=result,
                snapshot=snapshot,
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
            )
        except PackageAParserIdentityError as exc:
            repo.fail_parse_attempt(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                status="dead_letter",
                failure_code=exc.failure_code,
            )
            dead_letter = repo.record_dead_letter(
                dead_letter_id=f"dead-letter:{parse_attempt_id}",
                tenant_id=tenant_id,
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                source_ref=str(context["storage_uri"]),
                failure_code=exc.failure_code,
                retryable=False,
                retry_count=int(context["attempt_count"]) + 1,
                rabbitmq_dead_letter_ref=f"rabbitmq-dlq:{envelope.message_id}",
                payload={"parse_job_id": parse_job_id, "status": "parser_identity_mismatch"},
            )
            return PackageAWorkerReceipt(
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                status="dead_letter",
                acked_after_domain_commit=False,
                dead_letter_id=dead_letter.ref,
                failure_code=exc.failure_code,
            )
        if result.status != "succeeded" or result.document is None:
            retryable = bool(result.failure and result.failure.retryable)
            terminal_status = self._failure_terminal_status(
                retryable=retryable,
                prior_attempt_count=int(context["attempt_count"]),
            )
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
                    retry_parent_attempt_id=parse_attempt_id,
                    next_attempt_no=int(context["attempt_count"]) + 2,
                )
                retry_outbox = repo.enqueue_parse_requested(envelope=retry_envelope)
                retry_outbox_id = retry_outbox.ref
                repo.update_parse_job_status(parse_job_id=parse_job_id, tenant_id=tenant_id, status="queued")
            return PackageAWorkerReceipt(
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                status=terminal_status,
                acked_after_domain_commit=terminal_status != "dead_letter",
                retry_enqueued_after_domain_commit=terminal_status == "failed",
                outbox_event_id=retry_outbox_id,
                dead_letter_id=dead_letter_id,
                failure_code=result.failure.failure_classification if result.failure else result.status,
            )

        quality_gate, review_task = self.review_runtime.evaluate(
            document=result.document,
            parse_snapshot=snapshot,
            security_epoch_ref=str(context["security_epoch_ref"]),
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
            decision="publish" if HumanReviewRuntime.can_publish_snapshot(gate=quality_gate) else "human_review",
            review_task_ref=quality_gate.review_task_id,
        )
        if review_task is not None:
            repo.record_review_task(
                review_task_id=review_task.review_task_id,
                tenant_id=tenant_id,
                parse_snapshot_id=snapshot_receipt.ref,
                quality_decision_id=quality.ref,
                document_version_id=str(context["document_version_id"]),
                workspace_id=review_task.workspace_id,
                reviewer_scope=review_task.reviewer_scope,
                security_epoch_ref=review_task.security_epoch_ref,
                status=review_task.status,
                reason=review_task.reason,
                decision_hash=review_task.decision_hash,
                expires_at=review_task.expires_at,
            )
        if not HumanReviewRuntime.can_publish_snapshot(gate=quality_gate):
            repo.fail_parse_attempt(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                status="failed",
                failure_code=self._quality_failure_code(quality_gate),
            )
            return PackageAWorkerReceipt(
                parse_job_id=parse_job_id,
                parse_attempt_id=parse_attempt_id,
                status="failed",
                acked_after_domain_commit=True,
                failure_code=self._quality_failure_code(quality_gate),
            )
        visibility_ref = f"visibility:{context['workspace_id']}:{context['source_object_id']}"
        indexable_snapshot, snapshot_outbox = self.handoff_runtime.create_snapshot(
            document=result.document,
            parse_snapshot=snapshot,
            quality_gate=quality_gate,
            visibility_ref=visibility_ref,
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
            visibility_ref=visibility_ref,
            payload=indexable_snapshot.payload,
            handoff_idempotency_key=indexable_snapshot.idempotency_key,
        )
        outbox = repo.enqueue_outbox_event(
            outbox_event_id=snapshot_outbox.outbox_event_id,
            tenant_id=tenant_id,
            aggregate_ref=indexable.ref,
            event_type="ingestion.indexable_snapshot.ready",
            payload=handoff_payload,
            idempotency_key=snapshot_outbox.idempotency_key,
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
            handoff_idempotency_key=indexable_snapshot.idempotency_key,
            outbox_idempotency_key=snapshot_outbox.idempotency_key,
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
            "filename": command.filename,
            "mime_type": command.mime_type,
            "declared_format": self._declared_format(command.mime_type, command.filename),
            "classification_ref": command.classification_ref,
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
            deadline_at=command.deadline_at,
            payload=payload,
            payload_hash=canonical_sha256(payload),
            payload_schema_hash=canonical_sha256({"schema": "zuno.ingestion.parse.requested.v1"}),
        )

    def _retry_parse_requested_envelope(
        self,
        *,
        envelope: CrossModuleEnvelopeV1,
        context: dict[str, Any],
        retry_parent_attempt_id: str,
        next_attempt_no: int,
    ) -> CrossModuleEnvelopeV1:
        now = datetime.now(timezone.utc)
        retry_payload = dict(envelope.payload or {})
        retry_payload.update(
            {
                "retry_attempt_no": next_attempt_no,
                "retry_parent_attempt_id": retry_parent_attempt_id,
                "retry_parent_message_id": envelope.message_id,
                "retry_parent_idempotency_key": envelope.idempotency_key,
            }
        )
        return envelope.model_copy(
            update={
                "message_id": f"outbox:{context['parse_job_id']}:retry:{next_attempt_no}",
                "producer_module": "ingestion.parser_worker",
                "consumer_module": "ingestion.parser_worker",
                "causation_id": envelope.message_id,
                "idempotency_key": f"{envelope.idempotency_key}:retry:{next_attempt_no}",
                "occurred_at": now,
                "created_at": now,
                "payload": retry_payload,
                "payload_hash": canonical_sha256(retry_payload),
            }
        )

    def _failure_terminal_status(self, *, retryable: bool, prior_attempt_count: int) -> str:
        if prior_attempt_count < 0:
            raise ValueError("prior_attempt_count must not be negative")
        current_attempt_number = prior_attempt_count + 1
        if retryable and current_attempt_number < self.max_attempts:
            return "failed"
        return "dead_letter"

    @staticmethod
    def _validate_delivery_retry_policy(*, payload: dict[str, Any], max_attempts: int) -> None:
        try:
            payload_max_attempts = int(payload.get("max_attempts"))
        except (TypeError, ValueError) as exc:
            raise PackageARejectDeliveryError("delivery retry policy mismatch: max_attempts") from exc
        if payload_max_attempts < 1 or payload_max_attempts != max_attempts:
            raise PackageARejectDeliveryError("delivery retry policy mismatch: max_attempts")
        retry_attempt_no = payload.get("retry_attempt_no")
        if retry_attempt_no is not None:
            try:
                if int(retry_attempt_no) > max_attempts:
                    raise ValueError
            except (TypeError, ValueError) as exc:
                raise PackageARejectDeliveryError("delivery retry policy mismatch: retry_attempt_no") from exc

    @staticmethod
    def _validate_delivery_retry_envelope(*, payload: dict[str, Any], envelope: CrossModuleEnvelopeV1) -> None:
        retry_fields = {
            "retry_attempt_no",
            "retry_parent_attempt_id",
            "retry_parent_message_id",
            "retry_parent_idempotency_key",
        }
        present_retry_fields = {field_name for field_name in retry_fields if payload.get(field_name) is not None}
        if not present_retry_fields:
            return
        missing_retry_fields = retry_fields - present_retry_fields
        if missing_retry_fields:
            raise PackageARejectDeliveryError("delivery retry envelope mismatch: retry fields")
        try:
            retry_attempt_no = int(payload["retry_attempt_no"])
        except (TypeError, ValueError) as exc:
            raise PackageARejectDeliveryError("delivery retry envelope mismatch: retry_attempt_no") from exc
        if retry_attempt_no < 2:
            raise PackageARejectDeliveryError("delivery retry envelope mismatch: retry_attempt_no")
        expected_message_id = f"outbox:{payload['parse_job_id']}:retry:{retry_attempt_no}"
        expected_idempotency_key = f"{payload['retry_parent_idempotency_key']}:retry:{retry_attempt_no}"
        if envelope.message_id != expected_message_id:
            raise PackageARejectDeliveryError("delivery retry envelope mismatch: message_id")
        if envelope.causation_id != payload["retry_parent_message_id"]:
            raise PackageARejectDeliveryError("delivery retry envelope mismatch: causation_id")
        if envelope.idempotency_key != expected_idempotency_key:
            raise PackageARejectDeliveryError("delivery retry envelope mismatch: idempotency_key")

    @staticmethod
    def _validate_delivery_producer_lineage(*, payload: dict[str, Any], envelope: CrossModuleEnvelopeV1) -> None:
        retry_fields = {
            "retry_attempt_no",
            "retry_parent_attempt_id",
            "retry_parent_message_id",
            "retry_parent_idempotency_key",
        }
        is_retry_delivery = any(payload.get(field_name) is not None for field_name in retry_fields)
        expected_producer = (
            PACKAGE_A_PARSE_RETRY_PRODUCER_MODULE
            if is_retry_delivery
            else PACKAGE_A_PARSE_INITIAL_PRODUCER_MODULE
        )
        if envelope.producer_module != expected_producer:
            raise PackageARejectDeliveryError("delivery producer lineage mismatch")

    @staticmethod
    def _validate_delivery_outbox_headers(
        *,
        headers: dict[str, Any],
        envelope: CrossModuleEnvelopeV1,
        payload: dict[str, Any],
    ) -> None:
        ordering_key = headers.get("ordering_key")
        ordering_sequence = headers.get("ordering_sequence")
        if str(ordering_key) != str(envelope.aggregate_id):
            raise PackageARejectDeliveryError("delivery outbox header mismatch: ordering_key")
        try:
            if int(ordering_sequence) < 1:
                raise ValueError
        except (TypeError, ValueError) as exc:
            raise PackageARejectDeliveryError("delivery outbox header mismatch: ordering_sequence") from exc
        counter_names = ("outbox_publish_attempt", "outbox_retry_count", "outbox_replay_count")
        try:
            publish_attempt = int(headers.get("outbox_publish_attempt"))
            retry_count = int(headers.get("outbox_retry_count"))
            replay_count = int(headers.get("outbox_replay_count"))
        except (TypeError, ValueError) as exc:
            raise PackageARejectDeliveryError("delivery outbox header mismatch: publish counters") from exc
        if publish_attempt < 1 or retry_count < 0 or replay_count < 0:
            raise PackageARejectDeliveryError("delivery outbox header mismatch: publish counters")
        if any(headers.get(name) is None for name in counter_names):
            raise PackageARejectDeliveryError("delivery outbox header mismatch: publish counters")
        if headers.get("replayed_from_dlq") is True and replay_count < 1:
            raise PackageARejectDeliveryError("delivery outbox header mismatch: replay_count")
        retry_attempt_no = payload.get("retry_attempt_no")
        expected_retry_count = 0
        if retry_attempt_no is not None:
            try:
                expected_retry_count = int(retry_attempt_no) - 1
            except (TypeError, ValueError) as exc:
                raise PackageARejectDeliveryError("delivery outbox header mismatch: retry_count") from exc
        if retry_count != expected_retry_count:
            raise PackageARejectDeliveryError("delivery outbox header mismatch: retry_count")

    @staticmethod
    def _validate_delivery_lineage(*, payload: dict[str, Any], context: dict[str, Any]) -> None:
        expected_fields = {
            "tenant_id": context["tenant_id"],
            "workspace_id": context["workspace_id"],
            "source_object_id": context["source_object_id"],
            "document_version_id": context["document_version_id"],
            "parse_plan_id": context["parse_plan_id"],
            "parse_job_id": context["parse_job_id"],
            "object_ref": context["storage_uri"],
            "object_manifest_ref": context["object_manifest_ref"],
            "content_hash": context["source_sha256"],
            "mime_type": context["mime_type"],
            "filename": context["filename"],
            "declared_format": context["declared_format"],
            "classification_ref": context["classification_ref"],
            "parser_policy_ref": context["parser_policy_ref"],
            "quality_policy_ref": context["quality_policy_ref"],
            "security_decision_ref": context["security_decision_ref"],
            "security_epoch_ref": context["security_epoch_ref"],
        }
        for field_name, expected_value in expected_fields.items():
            if str(payload.get(field_name)) != str(expected_value):
                raise PackageARejectDeliveryError(f"delivery lineage mismatch: {field_name}")
        try:
            payload_size = int(payload.get("size_bytes", -1))
            context_size = int(context["size_bytes"])
        except (TypeError, ValueError) as exc:
            raise PackageARejectDeliveryError("delivery lineage mismatch: size_bytes") from exc
        if payload_size != context_size:
            raise PackageARejectDeliveryError("delivery lineage mismatch: size_bytes")
        retry_fields = {
            "retry_attempt_no",
            "retry_parent_attempt_id",
            "retry_parent_message_id",
            "retry_parent_idempotency_key",
        }
        present_retry_fields = {field_name for field_name in retry_fields if payload.get(field_name) is not None}
        if present_retry_fields:
            missing_retry_fields = retry_fields - present_retry_fields
            if missing_retry_fields:
                raise PackageARejectDeliveryError("delivery retry lineage mismatch: retry fields")
            try:
                retry_attempt_no = int(payload["retry_attempt_no"])
                expected_attempt_no = int(context["attempt_count"]) + 1
            except (TypeError, ValueError) as exc:
                raise PackageARejectDeliveryError("delivery retry lineage mismatch: retry_attempt_no") from exc
            if retry_attempt_no != expected_attempt_no:
                raise PackageARejectDeliveryError("delivery retry lineage mismatch: retry_attempt_no")
            if retry_attempt_no < 2:
                raise PackageARejectDeliveryError("delivery retry lineage mismatch: retry_attempt_no")
            if str(payload["retry_parent_attempt_id"]) != str(context.get("latest_attempt_id")):
                raise PackageARejectDeliveryError("delivery retry lineage mismatch: retry_parent_attempt_id")
            if str(context.get("latest_attempt_status")) != "failed":
                raise PackageARejectDeliveryError("delivery retry lineage mismatch: retry_parent_attempt_status")

    @staticmethod
    def _cancel_reason(*, payload: dict[str, Any], envelope: CrossModuleEnvelopeV1) -> str | None:
        if bool(payload.get("cancel_requested")):
            return "cancel_requested"
        if envelope.deadline_at is not None and envelope.deadline_at <= datetime.now(timezone.utc):
            return "deadline_expired"
        return None

    def _read_and_verify_object(self, context: dict[str, Any]) -> bytes:
        parsed = urlparse(str(context["storage_uri"]))
        if parsed.scheme != "s3" or not parsed.netloc or not parsed.path:
            raise PackageAObjectVerificationError(
                "Package A worker requires s3:// ObjectRef",
                failure_code="invalid_object_ref",
            )
        object_name = parsed.path.lstrip("/")
        expected_prefix = f"{context['tenant_id']}/{context['workspace_id']}/"
        if not object_name.startswith(expected_prefix):
            raise PackageAObjectVerificationError(
                "SourceObject ObjectRef is outside tenant/workspace scope",
                failure_code="object_ref_scope_mismatch",
            )
        source_status = str(context["source_status"])
        if source_status != "committed":
            failure_code = self._source_visibility_failure_code(source_status)
            raise PackageAObjectVerificationError(
                f"SourceObject is not visible for parsing: {source_status}",
                failure_code=failure_code,
            )
        content = self.object_store.store.read_object(bucket=parsed.netloc, object_name=object_name)
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != context["source_sha256"] or len(content) != int(context["size_bytes"]):
            raise PackageAObjectVerificationError(
                "SourceObject bytes do not match PostgreSQL lineage facts",
                failure_code="object_bytes_mismatch",
            )
        return content

    @staticmethod
    def _source_visibility_failure_code(source_status: str) -> str:
        if source_status in {"revoked", "visibility_revoked"}:
            return "object_visibility_revoked"
        if source_status in {"deleted", "physically_deleted"}:
            return "object_deleted"
        return "object_not_visible"

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

    @staticmethod
    def _quality_failure_code(quality_gate) -> str:
        return f"quality_gate_{str(quality_gate.verdict).lower()}"

    @staticmethod
    def _build_quality_gate_result(*, quality_row: dict[str, Any], review_task: ReviewTask) -> QualityGateResult:
        verdict_map = {
            "publish": "PASS",
            "human_review": "REVIEW",
            "block": "BLOCK",
            "fallback": "FALLBACK",
        }
        verdict = verdict_map.get(str(quality_row["decision"]), "REVIEW")
        return QualityGateResult(
            quality_decision_id=str(quality_row["quality_decision_id"]),
            parse_snapshot_id=str(quality_row["parse_snapshot_id"]),
            verdict=verdict,
            metrics=[
                QualityMetric(
                    name="coverage",
                    value=float(quality_row["coverage_score"]),
                    threshold=0.0,
                    passed=True,
                    reason="persisted_quality_gate_coverage",
                ),
                QualityMetric(
                    name="confidence",
                    value=float(quality_row["confidence_score"]),
                    threshold=0.0,
                    passed=True,
                    reason="persisted_quality_gate_confidence",
                ),
            ],
            review_task_id=review_task.review_task_id,
            decision_hash=str(quality_row["decision_hash"]),
        )

    @staticmethod
    def _build_review_resume_snapshot(*, parse_snapshot_row: dict[str, Any], context: dict[str, Any]) -> ParseJobSnapshot:
        return ParseJobSnapshot.model_validate(
            {
                "job_id": str(parse_snapshot_row["parse_job_id"]),
                "status": str(parse_snapshot_row["status"]),
                "document_id": str(context["source_object_id"]),
                "workspace_id": str(context["workspace_id"]),
                "source_uri": str(context["storage_uri"]),
                "mime_type": str(context["mime_type"]),
                "parser_id": str(parse_snapshot_row["parser_id"]),
                "parser_format": str(context["declared_format"]),
                "attempt": int(context["attempt_count"] or 1),
                "attempt_count": int(context["attempt_count"] or 1),
                "parse_plan_id": str(context["parse_plan_id"]),
                "parse_attempt_id": str(parse_snapshot_row["parse_attempt_id"]),
                "parse_idempotency_key": str(context["idempotency_key"]),
                "retryable": False,
                "source_provenance": {
                    "source_object_id": str(context["source_object_id"]),
                    "document_version_id": str(context["document_version_id"]),
                },
                "adapter_boundary": {"resume_mode": "approved_review"},
            }
        )

    @staticmethod
    def _validate_parser_identity(*, result, snapshot, parse_job_id: str, parse_attempt_id: str) -> None:
        if str(result.job_id) != parse_job_id:
            raise PackageAParserIdentityError(
                "Parser Gateway result job_id does not match PostgreSQL ParseJob",
                failure_code="parser_job_identity_mismatch",
            )
        if result.status == "succeeded" and str(snapshot.parse_attempt_id) != parse_attempt_id:
            raise PackageAParserIdentityError(
                "Parser Gateway snapshot parse_attempt_id does not match PostgreSQL ParseAttempt",
                failure_code="parser_attempt_identity_mismatch",
            )


__all__ = [
    "PackageAProductionIngestionRuntime",
    "PACKAGE_A_PARSE_CONTRACT_NAME",
    "PACKAGE_A_PARSE_CONSUMER_MODULE",
    "PACKAGE_A_PARSE_REQUESTED_TOPIC",
    "PackageAObjectVerificationError",
    "PackageAParserIdentityError",
    "PackageARejectDeliveryError",
    "PackageAUploadCommand",
    "PackageAUploadReceipt",
    "PackageAWorkerReceipt",
]
