---
phase: PHASE11
scope: P11-T08
status: completion_candidate
date: 2026-07-24
branch: integration/goal02-final-closure-repair
commit: 18a66c7868cd6ff28e8104398400eec22c99d332
---

# PHASE11 P11-T08 Delete / Recovery / Legacy Cutover Evidence

## 结论

P11-T08 当前达到 `completion_candidate`：Delete / Restore lifecycle 已从只表达状态的 receipt，补齐为显式 Port 驱动的外部链路。当前实现覆盖 visibility revoke、transactional cleanup outbox、RabbitMQ cleanup contract publish / ACK / crash replay / DLQ replay、Knowledge cleanup confirmation、MinIO physical delete、absence verification、legal hold、restore fresh authorization、duplicate restore、revoked authorization、object already missing、late worker reject 和 restart reconciliation。

本文件不单独关闭 PHASE11。完整 Phase Closure 仍需要 P11-T01～T08 证据汇总、完整 E2E / Fault 验证和 Coordinator Closure。

## 本轮实际变更

- PostgreSQL 表 `ingestion_delete_lifecycles` 保存：
  - `snapshot_ref` / `visibility_ref`
  - `indexable_snapshot_id` / `handoff_outbox_event_id`
  - parse 中删除所需的 `parse_job_id` / `parse_attempt_id` / `fencing_token`
  - `cleanup_ref` / `projection_cleanup_ref` / `physical_delete_ref` / `verification_ref`
  - `legal_hold_ref`
  - cleanup / physical delete verification flags
  - late worker reject / restore authorization flags
  - receipt hash 与 history
- `PersistentDeleteRestoreCoordinator` 当前通过明确端口推进状态转换：
  - `VisibilityRevocationPort`
  - `KnowledgeCleanupPort`
  - `ObjectDeletePort`
  - `ObjectVerificationPort`
  - `RestoreAuthorizationPort`
  - `AuditPort`
- Delete request 在同一 PostgreSQL UoW 内写入 lifecycle 与 cleanup outbox；RabbitMQ ACK 只证明 cleanup contract 已送达，不代替 Knowledge cleanup confirmation。
- 重复 Delete request 在 coordinator 层读取已有 PostgreSQL lifecycle，并复用同一个 cleanup outbox；相同 `delete_ref` 但 payload 不同会 fail closed 为冲突。
- `execute_cleanup()` 先要求 Knowledge cleanup confirmation，再执行 MinIO object delete，随后做 absence verification；MinIO delete API 返回不代替领域 verified。
- MinIO object manifest 只在真实对象删除成功或对象已缺失可重建为 deleted 时更新，避免对象删除失败却把 manifest 标为 deleted。
- restore 必须经过 fresh authorization；重复相同授权引用返回幂等结果，撤销授权或不同授权引用会 fail closed。
- late worker result reject 通过 PostgreSQL lifecycle reconciliation 持久化，不依赖进程内状态。

## 验收边界

- `verified` 状态必须同时具备 cleanup 与 physical delete verification。
- legal hold 存在时不得有 physical delete ref。
- restore 不自动恢复旧权限；`restored_authorization` 只表示本次 restore 已通过新的授权端口。
- Input 删除流程只发布 cleanup contract，不直接修改 Knowledge Index 内部结构。
- cleanup publish crash 和 DLQ replay 不得恢复已撤销数据；缺少 Knowledge cleanup confirmation 时不得进入 physical delete。
- MinIO delete 成功但领域事务提交失败时，restart reconciliation 必须把 object absence 与 lifecycle 对齐。
- 同一 delete command replay 不得产生第二个 lifecycle 或第二个 cleanup outbox；不同 payload 不得覆盖已有 lifecycle。

## 验证命令

```powershell
git diff --check
pytest -q tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider --tb=short
pytest -q tests/knowledge/test_ingestion_delete_restore.py -p no:cacheprovider --tb=short
pytest -q tests/integration/test_phase04_minio_object_store.py -p no:cacheprovider --tb=short
alembic -c infra/db/alembic.ini heads
alembic -c infra/db/alembic.ini upgrade head
```

## 验证结果

- `git diff --check`：通过。
- PHASE11 persistence runtime：`20 passed in 25.23s`。
- Delete coordinator idempotency focused regression：`tests/integration/test_phase11_ingestion_persistence_runtime.py::test_ingestion_duplicate_delete_after_snapshot_reuses_lifecycle_and_cleanup_outbox` 为 `1 passed in 10.13s`。
- Delete / restore unit contract：`7 passed in 8.38s`。
- PHASE04 MinIO object store regression：`3 passed in 2.17s`。
- Alembic head：`20260724_31 (head)`。
- Alembic upgrade：未在本次证据补写中重跑；最新已确认 single head 为 `20260724_31 (head)`。

## 剩余边界

- 本证据不声明旧 `ChunkModel` 类型从全仓库删除；它仍可存在于兼容 DTO、历史服务或 legacy adapter 内。
- 本证据声明的是生产默认 ingestion 路径不再依赖旧 parser/upload 直写路径。
- 本证据仍只是 P11-T08 的 `completion_candidate`。PHASE11 Coordinator Closure 仍为 `pending`，PR #41 不得合并。
