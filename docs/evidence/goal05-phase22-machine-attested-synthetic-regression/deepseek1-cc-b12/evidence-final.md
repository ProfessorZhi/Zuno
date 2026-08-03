# Goal05 PHASE22 Worker DeepSeek1 (CC-B1/B2) Final Evidence — State/Hash/Scope

## Identity

- agent: claude-code
- provider: deepseek
- worker: DeepSeek1
- worker_task_id: PHASE22-CC-B1-B2-STATE-HASH-SCOPE-FINAL
- branch: `claude/deepseek1-phase22-canonical-ingestion`
- pr: https://github.com/ProfessorZhi/Zuno/pull/112
- run_at: 2026-08-04T00:45:00+08:00
- model: deepseek-v4-flash (session)
- cost: NOT_AVAILABLE / NOT_AVAILABLE

## Status

```text
status: CC_B1_B2_COMPLETION_CANDIDATE
no fake IDs; no Snapshot activation; no three-index visibility; no PHASE22
completion; no production readiness; no CI-passed claim
```

## Three Frozen Hashes (non-interchangeable, never aliased)

```text
dataset_corpus_hash:  749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4
                      (candidate_dataset_manifest.json corpus_hash)
source_manifest_hash: 0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a
                      (source_upload_manifest.json)
canonical_ir_hash:    43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6
                      (canonical_ir_manifest.json)
```

The KnowledgeVersion index_spec freezes all three plus `document_set_hash`,
`chunk_set_hash` and `security_epoch_ref`. Hash contract tests cover positive,
aliased, missing and cross-manifest-mismatch cases (fail closed). The IR
manifest must reference the same source manifest.

## Formal Scope (restored, never changed by verification)

```text
tenant_id   = tenant_auroralis
workspace_id = workspace_regression
knowledge_space_id = space::tenant_auroralis::workspace_regression::phase22-synthetic
```

Every fact (run row, source, document version, parse snapshot, KnowledgeVersion,
chunks, entities, relations, security decisions) uses the formal scope. A
`verify_scope_consistency()` verifier checks all facts of each run; a mixed
scope test proves foreign tenant/workspace access yields nothing or raises.

**Isolation method:** dedicated scratch PostgreSQL database (separate database
name, created + `alembic upgrade head` + dropped by the corpus suite). The
shared development database is never touched by the corpus verification; the
CC-A preparation candidate facts under the official tenant were left intact
and were not part of the evidence run.

## State Transition Matrix (declared == executed)

```text
accepted                 -> object_staged | security_denied | credential_blocked | object_stage_failed
object_staged            -> object_committed | object_commit_failed | reconciliation_required
object_committed         -> canonical_ir_ready | canonicalization_failed | reconciliation_required
canonical_ir_ready       -> knowledge_version_ready | reconciliation_required
knowledge_version_ready -> reconciliation_required (designed reconciliation edge only)
retry: object_stage_failed -> object_staged
       object_commit_failed -> object_committed
       canonicalization_failed -> object_committed (re-parse)
reconciliation resume:   reconciliation_required -> object_staged | object_committed | canonical_ir_ready
                        (recovery point must be verified against durable facts)
```

Stage failure records `object_stage_failed`; commit failure records
`object_commit_failed` (from `object_staged`); both persist without re-raising
illegal transitions; explicit retries produce new versioned audit events.

## Accepted Initial Facts — Atomic (Task D)

`ensure_run` writes, in ONE transaction: the `canonical_ingestion_runs`
current fact (state `accepted`, state_version 1, attempt 1), the
`canonical_ingestion_run_history` accepted event, and the
`ingestion_outbox_events` accepted event. Tests prove: the returned
outbox_event_id is the persisted one; duplicate `ensure_run` creates no
duplicate history/outbox; a failing insert (CHECK violation) rolls back all
three.

## Outbox Event Identity (Task E)

`canonical_state_event_id(run_id, state_version, attempt_number, to_state)` —
each real transition has a unique audit event; retry and reconciliation
resume advance state_version/attempt_number and produce new events; replay of
the identical transition stays idempotent; history and outbox are one-to-one
(same event ids, same count: 40 = 40 for the corpus run). No timestamps are
used as idempotency basis.

## Outbox Payload Hash (Task F)

`effective_payload = outbox_payload or default_state_payload`;
`payload_hash = canonical_sha256(effective_payload)` — the stored payload and
payload_hash always match (test-verified for default and custom payloads;
tampering the payload breaks the hash check). History payload hash owns the
transition-fact payload; outbox payload hash owns the effective delivery
payload.

## Terminal / Reconciliation Semantics (Task G)

`knowledge_version_ready` leaves only through the explicit `reconcile()`
path with a concrete failure_code (`object_bytes_mismatch`,
`object_manifest_missing`, ...). `resume_after_reconcile()` verifies the
recovery point against durable facts: `object_committed` requires a visible
manifest AND matching physical readback; `canonical_ir_ready` requires the
parse snapshot; `object_staged` requires the physical object. Wrong recovery
points are rejected (tested).

## Official Corpus Live Run (formal scope, scratch DB)

```text
reconciled:            True
counts:                8 sources / 8 documents / 24 chunks / 15 entities / 5 directed relations
knowledge_version_id:  knowledge-version:tenant_auroralis:workspace_regression:space::tenant_auroralis::workspace_regression::phase22-synthetic:1
document_set_hash:     18fd8a5704723b3c3410901bf565b7273d98ed1e2f9add43f97cc869e7e6ee39
chunk_set_hash:        9c3b4ee28023e88e48e78e9fb290a8c5e771cae42bc287c295e0154a2feb7887
security_epoch_ref:    security-epoch:tenant_auroralis:phase22-corpus
state_history_count:   40 (5 events x 8 runs)
outbox_event_count:    40 (1:1 with history)
retry/reconciliation event count: 0 (clean run; retry/reconcile event
                         identity covered by fault tests)
migration_head:        20260803_58 (single head; fresh-DB upgrade/downgrade/
                         re-upgrade proven by bootstrap suite)
scope consistency:     verified for all 8 runs
```

8 security decision refs and 8 MinIO object refs (bucket
`zuno-phase22-final-evidence`, per-source keys under
`tenant_auroralis/workspace_regression/source/...`) — full lists in the live
command log below.

## Command Log

| command | exit_code | notes |
| --- | --- | --- |
| `alembic -c infra/db/alembic.ini heads` | 0 | single head `20260803_58` |
| `alembic -c infra/db/alembic.ini upgrade head` / `current` | 0 | head applied |
| fresh DB: upgrade head -> downgrade base -> upgrade head | 0 | bootstrap suite |
| `python -m pytest -q tests/knowledge/test_canonical_ingestion_runtime.py tests/knowledge/test_index_jobs_runtime.py tests/integration/test_phase22_canonical_ingestion_live.py tests/integration/test_phase22_official_corpus_live.py tests/integration/test_phase22_clean_db_bootstrap.py -p no:cacheprovider` | 0 | 74 passed |
| final live evidence run (IDs above) | 0 | formal scope, scratch DB |
| `git diff --check` | 0 | clean |

Services: PostgreSQL 16.14, MinIO RELEASE.2023-03-20T20-16-18Z, RabbitMQ
3.13 (docker compose).

Cleanup: scratch evidence database dropped, evidence bucket
`zuno-phase22-final-evidence` removed, temp config removed; corpus suite
drops its scratch database and bucket at teardown; shared development
database untouched.

## Tests Not Run

- ES/Milvus/Neo4j index visibility (GAP-B3), snapshot activation (GAP-B4),
  four-profile runtime (GAP-C), broader fault/security matrix (GAP-D)
- GitHub CI checks (none configured on this PR)
- pre-existing base failure `test_corrective_retrieval_runtime.py` unchanged
