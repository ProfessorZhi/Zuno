# PHASE17 Dynamic Plan DAG and Parallel Control

phase_id: PHASE17
status: planned
depends_on: PHASE08, PHASE12, PHASE16
owner: Module 06 Agent Core

## Phase 目标

在已验证的 Deterministic Runtime 上实现 Dynamic DAG Plan、ReadySet、安全并行 Admission、DispatchGroup/Item、Commit-before-Send、LangGraph Send、BranchResultRef、幂等 Reducer、JoinPolicy/JoinEvaluation、late result fencing 和 Replan Barrier。最终综合与 Replan 默认串行。

## Minimal Read Set

- `docs/modules/06-agent-core-planning-control.md`
- PHASE08 Agent Core Domain/Graph
- PHASE12 Knowledge Port
- PHASE16 Tool Effect semantics
- PHASE04 Lease/Fencing/Outbox
- PHASE06 Trace

## Current Anchors

```text
src/backend/zuno/agent/runtime/graph.py
runtime plan execution/routing/reflection/replan tests
any next_ready_step sequential executor
LangGraph version and Send usage
```

## Allowed Paths

```text
src/backend/zuno/agent/domain/plan/**
src/backend/zuno/agent/application/controller/**
src/backend/zuno/agent/runtime/**
src/backend/zuno/platform/database/agent/**
alembic/**
tests/agent/dag/**
tests/integration/agent/dag/**
tests/fault/agent/dag/**
docs/evidence/**
```

## Forbidden Paths

- 无 Resource/Security/Budget 检查就并行。
- Reducer 依赖到达顺序或覆盖旧结果。
- Replan 原地修改 active PlanVersion。
- Side Effect 分支在未知冲突下并行。

## Work Packages

### P17-T01 Dynamic Plan Proposal, Normalize and Validate
- Goal：实现 step/dependency/input/output/acceptance/capability/evidence/resource/side-effect metadata 和 DAG validation/repair。
- Tests：cycle、missing dependency、unbound input、huge step、unsupported executor、invalid side-effect parallelism。
- Acceptance：Planner proposal 通过 deterministic validator 才可激活。

### P17-T02 Immutable PlanVersion Activation and Supersession
- Goal：实现 version lineage、activation CAS、active pointer、superseded/cancelled state。
- Tests：concurrent activation、mutation reject、resume old version、replan lineage、rollback forbidden rules。
- Acceptance：active 后不可变。

### P17-T03 ReadySet and Admission Controller
- Goal：根据 dependencies、inputs、resource claims、side effects、budget、quota、security、capacity 算 ReadySet。
- Tests：data dependency、same resource write、exclusive resource、budget insufficient、stale epoch、quota wait。
- Acceptance：最大化安全并行，不是最大化任务数。

### P17-T04 Dispatch Transaction and Commit-before-Send
- Goal：同事务提交 DispatchGroup/Item、StepRun、reservations、epoch/fencing、Outbox，提交后才 Send。
- Tests：crash before/after commit、outbox duplicate、send unavailable、cancel before send。
- Acceptance：无未提交 Step 被 worker 执行。

### P17-T05 LangGraph Send and BranchResultRef
- Goal：动态发送独立 branch，返回 immutable result ref、observation/effect refs、version/epoch/fencing/hash。
- Tests：parallel success、partial failure、late result、duplicate result、worker loss、cancel。
- Acceptance：大 payload 用 ObjectRef；分支不直接改共享可变 state。

### P17-T06 Idempotent Reducer and JoinPolicy
- Goal：按 result identity/hash 去重，顺序无关 reduce；实现 ALL/QUORUM/BEST_EFFORT/FAIL_FAST 等受控 Join。
- Tests：permutation property、duplicate conflict、partial fail、quorum、discarded work、critical branch。
- Acceptance：Reducer 拒绝旧 PlanVersion/epoch/fencing。

### P17-T07 Join Evaluation, Reflection Trigger and ControlDecision
- Goal：评估 branch coverage/conflict/failure/budget，触发 continue/retry/wait/replan/finalize；仅必要时模型 Reflection。
- Tests：evidence conflict、critical partial failure、all optional fail、reflection timeout、deterministic fallback。
- Acceptance：Join 不直接改 Knowledge/Tool 事实。

### P17-T08 Replan Barrier and Parallel Recovery
- Goal：停止新 dispatch、处理/取消 in-flight、记录 late-result policy、创建新 PlanVersion、恢复 ReadySet。
- Tests：replan with active branches、irreversible side effect pending、late result after barrier、duplicate replan、restart。
- Acceptance：Replan 与 Retry 分开；新版本激活前 Barrier 完成或明确 blocked。

## Phase 完成定义

- Dynamic DAG、ReadySet、Commit-before-Send、Send、Reducer、Join、Replan 真实运行。
- 并行/晚到/重复/部分失败/重启 Fault Test 通过。
- Sequential executor 不再是默认动态计划实现；旧路径 PHASE22 删除。

## Validation

```bash
git diff --check
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/agent/dag tests/integration/agent/dag tests/fault/agent/dag -p no:cacheprovider
```
