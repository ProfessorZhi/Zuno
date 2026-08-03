from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


IndexTarget = Literal["bm25", "vector", "graph"]
Neo4jPathVisibilityStatus = Literal["visible", "hidden", "inconsistent"]
IndexVisibilityStatus = Literal["visible", "hidden"]


class IndexAdapterContract(BaseModel):
    adapter_id: str
    target: IndexTarget
    engine: str
    runtime_status: Literal["current", "target_blocked"]
    external_service: bool = False
    operations: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None


class KnowledgeSpaceManifest(BaseModel):
    knowledge_space_id: str
    workspace_id: str
    graph_project_id: str | None = None
    index_version: str
    status: Literal["created", "ready", "failed"] = "created"


class IndexJobManifest(BaseModel):
    job_id: str
    knowledge_space_id: str
    workspace_id: str
    document_id: str
    source_uri: str
    index_version: str
    targets: list[IndexTarget] = Field(default_factory=list)
    target_status: dict[str, str] = Field(default_factory=dict)
    status: Literal["succeeded", "failed"]
    error: str | None = None
    retry_count: int = 0
    previous_job_id: str | None = None
    graph_project_ref: str | None = None
    source_block_ids: list[str] = Field(default_factory=list)
    source_provenance: dict[str, Any] = Field(default_factory=dict)
    acl_scopes: list[str] = Field(default_factory=list)
    sensitivity_tags: list[str] = Field(default_factory=list)
    adapter_status: dict[str, str] = Field(default_factory=dict)
    adapter_dispatch_receipts: dict[str, dict[str, Any]] = Field(default_factory=dict)
    adapter_visibility_receipts: dict[str, dict[str, Any]] = Field(default_factory=dict)
    parse_job_id: str | None = None
    parse_attempt_id: str | None = None
    document_version_id: str = ""
    source_sha256: str = ""
    parser_config_hash: str = ""
    ir_schema_version: str = ""
    diagnostics_digest: str = ""
    parser_diagnostics: list[dict[str, Any]] = Field(default_factory=list)
    block_count: int = 0
    table_count: int = 0
    figure_count: int = 0


class IndexQueryResult(BaseModel):
    knowledge_space_id: str
    index_version: str
    query: str
    documents_by_source: dict[str, list[dict]] = Field(default_factory=dict)
    manifest: IndexJobManifest


class IndexVisibilityReceipt(BaseModel):
    receipt_ref: str
    receipt_kind: str
    adapter_target: IndexTarget
    adapter_id: str
    adapter_dispatch_ref: str | None = None
    adapter_status: str
    visibility: IndexVisibilityStatus
    visibility_failure_reason: str | None = None
    sample_query: str
    sample_match_count: int
    knowledge_space_id: str
    index_version: str
    document_id: str
    document_version_id: str
    source_block_count: int
    payload_hash: str


def build_index_visibility_receipt(
    *,
    adapter_target: IndexTarget,
    adapter_id: str,
    adapter_dispatch_ref: str | None,
    adapter_status: str,
    visibility: IndexVisibilityStatus,
    visibility_failure_reason: str | None,
    sample_query: str,
    sample_match_count: int,
    knowledge_space_id: str,
    index_version: str,
    document_id: str,
    document_version_id: str,
    source_block_count: int,
) -> IndexVisibilityReceipt:
    receipt_kind = _visibility_receipt_kind(adapter_target=adapter_target, adapter_id=adapter_id)
    payload = {
        "receipt_kind": receipt_kind,
        "adapter_target": adapter_target,
        "adapter_id": adapter_id,
        "adapter_dispatch_ref": adapter_dispatch_ref,
        "adapter_status": adapter_status,
        "visibility": visibility,
        "visibility_failure_reason": visibility_failure_reason,
        "sample_query": sample_query,
        "sample_match_count": sample_match_count,
        "knowledge_space_id": knowledge_space_id,
        "index_version": index_version,
        "document_id": document_id,
        "document_version_id": document_version_id,
        "source_block_count": source_block_count,
    }
    payload_hash = _stable_contract_hash(payload)
    receipt = IndexVisibilityReceipt(
        receipt_ref=f"index-visibility:{adapter_target}:{payload_hash[:16]}",
        payload_hash=payload_hash,
        **payload,
    )
    errors = validate_index_visibility_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    return receipt


def validate_index_visibility_receipt(receipt: IndexVisibilityReceipt | dict[str, Any]) -> list[str]:
    model = receipt if isinstance(receipt, IndexVisibilityReceipt) else IndexVisibilityReceipt(**receipt)
    errors: list[str] = []
    for field_name in [
        "receipt_ref",
        "receipt_kind",
        "adapter_target",
        "adapter_id",
        "adapter_status",
        "sample_query",
        "knowledge_space_id",
        "index_version",
        "document_id",
        "document_version_id",
        "payload_hash",
    ]:
        if not str(getattr(model, field_name) or "").strip():
            errors.append(f"{field_name} is required")
    if model.visibility == "visible":
        if model.visibility_failure_reason is not None:
            errors.append("visible receipt must not include visibility_failure_reason")
        if model.sample_match_count < 1:
            errors.append("visible receipt requires sample_match_count >= 1")
    if model.visibility == "hidden":
        if not model.visibility_failure_reason:
            errors.append("hidden receipt requires visibility_failure_reason")
        if model.sample_match_count != 0:
            errors.append("hidden receipt requires sample_match_count == 0")
    expected_kind = _visibility_receipt_kind(adapter_target=model.adapter_target, adapter_id=model.adapter_id)
    if model.receipt_kind != expected_kind:
        errors.append("receipt_kind mismatch")
    expected_hash = _stable_contract_hash(
        {
            "receipt_kind": model.receipt_kind,
            "adapter_target": model.adapter_target,
            "adapter_id": model.adapter_id,
            "adapter_dispatch_ref": model.adapter_dispatch_ref,
            "adapter_status": model.adapter_status,
            "visibility": model.visibility,
            "visibility_failure_reason": model.visibility_failure_reason,
            "sample_query": model.sample_query,
            "sample_match_count": model.sample_match_count,
            "knowledge_space_id": model.knowledge_space_id,
            "index_version": model.index_version,
            "document_id": model.document_id,
            "document_version_id": model.document_version_id,
            "source_block_count": model.source_block_count,
        }
    )
    if model.payload_hash != expected_hash:
        errors.append("payload_hash mismatch")
    if model.receipt_ref != f"index-visibility:{model.adapter_target}:{expected_hash[:16]}":
        errors.append("receipt_ref must be derived from payload_hash")
    return errors


class Neo4jPathVisibilityReceipt(BaseModel):
    receipt_id: str
    tenant_id: str
    workspace_id: str
    knowledge_version_id: str
    snapshot_id: str
    query_kind: str
    start_entity_ref: str
    end_entity_ref: str
    relation_kinds: list[str] = Field(default_factory=list)
    path_length: int
    matched_node_refs: list[str] = Field(default_factory=list)
    matched_relation_refs: list[str] = Field(default_factory=list)
    adapter_execution_ref: str
    visibility_status: Neo4jPathVisibilityStatus
    observed_at: datetime
    config_hash: str
    payload_hash: str


def build_neo4j_path_visibility_receipt(
    *,
    tenant_id: str,
    workspace_id: str,
    knowledge_version_id: str,
    snapshot_id: str,
    query_kind: str,
    start_entity_ref: str,
    end_entity_ref: str,
    relation_kinds: list[str],
    matched_node_refs: list[str],
    matched_relation_refs: list[str],
    adapter_execution_ref: str,
    visibility_status: Neo4jPathVisibilityStatus,
    observed_at: datetime,
    config_hash: str,
) -> Neo4jPathVisibilityReceipt:
    path_length = len(matched_relation_refs)
    payload = {
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "knowledge_version_id": knowledge_version_id,
        "snapshot_id": snapshot_id,
        "query_kind": query_kind,
        "start_entity_ref": start_entity_ref,
        "end_entity_ref": end_entity_ref,
        "relation_kinds": list(relation_kinds),
        "path_length": path_length,
        "matched_node_refs": list(matched_node_refs),
        "matched_relation_refs": list(matched_relation_refs),
        "adapter_execution_ref": adapter_execution_ref,
        "visibility_status": visibility_status,
        "observed_at": observed_at.isoformat(),
        "config_hash": config_hash,
    }
    payload_hash = _stable_contract_hash(payload)
    receipt = Neo4jPathVisibilityReceipt(
        receipt_id=f"neo4j-path-visibility:{payload_hash[:16]}",
        payload_hash=payload_hash,
        **payload,
    )
    errors = validate_neo4j_path_visibility_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    return receipt


def validate_neo4j_path_visibility_receipt(receipt: Neo4jPathVisibilityReceipt | dict[str, Any]) -> list[str]:
    model = receipt if isinstance(receipt, Neo4jPathVisibilityReceipt) else Neo4jPathVisibilityReceipt(**receipt)
    errors: list[str] = []
    required_text_fields = [
        "receipt_id",
        "tenant_id",
        "workspace_id",
        "knowledge_version_id",
        "snapshot_id",
        "query_kind",
        "start_entity_ref",
        "end_entity_ref",
        "adapter_execution_ref",
        "config_hash",
        "payload_hash",
    ]
    for field_name in required_text_fields:
        if not str(getattr(model, field_name) or "").strip():
            errors.append(f"{field_name} is required")
    if model.visibility_status == "visible":
        if model.path_length < 1:
            errors.append("visible path receipt requires path_length >= 1")
        if len(model.matched_relation_refs) != model.path_length:
            errors.append("matched_relation_refs must match path_length")
        if len(model.relation_kinds) != model.path_length:
            errors.append("relation_kinds must match path_length")
        if len(model.matched_node_refs) != model.path_length + 1:
            errors.append("matched_node_refs must contain path_length + 1 nodes")
        if model.matched_node_refs and model.matched_node_refs[0] != model.start_entity_ref:
            errors.append("matched_node_refs must start with start_entity_ref")
        if model.matched_node_refs and model.matched_node_refs[-1] != model.end_entity_ref:
            errors.append("matched_node_refs must end with end_entity_ref")
    if model.visibility_status in {"hidden", "inconsistent"} and model.receipt_id.startswith("neo4j-path-visibility:"):
        errors.append("hidden or inconsistent path readback must not emit a valid visibility receipt_id")
    expected_hash = _stable_contract_hash(
        {
            "tenant_id": model.tenant_id,
            "workspace_id": model.workspace_id,
            "knowledge_version_id": model.knowledge_version_id,
            "snapshot_id": model.snapshot_id,
            "query_kind": model.query_kind,
            "start_entity_ref": model.start_entity_ref,
            "end_entity_ref": model.end_entity_ref,
            "relation_kinds": model.relation_kinds,
            "path_length": model.path_length,
            "matched_node_refs": model.matched_node_refs,
            "matched_relation_refs": model.matched_relation_refs,
            "adapter_execution_ref": model.adapter_execution_ref,
            "visibility_status": model.visibility_status,
            "observed_at": model.observed_at.isoformat(),
            "config_hash": model.config_hash,
        }
    )
    if model.payload_hash != expected_hash:
        errors.append("payload_hash mismatch")
    if model.receipt_id != f"neo4j-path-visibility:{expected_hash[:16]}":
        errors.append("receipt_id must be derived from payload_hash")
    return errors


def _stable_contract_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _visibility_receipt_kind(*, adapter_target: IndexTarget, adapter_id: str) -> str:
    if adapter_id == "elasticsearch" and adapter_target == "bm25":
        return "elasticsearch_bm25_visibility"
    if adapter_id == "milvus" and adapter_target == "vector":
        return "milvus_vector_visibility"
    if adapter_id == "neo4j" and adapter_target == "graph":
        return "neo4j_graph_visibility"
    return f"{adapter_id}_{adapter_target}_visibility"


__all__ = [
    "IndexAdapterContract",
    "IndexJobManifest",
    "IndexQueryResult",
    "IndexTarget",
    "IndexVisibilityReceipt",
    "IndexVisibilityStatus",
    "KnowledgeSpaceManifest",
    "Neo4jPathVisibilityReceipt",
    "Neo4jPathVisibilityStatus",
    "build_index_visibility_receipt",
    "build_neo4j_path_visibility_receipt",
    "validate_index_visibility_receipt",
    "validate_neo4j_path_visibility_receipt",
]
