from __future__ import annotations

import pytest


def _parsed_document(*, document_id: str, source_uri: str, text: str):
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    result = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id=document_id,
            workspace_id="workspace-generation-isolation",
            source_uri=source_uri,
            mime_type="text/markdown",
            source_text=text,
            sensitivity_tags=["internal"],
        )
    )
    assert result.document is not None
    return result.document


def _empty_document():
    from zuno.knowledge.ingestion import CanonicalDocumentIR, DocumentMetadata, DocumentProvenance

    return CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc-v2-empty",
            workspace_id="workspace-generation-isolation",
            source_uri="file://generation-v2-empty.md",
            mime_type="text/markdown",
            hash="empty-generation-v2",
            parser_id="native",
            parser_version="generation-isolation-probe",
        ),
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="generation-isolation-probe",
            source_uri="file://generation-v2-empty.md",
            confidence=1.0,
        ),
    )


def test_failed_rebuild_does_not_replace_last_servable_manifest() -> None:
    """A failed next build must not make the last good index generation disappear from serving."""

    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    runtime = KnowledgeIndexRuntime()
    runtime.create_knowledge_space(
        "ks-generation-failure",
        "workspace-generation-isolation",
    )
    first = runtime.index_document(
        "ks-generation-failure",
        _parsed_document(
            document_id="doc-v1",
            source_uri="file://generation-v1.md",
            text="# Generation One\nStable serving evidence from generation one.",
        ),
        targets=["bm25", "vector"],
    )
    before = runtime.to_retrieval_payload(
        "ks-generation-failure",
        "stable serving evidence",
    )
    assert before["manifest"]["job_id"] == first.job_id
    assert before["retrievers_used"] == ["bm25", "vector"]

    failed = runtime.index_document(
        "ks-generation-failure",
        _empty_document(),
        targets=["bm25", "vector"],
    )
    assert failed.status == "failed"

    after = runtime.to_retrieval_payload(
        "ks-generation-failure",
        "stable serving evidence",
    )

    # Target invariant under review: BUILDING/FAILED next-generation work must
    # not replace the last known-good serving generation.
    assert after["manifest"]["job_id"] == first.job_id
    assert after["retrievers_used"] == ["bm25", "vector"]
    assert after["documents_by_source"]["bm25"]
    assert after["documents_by_source"]["bm25"][0]["document_id"] == "doc-v1"


class _SwitchableAdapter:
    def __init__(self, *, adapter_id: str, target: str) -> None:
        self.adapter_id = adapter_id
        self.target = target
        self.fail = False

    def index(self, *, runtime, handoff, document, lineage, graph_project_id):
        if self.fail:
            raise RuntimeError(f"injected {self.target} generation failure")
        content = " ".join(block.text for block in document.blocks)
        return [
            {
                "chunk_id": f"{document.metadata.document_id}::{self.target}",
                "document_id": document.metadata.document_id,
                "workspace_id": document.metadata.workspace_id,
                "content": content,
                "source_type": self.target,
                "metadata": {
                    "block_id": document.blocks[0].block_id,
                    "chunk_id": f"{document.metadata.document_id}::{self.target}",
                    "document_version_id": document.metadata.document_version_id,
                    "source_span": {
                        "document_version_id": document.metadata.document_version_id,
                        "chunk_id": f"{document.metadata.document_id}::{self.target}",
                    },
                },
            }
        ]


def test_mid_build_target_failure_does_not_mix_new_data_with_old_manifest() -> None:
    """Partial next-generation writes must not leak under the previously active manifest."""

    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    bm25 = _SwitchableAdapter(adapter_id="probe_bm25", target="bm25")
    vector = _SwitchableAdapter(adapter_id="probe_vector", target="vector")
    runtime = KnowledgeIndexRuntime(adapter_bindings={"bm25": bm25, "vector": vector})
    runtime.create_knowledge_space(
        "ks-generation-mixed",
        "workspace-generation-isolation",
    )

    first = runtime.index_document(
        "ks-generation-mixed",
        _parsed_document(
            document_id="doc-v1",
            source_uri="file://generation-mixed-v1.md",
            text="# Generation One\nOld serving content must stay internally consistent.",
        ),
        targets=["bm25", "vector"],
    )
    before = runtime.to_retrieval_payload(
        "ks-generation-mixed",
        "serving content",
    )
    assert before["manifest"]["job_id"] == first.job_id
    assert before["documents_by_source"]["bm25"][0]["document_id"] == "doc-v1"
    assert before["documents_by_source"]["vector"][0]["document_id"] == "doc-v1"

    vector.fail = True
    with pytest.raises(RuntimeError, match="injected vector generation failure"):
        runtime.index_document(
            "ks-generation-mixed",
            _parsed_document(
                document_id="doc-v2",
                source_uri="file://generation-mixed-v2.md",
                text="# Generation Two\nNew candidate content must not leak before activation.",
            ),
            targets=["bm25", "vector"],
        )

    after = runtime.to_retrieval_payload(
        "ks-generation-mixed",
        "content",
    )

    # The old manifest can remain active only if all data served through it is
    # still from that same generation. A new bm25 write plus old vector data is
    # an internally inconsistent serving generation.
    assert after["manifest"]["job_id"] == first.job_id
    assert after["documents_by_source"]["bm25"][0]["document_id"] == "doc-v1"
    assert after["documents_by_source"]["vector"][0]["document_id"] == "doc-v1"
