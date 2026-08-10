# Work Package 执行契约

program: zuno-canonical-architecture-runtime-realization-v1
status: active

本文规定每个弱模型 Implementer Agent 必须遵循的统一执行格式。Phase 文件中的每个 Work Package 都必须按本文执行，不得自由发挥。

## 1. 单任务原则

一个 Agent Thread 一次只领取一个 Work Package。禁止同时实现多个 Phase，禁止在未授权情况下顺手重构邻接模块。

每个任务必须具有：

```text
task_id
phase_id
owner_module
objective
dependencies
architecture_sources
allowed_paths
forbidden_paths
required_contracts
state_transitions
failure_semantics
migration_requirements
test_requirements
evidence_requirements
stop_conditions
```

缺少任一关键字段时，不开始编码，交回 Coordinator 补齐。

## 2. 开始前强制步骤

Implementer Agent 必须按顺序执行：

1. 确认目标仓库、目标 Branch、独立 Worktree 和当前 Commit。
2. 运行 `git status --short --branch`，工作区必须干净。
3. 读取：
   - `AGENTS.md`；
   - `.agent/programs/current.md`；
   - `.agent/programs/task-execution-contract.md`；
   - 当前 Phase 文件；
   - Work Package 指定的模块文档；
   - `docs/status/production-readiness.md`；
   - 相关 ADR 与共享 Contract Registry。
4. 搜索当前代码、Migration、测试和活跃引用，禁止仅按目标目录猜测 Current。
5. 在完成报告中记录实际起始 Commit 和读取的事实源。

## 3. Current 审计格式

编码前必须写出最小审计：

```text
Current:
- 已存在代码：路径 + 类/函数 + 真实行为
- 已存在数据：表/Migration/Store
- 已存在测试：正常/异常覆盖
- 已存在证据：Trace/Eval/E2E

Gap:
- 目标 Contract 与 Current 的差异
- 缺失状态转换
- 缺失失败/恢复语义
- 缺失测试与证据

Plan:
- 本任务将修改的精确文件
- Expand / Migrate / Verify / Contract 顺序
- 回滚方式
```

若审计发现任务描述与最新 `main` 不一致，以最新证据为准并停止，请 Coordinator 更新任务，不得默默改变架构。

## 4. 写入范围

### Allowed Paths

只能修改 Work Package 明确列出的目录和文件。测试文件、Migration 和文档同步路径必须显式列出。

### Forbidden Paths

默认禁止：

- 其他模块领域模型和数据库表；
- `docs/architecture/` 和模块架构原则；
- 不相关公开 API；
- 依赖版本；
- CI、部署和安全策略；
- 历史归档；
- 通过删除测试或降低 Gate 解决失败。

跨 Owner 写入必须由 Coordinator 拆成独立 Work Package。

## 5. 实现顺序

所有 Runtime Work Package 使用：

```text
Expand
→ Migrate
→ Verify
→ Contract
```

### Expand

增加新 Schema、Port、Adapter、表或路径，不破坏旧调用。

### Migrate

让真实生产路径逐步进入新实现；必要时保留受控兼容桥。

### Verify

用 Unit、Integration、Fault、E2E、Trace 或 Eval 证明正常与异常路径。

### Contract

删除重复 Owner、旧主路径或临时兼容层。只有新路径有证据后才能 Contract。

禁止先 Bulk Move 再补测试。

## 6. Contract 规则

- 所有跨模块对象使用显式版本。
- Canonical Serialization、Hash 和 Idempotency Key 必须确定性。
- Enum 未知值、Schema Version 不支持和 Hash 不匹配必须显式失败。
- Producer Fixture 和 Consumer Fixture 必须成对存在。
- Receipt 只能证明其 Owner 范围内的事实。
- Domain Model 不 Import Provider SDK、Web Framework 或外部 Observability SDK。
- Model 输出先进入 Proposal/Validation，不直接写领域终态。

## 7. 数据库与 Migration

涉及数据库的任务必须提供：

1. 新增/变更表、列、索引、唯一约束和外键说明。
2. Alembic Revision。
3. Upgrade 路径。
4. Downgrade 或明确的不可回滚原因与恢复策略。
5. Backfill、Dual Read/Write、Cutover 是否需要。
6. 并发、锁、隔离和幂等测试。
7. SQLite Adapter 与 PostgreSQL 语义差异说明。

禁止用 `create_all()` 冒充正式 Migration，禁止只在 SQLite 上证明 PostgreSQL 锁和并发语义。

## 8. 状态与失败

每个任务必须验证：

```text
触发条件
允许的状态转换
非法转换
失败传播
Retry Owner
Recovery Owner
Idempotency / Fencing
取消和 Deadline
审计要求
```

出现 `UNKNOWN`、部分提交、晚到结果或重复消息时，不得直接写成功或盲目 Retry。

## 9. 测试最低要求

### Contract / Domain Task

- Unit Test：Schema、状态机、Hash、Validation。
- Contract Test：Producer/Consumer Fixture、兼容性。

### Persistence / Queue Task

- Integration Test：真实 PostgreSQL/Queue/Object Adapter，或明确标记环境 Blocked。
- Fault Test：Crash、Duplicate、Out-of-order、Lease Loss、Retry Exhaustion。

### Agent / Knowledge / Tool Task

- 正常路径。
- Blocked/Denied/Abstain 路径。
- Retry 与 Replan 区分。
- Resume/Cancel/Deadline。
- Evidence、Citation、Effect 或 Usage 不得伪造。

### Product Task

- API Contract。
- Authorization Scope。
- SSE Cursor/Resume。
- Projection Freshness 和错误映射。

## 10. 验证命令

每个 Work Package 至少运行：

```bash
git diff --check
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_current_program.py
pytest -q <focused tests> -p no:cacheprovider
```

架构、模块或共享 Contract 相关任务追加：

```bash
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_wave1_contract_freeze.py
```

数据库任务追加 Alembic upgrade/downgrade 和 PostgreSQL integration；前端/API 任务追加对应构建与 E2E；Phase Closure 运行路线图指定的集成测试。

## 11. 完成证据

完成报告必须包含：

```text
Task ID
起始 Commit
最终 Commit
修改文件
实现的 Contract / 状态转换
Migration Revision
运行命令与结果
未运行命令及原因
正常路径证据
异常/恢复路径证据
已知限制
Current 状态是否改变
需要同步的文档
```

需要持久保存的证据写入 `docs/evidence/`，并包含 Artifact Hash、环境、配置版本和重现命令。

## 12. 禁止的完成声明

下列情况不能写 Task Completed：

- 只有接口或 Stub；
- 只有 Mock Test；
- 只有 README 或 Diagram；
- 真实依赖不可用却写成测试通过；
- 使用占位 Evidence、Citation、EffectReceipt 或 UsageReceipt；
- 删除失败测试；
- 将 BLOCKED、UNAVAILABLE 或 INCOMPARABLE 写成 FAILED/PASSED；
- 将本地单进程行为写成分布式恢复；
- 将 Adapter 存在写成 Provider/Store 已生产可用。

## 13. 标准完成报告模板

```markdown
# <TASK_ID> Completion Report

## Baseline
- start_commit:
- branch:
- current evidence:

## Changes
- files:
- contracts:
- migrations:
- state transitions:

## Verification
- command:
  result:

## Failure and Recovery Evidence
- scenario:
  evidence:

## Status Boundary
- newly current:
- remains target:
- blocked:

## Handoff
- next task:
- coordinator decisions required:
```

## 14. Coordinator 审查清单

Coordinator 合并前必须确认：

- Diff 未越过 Allowed Paths；
- Contract 与模块 Owner 一致；
- Migration 和回滚完整；
- 不存在第二套事实 Owner；
- 安全、预算、审批和审计未被绕过；
- Retry、Replan、Recovery、Reconciliation 语义正确；
- 测试覆盖异常路径；
- 文档只按证据更新 Current；
- Commit 和 Push 已完成；
- 未运行验证被明确披露。