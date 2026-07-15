# PHASE02 Temporary Compatibility and Cutover Control

phase_id: PHASE02
status: completed
depends_on: PHASE01
owner: Coordinator / Compatibility Governance

## Phase 目标

把所有旧 Agent、API、Store、Tool、Model、Retrieval、Frontend 和 Import 路径变成**临时迁移对象**：有版本、有 Feature Flag、有 Shadow/Canary、Rollback、Removal Gate 和静态 Guard。兼容层只允许存在于迁移窗口，最终代码树不保留 `legacy` 目录、`legacy_aliases.py`、永久双写或永久旧 Runtime。

## Minimal Read Set

- PHASE01 Work Products
- `.agent/programs/legacy-to-target-migration-map.md`
- 模块 01、06、08、11 文档
- 当前配置、兼容和旧入口代码

## Current Anchors

```text
src/backend/zuno/platform/compatibility/**
src/backend/zuno/api/services/completion.py
src/backend/zuno/api/services/workspace_task_runtime.py
src/backend/zuno/agent/runtime/**
src/backend/zuno/agent/durable_runtime.py
apps/web/src/**
apps/desktop/src/**
current feature flags and aliases
```

## Allowed Paths

```text
src/backend/zuno/platform/compatibility/**   # 仅迁移期
src/backend/zuno/platform/config/**
src/backend/zuno/api/compatibility/**       # 仅版本适配，不拥有事实
apps/web/src/compatibility/**                # 仅迁移期
apps/desktop/src/compatibility/**            # 仅迁移期
tools/scripts/*boundary*.*
tests/repo/**
.agent/programs/work-products/**
docs/evidence/**
```

## Forbidden Paths

- 在本 Phase 实现新领域模型或大规模迁移数据。
- 删除旧路径而没有新路径、Rollback 和证据。
- 让兼容层拥有领域状态、长期业务逻辑或永久目录地位。
- 新增任何没有 PHASE22 删除任务的兼容文件。

## Work Packages

### P02-T01 Public API Compatibility Matrix

- Goal：固定旧/新 API、DTO、SSE Event、Error、Cursor、Client Capability Version 的映射。
- Steps：为 endpoint/field/event 标记 keep/add/deprecate/version_adapter/remove；定义 Major/Minor 和 sunset。
- Output：`work-products/api-contract-compatibility-matrix.yaml`。
- Tests：现有 Web/Desktop 字段全部有策略；安全字段不得静默降级。
- Acceptance：外部必要兼容放 `api/product/v1|v2` 正常目录，不建 `legacy` API 目录。

### P02-T02 Feature Flag and Rollout State Machine

- Goal：建立 `DECLARED→SHADOW→CANARY→DEFAULT_NEW→ROLLBACK_WINDOW→RETIRED` Flag Registry。
- Required fields：owner、scope、default、metric、rollback_command、expires_at、retire_task。
- Tests：非法跳转、过期 Flag、无 Owner/回滚/删除任务被拒绝。
- Acceptance：Flag 只路由，不复制领域事实；PHASE22 前必须 RETIRED 并删除代码分支。

### P02-T03 Temporary Alias and Execution Allowlists

- Goal：为 Agent、Model、Tool、Retrieval、API、Import 旁路建立逐项临时 Allowlist。
- Steps：每条记录 path/symbol/reason/test/removal_task/deadline；新增旁路默认 CI Fail。
- Tests：静态 Guard 检测未登记 Provider SDK、Tool execute、旧 root import、跨 Owner DB write。
- Acceptance：Allowlist 只能减少；最终长度为零，Guard 从“登记旧路径”转为“禁止任何旧路径”。

### P02-T04 Data Migration and Dual-path Plan

- Goal：把每类数据映射到 `SCHEMA_EXPANDED→BACKFILLING→DUAL_READ→DUAL_WRITE(optional)→READ_CUTOVER→WRITE_CUTOVER→VERIFIED→LEGACY_REMOVED`。
- Required：source/target schema、transform、hash、backfill chunk、verification、rollback、retention。
- Output：`work-products/data-cutover-matrix.yaml`。
- Tests：每个 Target 对象有源数据或 greenfield 标记；不默认 Dual Write。
- Acceptance：最终只保留 Target Schema；旧表删除或归档由 Migration 完成，不保留 `legacy_*` 生产表。

### P02-T05 Rollback and Recovery Playbook

- Goal：为 Agent、Product API、Frontend、DB、Queue、Object、Model、Tool、Index 切流定义回滚。
- Required：trigger、max_window、data_reconcile、security_impact、operator_command、evidence。
- Tests：演练新 API 失败、Schema 回滚受限、Queue backlog、Tool UNKNOWN、Frontend rollout rollback。
- Acceptance：回滚不能恢复到绕过新 Security/Audit Gate 的旧路径；窗口结束即删除。

### P02-T06 Migration Guard Test Suite

- Goal：把 Matrix/Flag/Allowlist/Removal Gate 变成机器检查。
- Tests：模拟新增直接 SDK、旧 Import、无登记 Flag、永久 deprecated endpoint、`legacy/` 文件夹，验证 CI Fail。
- Acceptance：PHASE22 将 Guard 切换为生产根目录零 `legacy` 名称、零 alias registry、零旧主路径。

## Phase 完成定义

- 所有旧路径有临时迁移策略、Rollback、Deadline 和删除任务。
- API/Frontend/Data 兼容矩阵完整。
- 新旁路默认被 CI 阻止。
- 文档明确最终目录只保留 Canonical Target，不保留 Legacy 文件夹。

## Validation

```bash
git diff --check
python tools/scripts/verify_current_program.py
pytest -q tests/repo -k 'compatibility or boundary or current_program' -p no:cacheprovider
```
