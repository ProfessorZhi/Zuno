"""PHASE22 GAP-B4 snapshot activation runtime tests (DeepSeek2 / CC-B).

Covers the canonical SnapshotActivationAdapter fail-closed semantics:
activation only when all three authentic visibility receipts are visible and
scope-consistent; NOT_RUN_DEPENDENCY_BLOCKED while the real
knowledge_version_id is missing; deterministic (idempotent) snapshot id.
"""

from __future__ import annotations

from datetime import datetime, timezone

from zuno.knowledge.indexing import (
    REQUIRED_VISIBILITY_RECEIPT_KINDS,
    SnapshotActivationAdapter,
    build_index_visibility_receipt,
    build_neo4j_path_visibility_receipt,
    validate_snapshot_activation_receipt,
)

TENANT = "tenant_auroralis"
WORKSPACE = "workspace_regression"
KNOWLEDGE_VERSION = "knowledge-version::kv_real"
INDEX_VERSION = "idx_0123456789ab"
CONFIG_HASH = "sha256:embedding-config-frozen"
MANIFEST_HASH = "abc123manifesthash"


def _receipt(kind: str) -> dict:
    adapter_target = {
        "elasticsearch_bm25_visibility": "bm25",
        "milvus_vector_visibility": "vector",
        "neo4j_graph_visibility": "graph",
    }[kind]
    adapter_id = {
        "elasticsearch_bm25_visibility": "elasticsearch",
        "milvus_vector_visibility": "milvus",
        "neo4j_graph_visibility": "neo4j",
    }[kind]
    return build_index_visibility_receipt(
        adapter_target=adapter_target,
        adapter_id=adapter_id,
        adapter_dispatch_ref=f"index-dispatch:{adapter_target}:abc",
        adapter_status="current",
        visibility="visible",
        visibility_failure_reason=None,
        sample_query="renewal policy",
        sample_match_count=3,
        knowledge_space_id="ks_phase22",
        index_version=INDEX_VERSION,
        document_id="doc_security_policy_2026",
        document_version_id="document-version::doc_security_policy_2026::abc",
        source_block_count=3,
    ).model_dump()


def _receipts() -> list[dict]:
    return [_receipt(kind) for kind in REQUIRED_VISIBILITY_RECEIPT_KINDS]


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
        "adapter_execution_ref": "neo4j-path-readback:phase22",
        "visibility_status": "visible",
        "observed_at": datetime.now(timezone.utc),
        "config_hash": CONFIG_HASH,
    }
    kwargs.update(overrides)
    return build_neo4j_path_visibility_receipt(**kwargs).model_dump()


def _activate(**overrides):
    kwargs = {
        "tenant_id": TENANT,
        "workspace_id": WORKSPACE,
        "knowledge_version_id": KNOWLEDGE_VERSION,
        "index_job_manifest_hash": MANIFEST_HASH,
        "visibility_receipts": _receipts(),
        "neo4j_path_receipt": _path_receipt(),
        "embedding_config_hash": CONFIG_HASH,
    }
    kwargs.update(overrides)
    return SnapshotActivationAdapter().activate(**kwargs)


def test_activation_requires_all_three_receipts() -> None:
    result = _activate(
        visibility_receipts=[_receipt(k) for k in ("elasticsearch_bm25_visibility", "neo4j_graph_visibility")]
    )
    assert result.status == "BLOCKED"
    assert result.snapshot_id is None
    assert result.block_reason.startswith("index_visibility_receipts_missing:")
    assert "milvus_vector_visibility" in result.block_reason


def test_activation_blocks_on_hidden_receipt() -> None:
    hidden = _receipt("milvus_vector_visibility")
    hidden["visibility"] = "hidden"
    hidden["visibility_failure_reason"] = "sample_retrieval_no_source_match"
    hidden["sample_match_count"] = 0
    # rebuild the receipt with corrected hash fields
    rebuilt = build_index_visibility_receipt(
        adapter_target="vector",
        adapter_id="milvus",
        adapter_dispatch_ref=hidden["adapter_dispatch_ref"],
        adapter_status="current",
        visibility="hidden",
        visibility_failure_reason="sample_retrieval_no_source_match",
        sample_query=hidden["sample_query"],
        sample_match_count=0,
        knowledge_space_id=hidden["knowledge_space_id"],
        index_version=hidden["index_version"],
        document_id=hidden["document_id"],
        document_version_id=hidden["document_version_id"],
        source_block_count=hidden["source_block_count"],
    ).model_dump()
    result = _activate(
        visibility_receipts=[
            _receipt("elasticsearch_bm25_visibility"),
            _receipt("neo4j_graph_visibility"),
            rebuilt,
        ]
    )
    assert result.status == "BLOCKED"
    assert result.block_reason == "index_visibility_not_visible:milvus_vector_visibility"
    assert result.snapshot_id is None


def test_activation_blocks_without_real_knowledge_version() -> None:
    result = _activate(knowledge_version_id=None)
    assert result.status == "NOT_RUN_DEPENDENCY_BLOCKED"
    assert result.block_reason == "knowledge_version_dependency_missing"
    assert result.snapshot_id is None
    assert result.receipt is not None
    assert result.receipt.activation_status == "NOT_RUN_DEPENDENCY_BLOCKED"
    assert not validate_snapshot_activation_receipt(result.receipt)


def test_activation_blocks_on_scope_inconsistency() -> None:
    inconsistent = _receipt("elasticsearch_bm25_visibility")
    inconsistent["index_version"] = "idx_other"
    inconsistent = build_index_visibility_receipt(
        adapter_target="bm25",
        adapter_id="elasticsearch",
        adapter_dispatch_ref=inconsistent["adapter_dispatch_ref"],
        adapter_status="current",
        visibility="visible",
        visibility_failure_reason=None,
        sample_query=inconsistent["sample_query"],
        sample_match_count=inconsistent["sample_match_count"],
        knowledge_space_id=inconsistent["knowledge_space_id"],
        index_version="idx_other",
        document_id=inconsistent["document_id"],
        document_version_id=inconsistent["document_version_id"],
        source_block_count=inconsistent["source_block_count"],
    ).model_dump()
    result = _activate(
        visibility_receipts=[inconsistent] + [_receipt(k) for k in REQUIRED_VISIBILITY_RECEIPT_KINDS[1:]]
    )
    assert result.status == "BLOCKED"
    assert result.block_reason == "receipt_scope_inconsistent:index_version_consistent"
    assert result.snapshot_id is None


def test_activation_blocks_without_frozen_embedding_config() -> None:
    result = _activate(embedding_config_hash=None)
    assert result.status == "BLOCKED"
    assert result.block_reason == "embedding_config_not_frozen"
    assert result.snapshot_id is None


def test_activation_blocks_on_inconsistent_path_tenant() -> None:
    result = _activate(neo4j_path_receipt=_path_receipt(tenant_id="tenant_other"))
    assert result.status == "BLOCKED"
    assert result.block_reason == "receipt_scope_inconsistent:path_tenant_consistent"
    assert result.snapshot_id is None


def test_activation_succeeds_and_is_deterministic() -> None:
    first = _activate()
    second = _activate()

    assert first.status == "ACTIVATED"
    assert first.snapshot_id is not None
    assert first.snapshot_content_hash is not None
    assert first.receipt is not None
    assert first.receipt.activation_status == "ACTIVATED"
    assert first.receipt.snapshot_id == first.snapshot_id
    assert first.receipt.activated_at is not None
    assert first.receipt.block_reason is None
    assert not validate_snapshot_activation_receipt(first.receipt)
    assert first.activation_evidence["content_set_immutable"] is True

    # Idempotency: identical inputs produce the identical frozen content set.
    assert second.snapshot_id == first.snapshot_id
    assert second.snapshot_content_hash == first.snapshot_content_hash
    assert second.receipt.receipt_ref == first.receipt.receipt_ref

    # The snapshot content hash is bound to the receipts, manifest and
    # embedding config, so changing any input changes the snapshot id.
    changed = _activate(embedding_config_hash="sha256:other-config")
    assert changed.snapshot_id != first.snapshot_id


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
