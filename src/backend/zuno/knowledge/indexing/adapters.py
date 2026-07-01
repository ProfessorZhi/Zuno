from __future__ import annotations

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


def adapter_status_for_targets(targets: list[IndexTarget]) -> dict[str, str]:
    status: dict[str, str] = {}
    for target in targets:
        adapter_id = LOCAL_INDEX_ADAPTER_BY_TARGET[target]
        adapter = INDEX_ADAPTER_CONTRACTS[adapter_id]
        status[target] = f"{adapter.adapter_id}:{adapter.runtime_status}"
    return status


__all__ = [
    "INDEX_ADAPTER_CONTRACTS",
    "LOCAL_INDEX_ADAPTER_BY_TARGET",
    "adapter_status_for_targets",
]
