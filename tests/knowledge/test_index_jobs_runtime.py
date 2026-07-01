from __future__ import annotations


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
