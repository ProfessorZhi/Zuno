from __future__ import annotations

from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway
from zuno.knowledge.indexing import KnowledgeIndexRuntime


def test_sqlite_store_round_trips_source_file_parse_snapshot_and_index_manifest(tmp_path) -> None:
    from zuno.knowledge.storage import (
        IndexChunkRecord,
        LocalObjectStore,
        ParseJobRecord,
        SQLiteDurableIngestionStore,
        WorkspaceFileRecord,
    )

    source_text = "# Renewal\nRenewal notice must be sent 30 days before anniversary."
    object_store = LocalObjectStore(tmp_path / "objects")
    source_object = object_store.save_text(
        workspace_id="workspace_durable",
        source_id="source_renewal",
        filename="renewal.md",
        mime_type="text/markdown",
        content=source_text,
        owner_id="user_durable",
        acl_scope="workspace",
        sensitivity_tags=["internal"],
    )

    store = SQLiteDurableIngestionStore(tmp_path / "zuno.db")
    workspace_file = WorkspaceFileRecord(
        file_id="file_renewal",
        workspace_id="workspace_durable",
        source_id=source_object.source_id,
        owner_id="user_durable",
        filename="renewal.md",
        mime_type="text/markdown",
        source_sha256=source_object.source_sha256,
        parse_status="uploaded",
        security_label="internal",
    )
    store.save_source_object(source_object)
    store.save_workspace_file(workspace_file)

    request = ParseDocumentRequest(
        document_id=workspace_file.file_id,
        source_id=source_object.source_id,
        workspace_id=workspace_file.workspace_id,
        source_uri=source_object.storage_uri,
        mime_type=workspace_file.mime_type,
        source_text=source_text,
        hash=source_object.source_sha256,
        acl_scope="workspace",
        sensitivity_tags=["internal"],
    )
    parse_result = ParseGateway.submit_parse_job(request)
    parse_snapshot = ParseGateway.get_job_snapshot(parse_result.job_id)
    assert parse_result.document is not None

    store.create_parse_job(
        ParseJobRecord(
            parse_job_id=parse_result.job_id,
            workspace_id=workspace_file.workspace_id,
            file_id=workspace_file.file_id,
            source_id=source_object.source_id,
            status=parse_result.status,
            parser_id=parse_snapshot.parser_id,
            parser_version=request.parser_version,
            parse_idempotency_key=parse_snapshot.parse_idempotency_key,
            attempt_count=parse_snapshot.attempt_count,
        )
    )
    store.save_parse_snapshot(parse_snapshot)
    store.save_document_version(parse_result.document)

    index_runtime = KnowledgeIndexRuntime()
    index_runtime.create_knowledge_space("ks_durable", workspace_file.workspace_id)
    manifest = index_runtime.index_document(
        "ks_durable",
        parse_result.document,
        targets=["bm25", "vector", "graph"],
        parse_job_snapshot=parse_snapshot,
    )
    payload = index_runtime.to_retrieval_payload("ks_durable", "renewal notice")
    first_chunk = payload["documents_by_source"]["bm25"][0]
    store.save_index_manifest(manifest)
    store.save_index_chunk(
        IndexChunkRecord(
            chunk_id=first_chunk["chunk_id"],
            index_job_id=manifest.job_id,
            knowledge_space_id=manifest.knowledge_space_id,
            workspace_id=manifest.workspace_id,
            document_id=manifest.document_id,
            document_version_id=manifest.document_version_id,
            block_id=first_chunk["metadata"]["block_id"],
            content=first_chunk["content"],
            source_type=first_chunk["source_type"],
            metadata=first_chunk["metadata"],
            citation_lineage=first_chunk["metadata"]["citation_lineage"],
            acl_scope="workspace",
            sensitivity_tags=["internal"],
        )
    )

    restored = SQLiteDurableIngestionStore(tmp_path / "zuno.db")
    restored_file = restored.get_workspace_file(workspace_file.file_id)
    restored_job = restored.get_parse_job(parse_result.job_id)
    restored_snapshot = restored.get_parse_snapshot(parse_result.job_id)
    restored_document_version = restored.get_document_version(manifest.document_version_id)
    restored_manifest = restored.get_index_manifest(manifest.job_id)
    restored_chunks = restored.list_index_chunks(manifest.job_id)

    assert restored_file.source_sha256 == source_object.source_sha256
    assert restored_job.parse_idempotency_key == parse_snapshot.parse_idempotency_key
    assert restored_snapshot.parse_attempt_id == parse_snapshot.parse_attempt_id
    assert restored_document_version.source_sha256 == source_object.source_sha256
    assert restored_manifest.source_sha256 == source_object.source_sha256
    assert restored_chunks[0].citation_lineage["parse_job_id"] == parse_result.job_id
