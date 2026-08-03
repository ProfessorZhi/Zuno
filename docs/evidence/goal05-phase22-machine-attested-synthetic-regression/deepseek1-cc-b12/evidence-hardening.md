# Goal05 PHASE22 Worker DeepSeek1 (CC-B1/B2) Hardening Evidence

## Identity

- agent: claude-code
- provider: deepseek
- worker: DeepSeek1
- worker_task_id: PHASE22-CC-B1-B2-CANONICAL-HARDENING
- branch: `claude/deepseek1-phase22-canonical-ingestion`
- pr: https://github.com/ProfessorZhi/Zuno/pull/112
- run_at: 2026-08-03T22:50:00+08:00
- model: deepseek-v4-flash (session)
- cost: NOT_AVAILABLE / NOT_AVAILABLE

## Status

```text
status: CC_B1_B2_COMPLETION_CANDIDATE
scope: GAP-B1 canonical ingestion, GAP-B2 MinIO/PostgreSQL facts (hardened)
no fake IDs; no Snapshot activation; no three-index visibility; no PHASE22
completion claim; no production readiness claim
```

## Task A — Clean Alembic Bootstrap

`infra/db/alembic/env.py` imported the deleted `zuno.settings` shim; every
`alembic` invocation failed. Fixed to the current official entry
`zuno.platform.settings`. Regression tests prove a fresh empty database
reaches the single migration head, downgrade to base, and re-upgrade:

```text
alembic upgrade head   -> exit 0 (from scratch DB)
alembic current        -> 20260803_58
alembic heads          -> 20260803_58 (single head)
alembic downgrade base -> exit 0; re-upgrade -> exit 0
migration head:        20260803_58
```

## Task B — Canonical Run Domain State

No equivalent run/state table existed (verified against all public tables).
Reversible migration `20260803_57` adds:

```text
canonical_ingestion_runs
    run_id, tenant_id, workspace_id, source_set_ref, corpus_manifest_ref,
    current_state, state_version (optimistic), attempt_number,
    knowledge_version_id, last_error_code, last_error_detail,
    idempotency_key, payload_hash, created_at, updated_at, completed_at
canonical_ingestion_run_history   (append-only transitions)
```

Every write: read current (FOR UPDATE) -> validate declared transition ->
update current fact -> append history + outbox event -> commit one UoW.
Outbox delivery events are written in the same transaction and never serve as
the current-state query source.

## Task C — State Machine Enforcement

```text
accepted -> object_staged -> object_committed -> canonical_ir_ready
         -> knowledge_version_ready
failures: security_denied | credential_blocked | object_stage_failed
        | object_commit_failed | canonicalization_failed
        | reconciliation_required
explicit retry: object_stage_failed -> object_staged;
                object_commit_failed -> object_committed;
                canonicalization_failed -> object_committed (re-parse)
reconciliation: any active state -> reconciliation_required;
                knowledge_version_ready -> reconciliation_required (only edge)
reconciliation resume: reconciliation_required -> object_staged |
                       object_committed | canonical_ir_ready
```

Stage failure is recorded as `object_stage_failed` — never the illegal
`accepted -> object_commit_failed`. Terminal states reject ordinary
overwrites; the run store raises and the durable state is unchanged.

## Task D — Security Ownership

`IngestionSecurityClassifier` (self-approving) was removed. The command now
carries a Security-owned decision (`security_decision_ref`) and the runtime
only validates:

- decision exists for the tenant (`security_authorization_decisions`)
- action == `ingestion.source.upload`
- resource_ref == `ingestion:source:{tenant}:{workspace}:{source_id}`
- epoch_ref matches the command's security epoch
- prepared_action_hash == source content hash
- principal context tenant + principal match
- `validate_pre_effect_authorization` (epoch active, not DENY, approval ok)
- decision == `USE_ONLY`

Missing / stale / scope-mismatch / hash-mismatch / denied -> fail closed to
`security_denied`. Ingestion never issues or approves decisions.

## Task E — Entity / Relation PostgreSQL Facts

Reversible migration `20260803_58` adds `knowledge_entities` and
`knowledge_relations` (directed, from<>to, idempotent unique keys, hash
columns, tenant/workspace/knowledge-version scope). Neo4j remains an
index/read-model owner. Facts are consumed from the frozen canonical IR
manifest (the formal extractor output) — no token-regex extraction.

## Task F — Official Corpus Ingestion (live)

Consumed the frozen PR #107 artifacts only (source upload manifest, canonical
IR manifest, official corpus files). Corpus file hashes verified against the
frozen manifest (LF-normalized byte basis; git autocrlf on Windows can
materialize CRLF). The run pinned the isolated verification tenant
`tenant_auroralis_verify` (the official tenant holds unverified CC-A
preparation candidates: 8 sources, 59 legacy chunks, `runtime_ingested:
false`); all corpus identity fields come from the frozen manifest unchanged.

```text
corpus_hash:            0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a
source_count:           8
document_count:         8
chunk_count:            24        (knowledge_chunks, official chunk ids)
entity_count:           15        (knowledge_entities)
relation_count:         5         (knowledge_relations, directed)
knowledge_version_id:   knowledge-version:tenant_auroralis_verify:workspace_regression_verify:space::tenant_auroralis::workspace_regression::phase22-synthetic:1
document_set_hash:      18fd8a5704723b3c3410901bf565b7273d98ed1e2f9add43f97cc869e7e6ee39 (matches)
security_epoch_ref:     security-epoch:tenant_auroralis_verify:phase22-corpus
migration_head:         20260803_58
reconciliation:         PASSED (all IDs/counts match the official manifest)
rerun:                  idempotent (same knowledge_version_id, same facts)
```

8 source IDs (official manifest form), 8 document_version IDs
(`document-version:source::...:1`), 24 chunk IDs (`chunk::doc_*::NNN`), 15
entity IDs (`entity::org:Auroralis`, ...), 5 relation IDs
(`relation::person_issued_corrective_action::person:Nadya Soroka::product:Forge-X1`,
...), 8 run IDs, 8 security decision refs
(`decision:tenant_auroralis_verify:source::...:1`).

MinIO object refs (bucket `zuno-phase22-corpus-evidence`, per-source manifest
hashes equal the frozen source hashes):

```text
s3://zuno-phase22-corpus-evidence/tenant_auroralis_verify/workspace_regression_verify/source/source::tenant_auroralis::workspace_regression::doc_axis9_release_notes/doc_axis9_release_notes.md  (84949fd0...)
s3://.../doc_forge_recall/doc_forge_recall.md                          (273b2f35...)
s3://.../doc_legal_audit_2026_q1/doc_legal_audit_2026_q1.md            (d922d366...)
s3://.../doc_northwind_charter/doc_northwind_charter.md                (7ac618d8...)
s3://.../doc_northwind_sdk_overview/doc_northwind_sdk_overview.md      (61cc1f5e...)
s3://.../doc_org_chart_2026/doc_org_chart_2026.md                      (34caeaa6...)
s3://.../doc_security_policy_2024/doc_security_policy_2024.md          (0eed3f77...)
s3://.../doc_security_policy_2026/doc_security_policy_2026.md          (5f77b8d3...)
```

## Task G — Resume / Fault Matrix (live, 9 tests)

Crash simulation at every durable boundary (test-only fault hook, same
pattern as `DurableMinioObjectStore._after_physical_commit`):

1. crash after `object_staged` -> resume completes
2. crash after `object_committed` -> resume completes
3. crash after DocumentVersion commit -> resume; 1 source/document row
4. crash after ParseSnapshot commit -> resume; 1 attempt, 1 snapshot
5/6. crash after Chunk/Entity/Relation commit -> resume; no duplicates
7. crash after KnowledgeVersion commit, before receipt -> idempotent receipt
8. physical object present, manifest uncertain -> reconciliation_required;
   resume after reconcile recreates the manifest and completes
9. manifest exists, domain state behind -> resume completes, no duplicates
10. duplicate worker claim -> second worker returns the same facts
    idempotently; 1 parse attempt

No blind retry: failures only leave through explicit retry transitions;
unknown side effects enter `reconciliation_required`.

## Task H — Quality and Receipt Truth

- quality scores are measured by the deterministic quality contract
  (`HumanReviewRuntime.min_block_confidence` on the parsed IR); the persisted
  `coverage_score`/`confidence_score` equal the measured value (test-verified),
  never 1.0/1.0 by construction
- receipts are reconstructed only from owner rows: run row, source row,
  document version row (by source binding), parse snapshot row (by document),
  object manifest row, knowledge version/chunk/entity/relation facts —
  no naming-convention reconstruction (test: `object_manifest_hash` comes
  from the manifest row, not the source hash)
- entity/relation lookups are bound by tenant_id + workspace_id +
  knowledge_version_id (no outbox-event ordering)

## Command Log

| command | exit_code | notes |
| --- | --- | --- |
| `alembic -c infra/db/alembic.ini upgrade head` (dev DB) | 0 | 57 + 58 applied |
| `alembic -c infra/db/alembic.ini heads` | 0 | single head `20260803_58` |
| `alembic downgrade base` + re-`upgrade head` | 0 | reversible |
| required pytest (`test_canonical_ingestion_runtime.py` + `test_index_jobs_runtime.py`) | 0 | 51 passed |
| `test_phase22_canonical_ingestion_live.py` (resume/fault matrix) | 0 | 9 passed |
| `test_phase22_official_corpus_live.py` (official corpus) | 0 | 4 passed |
| `test_phase22_clean_db_bootstrap.py` | 0 | 3 passed |
| `test_workspace_package_a_production_bootstrap.py` | 0 | 2 passed |
| official corpus evidence run (IDs above) | 0 | rerun idempotent |
| `git diff --check` | 0 | clean |

Services: PostgreSQL 16.14, MinIO RELEASE.2023-03-20T20-16-18Z, RabbitMQ
3.13 (docker compose).

Cleanup: evidence bucket `zuno-phase22-corpus-evidence` removed after capture;
corpus test buckets removed by module teardown; the corpus facts (PG rows)
under `tenant_auroralis_verify` are the deliverable and remain for
verification. The CC-A preparation candidate facts under the official tenant
were left untouched.

## Tests Not Run

- ES/Milvus/Neo4j index visibility (GAP-B3 worker scope)
- Snapshot activation (GAP-B4 worker scope)
- Four-profile benchmark runtime (GAP-C worker scope)
- Fault matrix beyond ingestion resume (GAP-D worker scope)
- GitHub CI checks (no checks configured on this PR)
