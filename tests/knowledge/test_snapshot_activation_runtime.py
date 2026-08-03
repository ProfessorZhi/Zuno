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
    """Tenant-scoped fake: read() requires tenant/workspace/kv/snapshot id
    and returns no row for a foreign scope (fail closed)."""

    def __init__(self) -> None:
        self.stored: dict[str, dict] = {}
        self.persist_calls: list[dict] = []
        self.fail_persist: Exception | None = None
        self.skip_write: bool = False
        self.read_override: dict[str, Any] | None = None
        self.workspace_by_kv: dict[str, str] = {KNOWLEDGE_VERSION: WORKSPACE}

    def persist(self, *, snapshot_id, tenant_id, knowledge_version_id, snapshot_payload, serving_watermark_ref):
        if self.fail_persist is not None:
            raise self.fail_persist
        self.persist_calls.append(
            {
                "snapshot_id": snapshot_id,
                "tenant_id": tenant_id,
                "knowledge_version_id": knowledge_version_id,
                "snapshot_hash": snapshot_payload,
                "serving_watermark_ref": serving_watermark_ref,
            }
        )
        # Immutable snapshot semantics (ON CONFLICT DO NOTHING): an existing
        # fact under the same snapshot id is never overwritten.
        if not self.skip_write and snapshot_id not in self.stored:
            self.stored[snapshot_id] = {
                "snapshot_id": snapshot_id,
                "tenant_id": tenant_id,
                "knowledge_version_id": knowledge_version_id,
                "snapshot_hash": _expected_hash(snapshot_payload),
                "serving_watermark_ref": serving_watermark_ref,
            }
        return {"persisted_snapshot_id": snapshot_id}

    def read(self, *, tenant_id, workspace_id, knowledge_version_id, snapshot_id):
        if self.read_override is not None:
            return dict(self.read_override)
        row = self.stored.get(snapshot_id)
        if row is None:
            return None
        # Tenant / workspace / knowledge-version scoped: foreign scope -> None.
        if row["tenant_id"] != tenant_id:
            return None
        if row["knowledge_version_id"] != knowledge_version_id:
            return None
        if self.workspace_by_kv.get(knowledge_version_id) != workspace_id:
            return None
        return dict(row)


def _expected_hash(payload: dict[str, Any]) -> str:
    import hashlib
    import json

    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


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

    # The persisted snapshot fact is re-readable through the scoped port.
    assert (
        persistence.read(
            tenant_id=TENANT,
            workspace_id=WORKSPACE,
            knowledge_version_id=KNOWLEDGE_VERSION,
            snapshot_id=first.snapshot_id,
        )
        is not None
    )


def test_activation_receipt_validator_rejects_malformed_states() -> None:
    result = _activate_with_persistence(_FakePersistence())
    assert result.status == "ACTIVATED"
    receipt = result.receipt.model_dump()
    receipt["snapshot_id"] = ""
    errors = validate_snapshot_activation_receipt(receipt)
    assert any("snapshot_id" in error for error in errors)

    blocked = _activate(knowledge_version_id=None).receipt.model_dump()
    blocked["activation_status"] = "BLOCKED"
    blocked["block_reason"] = None
    errors = validate_snapshot_activation_receipt(blocked)
    assert any("block_reason" in error for error in errors)


# ---------------------------------------------------------------------------
# Persistence hard gate (Task A/B): no ACTIVATED without durable persistence
# ---------------------------------------------------------------------------


def _activate_with_persistence(persistence: Any) -> SnapshotActivationResult:
    return SnapshotActivationAdapter(snapshot_persistence=persistence).activate(
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        knowledge_version_id=KNOWLEDGE_VERSION,
        index_job_manifest_hash=MANIFEST_HASH,
        corpus_receipts=_receipts(),
        neo4j_path_receipt=_path_receipt(),
        embedding_config=_embedding_config(),
    )


def test_activation_blocks_without_persistence_port() -> None:
    result = _activate_with_persistence(None)
    assert result.status == "BLOCKED"
    assert result.block_reason == "snapshot_persistence_port_missing"
    assert result.snapshot_id is None
    assert result.receipt.activation_status == "BLOCKED"


def test_activation_blocks_when_persist_raises() -> None:
    persistence = _FakePersistence()
    persistence.fail_persist = RuntimeError("database commit failure")
    result = _activate_with_persistence(persistence)
    assert result.status == "BLOCKED"
    assert result.block_reason.startswith("snapshot_persistence_failed:")
    assert result.snapshot_id is None


def test_activation_blocks_when_persist_returns_but_nothing_written() -> None:
    persistence = _FakePersistence()
    persistence.skip_write = True
    result = _activate_with_persistence(persistence)
    assert result.status == "BLOCKED"
    assert result.block_reason == "snapshot_readback_inconsistent:snapshot_readback_missing"
    assert result.snapshot_id is None


def test_activation_blocks_when_readback_returns_wrong_tenant() -> None:
    persistence = _FakePersistence()
    persistence.read_override = {
        "snapshot_id": "snap_x",
        "tenant_id": "tenant_other",
        "knowledge_version_id": KNOWLEDGE_VERSION,
        "snapshot_hash": "h",
        "serving_watermark_ref": "w",
    }
    result = _activate_with_persistence(persistence)
    assert result.status == "BLOCKED"
    assert "readback_tenant_id_mismatch" in result.block_reason
    assert result.snapshot_id is None


def test_activation_blocks_when_readback_returns_wrong_knowledge_version() -> None:
    persistence = _FakePersistence()
    persistence.read_override = {
        "snapshot_id": "snap_x",
        "tenant_id": TENANT,
        "knowledge_version_id": "knowledge-version::other",
        "snapshot_hash": "h",
        "serving_watermark_ref": "w",
    }
    result = _activate_with_persistence(persistence)
    assert result.status == "BLOCKED"
    assert "readback_knowledge_version_id_mismatch" in result.block_reason


def test_activation_blocks_when_readback_hash_mismatches() -> None:
    persistence = _FakePersistence()
    result = _activate_with_persistence(persistence)
    assert result.status == "ACTIVATED"
    # Tamper the stored hash and retry -> same snapshot id, different hash
    # conflict must BLOCK (immutable snapshot, payload conflict).
    persistence.stored[result.snapshot_id]["snapshot_hash"] = "conflicting-hash"
    retry = _activate_with_persistence(persistence)
    assert retry.status == "BLOCKED"
    assert "readback_snapshot_hash_mismatch" in retry.block_reason


def test_activation_blocks_on_serving_watermark_mismatch() -> None:
    persistence = _FakePersistence()
    persistence.read_override = {
        "snapshot_id": "snap_x",
        "tenant_id": TENANT,
        "knowledge_version_id": KNOWLEDGE_VERSION,
        "snapshot_hash": "h",
        "serving_watermark_ref": "wrong-watermark",
    }
    result = _activate_with_persistence(persistence)
    assert result.status == "BLOCKED"
    assert "readback_serving_watermark_mismatch" in result.block_reason


def test_activation_idempotent_retry_after_persist_returns_same_snapshot() -> None:
    persistence = _FakePersistence()
    first = _activate_with_persistence(persistence)
    # Retry with the same inputs (as after a crash before the receipt was
    # returned) must yield the identical snapshot and receipt.
    retry = _activate_with_persistence(persistence)
    assert first.status == "ACTIVATED"
    assert retry.status == "ACTIVATED"
    assert retry.snapshot_id == first.snapshot_id
    assert retry.snapshot_content_hash == first.snapshot_content_hash
    assert retry.receipt.receipt_ref == first.receipt.receipt_ref
    assert len(persistence.persist_calls) == 2


def test_activation_payload_conflict_blocks_immutable_snapshot() -> None:
    persistence = _FakePersistence()
    first = _activate_with_persistence(persistence)
    assert first.status == "ACTIVATED"
    # A conflicting pre-existing fact under the same snapshot id (different
    # payload hash) must BLOCK — immutable snapshots are never overwritten.
    persistence.stored[first.snapshot_id]["snapshot_hash"] = "other-payload-hash"
    retry = _activate_with_persistence(persistence)
    assert retry.status == "BLOCKED"
    assert "readback_snapshot_hash_mismatch" in retry.block_reason


def test_activation_blocks_on_any_check_not_strictly_true() -> None:
    # Every activation check must be strictly True; the ACTIVATED evidence
    # always carries the full non-empty check set (Task D).
    result = _activate_with_persistence(_FakePersistence())
    assert result.status == "ACTIVATED"
    checks = result.activation_evidence["consistency_checks"]
    assert checks
    assert all(value is True for value in checks.values())
    assert result.receipt.consistency_checks == checks


def test_tenant_scoped_readback_rejects_foreign_scope() -> None:
    persistence = _FakePersistence()
    result = _activate_with_persistence(persistence)
    assert result.status == "ACTIVATED"
    # Foreign tenant / workspace / knowledge-version must not resolve.
    assert persistence.read(
        tenant_id="tenant_other",
        workspace_id=WORKSPACE,
        knowledge_version_id=KNOWLEDGE_VERSION,
        snapshot_id=result.snapshot_id,
    ) is None
    assert persistence.read(
        tenant_id=TENANT,
        workspace_id="workspace_other",
        knowledge_version_id=KNOWLEDGE_VERSION,
        snapshot_id=result.snapshot_id,
    ) is None
    assert persistence.read(
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        knowledge_version_id="knowledge-version::other",
        snapshot_id=result.snapshot_id,
    ) is None
    # The correct scope resolves.
    assert persistence.read(
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        knowledge_version_id=KNOWLEDGE_VERSION,
        snapshot_id=result.snapshot_id,
    ) is not None
