from __future__ import annotations

from typing import Any, Callable
from uuid import uuid4

from zuno.agent.contracts import (
    DeadLetterRecord,
    IndexWorkerResult,
    OutboxEvent,
    ParseAttempt,
    ParseJobStatus,
    ParserDependencyProbe,
    ParserWorkerResult,
    QueueBackendResult,
    QueueMessage,
    ReconcilerFinding,
)
from zuno.knowledge.indexing import IndexJobManifest, KnowledgeIndexRuntime
from zuno.knowledge.ingestion import CanonicalDocumentIR, ParseDocumentRequest, ParseGateway
from zuno.knowledge.storage import (
    IndexChunkRecord,
    LocalObjectStore,
    ParseJobRecord,
    SQLiteDurableIngestionStore,
    SourceObjectRecord,
    WorkspaceFileRecord,
)


class QueueDeliveryReceipt(QueueBackendResult):
    acked_after_domain_commit: bool = False
    domain_commit_ref: str | None = None
    retryable: bool = False
    dead_letter_id: str | None = None
    attempt: int = 0


class LocalQueueBackend:
    """In-process queue boundary with ack/fail/dead-letter/replay semantics."""

    def __init__(self) -> None:
        self._messages: dict[str, QueueMessage] = {}
        self._order: list[str] = []
        self._dead_letters: dict[str, DeadLetterRecord] = {}
        self._dead_letter_topics: dict[str, str] = {}
        self._dead_letter_attempts: dict[str, int] = {}
        self._outbox: list[OutboxEvent] = []

    def enqueue(
        self,
        *,
        topic: str,
        payload: dict,
        idempotency_key: str,
        trace_id: str | None = None,
    ) -> QueueMessage:
        existing = self._find_by_idempotency_key(idempotency_key)
        if existing is not None and existing.status in {"queued", "consumed"}:
            return existing
        message = QueueMessage(
            message_id=f"msg_{uuid4().hex[:12]}",
            topic=topic,
            payload=dict(payload),
            idempotency_key=idempotency_key,
            status="queued",
            attempt=0,
            trace_id=trace_id,
        )
        self._messages[message.message_id] = message
        self._order.append(message.message_id)
        return message

    def consume(self, topic: str) -> QueueMessage | None:
        for message_id in self._order:
            message = self._messages[message_id]
            if message.topic == topic and message.status == "queued":
                consumed = message.model_copy(update={"status": "consumed"})
                self._messages[message_id] = consumed
                return consumed
        return None

    def requeue(self, message: QueueMessage) -> QueueMessage:
        queued = message.model_copy(update={"status": "queued"})
        self._messages[message.message_id] = queued
        if message.message_id not in self._order:
            self._order.append(message.message_id)
        return queued

    def ack(self, message_id: str) -> QueueMessage:
        message = self._require_message(message_id)
        acked = message.model_copy(update={"status": "acked"})
        self._messages[message_id] = acked
        return acked

    def fail(
        self,
        message_id: str,
        *,
        reason: str,
        retryable: bool,
    ) -> DeadLetterRecord | QueueMessage:
        message = self._require_message(message_id)
        if retryable:
            retried = message.model_copy(update={"status": "queued", "attempt": message.attempt + 1})
            self._messages[message_id] = retried
            return retried

        dead_letter = DeadLetterRecord(
            dead_letter_id=f"dead_{uuid4().hex[:12]}",
            source_message_id=message.message_id,
            reason=reason,
            retryable=False,
            payload=dict(message.payload),
        )
        self._dead_letters[dead_letter.dead_letter_id] = dead_letter
        self._dead_letter_topics[dead_letter.dead_letter_id] = message.topic
        self._dead_letter_attempts[dead_letter.dead_letter_id] = message.attempt
        self._messages[message_id] = message.model_copy(update={"status": "dead_letter"})
        return dead_letter

    def ack_after_domain_commit(
        self,
        message: QueueMessage,
        *,
        commit: Callable[[], str],
        max_attempts: int = 3,
    ) -> QueueDeliveryReceipt:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        try:
            domain_commit_ref = commit()
        except Exception as exc:
            if message.attempt + 1 < max_attempts:
                retried = self.fail(
                    message.message_id,
                    reason=f"domain_commit_failed:{type(exc).__name__}",
                    retryable=True,
                )
                assert isinstance(retried, QueueMessage)
                return QueueDeliveryReceipt(
                    ok=False,
                    message_id=retried.message_id,
                    status=retried.status,
                    error=f"domain_commit_failed:{type(exc).__name__}",
                    retryable=True,
                    attempt=retried.attempt,
                )
            dead_letter = self.fail(
                message.message_id,
                reason=f"retry_exhausted:domain_commit_failed:{type(exc).__name__}",
                retryable=False,
            )
            assert isinstance(dead_letter, DeadLetterRecord)
            return QueueDeliveryReceipt(
                ok=False,
                message_id=message.message_id,
                status="dead_letter",
                error=dead_letter.reason,
                retryable=False,
                dead_letter_id=dead_letter.dead_letter_id,
                attempt=message.attempt,
            )
        acked = self.ack(message.message_id)
        return QueueDeliveryReceipt(
            ok=True,
            message_id=acked.message_id,
            status=acked.status,
            acked_after_domain_commit=True,
            domain_commit_ref=domain_commit_ref,
            attempt=acked.attempt,
        )

    def dead_letters(self) -> list[DeadLetterRecord]:
        return list(self._dead_letters.values())

    def replay_dead_letter(self, dead_letter_id: str) -> QueueMessage:
        dead_letter = self._dead_letters[dead_letter_id]
        topic = self._dead_letter_topics[dead_letter_id]
        attempt = self._dead_letter_attempts[dead_letter_id] + 1
        message = QueueMessage(
            message_id=f"msg_{uuid4().hex[:12]}",
            topic=topic,
            payload=dict(dead_letter.payload),
            idempotency_key=f"replay:{dead_letter.source_message_id}:{attempt}",
            status="queued",
            attempt=attempt,
        )
        self._messages[message.message_id] = message
        self._order.append(message.message_id)
        return message

    def record_file_status(
        self,
        *,
        file_id: str,
        status: str,
        trace_id: str | None = None,
        details: dict | None = None,
    ) -> OutboxEvent:
        event = OutboxEvent(
            event_id=f"outbox_{uuid4().hex[:12]}",
            aggregate_id=file_id,
            topic="file_status_changed",
            payload={"file_id": file_id, "status": status, **(details or {})},
            published=False,
        )
        if trace_id:
            event.payload["trace_id"] = trace_id
        self._outbox.append(event)
        return event

    def outbox_events(self, aggregate_id: str | None = None) -> list[OutboxEvent]:
        if aggregate_id is None:
            return list(self._outbox)
        return [event for event in self._outbox if event.aggregate_id == aggregate_id]

    def _find_by_idempotency_key(self, idempotency_key: str) -> QueueMessage | None:
        for message in self._messages.values():
            if message.idempotency_key == idempotency_key:
                return message
        return None

    def _require_message(self, message_id: str) -> QueueMessage:
        try:
            return self._messages[message_id]
        except KeyError as exc:
            raise KeyError(f"queue message not found: {message_id}") from exc


class RabbitMQQueueBackend:
    """Target boundary: RabbitMQ is not required for local PHASE03 tests."""

    def dependency_probe(self) -> ParserDependencyProbe:
        return ParserDependencyProbe(
            provider_id="rabbitmq",
            capability="queue_backend",
            status="target_blocked",
            blocked_reason="RabbitMQ is a production target and is not configured for the local baseline.",
            diagnostics={"external_service_required": True, "local_fallback": "LocalQueueBackend"},
        )

    def enqueue(
        self,
        *,
        topic: str,
        payload: dict,
        idempotency_key: str,
        trace_id: str | None = None,
    ) -> QueueBackendResult:
        probe = self.dependency_probe()
        return QueueBackendResult(
            ok=False,
            message_id=None,
            status="target_blocked",
            dependency_probe=probe,
            error=probe.blocked_reason,
        )


class RedisRuntimeStateBoundary:
    """Target boundary for Redis runtime state with explicit local fallback."""

    local_fallback_enabled = True

    def dependency_probe(self) -> ParserDependencyProbe:
        return ParserDependencyProbe(
            provider_id="redis",
            capability="runtime_state",
            status="target_blocked",
            blocked_reason="Redis runtime state is a production target; local in-process state is active.",
            diagnostics={"external_service_required": True, "local_fallback": "in_process_state"},
        )


class ParserWorker:
    def __init__(
        self,
        *,
        store: SQLiteDurableIngestionStore,
        object_store: LocalObjectStore,
        queue: LocalQueueBackend,
    ) -> None:
        self.store = store
        self.object_store = object_store
        self.queue = queue

    def run_once(self) -> ParserWorkerResult | None:
        message = self.queue.consume("parse_requested")
        if message is None:
            return None

        payload = dict(message.payload)
        file_id = str(payload["file_id"])
        source_id = str(payload["source_id"])
        knowledge_space_id = str(payload["knowledge_space_id"])
        trace_id = payload.get("trace_id") or message.trace_id
        durable_file = self.store.get_workspace_file(file_id)
        source_object = self.store.get_source_object(source_id)

        self.queue.record_file_status(file_id=file_id, status="queued", trace_id=trace_id)
        _save_file_status(self.store, durable_file, parse_status="queued")
        self.queue.record_file_status(file_id=file_id, status="parsing", trace_id=trace_id)
        _save_file_status(self.store, durable_file, parse_status="parsing")

        request = ParseDocumentRequest(
            document_id=file_id,
            source_id=source_object.source_id,
            workspace_id=source_object.workspace_id,
            source_uri=source_object.storage_uri,
            mime_type=source_object.mime_type,
            source_bytes=self.object_store.read_bytes(source_object),
            hash=source_object.source_sha256,
            acl_scope=source_object.acl_scope,
            sensitivity_tags=list(source_object.sensitivity_tags),
        )
        parse_job = ParseGateway.submit_parse_job(request)
        parse_snapshot = ParseGateway.get_job_snapshot(parse_job.job_id)
        document_version_id = parse_snapshot.source_provenance.get("document_version_id")
        parser_version = (
            parse_job.document.metadata.parser_version
            if parse_job.document is not None
            else request.parser_version
        )
        self.store.create_parse_job(
            ParseJobRecord(
                parse_job_id=parse_job.job_id,
                workspace_id=source_object.workspace_id,
                file_id=file_id,
                source_id=source_object.source_id,
                status=parse_job.status,
                parser_id=parse_snapshot.parser_id,
                parser_version=parser_version,
                parse_idempotency_key=parse_snapshot.parse_idempotency_key,
                attempt_count=parse_snapshot.attempt_count,
                document_version_id=document_version_id,
                blocked_reason=parse_snapshot.blocked_reason,
                failure_reason=parse_snapshot.failure_reason,
            )
        )
        self.store.save_parse_snapshot(parse_snapshot)

        if parse_job.status == "succeeded" and parse_job.document is not None:
            document_record = self.store.save_document_version(parse_job.document)
            document_version_id = document_record.document_version_id
            requires_review = any(
                bool(block.metadata.get("requires_human_review"))
                for block in parse_job.document.blocks
            )
            if requires_review:
                _save_file_status(
                    self.store,
                    durable_file,
                    parse_status="review_pending",
                    latest_parse_job_id=parse_job.job_id,
                    latest_document_version_id=document_version_id,
                )
                self.queue.record_file_status(
                    file_id=file_id,
                    status="review_pending",
                    trace_id=trace_id,
                    details={"reason": "quality_review_required"},
                )
                self.queue.ack(message.message_id)
                return ParserWorkerResult(
                    parse_job_id=parse_job.job_id,
                    status=ParseJobStatus.SUCCEEDED,
                    document_version_id=document_version_id,
                    parse_attempt=_parse_attempt(parse_snapshot),
                    diagnostics=[
                        *[diagnostic.model_dump() for diagnostic in parse_job.diagnostics],
                        {"code": "review_pending", "reason": "quality_review_required"},
                    ],
                )
            _save_file_status(
                self.store,
                durable_file,
                parse_status="parsed",
                latest_parse_job_id=parse_job.job_id,
                latest_document_version_id=document_version_id,
            )
            self.queue.record_file_status(file_id=file_id, status="parsed", trace_id=trace_id)
            self.queue.enqueue(
                topic="index_requested",
                payload={
                    "workspace_id": source_object.workspace_id,
                    "file_id": file_id,
                    "source_id": source_object.source_id,
                    "knowledge_space_id": knowledge_space_id,
                    "parse_job_id": parse_job.job_id,
                    "document_version_id": document_version_id,
                    "trace_id": trace_id,
                },
                idempotency_key=f"index:{knowledge_space_id}:{document_version_id}",
                trace_id=trace_id,
            )
            self.queue.ack(message.message_id)
            return ParserWorkerResult(
                parse_job_id=parse_job.job_id,
                status=ParseJobStatus.SUCCEEDED,
                document_version_id=document_version_id,
                parse_attempt=_parse_attempt(parse_snapshot),
                diagnostics=[diagnostic.model_dump() for diagnostic in parse_job.diagnostics],
            )

        final_status = "blocked" if parse_job.status == "blocked" else "failed"
        _save_file_status(
            self.store,
            durable_file,
            parse_status=final_status,
            latest_parse_job_id=parse_job.job_id,
        )
        self.queue.record_file_status(
            file_id=file_id,
            status=final_status,
            trace_id=trace_id,
            details={"blocked_reason": parse_snapshot.blocked_reason},
        )
        self.queue.ack(message.message_id)
        return ParserWorkerResult(
            parse_job_id=parse_job.job_id,
            status=ParseJobStatus(parse_job.status),
            document_version_id=document_version_id,
            parse_attempt=_parse_attempt(parse_snapshot),
            blocked_reason=parse_snapshot.blocked_reason,
            diagnostics=[diagnostic.model_dump() for diagnostic in parse_job.diagnostics],
        )


class IndexWorker:
    def __init__(
        self,
        *,
        store: SQLiteDurableIngestionStore,
        queue: LocalQueueBackend,
        index_runtime: KnowledgeIndexRuntime | None = None,
    ) -> None:
        self.store = store
        self.queue = queue
        self.index_runtime = index_runtime or KnowledgeIndexRuntime()

    def run_once(self) -> IndexWorkerResult | None:
        message = self.queue.consume("index_requested")
        if message is None:
            return None

        payload = dict(message.payload)
        file_id = str(payload["file_id"])
        knowledge_space_id = str(payload["knowledge_space_id"])
        document_version_id = str(payload["document_version_id"])
        parse_job_id = str(payload["parse_job_id"])
        trace_id = payload.get("trace_id") or message.trace_id
        durable_file = self.store.get_workspace_file(file_id)
        document_record = self.store.get_document_version(document_version_id)
        document = CanonicalDocumentIR.model_validate(document_record.ir_json)
        parse_snapshot = self.store.get_parse_snapshot(parse_job_id)

        self.queue.record_file_status(file_id=file_id, status="indexing", trace_id=trace_id)
        _save_file_status(self.store, durable_file, parse_status="indexing")
        self.index_runtime.create_knowledge_space(
            knowledge_space_id=knowledge_space_id,
            workspace_id=document.metadata.workspace_id,
        )
        index_job = self.index_runtime.index_document(
            knowledge_space_id,
            document,
            targets=["bm25", "vector", "graph"],
            parse_job_snapshot=parse_snapshot,
        )
        self.store.save_index_manifest(index_job)
        chunks = _index_chunks_for_manifest(
            index_runtime=self.index_runtime,
            index_job=index_job,
            knowledge_space_id=knowledge_space_id,
            query="\n".join(block.text for block in document.blocks),
        )
        for chunk in chunks:
            self.store.save_index_chunk(chunk)
        _save_file_status(
            self.store,
            durable_file,
            parse_status="indexed",
            latest_parse_job_id=parse_job_id,
            latest_document_version_id=document_version_id,
        )
        self.queue.record_file_status(file_id=file_id, status="indexed", trace_id=trace_id)
        self.queue.ack(message.message_id)
        return IndexWorkerResult(
            index_job_id=index_job.job_id,
            status=ParseJobStatus.SUCCEEDED,
            index_manifest_id=index_job.job_id,
            chunk_count=len(chunks),
            diagnostics=[{"code": "index_persisted", "chunk_count": len(chunks)}],
        )


class IngestionReconciler:
    def __init__(self, store: SQLiteDurableIngestionStore) -> None:
        self.store = store

    def scan(self) -> list[ReconcilerFinding]:
        findings: list[ReconcilerFinding] = []
        manifests = self.store.list_index_manifests()
        indexed_parse_job_ids = {manifest.parse_job_id for manifest in manifests if manifest.parse_job_id}
        for parse_job in self.store.list_parse_jobs():
            if parse_job.status == "succeeded" and parse_job.parse_job_id not in indexed_parse_job_ids:
                findings.append(
                    ReconcilerFinding(
                        finding_id=f"finding_{parse_job.parse_job_id}_missing_index",
                        finding_type="parse_succeeded_without_index",
                        severity="warning",
                        entity_id=parse_job.parse_job_id,
                        recommended_action="enqueue index_requested",
                        details={
                            "file_id": parse_job.file_id,
                            "document_version_id": parse_job.document_version_id,
                        },
                    )
                )

        for manifest in manifests:
            if manifest.status == "succeeded" and not self.store.list_index_chunks(manifest.job_id):
                findings.append(
                    ReconcilerFinding(
                        finding_id=f"finding_{manifest.job_id}_chunks_missing",
                        finding_type="index_chunks_missing",
                        severity="error",
                        entity_id=manifest.job_id,
                        recommended_action="replay index_requested",
                        details={
                            "knowledge_space_id": manifest.knowledge_space_id,
                            "document_version_id": manifest.document_version_id,
                        },
                    )
                )
        return findings


def _save_file_status(
    store: SQLiteDurableIngestionStore,
    durable_file: WorkspaceFileRecord,
    *,
    parse_status: str,
    latest_parse_job_id: str | None = None,
    latest_document_version_id: str | None = None,
) -> None:
    store.save_workspace_file(
        durable_file.model_copy(
            update={
                "parse_status": parse_status,
                "latest_parse_job_id": latest_parse_job_id or durable_file.latest_parse_job_id,
                "latest_document_version_id": latest_document_version_id
                or durable_file.latest_document_version_id,
            }
        )
    )


def _parse_attempt(snapshot) -> ParseAttempt:
    return ParseAttempt(
        parse_attempt_id=snapshot.parse_attempt_id,
        parse_job_id=snapshot.job_id,
        attempt=snapshot.attempt,
        status=ParseJobStatus(snapshot.status),
        diagnostics=list(snapshot.parser_diagnostics),
    )


def _index_chunks_for_manifest(
    *,
    index_runtime: KnowledgeIndexRuntime,
    index_job: IndexJobManifest,
    knowledge_space_id: str,
    query: str,
) -> list[IndexChunkRecord]:
    payload = index_runtime.to_retrieval_payload(knowledge_space_id, query or "__all__")
    chunks: list[IndexChunkRecord] = []
    seen_chunk_ids: set[str] = set()
    for source_name in ("bm25", "vector", "graph"):
        for document in payload.get("documents_by_source", {}).get(source_name, []):
            chunk_id = str(document.get("chunk_id") or "")
            if not chunk_id or chunk_id in seen_chunk_ids:
                continue
            seen_chunk_ids.add(chunk_id)
            metadata = dict(document.get("metadata") or {})
            chunks.append(
                IndexChunkRecord(
                    chunk_id=chunk_id,
                    index_job_id=index_job.job_id,
                    knowledge_space_id=index_job.knowledge_space_id,
                    workspace_id=index_job.workspace_id,
                    document_id=str(document.get("document_id") or index_job.document_id),
                    document_version_id=index_job.document_version_id,
                    block_id=str(metadata.get("block_id") or chunk_id.split("::", 1)[-1]),
                    content=str(document.get("content") or ""),
                    source_type=str(document.get("source_type") or source_name),
                    metadata=metadata,
                    citation_lineage=dict(metadata.get("citation_lineage") or {}),
                    acl_scope=str(metadata.get("acl_scope") or "workspace"),
                    sensitivity_tags=list(metadata.get("sensitivity_tags") or index_job.sensitivity_tags),
                )
            )
    return chunks


__all__ = [
    "IndexWorker",
    "IngestionReconciler",
    "LocalQueueBackend",
    "ParserWorker",
    "QueueDeliveryReceipt",
    "RabbitMQQueueBackend",
    "RedisRuntimeStateBoundary",
]
