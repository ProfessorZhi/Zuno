# PHASE22 DeepSeek2 (CC-B3/B4/C) Runtime Truth Facts — Hardening Pass

Worker: DeepSeek2 (Claude Code)
Task: PHASE22-CC-B3-B4-C-RUNTIME-TRUTH-HARDENING
Date: 2026-08-03
Branch: claude/deepseek2-phase22-index-snapshot-profiles (PR #113, Draft)

## 1. Truth Boundary (current, honest)

```
THREE_INDEX_ADAPTER_LIVE_SMOKE_AVAILABLE          = true
CORPUS_LEVEL_VISIBILITY_RECEIPTS_BLOCKED          = true
SNAPSHOT_ACTIVATION_NOT_RUN_DEPENDENCY_BLOCKED    = true
FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED   = true
```

No `all_visibility_passed` claim exists anywhere in the evidence.
Dependency: DeepSeek1 PR #112 (head `bf4b2cb11b53e78b3a7242df5996e4aed2cc1a4b`) is
`REQUEST_WORKER_CHANGES` and is NOT accepted; `knowledge_version_id = null`.

## 2. Canonical Corpus Identity (Task A)

- Canonical IR manifest: 8 documents, 24 chunks (exact).
- Adapter smoke consumed the frozen candidate manifest payload ONLY:
  `input_kind = frozen_candidate_manifest`, `not_owner_produced = true`,
  `knowledge_version_id = null`, `snapshot_eligible = false`.
- Identity validation passed (fail closed): document count equal, chunk
  count equal, chunk id set equal, every chunk text hash equal, no extra
  text, no missing chunk. No re-chunking — the canonical 24-chunk set was
  written as-is (no 35-chunk divergence).
- Writes: ES 24 / Milvus 24 / Neo4j 24 chunks + 15 entities + 5 relations.
- Readback: 24/24 chunk ids read back (ES and Milvus), per-chunk content
  hash verified, readback hash recorded.

## 3. Corpus-level IndexBuildRun Receipts (Task B)

One receipt per index kind, all `NOT_RUN_DEPENDENCY_BLOCKED`:
`receipt_scope = adapter_live_smoke`, `snapshot_eligible = false`,
`visibility_status = blocked`, `block_reason = knowledge_version_dependency_missing`.

Each receipt binds: tenant_id, workspace_id, knowledge_version_id (empty),
index_build_run_id, index_kind, expected_document_count=8,
expected_chunk_count=24, observed counts, content_set_hash, config_hash,
adapter_execution_ref, readback_hash, payload_hash.

Receipt refs (final run):
- elasticsearch_bm25: `corpus-index-build:elasticsearch_bm25:<hash[:16]>`
- milvus_vector: `corpus-index-build:milvus_vector:<hash[:16]>`
- neo4j_graph: `corpus-index-build:neo4j_graph:<hash[:16]>`
(exact values in `live_three_index_visibility_evidence.json` →
`corpus_index_build_receipts`)

## 4. Tenant / Workspace / Version Isolation (Task C)

Full scope matrix executed on ES and Milvus (all passed):

| Scope | ES | Milvus |
| --- | --- | --- |
| same tenant/workspace/kv | 24 | 24 |
| same workspace, different tenant | 0 | 0 |
| same tenant, different workspace | 0 | 0 |
| same tenant/workspace, different kv | 0 | 0 |
| foreign snapshot scope | 0 | 0 |
| missing scope | 24 (unscoped, documented) | 24 (unscoped, documented) |
| empty scope | 24 (unscoped, documented) | 24 (unscoped, documented) |

- Milvus search filter is passed as the TOP-LEVEL `expr` search argument
  (PyMilvus >= 2.4; `expr` inside `param` is silently ignored and would
  leak rows across scopes — fixed in this pass).
- Milvus literals are escaped (`_milvus_literal`); injection attempt
  `tenant" OR 1==1 --` contained (0 rows).
- Neo4j paths store-visible (1-hop / 2-hop / multi-hop); cross-tenant path
  query returns no rows; canonical path receipt emission blocked on
  knowledge_version_id (recorded `canonical_path_receipt_builder_blocked`).

## 5. Credentials (Task D)

- No credential in source: `neo4j12345` removed from the runner and the
  integration test.
- Credentials come from `ZUNO_TEST_NEO4J_URI` / `ZUNO_TEST_NEO4J_USERNAME` /
  `ZUNO_TEST_NEO4J_PASSWORD`; missing credentials → `credential_blocked`.
- Evidence redacts password / api_key / authorization / bearer / secret /
  token keys; credential source recorded, values never.

## 6. Snapshot Activation (Task E)

- Status: `NOT_RUN_DEPENDENCY_BLOCKED`; snapshot_id null;
  knowledge_version_id null; dependency_accepted false.
- 14-gate hardened adapter (duplicate kinds, per-receipt
  tenant/workspace/kv consistency, non-empty manifest hash, identical
  content_set_hash, owner kinds, payload hashes, unique ES/Milvus/Neo4j
  receipts, mandatory Neo4j path receipt, frozen embedding config, formal
  scope only, missing/unknown blocked) — unit-tested (17 tests).
- Persistence: formal `KnowledgeRepository.create_snapshot` exists;
  `PostgresKnowledgeSnapshotPersistence` reuses it (no new migration).
  Activation path proven in unit tests: deterministic snapshot id,
  re-readable persisted fact, immutable content set, distinct content hash
  → distinct snapshot.
- Activation receipt: `snapshot-activation:472dc3135ab0b9a3` (blocked-state).

## 7. Four-Profile Runtime (Tasks F/G)

- Status: `FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED`; per-profile
  BLOCKED with `knowledge_version_dependency_missing`; `profile_run_ids: []`;
  NO fabricated `RUNTIME_OBSERVED`; placeholder runtime engine deleted.
- Formal runtime owners resolved (all `OWNER_AVAILABLE`):
  standard_rag → `RagHandler.retrieve_ranked_documents`;
  local_graphrag → `GraphRetriever.retrieve` (neighbor traversal);
  deep_graphrag → `GraphRetriever.retrieve` (multi-hop);
  agentic_graphrag → `build_agent_graph` + `UnifiedAgentRuntimeService`
  (fixed AgentRunGraph + dynamic Plan DAG + StepExecutionGraph).
  Missing owners would report `PROFILE_RUNTIME_OWNER_MISSING:<profile>`.
- Release decision: `BLOCKED` (`profile_not_measured`), scope
  `machine_attested_synthetic_regression`; decision_hash
  `aebc93bb2d65236740a7b11b6a55390e0f15216546fcff7c60d790467067345d`.

## 8. Gold Isolation (Task H)

- 320 requests (80 cases x 4 profiles): forbidden gold field count = 0.
- Scan surfaces: runtime_request, prompt, trace, retrieval_context,
  tool_arguments, planner_input, step_input, final_synthesis_input.
- Trace scan: 0 trace files → `trace_gold_isolation_status =
  NOT_RUN_DEPENDENCY_BLOCKED`; scan of zero traces is never a pass.

## 9. Services

| Service | Version |
| --- | --- |
| Elasticsearch | 7.17.24 (docker-cluster) |
| Milvus | server v2.4.15 / pymilvus 2.6.11 |
| Neo4j | driver 5.28.1 |
| Embedding | dashscope text-embedding-v4, dim 1024, config hash `sha256:d4d77f48…` |

## 10. Evidence Hashes (final)

| Artifact | Hash |
| --- | --- |
| live_three_index_visibility_evidence.json | `13ef02d85331e7a3ce7a94724b9166afaf17d3a8e15715cfb4eca62959cdb2b3` |
| snapshot_activation_evidence.json | `582e546319b702226e7f4d479ba1e91bb38d539594f1b8b3e4897458e64677e3` |
| four_profile_runtime_evidence.json | `323d5b723ccbeca65f80fed12d1127bee63d6f9ba67aa8dfdf76df58d9c84a80` |

## 11. Cleanup

- ES index deleted; Milvus collection dropped; Neo4j chunk/entity nodes
  deleted; cleanup readback verified (deleted → zero documents).

## 12. Remaining Gaps (honest)

- Real `knowledge_version_id` (DeepSeek1 PR #112 not accepted) → snapshot
  activation, corpus-level visible receipts, Neo4j canonical path receipt,
  four-profile measured runs all remain dependency-blocked.
- Four-profile execution through the formal owners + measurement gate:
  wired and owner-resolved, not executed (no snapshot).
