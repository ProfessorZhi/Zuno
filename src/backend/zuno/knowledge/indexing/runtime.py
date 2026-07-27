from __future__ import annotations

import hashlib
import json
import re
from typing import Any
from uuid import uuid4

from zuno.knowledge.ingestion.contracts import CanonicalDocumentIR, ParseJobSnapshot
from zuno.knowledge.ingestion.router import build_index_handoff_payload

from .adapters import LOCAL_INDEX_ADAPTER_BY_TARGET, adapter_status_for_bindings
from .contracts import IndexJobManifest, IndexQueryResult, IndexTarget, KnowledgeSpaceManifest


class LocalIndexAdapterBinding:
    def __init__(self, *, adapter_id: str, target: IndexTarget) -> None:
        self.adapter_id = adapter_id
        self.target = target

    def index(
        self,
        *,
        runtime: "KnowledgeIndexRuntime",
        handoff: Any,
        document: CanonicalDocumentIR,
        lineage: dict[str, Any],
        graph_project_id: str | None,
    ) -> list[dict]:
        if self.target == "bm25":
            return runtime._bm25_documents(handoff.bm25_documents, document, lineage)
        if self.target == "vector":
            return runtime._vector_documents(handoff.vector_documents, document, lineage)
        if self.target == "graph":
            return runtime._graph_documents(handoff.graphrag_documents, document, graph_project_id, lineage)
        raise ValueError(f"unsupported index target: {self.target}")


class KnowledgeIndexRuntime:
    """PHASE05 local index job runtime for Document IR handoff payloads."""

    def __init__(self, *, adapter_bindings: dict[IndexTarget, Any] | None = None) -> None:
        self._spaces: dict[str, KnowledgeSpaceManifest] = {}
        self._jobs: dict[str, IndexJobManifest] = {}
        self._latest_job_by_space: dict[str, str] = {}
        self._indexes: dict[str, dict[str, list[dict]]] = {}
        self._adapter_bindings = adapter_bindings or _default_adapter_bindings()

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
                adapter_status=adapter_status_for_bindings(list(targets), self._adapter_bindings),
                adapter_dispatch_receipts={},
                adapter_visibility_receipts={},
                **_manifest_lineage_fields(lineage),
            )
            self._jobs[job_id] = manifest
            self._latest_job_by_space[knowledge_space_id] = job_id
            space.status = "failed"
            return manifest

        handoff = build_index_handoff_payload(document)
        target_status = {}
        adapter_dispatch_receipts = {}
        indexed_documents_by_target = {}
        for target in targets:
            adapter = self._adapter_for_target(target)
            indexed_documents = adapter.index(
                runtime=self,
                handoff=handoff,
                document=document,
                lineage=lineage,
                graph_project_id=space.graph_project_id,
            )
            self._indexes[knowledge_space_id][target] = indexed_documents
            indexed_documents_by_target[target] = indexed_documents
            target_status[target] = "ready"
            adapter_dispatch_receipts[target] = _adapter_dispatch_receipt(
                adapter=adapter,
                target=target,
                knowledge_space_id=knowledge_space_id,
                index_version=space.index_version,
                document=document,
                indexed_documents=indexed_documents,
            )

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
            adapter_status=adapter_status_for_bindings(list(targets), self._adapter_bindings),
            adapter_dispatch_receipts=adapter_dispatch_receipts,
            adapter_visibility_receipts=self._verified_adapter_visibility_receipts(
                adapter_bindings=self._adapter_bindings,
                knowledge_space_id=knowledge_space_id,
                index_version=space.index_version,
                document=document,
                target_status=target_status,
                adapter_dispatch_receipts=adapter_dispatch_receipts,
                indexed_documents_by_target=indexed_documents_by_target,
            ),
            **_manifest_lineage_fields(lineage),
        )
        for target, receipt in manifest.adapter_visibility_receipts.items():
            if receipt.get("visibility") != "visible":
                manifest.target_status[target] = "degraded"
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
            and _adapter_contract_is_current(result.manifest.adapter_status.get(source, ""))
            and result.manifest.adapter_visibility_receipts.get(source, {}).get("visibility") == "visible"
        ]
        return {
            "knowledge_space_id": result.knowledge_space_id,
            "index_version": result.index_version,
            "query": result.query,
            "retrievers_used": retrievers_used,
            "index_health": {source: result.manifest.target_status[source] for source in retrievers_used},
            "adapter_visibility_receipts": {
                source: result.manifest.adapter_visibility_receipts[source]
                for source in retrievers_used
            },
            "documents_by_source": {
                source: result.documents_by_source[source]
                for source in retrievers_used
                if source in result.documents_by_source
            },
            "manifest": result.manifest.model_dump(),
        }

    def rehydrate_index(self, manifest: IndexJobManifest, chunks: list[object]) -> None:
        self._spaces[manifest.knowledge_space_id] = KnowledgeSpaceManifest(
            knowledge_space_id=manifest.knowledge_space_id,
            workspace_id=manifest.workspace_id,
            graph_project_id=manifest.graph_project_ref,
            index_version=manifest.index_version,
            status="ready" if manifest.status == "succeeded" else manifest.status,
        )
        documents = [_rehydrated_document_payload(chunk) for chunk in chunks]
        self._indexes[manifest.knowledge_space_id] = {
            "bm25": [dict(document, source_type="bm25") for document in documents],
            "vector": [dict(document, source_type="vector") for document in documents],
            "graph": [
                {
                    **dict(document, source_type="graph"),
                    "graph_project_id": manifest.graph_project_ref,
                    "entities": _entities(str(document.get("content") or "")),
                }
                for document in documents
            ],
        }
        self._jobs[manifest.job_id] = manifest
        self._latest_job_by_space[manifest.knowledge_space_id] = manifest.job_id

    @staticmethod
    def _verified_adapter_visibility_receipts(
        *,
        adapter_bindings: dict[IndexTarget, Any],
        knowledge_space_id: str,
        index_version: str,
        document: CanonicalDocumentIR,
        target_status: dict[str, str],
        adapter_dispatch_receipts: dict[str, dict],
        indexed_documents_by_target: dict[str, list[dict]],
    ) -> dict[str, dict]:
        receipts: dict[str, dict] = {}
        for target in ["bm25", "vector", "graph"]:
            if target_status.get(target) != "ready":
                continue
            dispatch_receipt = adapter_dispatch_receipts.get(target, {})
            sample_verification = _adapter_sample_visibility_verification(
                adapter=adapter_bindings[target],
                document=document,
                indexed_documents=indexed_documents_by_target.get(target, []),
            )
            payload = {
                "adapter_target": target,
                "adapter_dispatch_ref": dispatch_receipt.get("dispatch_ref"),
                "document_id": document.metadata.document_id,
                "document_version_id": document.metadata.document_version_id,
                "index_version": index_version,
                "knowledge_space_id": knowledge_space_id,
                "source_block_ids": [block.block_id for block in document.blocks],
                "sample_verification": sample_verification,
            }
            receipts[target] = {
                "receipt_ref": f"index-visibility:{target}:{_stable_hash(payload)[:16]}",
                "adapter_target": target,
                "adapter_id": dispatch_receipt.get("adapter_id"),
                "adapter_dispatch_ref": dispatch_receipt.get("dispatch_ref"),
                "adapter_status": "current",
                "visibility": "visible" if sample_verification["passed"] else "hidden",
                "visibility_failure_reason": None if sample_verification["passed"] else sample_verification["reason"],
                "sample_query": sample_verification["sample_query"],
                "sample_match_count": sample_verification["match_count"],
                "knowledge_space_id": knowledge_space_id,
                "index_version": index_version,
                "document_id": document.metadata.document_id,
                "document_version_id": document.metadata.document_version_id,
                "source_block_count": len(document.blocks),
                "payload_hash": _stable_hash(payload),
            }
        return receipts

    def _adapter_for_target(self, target: IndexTarget) -> Any:
        try:
            return self._adapter_bindings[target]
        except KeyError as exc:
            raise ValueError(f"no Knowledge index adapter configured for target: {target}") from exc

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
        normalized_query = _normalize_phrase(query)
        ranked = []
        for document in documents:
            doc_tokens = set(_tokens(document["content"]))
            content = str(document.get("content") or "")
            normalized_content = _normalize_phrase(content)
            matched_terms = sorted(query_tokens & doc_tokens)
            phrase_match = bool(normalized_query and normalized_query in normalized_content)
            raw_score = len(matched_terms) + (3.0 if phrase_match else 0.0)
            normalized_score = raw_score / max(len(query_tokens), 1)
            ranked.append(
                {
                    **document,
                    "score": float(raw_score),
                    "raw_score": float(raw_score),
                    "normalized_score": round(float(normalized_score), 6),
                    "retriever_source": "normalized_phrase" if phrase_match else document.get("source_type"),
                    "matched_terms": matched_terms,
                    "matched_phrase": query if phrase_match else "",
                    "candidate_reason": "normalized_phrase_match" if phrase_match else "token_overlap",
                }
            )
        ranked.sort(key=lambda item: item["score"], reverse=True)
        for rank, item in enumerate(ranked, start=1):
            item["rank"] = rank
        return ranked


def _document_payload(
    chunk_id: str,
    content: str,
    metadata: dict,
    source_type: str,
    source: CanonicalDocumentIR,
    lineage: dict,
) -> dict:
    block_id = str(metadata.get("block_id") or chunk_id.split("::", 1)[-1])
    source_span = dict(metadata.get("source_span") or {})
    citation_lineage = {
        **_public_lineage_fields(lineage),
        "chunk_id": chunk_id,
        "block_id": block_id,
        "source_object_id": metadata.get("source_object_id") or source.metadata.source_id,
        "source_uri": metadata.get("source_uri") or source.metadata.source_uri,
        "source_span": source_span,
    }
    enriched_metadata = {
        **metadata,
        "block_id": block_id,
        "chunk_id": chunk_id,
        "source_object_id": metadata.get("source_object_id") or source.metadata.source_id,
        "source_uri": metadata.get("source_uri") or source.metadata.source_uri,
        "document_version_id": lineage["document_version_id"],
        "source_sha256": lineage["source_sha256"],
        "content_hash": metadata.get("content_hash") or lineage["source_sha256"],
        "parser_name": metadata.get("parser_name") or source.metadata.parser_id,
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


def _default_adapter_bindings() -> dict[IndexTarget, LocalIndexAdapterBinding]:
    return {
        target: LocalIndexAdapterBinding(adapter_id=adapter_id, target=target)
        for target, adapter_id in LOCAL_INDEX_ADAPTER_BY_TARGET.items()
    }


def _adapter_dispatch_receipt(
    *,
    adapter: Any,
    target: IndexTarget,
    knowledge_space_id: str,
    index_version: str,
    document: CanonicalDocumentIR,
    indexed_documents: list[dict],
) -> dict[str, Any]:
    payload = {
        "adapter_id": str(getattr(adapter, "adapter_id", "")),
        "adapter_target": target,
        "document_id": document.metadata.document_id,
        "document_version_id": document.metadata.document_version_id,
        "index_version": index_version,
        "indexed_document_count": len(indexed_documents),
        "knowledge_space_id": knowledge_space_id,
    }
    payload_hash = _stable_hash(payload)
    return {
        "dispatch_ref": f"index-dispatch:{target}:{payload_hash[:16]}",
        "adapter_id": payload["adapter_id"],
        "adapter_target": target,
        "operation": "index",
        "status": "succeeded",
        "knowledge_space_id": knowledge_space_id,
        "index_version": index_version,
        "document_id": document.metadata.document_id,
        "document_version_id": document.metadata.document_version_id,
        "indexed_document_count": len(indexed_documents),
        "payload_hash": payload_hash,
    }


def _adapter_sample_visibility_verification(
    *,
    adapter: Any,
    document: CanonicalDocumentIR,
    indexed_documents: list[dict],
) -> dict[str, Any]:
    source_text = " ".join(block.text for block in document.blocks)
    sample_tokens = tuple(_tokens(source_text)[:8])
    sample_query = " ".join(sample_tokens)
    verifier = getattr(adapter, "verify_visibility", None)
    if verifier is None:
        return _sample_visibility_verification(
            document=document,
            indexed_documents=indexed_documents,
        )
    result = verifier(
        document=document,
        sample_query=sample_query,
        indexed_documents=indexed_documents,
    )
    return {
        "passed": bool(result.get("passed")),
        "reason": str(result.get("reason") or "external_sample_retrieval_unknown"),
        "sample_query": str(result.get("sample_query") or sample_query),
        "match_count": int(result.get("match_count") or 0),
    }


def _adapter_contract_is_current(adapter_status: str) -> bool:
    return adapter_status.endswith(":current")


def _sample_visibility_verification(
    *,
    document: CanonicalDocumentIR,
    indexed_documents: list[dict],
) -> dict[str, Any]:
    source_text = " ".join(block.text for block in document.blocks)
    sample_tokens = tuple(_tokens(source_text)[:8])
    sample_query = " ".join(sample_tokens)
    if not indexed_documents:
        return {
            "passed": False,
            "reason": "sample_retrieval_empty",
            "sample_query": sample_query,
            "match_count": 0,
        }
    query_tokens = set(sample_tokens)
    match_count = 0
    for indexed in indexed_documents:
        if str(indexed.get("document_id") or "") != document.metadata.document_id:
            continue
        indexed_tokens = set(_tokens(str(indexed.get("content") or "")))
        if query_tokens & indexed_tokens:
            match_count += 1
    if match_count == 0:
        return {
            "passed": False,
            "reason": "sample_retrieval_no_source_match",
            "sample_query": sample_query,
            "match_count": 0,
        }
    return {
        "passed": True,
        "reason": "sample_retrieval_matched_source",
        "sample_query": sample_query,
        "match_count": match_count,
    }


def _rehydrated_document_payload(chunk: object) -> dict:
    metadata = dict(getattr(chunk, "metadata", {}) or {})
    citation_lineage = dict(getattr(chunk, "citation_lineage", {}) or {})
    if citation_lineage:
        metadata["citation_lineage"] = citation_lineage
    chunk_id = str(getattr(chunk, "chunk_id"))
    block_id = str(getattr(chunk, "block_id", "") or chunk_id.split("::", 1)[-1])
    metadata.setdefault("block_id", block_id)
    metadata.setdefault("chunk_id", chunk_id)
    metadata.setdefault("document_version_id", getattr(chunk, "document_version_id", ""))
    metadata.setdefault("acl_scope", getattr(chunk, "acl_scope", "workspace"))
    metadata.setdefault("sensitivity_tags", list(getattr(chunk, "sensitivity_tags", []) or []))
    if citation_lineage.get("source_span") and not metadata.get("source_span"):
        metadata["source_span"] = dict(citation_lineage["source_span"])
    return {
        "chunk_id": chunk_id,
        "document_id": str(getattr(chunk, "document_id")),
        "workspace_id": str(getattr(chunk, "workspace_id")),
        "content": str(getattr(chunk, "content")),
        "source_type": str(getattr(chunk, "source_type", "bm25")),
        "metadata": metadata,
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


def _stable_hash(payload: object) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


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


def _normalize_phrase(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _entities(text: str) -> list[str]:
    return sorted({token for token in re.findall(r"\b[A-Z][A-Za-z0-9_]+\b", text)})


__all__ = ["KnowledgeIndexRuntime"]
