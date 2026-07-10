from __future__ import annotations

import hashlib
import json


def _sample_document():
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_index",
            workspace_id="workspace_index",
            source_uri="file://contracts/index.md",
            mime_type="text/markdown",
            source_text="# Contract Renewal\nSupplier renewal risk is high.\nPayment is due monthly.",
            sensitivity_tags=["internal"],
        )
    )
    assert result.document is not None
    return result.document


def _submitted_document():
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    request = ParseDocumentRequest(
        document_id="doc_parse_index",
        workspace_id="workspace_index",
        source_uri="file://contracts/parse-index.md",
        mime_type="text/markdown",
        source_text="# Renewal\nSupplier renewal evidence carries lineage.",
        parser_config={"chunking": "line", "normalizer": "deterministic"},
        sensitivity_tags=["internal"],
    )
    submitted = ParseGateway.submit_parse_job(request)
    snapshot = ParseGateway.get_job_snapshot(submitted.job_id)
    assert submitted.document is not None
    return submitted.document, snapshot


def _diagnostics_digest(diagnostics: list[dict]) -> str:
    payload = json.dumps(diagnostics, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_index_runtime_builds_queryable_bm25_vector_and_graph_indexes() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document = _sample_document()
    runtime = KnowledgeIndexRuntime()
    space = runtime.create_knowledge_space(
        knowledge_space_id="ks_contracts",
        workspace_id="workspace_index",
        graph_project_id="contract_review",
    )
    manifest = runtime.index_document(
        knowledge_space_id=space.knowledge_space_id,
        document=document,
        targets=["bm25", "vector", "graph"],
    )

    assert manifest.status == "succeeded"
    assert manifest.knowledge_space_id == "ks_contracts"
    assert manifest.document_id == "doc_index"
    assert manifest.index_version.startswith("idx_")
    assert manifest.graph_project_ref == "contract_review"
    assert manifest.target_status == {"bm25": "ready", "vector": "ready", "graph": "ready"}
    assert manifest.error is None
    assert manifest.retry_count == 0
    assert manifest.source_block_ids

    result = runtime.query("ks_contracts", "renewal risk")
    assert result.knowledge_space_id == "ks_contracts"
    assert result.index_version == manifest.index_version
    assert result.documents_by_source["bm25"]
    assert result.documents_by_source["vector"]
    assert result.documents_by_source["graph"]
    assert result.documents_by_source["bm25"][0]["document_id"] == "doc_index"
    assert result.manifest.document_id == "doc_index"


def test_index_runtime_exposes_adapter_contracts_with_external_targets_blocked() -> None:
    from zuno.knowledge.indexing import INDEX_ADAPTER_CONTRACTS

    assert INDEX_ADAPTER_CONTRACTS["local_bm25"].runtime_status == "current"
    assert INDEX_ADAPTER_CONTRACTS["local_vector"].runtime_status == "current"
    assert INDEX_ADAPTER_CONTRACTS["local_graph"].runtime_status == "current"
    for adapter_id in ["elasticsearch", "milvus", "neo4j"]:
        adapter = INDEX_ADAPTER_CONTRACTS[adapter_id]
        assert adapter.runtime_status == "target_blocked"
        assert adapter.external_service is True
        assert adapter.blocked_reason


def test_index_manifest_tracks_document_ir_provenance_acl_and_adapter_status() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document = _sample_document()
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space(
        knowledge_space_id="ks_manifest",
        workspace_id="workspace_index",
        graph_project_id="contract_review",
    )
    manifest = runtime.index_document(
        knowledge_space_id="ks_manifest",
        document=document,
        targets=["bm25", "vector", "graph"],
    )

    assert manifest.source_provenance["parser_id"] == document.metadata.parser_id
    assert manifest.source_provenance["source_uri"] == document.metadata.source_uri
    assert manifest.acl_scopes == ["workspace"]
    assert manifest.sensitivity_tags == ["internal"]
    assert manifest.adapter_status == {
        "bm25": "local_bm25:current",
        "vector": "local_vector:current",
        "graph": "local_graph:current",
    }


def test_index_manifest_tracks_parse_job_lineage_and_diagnostics_digest() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document, parse_snapshot = _submitted_document()
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space(
        knowledge_space_id="ks_parse_lineage",
        workspace_id="workspace_index",
        graph_project_id="contract_review",
    )
    manifest = runtime.index_document(
        "ks_parse_lineage",
        document,
        targets=["bm25", "vector", "graph"],
        parse_job_snapshot=parse_snapshot,
    )

    assert manifest.status == "succeeded"
    assert manifest.parse_job_id == parse_snapshot.job_id
    assert manifest.parse_attempt_id == parse_snapshot.parse_attempt_id
    assert manifest.document_version_id == document.metadata.document_version_id
    assert manifest.source_sha256 == document.metadata.source_sha256
    assert manifest.parser_config_hash == document.metadata.parser_config_hash
    assert manifest.ir_schema_version == document.metadata.ir_schema_version
    assert manifest.diagnostics_digest == _diagnostics_digest(parse_snapshot.parser_diagnostics)
    assert manifest.block_count == len(document.blocks)
    assert manifest.table_count == len(document.tables)
    assert manifest.figure_count == len(document.figures)
    assert manifest.parser_diagnostics == parse_snapshot.parser_diagnostics
    assert manifest.source_provenance["parse_job_id"] == parse_snapshot.job_id
    assert manifest.source_provenance["document_version_id"] == document.metadata.document_version_id


def test_retrieval_payload_chunks_carry_citation_lineage_to_source_hash() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document, parse_snapshot = _submitted_document()
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_citation_lineage", "workspace_index")
    manifest = runtime.index_document(
        "ks_citation_lineage",
        document,
        targets=["bm25", "vector", "graph"],
        parse_job_snapshot=parse_snapshot,
    )
    payload = runtime.to_retrieval_payload("ks_citation_lineage", "renewal evidence")
    first_document = payload["documents_by_source"]["bm25"][0]
    lineage = first_document["metadata"]["citation_lineage"]

    assert lineage["index_job_id"] == manifest.job_id
    assert lineage["document_id"] == document.metadata.document_id
    assert lineage["block_id"] in manifest.source_block_ids
    assert lineage["chunk_id"] == first_document["chunk_id"]
    assert lineage["source_span"]["document_id"] == document.metadata.document_id
    assert lineage["source_span"]["chunk_id"] == first_document["chunk_id"]
    assert lineage["source_span"]["block_id"] in manifest.source_block_ids
    assert lineage["source_span"]["document_version_id"] == document.metadata.document_version_id
    assert lineage["source_span"]["source_uri"] == document.metadata.source_uri
    assert lineage["source_span"]["parser_name"] == document.metadata.parser_id
    assert lineage["document_version_id"] == document.metadata.document_version_id
    assert lineage["parse_job_id"] == parse_snapshot.job_id
    assert lineage["parse_attempt_id"] == parse_snapshot.parse_attempt_id
    assert lineage["source_sha256"] == document.metadata.source_sha256
    assert lineage["parser_config_hash"] == document.metadata.parser_config_hash
    assert first_document["metadata"]["document_version_id"] == document.metadata.document_version_id
    assert first_document["metadata"]["diagnostics_digest"] == manifest.diagnostics_digest
    assert first_document["metadata"]["source_span"]["chunk_id"] == first_document["chunk_id"]


def test_index_rehydrate_preserves_source_span_provenance_after_reload() -> None:
    from types import SimpleNamespace

    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document, parse_snapshot = _submitted_document()
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_reload_lineage", "workspace_index")
    manifest = runtime.index_document(
        "ks_reload_lineage",
        document,
        targets=["bm25", "vector", "graph"],
        parse_job_snapshot=parse_snapshot,
    )
    payload = runtime.to_retrieval_payload("ks_reload_lineage", "renewal evidence")
    first_document = payload["documents_by_source"]["bm25"][0]
    chunk = SimpleNamespace(
        chunk_id=first_document["chunk_id"],
        document_id=first_document["document_id"],
        workspace_id=first_document["workspace_id"],
        content=first_document["content"],
        document_version_id=first_document["metadata"]["document_version_id"],
        block_id=first_document["metadata"]["block_id"],
        source_type=first_document["source_type"],
        metadata=first_document["metadata"],
        citation_lineage=first_document["metadata"]["citation_lineage"],
        acl_scope=first_document["metadata"]["acl_scope"],
        sensitivity_tags=first_document["metadata"]["sensitivity_tags"],
    )

    reloaded = KnowledgeIndexRuntime()
    reloaded.rehydrate_index(manifest, [chunk])
    reloaded_document = reloaded.to_retrieval_payload(
        "ks_reload_lineage",
        "renewal evidence",
    )["documents_by_source"]["bm25"][0]

    assert reloaded_document["metadata"]["source_span"]["chunk_id"] == first_document["chunk_id"]
    assert (
        reloaded_document["metadata"]["citation_lineage"]["source_span"]["document_version_id"]
        == document.metadata.document_version_id
    )
    assert reloaded_document["metadata"]["source_span"]["page_number"] is None


def test_index_replay_keeps_stable_source_block_ids_and_chunk_ids() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document, parse_snapshot = _submitted_document()
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_replay_lineage", "workspace_index")
    first = runtime.index_document(
        "ks_replay_lineage",
        document,
        targets=["bm25", "vector", "graph"],
        parse_job_snapshot=parse_snapshot,
    )
    first_chunks = [
        item["chunk_id"]
        for item in runtime.to_retrieval_payload("ks_replay_lineage", "renewal")["documents_by_source"]["bm25"]
    ]
    second = runtime.index_document(
        "ks_replay_lineage",
        document,
        targets=["bm25", "vector", "graph"],
        parse_job_snapshot=parse_snapshot,
    )
    second_chunks = [
        item["chunk_id"]
        for item in runtime.to_retrieval_payload("ks_replay_lineage", "renewal")["documents_by_source"]["bm25"]
    ]

    assert first.source_block_ids == second.source_block_ids
    assert first_chunks == second_chunks
    assert len(second_chunks) == len(set(second_chunks))


def test_index_runtime_records_failed_jobs_and_retry_replays_manifest() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime
    from zuno.knowledge.ingestion import CanonicalDocumentIR, DocumentMetadata, DocumentProvenance

    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space(
        knowledge_space_id="ks_fail",
        workspace_id="workspace_index",
        graph_project_id="contract_review",
    )
    empty_document = CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_empty_index",
            workspace_id="workspace_index",
            source_uri="file://empty.md",
            mime_type="text/markdown",
            hash="empty",
            parser_id="native",
            parser_version="phase04-runtime-v1",
        ),
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="phase04-runtime-v1",
            source_uri="file://empty.md",
            confidence=1.0,
        ),
    )

    failed = runtime.index_document("ks_fail", empty_document, targets=["bm25", "vector", "graph"])
    replayed = runtime.get_job_manifest(failed.job_id)

    assert failed.status == "failed"
    assert failed.error == "document has no blocks to index"
    assert replayed.job_id == failed.job_id
    assert replayed.status == "failed"
    assert replayed.target_status == {"bm25": "failed", "vector": "failed", "graph": "failed"}

    repaired = _sample_document()
    retried = runtime.retry_job(failed.job_id, repaired)

    assert retried.job_id != failed.job_id
    assert retried.retry_count == 1
    assert retried.status == "succeeded"
    assert retried.previous_job_id == failed.job_id


def test_index_runtime_exports_retrieval_payload_for_later_retrieval_phase() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document = _sample_document()
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_retrieval", "workspace_index", graph_project_id="contract_review")
    manifest = runtime.index_document("ks_retrieval", document, targets=["bm25", "vector", "graph"])

    payload = runtime.to_retrieval_payload("ks_retrieval", "payment renewal")

    assert payload["knowledge_space_id"] == "ks_retrieval"
    assert payload["index_version"] == manifest.index_version
    assert payload["retrievers_used"] == ["bm25", "vector", "graph"]
    assert payload["index_health"] == {"bm25": "ready", "vector": "ready", "graph": "ready"}
    assert payload["documents_by_source"]["bm25"]
    assert payload["documents_by_source"]["vector"]
    assert payload["documents_by_source"]["graph"]


def test_index_runtime_retrieval_returns_citation_chunks_with_parent_context() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    document = _sample_document()
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_citation_chunks", "workspace_index")
    runtime.index_document("ks_citation_chunks", document, targets=["bm25", "vector", "graph"])

    payload = runtime.to_retrieval_payload("ks_citation_chunks", "supplier renewal risk")
    first_document = payload["documents_by_source"]["bm25"][0]

    assert first_document["chunk_id"].endswith("::cite1")
    assert first_document["metadata"]["chunk_role"] == "citation"
    assert first_document["metadata"]["parent_chunk_id"].startswith("doc_index::")
    assert first_document["metadata"]["parent_context"]
    assert first_document["metadata"]["source_span"]["parent_chunk_id"] == first_document["metadata"]["parent_chunk_id"]
    assert first_document["metadata"]["source_span"]["chunk_id"] == first_document["chunk_id"]
