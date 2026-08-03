# Goal05 PHASE22 Worker DeepSeek1 (CC-B1/B2) Canonical Ingestion + MinIO/PostgreSQL Facts

## Identity

- agent: claude-code
- provider: deepseek
- worker: DeepSeek1
- worker_task_id: PHASE22-CC-B1-B2
- branch: `claude/deepseek1-phase22-canonical-ingestion`
- base: `codex/phase22-real-synthetic-benchmark-readiness` @ `87f6eeed994d1db28f25ad916e052b3a3cd00992`
- scope: GAP-B1 Canonical Ingestion / GAP-B2 MinIO / PostgreSQL Facts
- run_at: 2026-08-03T21:30:00+08:00

## Status

```text
status: completion_candidate
scope: GAP-B1 (canonical ingestion runtime), GAP-B2 (MinIO/PostgreSQL facts)
forbidden states never written: indexes_visible, snapshot_activated
no fake IDs: every asserted ID is produced by the real pipeline
```

## Task 1 — Object Store Runtime Binding (solved, not deleted)

The four `*ObjectStore` classes are resolved into one formal ownership surface
(`src/backend/zuno/platform/storage/binding.py`):

| Role | Class | Deployment class | Authoritative |
| --- | --- | --- | --- |
| Port | `DurableObjectStore` (Protocol) | n/a (typed port) | no |
| Production adapter | `DurableMinioObjectStore` | SERVER_PRODUCT | **yes (sole owner)** |
| Physical transport | `MinioObjectStore` | SERVER_PRODUCT | no (owned by Durable) |
| Local adapter | `LocalObjectStore` | DEVELOPER_CI only | no |

Enforcement:

- `resolve_durable_minio_binding()` — single composition-root resolver; returns
  `None` (fail closed → API 503) when storage mode/credentials are absent.
- `require_durable_minio_binding()` — fail-fast variant for boot-time checks.
- `build_local_object_store(profile=...)` — rejects `server_product` with
  `ObjectStoreLocalAdapterForbidden`.
- `assert_binding_is_production_durable()` — the canonical runtime refuses any
  non-durable adapter at construction.
- `workspace_task_runtime.build_package_a_production_ingestion_runtime` now
  delegates to the binding module (signature and behavior preserved; the
  bootstrap test suite passes).

## Task 2 — Real Canonical Ingestion

New runtime `src/backend/zuno/knowledge/ingestion/canonical_runtime.py`
(`Phase22CanonicalIngestionRuntime`) drives the real path with real services:

```text
Source Upload -> Security/Classification -> Object Staged (MinIO, hash verified)
-> MinIO Object Commit (durable adapter + PostgreSQL object manifest)
-> PostgreSQL Source/Document/DocumentVersion facts
-> Canonical Document IR (real ParseGateway, fenced parse attempt/lease)
-> Chunk facts (knowledge_chunks) -> Entity/Directed Relation facts
   (deterministic extraction over the real graph handoff payload, committed as
   a hash-verified MinIO artifact) -> KnowledgeVersion fact
   (knowledge_domain_versions)
```

State machine is recorded as tenant-scoped, idempotent PostgreSQL domain state
events in `ingestion_outbox_events` (no migration required):

```text
accepted -> object_staged -> object_committed -> canonical_ir_ready
         -> knowledge_version_ready
failure: security_denied | credential_blocked | object_commit_failed
       | canonicalization_failed | reconciliation_required
```

Readback store `src/backend/zuno/knowledge/storage/canonical_facts.py` is
tenant-scoped; cross-tenant reads return no rows (`CanonicalFactsMissing`).

## Real IDs (live run, 2026-08-03)

```text
namespace bucket:              zuno-phase22-cc-b1b2-evidence
object_ref:                   s3://zuno-phase22-cc-b1b2-evidence/tenant-evidence-fecce25a/workspace-evidence-fecce25a/source/source-evidence-fecce25a/phase22-evidence.md
object_manifest_ref:          object-manifest:s3://zuno-phase22-cc-b1b2-evidence/.../phase22-evidence.md
object_manifest_hash:         abc2f2b81e09f6f2a1d01c54ea3a7f7a4ea0d6802e81d879d6a8f9c97bbbcd21
source_id:                    source-evidence-fecce25a
source_sha256:                abc2f2b81e09f6f2a1d01c54ea3a7f7a4ea0d6802e81d879d6a8f9c97bbbcd21
document_id:                  source-evidence-fecce25a
document_version_id:          document-version:source-evidence-fecce25a:1
parse_plan_id:                parse-plan:source-evidence-fecce25a:1
parse_job_id:                 parse-job:source-evidence-fecce25a:1
parse_snapshot_id:            parse-snapshot:source-evidence-fecce25a:1
canonical_ir_ref:             canonical-ir:parse-snapshot:source-evidence-fecce25a:1
knowledge_version_id:         knowledge-version:tenant-evidence-fecce25a:workspace-evidence-fecce25a:space-evidence-fecce25a:1
chunk_count:                  6
entity_count:                 17
relation_count:               12
graph_facts_object_ref:       s3://zuno-phase22-cc-b1b2-evidence/tenant-evidence-fecce25a/workspace-evidence-fecce25a/canonical-graph-facts/knowledge-version:tenant-evidence-fecce25a:workspace-evidence-fecce25a:space-evidence-fecce25a:1/graph-facts.json
graph_facts_manifest_hash:    de36f05f61b21d6f12fddcf947f30e597261c16664afd09187c9344b0c038ff2
postgresql_migration_head:    20260729_56
ledger_states:                accepted, object_staged, object_committed, canonical_ir_ready, knowledge_version_ready
knowledge_version_status:     BUILDING (index visibility is the downstream worker's scope)
```

Verification results (live):

| Check | Result |
| --- | --- |
| MinIO object write | PASS (real put_object + copy_object) |
| MinIO object readback | PASS (bytes == uploaded content) |
| Object hash agreement | PASS (readback sha256 == source_sha256 == manifest hash) |
| Object manifest row | PASS (owner `phase22.evidence`, visibility `visible`, hash match) |
| PostgreSQL facts queryable | PASS (source, document version, canonical IR, chunks, version) |
| Same source hash rerun idempotent | PASS (same knowledge_version_id, same chunk_ids, `idempotent=True`, no duplicate facts) |
| Cross tenant isolation | PASS (foreign tenant read raises `CanonicalFactsMissing`; ledger invisible) |
| Queue ACK != domain success | PASS (pending parse-request outbox never determines run state) |
| submitted != ingested | PASS (parse requested while run state is `canonicalization_failed`, no chunks) |
| UNKNOWN side effect | PASS (tampered object -> `reconciliation_required` / `object_bytes_mismatch`) |
| Credential missing | PASS (`credential_blocked` / `object_store_binding_missing`) |
| Object commit failure | PASS (fault injection -> `object_commit_failed` / `object_hash_mismatch`) |
| Security denied | PASS (`security_denied` / `classification_forbidden`) |

## Command Log

| command | exit_code | service_version |
| --- | --- | --- |
| `docker ps` (postgres 16, minio RELEASE.2023-03-20T20-16-18Z, rabbitmq 3.13) | 0 | PostgreSQL 16.14 / MinIO 2023-03-20 / RabbitMQ 3.13 |
| `python -m pytest -q tests/knowledge/test_canonical_ingestion_runtime.py tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider` | 0 | 51 passed |
| `python -m pytest -q tests/integration/test_phase22_canonical_ingestion_live.py -p no:cacheprovider` | 0 | 7 passed |
| `python -m pytest -q tests/api/test_workspace_package_a_production_bootstrap.py -p no:cacheprovider` | 0 | 2 passed |
| `python -m pytest -q tests/knowledge/ -p no:cacheprovider` | 1 | 249 passed, 16 failed (pre-existing, see below) |
| `git diff --check` | 0 | clean |
| live evidence pipeline script (IDs above) | 0 | — |

Namespace: bucket `zuno-phase22-cc-b1b2-evidence` created for the evidence run,
objects committed with hash-verified manifest, **cleanup: bucket removed after
evidence capture** (`remove_bucket_tree`). PostgreSQL facts for the evidence
tenant remain as domain rows (source/document/IR/chunk/version facts are the
deliverable).

## Pre-existing failures on the base branch (not caused by this worker)

1. `infra/db/alembic/env.py` imports `zuno.settings`, a compatibility shim
   deleted in commit `29a13df5` ("chore: close program3 backend root layout").
   Every `alembic upgrade head` invocation fails with
   `ModuleNotFoundError: No module named 'zuno.settings'`. This breaks
   `tests/integration/test_phase11_package_a_production_runtime.py` (19 tests)
   at setup. Verified identical on the clean base (stash test). `infra/db/**`
   is outside this worker's allowed paths — reported to coordinator, do not
   fix here.
2. `tests/knowledge/test_corrective_retrieval_runtime.py` — 16 failures
   (`document_version_id is required` from `indexing/contracts.py`).
   Verified identical on the clean base (stash test). Not in worker scope.

## STOP / report items (worker boundary)

- **Entity/Relation PostgreSQL domain tables do not exist.** Chunk facts have a
  real table (`knowledge_chunks`); entity/relation facts are persisted as a
  hash-verified MinIO artifact (object write + readback + manifest + event
  record). Promoting them to first-class PostgreSQL facts requires a new
  reversible alembic migration (`knowledge_entities` / `knowledge_relations`),
  which is outside this worker's allowed paths. **Coordinator approval
  required** before a migration is created.
- Canonical run ledger uses the existing `ingestion_outbox_events` table via
  idempotent domain state events — no schema change, no migration needed.

## Changed Files

```text
src/backend/zuno/platform/storage/binding.py                  (new, Task 1)
src/backend/zuno/platform/storage/__init__.py                 (exports)
src/backend/zuno/api/services/workspace_task_runtime.py       (composition root delegates to binding)
src/backend/zuno/knowledge/ingestion/canonical_runtime.py     (new, Task 2)
src/backend/zuno/knowledge/storage/canonical_facts.py         (new, readback store)
tests/knowledge/test_canonical_ingestion_runtime.py           (new, 26 tests)
tests/integration/test_phase22_canonical_ingestion_live.py    (new, 7 tests)
docs/evidence/goal05-phase22-machine-attested-synthetic-regression/deepseek1-cc-b12/evidence.md
```

## Not Touched (worker boundary)

Elasticsearch / Milvus / Neo4j adapter files, snapshot activation files,
`tools/evals/zuno/**`, `tests/evals/**`, MiniMax worker directories, PHASE22
completed status, production readiness, alembic migrations, `infra/db/**`.
