from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


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


def test_index_runtime_exposes_adapter_contracts_with_current_external_targets() -> None:
    from zuno.knowledge.indexing import INDEX_ADAPTER_CONTRACTS

    assert INDEX_ADAPTER_CONTRACTS["local_bm25"].runtime_status == "current"
    assert INDEX_ADAPTER_CONTRACTS["local_vector"].runtime_status == "current"
    assert INDEX_ADAPTER_CONTRACTS["local_graph"].runtime_status == "current"
    for adapter_id in ["elasticsearch", "milvus", "neo4j"]:
        adapter = INDEX_ADAPTER_CONTRACTS[adapter_id]
        assert adapter.runtime_status == "current"
        assert adapter.external_service is True
        assert adapter.blocked_reason is None
    assert "path_visibility_receipt" in INDEX_ADAPTER_CONTRACTS["neo4j"].operations


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
    assert set(manifest.adapter_dispatch_receipts) == {"bm25", "vector", "graph"}
    assert manifest.adapter_dispatch_receipts["bm25"]["adapter_id"] == "local_bm25"
    assert manifest.adapter_dispatch_receipts["vector"]["operation"] == "index"
    assert manifest.adapter_dispatch_receipts["graph"]["status"] == "succeeded"
    assert set(manifest.adapter_visibility_receipts) == {"bm25", "vector", "graph"}
    for target, receipt in manifest.adapter_visibility_receipts.items():
        assert receipt["adapter_target"] == target
        assert receipt["adapter_id"] == f"local_{target}"
        assert receipt["adapter_dispatch_ref"] == manifest.adapter_dispatch_receipts[target]["dispatch_ref"]
        assert receipt["adapter_status"] == "current"
        assert receipt["visibility"] == "visible"
        assert receipt["document_id"] == document.metadata.document_id
        assert receipt["document_version_id"] == document.metadata.document_version_id
        assert receipt["source_block_count"] == len(document.blocks)
        assert receipt["receipt_ref"].startswith(f"index-visibility:{target}:")
        assert len(receipt["payload_hash"]) == 64


def test_index_runtime_invokes_configured_adapter_bindings() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    class SpyAdapter:
        def __init__(self, adapter_id: str, target: str) -> None:
            self.adapter_id = adapter_id
            self.target = target
            self.calls: list[dict] = []

        def index(self, *, runtime, handoff, document, lineage, graph_project_id):
            self.calls.append(
                {
                    "document_id": document.metadata.document_id,
                    "document_version_id": lineage["document_version_id"],
                    "graph_project_id": graph_project_id,
                }
            )
            return [
                {
                    "chunk_id": f"{document.metadata.document_id}::{self.target}",
                    "document_id": document.metadata.document_id,
                    "workspace_id": document.metadata.workspace_id,
                    "content": f"{self.target} adapter indexed renewal evidence.",
                    "source_type": self.target,
                    "metadata": {
                        "block_id": self.target,
                        "chunk_id": f"{document.metadata.document_id}::{self.target}",
                        "source_span": {"chunk_id": f"{document.metadata.document_id}::{self.target}"},
                    },
                }
            ]

    bm25 = SpyAdapter("configured_bm25", "bm25")
    vector = SpyAdapter("configured_vector", "vector")
    runtime = KnowledgeIndexRuntime(adapter_bindings={"bm25": bm25, "vector": vector})
    runtime.create_knowledge_space(
        knowledge_space_id="ks_configured_adapter",
        workspace_id="workspace_index",
        graph_project_id="configured_graph_project",
    )

    manifest = runtime.index_document(
        knowledge_space_id="ks_configured_adapter",
        document=_sample_document(),
        targets=["bm25", "vector"],
    )

    assert [call["document_id"] for call in bm25.calls] == ["doc_index"]
    assert [call["document_version_id"] for call in vector.calls] == [manifest.document_version_id]
    assert manifest.adapter_dispatch_receipts["bm25"]["adapter_id"] == "configured_bm25"
    assert manifest.adapter_dispatch_receipts["vector"]["adapter_id"] == "configured_vector"
    assert manifest.adapter_visibility_receipts["bm25"]["adapter_dispatch_ref"] == manifest.adapter_dispatch_receipts["bm25"]["dispatch_ref"]
    result = runtime.query("ks_configured_adapter", "renewal evidence")
    assert result.documents_by_source["bm25"][0]["source_type"] == "bm25"
    assert result.documents_by_source["vector"][0]["source_type"] == "vector"


def test_index_runtime_external_adapter_requires_service_readback_visibility() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime, external_adapter_bindings

    class ServiceClient:
        def __init__(self) -> None:
            self.index_calls: list[dict] = []
            self.search_calls: list[dict] = []
            self.documents: list[dict] = []

        def index_documents(self, index_name: str, documents: list[dict]) -> None:
            self.index_calls.append({"index_name": index_name, "document_count": len(documents)})
            self.documents = list(documents)

        def search_documents(self, query: str, index_name: str) -> list[dict]:
            self.search_calls.append({"index_name": index_name, "query": query})
            return list(self.documents)

    client = ServiceClient()
    runtime = KnowledgeIndexRuntime(
        adapter_bindings=external_adapter_bindings(
            elasticsearch_client=client,
            index_prefix="goal03",
        )
    )
    runtime.create_knowledge_space("ks_external_bm25", "workspace_index")

    manifest = runtime.index_document(
        "ks_external_bm25",
        _sample_document(),
        targets=["bm25"],
    )
    payload = runtime.to_retrieval_payload("ks_external_bm25", "supplier renewal")

    assert client.index_calls == [{"index_name": "goal03_bm25", "document_count": len(client.documents)}]
    assert client.search_calls[0]["index_name"] == "goal03_bm25"
    assert manifest.adapter_status == {"bm25": "elasticsearch:current"}
    assert manifest.adapter_dispatch_receipts["bm25"]["adapter_id"] == "elasticsearch"
    assert manifest.adapter_visibility_receipts["bm25"]["visibility"] == "visible"
    assert manifest.adapter_visibility_receipts["bm25"]["visibility_failure_reason"] is None
    assert manifest.adapter_visibility_receipts["bm25"]["sample_match_count"] > 0
    assert payload["retrievers_used"] == ["bm25"]
    assert payload["documents_by_source"]["bm25"]


def test_index_runtime_external_adapter_does_not_serve_without_readback_match() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime, external_adapter_bindings

    class EmptyReadbackClient:
        def index_documents(self, index_name: str, documents: list[dict]) -> None:
            self.index_name = index_name
            self.document_count = len(documents)

        def search_documents(self, query: str, index_name: str) -> list[dict]:
            return []

    runtime = KnowledgeIndexRuntime(
        adapter_bindings=external_adapter_bindings(
            elasticsearch_client=EmptyReadbackClient(),
            index_prefix="goal03",
        )
    )
    runtime.create_knowledge_space("ks_external_hidden", "workspace_index")

    manifest = runtime.index_document(
        "ks_external_hidden",
        _sample_document(),
        targets=["bm25"],
    )
    payload = runtime.to_retrieval_payload("ks_external_hidden", "supplier renewal")

    assert manifest.adapter_dispatch_receipts["bm25"]["status"] == "succeeded"
    assert manifest.adapter_visibility_receipts["bm25"]["visibility"] == "hidden"
    assert (
        manifest.adapter_visibility_receipts["bm25"]["visibility_failure_reason"]
        == "external_sample_retrieval_no_source_match"
    )
    assert manifest.target_status["bm25"] == "degraded"
    assert payload["retrievers_used"] == []
    assert payload["documents_by_source"] == {}


def test_index_runtime_milvus_vector_adapter_serves_after_readback() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime, external_adapter_bindings

    class VectorClient:
        def __init__(self) -> None:
            self.index_calls: list[dict] = []
            self.search_calls: list[dict] = []
            self.documents: list[dict] = []

        def index_documents(self, index_name: str, documents: list[dict]) -> None:
            self.index_calls.append({"index_name": index_name, "document_count": len(documents)})
            self.documents = list(documents)

        def search_documents(self, query: str, index_name: str) -> list[dict]:
            self.search_calls.append({"index_name": index_name, "query": query})
            return list(self.documents)

    client = VectorClient()
    runtime = KnowledgeIndexRuntime(
        adapter_bindings=external_adapter_bindings(
            milvus_client=client,
            index_prefix="goal03",
        )
    )
    runtime.create_knowledge_space("ks_milvus_vector_contract", "workspace_index")

    manifest = runtime.index_document(
        "ks_milvus_vector_contract",
        _sample_document(),
        targets=["vector"],
    )
    payload = runtime.to_retrieval_payload("ks_milvus_vector_contract", "supplier renewal")

    assert client.index_calls == [{"index_name": "goal03_vector", "document_count": len(client.documents)}]
    assert client.search_calls[0]["index_name"] == "goal03_vector"
    assert manifest.adapter_status == {"vector": "milvus:current"}
    assert manifest.adapter_dispatch_receipts["vector"]["adapter_id"] == "milvus"
    assert manifest.adapter_visibility_receipts["vector"]["visibility"] == "visible"
    assert manifest.adapter_visibility_receipts["vector"]["sample_match_count"] > 0
    assert manifest.target_status["vector"] == "ready"
    assert payload["retrievers_used"] == ["vector"]
    assert payload["documents_by_source"]["vector"]


def test_index_runtime_visibility_requires_sample_retrieval_before_serving() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    class EmptyAdapter:
        adapter_id = "empty_vector"
        target = "vector"

        def index(self, *, runtime, handoff, document, lineage, graph_project_id):
            return []

    document = _sample_document()
    runtime = KnowledgeIndexRuntime(adapter_bindings={"vector": EmptyAdapter()})
    runtime.create_knowledge_space("ks_visibility_sample", "workspace_index")

    manifest = runtime.index_document(
        knowledge_space_id="ks_visibility_sample",
        document=document,
        targets=["vector"],
    )
    payload = runtime.to_retrieval_payload("ks_visibility_sample", "supplier renewal risk")

    assert manifest.adapter_dispatch_receipts["vector"]["status"] == "succeeded"
    assert manifest.adapter_visibility_receipts["vector"]["visibility"] == "hidden"
    assert manifest.adapter_visibility_receipts["vector"]["visibility_failure_reason"] == "sample_retrieval_empty"
    assert manifest.adapter_visibility_receipts["vector"]["sample_match_count"] == 0
    assert manifest.target_status["vector"] == "degraded"
    assert payload["retrievers_used"] == []
    assert payload["index_health"] == {}
    assert payload["documents_by_source"] == {}


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
    assert set(payload["adapter_visibility_receipts"]) == {"bm25", "vector", "graph"}
    assert payload["adapter_visibility_receipts"]["bm25"]["visibility"] == "visible"
    assert payload["manifest"]["adapter_visibility_receipts"]["vector"]["adapter_status"] == "current"
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


def test_index_runtime_promotes_normalized_phrase_over_keyword_noise() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
    )

    document = CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_phrase",
            workspace_id="workspace_index",
            source_uri="file://phrase.md",
            mime_type="text/markdown",
            hash="sha256:phrase",
            parser_id="native",
            parser_version="phase04-test",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_noise",
                type="paragraph",
                text="Renewal risk risk risk appears often but not as the exact obligation.",
                source_span=SourceSpan(line_range=[1, 1]),
            ),
            DocumentBlock(
                block_id="block_phrase",
                type="paragraph",
                text="The supplier renewal evidence carries lineage.",
                source_span=SourceSpan(line_range=[2, 2]),
            ),
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="phase04-test",
            source_uri="file://phrase.md",
            confidence=1.0,
        ),
    )
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_phrase", "workspace_index")
    runtime.index_document("ks_phrase", document, targets=["bm25", "vector", "graph"])

    first_document = runtime.to_retrieval_payload(
        "ks_phrase",
        "supplier renewal evidence",
    )["documents_by_source"]["bm25"][0]

    assert first_document["metadata"]["block_id"] == "block_phrase"
    assert first_document["retriever_source"] == "normalized_phrase"
    assert first_document["candidate_reason"] == "normalized_phrase_match"
    assert first_document["matched_phrase"] == "supplier renewal evidence"
    assert first_document["rank"] == 1


def test_index_runtime_normalized_phrase_handles_punctuation_and_newlines() -> None:
    from zuno.knowledge.indexing import KnowledgeIndexRuntime
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
    )

    document = CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_phrase_norm",
            workspace_id="workspace_index",
            source_uri="file://phrase-normalized.md",
            mime_type="text/markdown",
            hash="sha256:phrase-normalized",
            parser_id="native",
            parser_version="phase04-test",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_phrase",
                type="paragraph",
                text="Console-2026.04\nrollout checklist is current.",
                source_span=SourceSpan(line_range=[1, 2]),
            )
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="phase04-test",
            source_uri="file://phrase-normalized.md",
            confidence=1.0,
        ),
    )
    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space("ks_phrase_norm", "workspace_index")
    runtime.index_document("ks_phrase_norm", document, targets=["bm25", "vector", "graph"])

    first_document = runtime.to_retrieval_payload(
        "ks_phrase_norm",
        "console 2026 04 rollout checklist",
    )["documents_by_source"]["bm25"][0]

    assert first_document["retriever_source"] == "normalized_phrase"
    assert first_document["candidate_reason"] == "normalized_phrase_match"


def test_neo4j_path_visibility_receipt_contract_accepts_two_hop_readback() -> None:
    from zuno.knowledge.indexing import (
        build_neo4j_path_visibility_receipt,
        validate_neo4j_path_visibility_receipt,
    )

    receipt = build_neo4j_path_visibility_receipt(
        tenant_id="tenant_auroralis",
        workspace_id="workspace_finance",
        knowledge_version_id="kv_2026_04",
        snapshot_id="snapshot_2026_04",
        query_kind="two_hop_path",
        start_entity_ref="entity:auroralis:console",
        end_entity_ref="entity:auroralis:audit",
        relation_kinds=["OWNED_BY", "REVIEWED_BY"],
        matched_node_refs=[
            "entity:auroralis:console",
            "entity:auroralis:platform",
            "entity:auroralis:audit",
        ],
        matched_relation_refs=[
            "relation:console-owned-by-platform",
            "relation:platform-reviewed-by-audit",
        ],
        adapter_execution_ref="neo4j-exec:readback:001",
        visibility_status="visible",
        observed_at=datetime(2026, 8, 3, 9, 30, tzinfo=timezone.utc),
        config_hash="sha256:neo4j-config-v1",
    )

    assert receipt.receipt_id.startswith("neo4j-path-visibility:")
    assert receipt.path_length == 2
    assert receipt.visibility_status == "visible"
    assert validate_neo4j_path_visibility_receipt(receipt) == []


def test_neo4j_path_visibility_receipt_rejects_missing_snapshot_and_wrong_path_shape() -> None:
    from zuno.knowledge.indexing import Neo4jPathVisibilityReceipt, validate_neo4j_path_visibility_receipt

    receipt = Neo4jPathVisibilityReceipt(
        receipt_id="neo4j-path-visibility:forged",
        tenant_id="tenant_auroralis",
        workspace_id="workspace_finance",
        knowledge_version_id="kv_2026_04",
        snapshot_id="",
        query_kind="two_hop_path",
        start_entity_ref="entity:auroralis:console",
        end_entity_ref="entity:auroralis:audit",
        relation_kinds=["OWNED_BY"],
        path_length=2,
        matched_node_refs=["entity:auroralis:wrong", "entity:auroralis:audit"],
        matched_relation_refs=["relation:console-owned-by-platform"],
        adapter_execution_ref="neo4j-exec:readback:001",
        visibility_status="visible",
        observed_at=datetime(2026, 8, 3, 9, 30, tzinfo=timezone.utc),
        config_hash="sha256:neo4j-config-v1",
        payload_hash="forged",
    )

    errors = validate_neo4j_path_visibility_receipt(receipt)

    assert "snapshot_id is required" in errors
    assert "matched_relation_refs must match path_length" in errors
    assert "relation_kinds must match path_length" in errors
    assert "matched_node_refs must contain path_length + 1 nodes" in errors
    assert "matched_node_refs must start with start_entity_ref" in errors
    assert "payload_hash mismatch" in errors


class _FakeNeo4jRecord:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def data(self) -> dict:
        return dict(self._payload)


class _FakeNeo4jSession:
    def __init__(self, path_rows: list[dict]) -> None:
        self.path_rows = path_rows
        self.calls: list[dict] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def run(self, cypher: str, parameters: dict):
        self.calls.append({"cypher": cypher, "parameters": parameters})
        if "relationships(path)" in cypher:
            return [_FakeNeo4jRecord(row) for row in self.path_rows]
        return []


class _FakeNeo4jDriver:
    def __init__(self, path_rows: list[dict]) -> None:
        self.session_obj = _FakeNeo4jSession(path_rows)
        self.closed = False

    def session(self, *, database: str):
        self.database = database
        return self.session_obj

    def close(self) -> None:
        self.closed = True


def test_neo4j_graph_client_generates_path_receipt_from_owner_readback() -> None:
    from zuno.knowledge.indexing import Neo4jGraphIndexClient

    driver = _FakeNeo4jDriver(
        [
            {
                "matched_node_refs": [
                    "entity:auroralis:console",
                    "entity:auroralis:platform",
                    "entity:auroralis:audit",
                ],
                "matched_relation_refs": [
                    "relation:console-owned-by-platform",
                    "relation:platform-reviewed-by-audit",
                ],
            }
        ]
    )
    client = Neo4jGraphIndexClient(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="unused",
        driver_factory=lambda: driver,
    )

    client.index_graph_relations(
        "phase22_graph",
        tenant_id="tenant_auroralis",
        workspace_id="workspace_finance",
        knowledge_version_id="kv_2026_04",
        snapshot_id="snapshot_2026_04",
        entities=[
            {"entity_ref": "entity:auroralis:console", "kind": "Product"},
            {"entity_ref": "entity:auroralis:platform", "kind": "System"},
            {"entity_ref": "entity:auroralis:audit", "kind": "Team"},
        ],
        relations=[
            {
                "relation_ref": "relation:console-owned-by-platform",
                "from": "entity:auroralis:console",
                "to": "entity:auroralis:platform",
                "kind": "OWNED_BY",
            },
            {
                "relation_ref": "relation:platform-reviewed-by-audit",
                "from": "entity:auroralis:platform",
                "to": "entity:auroralis:audit",
                "kind": "REVIEWED_BY",
            },
        ],
    )
    receipt = client.verify_path_visibility_receipt(
        "phase22_graph",
        tenant_id="tenant_auroralis",
        workspace_id="workspace_finance",
        knowledge_version_id="kv_2026_04",
        snapshot_id="snapshot_2026_04",
        start_entity_ref="entity:auroralis:console",
        end_entity_ref="entity:auroralis:audit",
        relation_kinds=["OWNED_BY", "REVIEWED_BY"],
        query_kind="two_hop_path",
        config_hash="sha256:neo4j-config-v1",
        observed_at=datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc),
    )

    assert receipt is not None
    assert receipt.receipt_id.startswith("neo4j-path-visibility:")
    assert receipt.path_length == 2
    assert receipt.matched_relation_refs == [
        "relation:console-owned-by-platform",
        "relation:platform-reviewed-by-audit",
    ]
    assert receipt.adapter_execution_ref == "neo4j-path-readback:phase22_graph"
    assert any("MERGE (from)-[r:ZUNO_DIRECTED_RELATION" in call["cypher"] for call in driver.session_obj.calls)
    assert any("relationships(path)" in call["cypher"] for call in driver.session_obj.calls)
    assert driver.closed is True


def test_neo4j_graph_client_returns_no_receipt_when_path_readback_missing() -> None:
    from zuno.knowledge.indexing import Neo4jGraphIndexClient

    driver = _FakeNeo4jDriver([])
    client = Neo4jGraphIndexClient(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="unused",
        driver_factory=lambda: driver,
    )

    receipt = client.verify_path_visibility_receipt(
        "phase22_graph",
        tenant_id="tenant_auroralis",
        workspace_id="workspace_finance",
        knowledge_version_id="kv_2026_04",
        snapshot_id="snapshot_2026_04",
        start_entity_ref="entity:auroralis:console",
        end_entity_ref="entity:auroralis:audit",
        relation_kinds=["OWNED_BY", "REVIEWED_BY"],
        config_hash="sha256:neo4j-config-v1",
    )

    assert receipt is None
    assert driver.closed is True
