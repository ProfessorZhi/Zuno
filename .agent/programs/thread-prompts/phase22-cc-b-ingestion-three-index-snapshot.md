# PHASE22 CC-B Canonical Ingestion Three Index Snapshot

WORKER_TASK_ID: CC-B

## Recommended Provider / Model
DeepSeek；适合 Canonical Ingestion、MinIO/PostgreSQL 状态机、三索引 Visibility 和 Snapshot Activation 跨模块根因。

## Base SHA
origin/main `c9d099d64a1af28102231751ce55df8217173e89`；PR #106 head `95e17fc522591e7ee543b40b5b568d71963b6aa0`；PR #107 handoff source `6c9c75eaea16a047107e20fa156824bce068ee4c`。

## Goal
执行真实路径：Canonical Ingestion -> MinIO durable object -> PostgreSQL facts -> ES BM25 -> Milvus formal embedding -> Neo4j directed graph -> Visibility Receipts -> Snapshot Activation。

## Current Facts
source_count=8；document_count=8；chunk_count=24；entity_count=15；relation_count=5；index_job_count=3；visibility_receipt_refs=[]；knowledge_version_id=null；snapshot_id=null。

## Current Gap
只有 input/candidate manifests；无 live MinIO readback、PostgreSQL fact IDs、live ES/Milvus/Neo4j receipt 或 activated snapshot。

## Allowed Paths
`src/backend/zuno/knowledge/**`、`src/backend/zuno/platform/**`、`infra/docker/**`、`tests/knowledge/**`、`tests/integration/**`、`docs/evidence/**`。

## Forbidden Paths
不得整体复制历史 PR；不得手写 fake receipt/snapshot；不得用端口可达冒充 read/write verified；不得未经批准修改 migration；不得改状态机语义绕过失败。

## Canonical Owner
Input owner 负责 durable source facts；Knowledge owner 负责 Canonical IR、KnowledgeVersion、Index Job、Visibility Receipt 和 Snapshot Activation。

## Contracts
Receipt 必须来自正式 owner builder，并绑定 tenant/workspace/knowledge_version/snapshot scope/adapter execution/hash/observed_at。

## State Transitions
正常：`accepted -> object_staged -> object_committed -> canonical_ir_ready -> indexing -> indexes_visible -> snapshot_activated`。失败：`index_partially_failed`、`index_visibility_failed`、`snapshot_activation_blocked`。

## Failure Semantics
缺 Embedding Gateway/credential 必须 `credential_blocked`；Neo4j readback 不一致不得生成 receipt；未知副作用进入 `reconciliation_required`。

## Retry / Recovery / Idempotency
重复 ingest 不得重复创建 Source、KnowledgeVersion、Chunk、Node、Edge；必须复用事实或返回幂等结果。

## Security Requirements
使用独立 tenant/workspace/namespace；不得输出密码、token、API key 或敏感路径；跨 tenant/workspace 必须拒绝或隔离。

## Gold Isolation Requirements
不得把 expected answer、derivation spec 或 world model 传入 ingestion/index runtime。

## Required Tests
`git diff --check`
`python -m pytest -q tests/knowledge/test_canonical_ingestion_runtime.py tests/knowledge/test_index_jobs_runtime.py tests/integration/test_goal03_wave_a_external_index_adapters.py -p no:cacheprovider`

## Acceptance Criteria
MinIO readback、PostgreSQL facts、ES BM25、Milvus formal embedding ANN、Neo4j two-hop 均真实写读；三 receipt authentic；Snapshot 只在 receipt 完整时激活。

## Commit Contract
仅提交 CC-B 范围，message 前缀 `feat(phase22):`、`fix(phase22):` 或 `test(phase22):`；只提交 completion_candidate。

## Worker Result Schema
```yaml
worker_task_id: CC-B
status: completion_candidate | blocked
commit_sha: null
tests_run: []
tests_not_run: []
live_ids:
  knowledge_version_id: null
  snapshot_id: null
  visibility_receipt_refs: []
remaining_gaps: []
```

## Handoff Format
返回 exact commit SHA、命令、exit code、服务版本、真实 ID、cleanup、失败归因和未运行项。

## Stop Conditions
需要改跨模块 Contract、状态机、security policy、migration，或只能靠 fake receipt 通过时停止交回 Coordinator。
