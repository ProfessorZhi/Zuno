# PHASE22 DeepSeek2 (CC-B3/B4) Runtime Truth Facts — Snapshot Fail-Closed Final

Worker: DeepSeek2 (Claude Code)
Task: PHASE22-CC-B3-B4-SNAPSHOT-FAIL-CLOSED-FINAL
Date: 2026-08-04
Branch: claude/deepseek2-phase22-index-snapshot-profiles (PR #113, Draft)

## 1. Truth Boundary (current, honest)

```
THREE_INDEX_ADAPTER_LIVE_SMOKE_AVAILABLE          = true
CORPUS_LEVEL_VISIBILITY_RECEIPTS_BLOCKED          = true
SNAPSHOT_ACTIVATION_NOT_RUN_DEPENDENCY_BLOCKED    = true
FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED   = true
snapshot_id = null
profile_run_ids = []
metrics_computed = false
release_decision = BLOCKED
```

Dependency: DeepSeek1 PR #112 candidate head `ce495af2a39c01379878a9e2c1bb58d876456b1e`,
coordinator state REQUEST_WORKER_CHANGES, `dependency_accepted=false`,
`knowledge_version_id=null`. No `all_visibility_passed` claim exists.

## 2. Five Hash Identities (Task G — recorded separately, never conflated)

| Hash | Value |
| --- | --- |
| dataset_corpus_hash | `749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4` |
| source_manifest_hash | `0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a` |
| canonical_ir_hash | `43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6` |
| content_set_hash | `77f1d7dbd30d2ed26d94c788dc0447a082807f9ac623092762e326a611955be9` (deterministic from the 24 canonical chunks) |
| embedding_config_hash | `sha256:d4d77f48b3dcc15f5abdb0a8e1d610c0cccd38f3c5bf7d5a7464c84b7863961d` |

## 3. Canonical Corpus + Source Manifest Identity (Task F)

`validate_canonical_corpus_identity` validates BOTH manifests fail-closed:
source_count=8, source paths exist, source hashes match corpus file text
(sha256 of UTF-8 content), document ids consistent, source tenant /
workspace all identical, canonical IR documents 1:1 with source manifest
documents, chunk documents exist, recomputed source_manifest_hash valid,
canonical_ir.source_manifest_hash binds the source manifest, corpus files
exact (no extra/missing), plus the 24-chunk identity (counts, id set,
per-chunk text hashes).  Input remains `input_kind=frozen_candidate_manifest`,
`not_owner_produced=true`, `snapshot_eligible=false`.

## 4. Adapter Live Smoke (24 canonical chunks)

- Writes: ES 24 / Milvus 24 / Neo4j 24 chunks + 15 entities + 5 relations.
- Readback: 24/24 chunk ids (ES + Milvus), content hashes verified.
- Credentials: `ZUNO_TEST_NEO4J_*` environment only (source: env, values
  redacted in evidence); missing → credential_blocked.

## 5. Index Query Scope Fail-Closed (Task E)

- `ScopeValidationError` raised for missing / None / empty tenant_id,
  workspace_id or knowledge_version_id on ES search/count, Milvus
  search/count and Neo4j query_path — no unscoped query is ever executed.
- Scope matrix (ES + Milvus, all passed):
  - same tenant/workspace/kv (kv empty while dependency blocked): REJECTED
    (`query_executed=false`, `rejected=true`)
  - missing scope: REJECTED; empty scope: REJECTED
  - same workspace, foreign tenant: 0 rows (executed)
  - same tenant, foreign workspace: 0 rows
  - same tenant/workspace, foreign kv: 0 rows
  - foreign snapshot scope: 0 rows
  - scoped search (kv empty): REJECTED; foreign-tenant search: 0 hits
  - Milvus expr injection `tenant" OR 1==1 --`: contained (0 rows)
- Neo4j path queries (kv empty): REJECTED (fail closed);
  cross-tenant path with foreign kv: 0 rows.
- Milvus search expr is the TOP-LEVEL search argument (PyMilvus >= 2.4);
  literals escaped via `_milvus_literal`.

## 6. Snapshot Persistence Hard Gate (Tasks A/B/C/D)

- No persistence port → BLOCKED (`snapshot_persistence_port_missing`).
- persist() raises → BLOCKED (`snapshot_persistence_failed`).
- Readback missing → BLOCKED (`snapshot_readback_inconsistent:
  snapshot_readback_missing`).
- Readback scope/hash mismatch (snapshot_id / tenant_id /
  knowledge_version_id / snapshot_hash / serving_watermark_ref) → BLOCKED.
- ACTIVATED requires: port configured, create_snapshot committed in a UoW,
  tenant-scoped readback success, all ten identity checks equal, all
  consistency checks strictly True, receipt hash valid.
- Receipt is built ONLY after the persisted fact is verified (never
  ACTIVATED-then-persist).
- Tenant-scoped read port `read(*, tenant_id, workspace_id,
  knowledge_version_id, snapshot_id)` — workspace validated through the
  KnowledgeVersion owner (knowledge_domain_versions join); foreign scope
  → no row.
- Idempotent retry returns the same snapshot; same snapshot id with a
  different payload hash → BLOCKED (immutable, ON CONFLICT DO NOTHING +
  hash check); different content set → different snapshot.
- Fault tests: port missing, persist raises, persist-no-write, wrong
  tenant, wrong kv, wrong hash, receipt-before-crash retry, payload
  conflict, database commit failure — all covered in
  test_snapshot_activation_runtime.py (28 tests).

Current status: `NOT_RUN_DEPENDENCY_BLOCKED` (unit tests prove the
activated path; the formal evidence stays blocked because PR #112 is not
accepted).

## 7. Four-Profile Runtime

- `FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED`; per-profile BLOCKED
  with `knowledge_version_dependency_missing`; profile_run_ids [];
  no RUNTIME_OBSERVED; formal owners all OWNER_AVAILABLE (RagHandler /
  GraphRetriever / build_agent_graph + UnifiedAgentRuntimeService).
- Release decision BLOCKED (`profile_not_measured`), decision_hash
  `aebc93bb2d65236740a7b11b6a55390e0f15216546fcff7c60d790467067345d`.

## 8. Gold Isolation

- 320 requests: forbidden field count 0; 0 trace files →
  `trace_gold_isolation_status = NOT_RUN_DEPENDENCY_BLOCKED` (never a pass).

## 9. Services

Elasticsearch 7.17.24 (docker-cluster) / Milvus v2.4.15 (pymilvus 2.6.11) /
Neo4j driver 5.28.1 / Embedding dashscope text-embedding-v4 dim 1024.

## 10. Evidence Hashes (final)

| Artifact | Hash |
| --- | --- |
| live_three_index_visibility_evidence.json | `995817e90a889bcd4a67f1ab4372d755f2f2beceeedcbc8e9475d1096edc0f7e` |
| snapshot_activation_evidence.json | `78ce8451ec3ca8969d7772a4f0c5c52e595092882e35b3c1335bfae5e0a73edb` |
| four_profile_runtime_evidence.json | `3fb78fc39ca9944e8722d7f66dcd119be15f9e6475e697c1136359003d7520fa` |

## 11. Cleanup

ES index deleted, Milvus collection dropped, Neo4j nodes deleted;
cleanup readback verified (deleted → zero documents).

## 12. Remaining Gaps (honest)

- Real knowledge_version_id (PR #112 not accepted) → corpus-level visible
  receipts, Neo4j canonical path receipts, snapshot activation, four-profile
  measured runs all dependency-blocked.
- Snapshot persistence gate is proven by unit tests; live persistence runs
  only after the dependency lands.
