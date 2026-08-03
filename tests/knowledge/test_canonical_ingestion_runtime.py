from __future__ import annotations

from dataclasses import dataclass, field

from zuno.knowledge.ingestion import (
    CanonicalIngestionRuntimeInput,
    CanonicalIngestionSliceRuntime,
    CanonicalIngestionState,
    PackageAUploadReceipt,
    PackageAWorkerReceipt,
    ParseDocumentRequest,
    ParseGateway,
)
from zuno.knowledge.ingestion.handoff import IndexableDocumentSnapshotV1
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from tools.evals.zuno.synthetic_benchmark.package_a_uploads import auroralis_representative_uploads


def test_auroralis_cases_convert_to_formal_package_a_upload_commands() -> None:
    uploads = auroralis_representative_uploads(
        tenant_id="tenant-phase22",
        workspace_id="workspace-phase22",
        principal_id="principal-phase22",
        bucket="zuno-phase22-auroralis",
        classification_ref="classification:internal",
        security_epoch_ref="security-epoch:phase22",
    )

    assert [upload.case_id for upload in uploads] == ["syn_sd_001", "syn_gp_001", "syn_tv_001"]
    assert {upload.question_type for upload in uploads} == {
        "single_doc_fact",
        "graph_path",
        "temporal_version",
    }
    for upload in uploads:
        assert upload.command.mime_type == "text/markdown"
        assert upload.command.content
        assert upload.command.source_object_id == upload.source_object_id
        assert upload.command.source_object_id.startswith(f"source:auroralis:{upload.case_id}:")
        assert upload.source_hash[:16] in upload.command.source_object_id
        assert upload.command.classification_ref == "classification:internal"
        assert upload.command.security_epoch_ref == "security-epoch:phase22"


def test_canonical_ingestion_activates_snapshot_only_after_three_visibility_receipts() -> None:
    command = _runtime_input()
    repo = _FakeKnowledgeRepo()
    runtime = CanonicalIngestionSliceRuntime(
        engine=object(),  # type: ignore[arg-type]
        index_runtime=KnowledgeIndexRuntime(),
        knowledge_uow_factory=lambda _engine: _FakeKnowledgeUow(repo),
    )

    receipt = runtime.activate_from_package_a_handoff(command)
    repeat = runtime.activate_from_package_a_handoff(command)

    assert receipt.state == CanonicalIngestionState.SNAPSHOT_ACTIVATED
    assert receipt.activated is True
    assert receipt.knowledge_version_id == repeat.knowledge_version_id
    assert receipt.idempotency_key == repeat.idempotency_key
    assert receipt.index_manifest is not None
    assert set(receipt.index_manifest.adapter_visibility_receipts) == {"bm25", "vector", "graph"}
    assert all(
        item["visibility"] == "visible"
        for item in receipt.index_manifest.adapter_visibility_receipts.values()
    )
    assert receipt.state_transitions == (
        CanonicalIngestionState.ACCEPTED,
        CanonicalIngestionState.OBJECT_STAGED,
        CanonicalIngestionState.OBJECT_COMMITTED,
        CanonicalIngestionState.CANONICAL_IR_READY,
        CanonicalIngestionState.INDEXING,
        CanonicalIngestionState.INDEXES_VISIBLE,
        CanonicalIngestionState.SNAPSHOT_ACTIVATED,
    )
    assert {item["index_kind"] for item in repo.index_visibility_jobs} == {"BM25", "VECTOR", "GRAPH"}
    assert repo.snapshots
    assert repo.cutovers


def test_canonical_ingestion_blocks_snapshot_when_vector_readback_is_hidden() -> None:
    command = _runtime_input()
    repo = _FakeKnowledgeRepo()
    runtime = CanonicalIngestionSliceRuntime(
        engine=object(),  # type: ignore[arg-type]
        index_runtime=KnowledgeIndexRuntime(
            adapter_bindings={
                "bm25": _VisibleAdapter("bm25"),
                "vector": _EmptyAdapter("vector"),
                "graph": _VisibleAdapter("graph"),
            }
        ),
        knowledge_uow_factory=lambda _engine: _FakeKnowledgeUow(repo),
    )

    receipt = runtime.activate_from_package_a_handoff(command)

    assert receipt.state == CanonicalIngestionState.INDEX_VISIBILITY_FAILED
    assert receipt.activated is False
    assert receipt.snapshot_id is None
    assert receipt.blocker == "vector:visibility:hidden:sample_retrieval_empty"
    assert repo.snapshots == []
    assert repo.cutovers == []


def _runtime_input() -> CanonicalIngestionRuntimeInput:
    source_text = "# Phase22\nSupplier renewal evidence carries lineage."
    request = ParseDocumentRequest(
        document_id="source:auroralis:syn_sd_001:test",
        source_id="source:auroralis:syn_sd_001:test",
        document_version_id="document-version:auroralis:syn_sd_001:1",
        parse_plan_id="parse-plan:auroralis:syn_sd_001:1",
        parse_job_id="parse-job:auroralis:syn_sd_001:1",
        parse_attempt_id="parse-attempt:auroralis:syn_sd_001:1",
        workspace_id="workspace-phase22",
        source_uri="s3://zuno-phase22-auroralis/tenant-phase22/workspace-phase22/syn_sd_001.md",
        mime_type="text/markdown",
        source_text=source_text,
        hash="source-hash-phase22",
        security_epoch_ref="security-epoch:phase22",
        sensitivity_tags=["internal"],
    )
    result = ParseGateway.submit_parse_job(request)
    assert result.document is not None
    snapshot = ParseGateway.get_job_snapshot(result.job_id)
    indexable = IndexableDocumentSnapshotV1(
        indexable_snapshot_id="snapshot:auroralis:syn_sd_001",
        document_version_id="document-version:auroralis:syn_sd_001:1",
        parse_snapshot_id=snapshot.job_id,
        quality_decision_id="quality:auroralis:syn_sd_001",
        workspace_id="workspace-phase22",
        document_id=result.document.metadata.document_id,
        canonical_hash="canonical-hash-phase22",
        idempotency_key="handoff:auroralis:syn_sd_001",
        parser_version=result.document.metadata.parser_version,
        ir_schema_version=result.document.metadata.ir_schema_version,
        source_span_refs=[
            {
                "block_id": block.block_id,
                "source_span_ref": f"source-span:{snapshot.parse_attempt_id}:{block.block_id}",
            }
            for block in result.document.blocks
        ],
        security_refs={"visibility_ref": "visibility:workspace-phase22:source:auroralis:syn_sd_001:test"},
        payload={"document": result.document.model_dump(mode="json")},
    )
    return CanonicalIngestionRuntimeInput(
        tenant_id="tenant-phase22",
        workspace_id="workspace-phase22",
        knowledge_space_id="knowledge-space:auroralis:syn_sd_001",
        upload_receipt=PackageAUploadReceipt(
            source_object_id="source:auroralis:syn_sd_001:test",
            document_version_id="document-version:auroralis:syn_sd_001:1",
            parse_plan_id="parse-plan:auroralis:syn_sd_001:1",
            parse_job_id="parse-job:auroralis:syn_sd_001:1",
            outbox_event_id="outbox:auroralis:syn_sd_001:1",
            object_ref="s3://zuno-phase22-auroralis/tenant-phase22/workspace-phase22/syn_sd_001.md",
        ),
        worker_receipt=PackageAWorkerReceipt(
            parse_job_id="parse-job:auroralis:syn_sd_001:1",
            parse_attempt_id="parse-attempt:auroralis:syn_sd_001:1",
            status="succeeded",
            acked_after_domain_commit=True,
            indexable_snapshot_id="snapshot:auroralis:syn_sd_001",
            outbox_event_id="outbox:snapshot:auroralis:syn_sd_001",
            handoff_idempotency_key="handoff:auroralis:syn_sd_001",
        ),
        document=result.document,
        parse_snapshot=snapshot,
        indexable_snapshot=indexable,
        security_epoch_ref="security-epoch:phase22",
        graph_project_id="graph-project:auroralis",
    )


class _VisibleAdapter:
    def __init__(self, target: str) -> None:
        self.adapter_id = f"visible_{target}"
        self.target = target

    def index(self, *, runtime, handoff, document, lineage, graph_project_id):
        return [
            {
                "chunk_id": f"{document.metadata.document_id}:{self.target}:1",
                "document_id": document.metadata.document_id,
                "workspace_id": document.metadata.workspace_id,
                "content": document.blocks[0].text,
                "source_type": self.target,
                "metadata": {"block_id": document.blocks[0].block_id},
            }
        ]


class _EmptyAdapter(_VisibleAdapter):
    def index(self, *, runtime, handoff, document, lineage, graph_project_id):
        return []


@dataclass
class _FakeKnowledgeRepo:
    versions: list[object] = field(default_factory=list)
    chunks: list[dict] = field(default_factory=list)
    index_visibility_jobs: list[dict] = field(default_factory=list)
    snapshots: list[dict] = field(default_factory=list)
    cutovers: list[dict] = field(default_factory=list)

    def next_version_no(self, **_kwargs) -> int:
        return len(self.versions) + 1

    def create_version(self, draft) -> None:
        if draft.knowledge_version_id not in {item.knowledge_version_id for item in self.versions}:
            self.versions.append(draft)

    def append_chunk(self, **kwargs) -> None:
        if kwargs not in self.chunks:
            self.chunks.append(kwargs)

    def record_index_visibility(self, **kwargs) -> None:
        if kwargs not in self.index_visibility_jobs:
            self.index_visibility_jobs.append(kwargs)

    def mark_ready(self, *, knowledge_version_id: str) -> None:
        visible = {
            item["index_kind"]
            for item in self.index_visibility_jobs
            if item["knowledge_version_id"] == knowledge_version_id
        }
        assert {"BM25", "VECTOR", "GRAPH"} <= visible

    def create_snapshot(self, **kwargs) -> None:
        if kwargs not in self.snapshots:
            self.snapshots.append(kwargs)

    def next_cutover_expected_generation(self, **_kwargs) -> int:
        return len(self.cutovers) + 1

    def cutover(self, **kwargs) -> None:
        if kwargs not in self.cutovers:
            self.cutovers.append(kwargs)


class _FakeKnowledgeUow:
    def __init__(self, repo: _FakeKnowledgeRepo) -> None:
        self.repo = repo

    def __enter__(self) -> _FakeKnowledgeRepo:
        return self.repo

    def __exit__(self, exc_type, exc, tb) -> None:
        return None
