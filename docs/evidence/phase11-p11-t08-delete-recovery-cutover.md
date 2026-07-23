---
phase: PHASE11
scope: P11-T08
status: completion_candidate
date: 2026-07-23
branch: integration/goal02-agent-core-ingestion-closure
---

# PHASE11 P11-T08 Delete / Recovery / Legacy Cutover Evidence

## 结论

P11-T08 当前达到 `completion_candidate`：Delete / Restore lifecycle 已覆盖 visibility revoke、projection cleanup request、physical delete、verification、legal hold、restore、delete during parse、late worker result reject，并新增 PostgreSQL 审计事实表。

本文件不单独关闭 PHASE11。完整 Phase Closure 仍需要 P11-T01～T08 证据汇总、完整 E2E / Fault 验证和 Coordinator Closure。

## 本轮实际变更

- 新增 PostgreSQL 表 `ingestion_delete_lifecycles`。
- 新增 `IngestionRepository.record_delete_lifecycle()` 与 `get_delete_lifecycle()`。
- `ingestion_delete_lifecycles` 保存：
  - `snapshot_ref` / `visibility_ref`
  - `indexable_snapshot_id` / `handoff_outbox_event_id`
  - parse 中删除所需的 `parse_job_id` / `parse_attempt_id` / `fencing_token`
  - `cleanup_ref` / `projection_cleanup_ref` / `physical_delete_ref` / `verification_ref`
  - `legal_hold_ref`
  - cleanup / physical delete verification flags
  - late worker reject / restore authorization flags
  - receipt hash 与 history

## 验收边界

- `verified` 状态必须同时具备 cleanup 与 physical delete verification。
- legal hold 存在时不得有 physical delete ref。
- restore 不恢复授权，`restored_authorization` 必须保持 false，后续授权必须重新决策。
- Input 删除流程只产出 lifecycle / cleanup / handoff 事实，不直接删除 Knowledge Index 内部结构。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge/test_ingestion_delete_restore.py tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider --tb=short
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
pytest -q tests/repo/test_phase11_legacy_upload_parser_cutover.py tests/knowledge/test_legacy_cutover_adapter.py tests/storage/test_pipeline.py -p no:cacheprovider --tb=short
alembic -c infra/db/alembic.ini heads
alembic -c infra/db/alembic.ini upgrade head
```

## 验证结果

- `git diff --check`：通过。
- Delete / restore + PostgreSQL persistence：`14 passed in 16.19s`。
- Legacy upload/parser cutover verifier：通过。
- Legacy cutover test bundle：`11 passed in 34.68s`。
- Alembic head：`20260724_25 (head)`。
- Alembic upgrade：通过。

## 剩余边界

- 本证据不声明旧 `ChunkModel` 类型从全仓库删除；它仍可存在于兼容 DTO、历史服务或 legacy adapter 内。
- 本证据声明的是生产默认 ingestion 路径不再依赖旧 parser/upload 直写路径。
