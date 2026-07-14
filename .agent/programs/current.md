# 当前程序

state: active
active_program: zuno-canonical-architecture-runtime-realization-v1
current_phase: PHASE01
program_version: 1
activated_at: 2026-07-14
base_branch: main
architecture_baseline_commit: 249f1c95855043627cedd289a5de1fd3719f6cd0

## 程序目标

把已经冻结的十一模块 Target 架构转化为可执行、可恢复、可审计、可评测的 Runtime Current，并提供足以让弱模型 Agent 按任务清单逐项实现的强约束执行系统。

本 Program 不是新一轮架构发散，也不是一次性大重构。执行顺序固定为：

```text
Current 证据审计
→ Executable Contract
→ Infrastructure / Security / Observability 基础
→ Model Gateway
→ Agent Core 最小真实闭环
→ Product / Ingestion / Knowledge / Memory
→ Capability / Tool Effect
→ 动态 DAG 与 Agentic GraphRAG
→ Final Gate / Eval / Fault / Benchmark
→ Cutover 与归档
```

## 当前阶段

```text
PHASE01_current-baseline-and-requirement-ledger
```

PHASE01 只做最新 `main` 的 Current 证据盘点、Requirement 映射、依赖图和执行基线。不得在 PHASE01 大规模修改 Runtime、数据库或公开 API。

## 唯一事实源

执行时按以下优先级读取：

```text
已接受 ADR / 共享 Contract Registry
→ 十一份 Canonical Owner 模块文档
→ docs/architecture/architecture.md
→ 本 Program
→ 最新 main 的代码、Migration、测试、Trace、Eval 和运行证据
```

模块文档定义 Target；代码和证据定义 Current。任何任务不得因为文档存在类名、表名或流程就把能力写成已实现。

## Program 文件

```text
.agent/programs/current.md
.agent/programs/implementation-roadmap.md
.agent/programs/closure-checklist.md
.agent/programs/task-execution-contract.md
.agent/programs/program-manifest.yaml
.agent/programs/PHASE01_*.md ... PHASE19_*.md
```

## 执行角色

### Coordinator

负责：

- 选择当前 Phase 和可执行 Work Package；
- 检查依赖、写入范围和 Stop Condition；
- 解决跨模块 Contract 冲突；
- 审查 Diff、Migration、测试和证据；
- 合并、更新 Current 状态和关闭 Phase。

### Implementer Agent

负责：

- 只执行一个明确 Work Package；
- 先读取任务指定的架构与当前代码；
- 在独立 Worktree 和 Branch 中修改；
- 运行任务要求的全部验证；
- Commit、Push，并提交标准化完成报告。

Implementer Agent 不得自行改变架构原则、扩大范围、跳过 Migration、把 Mock 当真实集成或把 blocked 写成 measured。

## 固定架构原则

以下原则在整个 Program 中冻结，任何实现任务不得自行改变：

1. Product Runtime 使用 LangGraph Single Controller，不默认建设自治 Multi-Agent Runtime。
2. 每个任务必须有 Plan；简单任务使用 Deterministic Single-Step Plan，复杂任务使用 Dynamic DAG Plan。
3. 不允许通过 direct answer 绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。
4. 固定 AgentRunGraph、动态不可变 PlanVersion DAG、固定 StepExecutionGraph。
5. Retry 与 Replan 分开；Replan 必须经过 Replan Barrier 并创建新 PlanVersion。
6. PostgreSQL 保存领域事实；LangGraph Checkpointer 保存图控制状态；Memory 和 Knowledge 另有明确 Owner。
7. 模型只产生 Proposal，不直接批准权限、执行未审批副作用、激活 PlanVersion 或提交长期 Memory。
8. Tool UNKNOWN Effect 禁止盲目 Retry，必须进入 EffectReconciliation。
9. Queue ACK、Lease Release、Checkpoint Commit、Audit Receipt 和 HTTP 2xx 都不能冒充领域成功。
10. Observability 生成 Projection、Eval、Benchmark、Gate 和 Evidence，但不修改源领域事实。

## 阶段推进规则

一个 Phase 只有同时满足以下条件才能关闭：

- 所有 Mandatory Work Package 完成；
- 相关 Migration 可升级、可回滚或明确不可回滚边界；
- 正常、失败、重试、恢复和幂等路径有测试；
- 相关模块文档与 Current 状态只按真实证据同步；
- 完成证据进入 `docs/evidence/`；
- Coordinator 审查通过；
- 当前 Phase 文件和 Closure Checklist 更新。

只增加 Type、接口、README、Mock、Diagram 或未接入的 Adapter，不能关闭 Runtime Phase。

## 状态表达

允许：

```text
design available
implementation available
runtime observed
measurement blocked
quality not yet proven
```

只有满足固定 Dataset、完整 Profile、可比较 Benchmark、Release Gate 和 Evidence 时才能写：

```text
measured
quality proven
```

只有完成安全、恢复、运维、负载和生产运行证据后才能评估 `production ready`。

## Stop Condition

出现以下情况必须停止当前 Work Package 并交回 Coordinator：

- 需要改变十一模块 Ownership；
- 需要改变共享 Contract 的字段语义或版本兼容策略；
- 需要修改公开 API 的既有字段；
- 需要新增或升级关键依赖；
- 需要数据库不可逆迁移；
- 需要降低 Security、Audit、Approval 或 Redaction Gate；
- 发现现有 Target 无法满足恢复、幂等或事实一致性；
- 测试只能通过伪造 Evidence、Citation、Receipt 或成功状态。

## 当前质量边界

Program 激活不改变现有事实：

```text
implementation available
measurement blocked
quality not yet proven
production ready not established
```

PHASE19 之前不得声明 Agentic GraphRAG 已稳定优于 Baseline。