# Goal03 Wave A Capability Planning Snapshot Evidence

status: partial_runtime_evidence
phase: PHASE14
commit_scope: Capability planning snapshot and selection outbox repair

本文只证明本次 Wave A 修复切片：Agent Core 的 `CapabilityPlan` 可以携带不可变 `CapabilityAvailabilitySnapshot` 与 `CapabilitySelectionResult` 引用；Capability Repository 在新 selection 事实提交时，同一事务写入 PHASE04 统一 `infra_outbox_events`，供 Agent Core 按 outbox 幂等消费。

## 已证明

- `CapabilityPlan` 增加 `availability_snapshot_ref`、`selection_result_ref` 和 `selection_validity`。
- `StrategySelector` 在有候选 capability 时生成稳定 snapshot / selection refs，并把它们放入 Planner 输出。
- `CapabilityRepository.record_selection` 只在新 `capability_selection_results` 插入成功时写入 `infra_outbox_events`。
- `infra_outbox_events.topic = capability.selection.committed`，payload 明确标记 `consumer_module = Agent Core`。
- 重复提交同一 selection 不重复创建 outbox 事件。
- Capability 仍只产生 selection/projection，不执行 Tool，不拥有 Approval、Credential 或 ToolAttempt。

## 已运行验证

```powershell
python -m pytest -q tests/agent/test_planning_control_runtime.py tests/agent/test_shared_contract_freeze.py -p no:cacheprovider
python tools/scripts/verify_capability_skill_target_protocols.py
git diff --check
alembic -c infra/db/alembic.ini heads
python -m compileall -q src/backend/zuno/agent src/backend/zuno/platform/database/capability
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_doc_boundaries.py
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
```

结果：

```text
9 passed
Capability / Skill target architecture verification passed.
20260725_37 (head)
3 passed
Repository structure verification passed.
Doc boundary verification passed.
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

- PHASE14 的 Installation/Activation CAS、revocation propagation、supply-chain crash recovery、progressive loading budget 和 legacy registry full cutover 尚未完成。
- PHASE14 仍是 `in_progress`，不能据此关闭 Wave A Gate。
