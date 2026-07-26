# Goal03 Wave A Capability Planning Snapshot Evidence

status: partial_runtime_evidence
phase: PHASE14
commit_scope: Capability planning snapshot and selection outbox repair

本文只证明本次 Wave A 修复切片：Agent Core 的 `CapabilityPlan` 可以携带不可变 `CapabilityAvailabilitySnapshot` 与 `CapabilitySelectionResult` 引用；默认 Runtime strategy selector 会把同一组 capability decision refs 固定进 `ContextPack.task_state`，供 checkpoint/resume 后继续引用；Capability Repository 在新 selection 事实提交时，同一事务写入 PHASE04 统一 `infra_outbox_events`，供 Agent Core 按 outbox 幂等消费。

## 已证明

- `CapabilityPlan` 增加 `availability_snapshot_ref`、`selection_result_ref` 和 `selection_validity`。
- `StrategySelector` 在有候选 capability 时生成稳定 snapshot / selection refs，并把它们放入 Planner 输出。
- `StrategySelector` 的 planner 阶段只消费 `CapabilityRouteDecision` 中的 allowed tools、approval-required 和 planner exposure，不在 route 后二次遍历 legacy registry。
- Planner 生成的每个 `PlanStep` 都把同一组 `availability_snapshot_ref` / `selection_result_ref` 固定进 `input_refs`，并以 `selection_result_ref` 作为 `tool_policy_ref`；`plan_created` trace payload 同步暴露 snapshot / selection / validity，供执行层和 Closure Review 审计每一步来自同一个 capability decision。
- 默认 `RuntimeStrategySelector` 在 strategy select 后把 `capability_availability_snapshot_ref`、`capability_selection_result_ref`、`capability_selection_validity`、`capability_planner_exposure_ref` 和 exposure visibility 写入 `ContextPack.task_state`；`AgentRuntimeSnapshot` round-trip 后仍保留这些 refs，不只停留在瞬时内存字段。
- 默认 `RuntimeStrategySelector` 在 ContextPack 已有 `fixed_planning_snapshot` refs 时复用 pinned capability plan，不重新生成新的 selection；resume/replan 后 `PlanStep.input_refs` 和 `tool_policy_ref` 继续指向原 selection。
- 默认 `RuntimeDependencyFactory` 提供 `CapabilityPlanningRuntime`；`RuntimeStrategySelector` 通过 `deps.capability_runtime.select(...)` 获取 capability plan，不在默认 runtime 内直接遍历 legacy registry。Capability runtime / Repository 不可用时，selection fail closed 为 `blocked_capability_selection`，不会回退到 Planner 本地选择。
- `CapabilityRepository.record_selection` 只在新 `capability_selection_results` 插入成功时写入 `infra_outbox_events`。
- `CapabilityRepository.record_selection` 在 Repository 边界规范化 `candidate_summary` 与 `rejection_reason_codes`：同一候选集合即使输入顺序不同，也产生相同 `candidate_summary_hash` / `selection_hash`；selection outbox payload 携带 `candidate_summary.deterministic_candidate_order` 和去重排序后的 reason codes，供 Agent Core 审计多候选排序与拒绝原因。
- `infra_outbox_events.topic = capability.selection.committed`，payload 明确标记 `consumer_module = Agent Core`。
- 重复提交同一 selection 不重复创建 outbox 事件。
- `CapabilityService.consume_selection_event(...)` 会 claim `capability.selection.committed` outbox，写入 Agent Core consumer inbox，mark processed，并 complete outbox；这证明 selection fact 可以进入 Agent Core inbox，而不是停留在只读 projection。
- Capability 仍只产生 selection/projection，不执行 Tool，不拥有 Approval、Credential 或 ToolAttempt。

## 已运行验证

```powershell
python -m pytest -q tests/agent/runtime/test_runtime_state_contract.py tests/agent/test_planning_control_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/test_planning_control_runtime.py tests/capability/test_capability_skill_layer.py -p no:cacheprovider
python -m pytest -q tests/agent/test_planning_control_runtime.py tests/agent/test_shared_contract_freeze.py -p no:cacheprovider
python -m pytest -q tests/agent/test_planning_control_runtime.py -p no:cacheprovider
python tools/scripts/verify_capability_skill_target_protocols.py
git diff --check
alembic -c infra/db/alembic.ini heads
python -m compileall -q src/backend/zuno/agent src/backend/zuno/platform/database/capability
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_doc_boundaries.py
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase14_capability_blocks_unverified_skill_and_model_only_active_binding -p no:cacheprovider
```

结果：

```text
12 passed
17 passed
9 passed
8 passed
Capability / Skill target architecture verification passed.
20260725_37 (head)
3 passed
Repository structure verification passed.
Doc boundary verification passed.
12 passed
1 passed
```

Focused rerun after deterministic selection normalization:

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase14_capability_blocks_unverified_skill_and_model_only_active_binding -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python -m pytest -q tests/agent/test_capability_layer_surfaces.py tests/api/test_goal03_capability_route.py tests/capability/test_capability_skill_layer.py -p no:cacheprovider
python .agent/scripts/verify_doc_boundaries.py
git diff --check
```

结果：

```text
1 passed
13 passed
16 passed, 1 warning
Doc boundary verification passed.
git diff --check passed with LF/CRLF warnings only
```

Focused rerun after pinned capability refs reuse:

```powershell
python -m pytest -q tests/agent/runtime/test_runtime_state_contract.py tests/agent/test_planning_control_runtime.py -p no:cacheprovider
python -m pytest -q tests/capability/test_capability_skill_layer.py tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
python -m pytest -q tests/api/test_goal03_capability_route.py tests/repo/test_goal03_wave_a_migration_contract.py tests/agent/runtime/test_runtime_state_contract.py tests/agent/test_planning_control_runtime.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python tools/scripts/verify_capability_skill_target_protocols.py
python -m compileall -q src/backend/zuno/agent/planning.py src/backend/zuno/agent/runtime/planning/selector.py tests/agent/runtime/test_runtime_state_contract.py
```

结果：

```text
13 passed
14 passed
21 passed, 1 warning
13 passed
Capability / Skill target architecture verification passed.
compileall passed
```

Focused rerun after default capability runtime port:

```powershell
python -m pytest -q tests/agent/runtime/test_runtime_state_contract.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_state_contract.py tests/agent/test_planning_control_runtime.py tests/capability/test_capability_skill_layer.py tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python tools/scripts/verify_capability_skill_target_protocols.py
python -m compileall -q src/backend/zuno/capability/planning_runtime.py src/backend/zuno/agent/runtime/factory.py src/backend/zuno/agent/runtime/planning/selector.py tests/agent/runtime/test_runtime_state_contract.py tests/agent/runtime/test_runtime_dependency_factory.py
```

结果：

```text
13 passed
29 passed
13 passed
Capability / Skill target architecture verification passed.
compileall passed
```

## 历史失败指纹

以下失败只保留为历史环境指纹，已由 `docs/evidence/goal03-wave-a-postgres-integration-recovery.md` 的当前运行结果覆盖：

```text
command: python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
test name: migrated_postgres fixture
exception type: sqlalchemy.exc.OperationalError / psycopg.errors.ConnectionTimeout
first relevant stack frame: infra/db/alembic/env.py:94 run_migrations_online with connectable.connect()
environment signature: localhost:5432 TcpTestSucceeded=False; docker compose postgres startup failed because Docker daemon pipe dockerDesktopLinuxEngine was unavailable
retry count: 1
```

## 未证明

- 本证据不单独证明 PHASE14 的 Installation/Activation CAS、revocation propagation、ordered transition crash recovery、progressive loading budget 或 legacy registry cutover；这些需结合对应 evidence 做 Closure Gate 汇总。
- PHASE14 仍是 `in_progress`，不能据此关闭 Wave A Gate。
