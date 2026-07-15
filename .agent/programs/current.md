# 当前程序

state: active
active_program: zuno-canonical-architecture-runtime-realization-v1
current_phase: PHASE02
phase_count: 22
program_version: 1
activated_at: 2026-07-14
base_branch: main
architecture_baseline_commit: 249f1c95855043627cedd289a5de1fd3719f6cd0

## 程序目标

把十一份 Canonical Module Target 架构完整实现为可执行、可恢复、可并行、可审计、可评测的 Runtime Current，并从当前 GeneralAgent、局部 Unified Runtime、SQLite、本地 Store、直接 Tool/Provider 调用和旧前端 Contract 平滑迁移到新架构。

这是一个总 Program，不拆成多个互相竞争的 Program。内部 22 个 Phase 共同完成：

```text
Current 审计
→ Legacy 兼容与切流图
→ Executable Contract
→ PostgreSQL / Queue / Object / Checkpointer
→ Security / Observability / Model Gateway
→ Single Controller / Product API / Web / Desktop
→ Ingestion / Knowledge / Memory / Capability
→ Tool Read-only / Side Effect / UNKNOWN Reconciliation
→ Dynamic DAG / Agentic GraphRAG
→ Final Gate / Publication / Reflexion
→ Eval / Release Gate / Fault / E2E
→ Fixed Benchmark / Legacy Removal / Closure
```

## 当前阶段

```text
PHASE02_legacy-runtime-compatibility-and-cutover-map
```

PHASE01 已完成 Current Baseline、Requirement Ledger、Frontend Inventory、Legacy Bypass Inventory 和风险依赖图，产物位于 `.agent/programs/work-products/`。

PHASE02 基于 PHASE01 产物把旧 Agent、API、Store、Tool、Model、Retrieval、Frontend 和 Import 路径转成临时迁移对象：有版本、有 Feature Flag、有 Shadow/Canary、Rollback、Removal Gate 和静态 Guard。不得在 PHASE02 实现新领域模型或大规模迁移数据。

## 事实源优先级

```text
已接受 ADR / 共享 Contract Registry
→ 十一份 Canonical Owner 模块文档
→ docs/architecture/architecture.md
→ 本 Program
→ 最新 main 的代码、Migration、测试、Trace、Eval 和运行证据
```

模块文档定义 Target；代码和证据定义 Current。Mermaid 和旧 Program 不能反向覆盖新模块 Contract。

## 固定架构原则

1. Product Runtime 使用 LangGraph Single Controller，不默认建设自治 Multi-Agent Runtime。
2. 每个任务必须有 Plan；简单任务使用 Deterministic Single-Step Plan，复杂任务使用 Dynamic DAG Plan。
3. 不允许 direct answer 绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。
4. 固定 AgentRunGraph、动态不可变 PlanVersion DAG、固定 StepExecutionGraph。
5. Retry 与 Replan 分开；Replan 经过 Replan Barrier 并创建新 PlanVersion。
6. PostgreSQL 保存领域事实；LangGraph Checkpointer 保存图控制状态；Memory、Knowledge、Trace 各有 Owner。
7. 模型只产生 Proposal，不直接批准权限、激活 PlanVersion、执行未审批副作用或提交长期 Memory。
8. Tool UNKNOWN Effect 禁止盲目 Retry，必须进入 EffectReconciliation。
9. Queue ACK、Lease Release、Checkpoint Commit、Audit Receipt 和 HTTP 2xx 都不能冒充领域成功。
10. Observability 形成 Projection、Eval、Benchmark、Gate 和 Evidence，但不修改源领域事实。
11. Frontend 只消费 Authorized Projection 和 AvailableAction，不拥有 Run、Approval、Effect、Evidence、Memory 或 Eval 事实。
12. 架构能力不得因使用 GPT-5.5 medium、Token 成本或工期而降级。

## Program 文件

```text
.agent/programs/README.md
.agent/programs/current.md
.agent/programs/implementation-roadmap.md
.agent/programs/task-execution-contract.md
.agent/programs/codex-medium-runbook.md
.agent/programs/legacy-to-target-migration-map.md
.agent/programs/program-manifest.yaml
.agent/programs/closure-checklist.md
.agent/programs/PHASE01_*.md ... PHASE22_*.md
```

## 阶段推进规则

一个 Phase 只有同时满足以下条件才能关闭：

- 所有 Mandatory Work Package 完成；
- 真实主路径已接入，不只有 Stub、Interface 或 Mock；
- Migration 可升级、可回滚或有正式不可回滚恢复策略；
- 正常、失败、重试、恢复、取消、幂等和安全路径有测试；
- Frontend Contract 变化已同步 Web/Desktop 与契约测试；
- 完成证据进入 `docs/evidence/`；
- Current 状态只按代码、测试、Trace、Eval 或运行证据更新；
- Coordinator 审查 Diff、验证和架构一致性后批准。

Implementer Agent 只能提交 `completion_candidate`，不得自行把 Phase 改成 `completed`。

## Stop Condition

出现以下情况立即停止并交回 Coordinator：

- 需要改变十一模块 Ownership 或固定架构原则；
- 需要改变共享 Contract 字段语义、Major Version 或兼容策略；
- 需要删除或重命名既有公开 API 字段；
- 需要新增或升级关键依赖；
- 需要数据库不可逆 Migration；
- 需要降低 Security、Audit、Approval、Redaction、Budget 或 Final Gate；
- 发现目标状态无法满足恢复、幂等、隔离或事实一致性；
- 测试只能靠伪造 Evidence、Citation、EffectReceipt、UsageReceipt 或成功状态通过。

## 当前状态边界

Program 激活不改变现有事实：

```text
implementation available
measurement blocked
quality not yet proven
production ready not established
```

PHASE22 之前不得声明 Agentic GraphRAG 已稳定优于 Baseline，不得把文档完成写成系统完成。
