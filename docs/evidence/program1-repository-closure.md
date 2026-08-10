# Program1 Repository Closure Follow-up

状态：`completed`

日期：2026-08-10

本证据记录 `PROGRAM01_real-unified-runtime-cutover.md` 作为 queued candidate 的第一阶段 repository closure follow-up。它没有激活完整七阶段 Program，也不代表 benchmark、quality 或 production readiness 已通过。

## 已关闭的仓库阻塞项

1. Product artifact / feedback 现在由 `ProductArtifactService` 通过现有 `SQLiteDurableIngestionStore` 读写 durable ingestion contracts。Product API 不再导入或调用 `WorkspaceTaskRuntimeService`；store 未绑定时返回 `503 PRODUCT_ARTIFACT_OWNER_NOT_BOUND`，不回退到进程内字典。未新增数据库迁移。
2. `/completion` 的 `shadow / canary / new_default` 分别使用 `SHADOW_SUBMIT_USER_GOAL`、`CANARY_SUBMIT_USER_GOAL`、`SUBMIT_USER_GOAL`。Product persistence 失败时所有模式都只输出 blocked Product record，不启动 Unified Agent Runtime。
3. Current / Target / History 边界已同步：Program1 仍是 queued candidate；root README、Current Program、Project Map、workflow、Production Readiness 和旧 evidence 不再把旧事实写成当前事实。

## 可复现验证

- `python -m pytest -q tests/api/test_completion_unified_runtime.py tests/api/test_goal03_product_route.py tests/api/test_product_artifact_service.py -p no:cacheprovider`：`33 passed`。
- `python -m pytest -q tests/repo/test_phase22_feature_flag_runtime_cutover.py -p no:cacheprovider`：`59 passed`。
- `python tools/scripts/verify_phase22_feature_flag_runtime_cutover.py`：`FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED`。
- `python tools/scripts/verify_phase22_final_legacy_cutover.py --json`：应为 `LEGACY_CUTOVER_AUDIT_CLEAN`；该 verifier 的排除范围和未证明边界仍以 JSON 为准。

## 保留边界

- Fixed Benchmark 仍是 `blocked_external / blocked_not_measured`，quality 仍是 `not_yet_proven`，production readiness 仍是 `NOT_ESTABLISHED`。
- `WorkspaceTaskRuntimeService` 继续作为 `/workspace/task*` 的 bounded compatibility facade；它不是 Product artifact / feedback 的 owner。
- Product durable store 需要由应用组合根或测试显式绑定；未绑定是 fail-closed，而不是成功状态。
