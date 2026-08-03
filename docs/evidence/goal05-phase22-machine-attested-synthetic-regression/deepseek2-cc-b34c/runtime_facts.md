# PHASE22 DeepSeek2 (CC-B3/B4/C) Runtime Facts

Worker: DeepSeek2 (Claude Code)
Task: PHASE22-CC-B3-B4-C — Three Index Visibility / Snapshot Activation / Four Profile Runtime
Date: 2026-08-03
Branch: claude/deepseek2-phase22-index-snapshot-profiles

## 1. Live Services (verified reachable during the run)

| Service | Endpoint | Version |
| --- | --- | --- |
| Elasticsearch | http://localhost:9200 | 7.17.24 (docker-cluster) |
| Milvus | localhost:19530 (health 9091) | server v2.4.15 / pymilvus 2.6.11 |
| Neo4j | bolt://localhost:7687 (database `neo4j`) | driver 5.28.1 |
| MinIO | localhost:9000 | running (not exercised by this worker) |

## 2. Embedding Configuration (frozen)

- Provider: `dashscope`
- Model: `text-embedding-v4`
- Dimension: `1024`
- Gateway: OpenAI-compatible embedding gateway (`build_openai_embedding_gateway_adapter`)
- Config Hash: `sha256:d4d77f48b3dcc15f5abdb0a8e1d610c0cccd38f3c5bf7d5a7464c84b7863961d`
- Vector source: `formal_embedding_gateway` (real model embeddings; no random / fixed / gold vectors)

## 3. Live Index Names (isolated namespace, cleaned up after run)

- ES index: `deepseek2_phase22_9a9735f3_bm25` (deleted after evidence capture)
- Milvus collection: `deepseek2_phase22_9a9735f3_vector` (dropped after evidence capture)
- Neo4j nodes: `ZunoIndexChunk` / `ZunoIndexEntity` under `deepseek2_phase22_9a9735f3_graph` (deleted after evidence capture)

## 4. Visibility Receipts (authentic, canonical owner builders)

| Target | Receipt kind | Receipt ref | Visibility | Sample matches |
| --- | --- | --- | --- | --- |
| bm25 | elasticsearch_bm25_visibility | `index-visibility:bm25:6f6db812517fceb3` | visible | 4 |
| vector | milvus_vector_visibility | `index-visibility:vector:71672246b8621a57` | visible | 4 |
| graph | neo4j_graph_visibility | `index-visibility:graph:bd6fc455372e6722` | visible | 4 |

(The receipt payload hashes are inside `live_three_index_visibility_evidence.json` under `visibility_receipt_refs`; they are regenerated per isolated run namespace.)

- Chunks written and read back: 35/35 (ES and Milvus by chunk_id).
- Tenant/workspace isolation: wrong-tenant and wrong-workspace queries return 0 hits (ES, Milvus, Neo4j paths).
- Rebuild idempotency: full corpus re-index keeps counts stable (35 -> 35) and receipt payload hashes identical.
- Neo4j path readbacks (store level): 1-hop (Haruto Soma -> Axis-9), 2-hop (Kjartan Eliasson -> Northwind -> Northwind SDK), multi-hop `*1..5`; cross-tenant path query returns no rows.
- Neo4j canonical path receipt emission is blocked while `knowledge_version_id` is empty (canonical owner builder refuses; recorded as `canonical_receipt_builder_blocked`).

## 5. Snapshot Activation

- Status: `NOT_RUN_DEPENDENCY_BLOCKED`
- block_reason: `knowledge_version_dependency_missing`
- snapshot_id: `null`
- knowledge_version_id: `null`
- dependency_pr: `null` (DeepSeek1 canonical ingestion PR not yet opened)
- dependency_head_sha: `null`
- Activation receipt: `snapshot-activation:dfd7a8a7a127fe52` (blocked-state receipt, valid)
- Activation evidence: `snapshot_activation_evidence.json`

## 6. Four-Profile Benchmark

- Status: `FOUR_PROFILE_RUNTIME_BLOCKED` (block_reason `knowledge_version_dependency_missing`)
- Requests built: 320 (80 cases x 4 profiles), gold forbidden fields: 0
- snapshot_id: `null` -> per-profile `blocked_not_measured`, `profile_run_ids: []`
- runtime_metrics_ref: `null`, metrics computed: false
- Release decision: `BLOCKED` (`profile_not_measured`), scope `machine_attested_synthetic_regression`
- decision_hash: `aebc93bb2d65236740a7b11b6a55390e0f15216546fcff7c60d790467067345d`
- Evidence: `four_profile_runtime_evidence.json`, `gold_isolation_scan.json`

## 7. Evidence Hashes

| Artifact | Hash |
| --- | --- |
| live_three_index_visibility_evidence.json | `9156e193d5019445bb381d57d6f4d79e25b9f95c2e7f668098eee8c1022ed2d4` |
| snapshot_activation_evidence.json | `23b522bf58e65f2272200b9a151de71908e4c3a7816b9cbb6e36cc8c73803eb4` |
| four_profile_runtime_evidence.json | `0f31ab1acfc9ea614258e6c376b793b3999d7101d0a08509f30642382f1843a0` |

## 8. Cleanup

- ES index deleted; Milvus collection dropped; Neo4j chunk/entity nodes deleted (recorded in evidence `cleanup`).

## 9. Remaining Gaps (honest)

- Real `knowledge_version_id` / activated `snapshot_id` — depends on DeepSeek1 canonical ingestion (GAP-B1/B2).
- Neo4j canonical path visibility receipt emission — blocked on knowledge_version_id.
- Four-profile measured runs + metrics + release decision PASSED/FAILED — blocked on snapshot activation.
- Gold isolation trace-level scan: no profile traces exist yet (request-level scan: 0 forbidden).
