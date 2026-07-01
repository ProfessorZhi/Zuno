from __future__ import annotations

import hashlib
import json
import re
from uuid import uuid4

from zuno.knowledge.ingestion import CanonicalDocumentIR, ParseJobSnapshot, build_index_handoff_payload

from .adapters import adapter_status_for_targets
from .contracts import IndexJobManifest, IndexQueryResult, IndexTarget, KnowledgeSpaceManifest


class KnowledgeIndexRuntime:
    """PHASE05 local index job runtime for Document IR handoff payloads."""

    def __init__(self) -> None:
        self._spaces: dict[str, KnowledgeSpaceManifest] = {}
        self._jobs: dict[str, IndexJobManifest] = {}
        self._latest_job_by_space: dict[str, str] = {}
        self._indexes: dict[str, dict[str, list[dict]]] = {}

    def create_knowledge_space(
        self,
        knowledge_space_id: str,
        workspace_id: str,
        *,
        graph_project_id: str | None = None,
    ) -> KnowledgeSpaceManifest:
        space = KnowledgeSpaceManifest(
            knowledge_space_id=knowledge_space_id,
            workspace_id=workspace_id,
            graph_project_id=graph_project_id,
            index_version=f"idx_{uuid4().hex[:12]}",
            status="created",
        )
        self._spaces[knowledge_space_id] = space
        self._indexes[knowledge_space_id] = {"bm25": [], "vector": [], "graph": []}
        return space

    def index_document(
        self,
        knowledge_space_id: str,
        document: CanonicalDocumentIR,
        *,
        targets: list[IndexTarget],
        retry_count: int = 0,
        previous_job_id: str | None = None,
        parse_job_snapshot: ParseJobSnapshot | None = None,
    ) -> IndexJobManifest:
        space = self._require_space(knowledge_space_id)
        job_id = f"index_{uuid4().hex[:12]}"
        source_block_ids = [block.block_id for block in document.blocks]
        lineage = _parse_index_lineage(document, parse_job_snapshot, index_job_id=job_id)
        if not document.blocks:
            manifest = IndexJobManifest(
                job_id=job_id,
                knowledge_space_id=knowledge_space_id,
                workspace_id=space.workspace_id,
                document_id=document.metadata.document_id,
                source_uri=document.metadata.source_uri,
                index_version=space.index_version,
                targets=list(targets),
                target_status={target: "failed" for target in targets},
                status="failed",
                error="document has no blocks to index",
                retry_count=retry_count,
                previous_job_id=previous_job_id,
                graph_project_ref=space.graph_project_id,
                source_block_ids=source_block_ids,
                source_provenance=_source_provenance(document, lineage),
                acl_scopes=_acl_scopes(document),
                sensitivity_tags=_sensitivity_tags(document),
                adapter_status=adapter_status_for_targets(list(targets)),
                **_manifest_lineage_fields(lineage),
            )
            self._jobs[job_id] = manifest
            self._latest_job_by_space[knowledge_space_id] = job_id
            space.status = "failed"
            return manifest

        handoff = build_index_handoff_payload(document)
        target_status = {}
        if "bm25" in targets:
            self._indexes[knowledge_space_id]["bm25"] = self._bm25_documents(
                handoff.bm25_documents,
                document,
                lineage,
            )
            target_status["bm25"] = "ready"
        if "vector" in targets:
            self._indexes[knowledge_space_id]["vector"] = self._vector_documents(
                handoff.vector_documents,
                document,
                lineage,
            )
            target_status["vector"] = "ready"
        if "graph" in targets:
            self._indexes[knowledge_space_id]["graph"] = self._graph_documents(
                handoff.graphrag_documents,
                document,
                space.graph_project_id,
                lineage,
            )
            target_status["graph"] = "ready"

        manifest = IndexJobManifest(
            job_id=job_id,
            knowledge_space_id=knowledge_space_id,
            workspace_id=space.workspace_id,
            document_id=document.metadata.document_id,
            source_uri=document.metadata.source_uri,
            index_version=space.index_version,
            targets=list(targets),
            target_status=target_status,
            status="succeeded",
            retry_count=retry_count,
            previous_job_id=previous_job_id,
            graph_project_ref=space.graph_project_id,
            source_block_ids=source_block_ids,
            source_provenance=_source_provenance(document, lineage),
            acl_scopes=_acl_scopes(document),
            sensitivity_tags=_sensitivity_tags(document),
            adapter_status=adapter_status_for_targets(list(targets)),
            **_manifest_lineage_fields(lineage),
        )
        self._jobs[job_id] = manifest
        self._latest_job_by_space[knowledge_space_id] = job_id
        space.status = "ready"
        return manifest

    def get_job_manifest(self, job_id: str) -> IndexJobManifest:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"index job not found: {job_id}") from exc

    def retry_job(self, job_id: str, document: CanonicalDocumentIR) -> IndexJobManifest:
        previous = self.get_job_manifest(job_id)
        return self.index_document(
            previous.knowledge_space_id,
            document,
            targets=list(previous.targets),
            retry_count=previous.retry_count + 1,
            previous_job_id=previous.job_id,
        )

    def query(self, knowledge_space_id: str, query: str) -> IndexQueryResult:
        manifest = self._latest_manifest(knowledge_space_id)
        documents_by_source = {
            source: self._rank_documents(query, docs)
            for source, docs in self._indexes[knowledge_space_id].items()
            if manifest.target_status.get(source) == "ready"
        }
        return IndexQueryResult(
            knowledge_space_id=knowledge_space_id,
            index_version=manifest.index_version,
            query=query,
            documents_by_source=documents_by_source,
            manifest=manifest,
        )

    def to_retrieval_payload(self, knowledge_space_id: str, query: str) -> dict:
        result = self.query(knowledge_space_id, query)
        retrievers_used = [
            source
            for source in ["bm25", "vector", "graph"]
            if result.manifest.target_status.get(source) == "ready"
        ]
        return {
            "knowledge_space_id": result.knowledge_space_id,
            "index_version": result.index_version,
            "query": result.query,
            "retrievers_used": retrievers_used,
            "index_health": {source: result.manifest.target_status[source] for source in retrievers_used},
            "documents_by_source": result.documents_by_source,
            "manifest": result.manifest.model_dump(),
        }

    def _require_space(self, knowledge_space_id: str) -> KnowledgeSpaceManifest:
        try:
            return self._spaces[knowledge_space_id]
        except KeyError as exc:
            raise KeyError(f"knowledge space not found: {knowledge_space_id}") from exc

    def _latest_manifest(self, knowledge_space_id: str) -> IndexJobManifest:
        self._require_space(knowledge_space_id)
        job_id = self._latest_job_by_space.get(knowledge_space_id)
        if not job_id:
            raise KeyError(f"knowledge space has no index job: {knowledge_space_id}")
        return self._jobs[job_id]

    @staticmethod
    def _bm25_documents(
        documents: list[dict],
        source: CanonicalDocumentIR,
        lineage: dict,
    ) -> list[dict]:
        return [
            _document_payload(
                document["chunk_id"],
                document["content"],
                document["metadata"],
                "bm25",
                source,
                lineage,
            )
            for document in documents
        ]

    @staticmethod
    def _vector_documents(
        documents: list[dict],
        source: CanonicalDocumentIR,
        lineage: dict,
    ) -> list[dict]:
        return [
            _document_payload(
                document["id"],
                document["text"],
                document["metadata"],
                "vector",
                source,
                lineage,
            )
            for document in documents
        ]

    @staticmethod
    def _graph_documents(
        documents: list[dict],
        source: CanonicalDocumentIR,
        graph_project_id: str | None,
        lineage: dict,
    ) -> list[dict]:
        graph_documents = []
        for document in documents:
            graph_documents.append(
                {
                    **_document_payload(
                        document["chunk_id"],
                        document["content"],
                        document,
                        "graph",
                        source,
                        lineage,
                    ),
                    "graph_project_id": graph_project_id,
                    "entities": _entities(document["content"]),
                }
            )
        return graph_documents

    @staticmethod
    def _rank_documents(query: str, documents: list[dict]) -> list[dict]:
        query_tokens = set(_tokens(query))
        ranked = []
        for document in documents:
            doc_tokens = set(_tokens(document["content"]))
            score = len(query_tokens & doc_tokens)
            ranked.append({**document, "score": float(score)})
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked


def _document_payload(
    chunk_id: str,
    content: str,
    metadata: dict,
    source_type: str,
    source: CanonicalDocumentIR,
    lineage: dict,
) -> dict:
    block_id = chunk_id.split("::", 1)[-1]
    citation_lineage = {
        **_public_lineage_fields(lineage),
        "chunk_id": chunk_id,
        "block_id": block_id,
    }
    enriched_metadata = {
        **metadata,
        "block_id": block_id,
        "document_version_id": lineage["document_version_id"],
        "source_sha256": lineage["source_sha256"],
        "parser_config_hash": lineage["parser_config_hash"],
        "ir_schema_version": lineage["ir_schema_version"],
        "diagnostics_digest": lineage["diagnostics_digest"],
        "citation_lineage": citation_lineage,
    }
    return {
        "chunk_id": chunk_id,
        "document_id": source.metadata.document_id,
        "workspace_id": source.metadata.workspace_id,
        "content": content,
        "source_type": source_type,
        "metadata": enriched_metadata,
    }


def _source_provenance(document: CanonicalDocumentIR, lineage: dict | None = None) -> dict:
    lineage = lineage or _parse_index_lineage(document, None, index_job_id=None)
    return {
        "document_id": document.metadata.document_id,
        "source_id": document.metadata.source_id,
        "workspace_id": document.metadata.workspace_id,
        "source_uri": document.metadata.source_uri,
        "mime_type": document.metadata.mime_type,
        "hash": document.metadata.hash,
        "source_sha256": lineage["source_sha256"],
        "parser_id": document.metadata.parser_id,
        "parser_version": document.metadata.parser_version,
        "parser_config_hash": lineage["parser_config_hash"],
        "document_version_id": lineage["document_version_id"],
        "ir_schema_version": lineage["ir_schema_version"],
        "parse_job_id": lineage["parse_job_id"],
        "parse_attempt_id": lineage["parse_attempt_id"],
        "diagnostics_digest": lineage["diagnostics_digest"],
        "confidence": document.provenance.confidence,
        "warnings": list(document.provenance.warnings),
    }


def _parse_index_lineage(
    document: CanonicalDocumentIR,
    parse_job_snapshot: ParseJobSnapshot | None,
    *,
    index_job_id: str | None,
) -> dict:
    diagnostics = parse_job_snapshot.parser_diagnostics if parse_job_snapshot else []
    return {
        "index_job_id": index_job_id,
        "parse_job_id": parse_job_snapshot.job_id if parse_job_snapshot else None,
        "parse_attempt_id": parse_job_snapshot.parse_attempt_id if parse_job_snapshot else None,
        "document_id": document.metadata.document_id,
        "document_version_id": document.metadata.document_version_id,
        "source_sha256": document.metadata.source_sha256 or document.metadata.hash,
        "parser_config_hash": document.metadata.parser_config_hash,
        "ir_schema_version": document.metadata.ir_schema_version,
        "diagnostics_digest": _diagnostics_digest(diagnostics),
        "parser_diagnostics": list(diagnostics),
        "block_count": len(document.blocks),
        "table_count": len(document.tables),
        "figure_count": len(document.figures),
    }


def _manifest_lineage_fields(lineage: dict) -> dict:
    return {
        "parse_job_id": lineage["parse_job_id"],
        "parse_attempt_id": lineage["parse_attempt_id"],
        "document_version_id": lineage["document_version_id"],
        "source_sha256": lineage["source_sha256"],
        "parser_config_hash": lineage["parser_config_hash"],
        "ir_schema_version": lineage["ir_schema_version"],
        "diagnostics_digest": lineage["diagnostics_digest"],
        "parser_diagnostics": list(lineage["parser_diagnostics"]),
        "block_count": lineage["block_count"],
        "table_count": lineage["table_count"],
        "figure_count": lineage["figure_count"],
    }


def _public_lineage_fields(lineage: dict) -> dict:
    return {
        "index_job_id": lineage["index_job_id"],
        "parse_job_id": lineage["parse_job_id"],
        "parse_attempt_id": lineage["parse_attempt_id"],
        "document_id": lineage["document_id"],
        "document_version_id": lineage["document_version_id"],
        "source_sha256": lineage["source_sha256"],
        "parser_config_hash": lineage["parser_config_hash"],
        "ir_schema_version": lineage["ir_schema_version"],
        "diagnostics_digest": lineage["diagnostics_digest"],
    }


def _diagnostics_digest(diagnostics: list[dict]) -> str:
    payload = json.dumps(diagnostics, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _acl_scopes(document: CanonicalDocumentIR) -> list[str]:
    return sorted(
        {
            document.metadata.acl_scope,
            *(block.acl_scope for block in document.blocks),
        }
    )


def _sensitivity_tags(document: CanonicalDocumentIR) -> list[str]:
    tags = set(document.metadata.sensitivity_tags)
    for block in document.blocks:
        tags.update(block.sensitivity_tags)
    return sorted(tags)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _entities(text: str) -> list[str]:
    return sorted({token for token in re.findall(r"\b[A-Z][A-Za-z0-9_]+\b", text)})


__all__ = ["KnowledgeIndexRuntime"]
