# PHASE08 Deterministic Single Controller Runtime

phase_id: PHASE08
status: ready
depends_on: PHASE04, PHASE05, PHASE06, PHASE07
owner: Module 06 Agent Core

## Phase 目标

实现最小但真实的 Single Controller：每个请求创建 TaskContract、GoalVersion、ExecutionContextSnapshot、Deterministic Single-Step PlanVersion，并通过正式 AgentRunGraph 和 StepExecutionGraph 完成执行、Checkpoint、Interrupt/Resume、Cancel、Deadline、Finalization 和 RunOutcome。此 Phase 不实现动态并行 DAG。

## Minimal Read Set

- `docs/modules/06-agent-core-planning-control.md`
- PHASE03 Agent Contracts
- PHASE04 PostgreSQL/Checkpointer
- PHASE05 Security
- PHASE06 Trace
- PHASE07 Model Gateway
- 当前 `agent/runtime/**` 与 completion/workspace path

## Current Anchors

```text
src/backend/zuno/agent/runtime/service.py
src/backend/zuno/agent/runtime/graph.py
src/backend/zuno/agent/runtime/state.py
src/backend/zuno/agent/runtime/store.py
src/backend/zuno/agent/runtime/checkpointer.py
src/backend/zuno/agent/durable_runtime.py
src/backend/zuno/api/services/completion.py
```

## Allowed Paths

```text
src/backend/zuno/agent/domain/**
src/backend/zuno/agent/application/**
src/backend/zuno/agent/runtime/**
src/backend/zuno/platform/database/agent/**
tests/agent/**
tests/integration/agent/**
tests/fault/agent/**
docs/evidence/**
```

## Forbidden Paths

- Multi-Agent Controller、direct answer bypass、动态 DAG 并行。
- Agent Core 直接调用 Provider SDK、Tool Adapter 或跨模块 Repository。
- Checkpoint 状态冒充 Domain Fact。

## Work Packages

### P08-T01 AgentRun, TaskContract and GoalVersion Domain
- Goal：实现 aggregate、version、state transition、tenant/workspace/principal/security/deadline/budget refs。
- Tests：create/authorize/start/cancel/fail/complete、illegal transition、optimistic version conflict。
- Acceptance：每个请求都有 TaskContract/GoalVersion，无 direct_answer shortcut。

### P08-T02 Deterministic PlanVersion and Step Definition
- Goal：实现不可变 PlanVersion、单 StepDefinition、inputs/outputs/acceptance/capability/model/evidence requirements。
- Tests：activation once、mutation reject、invalid dependency、unsupported executor、hash stability。
- Acceptance：简单任务也是 Plan，不绕过 PlanVersion。

### P08-T03 ExecutionContextSnapshot and Budget Ledger
- Goal：固定 security/context/model/capability/knowledge/answer policy refs 与 budget reservation/settlement。
- Tests：stale epoch、deadline、budget insufficient、snapshot immutability、resume same refs。
- Acceptance：上下文不是可变全局 dict。

### P08-T04 Fixed AgentRunGraph
- Goal：实现 initialize→authorize→context→plan→activate→execute→finalize 的固定 LangGraph 图。
- Tests：node routing、state schema、native checkpoint、interrupt、resume、cancel、deadline。
- Acceptance：产品主路径调用 compiled graph，不由手写 while loop 控制。

### P08-T05 Fixed StepExecutionGraph
- Goal：实现 load step→resolve input→security→model/action proposal→execute owner port→observation→evaluation→acceptance。
- Tests：success、blocked、denied、invalid proposal、retryable failure、abstain。
- Acceptance：每个 Action 有 Evaluation，每个 Step 有 Acceptance。

### P08-T06 Domain/Checkpoint Generation Reconciliation
- Goal：实现 committed generation、checkpoint generation、orphan run/dispatch detection 和安全 resume node。
- Tests：domain commit 后 checkpoint fail、checkpoint ahead、restart、duplicate resume、stale schema。
- Acceptance：不假装分布式原子提交。

### P08-T07 Interrupt, Signal, Cancel and Deadline
- Goal：实现多 Interrupt、signal journal、approval/user input/external wait、cancel precedence、deadline。
- Tests：duplicate signal、wrong run/epoch、deny、expire、cancel while waiting、resume after restart。
- Acceptance：Interrupt 是 Agent Core 控制事实，Approval Decision 仍归 Security。

### P08-T08 Legacy Runtime Shadow and Deterministic Cutover
- Goal：将真实产品请求 shadow 到新 Runtime，比对结果/trace；canary/default new/rollback。
- Tests：同一 request hash、rollback、new runtime unavailable、no double side effect。
- Acceptance：旧 GeneralAgent 仅临时回滚窗口；PHASE22 删除旧主路径、flag、legacy alias，不保留 Legacy Agent 目录。

## Phase 完成定义

- Deterministic Single-Step Plan 的真实 LangGraph 闭环通过。
- Restart/Interrupt/Resume/Cancel/Deadline/Generation Reconcile 有 Fault Test。
- Model 调用走 Gateway，Security/Trace/DB 接入。
- 动态 DAG 仍明确 Target，未伪装完成。

## Validation

```bash
git diff --check
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/agent tests/integration/agent tests/fault/agent -p no:cacheprovider
```
