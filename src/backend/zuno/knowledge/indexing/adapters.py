from __future__ import annotations

import asyncio
import inspect
from typing import Any

from .contracts import IndexAdapterContract, IndexTarget


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
        runtime_status="target_blocked",
        external_service=True,
        operations=["index", "query", "delete"],
        blocked_reason="external Elasticsearch cluster is not provisioned in the local runtime",
    ),
    "milvus": IndexAdapterContract(
        adapter_id="milvus",
        target="vector",
        engine="Milvus",
        runtime_status="target_blocked",
        external_service=True,
        operations=["index", "query", "delete"],
        blocked_reason="external Milvus cluster and embedding operations are not provisioned in the local runtime",
    ),
    "neo4j": IndexAdapterContract(
        adapter_id="neo4j",
        target="graph",
        engine="Neo4j",
        runtime_status="target_blocked",
        external_service=True,
        operations=["index", "query", "delete"],
        blocked_reason="external Neo4j graph service is not provisioned in the local runtime",
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


__all__ = [
    "ExternalServiceIndexAdapterBinding",
    "INDEX_ADAPTER_CONTRACTS",
    "LOCAL_INDEX_ADAPTER_BY_TARGET",
    "adapter_status_for_bindings",
    "adapter_status_for_targets",
    "external_adapter_bindings",
]
