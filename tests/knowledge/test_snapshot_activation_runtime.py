"""PHASE22 GAP-B4 snapshot activation runtime tests (hardened gate).

Covers the 14 activation gates: unique known receipt kinds, per-receipt
tenant/workspace/knowledge_version consistency, non-empty manifest hash,
identical content set hash, correct owner kinds, valid payload hashes,
mandatory Neo4j path receipt, frozen embedding config, formal scope only
(adapter smoke never activates), missing/unknown receipts blocked, plus
NOT_RUN_DEPENDENCY_BLOCKED while no real KnowledgeVersion exists, and
deterministic idempotent activation with immutable persisted facts.
"""

from __future__ import annotations

from datetime import datetime, timezone

from zuno.knowledge.indexing import (
    REQUIRED_CORPUS_RECEIPT_KINDS,
    SnapshotActivationAdapter,
    build_corpus_index_build_receipt,
    build_neo4j_path_visibility_receipt,
    validate_corpus_index_build_receipt,
    validate_snapshot_activation_receipt,
)

TENANT = "tenant_auroralis"
WORKSPACE = "workspace_regression"
KNOWLEDGE_VERSION = "knowledge-version::kv_real"
CONFIG_HASH = "sha256:embedding-config-frozen"
MANIFEST_HASH = "abc123manifesthash"
CONTENT_HASH = "content-set-hash-frozen"


def _corpus_receipt(
    kind: str,
    *,
    knowledge_version_id: str = KNOWLEDGE_VERSION,
    receipt_scope: str = "formal",
    not_owner_produced: bool = False,
    snapshot_eligible: bool = True,
    tenant_id: str = TENANT,
    workspace_id: str = WORKSPACE,
    content_set_hash: str = CONTENT_HASH,
    config_hash: str = CONFIG_HASH,
    visibility: str = "visible",
) -> dict:
    return build_corpus_index_build_receipt(
        index_kind=kind,
        receipt_scope=receipt_scope,
        input_kind="owner_produced" if not not_owner_produced else "frozen_candidate_manifest",
        not_owner_produced=not_owner_produced,
        snapshot_eligible=snapshot_eligible,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id,
        index_build_run_id="index-build-run::test",
        expected_document_count=8,
        expected_chunk_count=24,
        observed_document_count=8,
        observed_chunk_count=24,
        content_set_hash=content_set_hash,
        config_hash=config_hash,
        adapter_execution_ref="adapter-execution:test",
        readback_hash="readback-hash",
        visibility_status=visibility,
        block_reason=None if visibility == "visible" else "knowledge_version_dependency_missing",
    ).model_dump()


def _receipts() -> list[dict]:
    return [_corpus_receipt(kind) for kind in REQUIRED_CORPUS_RECEIPT_KINDS]


def _path_receipt(**overrides) -> dict:
    kwargs = {
        "tenant_id": TENANT,
        "workspace_id": WORKSPACE,
        "knowledge_version_id": KNOWLEDGE_VERSION,
        "snapshot_id": "snap_1234",
        "query_kind": "directed_path",
        "start_entity_ref": "person:Kjartan Eliasson",
        "end_entity_ref": "product:Northwind SDK v3.0.0",
        "relation_kinds": ["person_sponsors_project", "project_delivers_product"],
        "matched_node_refs": [
            "person:Kjartan Eliasson",
            "project:Northwind",
            "product:Northwind SDK v3.0.0",
        ],
        "matched_relation_refs": ["r1", "r2"],
        "adapter_execution_ref": "neo4j-path-readback:test",
        "visibility_status": "visible",
        "observed_at": datetime.now(timezone.utc),
        "config_hash": CONFIG_HASH,
    }
    kwargs.update(overrides)
    return build_neo4j_path_visibility_receipt(**kwargs).model_dump()


def _embedding_config() -> dict:
    return {
        "provider": "dashscope",
        "model": "text-embedding-v4",
        "dimension": 1024,
        "config_hash": CONFIG_HASH,
    }


def _activate(**overrides):
    kwargs = {
        "tenant_id": TENANT,
        "workspace_id": WORKSPACE,
        "knowledge_version_id": KNOWLEDGE_VERSION,
        "index_job_manifest_hash": MANIFEST_HASH,
        "corpus_receipts": _receipts(),
        "neo4j_path_receipt": _path_receipt(),
        "embedding_config": _embedding_config(),
    }
    kwargs.update(overrides)
    return SnapshotActivationAdapter().activate(**kwargs)


class _FakePersistence:
    def __init__(self) -> None:
        self.stored: dict[str, dict] = {}

    def persist(self, *, snapshot_id, tenant_id, knowledge_version_id, snapshot_payload, serving_watermark_ref):
        self.stored[snapshot_id] = {
            "snapshot_id": snapshot_id,
            "tenant_id": tenant_id,
            "knowledge_version_id": knowledge_version_id,
            "snapshot_hash": snapshot_payload,
            "serving_watermark_ref": serving_watermark_ref,
        }
        return {"persisted_snapshot_id": snapshot_id}

    def read(self, snapshot_id):
        return self.stored.get(snapshot_id)


def test_corpus_receipt_validator_requires_kv_for_visible() -> None:
    invalid = _corpus_receipt("elasticsearch_bm25")
    invalid["knowledge_version_id"] = ""
    errors = validate_corpus_index_build_receipt(invalid)
    assert any("knowledge_version_id" in error for error in errors)
    errors = validate_corpus_index_build_receipt(
        _corpus_receipt(
            "elasticsearch_bm25",
            receipt_scope="adapter_live_smoke",
            snapshot_eligible=False,
            knowledge_version_id="",
            visibility="blocked",
        )
    )
    assert not errors


def test_activation_blocks_without_real_knowledge_version() -> None:
    result = _activate(knowledge_version_id=None)
    assert result.status == "NOT_RUN_DEPENDENCY_BLOCKED"
    assert result.block_reason == "knowledge_version_dependency_missing"
    assert result.snapshot_id is None
    assert result.receipt is not None
    assert not validate_snapshot_activation_receipt(result.receipt)


def test_activation_rejects_duplicate_receipt_kind() -> None:
    duplicate = _receipts() + [_corpus_receipt("elasticsearch_bm25")]
    result = _activate(corpus_receipts=duplicate)
    assert result.status == "BLOCKED"
    assert "duplicate_receipt_kind" in result.block_reason
    assert result.snapshot_id is None


def test_activation_rejects_unknown_receipt_kind() -> None:
    unknown = _corpus_receipt("elasticsearch_bm25")
    unknown["index_kind"] = "elasticsearch_dynamic"
    unknown["receipt_kind"] = "dynamic_receipt"
    result = _activate(corpus_receipts=_receipts()[:2] + [unknown])
    assert result.status == "BLOCKED"
    assert "unknown_receipt_kind" in result.block_reason or "dynamic_receipt_kind" in result.block_reason


def test_activation_blocks_on_missing_receipt_kind() -> None:
    result = _activate(corpus_receipts=_receipts()[:2])
    assert result.status == "BLOCKED"
    assert "corpus_index_build_receipts_missing" in result.block_reason
    assert "neo4j_graph" in result.block_reason
    assert result.snapshot_id is None


def test_activation_rejects_adapter_smoke_receipts() -> None:
    smoke = [_corpus_receipt(kind, receipt_scope="adapter_live_smoke", snapshot_eligible=False, knowledge_version_id="", visibility="blocked") for kind in REQUIRED_CORPUS_RECEIPT_KINDS]
    result = _activate(corpus_receipts=smoke)
    assert result.status == "BLOCKED"
    assert "formal_scope" in result.block_reason


def test_activation_rejects_not_owner_produced_input() -> None:
    candidate = [_corpus_receipt(kind, not_owner_produced=True) for kind in REQUIRED_CORPUS_RECEIPT_KINDS]
    result = _activate(corpus_receipts=candidate)
    assert result.status == "BLOCKED"
    assert "owner_produced" in result.block_reason


def test_activation_rejects_tenant_mismatch() -> None:
    mismatched = [
        _corpus_receipt("elasticsearch_bm25", tenant_id="tenant_other"),
        *_corpus_receipts_rest("elasticsearch_bm25"),
    ]
    result = _activate(corpus_receipts=mismatched)
    assert result.status == "BLOCKED"
    assert "tenant_consistent" in result.block_reason


def _corpus_receipts_rest(excluded: str) -> list[dict]:
    return [_corpus_receipt(kind) for kind in REQUIRED_CORPUS_RECEIPT_KINDS if kind != excluded]


def test_activation_rejects_workspace_mismatch() -> None:
    mismatched = [
        _corpus_receipt("milvus_vector", workspace_id="workspace_other"),
        *_corpus_receipts_rest("milvus_vector"),
    ]
    result = _activate(corpus_receipts=mismatched)
    assert result.status == "BLOCKED"
    assert "workspace_consistent" in result.block_reason


def test_activation_rejects_knowledge_version_mismatch() -> None:
    mismatched = [
        _corpus_receipt("neo4j_graph", knowledge_version_id="knowledge-version::other"),
        *_corpus_receipts_rest("neo4j_graph"),
    ]
    result = _activate(corpus_receipts=mismatched)
    assert result.status == "BLOCKED"
    assert "knowledge_version_consistent" in result.block_reason


def test_activation_rejects_inconsistent_content_set_hash() -> None:
    mismatched = [
        _corpus_receipt("elasticsearch_bm25", content_set_hash="different-content-hash"),
        *_corpus_receipts_rest("elasticsearch_bm25"),
    ]
    result = _activate(corpus_receipts=mismatched)
    assert result.status == "BLOCKED"
    assert "content_set_hash_consistent" in result.block_reason


def test_activation_blocks_on_empty_manifest_hash() -> None:
    result = _activate(index_job_manifest_hash=None)
    assert result.status == "BLOCKED"
    assert "index_job_manifest_hash_present" in result.block_reason


def test_activation_requires_neo4j_path_receipt() -> None:
    result = _activate(neo4j_path_receipt=None)
    assert result.status == "BLOCKED"
    assert "path_receipt_present" in result.block_reason


def test_activation_rejects_inconsistent_path_tenant() -> None:
    result = _activate(neo4j_path_receipt=_path_receipt(tenant_id="tenant_other"))
    assert result.status == "BLOCKED"
    assert "path_tenant_consistent" in result.block_reason


def test_activation_blocks_without_frozen_embedding_config() -> None:
    result = _activate(embedding_config=None)
    assert result.status == "BLOCKED"
    assert "embedding_config_frozen" in result.block_reason


def test_activation_succeeds_persists_and_is_deterministic() -> None:
    persistence = _FakePersistence()
    adapter = SnapshotActivationAdapter(snapshot_persistence=persistence)
    first = adapter.activate(
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        knowledge_version_id=KNOWLEDGE_VERSION,
        index_job_manifest_hash=MANIFEST_HASH,
        corpus_receipts=_receipts(),
        neo4j_path_receipt=_path_receipt(),
        embedding_config=_embedding_config(),
    )
    second = adapter.activate(
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        knowledge_version_id=KNOWLEDGE_VERSION,
        index_job_manifest_hash=MANIFEST_HASH,
        corpus_receipts=_receipts(),
        neo4j_path_receipt=_path_receipt(),
        embedding_config=_embedding_config(),
    )

    assert first.status == "ACTIVATED"
    assert first.snapshot_id is not None
    assert first.receipt is not None
    assert not validate_snapshot_activation_receipt(first.receipt)
    assert first.activation_evidence["content_set_immutable"] is True
    assert first.activation_evidence["persistence"]["persisted"] is True
    assert first.activation_evidence["persistence"]["snapshot_re_readable"] is True

    # Idempotency: identical inputs -> identical snapshot and receipt.
    assert second.snapshot_id == first.snapshot_id
    assert second.snapshot_content_hash == first.snapshot_content_hash
    assert second.receipt.receipt_ref == first.receipt.receipt_ref

    # Different content hash -> different snapshot.
    changed = adapter.activate(
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        knowledge_version_id=KNOWLEDGE_VERSION,
        index_job_manifest_hash=MANIFEST_HASH,
        corpus_receipts=[
            _corpus_receipt(kind, content_set_hash="other-content-hash")
            for kind in REQUIRED_CORPUS_RECEIPT_KINDS
        ],
        neo4j_path_receipt=_path_receipt(),
        embedding_config=_embedding_config(),
    )
    assert changed.snapshot_id != first.snapshot_id

    # The persisted snapshot fact is re-readable.
    assert persistence.read(first.snapshot_id) is not None


def test_activation_receipt_validator_rejects_malformed_states() -> None:
    result = _activate()
    receipt = result.receipt.model_dump()
    receipt["snapshot_id"] = ""
    errors = validate_snapshot_activation_receipt(receipt)
    assert any("snapshot_id" in error for error in errors)

    blocked = _activate(knowledge_version_id=None).receipt.model_dump()
    blocked["activation_status"] = "BLOCKED"
    blocked["block_reason"] = None
    errors = validate_snapshot_activation_receipt(blocked)
    assert any("block_reason" in error for error in errors)
