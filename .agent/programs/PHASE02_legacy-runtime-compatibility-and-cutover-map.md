# PHASE02 Temporary Compatibility and Cutover Control

phase_id: PHASE02
status: ready
depends_on: PHASE01
owner: Coordinator / Compatibility Governance

## 订正说明

2026-07-16 撤回此前 `completed` 结论。已有 API Matrix、Feature Flag Registry、Allowlist、Data Cutover Matrix 和 Rollback Playbook 只证明迁移设计存在，没有证明真实 Runtime 已受控、Rollback 已演练、旁路已被机器阻断或 Allowlist 已开始收缩。

本 Phase 不再以 YAML/Markdown 和静态清单作为完成标准。必须把兼容、Flag、Cutover、Rollback、Guard 和 Removal Gate 实现为可执行控制面，并让所有当前旧入口进入受控状态。

## Phase 目标

把所有旧 Agent、API、Store、Tool、Model、Retrieval、Frontend、Desktop 和 Import 路径变成有期限、可观测、可回滚、可删除的迁移对象。每个旧路径必须满足以下之一：

```text
routed through versioned compatibility adapter
or disabled by default with explicit rollback-only access
or removed after verified cutover
```

兼容层只能路由和转换，不能拥有领域事实、复制状态机或绕过 Security、Audit、Budget、Approval、Idempotency、Final Gate 和 RunOutcome。

## Minimal Read Set

- 完整 PHASE01 Work Products 和 Evidence
- `.agent/programs/legacy-to-target-migration-map.md`
- `.agent/programs/canonical-directory-contract.md`
- 模块 01、04、06、07、08、09、10、11 文档
- 当前 API、Runtime、Frontend/Desktop、Provider/Tool/Model factories、配置和兼容代码

## Current Anchors

```text
src/backend/zuno/platform/compatibility/**
src/backend/zuno/api/services/completion.py
src/backend/zuno/api/services/workspace_task_runtime.py
src/backend/zuno/agent/**
src/backend/zuno/knowledge/**
src/backend/zuno/memory/**
src/backend/zuno/capability/**
src/backend/zuno/platform/**
apps/web/src/**
apps/desktop/**
all feature flags, aliases, registries, factories and dynamic imports
```

## Allowed Paths

```text
src/backend/zuno/platform/compatibility/**       # only during migration window
src/backend/zuno/platform/config/**
src/backend/zuno/api/compatibility/**            # version adapter only, no facts
apps/web/src/compatibility/**                     # only during migration window
apps/desktop/src/compatibility/**                 # only during migration window
tools/scripts/*boundary*.*
tools/scripts/*cutover*.*
tests/repo/**
tests/integration/**
tests/fault/**
.agent/programs/work-products/**
docs/evidence/**
```

## Forbidden Paths

- 让兼容层拥有领域状态、长期业务逻辑或第二套 Controller。
- 新增没有 Owner、Deadline、Rollback、Removal Task 和 Guard 的兼容文件或 Flag。
- 删除旧路径而没有新路径、数据验证、Rollback 和 Evidence。
- 通过旧路径绕过新 Security/Audit/Approval/Budget/Final Gate。
- 永久双写、永久双读、永久 Feature Flag、永久旧 DTO 或永久 Alias Registry。
- 只写矩阵或测试 Fixture 就声明 Runtime 已切流。

## Work Packages

### P02-T01 Executable Public API and Client Compatibility Layer

- Goal：实现旧/新 API、DTO、SSE Event、Error、Cursor 和 Client Capability Version 的真实版本 Adapter。
- Required：请求/响应字段映射、未知 Enum fail-closed、Security 字段不可丢失、RunOutcome 不扁平化、Adapter 不写领域表。
- Tests：Backend Contract、Web/Desktop Consumer、旧 Minor 兼容、未知 Major/字段、SSE Resume、授权撤销。
- Acceptance：所有活跃旧 Endpoint 均通过版本 Adapter 或被明确禁用；不存在 Route 直接进入旧业务主路径。

### P02-T02 Runtime Feature Flag and Rollout State Machine

- Goal：实现持久化或配置受控的 `DECLARED→SHADOW→CANARY→DEFAULT_NEW→ROLLBACK_WINDOW→RETIRED` 状态机和 Operator Command。
- Required：owner、scope、default、metric、security precondition、rollback command、expires_at、retire task、audit event。
- Tests：非法跳转、过期 Flag、并发更新、撤权、配置丢失、Rollback、RETIRED 后旧分支不可达。
- Acceptance：Flag 只决定路由，不复制领域事实；每次切换可审计、可恢复。

### P02-T03 Executable Alias and Bypass Enforcement

- Goal：把 Agent、Model、Tool、Retrieval、API、Import、DB Write 旁路转换为 CI 与 Runtime Guard。
- Required：AST/Import/Registry/Factory 扫描、动态 Provider/Tool 调用 Hook、跨 Owner Repository 检测、逐项 Allowlist 和 Deadline。
- Tests：新增直接 SDK、Tool Execute、旧 Import、动态注册、Monkey Patch、无登记 Flag 和跨 Owner DB Write 必须失败。
- Acceptance：Allowlist 具有单调递减验证；新增旁路默认拒绝。

### P02-T04 Executable Data Cutover Controller

- Goal：实现 `SCHEMA_EXPANDED→BACKFILLING→DUAL_READ→DUAL_WRITE_OPTIONAL→READ_CUTOVER→WRITE_CUTOVER→VERIFIED→LEGACY_FROZEN→LEGACY_REMOVED` 的迁移记录、Watermark 和验证接口。
- Required：source/target schema、transform、canonical hash、chunk/checkpoint、verification query、rollback boundary、retention、owner approval。
- Tests：断点续传、重复 Backfill、Hash Conflict、部分失败、Read/Write Cutover、Rollback Window、旧写入冻结。
- Acceptance：本 Phase 可使用代表性数据和当前 Store 证明控制器，不要求完成全部模块数据迁移；但后续模块必须复用同一控制语义。

### P02-T05 Rollback, Recovery and Reconciliation Drills

- Goal：为 Agent、Product API、Frontend、DB、Queue、Object、Model、Tool 和 Index 实现可执行回滚命令与演练。
- Required：trigger、max window、data reconcile、security impact、operator command、audit/evidence、不可回滚边界。
- Tests：新 API 失败、Client Version 不兼容、Queue Backlog、Tool UNKNOWN、Schema Forward-fix、Frontend Rollback、Security Epoch 变化。
- Acceptance：回滚不恢复任何绕过新 Security/Audit Gate 的路径；窗口结束后旧路径被删除或冻结。

### P02-T06 Migration Guard and Removal Gate Suite

- Goal：把 Matrix、Flag、Allowlist、Cutover、Rollback 和 Removal Gate 变为持续 CI Gate。
- Tests：真实仓库扫描、模拟违规提交、Flag 过期、Allowlist 增长、无 Evidence 切流、永久 deprecated Endpoint、`legacy/` 文件夹、未删除 Adapter。
- Acceptance：PHASE02 关闭时所有当前旧路径已受控；PHASE22 时 Gate 自动切换为零 Legacy、零 Alias、零旧主路径。

## Phase 完成定义

- 所有 PHASE01 登记的旧入口均已接入可执行 Adapter/Flag/Guard，或被明确禁用/删除。
- Feature Flag 状态机、Operator Rollback、Cutover Record 和 Removal Gate 有真实代码、Migration（如需要）与审计证据。
- API/Web/Desktop 兼容 Contract 有 Producer/Consumer Test，安全字段和 RunOutcome 不丢失。
- 旁路扫描覆盖静态与动态注册；新增未登记旁路在 CI 中失败。
- 至少完成一次代表性 API、Runtime、Frontend 和数据切流/回滚演练。
- Allowlist 只减不增；每项有 Deadline 和 PHASE22 Removal Gate。
- 所有 Work Package 经 Coordinator 批准，不能停留在 `completion_candidate`。

## Validation

```bash
git diff --check
python tools/scripts/verify_current_program.py
python tools/scripts/verify_phase02_compatibility_boundaries.py
pytest -q tests/repo tests/contracts tests/integration tests/fault -k 'compatibility or boundary or cutover or rollback or feature_flag' -p no:cacheprovider
# Web/Desktop contract, build and selected E2E commands recorded in docs/evidence/
```
