# PHASE01 Persistence and Infrastructure Inventory Evidence

task_id: P01-T02
phase_id: PHASE01
branch: codex/P01-T02-persistence-infrastructure-inventory
requested_start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
actual_start_commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
evidence_status: completion_candidate

## Objective

重新审计 Persistence and Infrastructure Current，并补齐 `.agent/programs/work-products/current-persistence-inventory.md`。本证据只证明 PHASE01 inventory 已按代码、测试、环境和已存在 evidence 重新归档，不证明任何新的 Runtime 能力已经实现。

## Environment

| item | value |
| --- | --- |
| OS shell | Windows PowerShell |
| workspace | `C:\Users\Administrator\.codex\worktrees\2987\Zuno` |
| branch | `codex/P01-T02-persistence-infrastructure-inventory` |
| audit baseline commit | `688a50fa5730f8815b2f09050f01eeb42633ae1d` |
| current date | 2026-07-16 |
| Python / package versions | captured by validation command runtime; no dependency upgrade performed |
| real dependency services | not started by P01-T02 |

## Commands And Results

| command | result |
| --- | --- |
| `git status --short --branch` | clean at task start on detached HEAD; branch then created as `codex/P01-T02-persistence-infrastructure-inventory` |
| `git rev-parse HEAD` | `688a50fa5730f8815b2f09050f01eeb42633ae1d` |
| `rg -n "SQLiteDurableIngestionStore\|SQLModel\|create_engine\|alembic\|RabbitMQQueueBackend\|QueueClient\|MinioClient\|RedisClient\|RuntimeGraphCheckpointer\|SQLiteAgentRunStore\|LocalObjectStore\|LocalQueueBackend\|KnowledgeIndexRuntime\|milvus\|neo4j\|elasticsearch\|backup\|restore\|PITR\|docker-compose\|postgres\|rabbitmq\|minio\|redis" src infra tests tools docs/evidence .agent/programs -S` | completed; used to identify code, tests, existing evidence and target-only declarations |
| `Get-Content` reads for PHASE01 prompt, AGENTS, current Program, task contract, PHASE01 file, Infrastructure module, ADR 0003, registry, existing inventory, verifier and tests | completed; used as fact sources |

Final validation commands are recorded in the completion report after edits. Any failures are reported with their exact command result.

## Final Validation Results

| command | result |
| --- | --- |
| `git diff --check` | passed; only line-ending warnings for touched text files |
| `python tools/scripts/verify_current_program.py` | passed: `Current program verification passed.` |
| `python .agent/scripts/verify_agent_system.py` | passed: `agent system verification passed.` |
| `python tools/scripts/verify_phase01_complete_baseline.py` | failed as expected for Phase-level residuals outside P01-T02: stale P01-T01/P01-T04/P01-T05 baselines, missing P01-T01 dynamic-entry coverage, missing P01-T04 Browser E2E, missing P01-T05 deadline, incomplete requirement ledger reviewer/reverse trace/test/evidence fields, P01-T01..T06 not completed, Coordinator approval pending, PHASE02 gate closed, risk register P0 proof incomplete |
| `pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider` | passed: `11 passed` |

## Sampled Code Evidence

| capability | sampled code | sampled tests/evidence | conclusion |
| --- | --- | --- | --- |
| SQLite durable ingestion store | `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`; `src/backend/zuno/knowledge/storage/sqlmodel_models.py` | `tests/knowledge/test_enterprise_ingestion_storage_contract.py`; `tests/api/test_workspace_durable_ingest_runtime.py`; `tests/storage/test_database_schema.py` | `implementation available` for Developer / CI local baseline |
| SQLite agent runtime store | `src/backend/zuno/agent/runtime/sqlite_store.py`; `src/backend/zuno/agent/runtime/checkpointer.py` | `tests/agent/runtime/test_runtime_store.py`; `tests/api/test_workspace_runtime_recovery.py`; `tests/agent/runtime/test_runtime_restart_persistence.py` | `implementation available` locally; official PostgreSQL Checkpointer remains `target_not_current` |
| Local object and queue | `src/backend/zuno/knowledge/storage/local_object_store.py`; `src/backend/zuno/knowledge/ingestion/async_runtime.py` | `tests/knowledge/test_ingestion_async_infrastructure.py`; `tests/api/test_workspace_durable_ingest_runtime.py` | local object/queue/worker baseline only |
| PostgreSQL primitive | `src/backend/zuno/platform/database/foundation.py`; `infra/db/alembic/versions/20260715_04_infrastructure_foundation.py` | `tests/integration/test_phase04_postgres_foundation.py`; `docs/evidence/phase04-postgres-foundation.md` | `partial implementation available`; not full Server Product Current |
| RabbitMQ target | `src/backend/zuno/platform/services/queue/client.py`; `src/backend/zuno/knowledge/ingestion/async_runtime.py` `RabbitMQQueueBackend` | no real broker integration/fault evidence found | `target_not_current` |
| MinIO/S3 target | `src/backend/zuno/platform/services/storage/minio.py`; `infra/docker/docker-compose.yml` | no bucket/lifecycle/restore integration evidence found | `target_not_current` |
| Redis target | `src/backend/zuno/platform/services/redis.py`; `RedisRuntimeStateBoundary` | no Redis integration/fault evidence found | `target_not_current` |
| Milvus / Neo4j / Elasticsearch target | `src/backend/zuno/platform/services/memory/vector_stores/milvus.py`; `src/backend/zuno/platform/services/graphrag/client.py`; `infra/docker/docker-compose.yml` | no real index publish/visibility/delete/rebuild evidence found | `target_not_current` |
| Backup / Restore / PITR | Docker volumes and PHASE04 readiness references | no backup artifact, restore rehearsal or PITR evidence found | `target_not_current` |
| Secret delivery | config example fields and settings loader | no SecretLease/rotation/revocation evidence found | `needs_evidence` |

## Artifact Hash

Primary artifact hash:

```powershell
Get-FileHash .agent/programs/work-products/current-persistence-inventory.md -Algorithm SHA256
```

```text
5B439BF070A8654D6DCD7F1389409A2F2821957D12263EDCF44D17E525799A95
```

The evidence file, verifier and tests are fixed by the final git commit. The evidence file does not embed its own hash to avoid a self-referential artifact.

## Not-Run Real Dependency Checks

The following checks were intentionally not run in P01-T02 because this work package is a Current inventory task and must not fabricate real dependency evidence:

| dependency | not-run check | status |
| --- | --- | --- |
| PostgreSQL full domain Current | default Product/Agent/Knowledge/Memory paths writing PostgreSQL under failures | `needs_evidence` |
| RabbitMQ | ACK/redelivery/DLQ/replay/partition/duplicate delivery integration | `target_not_current` |
| MinIO/S3 | staging, commit, visibility, authorization, lifecycle, delete and restore integration | `target_not_current` |
| Redis | connection, eviction, failover and non-authoritative cache recovery | `target_not_current` |
| Milvus | collection write, visibility, deletion, rebuild and cutover | `target_not_current` |
| Neo4j | graph write, constraint, visibility, deletion, rebuild and cutover | `target_not_current` |
| Elasticsearch | index write, analyzer/mapping version, visibility, deletion and rebuild | `target_not_current` |
| LangGraph PostgreSQL Checkpointer | official saver interrupt/resume/thread isolation/generation reconcile | `target_not_current` |
| Backup / Restore / PITR | isolated restore, recovery set validation and cutover | `target_not_current` |
| Secret / KMS | SecretLease, rotation, revocation and redaction proof | `needs_evidence` |

## Current / Gap / Plan Summary

Current:
- Local Developer / CI persistence and infrastructure baseline is executable for SQLite, local object store, local queue, local index and local checkpoint bridge.
- PostgreSQL / Alembic infrastructure foundation has partial real integration evidence from PHASE04.

Gap:
- Canonical Server Product Target remains incomplete for RabbitMQ, MinIO/S3, Redis, external indexes, official Checkpointer, Backup/Restore/PITR, Secret Lease, object lifecycle, full CI real dependency matrix and combined recovery.

Plan:
- PHASE04 and later infrastructure work packages must turn target-only surfaces into Current using real integration/fault/recovery evidence.
- Coordinator must review P01-T02 before marking it completed; this Implementer only submits a `completion_candidate`.
