# Goal04 PHASE17 Startup Audit

status: startup_frozen_gap_list
phase_id: PHASE17
branch: codex/goal04-phase17-dynamic-plan-dag
base_branch: main
base_main_sha: d78426171df0591643af12549a36214a24734f7c
phase16_merge_sha: d78426171df0591643af12549a36214a24734f7c
alembic_head_at_start: 20260727_45
production_readiness: not_established

## 启动结论

PHASE17 Dynamic Plan DAG and Parallel Control 已按 Goal04 依赖规则从 PR B 合并后的最新 `main` 启动。PHASE16 已完成并合并；PHASE18 和 PHASE19 仍不得启动。当前文件只冻结 PHASE17 Gap List，不声明 PHASE17 completed。

## 已读取事实源

- Goal objective：`C:\Users\Administrator\.codex\attachments\32391a4a-41c5-471b-94e4-baaf7f820141\goal-objective.md`
- PHASE17 Program：`.agent/programs/PHASE17_dynamic-plan-dag-parallel-control.md`
- Agent Core Target：`docs/modules/06-agent-core-planning-control.md`
- 总架构：`docs/architecture/architecture.md`
- Current / Readiness：`docs/status/production-readiness.md`
- Current Program：`.agent/programs/current.md`
- Code Map / Routing：`.agent/references/code-map.md`、`.agent/references/task-routing.md`
- Agent Core verifier：`tools/scripts/verify_agent_core_target_protocols.py`

## 启动检查

```text
git status -sb
## codex/goal04-phase17-dynamic-plan-dag...origin/main
```

```text
git rev-parse HEAD
d78426171df0591643af12549a36214a24734f7c
```

```text
git rev-parse origin/main
d78426171df0591643af12549a36214a24734f7c
```

```text
alembic -c infra\db\alembic.ini heads
20260727_45 (head)
```

## Current Code Findings

- `src/backend/zuno/agent/domain/task_contracts.py` 和 `src/backend/zuno/platform/database/agent/domain.py` 已有 PHASE08 的 `PlanVersion` / single-step activation / immutable active guard。
- `src/backend/zuno/agent/runtime/planning/executor.py` 仍是顺序 `next_ready_step(...)` 执行器，不是 PHASE17 ReadySet / Admission / DispatchGroup 实现。
- `src/backend/zuno/agent/runtime/nodes/core.py` 仍从 `_PLAN_EXECUTOR.next_ready_step(state.plan_state)` 选择单个 Step。
- `src/backend/zuno/agent/runtime_batch.py` 有 batch-level `BranchResultRef` / `PlanVersionRecord` / generation 检查，但不是默认运行路径。
- `tests/agent/dag`、`tests/integration/agent/dag`、`tests/fault/agent/dag` 当前不存在。
- `src/backend/zuno/agent/domain/plan` 和 `src/backend/zuno/agent/application/controller` 当前不存在。

## Frozen Gap List

### P17-G01 Dynamic Plan Proposal / Validate

当前只有 Deterministic Single-step PlanVersion 和 batch contract。缺少动态 DAG step schema、dependency/input/output/resource/side-effect metadata、deterministic validator/repair，以及 cycle、missing dependency、unbound input、unsupported executor 和 side-effect parallelism fail-closed 测试。

### P17-G02 Immutable Activation / Supersession

已有 PHASE08 active PlanVersion 不可变 guard，但缺少动态 PlanVersion lineage、activation CAS、supersession/cancellation、resume old version、replan lineage 和 rollback-forbidden 测试。

### P17-G03 ReadySet / Admission

默认 runtime 仍按 `next_ready_step` 取一个步骤。缺少 dependency/input/resource/security/budget/quota/capacity admission、same-resource write conflict、side-effect conflict 和 stale epoch gate。

### P17-G04 Dispatch Transaction / Commit-before-Send

缺少 Agent Core `DispatchGroup`、`DispatchItem`、`StepRun` reservation/outbox 同事务持久化，以及 commit 后才 LangGraph Send 的默认路径。缺少 crash before/after commit、send unavailable 和 duplicate outbox 测试。

### P17-G05 LangGraph Send / BranchResultRef

缺少默认 runtime 动态 Send worker、immutable BranchResultRef、ObjectRef 大 payload、execution epoch/fencing/hash 校验、worker loss、duplicate result 和 cancel 测试。

### P17-G06 Idempotent Reducer / JoinPolicy

缺少顺序无关 reducer、result identity/hash 去重、ALL/QUORUM/BEST_EFFORT/FAIL_FAST JoinPolicy、partial fail、quorum、discarded work 和 stale PlanVersion/epoch/fencing rejection。

### P17-G07 Join Evaluation / Reflection Trigger

缺少 branch coverage/conflict/failure/budget join evaluation、conditional reflection trigger、deterministic fallback 和 continue/retry/wait/replan/finalize ControlDecision。

### P17-G08 Replan Barrier / Parallel Recovery

缺少停止新 dispatch、in-flight cancel/drain/non-interruptible side-effect policy、late-result policy、新 PlanVersion 创建激活和 restart 后 ReadySet 恢复。当前不得把 sequential replan helper 冒充 PHASE17 barrier。

## 下一步执行边界

优先从 P17-G01 / P17-G03 开始，建立可执行 DAG proposal + validator + ReadySet admission 的最小正式领域模型和 focused tests；不得先接默认并行 dispatch，直到资源、安全、预算和 side-effect conflict gate 可验证。
