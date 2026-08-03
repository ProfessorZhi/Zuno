# CC-B PHASE22 Canonical Ingestion / Object / PostgreSQL / Three Indexes

WORKER_TASK_ID: CC-B-PHASE22-CANONICAL-INGESTION-THREE-INDEXES
Base SHA: 95e17fc522591e7ee543b40b5b568d71963b6aa0

## Goal

让完整 Synthetic Corpus 走正式 Source Upload 到 Snapshot Activation 路径，并真实写入 MinIO、PostgreSQL、Elasticsearch、Milvus、Neo4j。

## Current Gap

PR #105 有候选 `CanonicalIngestionSliceRuntime`，但已关闭未合并，且没有 Current 证明完整 Corpus、三索引、Visibility Receipt 和 Snapshot Activation。

## Allowed Paths

- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/platform/database/**`
- `infra/db/alembic/**`
- `tools/evals/zuno/synthetic_benchmark/**`
- `tests/knowledge/**`
- `tests/integration/**`
- `docs/evidence/goal05-phase22-machine-attested-synthetic-regression/**`

## Forbidden Paths

- 不整体合并 PR #105。
- 不绕过 Security、Object Store、Repository/UoW、Index Job、Visibility Receipt 或 Snapshot Activation。
- 不用 Queue ACK 冒充领域成功。
- 不用端口可达冒充 Index Ready。
- 不在 Benchmark Harness 手写 Receipt。

## Contracts

状态机必须覆盖：`accepted`、`object_staged`、`object_committed`、`canonical_ir_ready`、`indexing`、`indexes_visible`、`snapshot_activated`。

失败状态必须覆盖：`security_denied`、`credential_blocked`、`object_commit_failed`、`canonicalization_failed`、`index_partially_failed`、`index_visibility_failed`、`snapshot_activation_blocked`、`reconciliation_required`。

## Owner

Knowledge Ingestion Runtime owns ingestion facts；Object Store owns object receipt；Index adapters own visibility receipt；Snapshot Runtime owns activation.

## State Transitions

完整路径：`Source Upload -> Security / Classification -> Durable Object Store -> PostgreSQL Ingestion Facts -> Canonical Document IR -> Chunk / Entity / Directed Relation -> KnowledgeVersion -> Index Jobs -> Index Visibility -> Snapshot Activation`

## Failure Semantics

三索引任一不可见不得激活 Snapshot；UNKNOWN side effect 进入 `reconciliation_required`；缺 credential 进入 `credential_blocked`。

## Retry / Recovery / Idempotency

相同 source hash 重跑不得重复 Source、Document、KnowledgeVersion、Chunk、Entity、Relation、Index 文档；重复消息必须 idempotent。

## Security

Tenant/Workspace 必须隔离；越权必须拒绝或隔离；Security Epoch 过期必须 fail-closed。

## Required Tests

```powershell
python -m pytest -q tests/knowledge/test_canonical_ingestion_runtime.py -p no:cacheprovider
python -m pytest -q tests/integration -k "canonical_ingestion or external_index or snapshot" -p no:cacheprovider
```

## Acceptance Criteria

真实记录 `source_id`、`object_ref`、`object_manifest_ref`、`document_id`、`document_version_id`、`chunk_ids`、`entity_ids`、`relation_ids`、`knowledge_version_id`、`index_job_ids`、`visibility_receipt_refs`、`snapshot_id`。

## Commit Contract

普通 commit，禁止 amend/force-push；提交信息包含 `[worker=CC-B]`。

## Handoff Format

提交 `git show <WORKER_SHA>` 摘要、allowed path 清单、真实 ID 摘要、cleanup 记录、验证命令和 exit code。
