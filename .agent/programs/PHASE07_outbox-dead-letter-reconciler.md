# PHASE07 Outbox / Dead Letter / Reconciler

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE07_outbox-dead-letter-reconciler
mode: tdd-implementation

## 目标

实现本地可测的 outbox、dead letter、worker lease / heartbeat 和 reconciler baseline，解决“DB 写了任务但队列消息丢失”“parse 成功但 index 缺失”“blocked 没有 diagnostics”等状态漂移问题。

## 范围

- OutboxEvent contract：event_id、topic、payload、status、attempt_count、last_error、created_at。
- Outbox dispatcher local runner：从 store 读取 pending outbox，投递 queue，成功标记 sent，失败保留 retry。
- DeadLetter record：message、reason、terminal / blocked、payload、source job。
- Reconciler checks：uploaded_without_parse、parse_succeeded_without_index、blocked_without_diagnostics、index_chunks_missing、citation_lineage_missing、object_missing。
- Worker lease / heartbeat baseline 可被 Redis state 或 store 记录。

## 禁止范围

- 不实现复杂 scheduler。
- 不要求真实 distributed lock。
- 不把 reconciler 自动修复所有问题作为本 phase 必需。
- 不删除人工 review / blocked evidence。

## 验收闸门

- focused test：outbox 先失败后重放成功，不丢事件。
- focused test：missing index_chunks 被 reconciler 报告。
- focused test：blocked_without_diagnostics 被报告。
- focused test：dead letter 可查询并保留 reason。
- worker lease / heartbeat 不破坏 retry。

## 验证命令

```powershell
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/storage/`
- `src/backend/zuno/knowledge/queue/`
- `src/backend/zuno/knowledge/workers/`
- `docs/architecture/document-ingestion-foundation.md`

## 需要修改的文件

- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/sqlmodel_models.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- 新增 `src/backend/zuno/knowledge/reconcile/`
- 更新 focused tests

## 执行拆解

1. 写 failing test：outbox dispatch retry。
2. 实现 OutboxEvent records 和 local dispatcher。
3. 写 failing test：missing chunks reconciler finding。
4. 实现 Reconciler。
5. 写 dead letter focused test。
6. 接入 queue / worker failure path。

## 多 agent 分工

- Reliability Agent：审 outbox / DLQ semantics。
- Storage Agent：审 store schema compatibility。
- Verification Agent：跑 reconciler tests。

## 需要返回的证据

- outbox event lifecycle 示例。
- reconciler findings 示例。
- dead letter record 示例。

## 停止条件

- 需要跨进程 scheduler 才能测试。
- Outbox 会造成重复 parse / index 且没有 idempotency key。
- Reconciler 自动修复可能破坏事实源。
