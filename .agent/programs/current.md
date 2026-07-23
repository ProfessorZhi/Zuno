# 当前程序

state: active
active_program: zuno-canonical-architecture-runtime-realization-v1
current_phase: PHASE09
phase_count: 22
program_version: 2
activated_at: 2026-07-14
corrected_at: 2026-07-16
base_branch: main
architecture_baseline_commit: 249f1c95855043627cedd289a5de1fd3719f6cd0
correction_baseline_commit: 49a6aec8392bfa4be8e0662f98b9d1ef6a65960a

## 程序目标

把十一份 Canonical Module Target 架构**完整实现**为可执行、可恢复、可并行、可审计、可评测的 Runtime Current，并从 GeneralAgent、局部 Unified Runtime、SQLite、本地 Store、直接 Tool/Provider 调用和旧前端 Contract 平滑迁移到 Canonical Runtime。

本 Program 不接受“最小闭环实现后把剩余范围交给未来 Phase”的关闭方式。最小 Vertical Slice 只能作为阶段中的中间检查点；Phase `completed` 必须证明该 Phase 文件列出的完整范围、异常路径、恢复、迁移、真实依赖和 Requirement 均已完成。

```text
Current 审计
→ 可执行 Legacy/Cutover Control
→ 完整 Executable Contract Adoption
→ 完整 PostgreSQL / RabbitMQ / Object / Checkpointer Foundation
→ Security / Observability / Model Gateway
→ Single Controller / Product API / Web / Desktop
→ Ingestion / Knowledge / Memory / Capability
→ Tool Read-only / Side Effect / UNKNOWN Reconciliation
→ Dynamic DAG / Agentic GraphRAG
→ Final Gate / Publication / Reflexion
→ Eval / Release Gate / Fault / E2E
→ Fixed Benchmark / Legacy Removal / Closure
```

## PHASE01–04 订正决定

2026-07-16 经架构审查，撤回 PHASE01–04 的 `completed` 结论并重新打开：

- PHASE01 已完成重新审计和 Coordinator Closure；Inventory、Requirement Ledger、Risk Register 与 Readiness 作为 PHASE02 输入。
- PHASE02 已有 Matrix/Flag/Allowlist/Playbook 是迁移设计，尚未形成可执行 Adapter、Flag State Machine、Cutover Controller、Rollback Drill 和 Runtime/CI Guard。
- PHASE03 已有共享 Contract 内核是部分实现，尚未覆盖十一模块完整 Contract、真实 Producer/Consumer、Web/Desktop 类型和重复定义清理。
- PHASE04 completed。PostgreSQL、Alembic、UoW、Outbox/Inbox、RabbitMQ、Idempotency、Lease/Fencing、MinIO/S3、官方 LangGraph PostgreSQL Checkpointer、Backup/Restore、Generic Replay Framework、Fault Recovery 和 Operator Readiness 已按 PHASE04 范围完成；这不表示 PHASE05–22 Runtime 已实现，也不表示 production ready。

这些已有产物保留并作为后续实现输入。PHASE05 completed，PHASE06 completed，PHASE07 completed；PHASE08 completed；PHASE11 completed；PHASE09 ready，等待正式实施；PHASE12 ready，等待正式实施；PHASE10、PHASE12–22 不得提前提升为 Current。

## 当前阶段

```text
PHASE09_product-surface-backend-runtime
```

PHASE01 先重新冻结最新 `main` Current、完整 Requirement Ledger、Runtime/Persistence/Frontend/Legacy Inventory 和风险依赖，确保后续实现没有遗漏范围。PHASE02–04 按订正后的完整完成定义依次推进。

## 事实源优先级

```text
已接受 ADR / 共享 Contract Registry
→ 十一份 Canonical Owner 模块文档
→ docs/architecture/architecture.md
→ 本 Program
→ 最新 main 的代码、Migration、测试、Trace、Eval 和运行证据
```

模块文档定义 Target；代码和证据定义 Current。Program 状态、README、Mermaid、类名、表名和目录存在都不能单独把 Target 提升为 Current。

## 固定架构原则

1. Product Runtime 使用 LangGraph Single Controller，不默认建设自治 Multi-Agent Runtime。
2. 每个任务必须有 Plan；简单任务使用 Deterministic Single-Step Plan，复杂任务使用 Dynamic DAG Plan。
3. 不允许 direct answer 绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。
4. 固定 AgentRunGraph、动态不可变 PlanVersion DAG、固定 StepExecutionGraph。
5. Retry 与 Replan 分开；Replan 经过 Replan Barrier 并创建新 PlanVersion。
6. PostgreSQL 保存领域事实；LangGraph Checkpointer 保存图控制状态；Memory、Knowledge、Trace 各有 Owner。
7. 模型只产生 Proposal，不直接批准权限、激活 PlanVersion、执行未审批副作用或提交长期 Memory。
8. Tool UNKNOWN Effect 禁止盲目 Retry，必须进入 EffectReconciliation。
9. Queue ACK、Lease Release、Checkpoint Commit、Audit Receipt、Object Commit 和 HTTP 2xx 都不能冒充领域成功。
10. Observability 形成 Projection、Eval、Benchmark、Gate 和 Evidence，但不修改源领域事实。
11. Frontend 只消费 Authorized Projection 和 AvailableAction，不拥有 Run、Approval、Effect、Evidence、Memory 或 Eval 事实。
12. 架构能力不得因模型能力、Token 成本或工期而降级。
13. 最小实现、Stub、局部 Happy Path 或单机 Mock 不能关闭 Phase；完整范围内仍有 `target_not_current` 即不得关闭。

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

- 所有 Mandatory Work Package 完成并由 Coordinator 批准；
- Phase 文件列出的完整范围已实现，不以最小闭环、未来补齐或后续 Phase 代替；
- 真实默认主路径已接入，不只有 Stub、Interface、Fixture、Mock 或旁路调用；
- 所有范围内 Mandatory Requirement 已从 `target_not_current` 更新为有 Code/Migration/Test/Evidence 的 Current；
- Migration 可升级、可回滚或有正式不可回滚恢复策略；
- 正常、失败、重试、恢复、取消、并发、幂等、安全和故障注入路径有测试；
- 真实 PostgreSQL/Queue/Object/Checkpointer/Provider 等依赖按任务要求运行，环境缺失必须 Block；
- Frontend Contract 变化同步 Web/Desktop 与 Producer/Consumer Test；
- 完成证据进入 `docs/evidence/`，包含环境、版本、Hash、Commit 和重现命令；
- Requirement Ledger、Current/Gap、Legacy Allowlist 和 Removal Gate 同步更新；
- 未运行完整 CI、E2E、Fault、Migration、Security、Load 或 DR 时，不得声称对应 Gate 通过。

Implementer Agent 只能提交 `completion_candidate`，不得自行把 Phase 改成 `completed`。Coordinator 不得在 Readiness 或 Evidence 仍为 `completion_candidate/pending` 时修改 Program Manifest 为 `completed`。

## Stop Condition

出现以下情况立即停止并交回 Coordinator：

- 需要改变十一模块 Ownership 或固定架构原则；
- 需要改变共享 Contract 字段语义、Major Version 或兼容策略；
- 需要删除或重命名既有公开 API 字段；
- 需要新增或升级关键依赖；
- 需要数据库不可逆 Migration；
- 需要降低 Security、Audit、Approval、Redaction、Budget 或 Final Gate；
- 发现目标状态无法满足恢复、幂等、隔离或事实一致性；
- 测试只能靠伪造 Evidence、Citation、EffectReceipt、UsageReceipt 或成功状态通过；
- 只能实现最小 Happy Path，无法完成当前 Phase 全部 Requirement。

## 当前状态边界

```text
partial implementation available
measurement blocked
quality not yet proven
production ready not established
```

已有 PHASE03/04 代码是可复用的部分实现，不代表完整阶段完成。PHASE22 之前不得声明 Agentic GraphRAG 稳定优于 Baseline，不得把文档完成、最小闭环或局部 CI 绿灯写成系统完成。


Goal02 completed compatibility phrase: PHASE08 completed; PHASE11 completed; PHASE09 ready waits for implementation; PHASE12 ready waits for implementation.
