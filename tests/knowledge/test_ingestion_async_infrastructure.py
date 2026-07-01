from __future__ import annotations

import hashlib

from zuno.knowledge.storage import (
    LocalObjectStore,
    SQLiteDurableIngestionStore,
    SourceObjectRecord,
    WorkspaceFileRecord,
)


def _source_and_file(
    *,
    store: SQLiteDurableIngestionStore,
    object_store: LocalObjectStore,
    workspace_id: str,
    file_id: str,
    filename: str,
    mime_type: str,
    payload: bytes,
) -> SourceObjectRecord:
    source_id = f"source_{file_id}"
    source = object_store.save_bytes(
        workspace_id=workspace_id,
        source_id=source_id,
        filename=filename,
        mime_type=mime_type,
        content=payload,
        owner_id="user_phase03",
        sensitivity_tags=["internal"],
    )
    store.save_source_object(source)
    store.save_workspace_file(
        WorkspaceFileRecord(
            file_id=file_id,
            workspace_id=workspace_id,
            source_id=source_id,
            owner_id="user_phase03",
            filename=filename,
            mime_type=mime_type,
            source_sha256=source.source_sha256,
            parse_status="uploaded",
            security_label="internal",
        )
    )
    return source


def test_local_object_store_bytes_round_trip_and_missing_diagnostics(tmp_path) -> None:
    object_store = LocalObjectStore(tmp_path / "objects")
    payload = b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\n"
    expected_sha = hashlib.sha256(payload).hexdigest()

    source = object_store.save_bytes(
        workspace_id="workspace_bytes",
        source_id="source_pdf",
        filename="contract.pdf",
        mime_type=None,
        content=payload,
        owner_id="user_phase03",
    )

    assert source.mime_type == "application/pdf"
    assert source.size_bytes == len(payload)
    assert source.source_sha256 == expected_sha
    assert object_store.read_bytes(source) == payload
    assert object_store.verify_sha256(source)
    with object_store.open_stream(source) as stream:
        assert stream.read(5) == b"%PDF-"

    missing = source.model_copy(update={"storage_uri": (tmp_path / "missing.bin").resolve().as_uri()})
    diagnostics = object_store.diagnose_object(missing)
    assert diagnostics.ok is False
    assert diagnostics.diagnostics[0]["code"] == "object_missing"


def test_local_queue_lifecycle_replay_and_external_dependency_probes() -> None:
    from zuno.knowledge.ingestion.async_runtime import (
        LocalQueueBackend,
        RabbitMQQueueBackend,
        RedisRuntimeStateBoundary,
    )

    queue = LocalQueueBackend()
    message = queue.enqueue(
        topic="parse_requested",
        payload={"file_id": "file_queue"},
        idempotency_key="parse:file_queue",
        trace_id="trace_queue",
    )

    consumed = queue.consume("parse_requested")
    assert consumed is not None
    assert consumed.message_id == message.message_id
    assert consumed.status == "consumed"
    assert queue.ack(consumed.message_id).status == "acked"

    failed = queue.enqueue(
        topic="parse_requested",
        payload={"file_id": "file_failed"},
        idempotency_key="parse:file_failed",
    )
    dead_letter = queue.fail(failed.message_id, reason="parser crashed", retryable=False)
    assert dead_letter.reason == "parser crashed"
    assert queue.dead_letters()[0].source_message_id == failed.message_id

    replayed = queue.replay_dead_letter(dead_letter.dead_letter_id)
    assert replayed.payload == failed.payload
    assert replayed.attempt == failed.attempt + 1
    assert queue.consume("parse_requested").message_id == replayed.message_id

    rabbit_probe = RabbitMQQueueBackend().dependency_probe()
    assert rabbit_probe.status == "target_blocked"
    rabbit_result = RabbitMQQueueBackend().enqueue(
        topic="parse_requested",
        payload={},
        idempotency_key="parse:target-blocked",
    )
    assert rabbit_result.ok is False
    assert rabbit_result.status == "target_blocked"
    assert rabbit_result.dependency_probe.status == "target_blocked"

    redis_boundary = RedisRuntimeStateBoundary()
    assert redis_boundary.local_fallback_enabled is True
    assert redis_boundary.dependency_probe().status == "target_blocked"


def test_local_parser_and_index_workers_persist_async_success_lifecycle(tmp_path) -> None:
    from zuno.knowledge.ingestion.async_runtime import (
        IngestionReconciler,
        IndexWorker,
        LocalQueueBackend,
        ParserWorker,
    )

    store = SQLiteDurableIngestionStore(tmp_path / "zuno.db")
    object_store = LocalObjectStore(tmp_path / "objects")
    queue = LocalQueueBackend()
    source = _source_and_file(
        store=store,
        object_store=object_store,
        workspace_id="workspace_async",
        file_id="file_async",
        filename="policy.md",
        mime_type="text/markdown",
        payload=b"# Policy\nRetention evidence needs owner, due date, and approval.",
    )

    queue.enqueue(
        topic="parse_requested",
        payload={
            "workspace_id": source.workspace_id,
            "file_id": "file_async",
            "source_id": source.source_id,
            "knowledge_space_id": "ks_async",
            "trace_id": "trace_async",
        },
        idempotency_key=f"parse:{source.workspace_id}:{source.source_sha256}",
        trace_id="trace_async",
    )

    parse_result = ParserWorker(store=store, object_store=object_store, queue=queue).run_once()
    assert parse_result.status == "succeeded"
    assert store.get_workspace_file("file_async").parse_status == "parsed"
    assert store.get_parse_job(parse_result.parse_job_id).status == "succeeded"
    assert store.get_document_version(parse_result.document_version_id).block_count >= 1
    assert [event.payload["status"] for event in queue.outbox_events("file_async")] == [
        "queued",
        "parsing",
        "parsed",
    ]
    assert IngestionReconciler(store).scan()[0].finding_type == "parse_succeeded_without_index"

    index_message = queue.consume("index_requested")
    assert index_message is not None
    queue.requeue(index_message)
    index_result = IndexWorker(store=store, queue=queue).run_once()
    assert index_result.status == "succeeded"
    assert store.get_workspace_file("file_async").parse_status == "indexed"
    assert store.get_index_manifest(index_result.index_job_id).status == "succeeded"
    assert store.list_index_chunks(index_result.index_job_id)
    assert [event.payload["status"] for event in queue.outbox_events("file_async")][-2:] == [
        "indexing",
        "indexed",
    ]
    assert IngestionReconciler(store).scan() == []

    from zuno.knowledge.indexing import IndexJobManifest

    store.save_index_manifest(
        IndexJobManifest(
            job_id="index_missing_chunks",
            knowledge_space_id="ks_async",
            workspace_id="workspace_async",
            document_id="file_async",
            source_uri=source.storage_uri,
            index_version="idx_missing_chunks",
            targets=["bm25"],
            target_status={"bm25": "ready"},
            status="succeeded",
            parse_job_id=parse_result.parse_job_id,
            parse_attempt_id=parse_result.parse_attempt.parse_attempt_id,
            document_version_id=parse_result.document_version_id,
            source_sha256=source.source_sha256,
        )
    )
    missing_chunk_findings = IngestionReconciler(store).scan()
    assert missing_chunk_findings[0].finding_type == "index_chunks_missing"
    assert missing_chunk_findings[0].entity_id == "index_missing_chunks"


def test_blocked_ocr_vlm_worker_does_not_create_fake_index(tmp_path) -> None:
    from zuno.knowledge.ingestion.async_runtime import LocalQueueBackend, ParserWorker

    store = SQLiteDurableIngestionStore(tmp_path / "zuno.db")
    object_store = LocalObjectStore(tmp_path / "objects")
    queue = LocalQueueBackend()
    source = _source_and_file(
        store=store,
        object_store=object_store,
        workspace_id="workspace_blocked",
        file_id="file_scan",
        filename="scan.png",
        mime_type="image/png",
        payload=b"\x89PNG\r\nblocked ocr boundary",
    )

    queue.enqueue(
        topic="parse_requested",
        payload={
            "workspace_id": source.workspace_id,
            "file_id": "file_scan",
            "source_id": source.source_id,
            "knowledge_space_id": "ks_blocked",
            "trace_id": "trace_blocked",
        },
        idempotency_key=f"parse:{source.workspace_id}:{source.source_sha256}",
        trace_id="trace_blocked",
    )

    result = ParserWorker(store=store, object_store=object_store, queue=queue).run_once()
    assert result.status == "blocked"
    assert store.get_workspace_file("file_scan").parse_status == "blocked"
    assert store.get_parse_job(result.parse_job_id).blocked_reason
    assert store.get_parse_snapshot(result.parse_job_id).parser_diagnostics[0]["code"] == "target_blocked_adapter"
    assert queue.consume("index_requested") is None
    assert [event.payload["status"] for event in queue.outbox_events("file_scan")] == [
        "queued",
        "parsing",
        "blocked",
    ]
