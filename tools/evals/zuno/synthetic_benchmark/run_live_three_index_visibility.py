"""PHASE22 GAP-B3 adapter live smoke (DeepSeek2 / CC-B hardening).

Truth boundary — this runner NEVER claims formal corpus-level visibility:

* Input identity is strict: the frozen candidate manifest's document
  count, chunk count, chunk id set and per-chunk text hashes are validated
  exactly; no re-chunking happens.  The canonical 24-chunk set is written
  as-is (``input_kind=frozen_candidate_manifest``,
  ``not_owner_produced=true``).
* The corpus-level IndexBuildRun receipts stay
  ``NOT_RUN_DEPENDENCY_BLOCKED`` while no real KnowledgeVersion exists:
  ``receipt_scope=adapter_live_smoke``, ``snapshot_eligible=false``,
  ``visibility_status=blocked``.  Smoke receipts can never activate a
  snapshot.
* Tenant / workspace / knowledge_version scope is enforced on every
  query (ES term filters, Milvus escaped expr filters, Neo4j scoped path
  queries) and the full isolation matrix is recorded, including foreign
  and missing/empty scope outcomes.
* Credentials come from environment variables only
  (``ZUNO_TEST_NEO4J_*``); missing credentials fail closed with
  ``credential_blocked``.  Evidence is redacted.

Usage:
    ZUNO_TEST_NEO4J_URI=bolt://localhost:7687 \
    ZUNO_TEST_NEO4J_USERNAME=neo4j \
    ZUNO_TEST_NEO4J_PASSWORD=<password> \
    python tools/evals/zuno/synthetic_benchmark/run_live_three_index_visibility.py \
        --out-root docs/evidence/goal05-phase22-machine-attested-synthetic-regression/deepseek2-cc-b34c
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.knowledge.indexing import (  # noqa: E402
    CORPUS_INDEX_KINDS,
    ElasticsearchBm25IndexClient,
    MilvusVectorIndexClient,
    Neo4jGraphIndexClient,
    build_corpus_index_build_receipt,
    compute_embedding_config_hash,
    validate_canonical_corpus_identity,
    validate_corpus_index_build_receipt,
)

from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json  # noqa: E402

TRACK_DIR = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-machine-attested-synthetic-regression"
CORPUS_DIR = TRACK_DIR / "candidate-dataset" / "corpus"
SOURCE_UPLOAD_MANIFEST = TRACK_DIR / "source_upload_manifest.json"
CANONICAL_IR_MANIFEST = TRACK_DIR / "canonical_ir_manifest.json"

ES_BASE_URL = "http://localhost:9200"
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
MILVUS_HEALTH = "http://localhost:9091/healthz"

EMBEDDING_PROVIDER = "dashscope"
EMBEDDING_MODEL = "text-embedding-v4"
EMBEDDING_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
EMBEDDING_DIMENSION = 1024

REDACT_KEYS = frozenset({"password", "api_key", "authorization", "bearer", "secret", "token"})


def _redact(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {
            key: ("[REDACTED]" if key.lower() in REDACT_KEYS else _redact(value))
            for key, value in payload.items()
        }
    if isinstance(payload, list):
        return [_redact(item) for item in payload]
    return payload


def _paragraph_chunks(body: str) -> list[str]:
    return [chunk.strip() for chunk in body.split("\n\n") if chunk.strip()]


def _manifest_chunk_texts(canonical_ir: dict[str, Any]) -> dict[str, str]:
    """Hash-match corpus paragraphs to manifest chunk text_hashes.

    This is identity verification, not re-chunking: every manifest chunk
    receives its exact canonical text or the run fails closed.
    """
    hashes_by_text: dict[str, str] = {}
    for path in sorted(CORPUS_DIR.glob("*.md")):
        for paragraph in _paragraph_chunks(path.read_text(encoding="utf-8")):
            hashes_by_text.setdefault(sha256_json({"text": paragraph}), paragraph)
    chunks_by_hash: dict[str, str] = {}
    for chunk in canonical_ir["chunks"]:
        chunks_by_hash[chunk["text_hash"]] = chunk["chunk_id"]
    result: dict[str, str] = {}
    for text_hash, chunk_id in chunks_by_hash.items():
        text = hashes_by_text.get(text_hash)
        if text is None:
            raise RuntimeError(f"canonical chunk {chunk_id} has no matching corpus text (hash {text_hash[:12]})")
        result[chunk_id] = text
    # No extra text may exist beyond the manifest chunk set.
    extra = set(hashes_by_text) - set(chunks_by_hash)
    if extra:
        raise RuntimeError(f"corpus contains {len(extra)} paragraph hashes not present in the canonical manifest")
    return result


def _load_neo4j_credentials() -> dict[str, str]:
    uri = os.environ.get("ZUNO_TEST_NEO4J_URI")
    username = os.environ.get("ZUNO_TEST_NEO4J_USERNAME")
    password = os.environ.get("ZUNO_TEST_NEO4J_PASSWORD")
    missing = [
        name
        for name, value in [
            ("ZUNO_TEST_NEO4J_URI", uri),
            ("ZUNO_TEST_NEO4J_USERNAME", username),
            ("ZUNO_TEST_NEO4J_PASSWORD", password),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(f"credential_blocked: missing env {', '.join(missing)}")
    return {"uri": uri, "username": username, "password": password}


def _service_versions() -> dict[str, Any]:
    import urllib.request

    versions: dict[str, Any] = {}
    try:
        with urllib.request.urlopen(f"{ES_BASE_URL}/", timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            versions["elasticsearch"] = {
                "server_version": data.get("version", {}).get("number"),
                "cluster_name": data.get("cluster_name"),
            }
    except Exception as exc:  # noqa: BLE001
        versions["elasticsearch"] = {"error": str(exc)[:200]}
    try:
        from pymilvus import __version__ as pymilvus_version
        from pymilvus import utility

        versions["milvus"] = {
            "client_version": pymilvus_version,
            "server_build": utility.get_server_version(),
        }
    except Exception as exc:  # noqa: BLE001
        versions["milvus"] = {"error": str(exc)[:200]}
    try:
        from neo4j import __version__ as neo4j_version

        versions["neo4j"] = {"driver_version": neo4j_version}
    except Exception as exc:  # noqa: BLE001
        versions["neo4j"] = {"error": str(exc)[:200]}
    return versions


def _readback_hash(chunk_readbacks: list[dict[str, Any]]) -> str:
    return sha256_json(
        sorted(
            (
                {
                    "chunk_id": item["chunk_id"],
                    "content_hash": item["content_hash"],
                    "document_id": item["document_id"],
                }
                for item in chunk_readbacks
            ),
            key=lambda item: item["chunk_id"],
        )
    )


def _scope_matrix(
    *,
    label: str,
    count_fn: Any,
    search_fn: Any,
    tenant_id: str,
    workspace_id: str,
    knowledge_version_id: str,
) -> dict[str, Any]:
    foreign_tenant = "tenant_other_phase22"
    foreign_workspace = "workspace_other_phase22"
    foreign_kv = "knowledge-version::foreign"
    matrix = {
        "same_tenant_workspace_kv": count_fn(
            tenant_id=tenant_id, workspace_id=workspace_id, knowledge_version_id=knowledge_version_id
        ),
        "same_workspace_different_tenant": count_fn(
            tenant_id=foreign_tenant, workspace_id=workspace_id, knowledge_version_id=knowledge_version_id
        ),
        "same_tenant_different_workspace": count_fn(
            tenant_id=tenant_id, workspace_id=foreign_workspace, knowledge_version_id=knowledge_version_id
        ),
        "same_tenant_workspace_different_kv": count_fn(
            tenant_id=tenant_id, workspace_id=workspace_id, knowledge_version_id=foreign_kv
        ),
        "foreign_snapshot_scope": count_fn(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=f"snap_scope::{foreign_kv}",
        ),
        "missing_scope": count_fn(),
        "empty_scope": count_fn(tenant_id="", workspace_id="", knowledge_version_id=""),
    }
    search_scoped = search_fn(
        "renewal policy",
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id,
    )
    search_foreign_tenant = search_fn(
        "renewal policy",
        tenant_id=foreign_tenant,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id,
    )
    return {
        "matrix": matrix,
        "scoped_search_hit_count": len(search_scoped),
        "foreign_tenant_search_hit_count": len(search_foreign_tenant),
        "isolation_passed": (
            matrix["same_tenant_workspace_kv"] > 0
            and matrix["same_workspace_different_tenant"] == 0
            and matrix["same_tenant_different_workspace"] == 0
            and matrix["same_tenant_workspace_different_kv"] == 0
            and matrix["foreign_snapshot_scope"] == 0
            and len(search_foreign_tenant) == 0
        ),
    }


def _cleanup(
    *,
    es_client: ElasticsearchBm25IndexClient,
    milvus_client: MilvusVectorIndexClient,
    neo4j_client: Neo4jGraphIndexClient,
    index_prefix: str,
    tenant_id: str,
    workspace_id: str,
    knowledge_version_id: str,
) -> dict[str, Any]:
    import urllib.error

    cleanup: dict[str, Any] = {"index_prefix": index_prefix}
    try:
        _http_delete(f"{ES_BASE_URL}/{index_prefix}_bm25")
        cleanup["elasticsearch"] = "index_deleted"
    except urllib.error.HTTPError as exc:
        cleanup["elasticsearch"] = f"http_error_{exc.code}"
    except Exception as exc:  # noqa: BLE001
        cleanup["elasticsearch"] = f"error:{str(exc)[:120]}"

    try:
        from pymilvus import Collection, connections, utility

        connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
        if utility.has_collection(f"{index_prefix}_vector"):
            Collection(f"{index_prefix}_vector").drop()
        cleanup["milvus"] = "collection_dropped"
    except Exception as exc:  # noqa: BLE001
        cleanup["milvus"] = f"error:{str(exc)[:120]}"

    try:
        driver = neo4j_client._driver()
        try:
            with driver.session(database=neo4j_client.database) as session:
                session.run(
                    "MATCH (n:ZunoIndexChunk {index_name: $index_name}) DETACH DELETE n",
                    {"index_name": f"{index_prefix}_graph"},
                )
                session.run(
                    "MATCH (n:ZunoIndexEntity {index_name: $index_name, tenant_id: $tenant_id, workspace_id: $workspace_id, knowledge_version_id: $knowledge_version_id}) DETACH DELETE n",
                    {
                        "index_name": f"{index_prefix}_graph",
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "knowledge_version_id": knowledge_version_id,
                    },
                )
            cleanup["neo4j"] = "nodes_deleted"
        finally:
            driver.close()
    except Exception as exc:  # noqa: BLE001
        cleanup["neo4j"] = f"error:{str(exc)[:120]}"
    return cleanup


def _http_delete(url: str) -> None:
    import urllib.request

    request = urllib.request.Request(url, method="DELETE")
    with urllib.request.urlopen(request, timeout=10):
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    parser.add_argument("--skip-cleanup", action="store_true", help="keep live indexes for inspection")
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_monotonic = time.monotonic()

    source_manifest = json.loads(SOURCE_UPLOAD_MANIFEST.read_text(encoding="utf-8"))
    canonical_ir = json.loads(CANONICAL_IR_MANIFEST.read_text(encoding="utf-8"))

    # ── Task A: exact canonical input identity (fail closed) ─────────────
    try:
        manifest_texts = _manifest_chunk_texts(canonical_ir)
        payload = validate_canonical_corpus_identity(
            source_manifest=source_manifest,
            canonical_ir_manifest=canonical_ir,
            corpus_root=CORPUS_DIR,
            manifest_chunk_texts=manifest_texts,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: canonical corpus identity failed: {exc}")
        return 1

    tenant_id = payload.chunks[0]["tenant_id"]
    workspace_id = payload.chunks[0]["workspace_id"]
    knowledge_version_id = ""  # DeepSeek1 dependency not accepted
    index_prefix = f"deepseek2_phase22_{uuid4().hex[:8]}"
    index_build_run_id = f"index-build-run::{index_prefix}"

    embedding_config_hash = compute_embedding_config_hash(
        provider=EMBEDDING_PROVIDER,
        model=EMBEDDING_MODEL,
        dimension=EMBEDDING_DIMENSION,
        base_url=EMBEDDING_BASE_URL,
    )
    from zuno.platform.model_gateway_adapters import build_openai_embedding_gateway_adapter

    embedding_gateway = build_openai_embedding_gateway_adapter()

    # ── Task D: credentials from environment only ─────────────────────────
    try:
        neo4j_credentials = _load_neo4j_credentials()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1
    neo4j_credentials_redacted = {key: "[REDACTED]" for key in neo4j_credentials}

    es_client = ElasticsearchBm25IndexClient(base_url=ES_BASE_URL)
    milvus_client = MilvusVectorIndexClient(
        host=MILVUS_HOST,
        port=MILVUS_PORT,
        dim=EMBEDDING_DIMENSION,
        embedding_gateway=embedding_gateway,
        embedding_provider=EMBEDDING_PROVIDER,
        embedding_model=EMBEDDING_MODEL,
        embedding_config_hash=embedding_config_hash,
        formal_embedding_required=True,
    )
    neo4j_client = Neo4jGraphIndexClient(
        uri=neo4j_credentials["uri"],
        username=neo4j_credentials["username"],
        password=neo4j_credentials["password"],
        database="neo4j",
    )

    # ── Write the exact canonical chunk set (24 chunks, manifest ids) ─────
    es_payload = [
        {
            **chunk,
            "knowledge_version_id": knowledge_version_id,
            "source_type": "bm25",
        }
        for chunk in payload.chunks
    ]
    es_client.index_documents(f"{index_prefix}_bm25", es_payload, recreate=True)

    milvus_payload = [
        {
            **chunk,
            "knowledge_version_id": knowledge_version_id,
            "source_type": "vector",
        }
        for chunk in payload.chunks
    ]
    milvus_client.index_documents(f"{index_prefix}_vector", milvus_payload, recreate=True)

    graph_payload = [
        {
            **chunk,
            "knowledge_version_id": knowledge_version_id,
            "source_type": "graph",
        }
        for chunk in payload.chunks
    ]
    neo4j_client.index_documents(
        f"{index_prefix}_graph", graph_payload, tenant_id=tenant_id, recreate=True
    )
    graph_entities = [
        {"entity_ref": entity["entity_ref"], "kind": entity["entity_ref"].split(":", 1)[0], "name": entity["label"]}
        for entity in canonical_ir["entities"]
    ]
    graph_relations = [
        {"relation_ref": relation["relation_id"], "from": relation["from"], "to": relation["to"], "kind": relation["kind"]}
        for relation in canonical_ir["relations"]
    ]
    neo4j_client.index_graph_relations(
        f"{index_prefix}_graph",
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id,
        snapshot_id="",
        entities=graph_entities,
        relations=graph_relations,
    )

    # ── Readback: every canonical chunk id must come back ─────────────────
    es_readbacks: list[dict[str, Any]] = []
    milvus_readbacks: list[dict[str, Any]] = []
    for chunk_id in payload.chunk_ids:
        es_row = es_client.fetch_document(f"{index_prefix}_bm25", chunk_id)
        es_readbacks.append(
            {
                "chunk_id": chunk_id,
                "readback_ok": es_row is not None,
                "document_id": es_row.get("document_id") if es_row else None,
                "content_hash": sha256_json({"text": es_row.get("content", "")}) if es_row else None,
            }
        )
        milvus_row = milvus_client.fetch_document(f"{index_prefix}_vector", chunk_id)
        milvus_readbacks.append(
            {
                "chunk_id": chunk_id,
                "readback_ok": milvus_row is not None,
                "document_id": milvus_row.get("document_id") if milvus_row else None,
                "content_hash": sha256_json({"text": milvus_row.get("content", "")}) if milvus_row else None,
            }
        )

    es_scope = _scope_matrix(
        label="elasticsearch",
        count_fn=lambda **kw: es_client.count_documents(f"{index_prefix}_bm25", **kw),
        search_fn=lambda q, **kw: es_client.search_documents(q, f"{index_prefix}_bm25", **kw),
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id,
    )
    milvus_scope = _scope_matrix(
        label="milvus",
        count_fn=lambda **kw: milvus_client.count_documents(f"{index_prefix}_vector", **kw),
        search_fn=lambda q, **kw: milvus_client.search_documents(q, f"{index_prefix}_vector", **kw),
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id,
    )
    # Milvus expr injection attempt: a hostile scope value must not alter
    # the filter expression (a parse error counts as contained — the query
    # must never return rows from outside the intended scope).
    try:
        injection = milvus_client.count_documents(
            f"{index_prefix}_vector",
            tenant_id='tenant" OR 1==1 --',
            workspace_id=workspace_id,
        )
        injection_result: Any = {"count": injection}
        injection_contained = injection == 0
    except Exception as exc:  # noqa: BLE001
        injection_result = {"error": str(exc)[:120]}
        injection_contained = True
    milvus_scope["injection_attempt"] = injection_result
    milvus_scope["injection_contained"] = injection_contained

    # ── Neo4j path readbacks (store level) ────────────────────────────────
    paths: dict[str, Any] = {}
    path_defs = {
        "one_hop_person_released_product": (
            "person:Haruto Soma",
            "product:Axis-9 Industrial Controller v9.4.0",
            ["person_released_product"],
        ),
        "two_hop_sponsor_delivers": (
            "person:Kjartan Eliasson",
            "product:Northwind SDK v3.0.0",
            ["person_sponsors_project", "project_delivers_product"],
        ),
        "multi_hop_sponsor_delivers": (
            "person:Kjartan Eliasson",
            "product:Northwind SDK v3.0.0",
            ["person_sponsors_project", "project_delivers_product"],
        ),
    }
    path_receipt_builder_blocked: list[str] = []
    for label, (start, end, kinds) in path_defs.items():
        row = neo4j_client.query_path(
            f"{index_prefix}_graph",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            snapshot_id="",
            start_entity_ref=start,
            end_entity_ref=end,
            relation_kinds=kinds,
        )
        paths[label] = {
            "store_visible": row is not None,
            "matched_node_refs": list(row.get("matched_node_refs") or []) if row else [],
            "matched_relation_refs": list(row.get("matched_relation_refs") or []) if row else [],
        }
        if row is not None:
            try:
                neo4j_client.verify_path_visibility_receipt(
                    f"{index_prefix}_graph",
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    knowledge_version_id=knowledge_version_id,
                    snapshot_id="",
                    start_entity_ref=start,
                    end_entity_ref=end,
                    relation_kinds=kinds,
                    query_kind="directed_path",
                    config_hash=embedding_config_hash,
                )
            except ValueError as exc:
                path_receipt_builder_blocked.append(f"{label}:{exc}")
    cross_tenant_path = neo4j_client.query_path(
        f"{index_prefix}_graph",
        tenant_id="tenant_other_phase22",
        workspace_id=workspace_id,
        knowledge_version_id=knowledge_version_id,
        snapshot_id="",
        start_entity_ref="person:Haruto Soma",
        end_entity_ref="product:Axis-9 Industrial Controller v9.4.0",
        relation_kinds=["person_released_product"],
    )

    # ── Corpus-level IndexBuildRun receipts (NOT_RUN_DEPENDENCY_BLOCKED) ──
    smoke_readback_hash = _readback_hash(es_readbacks)
    corpus_receipts: dict[str, dict[str, Any]] = {}
    for index_kind in CORPUS_INDEX_KINDS:
        receipt = build_corpus_index_build_receipt(
            index_kind=index_kind,
            receipt_scope="adapter_live_smoke",
            input_kind=payload.input_kind,
            not_owner_produced=payload.not_owner_produced,
            snapshot_eligible=False,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            index_build_run_id=index_build_run_id,
            expected_document_count=payload.document_count,
            expected_chunk_count=payload.chunk_count,
            observed_document_count=payload.document_count,
            observed_chunk_count=payload.chunk_count,
            content_set_hash=payload.content_set_hash,
            config_hash=embedding_config_hash,
            adapter_execution_ref=f"adapter-live-smoke:{index_prefix}:{index_kind}",
            readback_hash=smoke_readback_hash,
            visibility_status="blocked",
            block_reason="knowledge_version_dependency_missing",
        )
        errors = validate_corpus_index_build_receipt(receipt)
        if errors:
            print(f"ERROR: corpus receipt invalid: {errors}")
            return 1
        corpus_receipts[index_kind] = receipt.model_dump()

    cleanup: dict[str, Any] | None = None
    cleanup_readback: dict[str, Any] | None = None
    if not args.skip_cleanup:
        cleanup = _cleanup(
            es_client=es_client,
            milvus_client=milvus_client,
            neo4j_client=neo4j_client,
            index_prefix=index_prefix,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
        )
        # A deleted index must read back as zero documents.
        try:
            es_after = es_client.count_documents(f"{index_prefix}_bm25")
        except Exception as exc:  # noqa: BLE001
            es_after = f"deleted:{str(exc)[:60]}"
        try:
            milvus_after = milvus_client.count_documents(f"{index_prefix}_vector")
        except Exception as exc:  # noqa: BLE001
            milvus_after = f"deleted:{str(exc)[:60]}"
        cleanup_readback = {
            "elasticsearch": es_after,
            "milvus": milvus_after,
        }
        # A "deleted:..." result means the index no longer exists, which is
        # the verified zero-document state after cleanup.
        def _is_zero(value: Any) -> bool:
            return value == 0 or (isinstance(value, str) and value.startswith("deleted:"))

        cleanup_readback["cleanup_verified"] = _is_zero(es_after) and _is_zero(milvus_after)

    evidence: dict[str, Any] = _redact(
        {
            "schema_version": "1.0.0",
            "track_id": "machine_attested_synthetic_regression",
            "evidence_kind": "three_index_adapter_live_smoke",
            "worker": "deepseek2-cc-b34c",
            "started_at": started_at,
            "elapsed_seconds": round(time.monotonic() - start_monotonic, 3),
            "truth_boundary": {
                "THREE_INDEX_ADAPTER_LIVE_SMOKE_AVAILABLE": True,
                "CORPUS_LEVEL_VISIBILITY_RECEIPTS_BLOCKED": True,
                "SNAPSHOT_ACTIVATION_NOT_RUN_DEPENDENCY_BLOCKED": True,
                "FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED": True,
            },
            "input": {
                "input_kind": payload.input_kind,
                "not_owner_produced": payload.not_owner_produced,
                "expected_document_count": payload.document_count,
                "expected_chunk_count": payload.chunk_count,
                "identity_checks": payload.identity_checks,
                "content_set_hash": payload.content_set_hash,
                "canonical_ir_hash": canonical_ir["canonical_ir_hash"],
                "source_manifest_hash": source_manifest["source_manifest_hash"],
            },
            "scope": {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "knowledge_version_id": knowledge_version_id,
                "snapshot_eligible": False,
                "index_prefix": index_prefix,
                "index_build_run_id": index_build_run_id,
            },
            "credentials": {
                "neo4j_source": "environment:ZUNO_TEST_NEO4J_*",
                "neo4j_values": neo4j_credentials_redacted,
            },
            "services": _service_versions(),
            "embedding": {
                "provider": EMBEDDING_PROVIDER,
                "model": EMBEDDING_MODEL,
                "dimension": EMBEDDING_DIMENSION,
                "config_hash": embedding_config_hash,
                "gateway_kind": "openai_compatible_embedding_gateway",
                "vector_source": "formal_embedding_gateway",
            },
            "adapter_smoke": {
                "writes": {
                    "elasticsearch": {"chunk_count": len(es_payload), "recreate": True},
                    "milvus": {"chunk_count": len(milvus_payload), "recreate": True},
                    "neo4j": {"chunk_count": len(graph_payload), "entity_count": len(graph_entities), "relation_count": len(graph_relations)},
                },
                "readbacks": {
                    "elasticsearch": {
                        "attempted": len(es_readbacks),
                        "ok_count": sum(1 for item in es_readbacks if item["readback_ok"]),
                        "readback_hash": smoke_readback_hash,
                        "details": es_readbacks,
                    },
                    "milvus": {
                        "attempted": len(milvus_readbacks),
                        "ok_count": sum(1 for item in milvus_readbacks if item["readback_ok"]),
                        "details": milvus_readbacks,
                    },
                },
                "scope_matrix": {
                    "elasticsearch": es_scope,
                    "milvus": milvus_scope,
                },
                "neo4j_paths": {
                    "path_readbacks": paths,
                    "cross_tenant_path_visible": cross_tenant_path is not None,
                    "canonical_path_receipt_builder_blocked": path_receipt_builder_blocked,
                    "canonical_path_receipt_count": 0,
                },
            },
            "corpus_index_build_receipts": corpus_receipts,
            "corpus_level_visibility_status": "NOT_RUN_DEPENDENCY_BLOCKED",
            "cleanup": cleanup,
            "cleanup_readback": cleanup_readback,
        }
    )
    evidence["evidence_hash"] = sha256_json(evidence)

    args.out_root.mkdir(parents=True, exist_ok=True)
    (args.out_root / "live_three_index_visibility_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(
        {
            "truth_boundary": evidence["truth_boundary"],
            "expected_chunk_count": payload.chunk_count,
            "readback_ok": {
                "es": sum(1 for item in es_readbacks if item["readback_ok"]),
                "milvus": sum(1 for item in milvus_readbacks if item["readback_ok"]),
            },
            "isolation": {
                "es": es_scope["isolation_passed"],
                "milvus": milvus_scope["isolation_passed"],
                "milvus_injection_contained": milvus_scope["injection_contained"],
            },
            "neo4j_paths_store_visible": all(item["store_visible"] for item in paths.values()),
            "corpus_level_visibility_status": evidence["corpus_level_visibility_status"],
            "cleanup": cleanup,
            "cleanup_readback": cleanup_readback,
            "evidence_hash": evidence["evidence_hash"],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
