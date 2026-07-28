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

## P17-T01 Dynamic DAG Proposal and Validator Slice

状态：completed-for-current-slice，未构成 PHASE17 closure。

本轮新增 `src/backend/zuno/agent/runtime/planning/dynamic_dag.py`，建立 PHASE17 动态 DAG proposal 的第一组正式运行合同：

- `DynamicPlanProposal` 绑定 `plan_id`、`goal_version_id`、`planner_ref`、`join_policy` 和 step 列表；
- `DynamicPlanStep` 显式表达 objective、executor、dependency rule、activation condition、input binding、output contract、acceptance、evidence、capability、resource claim、side-effect class、budget 和 deadline；
- `DynamicPlanValidator` 覆盖空 plan、step 数上限、重复 step、unsupported executor、空 goal、缺 acceptance、缺 output contract、自依赖、missing dependency、cycle、unbound input、missing output、并行 resource write conflict 和无 resource scope 的并行 side-effect；
- `DynamicPlanRepairer` 只做确定性修复：补 acceptance criteria 和 output contract，不激活 PlanVersion，不调度并行分支，不绕过后续 ReadySet / Admission / Dispatch gate。

验证：

```text
python -m pytest tests\agent\dag\test_phase17_dynamic_dag_validator.py -q -p no:cacheprovider --tb=short
6 passed
```

```text
python -m py_compile src\backend\zuno\agent\runtime\planning\dynamic_dag.py src\backend\zuno\agent\runtime\planning\__init__.py tests\agent\dag\test_phase17_dynamic_dag_validator.py
passed
```

边界：

- 该切片只完成 P17-T01 的 proposal / normalize / validate / deterministic repair 起点；
- 尚未实现 ReadySet、Admission、DispatchGroup、Commit-before-Send、LangGraph Send、Reducer、JoinEvaluation 或 Replan Barrier；
- PHASE17 仍为 `in_progress`，不能写 completed。

## P17-T02 Dynamic PlanVersion Domain and Supersession Slice

状态：completed-for-current-slice，未构成 PHASE17 closure。

本轮扩展 `src/backend/zuno/agent/domain/task_contracts.py`，把 PHASE08 只支持 `DETERMINISTIC_SINGLE_STEP` 的 `PlanVersion` 领域边界打开为可同时表达：

- `PlanKind.DETERMINISTIC_SINGLE_STEP`：保留原单步计划不变量；
- `PlanKind.DYNAMIC_DAG`：新增 `DynamicStepDefinition`，显式保存 dynamic step id、dependency ids、dependency rule、activation condition、resource claim refs、join policy ref、executor、acceptance、evidence、budget 和 deadline；
- 动态 PlanVersion 创建时执行 step id 唯一、step_no 唯一、依赖存在和 DAG cycle fail-closed；
- `PlanVersion.activate(...)` 继续使用 optimistic CAS，只允许 `DRAFT -> ACTIVE`；
- `PlanVersion.supersede(...)` 只允许 `ACTIVE -> SUPERSEDED`，并通过 expected aggregate version 防止 stale supersession；
- active PlanVersion 仍通过 `reject_mutation()` 明确禁止原地修改，Replan 必须创建新 PlanVersion。

验证：

```text
python -m pytest tests\agent\test_phase08_plan_version_domain.py tests\agent\dag\test_phase17_dynamic_plan_version_domain.py -q -p no:cacheprovider --tb=short
10 passed
```

```text
python -m py_compile src\backend\zuno\agent\domain\task_contracts.py src\backend\zuno\agent\domain\__init__.py tests\agent\dag\test_phase17_dynamic_plan_version_domain.py
passed
```

边界：

- 该切片只完成动态 PlanVersion 领域模型、激活 CAS 和 supersession 领域入口；
- 尚未把动态 PlanVersion 持久化 schema 扩展为完整 DAG step metadata，尚未实现 ReadySet / Admission / DispatchGroup / Commit-before-Send；
- PHASE17 仍为 `in_progress`，不能写 completed。

## P17-T03 ReadySet and Admission Domain Slice

状态：completed-for-current-slice，未构成 PHASE17 closure。

本轮新增 `src/backend/zuno/agent/runtime/planning/admission.py`，在 DispatchGroup / Send 之前建立可验证的安全并行闸门：

- `ReadySetBuilder` 根据动态 DAG dependency rule 和 step run state 计算 ready / waiting / terminal step；
- ReadySet 覆盖 `ALL_SUCCESS`、`ALL_TERMINAL`、`ANY_SUCCESS`、`OPTIONAL_INPUT` 和 `QUORUM` 的确定性判断；
- `AdmissionContext` 绑定 `plan_id`、`plan_version_id`、security epoch、authorized capabilities、budget、quota、capacity 和 in-flight resource claims；
- `AdmissionController` 对 ready steps 按 proposal 顺序执行 Resource / Security / Budget / Quota / Capacity gate；
- admission 结果区分 `ADMITTED`、`DEFERRED` 和 `REJECTED`，stale security epoch 与 unauthorized capability fail closed；
- admission 只生成可进入后续 dispatch 的决定和预算保留量，不发送 LangGraph worker，不写 StepRun 成功，不冒充领域执行完成。

验证：

```text
python -m pytest tests\agent\dag\test_phase17_readyset_admission.py -q -p no:cacheprovider --tb=short
4 passed
```

```text
python -m py_compile src\backend\zuno\agent\runtime\planning\admission.py src\backend\zuno\agent\runtime\planning\__init__.py tests\agent\dag\test_phase17_readyset_admission.py
passed
```

边界：

- 该切片只完成 ReadySet 和 Admission 的 runtime planning gate；
- 尚未实现 DispatchGroup、DispatchItem、StepRun、Commit-before-Send、LangGraph Send、BranchResultRef、Reducer、JoinEvaluation 或 Replan Barrier；
- PHASE17 仍为 `in_progress`，不能写 completed。

## P17-T04 Dispatch Commit-before-Send Domain Slice

状态：completed-for-current-slice，未构成 PHASE17 closure。

本轮新增 `src/backend/zuno/agent/runtime/planning/dispatch.py`，把 Admission 结果转成可持久化的并行 dispatch 领域事实：

- `DispatchGroup` 绑定 run、plan、PlanVersion、execution epoch、admitted step ids，并带 `committed_before_send` 标记；
- `DispatchItem` 绑定 DispatchGroup、StepRun、dynamic step、send idempotency key 和 outbox event id；
- `StepRun` 以 `QUEUED` 状态创建，绑定 PlanVersion、dynamic step、execution epoch、attempt 和 step hash；
- `DispatchOutboxMessage` 只表达待发送请求，topic 固定为 `agent.dynamic_step.dispatch.requested`；
- `DispatchCommitBuilder` 只消费 admitted steps，确定性生成 DispatchGroup / DispatchItem / StepRun / OutboxMessage，并要求所有 outbox payload 都引用已提交 StepRun；
- 该切片证明 commit-before-send 的领域 payload，不发送 LangGraph worker，不创建 BranchResultRef，不把 queued StepRun 冒充执行成功。

验证：

```text
python -m pytest tests\agent\dag\test_phase17_dispatch_commit.py -q -p no:cacheprovider --tb=short
3 passed
```

```text
python -m py_compile src\backend\zuno\agent\runtime\planning\dispatch.py src\backend\zuno\agent\runtime\planning\__init__.py tests\agent\dag\test_phase17_dispatch_commit.py
passed
```

边界：

- 该切片只完成 DispatchGroup / DispatchItem / StepRun / OutboxMessage 的领域提交 payload；
- 尚未完成 PostgreSQL append-only migration、Repository/UoW 同事务提交、真实 LangGraph Send、BranchResultRef、Reducer、JoinEvaluation 或 Replan Barrier；
- PHASE17 仍为 `in_progress`，不能写 completed。

## P17-T05 Dispatch PostgreSQL Persistence Slice

状态：completed-for-current-slice，未构成 PHASE17 closure。

本轮新增 append-only migration `infra/db/alembic/versions/20260728_46_phase17_dynamic_dispatch.py`，并扩展 `src/backend/zuno/platform/database/agent/domain.py`：

- 放开 `agent_plan_versions.plan_kind`，允许 `DYNAMIC_DAG`；
- 放开 `agent_plan_step_definitions.step_no = 1`，并新增 dynamic step id、dependency ids、dependency rule、activation condition、resource claim refs 和 join policy ref；
- 新增 `agent_dispatch_groups`、`agent_step_runs`、`agent_dispatch_items`；
- `AgentDomainRepository.record_dispatch_commit(...)` 在一个 UoW 事务中写 DispatchGroup、StepRun、infra outbox 和 DispatchItem；
- outbox 使用 `InfrastructureRepository.enqueue_outbox(...)`，topic 为 `agent.dynamic_step.dispatch.requested`，ordering key 为 DispatchGroup；
- integration test 查询数据库证明 outbox payload 的 `step_run_id` 已对应已提交 `agent_step_runs`，且 `commit_required_before_send = true`。

验证：

```text
python -m py_compile infra\db\alembic\versions\20260728_46_phase17_dynamic_dispatch.py src\backend\zuno\platform\database\agent\domain.py tests\integration\agent\test_phase17_dispatch_commit_persistence.py
passed
```

```text
python -m pytest tests\integration\agent\test_phase17_dispatch_commit_persistence.py -q -p no:cacheprovider --tb=short
1 passed
```

边界：

- 该切片完成 dispatch commit-before-send 的 PostgreSQL migration 和 Repository/UoW 同事务提交；
- 尚未实现真实 LangGraph Send worker、BranchResultRef、late-result fencing、Reducer、JoinEvaluation、Replan Barrier 或 restart parallel recovery；
- PHASE17 仍为 `in_progress`，不能写 completed。

## P17-T06 BranchResultRef and Late-result Fencing Slice

状态：completed-for-current-slice，未构成 PHASE17 closure。

本轮新增 `src/backend/zuno/agent/runtime/planning/branch_result.py`，建立 LangGraph Send worker 返回后的结果入口边界：

- `BranchResultSubmission` 表达 worker 提交的 step_run、PlanVersion、dynamic step、execution epoch、attempt、step hash、object result ref 和 producer；
- `BranchResultFencer` 只接受当前 active PlanVersion、当前 execution epoch、匹配 StepRun step hash、非终态 StepRun 和 `object://` result ref；
- stale PlanVersion、stale execution epoch、stale step hash、obsolete/terminal StepRun 和 inline payload 全部拒绝；
- `BranchResultRef` 是不可变结果引用，保存 object ref 与 result hash，`ref_hash` 防止结果引用被原地篡改；
- 该切片只处理 Send result ingress 与 late-result fencing，不执行 reducer，不推进 join，不写 StepRun success。

验证：

```text
python -m pytest tests\agent\dag\test_phase17_branch_result_fencing.py -q -p no:cacheprovider --tb=short
6 passed
```

```text
python -m py_compile src\backend\zuno\agent\runtime\planning\branch_result.py src\backend\zuno\agent\runtime\planning\__init__.py tests\agent\dag\test_phase17_branch_result_fencing.py
passed
```

边界：

- 该切片完成 BranchResultRef 和 late-result fencing 的领域判断；
- 尚未实现真实 LangGraph Send worker、BranchResultRef PostgreSQL persistence、Reducer、JoinEvaluation、Replan Barrier 或 restart parallel recovery；
- PHASE17 仍为 `in_progress`，不能写 completed。

## P17-T07 BranchResultRef PostgreSQL Persistence Slice

状态：completed-for-current-slice，未构成 PHASE17 closure。

本轮新增 append-only migration `infra/db/alembic/versions/20260728_47_phase17_branch_results.py`，并扩展 `src/backend/zuno/platform/database/agent/domain.py`：

- 新增 `agent_branch_result_refs`，外键绑定 `agent_step_runs`、`agent_domain_runs` 和 `agent_plan_versions`；
- 表约束要求 positive execution epoch / attempt、`object://` result ref、canonical result hash 和 ref hash；
- `AgentDomainRepository.record_branch_result_ref(...)` 只记录已经由 `BranchResultFencer` 接受的 immutable `BranchResultRef`；
- 重复相同 `branch_result_id` + `ref_hash` 返回 `duplicate:ACCEPTED`，不同 ref hash 视为冲突；
- integration test 证明 accepted BranchResultRef 落库，重复提交幂等，stale PlanVersion result 不产生可记录 BranchResultRef。

验证：

```text
python -m py_compile infra\db\alembic\versions\20260728_47_phase17_branch_results.py src\backend\zuno\platform\database\agent\domain.py tests\integration\agent\test_phase17_dispatch_commit_persistence.py
passed
```

```text
python -m pytest tests\integration\agent\test_phase17_dispatch_commit_persistence.py -q -p no:cacheprovider --tb=short
2 passed
```

边界：

- 该切片完成 BranchResultRef PostgreSQL persistence；
- 尚未实现真实 LangGraph Send worker、Reducer、JoinEvaluation、Replan Barrier 或 restart parallel recovery；
- PHASE17 仍为 `in_progress`，不能写 completed。
