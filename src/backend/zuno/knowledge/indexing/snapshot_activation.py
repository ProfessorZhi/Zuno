"""Knowledge Snapshot Activation (PHASE22 canonical owner adapter, hardened).

Snapshot activation is the Knowledge-owned gate between "corpus-level
index build receipts are authentic" and "a frozen KnowledgeSnapshot can be
served".  It only fires when all gates pass:

1. duplicate receipt_kind -> reject (never override);
2. every corpus receipt tenant_id == activation request tenant;
3. every corpus receipt workspace_id == activation request workspace;
4. every corpus receipt knowledge_version_id == request (non-empty);
5. index_job_manifest_hash non-empty;
6. content_set_hash identical across the three corpus receipts;
7. receipt owner kind correct (``corpus_index_build_receipt`` + the three
   index kinds);
8. every receipt payload hash valid;
9. ES / Milvus / Neo4j corpus receipts unique (one per index kind);
10. Neo4j path visibility receipt present, valid, visible, scope-consistent;
11. embedding provider/model/dimension/config hash consistent;
12. adapter-live-smoke receipts can never activate (formal scope,
    owner-produced input, snapshot_eligible required);
13. missing receipt -> BLOCKED with the exact missing kind;
14. dynamic/unknown receipt -> BLOCKED.

Without a real ``knowledge_version_id`` the adapter stays
``NOT_RUN_DEPENDENCY_BLOCKED`` and never invents a KnowledgeVersion.

Activated snapshots are deterministic (same inputs -> same snapshot id,
content hash, receipt ref) and immutable; the snapshot fact is persisted
through the formal KnowledgeSnapshot repository
(``KnowledgeRepository.create_snapshot``) and proven re-readable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

from .contracts import Neo4jPathVisibilityReceipt, validate_neo4j_path_visibility_receipt
from .corpus_index_build import (
    CORPUS_INDEX_KINDS,
    CorpusIndexBuildReceipt,
    validate_corpus_index_build_receipt,
)

SnapshotActivationStatus = Literal[
    "ACTIVATED",
    "NOT_RUN_DEPENDENCY_BLOCKED",
    "BLOCKED",
]

REQUIRED_CORPUS_RECEIPT_KINDS: tuple[str, ...] = CORPUS_INDEX_KINDS


class SnapshotPersistencePort(Protocol):
    """Formal persistence of the immutable snapshot fact.

    ``read`` MUST be tenant / workspace / knowledge_version scoped: a
    cross-tenant, cross-workspace or cross-version lookup must return None
    (fail closed), never a row from another scope.  Workspace is validated
    through the KnowledgeVersion owner because the snapshot table itself
    does not carry workspace.
    """

    def persist(
        self,
        *,
        snapshot_id: str,
        tenant_id: str,
        knowledge_version_id: str,
        snapshot_payload: dict[str, Any],
        serving_watermark_ref: str,
    ) -> dict[str, Any]: ...

    def read(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        snapshot_id: str,
    ) -> dict[str, Any] | None: ...


class SnapshotActivationReceipt(BaseModel):
    receipt_ref: str
    receipt_kind: str = "snapshot_activation_receipt"
    tenant_id: str
    workspace_id: str
    knowledge_version_id: str
    snapshot_id: str
    snapshot_content_hash: str
    index_job_manifest_hash: str
    required_corpus_receipt_kinds: list[str] = Field(default_factory=list)
    provided_corpus_receipt_kinds: list[str] = Field(default_factory=list)
    corpus_receipt_refs: dict[str, str] = Field(default_factory=dict)
    receipt_visibility: dict[str, str] = Field(default_factory=dict)
    consistency_checks: dict[str, bool] = Field(default_factory=dict)
    embedding_config_hash: str | None = None
    activation_status: SnapshotActivationStatus
    block_reason: str | None = None
    activated_at: datetime | None = None
    payload_hash: str


def build_snapshot_activation_receipt(
    *,
    tenant_id: str,
    workspace_id: str,
    knowledge_version_id: str,
    snapshot_id: str,
    snapshot_content_hash: str,
    index_job_manifest_hash: str,
    required_corpus_receipt_kinds: list[str],
    provided_corpus_receipt_kinds: list[str],
    corpus_receipt_refs: dict[str, str],
    receipt_visibility: dict[str, str],
    consistency_checks: dict[str, bool],
    embedding_config_hash: str | None,
    activation_status: SnapshotActivationStatus,
    block_reason: str | None,
    activated_at: datetime | None,
) -> SnapshotActivationReceipt:
    payload = {
        "receipt_kind": "snapshot_activation_receipt",
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "knowledge_version_id": knowledge_version_id,
        "snapshot_id": snapshot_id,
        "snapshot_content_hash": snapshot_content_hash,
        "index_job_manifest_hash": index_job_manifest_hash,
        "required_corpus_receipt_kinds": list(required_corpus_receipt_kinds),
        "provided_corpus_receipt_kinds": list(provided_corpus_receipt_kinds),
        "corpus_receipt_refs": dict(corpus_receipt_refs),
        "receipt_visibility": dict(receipt_visibility),
        "consistency_checks": dict(consistency_checks),
        "embedding_config_hash": embedding_config_hash,
        "activation_status": activation_status,
        "block_reason": block_reason,
    }
    # activated_at is observational metadata and intentionally excluded from
    # the payload hash so that an identical input set always yields the same
    # receipt ref (idempotent, deterministic activation).
    payload_hash = _stable_contract_hash(payload)
    receipt = SnapshotActivationReceipt(
        receipt_ref=f"snapshot-activation:{payload_hash[:16]}",
        payload_hash=payload_hash,
        **payload,
        activated_at=activated_at,
    )
    errors = validate_snapshot_activation_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    return receipt


def validate_snapshot_activation_receipt(
    receipt: SnapshotActivationReceipt | dict[str, Any],
) -> list[str]:
    model = (
        receipt
        if isinstance(receipt, SnapshotActivationReceipt)
        else SnapshotActivationReceipt(**receipt)
    )
    errors: list[str] = []
    if model.receipt_kind != "snapshot_activation_receipt":
        errors.append("receipt_kind mismatch")
    if model.activation_status == "ACTIVATED":
        if not model.snapshot_id:
            errors.append("activated receipt requires snapshot_id")
        if not model.snapshot_content_hash:
            errors.append("activated receipt requires snapshot_content_hash")
        if model.block_reason is not None:
            errors.append("activated receipt must not include block_reason")
        if model.activated_at is None:
            errors.append("activated receipt requires activated_at")
        for field_name in ["tenant_id", "workspace_id", "knowledge_version_id", "index_job_manifest_hash"]:
            if not str(getattr(model, field_name) or "").strip():
                errors.append(f"{field_name} is required for activation")
    else:
        if model.snapshot_id:
            errors.append("non-activated receipt must keep snapshot_id null")
        if model.activation_status == "NOT_RUN_DEPENDENCY_BLOCKED":
            if model.block_reason != "knowledge_version_dependency_missing":
                errors.append("NOT_RUN_DEPENDENCY_BLOCKED requires knowledge_version_dependency_missing block_reason")
        elif model.activation_status == "BLOCKED":
            if not model.block_reason:
                errors.append("BLOCKED receipt requires block_reason")
        else:
            errors.append(f"unknown activation_status: {model.activation_status}")
    expected_hash = _stable_contract_hash(
        {
            "receipt_kind": model.receipt_kind,
            "tenant_id": model.tenant_id,
            "workspace_id": model.workspace_id,
            "knowledge_version_id": model.knowledge_version_id,
            "snapshot_id": model.snapshot_id,
            "snapshot_content_hash": model.snapshot_content_hash,
            "index_job_manifest_hash": model.index_job_manifest_hash,
            "required_corpus_receipt_kinds": list(model.required_corpus_receipt_kinds),
            "provided_corpus_receipt_kinds": list(model.provided_corpus_receipt_kinds),
            "corpus_receipt_refs": dict(model.corpus_receipt_refs),
            "receipt_visibility": dict(model.receipt_visibility),
            "consistency_checks": dict(model.consistency_checks),
            "embedding_config_hash": model.embedding_config_hash,
            "activation_status": model.activation_status,
            "block_reason": model.block_reason,
        }
    )
    if model.payload_hash != expected_hash:
        errors.append("payload_hash mismatch")
    if model.receipt_ref != f"snapshot-activation:{expected_hash[:16]}":
        errors.append("receipt_ref must be derived from payload_hash")
    return errors


@dataclass(frozen=True, slots=True)
class SnapshotActivationResult:
    status: SnapshotActivationStatus
    snapshot_id: str | None
    snapshot_content_hash: str | None
    block_reason: str | None
    dependency_pr: str | None = None
    dependency_head_sha: str | None = None
    receipt: SnapshotActivationReceipt | None = None
    activation_evidence: dict[str, Any] = field(default_factory=dict)


class SnapshotActivationAdapter:
    """Canonical owner adapter: activates a frozen KnowledgeSnapshot only
    when every corpus-level receipt gate passes, then persists the
    immutable snapshot fact through the formal repository."""

    def __init__(self, *, snapshot_persistence: SnapshotPersistencePort | None = None) -> None:
        self._snapshot_persistence = snapshot_persistence

    def activate(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str | None,
        index_job_manifest_hash: str | None,
        corpus_receipts: list[CorpusIndexBuildReceipt | dict[str, Any]],
        neo4j_path_receipt: Neo4jPathVisibilityReceipt | dict[str, Any] | None,
        embedding_config: dict[str, Any] | None = None,
        dependency_pr: str | None = None,
        dependency_head_sha: str | None = None,
        observed_at: datetime | None = None,
    ) -> SnapshotActivationResult:
        observed_at = observed_at or datetime.now(timezone.utc)

        # ── Gate 0: real KnowledgeVersion dependency ──────────────────────
        if not str(knowledge_version_id or "").strip():
            receipt = build_snapshot_activation_receipt(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id="",
                snapshot_id="",
                snapshot_content_hash="",
                index_job_manifest_hash=str(index_job_manifest_hash or ""),
                required_corpus_receipt_kinds=list(REQUIRED_CORPUS_RECEIPT_KINDS),
                provided_corpus_receipt_kinds=[],
                corpus_receipt_refs={},
                receipt_visibility={},
                consistency_checks={"knowledge_version_present": False},
                embedding_config_hash=None,
                activation_status="NOT_RUN_DEPENDENCY_BLOCKED",
                block_reason="knowledge_version_dependency_missing",
                activated_at=None,
            )
            return SnapshotActivationResult(
                status="NOT_RUN_DEPENDENCY_BLOCKED",
                snapshot_id=None,
                snapshot_content_hash=None,
                block_reason="knowledge_version_dependency_missing",
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
                receipt=receipt,
            )

        # ── Gate 1 + 9 + 14: unique, known corpus receipt kinds ───────────
        normalized: dict[str, CorpusIndexBuildReceipt] = {}
        kind_errors: list[str] = []
        for raw in corpus_receipts:
            if not isinstance(raw, CorpusIndexBuildReceipt):
                if not isinstance(raw, dict):
                    kind_errors.append("dynamic_receipt_payload:not_an_object")
                    continue
                try:
                    candidate = CorpusIndexBuildReceipt(**raw)
                except (ValueError, TypeError) as exc:
                    kind_errors.append(f"dynamic_receipt_kind:{str(exc)[:120]}")
                    continue
            else:
                candidate = raw
            if candidate.receipt_kind != "corpus_index_build_receipt":
                kind_errors.append(f"unknown_receipt_kind:{candidate.receipt_kind}")
                continue
            if candidate.index_kind not in CORPUS_INDEX_KINDS:
                kind_errors.append(f"dynamic_receipt_kind:{candidate.index_kind}")
                continue
            if candidate.index_kind in normalized:
                kind_errors.append(f"duplicate_receipt_kind:{candidate.index_kind}")
                continue
            receipt_errors = validate_corpus_index_build_receipt(candidate)
            if receipt_errors:
                kind_errors.append(f"receipt_payload_invalid:{candidate.index_kind}:{','.join(receipt_errors)}")
                continue
            normalized[candidate.index_kind] = candidate
        if kind_errors:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                receipt_visibility={},
                consistency_checks={"receipt_kinds_unique_and_known": False},
                block_reason=f"corpus_receipt_rejected:{','.join(kind_errors)}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        # ── Gate 13: missing receipt kinds ────────────────────────────────
        missing = [kind for kind in REQUIRED_CORPUS_RECEIPT_KINDS if kind not in normalized]
        if missing:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                receipt_visibility={kind: "missing" for kind in missing},
                consistency_checks={"corpus_receipts_complete": False},
                block_reason=f"corpus_index_build_receipts_missing:{','.join(missing)}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        # ── Gate 8 + 12: formal, visible, owner-produced receipts only ─────
        checks: dict[str, bool] = {
            "corpus_receipts_complete": True,
            "receipt_kinds_unique_and_known": True,
        }
        receipt_visibility: dict[str, str] = {}
        corpus_receipt_refs: dict[str, str] = {}
        for kind in REQUIRED_CORPUS_RECEIPT_KINDS:
            receipt = normalized[kind]
            receipt_visibility[kind] = receipt.visibility_status
            corpus_receipt_refs[kind] = receipt.receipt_ref
            checks[f"{kind}_visible"] = receipt.visibility_status == "visible"
            checks[f"{kind}_formal_scope"] = receipt.receipt_scope == "formal"
            checks[f"{kind}_owner_produced"] = receipt.not_owner_produced is False
            checks[f"{kind}_snapshot_eligible"] = receipt.snapshot_eligible is True

        # ── Gates 2/3/4: per-receipt scope consistency ────────────────────
        for kind in REQUIRED_CORPUS_RECEIPT_KINDS:
            receipt = normalized[kind]
            checks[f"{kind}_tenant_consistent"] = receipt.tenant_id == tenant_id
            checks[f"{kind}_workspace_consistent"] = receipt.workspace_id == workspace_id
            checks[f"{kind}_knowledge_version_consistent"] = (
                receipt.knowledge_version_id == knowledge_version_id
            )

        # ── Gate 5: non-empty index manifest hash ─────────────────────────
        checks["index_job_manifest_hash_present"] = bool(str(index_job_manifest_hash or "").strip())

        # ── Gate 6: identical content set hash across the three receipts ──
        content_hashes = {normalized[kind].content_set_hash for kind in REQUIRED_CORPUS_RECEIPT_KINDS}
        checks["content_set_hash_consistent"] = len(content_hashes) == 1

        # ── Gate 10: Neo4j path visibility receipt present & consistent ───
        path_model: Neo4jPathVisibilityReceipt | None = None
        if neo4j_path_receipt is not None:
            path_model = (
                neo4j_path_receipt
                if isinstance(neo4j_path_receipt, Neo4jPathVisibilityReceipt)
                else Neo4jPathVisibilityReceipt(**neo4j_path_receipt)
            )
            path_errors = validate_neo4j_path_visibility_receipt(path_model)
            checks["path_receipt_valid"] = not path_errors
            checks["path_receipt_visible"] = path_model.visibility_status == "visible"
            checks["path_tenant_consistent"] = path_model.tenant_id == tenant_id
            checks["path_workspace_consistent"] = path_model.workspace_id == workspace_id
            checks["path_knowledge_version_consistent"] = (
                path_model.knowledge_version_id == knowledge_version_id
            )
        else:
            checks["path_receipt_present"] = False
        if "path_receipt_present" not in checks:
            checks["path_receipt_present"] = True

        # ── Gate 11: frozen embedding config hash ─────────────────────────
        request_config_hash = None
        if embedding_config:
            request_config_hash = str(embedding_config.get("config_hash") or "")
            checks["embedding_config_frozen"] = bool(request_config_hash)
            checks["embedding_provider_frozen"] = bool(embedding_config.get("provider"))
            checks["embedding_model_frozen"] = bool(embedding_config.get("model"))
            checks["embedding_dimension_frozen"] = bool(embedding_config.get("dimension"))
        else:
            checks["embedding_config_frozen"] = False
        if request_config_hash:
            receipt_config_hashes = {
                normalized[kind].config_hash for kind in REQUIRED_CORPUS_RECEIPT_KINDS
            }
            checks["embedding_config_consistent"] = (
                len(receipt_config_hashes) == 1 and request_config_hash in receipt_config_hashes
            )

        # Task D: every activation check must be strictly True — truthy,
        # defaulted or missing values never count as success.
        failed = [name for name, ok in checks.items() if ok is not True]
        if failed:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                receipt_visibility=receipt_visibility,
                consistency_checks=checks,
                block_reason=f"snapshot_activation_gate_failed:{','.join(sorted(failed))}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        # ── Activation: deterministic immutable content set ───────────────
        # The path fingerprint is derived from the deterministic path facts
        # (start/end/kinds/matched refs), never from the timestamped receipt
        # id, so identical graph state yields the identical snapshot.
        content_payload = {
            "index_job_manifest_hash": str(index_job_manifest_hash),
            "corpus_receipt_payload_hashes": sorted(
                normalized[kind].payload_hash for kind in REQUIRED_CORPUS_RECEIPT_KINDS
            ),
            "corpus_receipt_content_set_hash": normalized["elasticsearch_bm25"].content_set_hash,
            "neo4j_path_fingerprint": {
                "start_entity_ref": path_model.start_entity_ref,
                "end_entity_ref": path_model.end_entity_ref,
                "relation_kinds": list(path_model.relation_kinds),
                "matched_node_refs": list(path_model.matched_node_refs),
                "matched_relation_refs": list(path_model.matched_relation_refs),
            },
            "embedding_config_hash": request_config_hash,
            "knowledge_version_id": knowledge_version_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
        }
        snapshot_content_hash = _stable_contract_hash(content_payload)
        snapshot_id = f"snap_{snapshot_content_hash[:16]}"
        serving_watermark_ref = f"serving-watermark::{snapshot_id}"

        # ── Task A: persistence is a HARD gate.  No ACTIVATED receipt is
        # ever built before the snapshot fact is durably persisted in a
        # committed UoW and re-read through the tenant-scoped port. ───────
        if self._snapshot_persistence is None:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                receipt_visibility=receipt_visibility,
                consistency_checks=checks,
                block_reason="snapshot_persistence_port_missing",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        try:
            persist_result = self._snapshot_persistence.persist(
                snapshot_id=snapshot_id,
                tenant_id=tenant_id,
                knowledge_version_id=knowledge_version_id,
                snapshot_payload=content_payload,
                serving_watermark_ref=serving_watermark_ref,
            )
        except Exception as exc:  # noqa: BLE001
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                receipt_visibility=receipt_visibility,
                consistency_checks=checks,
                block_reason=f"snapshot_persistence_failed:{str(exc)[:160]}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        try:
            re_read = self._snapshot_persistence.read(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                snapshot_id=snapshot_id,
            )
        except Exception as exc:  # noqa: BLE001
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                receipt_visibility=receipt_visibility,
                consistency_checks=checks,
                block_reason=f"snapshot_readback_failed:{str(exc)[:160]}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        # ── Task B/C: verified, tenant-scoped readback ────────────────────
        readback_gaps: list[str] = []
        if re_read is None:
            readback_gaps.append("snapshot_readback_missing")
        else:
            if str(re_read.get("snapshot_id") or "") != snapshot_id:
                readback_gaps.append("readback_snapshot_id_mismatch")
            if str(re_read.get("tenant_id") or "") != tenant_id:
                readback_gaps.append("readback_tenant_id_mismatch")
            if str(re_read.get("knowledge_version_id") or "") != knowledge_version_id:
                readback_gaps.append("readback_knowledge_version_id_mismatch")
            if str(re_read.get("snapshot_hash") or "") != snapshot_content_hash:
                readback_gaps.append("readback_snapshot_hash_mismatch")
            if str(re_read.get("serving_watermark_ref") or "") != serving_watermark_ref:
                readback_gaps.append("readback_serving_watermark_mismatch")
        if readback_gaps:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                receipt_visibility=receipt_visibility,
                consistency_checks=checks,
                block_reason=f"snapshot_readback_inconsistent:{','.join(readback_gaps)}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        # ── Receipt built ONLY after the persisted fact is verified ───────
        receipt = build_snapshot_activation_receipt(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            snapshot_id=snapshot_id,
            snapshot_content_hash=snapshot_content_hash,
            index_job_manifest_hash=str(index_job_manifest_hash),
            required_corpus_receipt_kinds=list(REQUIRED_CORPUS_RECEIPT_KINDS),
            provided_corpus_receipt_kinds=list(REQUIRED_CORPUS_RECEIPT_KINDS),
            corpus_receipt_refs=corpus_receipt_refs,
            receipt_visibility=receipt_visibility,
            consistency_checks=checks,
            embedding_config_hash=request_config_hash,
            activation_status="ACTIVATED",
            block_reason=None,
            activated_at=observed_at,
        )

        persistence_evidence = {
            "persisted": True,
            "persist_result": persist_result,
            "snapshot_re_readable": True,
            "readback": re_read,
        }
        return SnapshotActivationResult(
            status="ACTIVATED",
            snapshot_id=snapshot_id,
            snapshot_content_hash=snapshot_content_hash,
            block_reason=None,
            dependency_pr=dependency_pr,
            dependency_head_sha=dependency_head_sha,
            receipt=receipt,
            activation_evidence={
                "snapshot_id": snapshot_id,
                "snapshot_content_hash": snapshot_content_hash,
                "activation_receipt_ref": receipt.receipt_ref,
                "required_corpus_receipt_kinds": list(REQUIRED_CORPUS_RECEIPT_KINDS),
                "provided_corpus_receipt_kinds": list(REQUIRED_CORPUS_RECEIPT_KINDS),
                "corpus_receipt_refs": corpus_receipt_refs,
                "receipt_visibility": receipt_visibility,
                "consistency_checks": checks,
                "content_set_immutable": True,
                "content_set_hash": normalized["elasticsearch_bm25"].content_set_hash,
                "persistence": persistence_evidence,
                "activated_at": observed_at.isoformat(),
            },
        )

    @staticmethod
    def _blocked(
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        index_job_manifest_hash: str | None,
        receipt_visibility: dict[str, str],
        consistency_checks: dict[str, bool],
        block_reason: str,
        observed_at: datetime,
        dependency_pr: str | None,
        dependency_head_sha: str | None,
    ) -> SnapshotActivationResult:
        receipt = build_snapshot_activation_receipt(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            snapshot_id="",
            snapshot_content_hash="",
            index_job_manifest_hash=str(index_job_manifest_hash or ""),
            required_corpus_receipt_kinds=list(REQUIRED_CORPUS_RECEIPT_KINDS),
            provided_corpus_receipt_kinds=sorted(receipt_visibility),
            corpus_receipt_refs={},
            receipt_visibility=receipt_visibility,
            consistency_checks=consistency_checks,
            embedding_config_hash=None,
            activation_status="BLOCKED",
            block_reason=block_reason,
            activated_at=None,
        )
        return SnapshotActivationResult(
            status="BLOCKED",
            snapshot_id=None,
            snapshot_content_hash=None,
            block_reason=block_reason,
            dependency_pr=dependency_pr,
            dependency_head_sha=dependency_head_sha,
            receipt=receipt,
        )


class PostgresKnowledgeSnapshotPersistence:
    """Formal snapshot persistence through KnowledgeRepository.create_snapshot.

    Reuses the existing KnowledgeSnapshot domain owner (PostgreSQL
    ``knowledge_snapshots`` table, alembic-managed).  No migration is
    created here.  The engine is injected so tests can substitute an
    in-memory or throwaway engine.
    """

    def __init__(self, engine_factory: Any | None = None) -> None:
        self._engine_factory = engine_factory or _default_engine_factory

    def persist(
        self,
        *,
        snapshot_id: str,
        tenant_id: str,
        knowledge_version_id: str,
        snapshot_payload: dict[str, Any],
        serving_watermark_ref: str,
    ) -> dict[str, Any]:
        from zuno.platform.database.knowledge.domain import KnowledgeUnitOfWork

        engine = self._engine_factory()
        with KnowledgeUnitOfWork(engine) as repo:
            repo.create_snapshot(
                snapshot_id=snapshot_id,
                tenant_id=tenant_id,
                knowledge_version_id=knowledge_version_id,
                snapshot_payload=snapshot_payload,
                serving_watermark_ref=serving_watermark_ref,
            )
        return {
            "persisted_snapshot_id": snapshot_id,
            "knowledge_version_id": knowledge_version_id,
            "tenant_id": tenant_id,
            "serving_watermark_ref": serving_watermark_ref,
        }

    def read(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        snapshot_id: str,
    ) -> dict[str, Any] | None:
        """Tenant / workspace / knowledge-version scoped snapshot readback.

        The workspace is validated through the KnowledgeVersion owner
        (``knowledge_domain_versions``) because the snapshot table itself
        does not carry workspace.  A cross-tenant, cross-workspace or
        cross-version lookup returns no row (fail closed).
        """
        from sqlalchemy import text

        engine = self._engine_factory()
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT s.snapshot_id, s.tenant_id, s.knowledge_version_id, "
                    "       s.snapshot_hash, s.serving_watermark_ref "
                    "FROM knowledge_snapshots s "
                    "JOIN knowledge_domain_versions v "
                    "  ON v.knowledge_version_id = s.knowledge_version_id "
                    "WHERE s.snapshot_id = :snapshot_id "
                    "  AND s.tenant_id = :tenant_id "
                    "  AND s.knowledge_version_id = :knowledge_version_id "
                    "  AND v.workspace_id = :workspace_id"
                ),
                {
                    "snapshot_id": snapshot_id,
                    "tenant_id": tenant_id,
                    "knowledge_version_id": knowledge_version_id,
                    "workspace_id": workspace_id,
                },
            ).fetchone()
        if row is None:
            return None
        return {
            "snapshot_id": row[0],
            "tenant_id": row[1],
            "knowledge_version_id": row[2],
            "snapshot_hash": row[3],
            "serving_watermark_ref": row[4],
        }


def _default_engine_factory() -> Any:
    from sqlalchemy import create_engine

    from zuno.platform.database.runtime import PostgresRuntimeConfig
    from zuno.platform.settings import app_settings

    config = PostgresRuntimeConfig(**app_settings.database)
    return create_engine(config.sync_url, future=True)


def _stable_contract_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "PostgresKnowledgeSnapshotPersistence",
    "REQUIRED_CORPUS_RECEIPT_KINDS",
    "SnapshotActivationAdapter",
    "SnapshotActivationReceipt",
    "SnapshotActivationResult",
    "SnapshotActivationStatus",
    "SnapshotPersistencePort",
    "build_snapshot_activation_receipt",
    "validate_snapshot_activation_receipt",
]
