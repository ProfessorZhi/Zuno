"""Corpus-level IndexBuildRun and visibility receipt (PHASE22 GAP-B3 hardening).

A corpus-level index build binds ONE KnowledgeVersion to ONE immutable
chunk set and produces ONE receipt per index kind (elasticsearch_bm25 /
milvus_vector / neo4j_graph).  The receipt is the formal input to snapshot
activation.

Truth boundary:

* The canonical input identity must be exact: the frozen candidate
  manifest's document count, chunk count, chunk id set and per-chunk text
  hashes are validated before anything is written.  Re-chunking is
  forbidden — the adapter consumes the canonical chunk set as-is.
* While no real KnowledgeVersion exists (DeepSeek1 dependency), the
  corpus-level receipt stays ``NOT_RUN_DEPENDENCY_BLOCKED`` with
  ``visibility_status="blocked"``.  Adapter smoke runs are explicitly
  scoped ``receipt_scope="adapter_live_smoke"`` with
  ``snapshot_eligible=false``; smoke receipts can never activate a
  snapshot.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

CorpusIndexBuildStatus = Literal[
    "COMPLETED",
    "NOT_RUN_DEPENDENCY_BLOCKED",
    "BLOCKED",
]
ReceiptScope = Literal["adapter_live_smoke", "formal"]
IndexKind = Literal["elasticsearch_bm25", "milvus_vector", "neo4j_graph"]

CORPUS_INDEX_KINDS: tuple[IndexKind, ...] = (
    "elasticsearch_bm25",
    "milvus_vector",
    "neo4j_graph",
)


class CorpusIndexBuildReceipt(BaseModel):
    receipt_ref: str
    receipt_kind: str = "corpus_index_build_receipt"
    index_kind: IndexKind
    receipt_scope: ReceiptScope
    input_kind: str
    not_owner_produced: bool
    snapshot_eligible: bool
    tenant_id: str
    workspace_id: str
    knowledge_version_id: str
    index_build_run_id: str
    expected_document_count: int
    expected_chunk_count: int
    observed_document_count: int
    observed_chunk_count: int
    content_set_hash: str
    config_hash: str
    adapter_execution_ref: str
    readback_hash: str
    visibility_status: Literal["visible", "blocked"]
    block_reason: str | None = None
    payload_hash: str


def build_corpus_index_build_receipt(
    *,
    index_kind: IndexKind,
    receipt_scope: ReceiptScope,
    input_kind: str,
    not_owner_produced: bool,
    snapshot_eligible: bool,
    tenant_id: str,
    workspace_id: str,
    knowledge_version_id: str,
    index_build_run_id: str,
    expected_document_count: int,
    expected_chunk_count: int,
    observed_document_count: int,
    observed_chunk_count: int,
    content_set_hash: str,
    config_hash: str,
    adapter_execution_ref: str,
    readback_hash: str,
    visibility_status: Literal["visible", "blocked"],
    block_reason: str | None,
) -> CorpusIndexBuildReceipt:
    payload = {
        "receipt_kind": "corpus_index_build_receipt",
        "index_kind": index_kind,
        "receipt_scope": receipt_scope,
        "input_kind": input_kind,
        "not_owner_produced": not_owner_produced,
        "snapshot_eligible": snapshot_eligible,
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "knowledge_version_id": knowledge_version_id,
        "index_build_run_id": index_build_run_id,
        "expected_document_count": expected_document_count,
        "expected_chunk_count": expected_chunk_count,
        "observed_document_count": observed_document_count,
        "observed_chunk_count": observed_chunk_count,
        "content_set_hash": content_set_hash,
        "config_hash": config_hash,
        "adapter_execution_ref": adapter_execution_ref,
        "readback_hash": readback_hash,
        "visibility_status": visibility_status,
        "block_reason": block_reason,
    }
    payload_hash = _stable_contract_hash(payload)
    receipt = CorpusIndexBuildReceipt(
        receipt_ref=f"corpus-index-build:{index_kind}:{payload_hash[:16]}",
        payload_hash=payload_hash,
        **payload,
    )
    errors = validate_corpus_index_build_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    return receipt


def validate_corpus_index_build_receipt(
    receipt: CorpusIndexBuildReceipt | dict[str, Any],
) -> list[str]:
    model = (
        receipt
        if isinstance(receipt, CorpusIndexBuildReceipt)
        else CorpusIndexBuildReceipt(**receipt)
    )
    errors: list[str] = []
    if model.receipt_kind != "corpus_index_build_receipt":
        errors.append("receipt_kind mismatch")
    if model.index_kind not in CORPUS_INDEX_KINDS:
        errors.append(f"unknown index_kind: {model.index_kind}")
    if model.visibility_status == "visible":
        if not model.knowledge_version_id:
            errors.append("visible corpus receipt requires knowledge_version_id")
        if model.snapshot_eligible is not True:
            errors.append("visible corpus receipt requires snapshot_eligible=true")
        if model.receipt_scope != "formal":
            errors.append("visible corpus receipt requires formal receipt_scope")
        if model.block_reason is not None:
            errors.append("visible receipt must not include block_reason")
        if model.observed_document_count != model.expected_document_count:
            errors.append("observed_document_count must equal expected_document_count")
        if model.observed_chunk_count != model.expected_chunk_count:
            errors.append("observed_chunk_count must equal expected_chunk_count")
        if model.observed_chunk_count < 1:
            errors.append("visible receipt requires observed_chunk_count >= 1")
    else:
        if model.visibility_status != "blocked":
            errors.append(f"unknown visibility_status: {model.visibility_status}")
        if not model.block_reason:
            errors.append("blocked receipt requires block_reason")
        if model.snapshot_eligible is not False:
            errors.append("blocked corpus receipt must keep snapshot_eligible=false")
        if model.knowledge_version_id:
            errors.append("blocked corpus receipt must not carry a knowledge_version_id")
    expected_hash = _stable_contract_hash(
        {
            "receipt_kind": model.receipt_kind,
            "index_kind": model.index_kind,
            "receipt_scope": model.receipt_scope,
            "input_kind": model.input_kind,
            "not_owner_produced": model.not_owner_produced,
            "snapshot_eligible": model.snapshot_eligible,
            "tenant_id": model.tenant_id,
            "workspace_id": model.workspace_id,
            "knowledge_version_id": model.knowledge_version_id,
            "index_build_run_id": model.index_build_run_id,
            "expected_document_count": model.expected_document_count,
            "expected_chunk_count": model.expected_chunk_count,
            "observed_document_count": model.observed_document_count,
            "observed_chunk_count": model.observed_chunk_count,
            "content_set_hash": model.content_set_hash,
            "config_hash": model.config_hash,
            "adapter_execution_ref": model.adapter_execution_ref,
            "readback_hash": model.readback_hash,
            "visibility_status": model.visibility_status,
            "block_reason": model.block_reason,
        }
    )
    if model.payload_hash != expected_hash:
        errors.append("payload_hash mismatch")
    if model.receipt_ref != f"corpus-index-build:{model.index_kind}:{expected_hash[:16]}":
        errors.append("receipt_ref must be derived from payload_hash")
    return errors


@dataclass(frozen=True, slots=True)
class FrozenCorpusPayload:
    """The exact canonical chunk set consumed by an IndexBuildRun."""

    input_kind: str
    not_owner_produced: bool
    document_count: int
    chunk_count: int
    chunk_ids: tuple[str, ...]
    chunks: tuple[dict[str, Any], ...]
    content_set_hash: str
    identity_checks: dict[str, Any]


class CorpusInputIdentityError(RuntimeError):
    """Raised when the input does not match the canonical manifest exactly."""


def validate_canonical_corpus_identity(
    *,
    source_manifest: dict[str, Any],
    canonical_ir_manifest: dict[str, Any],
    corpus_root: Any,
    manifest_chunk_texts: dict[str, str],
) -> FrozenCorpusPayload:
    """Validate exact identity against the frozen candidate manifest.

    Rules (fail closed, no re-chunking):
    1. document count equal;
    2. chunk count equal;
    3. chunk id set equal;
    4. every chunk text hash equal to the manifest text_hash;
    5. no extra text and no missing chunk.
    """
    checks: dict[str, Any] = {}
    documents = canonical_ir_manifest["documents"]
    chunks = canonical_ir_manifest["chunks"]
    expected_document_count = canonical_ir_manifest["document_count"]
    expected_chunk_count = canonical_ir_manifest["chunk_count"]

    checks["document_count_equal"] = len(documents) == expected_document_count == len(
        list(corpus_root.glob("*.md"))
    )
    checks["chunk_count_equal"] = len(chunks) == expected_chunk_count
    checks["chunk_id_set_equal"] = len(manifest_chunk_texts) == len(chunks) and set(
        manifest_chunk_texts
    ) == {chunk["chunk_id"] for chunk in chunks}

    hash_mismatches: list[str] = []
    for chunk in chunks:
        text = manifest_chunk_texts.get(chunk["chunk_id"])
        if text is None:
            hash_mismatches.append(f"{chunk['chunk_id']}:missing_text")
            continue
        actual_hash = _sha256_json({"text": text})
        if actual_hash != chunk["text_hash"]:
            hash_mismatches.append(
                f"{chunk['chunk_id']}:{actual_hash[:12]}!={chunk['text_hash'][:12]}"
            )
    checks["chunk_hash_mismatch_count"] = len(hash_mismatches)
    checks["chunk_hashes_all_equal"] = not hash_mismatches

    failures = [
        name
        for name, ok in checks.items()
        if ok is False
    ]
    if failures or hash_mismatches:
        raise CorpusInputIdentityError(
            f"canonical corpus identity mismatch: {','.join(failures)}; {len(hash_mismatches)} hash mismatches"
        )

    documents_by_id = {doc["document_id"]: doc for doc in documents}
    chunks_by_id = {chunk["chunk_id"]: chunk for chunk in chunks}
    payload_chunks = []
    for chunk in chunks:
        doc = documents_by_id[chunk["document_id"]]
        payload_chunks.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "tenant_id": chunk["tenant_id"],
                "workspace_id": chunk["workspace_id"],
                "document_version_id": chunk["document_version_id"],
                "content": manifest_chunk_texts[chunk["chunk_id"]],
            }
        )
    content_set_hash = _stable_contract_hash(
        {
            "canonical_ir_hash": canonical_ir_manifest["canonical_ir_hash"],
            "chunk_ids": sorted(chunks_by_id),
            "chunk_text_hashes": sorted(
                chunk["text_hash"] for chunk in chunks
            ),
        }
    )
    return FrozenCorpusPayload(
        input_kind="frozen_candidate_manifest",
        not_owner_produced=True,
        document_count=len(documents),
        chunk_count=len(chunks),
        chunk_ids=tuple(sorted(chunks_by_id)),
        chunks=tuple(payload_chunks),
        content_set_hash=content_set_hash,
        identity_checks=checks,
    )


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _stable_contract_hash(payload: dict[str, Any]) -> str:
    return _sha256_json(payload)


__all__ = [
    "CORPUS_INDEX_KINDS",
    "CorpusIndexBuildReceipt",
    "CorpusIndexBuildStatus",
    "CorpusInputIdentityError",
    "FrozenCorpusPayload",
    "IndexKind",
    "ReceiptScope",
    "build_corpus_index_build_receipt",
    "validate_canonical_corpus_identity",
    "validate_corpus_index_build_receipt",
]
