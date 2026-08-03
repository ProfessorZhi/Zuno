"""Knowledge Snapshot Activation (PHASE22 canonical owner adapter).

Snapshot activation is the Knowledge-owned gate between "indexes are
visible" and "a frozen KnowledgeSnapshot can be served".  It only fires
when all three index visibility receipts are authentic, scoped to the same
tenant / workspace / knowledge version, and re-readable.

Failure semantics (fail closed):

* Missing real ``knowledge_version_id``  -> ``NOT_RUN_DEPENDENCY_BLOCKED``
  (DeepSeek1 canonical ingestion must deliver the KnowledgeVersion first;
  the adapter never invents one).
* Missing / invalid / non-visible receipt -> ``BLOCKED`` with the exact
  missing or failed kind.
* Inconsistent tenant / workspace / knowledge_version / index_version
  scope across receipts -> ``BLOCKED`` (``receipt_scope_inconsistent``).
* Missing frozen embedding config hash -> ``BLOCKED``
  (``embedding_config_not_frozen``).

An activated snapshot is deterministic: the same inputs always produce the
same snapshot id, content hash and receipt ref (idempotent, append-only
semantics for the content set — the content set is immutable once frozen).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from .contracts import (
    IndexVisibilityReceipt,
    Neo4jPathVisibilityReceipt,
    validate_index_visibility_receipt,
    validate_neo4j_path_visibility_receipt,
)

SnapshotActivationStatus = Literal[
    "ACTIVATED",
    "NOT_RUN_DEPENDENCY_BLOCKED",
    "BLOCKED",
]

REQUIRED_VISIBILITY_RECEIPT_KINDS = (
    "elasticsearch_bm25_visibility",
    "milvus_vector_visibility",
    "neo4j_graph_visibility",
)


class SnapshotActivationReceipt(BaseModel):
    receipt_ref: str
    receipt_kind: str = "snapshot_activation_receipt"
    tenant_id: str
    workspace_id: str
    knowledge_version_id: str
    snapshot_id: str
    snapshot_content_hash: str
    index_job_manifest_hash: str
    required_receipt_kinds: list[str] = Field(default_factory=list)
    provided_receipt_kinds: list[str] = Field(default_factory=list)
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
    required_receipt_kinds: list[str],
    provided_receipt_kinds: list[str],
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
        "required_receipt_kinds": list(required_receipt_kinds),
        "provided_receipt_kinds": list(provided_receipt_kinds),
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
            "required_receipt_kinds": list(model.required_receipt_kinds),
            "provided_receipt_kinds": list(model.provided_receipt_kinds),
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
    """Canonical owner adapter: consumes index visibility receipts and
    activates a frozen KnowledgeSnapshot only when every gate passes."""

    def activate(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str | None,
        index_job_manifest_hash: str | None,
        visibility_receipts: list[IndexVisibilityReceipt | dict[str, Any]],
        neo4j_path_receipt: Neo4jPathVisibilityReceipt | dict[str, Any] | None = None,
        embedding_config_hash: str | None = None,
        dependency_pr: str | None = None,
        dependency_head_sha: str | None = None,
        observed_at: datetime | None = None,
    ) -> SnapshotActivationResult:
        observed_at = observed_at or datetime.now(timezone.utc)

        # ── Gate 1: real KnowledgeVersion dependency ──────────────────────
        if not str(knowledge_version_id or "").strip():
            receipt = build_snapshot_activation_receipt(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id="",
                snapshot_id="",
                snapshot_content_hash="",
                index_job_manifest_hash=str(index_job_manifest_hash or ""),
                required_receipt_kinds=list(REQUIRED_VISIBILITY_RECEIPT_KINDS),
                provided_receipt_kinds=[],
                receipt_visibility={},
                consistency_checks={"knowledge_version_present": False},
                embedding_config_hash=embedding_config_hash,
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

        # ── Gate 2: receipt kinds complete and authentic ───────────────────
        normalized: dict[str, IndexVisibilityReceipt] = {}
        for raw in visibility_receipts:
            model = raw if isinstance(raw, IndexVisibilityReceipt) else IndexVisibilityReceipt(**raw)
            errors = validate_index_visibility_receipt(model)
            if errors:
                return self._blocked(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    knowledge_version_id=knowledge_version_id,
                    index_job_manifest_hash=index_job_manifest_hash,
                    embedding_config_hash=embedding_config_hash,
                    receipt_visibility={},
                    consistency_checks={"receipt_authenticity": False},
                    block_reason=f"index_visibility_receipt_invalid:{','.join(errors)}",
                    observed_at=observed_at,
                    dependency_pr=dependency_pr,
                    dependency_head_sha=dependency_head_sha,
                )
            normalized[model.receipt_kind] = model

        provided_kinds = sorted(normalized)
        missing = [kind for kind in REQUIRED_VISIBILITY_RECEIPT_KINDS if kind not in normalized]
        if missing:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                embedding_config_hash=embedding_config_hash,
                receipt_visibility={kind: normalized[kind].visibility for kind in provided_kinds},
                consistency_checks={"receipt_kinds_complete": False},
                block_reason=f"index_visibility_receipts_missing:{','.join(missing)}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        receipt_visibility = {
            kind: normalized[kind].visibility for kind in REQUIRED_VISIBILITY_RECEIPT_KINDS
        }
        non_visible = [
            kind for kind, visibility in receipt_visibility.items() if visibility != "visible"
        ]
        if non_visible:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                embedding_config_hash=embedding_config_hash,
                receipt_visibility=receipt_visibility,
                consistency_checks={"all_receipts_visible": False},
                block_reason=f"index_visibility_not_visible:{','.join(non_visible)}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        # ── Gate 3: scope consistency (tenant/workspace/version/index) ─────
        knowledge_space_ids = {r.knowledge_space_id for r in normalized.values()}
        index_versions = {r.index_version for r in normalized.values()}
        consistency_checks = {
            "receipt_kinds_complete": True,
            "all_receipts_visible": True,
            "knowledge_space_consistent": len(knowledge_space_ids) == 1,
            "index_version_consistent": len(index_versions) == 1,
        }
        if neo4j_path_receipt is not None:
            path_model = (
                neo4j_path_receipt
                if isinstance(neo4j_path_receipt, Neo4jPathVisibilityReceipt)
                else Neo4jPathVisibilityReceipt(**neo4j_path_receipt)
            )
            path_errors = validate_neo4j_path_visibility_receipt(path_model)
            if path_errors:
                return self._blocked(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    knowledge_version_id=knowledge_version_id,
                    index_job_manifest_hash=index_job_manifest_hash,
                    embedding_config_hash=embedding_config_hash,
                    receipt_visibility=receipt_visibility,
                    consistency_checks=consistency_checks,
                    block_reason=f"neo4j_path_receipt_invalid:{','.join(path_errors)}",
                    observed_at=observed_at,
                    dependency_pr=dependency_pr,
                    dependency_head_sha=dependency_head_sha,
                )
            consistency_checks["path_tenant_consistent"] = path_model.tenant_id == tenant_id
            consistency_checks["path_workspace_consistent"] = path_model.workspace_id == workspace_id
            consistency_checks["path_knowledge_version_consistent"] = (
                path_model.knowledge_version_id == knowledge_version_id
            )
            if path_model.visibility_status != "visible":
                consistency_checks["path_visibility_visible"] = False
                return self._blocked(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    knowledge_version_id=knowledge_version_id,
                    index_job_manifest_hash=index_job_manifest_hash,
                    embedding_config_hash=embedding_config_hash,
                    receipt_visibility=receipt_visibility,
                    consistency_checks=consistency_checks,
                    block_reason="neo4j_path_visibility_not_visible",
                    observed_at=observed_at,
                    dependency_pr=dependency_pr,
                    dependency_head_sha=dependency_head_sha,
                )
            consistency_checks["path_visibility_visible"] = True

        scope_inconsistent = [
            name for name, ok in consistency_checks.items() if ok is False
        ]
        if scope_inconsistent:
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                embedding_config_hash=embedding_config_hash,
                receipt_visibility=receipt_visibility,
                consistency_checks=consistency_checks,
                block_reason=f"receipt_scope_inconsistent:{','.join(scope_inconsistent)}",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )

        # ── Gate 4: frozen embedding config hash ───────────────────────────
        if not str(embedding_config_hash or "").strip():
            return self._blocked(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
                index_job_manifest_hash=index_job_manifest_hash,
                embedding_config_hash=None,
                receipt_visibility=receipt_visibility,
                consistency_checks=consistency_checks,
                block_reason="embedding_config_not_frozen",
                observed_at=observed_at,
                dependency_pr=dependency_pr,
                dependency_head_sha=dependency_head_sha,
            )
        consistency_checks["embedding_config_frozen"] = True

        # ── Activation: deterministic content set, immutable after freeze ──
        content_payload = {
            "index_job_manifest_hash": str(index_job_manifest_hash or ""),
            "receipt_payload_hashes": sorted(
                r.payload_hash for r in normalized.values()
            ),
            "embedding_config_hash": embedding_config_hash,
            "knowledge_version_id": knowledge_version_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
        }
        snapshot_content_hash = _stable_contract_hash(content_payload)
        snapshot_id = f"snap_{snapshot_content_hash[:16]}"

        receipt = build_snapshot_activation_receipt(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            snapshot_id=snapshot_id,
            snapshot_content_hash=snapshot_content_hash,
            index_job_manifest_hash=str(index_job_manifest_hash or ""),
            required_receipt_kinds=list(REQUIRED_VISIBILITY_RECEIPT_KINDS),
            provided_receipt_kinds=provided_kinds,
            receipt_visibility=receipt_visibility,
            consistency_checks=consistency_checks,
            embedding_config_hash=embedding_config_hash,
            activation_status="ACTIVATED",
            block_reason=None,
            activated_at=observed_at,
        )
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
                "required_receipt_kinds": list(REQUIRED_VISIBILITY_RECEIPT_KINDS),
                "provided_receipt_kinds": provided_kinds,
                "receipt_visibility": receipt_visibility,
                "consistency_checks": consistency_checks,
                "content_set_immutable": True,
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
        embedding_config_hash: str | None,
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
            required_receipt_kinds=list(REQUIRED_VISIBILITY_RECEIPT_KINDS),
            provided_receipt_kinds=sorted(receipt_visibility),
            receipt_visibility=receipt_visibility,
            consistency_checks=consistency_checks,
            embedding_config_hash=embedding_config_hash,
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


def _stable_contract_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "REQUIRED_VISIBILITY_RECEIPT_KINDS",
    "SnapshotActivationAdapter",
    "SnapshotActivationReceipt",
    "SnapshotActivationResult",
    "SnapshotActivationStatus",
    "build_snapshot_activation_receipt",
    "validate_snapshot_activation_receipt",
]
