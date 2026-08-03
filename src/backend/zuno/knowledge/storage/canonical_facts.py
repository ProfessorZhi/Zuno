from __future__ import annotations

"""PHASE22 canonical ingestion PostgreSQL facts — readback verification.

Every query is tenant-scoped. Cross-tenant access must return no rows or raise
:class:`CanonicalFactsTenantMismatch`.

Receipts are reconstructed only from persisted owner rows: the canonical run
row (``canonical_ingestion_runs``), source/document/parse facts
(``ingestion_source_objects``, ``ingestion_document_versions``,
``ingestion_parse_snapshots``), knowledge facts (``knowledge_domain_versions``,
``knowledge_chunks``, ``knowledge_entities``, ``knowledge_relations``) and the
physical object manifest (``infra_object_manifests``). IDs are read, never
reconstructed from naming conventions.
"""


from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine, text


class CanonicalFactsTenantMismatch(RuntimeError):
    pass


class CanonicalFactsMissing(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SourceObjectFact:
    source_object_id: str
    tenant_id: str
    workspace_id: str
    filename: str
    mime_type: str
    declared_format: str
    storage_uri: str
    object_manifest_ref: str
    source_sha256: str
    size_bytes: int
    classification_ref: str
    security_epoch_ref: str
    status: str
    created_at: Any | None = None


@dataclass(frozen=True, slots=True)
class DocumentVersionFact:
    document_version_id: str
    tenant_id: str
    workspace_id: str
    source_object_id: str
    version_no: int
    content_hash: str
    metadata_hash: str
    immutability_ref: str
    status: str
    created_at: Any | None = None


@dataclass(frozen=True, slots=True)
class ParseSnapshotFact:
    parse_snapshot_id: str
    tenant_id: str
    parse_job_id: str
    parse_attempt_id: str
    document_version_id: str
    snapshot_hash: str
    canonical_ir_ref: str
    canonical_ir_schema_ref: str
    parser_id: str
    parser_version: str
    status: str
    canonical_ir: dict[str, Any]
    created_at: Any | None = None


@dataclass(frozen=True, slots=True)
class KnowledgeChunkFact:
    chunk_id: str
    tenant_id: str
    knowledge_version_id: str
    document_version_id: str
    source_span_ref: str
    chunk_hash: str
    acl_ref: str
    authority_ref: str


@dataclass(frozen=True, slots=True)
class KnowledgeVersionFact:
    knowledge_version_id: str
    tenant_id: str
    workspace_id: str
    knowledge_space_id: str
    version_no: int
    document_set_hash: str
    source_span_manifest_hash: str
    index_spec_hash: str
    security_epoch_ref: str
    status: str
    generation: int


@dataclass(frozen=True, slots=True)
class ObjectManifestFact:
    object_ref: str
    owner: str
    content_hash: str
    size_bytes: int
    visibility: str


class CanonicalIngestionFactsStore:
    """Tenant-scoped readback of the canonical ingestion PostgreSQL facts."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    # --- source / document ---------------------------------------------------

    def source_object_fact(self, *, tenant_id: str, source_id: str) -> SourceObjectFact:
        row = self._one(
            """
            SELECT source_object_id, tenant_id, workspace_id, source_kind, filename,
                   mime_type, declared_format, storage_uri, object_manifest_ref,
                   source_sha256, size_bytes, classification_ref, security_epoch_ref,
                   status, created_at
            FROM ingestion_source_objects
            WHERE source_object_id = :source_id AND tenant_id = :tenant_id
            """,
            {"source_id": source_id, "tenant_id": tenant_id},
        )
        return SourceObjectFact(
            source_object_id=str(row["source_object_id"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            filename=str(row["filename"]),
            mime_type=str(row["mime_type"]),
            declared_format=str(row["declared_format"]),
            storage_uri=str(row["storage_uri"]),
            object_manifest_ref=str(row["object_manifest_ref"]),
            source_sha256=str(row["source_sha256"]),
            size_bytes=int(row["size_bytes"]),
            classification_ref=str(row["classification_ref"]),
            security_epoch_ref=str(row["security_epoch_ref"]),
            status=str(row["status"]),
            created_at=row["created_at"],
        )

    def source_object_fact_optional(
        self, *, tenant_id: str, source_id: str
    ) -> SourceObjectFact | None:
        try:
            return self.source_object_fact(tenant_id=tenant_id, source_id=source_id)
        except CanonicalFactsMissing:
            return None

    def source_fact_cross_tenant(
        self, *, owner_tenant_id: str, other_tenant_id: str, source_id: str
    ) -> None:
        """Prove cross-tenant isolation: owner row is invisible to other tenant."""
        row = self._one_optional(
            """
            SELECT source_object_id
            FROM ingestion_source_objects
            WHERE source_object_id = :source_id AND tenant_id = :tenant_id
            """,
            {"source_id": source_id, "tenant_id": other_tenant_id},
        )
        if row is not None:
            raise CanonicalFactsTenantMismatch(
                f"source {source_id} of tenant {owner_tenant_id} is visible to "
                f"tenant {other_tenant_id}"
            )

    def document_version_fact(
        self, *, tenant_id: str, document_version_id: str
    ) -> DocumentVersionFact:
        row = self._one(
            """
            SELECT document_version_id, tenant_id, workspace_id, source_object_id,
                   version_no, content_hash, metadata_hash, immutability_ref,
                   status, created_at
            FROM ingestion_document_versions
            WHERE document_version_id = :document_version_id AND tenant_id = :tenant_id
            """,
            {"document_version_id": document_version_id, "tenant_id": tenant_id},
        )
        return DocumentVersionFact(
            document_version_id=str(row["document_version_id"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            source_object_id=str(row["source_object_id"]),
            version_no=int(row["version_no"]),
            content_hash=str(row["content_hash"]),
            metadata_hash=str(row["metadata_hash"]),
            immutability_ref=str(row["immutability_ref"]),
            status=str(row["status"]),
            created_at=row["created_at"],
        )

    def document_version_fact_for_source(
        self, *, tenant_id: str, source_id: str
    ) -> DocumentVersionFact:
        """Read the document version from the owner table by its source binding."""
        row = self._one(
            """
            SELECT document_version_id, tenant_id, workspace_id, source_object_id,
                   version_no, content_hash, metadata_hash, immutability_ref,
                   status, created_at
            FROM ingestion_document_versions
            WHERE source_object_id = :source_id AND tenant_id = :tenant_id
            ORDER BY version_no
            LIMIT 1
            """,
            {"source_id": source_id, "tenant_id": tenant_id},
        )
        return DocumentVersionFact(
            document_version_id=str(row["document_version_id"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            source_object_id=str(row["source_object_id"]),
            version_no=int(row["version_no"]),
            content_hash=str(row["content_hash"]),
            metadata_hash=str(row["metadata_hash"]),
            immutability_ref=str(row["immutability_ref"]),
            status=str(row["status"]),
            created_at=row["created_at"],
        )

    def parse_snapshot_fact_for_document(
        self, *, tenant_id: str, document_version_id: str
    ) -> ParseSnapshotFact:
        """Read the canonical IR snapshot from the owner table by document."""
        row = self._one(
            """
            SELECT parse_snapshot_id, tenant_id, parse_job_id, parse_attempt_id,
                   document_version_id, snapshot_hash, canonical_ir_json,
                   canonical_ir_ref, canonical_ir_schema_ref, parser_id,
                   parser_version, status, created_at
            FROM ingestion_parse_snapshots
            WHERE document_version_id = :document_version_id
              AND tenant_id = :tenant_id
            ORDER BY created_at
            LIMIT 1
            """,
            {"document_version_id": document_version_id, "tenant_id": tenant_id},
        )
        return ParseSnapshotFact(
            parse_snapshot_id=str(row["parse_snapshot_id"]),
            tenant_id=str(row["tenant_id"]),
            parse_job_id=str(row["parse_job_id"]),
            parse_attempt_id=str(row["parse_attempt_id"]),
            document_version_id=str(row["document_version_id"]),
            snapshot_hash=str(row["snapshot_hash"]),
            canonical_ir_ref=str(row["canonical_ir_ref"]),
            canonical_ir_schema_ref=str(row["canonical_ir_schema_ref"]),
            parser_id=str(row["parser_id"]),
            parser_version=str(row["parser_version"]),
            status=str(row["status"]),
            canonical_ir=dict(row["canonical_ir_json"] or {}),
            created_at=row["created_at"],
        )

    def parse_snapshot_fact(
        self, *, tenant_id: str, parse_snapshot_id: str
    ) -> ParseSnapshotFact:
        row = self._one(
            """
            SELECT parse_snapshot_id, tenant_id, parse_job_id, parse_attempt_id,
                   document_version_id, snapshot_hash, canonical_ir_json,
                   canonical_ir_ref, canonical_ir_schema_ref, parser_id,
                   parser_version, status, created_at
            FROM ingestion_parse_snapshots
            WHERE parse_snapshot_id = :parse_snapshot_id AND tenant_id = :tenant_id
            """,
            {"parse_snapshot_id": parse_snapshot_id, "tenant_id": tenant_id},
        )
        return ParseSnapshotFact(
            parse_snapshot_id=str(row["parse_snapshot_id"]),
            tenant_id=str(row["tenant_id"]),
            parse_job_id=str(row["parse_job_id"]),
            parse_attempt_id=str(row["parse_attempt_id"]),
            document_version_id=str(row["document_version_id"]),
            snapshot_hash=str(row["snapshot_hash"]),
            canonical_ir_ref=str(row["canonical_ir_ref"]),
            canonical_ir_schema_ref=str(row["canonical_ir_schema_ref"]),
            parser_id=str(row["parser_id"]),
            parser_version=str(row["parser_version"]),
            status=str(row["status"]),
            canonical_ir=dict(row["canonical_ir_json"] or {}),
            created_at=row["created_at"],
        )

    # --- knowledge version + chunks -------------------------------------------

    def knowledge_version_fact(
        self, *, tenant_id: str, knowledge_version_id: str
    ) -> KnowledgeVersionFact:
        row = self._one(
            """
            SELECT knowledge_version_id, tenant_id, workspace_id, knowledge_space_id,
                   version_no, document_set_hash, source_span_manifest_hash,
                   index_spec_hash, security_epoch_ref, status, generation
            FROM knowledge_domain_versions
            WHERE knowledge_version_id = :knowledge_version_id AND tenant_id = :tenant_id
            """,
            {"knowledge_version_id": knowledge_version_id, "tenant_id": tenant_id},
        )
        return KnowledgeVersionFact(
            knowledge_version_id=str(row["knowledge_version_id"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            knowledge_space_id=str(row["knowledge_space_id"]),
            version_no=int(row["version_no"]),
            document_set_hash=str(row["document_set_hash"]),
            source_span_manifest_hash=str(row["source_span_manifest_hash"]),
            index_spec_hash=str(row["index_spec_hash"]),
            security_epoch_ref=str(row["security_epoch_ref"]),
            status=str(row["status"]),
            generation=int(row["generation"]),
        )

    def chunk_facts(
        self, *, tenant_id: str, knowledge_version_id: str
    ) -> tuple[KnowledgeChunkFact, ...]:
        rows = self._all(
            """
            SELECT chunk_id, tenant_id, knowledge_version_id, document_version_id,
                   source_span_ref, chunk_hash, acl_ref, authority_ref
            FROM knowledge_chunks
            WHERE tenant_id = :tenant_id AND knowledge_version_id = :knowledge_version_id
            ORDER BY chunk_id
            """,
            {
                "tenant_id": tenant_id,
                "knowledge_version_id": knowledge_version_id,
            },
        )
        return tuple(
            KnowledgeChunkFact(
                chunk_id=str(row["chunk_id"]),
                tenant_id=str(row["tenant_id"]),
                knowledge_version_id=str(row["knowledge_version_id"]),
                document_version_id=str(row["document_version_id"]),
                source_span_ref=str(row["source_span_ref"]),
                chunk_hash=str(row["chunk_hash"]),
                acl_ref=str(row["acl_ref"]),
                authority_ref=str(row["authority_ref"]),
            )
            for row in rows
        )

    def knowledge_version_for_document_set(
        self, *, tenant_id: str, workspace_id: str, knowledge_space_id: str, document_set_hash: str
    ) -> KnowledgeVersionFact | None:
        """Find an existing knowledge version bound to the same document set."""
        row = self._one_optional(
            """
            SELECT knowledge_version_id, tenant_id, workspace_id, knowledge_space_id,
                   version_no, document_set_hash, source_span_manifest_hash,
                   index_spec_hash, security_epoch_ref, status, generation
            FROM knowledge_domain_versions
            WHERE tenant_id = :tenant_id
              AND workspace_id = :workspace_id
              AND knowledge_space_id = :knowledge_space_id
              AND document_set_hash = :document_set_hash
            ORDER BY version_no
            LIMIT 1
            """,
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "knowledge_space_id": knowledge_space_id,
                "document_set_hash": document_set_hash,
            },
        )
        if row is None:
            return None
        return KnowledgeVersionFact(
            knowledge_version_id=str(row["knowledge_version_id"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            knowledge_space_id=str(row["knowledge_space_id"]),
            version_no=int(row["version_no"]),
            document_set_hash=str(row["document_set_hash"]),
            source_span_manifest_hash=str(row["source_span_manifest_hash"]),
            index_spec_hash=str(row["index_spec_hash"]),
            security_epoch_ref=str(row["security_epoch_ref"]),
            status=str(row["status"]),
            generation=int(row["generation"]),
        )

    # --- object manifest --------------------------------------------------------

    def object_manifest_fact(self, *, object_ref: str) -> ObjectManifestFact:
        row = self._one(
            """
            SELECT object_ref, owner, content_hash, size_bytes, visibility
            FROM infra_object_manifests
            WHERE object_ref = :object_ref
            """,
            {"object_ref": object_ref},
        )
        return ObjectManifestFact(
            object_ref=str(row["object_ref"]),
            owner=str(row["owner"]),
            content_hash=str(row["content_hash"]),
            size_bytes=int(row["size_bytes"]),
            visibility=str(row["visibility"]),
        )

    def object_manifest_fact_optional(self, *, object_ref: str) -> ObjectManifestFact | None:
        try:
            return self.object_manifest_fact(object_ref=object_ref)
        except CanonicalFactsMissing:
            return None

    # --- helpers ---------------------------------------------------------------

    def _one(self, sql: str, params: dict[str, Any]) -> dict[str, Any]:
        with self.engine.connect() as connection:
            row = connection.execute(text(sql), params).mappings().first()
        if row is None:
            raise CanonicalFactsMissing("canonical ingestion fact not found")
        return dict(row)

    def _one_optional(self, sql: str, params: dict[str, Any]) -> dict[str, Any] | None:
        with self.engine.connect() as connection:
            row = connection.execute(text(sql), params).mappings().first()
        return None if row is None else dict(row)

    def _all(self, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(text(sql), params).mappings().all()
        return [dict(row) for row in rows]


__all__ = [
    "CanonicalFactsMissing",
    "CanonicalFactsTenantMismatch",
    "CanonicalIngestionFactsStore",
    "DocumentVersionFact",
    "KnowledgeChunkFact",
    "KnowledgeVersionFact",
    "ObjectManifestFact",
    "ParseSnapshotFact",
    "SourceObjectFact",
]
