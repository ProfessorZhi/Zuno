# PHASE01 Current Baseline and Requirement Ledger

phase_id: PHASE01
status: completed
depends_on: none
owner: Coordinator / Repository Governance

## 订正说明

2026-07-16 撤回此前 `completed` 结论。已有 Inventory、Requirement Ledger 和 Risk Register 作为部分证据保留，但未经过完整 Coordinator Closure、双向 Requirement Traceability、陈旧路径检查和独立复核，不足以证明本 Phase 完成。

本 Phase 是完整目标架构实现的事实基线，不是一次性盘点。后续任何 Phase 都不得以旧文档、目录存在或局部测试替代这里冻结的最新 `main` Current。

## Phase 目标

基于最新 `main` 的代码、Migration、测试、Trace、Eval、运行配置和真实环境证据，建立十一模块可机器验证的 Current 真相与完整 Gap Ledger。每个 Mandatory Requirement 必须能够从 Target Requirement 双向追踪到 Current 代码、数据、测试、证据和负责 Phase；无法证明的能力必须标记为 `target_not_current`、`blocked` 或 `needs_evidence`。

本 Phase 不实现业务 Runtime，但必须把后续完整实现需要的所有范围、旧路径、数据源、环境依赖、风险和验收证据固定下来。遗漏任何生产入口、动态注册路径、持久化事实源或 Mandatory Requirement 都会阻止 Phase 关闭。

## Minimal Read Set

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/task-execution-contract.md`
- `docs/modules/README.md`
- 十一份模块 Target 文档
- `docs/architecture/architecture.md`
- `docs/status/production-readiness.md`
- accepted ADR、Contract Registry 与 Governance 文档
- 最新代码、Migration、测试、CI、Trace、Eval 和部署配置

## Current Anchors

```text
src/backend/zuno/{api,agent,memory,capability,knowledge,platform}/**
apps/web/**
apps/desktop/**
infra/**
tests/**
tools/evals/zuno/**
docs/status/**
.agent/references/**
所有 migration roots、动态 registry、feature flags、plugin/tool/model/provider factories
```

## Allowed Paths

```text
.agent/programs/work-products/**
.agent/references/code-map.md
.agent/references/runtime-call-chain.md
docs/status/production-readiness.md
docs/evidence/phase01-*.md
tools/scripts/verify_current_program.py
tools/scripts/verify_phase01_*.py
tests/repo/test_current_program_contract.py
tests/repo/test_phase01_*.py
```

## Forbidden Paths

- Runtime 业务代码、Migration、公开 API 和前端行为。
- 改变十一模块 Target、Ownership 或已接受 ADR。
- 以文档存在、类名存在、Compose 声明或 Mock 作为 Current。
- 为通过审计删除失败测试、降低 Requirement、忽略动态入口或把未知写成已实现。
- 使用模糊的 `implementation available` 覆盖模块级、Requirement 级真实状态。

## Work Packages

### P01-T01 Runtime Call-chain Inventory

- Goal：完整列出所有产品默认路径、测试路径、回滚路径和旁路，包括 Completion、Workspace、Agent Core、Knowledge、Memory、Capability、Tool、Model、Security、Observability、Ingestion、Web 与 Desktop。
- Required：path、symbol、caller、callee、selection condition、default/legacy、state owner、transaction、external effect、security gate、test/evidence、target phase。
- Tests：静态搜索、动态 Registry/Factory 枚举和 focused runtime tests 三方对账；所有公开入口均能到达唯一 Owner。
- Acceptance：不存在未登记默认入口、直接 Provider/Tool 调用或 Route 业务编排。

### P01-T02 Persistence and Infrastructure Inventory

- Goal：完整盘点 PostgreSQL/SQLite、Alembic、RabbitMQ、Object Store、Redis、Checkpointer、Vector/Graph/Search、Secret、Backup/Restore、PITR 和 Projection Rebuild Current。
- Required：物理 Owner、领域 Owner、表/对象/队列、Migration、连接配置、事务边界、并发/故障测试、真实环境证据、恢复责任。
- Tests：每个 Current 至少关联代码与真实 Integration/Fault/运行证据；配置或 Adapter 声明不能单独算 Current。
- Acceptance：Developer/CI Adapter、Server Product Current、Target 和 blocked 边界清晰。

### P01-T03 Architecture Requirement Ledger

- Goal：提取十一模块全部 Mandatory `ARCH-*` Requirement，形成 Target→Current→Gap→Phase→Test→Evidence 双向追踪。
- Required：requirement_id、owner、mandatory、target statement、current status、current paths、migration/data impact、failure/recovery requirement、dependencies、target phase、test IDs、evidence refs、reviewer。
- Tests：Requirement ID 与模块文档完全一致；每项只有一个 Owner；每项分配到 PHASE02–22；无悬空依赖、空 Evidence 或通用占位符。
- Acceptance：Ledger 能生成每 Phase 完整验收清单，并能从代码/测试反向找到所满足的 Requirement。

### P01-T04 Frontend and Desktop Inventory

- Goal：完整盘点 Web/Desktop API Client、Store、DTO、SSE、Approval、Citation、Artifact、Trace/Eval、路由、Bridge、Build、Browser E2E 和 Desktop Smoke。
- Required：旧 DTO、字符串状态推断、单 Pending Approval、SSE Cursor/Resume、Authorized Projection、AvailableAction、下载授权、断线/撤权/多 Interrupt/UNKNOWN UI 缺口。
- Tests：运行可用的 lint/build/unit/E2E；未运行项必须明确 blocked 原因和后续 Phase。
- Acceptance：区分页面存在、Contract 接入、真实断线恢复和端到端证明。

### P01-T05 Legacy, Alias and Bypass Inventory

- Goal：枚举所有直接 Provider SDK、Tool Execute、MCP、HTTP Write、Subprocess、旧 Import Alias、跨 Owner DB Write、旧 Runtime、动态加载和环境 Flag。
- Required：path、symbol、owner、risk、target gateway、current callers、temporary allowlist、migration task、removal task、deadline、guard test。
- Tests：AST/文本/运行时注册表联合扫描；新增未登记旁路必须 CI Fail；Inventory 与 PHASE22 删除清单双向一致。
- Acceptance：不存在无法归属或没有迁移/删除任务的生产旁路。

### P01-T06 Risk, Dependency and Readiness Report

- Goal：把 P01-T01–T05 转为完整依赖图、环境矩阵、P0/P1 风险、Stop Condition 和 Phase Readiness。
- Required risks：Schema/Cutover、Provider、PostgreSQL/RabbitMQ/Object/Checkpointer、Security/Secret、Frontend、Benchmark、Legacy Removal、Backup/Restore、CI capacity。
- Tests：所有 P0 有 Owner、Mitigation、验证 Phase 和 Stop Condition；对 Inventory 和 Ledger 进行独立抽样复核。
- Acceptance：只有在无遗漏 Mandatory Requirement、无未归属 P0、无陈旧路径且 Coordinator 正式批准后，PHASE02 才可 ready。

## Phase 完成定义

- 六个 Work Package 全部由 Coordinator 复核并标记 `completed`，不能停留在 `completion_candidate`。
- Requirement Ledger 100% 覆盖十一模块 Mandatory Requirement，具备 Target↔Code/Test/Evidence 双向追踪。
- Runtime、Persistence、Frontend、Legacy Inventory 覆盖静态与动态入口，并记录审计基线 Commit。
- 所有 Current 声明有代码与测试/运行证据；所有未证明能力明确为 Gap/Blocked。
- 每个 Legacy/Bypass 有迁移、Guard、Deadline 和最终删除任务。
- 运行仓库级验证并保存 Evidence；未运行完整 CI 时不得关闭。
- 本 Phase 未修改 Runtime 行为。

## Validation

```bash
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_phase01_complete_baseline.py
pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider
# 运行并记录仓库当前可用的 backend/web/desktop inventory verification commands
```
