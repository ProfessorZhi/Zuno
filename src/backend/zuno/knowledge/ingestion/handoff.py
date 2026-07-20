from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field

from .contracts import CanonicalDocumentIR, ParseJobSnapshot, build_source_span_provenance
from .review import QualityGateResult


class IndexableDocumentSnapshotV1(BaseModel):
    indexable_snapshot_id: str
    document_version_id: str
    parse_snapshot_id: str
    quality_decision_id: str
    workspace_id: str
    document_id: str
    canonical_hash: str
    idempotency_key: str
    parser_version: str
    ir_schema_version: str
    source_span_refs: list[dict[str, Any]] = Field(default_factory=list)
    security_refs: dict[str, Any] = Field(default_factory=dict)
    delete_refs: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)


class SnapshotOutboxEvent(BaseModel):
    outbox_event_id: str
    aggregate_ref: str
    event_type: str = "indexable_document_snapshot.ready"
    payload_hash: str
    idempotency_key: str
    publish_status: str = "pending"
    replay_count: int = 0


class SnapshotHandoffRuntime:
    schema_version = "indexable-document-snapshot-v1"

    def create_snapshot(
        self,
        *,
        document: CanonicalDocumentIR,
        parse_snapshot: ParseJobSnapshot,
        quality_gate: QualityGateResult,
        visibility_ref: str,
        delete_refs: list[str] | None = None,
    ) -> tuple[IndexableDocumentSnapshotV1, SnapshotOutboxEvent]:
        canonical_payload = {
            "schema_version": self.schema_version,
            "document": document.model_dump(),
            "parse_snapshot_ref": parse_snapshot.job_id,
            "quality_decision_id": quality_gate.quality_decision_id,
            "visibility_ref": visibility_ref,
            "delete_refs": list(delete_refs or []),
        }
        canonical_hash = _hash(canonical_payload)
        idempotency_key = _hash(
            {
                "document_version_id": document.metadata.document_version_id,
                "parse_snapshot_id": parse_snapshot.job_id,
                "quality_decision_id": quality_gate.quality_decision_id,
                "canonical_hash": canonical_hash,
            }
        )
        snapshot_id = f"snapshot_{idempotency_key[:24]}"
        snapshot = IndexableDocumentSnapshotV1(
            indexable_snapshot_id=snapshot_id,
            document_version_id=document.metadata.document_version_id,
            parse_snapshot_id=parse_snapshot.job_id,
            quality_decision_id=quality_gate.quality_decision_id,
            workspace_id=document.metadata.workspace_id,
            document_id=document.metadata.document_id,
            canonical_hash=canonical_hash,
            idempotency_key=idempotency_key,
            parser_version=document.metadata.parser_version,
            ir_schema_version=document.metadata.ir_schema_version,
            source_span_refs=[
                build_source_span_provenance(
                    document=document,
                    block=block,
                    chunk_id=f"{document.metadata.document_id}::{block.block_id}",
                )
                for block in document.blocks
            ],
            security_refs={
                "acl_scope": document.metadata.acl_scope,
                "sensitivity_tags": list(document.metadata.sensitivity_tags),
                "visibility_ref": visibility_ref,
            },
            delete_refs=list(delete_refs or []),
            payload=canonical_payload,
        )
        outbox_payload = {
            "indexable_snapshot_id": snapshot.indexable_snapshot_id,
            "document_version_id": snapshot.document_version_id,
            "quality_decision_id": snapshot.quality_decision_id,
            "canonical_hash": snapshot.canonical_hash,
            "idempotency_key": snapshot.idempotency_key,
        }
        outbox = SnapshotOutboxEvent(
            outbox_event_id=f"outbox_{snapshot.indexable_snapshot_id}",
            aggregate_ref=snapshot.indexable_snapshot_id,
            payload_hash=_hash(outbox_payload),
            idempotency_key=snapshot.idempotency_key,
        )
        return snapshot, outbox

    @staticmethod
    def duplicate_handoff(
        existing: IndexableDocumentSnapshotV1,
        candidate: IndexableDocumentSnapshotV1,
    ) -> bool:
        return existing.idempotency_key == candidate.idempotency_key


def _hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


__all__ = [
    "IndexableDocumentSnapshotV1",
    "SnapshotHandoffRuntime",
    "SnapshotOutboxEvent",
]
