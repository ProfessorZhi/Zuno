from __future__ import annotations


class GraphWriter:
    @staticmethod
    def _attach_runtime_metadata(
        payload: dict,
        *,
        graphrag_project_id: str | None = None,
        domain_pack_id: str | None = None,
        index_version: str | None = None,
        status: str | None = None,
        knowledge_file_id: str | None = None,
    ) -> dict:
        if graphrag_project_id:
            payload.setdefault("graphrag_project_id", graphrag_project_id)
        elif domain_pack_id:
            payload.setdefault("domain_pack_id", domain_pack_id)
        if index_version:
            payload.setdefault("index_version", index_version)
        if status:
            payload.setdefault("status", status)
        if knowledge_file_id:
            payload.setdefault("knowledge_file_id", knowledge_file_id)
        source_chunk_id = str(payload.get("source_chunk_id") or payload.get("chunk_id") or "").strip()
        if source_chunk_id:
            payload.setdefault("source_chunk_id", source_chunk_id)
        document_hash = str(payload.get("document_hash") or "").strip()
        if document_hash:
            payload.setdefault("document_hash", document_hash)
        chunk_hash = str(payload.get("chunk_hash") or "").strip()
        if chunk_hash:
            payload.setdefault("chunk_hash", chunk_hash)
        return payload

    def build_entity_payload(
        self,
        entity: dict,
        *,
        graphrag_project_id: str | None = None,
        domain_pack_id: str | None = None,
        index_version: str | None = None,
        status: str | None = None,
        knowledge_file_id: str | None = None,
    ) -> dict:
        payload = dict(entity)
        return self._attach_runtime_metadata(
            payload,
            graphrag_project_id=graphrag_project_id,
            domain_pack_id=domain_pack_id,
            index_version=index_version,
            status=status,
            knowledge_file_id=knowledge_file_id,
        )

    def build_relation_payload(
        self,
        relation: dict,
        *,
        graphrag_project_id: str | None = None,
        domain_pack_id: str | None = None,
        index_version: str | None = None,
        status: str | None = None,
        knowledge_file_id: str | None = None,
    ) -> dict:
        payload = dict(relation)
        return self._attach_runtime_metadata(
            payload,
            graphrag_project_id=graphrag_project_id,
            domain_pack_id=domain_pack_id,
            index_version=index_version,
            status=status,
            knowledge_file_id=knowledge_file_id,
        )


__all__ = ["GraphWriter"]
