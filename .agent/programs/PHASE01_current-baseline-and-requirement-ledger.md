# PHASE01 Current Baseline and Requirement Ledger

phase_id: PHASE01
status: completed
depends_on: none
owner: Coordinator / Repository Governance

## Phase 目标

基于最新 `main` 的代码、Migration、测试、Trace、Eval 和运行证据建立 Current 真相，生成十一模块 Requirement Ledger、Legacy/Bypass Inventory、Frontend Inventory、数据迁移源表和风险依赖图。本 Phase 不实现新 Runtime。

## Minimal Read Set

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/task-execution-contract.md`
- `docs/modules/README.md`
- `docs/status/production-readiness.md`
- `.agent/references/code-map.md`
- 当前任务对应模块文档

## Current Anchors

```text
src/backend/zuno/{api,agent,memory,capability,knowledge,platform}/**
apps/web/**
apps/desktop/**
infra/**
alembic/** 或当前 migration roots
tests/**
tools/evals/zuno/**
src/backend/zuno/platform/compatibility/legacy_aliases.py
```

## Allowed Paths

```text
.agent/programs/work-products/**
.agent/references/code-map.md
.agent/references/runtime-call-chain.md
docs/status/production-readiness.md
tools/scripts/verify_current_program.py
tests/repo/test_current_program_contract.py
```

## Forbidden Paths

- Runtime 业务代码、Migration、公开 API 和前端行为。
- 十一模块 Target 原则和总架构。
- 为让审计通过而删除失败测试或把未知写成已实现。

## Work Packages

### P01-T01 Runtime Call-chain Inventory

- Goal：列出 Completion、Workspace Task、Unified Runtime、GeneralAgent、Knowledge、Memory、Capability、Tool、Model 的真实默认调用链、测试调用链和回滚 Flag。
- Steps：用 `rg` 搜入口、构造点、默认值、依赖工厂和调用者；记录同步/异步、事务、状态写入和外部副作用。
- Output：`work-products/current-runtime-inventory.md`。
- Required fields：path、symbol、caller、callee、default_or_legacy、state_owner、side_effect、test_evidence、target_phase。
- Tests：Inventory 中每个符号可被仓库搜索命中；抽样链路与 focused tests 对齐。
- Acceptance：不得用旧 Program 结论替代最新代码事实。

### P01-T02 Persistence and Infrastructure Inventory

- Goal：盘点 SQLite/PostgreSQL、SQLModel、Alembic、Object Store、Queue、Redis、Checkpointer、Vector/Graph Index、Secret 和 Backup Current。
- Steps：记录配置、Adapter、表、Migration、真实连接、环境要求、并发/恢复测试和未证明能力。
- Output：`work-products/current-persistence-inventory.md`。
- Tests：每个“Current”至少关联代码与测试或运行证据；Compose/依赖声明不能单独算 Current。
- Acceptance：明确 Developer/CI Adapter 与 Server Product Target。

### P01-T03 Architecture Requirement Ledger

- Goal：提取十一模块全部 `ARCH-*` Requirement，映射 Current、Gap、依赖、测试和 Evidence。
- Output：`work-products/requirement-ledger.yaml`。
- Required fields：requirement_id、module、mandatory、current_status、current_paths、gap、dependencies、target_phase、test_ids、evidence_refs。
- Tests：Requirement ID 唯一；每个 Mandatory Requirement 分配到 PHASE02–PHASE22；无悬空依赖。
- Acceptance：文档中存在类名、表名或流程不能自动标记 implementation available。

### P01-T04 Frontend and Desktop Inventory

- Goal：盘点 Web/Desktop API Client、Pinia Store、SSE、Approval、Citation、Artifact、Trace/Eval、路由、Bridge 和现有 E2E。
- Output：`work-products/frontend-current-inventory.md`。
- Required：旧 DTO、状态字符串推断、单 pending approval、SSE cursor/resume、桌面 bridge、下载/授权、构建/测试入口。
- Tests：记录 `npm run lint`、`npm run build` 和可用 Browser/Desktop 测试；本任务不修改页面。
- Acceptance：区分“页面存在”“Contract 接入”“真实断线/撤权/E2E 证明”。

### P01-T05 Legacy, Alias and Bypass Inventory

- Goal：枚举所有直接 Provider SDK、Tool Execute、MCP call、httpx write、subprocess、旧 root import alias、跨模块 Repository/DB 写入和 Route 业务编排。
- Output：`work-products/legacy-bypass-inventory.yaml`。
- Required：path、symbol、owner、risk、target_gateway、temporary_allowlist、migration_task、removal_task。
- Tests：静态搜索可重复；覆盖动态 Import、注册表、Monkey Patch 和环境 Flag。
- Acceptance：生产代码中名称含 `legacy` 的目录/文件、`platform/compatibility/legacy_aliases.py` 和 `tests/legacy_guards/**` 都登记到 PHASE22 删除，不允许最终保留。

### P01-T06 Risk, Dependency and Readiness Report

- Goal：把 P01-T01–T05 转成 Phase 依赖、环境需求、并行边界和 Stop Condition。
- Output：`work-products/program-risk-register.md`、`work-products/phase-readiness.yaml`。
- Required risks：schema migration、dual path、provider、Postgres/RabbitMQ/Object/Checkpointer、frontend compatibility、benchmark data、security/secret、legacy retirement。
- Tests：PHASE02 只有在无未归属 P0 风险时才可 ready。
- Acceptance：未知项写 blocked/needs-evidence，不通过猜测关闭。

## Phase 完成定义

- 六个 Work Package 经 Coordinator 审核。
- Requirement Ledger 覆盖十一模块 Mandatory Requirement。
- Runtime、Persistence、Frontend、Legacy Current 有路径和证据。
- 每个 Legacy/Bypass 都有迁移任务和最终删除任务。
- 本 Phase 未修改 Runtime 行为。

## Validation

```bash
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_current_program_contract.py -p no:cacheprovider
```
