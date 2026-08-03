from __future__ import annotations

import asyncio
import inspect
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .contracts import (
    IndexAdapterContract,
    IndexTarget,
    Neo4jPathVisibilityReceipt,
    build_neo4j_path_visibility_receipt,
)


INDEX_ADAPTER_CONTRACTS = {
    "local_bm25": IndexAdapterContract(
        adapter_id="local_bm25",
        target="bm25",
        engine="deterministic in-process lexical index",
        runtime_status="current",
        operations=["index", "query", "retry", "replay"],
    ),
    "local_vector": IndexAdapterContract(
        adapter_id="local_vector",
        target="vector",
        engine="deterministic in-process vector-shaped index",
        runtime_status="current",
        operations=["index", "query", "retry", "replay"],
    ),
    "local_graph": IndexAdapterContract(
        adapter_id="local_graph",
        target="graph",
        engine="deterministic in-process graph-shaped index",
        runtime_status="current",
        operations=["index", "query", "retry", "replay"],
    ),
    "elasticsearch": IndexAdapterContract(
        adapter_id="elasticsearch",
        target="bm25",
        engine="Elasticsearch",
        runtime_status="current",
        external_service=True,
        operations=["index", "query", "delete"],
    ),
    "milvus": IndexAdapterContract(
        adapter_id="milvus",
        target="vector",
        engine="Milvus",
        runtime_status="current",
        external_service=True,
        operations=["index", "query", "delete"],
    ),
    "neo4j": IndexAdapterContract(
        adapter_id="neo4j",
        target="graph",
        engine="Neo4j",
        runtime_status="current",
        external_service=True,
        operations=["index", "query", "delete", "path_visibility_receipt"],
    ),
}

LOCAL_INDEX_ADAPTER_BY_TARGET: dict[IndexTarget, str] = {
    "bm25": "local_bm25",
    "vector": "local_vector",
    "graph": "local_graph",
}


class ExternalServiceIndexAdapterBinding:
    """Adapter binding for service-backed PHASE12 index engines.

    The binding is intentionally client-injected. A service can only become
    Current after an integration test proves the configured client writes to
    and reads back from the real engine.
    """

    def __init__(
        self,
        *,
        adapter_id: str,
        target: IndexTarget,
        client: Any,
        index_name: str,
    ) -> None:
        self.adapter_id = adapter_id
        self.target = target
        self.client = client
        self.index_name = index_name

    def index(
        self,
        *,
        runtime: Any,
        handoff: Any,
        document: Any,
        lineage: dict[str, Any],
        graph_project_id: str | None,
    ) -> list[dict]:
        indexed_documents = self._canonical_documents(
            runtime=runtime,
            handoff=handoff,
            document=document,
            lineage=lineage,
            graph_project_id=graph_project_id,
        )
        _call_client(
            self.client,
            ("index_documents", "insert_documents", "index"),
            self.index_name,
            indexed_documents,
        )
        return indexed_documents

    def verify_visibility(
        self,
        *,
        document: Any,
        sample_query: str,
        indexed_documents: list[dict],
    ) -> dict[str, Any]:
        results = _call_client(
            self.client,
            ("search_documents", "search", "query"),
            sample_query,
            self.index_name,
        )
        result_documents = _normalize_result_documents(results)
        return _sample_result_verification(
            document_id=document.metadata.document_id,
            source_tokens=_tokens(sample_query),
            result_documents=result_documents,
        )

    def _canonical_documents(
        self,
        *,
        runtime: Any,
        handoff: Any,
        document: Any,
        lineage: dict[str, Any],
        graph_project_id: str | None,
    ) -> list[dict]:
        if self.target == "bm25":
            return runtime._bm25_documents(handoff.bm25_documents, document, lineage)
        if self.target == "vector":
            return runtime._vector_documents(handoff.vector_documents, document, lineage)
        if self.target == "graph":
            return runtime._graph_documents(handoff.graphrag_documents, document, graph_project_id, lineage)
        raise ValueError(f"unsupported external index target: {self.target}")


def external_adapter_bindings(
    *,
    elasticsearch_client: Any | None = None,
    milvus_client: Any | None = None,
    neo4j_client: Any | None = None,
    index_prefix: str = "zuno",
) -> dict[IndexTarget, ExternalServiceIndexAdapterBinding]:
    bindings: dict[IndexTarget, ExternalServiceIndexAdapterBinding] = {}
    if elasticsearch_client is not None:
        bindings["bm25"] = ExternalServiceIndexAdapterBinding(
            adapter_id="elasticsearch",
            target="bm25",
            client=elasticsearch_client,
            index_name=f"{index_prefix}_bm25",
        )
    if milvus_client is not None:
        bindings["vector"] = ExternalServiceIndexAdapterBinding(
            adapter_id="milvus",
            target="vector",
            client=milvus_client,
            index_name=f"{index_prefix}_vector",
        )
    if neo4j_client is not None:
        bindings["graph"] = ExternalServiceIndexAdapterBinding(
            adapter_id="neo4j",
            target="graph",
            client=neo4j_client,
            index_name=f"{index_prefix}_graph",
        )
    return bindings


class Neo4jGraphIndexClient:
    def __init__(
        self,
        *,
        uri: str,
        username: str,
        password: str,
        database: str = "neo4j",
        driver_factory: Any | None = None,
    ) -> None:
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver_factory = driver_factory

    def index_documents(self, index_name: str, documents: list[dict]) -> None:
        driver = self._driver()
        try:
            with driver.session(database=self.database) as session:
                session.run(
                    "MATCH (c:ZunoIndexChunk {index_name: $index_name}) DETACH DELETE c",
                    {"index_name": index_name},
                )
                for document in documents:
                    metadata = dict(document.get("metadata") or {})
                    chunk_id = str(document.get("chunk_id") or metadata.get("chunk_id") or uuid4().hex)
                    session.run(
                        """
                        MERGE (c:ZunoIndexChunk {index_name: $index_name, chunk_id: $chunk_id})
                        SET c.document_id = $document_id,
                            c.workspace_id = $workspace_id,
                            c.content = $content,
                            c.source_type = $source_type,
                            c.metadata_json = $metadata_json
                        """,
                        {
                            "index_name": index_name,
                            "chunk_id": chunk_id,
                            "document_id": str(document.get("document_id") or metadata.get("document_id") or ""),
                            "workspace_id": str(document.get("workspace_id") or metadata.get("workspace_id") or ""),
                            "content": str(document.get("content") or ""),
                            "source_type": str(document.get("source_type") or "graph"),
                            "metadata_json": _json_dumps(metadata),
                        },
                    )
        finally:
            driver.close()

    def search_documents(self, query: str, index_name: str) -> list[dict]:
        tokens = _tokens(query)
        driver = self._driver()
        try:
            with driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH (c:ZunoIndexChunk {index_name: $index_name})
                    WHERE any(token IN $tokens WHERE toLower(c.content) CONTAINS token)
                    RETURN c.chunk_id AS chunk_id,
                           c.document_id AS document_id,
                           c.workspace_id AS workspace_id,
                           c.content AS content,
                           c.source_type AS source_type
                    ORDER BY c.chunk_id
                    LIMIT 25
                    """,
                    {"index_name": index_name, "tokens": tokens},
                )
                return [record.data() for record in result]
        finally:
            driver.close()

    def index_graph_relations(
        self,
        index_name: str,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        snapshot_id: str,
        entities: list[dict],
        relations: list[dict],
    ) -> None:
        driver = self._driver()
        try:
            with driver.session(database=self.database) as session:
                session.run(
                    """
                    MATCH (e:ZunoIndexEntity {index_name: $index_name, tenant_id: $tenant_id,
                                              workspace_id: $workspace_id,
                                              knowledge_version_id: $knowledge_version_id,
                                              snapshot_id: $snapshot_id})
                    DETACH DELETE e
                    """,
                    {
                        "index_name": index_name,
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "knowledge_version_id": knowledge_version_id,
                        "snapshot_id": snapshot_id,
                    },
                )
                for entity in entities:
                    session.run(
                        """
                        MERGE (e:ZunoIndexEntity {index_name: $index_name, entity_ref: $entity_ref})
                        SET e.tenant_id = $tenant_id,
                            e.workspace_id = $workspace_id,
                            e.knowledge_version_id = $knowledge_version_id,
                            e.snapshot_id = $snapshot_id,
                            e.kind = $kind,
                            e.name = $name
                        """,
                        {
                            "index_name": index_name,
                            "entity_ref": str(entity.get("entity_ref") or entity.get("id") or ""),
                            "tenant_id": tenant_id,
                            "workspace_id": workspace_id,
                            "knowledge_version_id": knowledge_version_id,
                            "snapshot_id": snapshot_id,
                            "kind": str(entity.get("kind") or ""),
                            "name": str(entity.get("name") or entity.get("entity_ref") or entity.get("id") or ""),
                        },
                    )
                for relation in relations:
                    session.run(
                        """
                        MATCH (from:ZunoIndexEntity {index_name: $index_name, entity_ref: $from_ref})
                        MATCH (to:ZunoIndexEntity {index_name: $index_name, entity_ref: $to_ref})
                        MERGE (from)-[r:ZUNO_DIRECTED_RELATION {index_name: $index_name,
                                                                 relation_ref: $relation_ref}]->(to)
                        SET r.tenant_id = $tenant_id,
                            r.workspace_id = $workspace_id,
                            r.knowledge_version_id = $knowledge_version_id,
                            r.snapshot_id = $snapshot_id,
                            r.kind = $kind
                        """,
                        {
                            "index_name": index_name,
                            "relation_ref": str(relation.get("relation_ref") or relation.get("id") or ""),
                            "from_ref": str(relation.get("from") or relation.get("from_ref") or ""),
                            "to_ref": str(relation.get("to") or relation.get("to_ref") or ""),
                            "tenant_id": tenant_id,
                            "workspace_id": workspace_id,
                            "knowledge_version_id": knowledge_version_id,
                            "snapshot_id": snapshot_id,
                            "kind": str(relation.get("kind") or ""),
                        },
                    )
        finally:
            driver.close()

    def verify_path_visibility_receipt(
        self,
        index_name: str,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        snapshot_id: str,
        start_entity_ref: str,
        end_entity_ref: str,
        relation_kinds: list[str],
        query_kind: str = "directed_path",
        config_hash: str,
        observed_at: datetime | None = None,
    ) -> Neo4jPathVisibilityReceipt | None:
        driver = self._driver()
        try:
            with driver.session(database=self.database) as session:
                result = session.run(
                    """
                    MATCH path = (start:ZunoIndexEntity {index_name: $index_name,
                                                         tenant_id: $tenant_id,
                                                         workspace_id: $workspace_id,
                                                         knowledge_version_id: $knowledge_version_id,
                                                         snapshot_id: $snapshot_id,
                                                         entity_ref: $start_entity_ref})
                                 -[:ZUNO_DIRECTED_RELATION*1..5]->
                                 (end:ZunoIndexEntity {index_name: $index_name,
                                                       tenant_id: $tenant_id,
                                                       workspace_id: $workspace_id,
                                                       knowledge_version_id: $knowledge_version_id,
                                                       snapshot_id: $snapshot_id,
                                                       entity_ref: $end_entity_ref})
                    WHERE [relation IN relationships(path) | relation.kind] = $relation_kinds
                    RETURN [node IN nodes(path) | node.entity_ref] AS matched_node_refs,
                           [relation IN relationships(path) | relation.relation_ref] AS matched_relation_refs
                    LIMIT 1
                    """,
                    {
                        "index_name": index_name,
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "knowledge_version_id": knowledge_version_id,
                        "snapshot_id": snapshot_id,
                        "start_entity_ref": start_entity_ref,
                        "end_entity_ref": end_entity_ref,
                        "relation_kinds": relation_kinds,
                    },
                )
                rows = [record.data() for record in result]
        finally:
            driver.close()
        if not rows:
            return None
        row = rows[0]
        return build_neo4j_path_visibility_receipt(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            snapshot_id=snapshot_id,
            query_kind=query_kind,
            start_entity_ref=start_entity_ref,
            end_entity_ref=end_entity_ref,
            relation_kinds=relation_kinds,
            matched_node_refs=list(row.get("matched_node_refs") or []),
            matched_relation_refs=list(row.get("matched_relation_refs") or []),
            adapter_execution_ref=f"neo4j-path-readback:{index_name}",
            visibility_status="visible",
            observed_at=observed_at or datetime.now(timezone.utc),
            config_hash=config_hash,
        )

    def _driver(self) -> Any:
        if self._driver_factory is not None:
            return self._driver_factory()
        from neo4j import GraphDatabase

        return GraphDatabase.driver(self.uri, auth=(self.username, self.password))


class ElasticsearchBm25IndexClient:
    def __init__(self, *, base_url: str = "http://localhost:9200") -> None:
        self.base_url = base_url.rstrip("/")

    def index_documents(self, index_name: str, documents: list[dict]) -> None:
        import urllib.error

        try:
            _http_json("DELETE", f"{self.base_url}/{index_name}")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
        _http_json(
            "PUT",
            f"{self.base_url}/{index_name}",
            {
                "mappings": {
                    "properties": {
                        "chunk_id": {"type": "keyword"},
                        "document_id": {"type": "keyword"},
                        "workspace_id": {"type": "keyword"},
                        "content": {"type": "text"},
                        "source_type": {"type": "keyword"},
                    }
                }
            },
        )
        for document in documents:
            chunk_id = str(document.get("chunk_id") or uuid4().hex)
            _http_json(
                "PUT",
                f"{self.base_url}/{index_name}/_doc/{chunk_id}",
                {
                    "chunk_id": chunk_id,
                    "document_id": str(document.get("document_id") or ""),
                    "workspace_id": str(document.get("workspace_id") or ""),
                    "content": str(document.get("content") or ""),
                    "source_type": str(document.get("source_type") or "bm25"),
                },
            )
        _http_json("POST", f"{self.base_url}/{index_name}/_refresh")

    def search_documents(self, query: str, index_name: str) -> list[dict]:
        response = _http_json(
            "POST",
            f"{self.base_url}/{index_name}/_search",
            {
                "query": {"match": {"content": query}},
                "size": 25,
            },
        )
        hits = response.get("hits", {}).get("hits", [])
        return [dict(hit.get("_source") or {}) for hit in hits]


class MilvusVectorIndexClient:
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: str = "19530",
        dim: int = 16,
        embedding_gateway: Any | None = None,
        embedding_provider: str | None = None,
        embedding_model: str | None = None,
        embedding_config_hash: str | None = None,
        formal_embedding_required: bool = False,
        collection_factory: Any | None = None,
        collection_loader: Any | None = None,
    ) -> None:
        if formal_embedding_required and embedding_gateway is None:
            raise RuntimeError("credential_blocked: formal embedding gateway required")
        if embedding_gateway is not None and not (embedding_provider and embedding_model and embedding_config_hash):
            raise ValueError("formal embedding gateway requires provider, model, and config hash")
        self.host = host
        self.port = port
        self.dim = dim
        self.embedding_gateway = embedding_gateway
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.embedding_config_hash = embedding_config_hash
        self.formal_embedding_required = formal_embedding_required
        self._collection_factory = collection_factory
        self._collection_loader = collection_loader

    def index_documents(self, index_name: str, documents: list[dict]) -> None:
        collection = self._recreate_collection(index_name)
        embeddings = self._embed_documents([str(document.get("content") or "") for document in documents])
        rows = [
            {
                "chunk_id": str(document.get("chunk_id") or uuid4().hex),
                "document_id": str(document.get("document_id") or ""),
                "workspace_id": str(document.get("workspace_id") or ""),
                "content": str(document.get("content") or ""),
                "embedding": embeddings[index],
            }
            for index, document in enumerate(documents)
        ]
        if rows:
            collection.insert(rows)
            collection.flush()
        collection.load()

    def search_documents(self, query: str, index_name: str) -> list[dict]:
        collection = self._load_collection(index_name)
        collection.load()
        results = collection.search(
            data=[self._embed_query(query)],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 8}},
            limit=25,
            output_fields=["chunk_id", "document_id", "workspace_id", "content"],
        )
        documents: list[dict] = []
        for hit in results[0]:
            entity = hit.entity
            documents.append(
                {
                    "chunk_id": entity.get("chunk_id"),
                    "document_id": entity.get("document_id"),
                    "workspace_id": entity.get("workspace_id"),
                    "content": entity.get("content"),
                    "source_type": "vector",
                }
            )
        return documents

    def embedding_attestation(self) -> dict[str, Any]:
        if self.embedding_gateway is None:
            return {
                "status": "ADAPTER_SMOKE_ONLY",
                "provider": None,
                "model": None,
                "config_hash": None,
                "dimension": self.dim,
            }
        return {
            "status": "FORMAL_EMBEDDING_GATEWAY_CONFIGURED",
            "provider": self.embedding_provider,
            "model": self.embedding_model,
            "config_hash": self.embedding_config_hash,
            "dimension": self.dim,
        }

    def _embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self.embedding_gateway is None:
            return [_deterministic_vector(text, self.dim) for text in texts]
        method = getattr(self.embedding_gateway, "embed_documents", None)
        if method is not None:
            vectors = _resolve_maybe_awaitable(method(texts))
        else:
            method = getattr(self.embedding_gateway, "embed_async", None)
            if method is None:
                raise RuntimeError("formal embedding gateway does not implement embed_documents or embed_async")
            vectors = _resolve_maybe_awaitable(method(texts))
        return _normalize_embedding_vectors(vectors, expected_count=len(texts), expected_dim=self.dim)

    def _embed_query(self, query: str) -> list[float]:
        if self.embedding_gateway is None:
            return _deterministic_vector(query, self.dim)
        method = getattr(self.embedding_gateway, "embed_query", None)
        if method is not None:
            vector = _resolve_maybe_awaitable(method(query))
        else:
            method = getattr(self.embedding_gateway, "embed_async", None)
            if method is None:
                raise RuntimeError("formal embedding gateway does not implement embed_query or embed_async")
            vector = _resolve_maybe_awaitable(method(query))
        return _normalize_embedding_vector(vector, expected_dim=self.dim)

    def _recreate_collection(self, index_name: str) -> Any:
        if self._collection_factory is not None:
            return self._collection_factory(index_name, self.dim)
        from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

        connections.connect(alias="default", host=self.host, port=self.port)
        if utility.has_collection(index_name):
            Collection(index_name).drop()
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="workspace_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim),
        ]
        collection = Collection(index_name, CollectionSchema(fields, description=f"Zuno PHASE12 vector index {index_name}"))
        collection.create_index("embedding", {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 16}})
        return collection

    def _load_collection(self, index_name: str) -> Any:
        if self._collection_loader is not None:
            return self._collection_loader(index_name)
        from pymilvus import Collection

        return Collection(index_name)


def adapter_status_for_targets(targets: list[IndexTarget]) -> dict[str, str]:
    status: dict[str, str] = {}
    for target in targets:
        adapter_id = LOCAL_INDEX_ADAPTER_BY_TARGET[target]
        adapter = INDEX_ADAPTER_CONTRACTS[adapter_id]
        status[target] = f"{adapter.adapter_id}:{adapter.runtime_status}"
    return status


def adapter_status_for_bindings(targets: list[IndexTarget], bindings: dict[IndexTarget, Any]) -> dict[str, str]:
    status: dict[str, str] = {}
    for target in targets:
        adapter_id = str(getattr(bindings[target], "adapter_id", ""))
        contract = INDEX_ADAPTER_CONTRACTS.get(adapter_id)
        runtime_status = contract.runtime_status if contract else "target_blocked"
        status[target] = f"{adapter_id}:{runtime_status}"
    return status


def _call_client(client: Any, method_names: tuple[str, ...], *args: Any) -> Any:
    for method_name in method_names:
        method = getattr(client, method_name, None)
        if method is None:
            continue
        return _resolve_maybe_awaitable(method(*args))
    raise RuntimeError(f"external index client does not implement any of: {', '.join(method_names)}")


def _resolve_maybe_awaitable(value: Any) -> Any:
    if not inspect.isawaitable(value):
        return value
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(value)
    raise RuntimeError("external index adapter received an async client inside a running event loop")


def _normalize_result_documents(results: Any) -> list[dict]:
    if results is None:
        return []
    if isinstance(results, dict):
        return [results]
    normalized = []
    for result in list(results):
        if isinstance(result, dict):
            normalized.append(result)
        elif hasattr(result, "to_dict"):
            normalized.append(result.to_dict())
        else:
            normalized.append(dict(vars(result)))
    return normalized


def _sample_result_verification(
    *,
    document_id: str,
    source_tokens: list[str],
    result_documents: list[dict],
) -> dict[str, Any]:
    query_tokens = set(source_tokens)
    match_count = 0
    for result in result_documents:
        if str(result.get("document_id") or result.get("metadata", {}).get("document_id") or "") != document_id:
            continue
        content = str(result.get("content") or result.get("text") or result.get("summary") or "")
        if query_tokens & set(_tokens(content)):
            match_count += 1
    if match_count == 0:
        return {
            "passed": False,
            "reason": "external_sample_retrieval_no_source_match",
            "sample_query": " ".join(source_tokens),
            "match_count": 0,
        }
    return {
        "passed": True,
        "reason": "external_sample_retrieval_matched_source",
        "sample_query": " ".join(source_tokens),
        "match_count": match_count,
    }


def _tokens(text: str) -> list[str]:
    import re

    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _json_dumps(payload: object) -> str:
    import json

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _http_json(method: str, url: str, payload: object | None = None) -> dict:
    import json
    import urllib.request

    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        data = response.read()
    if not data:
        return {}
    return json.loads(data.decode("utf-8"))


def _deterministic_vector(text: str, dim: int) -> list[float]:
    import hashlib

    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [float(digest[index % len(digest)]) / 255.0 for index in range(dim)]


def _normalize_embedding_vectors(vectors: Any, *, expected_count: int, expected_dim: int) -> list[list[float]]:
    if not isinstance(vectors, list) or len(vectors) != expected_count:
        raise RuntimeError("formal embedding gateway returned mismatched vector count")
    return [_normalize_embedding_vector(vector, expected_dim=expected_dim) for vector in vectors]


def _normalize_embedding_vector(vector: Any, *, expected_dim: int) -> list[float]:
    if not isinstance(vector, list) or len(vector) != expected_dim:
        raise RuntimeError("formal embedding gateway returned mismatched vector dimension")
    return [float(value) for value in vector]


__all__ = [
    "ExternalServiceIndexAdapterBinding",
    "INDEX_ADAPTER_CONTRACTS",
    "LOCAL_INDEX_ADAPTER_BY_TARGET",
    "ElasticsearchBm25IndexClient",
    "MilvusVectorIndexClient",
    "Neo4jGraphIndexClient",
    "adapter_status_for_bindings",
    "adapter_status_for_targets",
    "external_adapter_bindings",
]
