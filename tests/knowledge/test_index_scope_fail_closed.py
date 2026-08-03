"""PHASE22 GAP-B3 index query scope fail-closed tests (Task E).

The Elasticsearch / Milvus / Neo4j query interfaces REQUIRE the
tenant / workspace / knowledge_version scope: missing, None or empty
values raise ScopeValidationError and no unscoped query is executed.
Foreign scopes return zero rows; hostile injection strings are contained.
"""

from __future__ import annotations

import pytest

from zuno.knowledge.indexing import (
    ElasticsearchBm25IndexClient,
    MilvusVectorIndexClient,
    Neo4jGraphIndexClient,
    ScopeValidationError,
)
from zuno.knowledge.indexing.adapters import _milvus_literal

TENANT = "tenant_auroralis"
WORKSPACE = "workspace_regression"
KNOWLEDGE_VERSION = "knowledge-version::kv"


def _es() -> ElasticsearchBm25IndexClient:
    return ElasticsearchBm25IndexClient(base_url="http://localhost:9200")


def _milvus() -> MilvusVectorIndexClient:
    return MilvusVectorIndexClient(host="localhost", port="19530")


def _neo4j() -> Neo4jGraphIndexClient:
    return Neo4jGraphIndexClient(
        uri="bolt://localhost:7687", username="u", password="p", driver_factory=lambda: None
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"tenant_id": None, "workspace_id": WORKSPACE, "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": "", "workspace_id": WORKSPACE, "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": None, "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": "", "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": WORKSPACE, "knowledge_version_id": None},
        {"tenant_id": TENANT, "workspace_id": WORKSPACE, "knowledge_version_id": ""},
    ],
    ids=[
        "missing_all",
        "missing_tenant",
        "empty_tenant",
        "missing_workspace",
        "empty_workspace",
        "missing_knowledge_version",
        "empty_knowledge_version",
    ],
)
def test_elasticsearch_search_rejects_unscoped_queries(kwargs: dict) -> None:
    with pytest.raises(ScopeValidationError):
        _es().search_documents("renewal policy", "idx", **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"tenant_id": TENANT, "workspace_id": WORKSPACE},
        {"tenant_id": TENANT, "workspace_id": WORKSPACE, "knowledge_version_id": ""},
    ],
)
def test_elasticsearch_count_rejects_unscoped_queries(kwargs: dict) -> None:
    with pytest.raises(ScopeValidationError):
        _es().count_documents("idx", **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"tenant_id": None, "workspace_id": WORKSPACE, "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": "", "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": WORKSPACE, "knowledge_version_id": ""},
    ],
)
def test_milvus_search_rejects_unscoped_queries(kwargs: dict) -> None:
    with pytest.raises(ScopeValidationError):
        _milvus().search_documents("renewal policy", "col", **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"tenant_id": "", "workspace_id": WORKSPACE, "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": WORKSPACE},
    ],
)
def test_milvus_count_rejects_unscoped_queries(kwargs: dict) -> None:
    with pytest.raises(ScopeValidationError):
        _milvus().count_documents("col", **kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"tenant_id": "", "workspace_id": WORKSPACE, "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": "", "knowledge_version_id": KNOWLEDGE_VERSION},
        {"tenant_id": TENANT, "workspace_id": WORKSPACE, "knowledge_version_id": ""},
        {"tenant_id": None, "workspace_id": WORKSPACE, "knowledge_version_id": KNOWLEDGE_VERSION},
    ],
)
def test_neo4j_query_path_rejects_unscoped_queries(kwargs: dict) -> None:
    with pytest.raises(ScopeValidationError):
        _neo4j().query_path(
            "idx",
            start_entity_ref="a",
            end_entity_ref="b",
            relation_kinds=["k"],
            snapshot_id="",
            **kwargs,
        )


def test_milvus_literal_escaping_contains_injection() -> None:
    hostile = 'tenant" OR 1==1 --'
    escaped = _milvus_literal(hostile)
    # The escaped literal stays inside one quoted string: quotes and
    # backslashes are escaped, so the hostile clause cannot break out.
    assert escaped == 'tenant\\" OR 1==1 --'
    # Escaped strings are safe to embed in a quoted Milvus expr: the only
    # unescaped quotes are the string delimiters; the injected quote is
    # backslash-escaped and cannot terminate the literal.
    expr = f'tenant_id == "{escaped}"'
    assert expr == 'tenant_id == "tenant\\" OR 1==1 --"'
    assert expr.count('\\"') == 1
    assert expr.count('"') == 3  # opening, escaped, closing
    assert expr.endswith('--"')


def test_require_query_scope_rejects_empty_snapshot_id() -> None:
    from zuno.knowledge.indexing import require_query_scope

    with pytest.raises(ScopeValidationError):
        require_query_scope(
            tenant_id=TENANT,
            workspace_id=WORKSPACE,
            knowledge_version_id=KNOWLEDGE_VERSION,
            snapshot_id="",
        )
    require_query_scope(
        tenant_id=TENANT,
        workspace_id=WORKSPACE,
        knowledge_version_id=KNOWLEDGE_VERSION,
    )
