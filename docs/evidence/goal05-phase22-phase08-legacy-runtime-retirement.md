# PHASE22 Phase08 Legacy Runtime Retirement

phase_id: PHASE22
work_package: PHASE22-RETIRE-PHASE08-LEGACY-CUTOVER
worker: deepseek-legacy-runtime
agent_name: DeepSeek-Legacy-Runtime
execution_client: Claude Code
provider: DeepSeek
base_sha: 83c1bbd0689d1b2b3b4ffd7f3983de813da11ebb
# Runtime Subject Head: the commit at which the Phase08 *execution*
# dual-path retirement landed in source. This is NOT the Evidence
# Revision SHA — see `evidence_revision` below.
runtime_subject_head_sha: a83f0c53c6c6e9058138736965a218e006e6ff95
truth_boundary: PHASE08_EXECUTION_DUAL_PATH_RETIRED
production_ready: false
pr: https://github.com/ProfessorZhi/Zuno/pull/124
pr_v1_record: https://github.com/ProfessorZhi/Zuno/pull/122 (closed; trailer gate)  # noqa: E501
# Evidence Revision is intentionally NOT recorded inside this file.
# Any commit that mutates this Evidence would change its own content,
# so a self-referenced "final SHA" inside the file would be a
# circular reference. The Evidence Revision SHA is recorded at the
# PR Body / GitHub commit history instead.
evidence_revision: see PR #124 body (recorded externally to avoid self-reference)
ci_run: "30909803998" (PHASE22 Contract Verification; conclusion success; against runtime_subject_head_sha a83f0c53... in the same branch as this Evidence file)
ci_jobs:
  - "Repository Gates & Static Checks: success"
  - "PHASE22 Focused Test Suite: success"
  - "Generate Verification Evidence & Summary: success"

## Summary

退休了 `Phase08CutoverController` 中仍然活跃的 Legacy Runtime、rollback/shadow/canary
双路径和异常自动 fallback。Rollback Window 结束后,生产路径只有 Single Controller
Product Runtime → 固定 `AgentRunGraph` / `StepExecutionGraph` → `RunOutcome`。

## Truth Boundary (narrowed)

This work package retires ONLY the Phase08 *execution* dual-path
surfaces the spec mandates. It does NOT declare the whole repository
CLEAN or PHASE22 Completed.

Retired here:
- Phase08CutoverController execution dual-path
- LegacyRunner type alias
- _run_legacy, _fallback_to_legacy methods
- rollback / shadow / canary mode dispatch in Phase08 Runtime handle()
- WorkspaceTaskRuntimeService.configure_phase08_cutover,
  _run_phase08_cutover_for_task, and the _phase08_cutover_* task
  lifecycle state

Kept (not retired here; other work packages own these):
- CutoverMode type / product-layer command-kind Contract
- completion.py and product command service fail-closed input
  validation
- Historical audit ledger (agent_cutover_audit_events)
- SideEffectLedger / PostgresPhase08CutoverLedger (canonical
  persistence)
- Product protocol compatibility surfaces that do not route
  through the Phase08 Runtime execution dual-path

Status string (this PR): PHASE08_EXECUTION_DUAL_PATH_RETIRED.
Forbidden status strings: ALL_CUTOVER_CONTRACTS_REMOVED,
PHASE22_COMPLETED, PRODUCTION_READY.

## Before Call Chain

```text
Composition Root (main.py)
  (phase08 cutover was never configured in production; tests configured it)
WorkspaceTaskRuntimeService.create_task
  -> _start_unified_runtime_for_task            # canonical (kept)
  -> _run_phase08_cutover_for_task              # REMOVED
       -> Phase08CutoverController.handle(mode)
            -> rollback: legacy_runner(allow_side_effect=True)
            -> shadow:   legacy_runner(primary, allow_side_effect=True)
                         + new runtime shadow (allow_side_effect=False)
            -> canary:   new runtime (allow_side_effect=True)
                         + legacy_runner shadow (allow_side_effect=False)
            -> new_default: new runtime; on exception
                 -> _fallback_to_legacy(allow_side_effect=True)
                      (fallback_allowed=True audit when no side-effect claim)
```

## After Call Chain

```text
Product/API/Worker
  -> WorkspaceTaskRuntimeService.create_task
       -> SingleControllerDurableRuntime (durable task surface)
       -> UnifiedAgentRuntimeService (canonical runtime, kept)
       -> Fixed AgentRunGraph / Fixed StepExecutionGraph -> RunOutcome
```

`Phase08CutoverController`、`LegacyRunner`、`_fallback_to_legacy`、`_run_legacy` 与
`WorkspaceTaskRuntimeService.configure_phase08_cutover` / `_run_phase08_cutover_for_task`
均已移除。唯一幸存符号是 fail-closed `Phase08RetiredController`(不持有 mode、不持有
runner、不持有 runtime,`handle()` 恒抛 `Phase08CutoverError`)。

## Removed Modes

- `rollback`:拒绝(不存在符号;`Phase08RetiredController(mode="rollback")` 抛 `TypeError`)。
- `shadow`(legacy-primary):拒绝/不存在。
- `canary`(legacy-shadow):拒绝/不存在。
- `new_default` 上的 `_fallback_to_legacy`:删除。
- `LegacyRunner` 类型:删除,package export 中不存在。

## Failure Semantics

新 Runtime 失败时(`classify_phase08_final_state`,canonical `Phase08RunService.start`
结果分类):

- `EFFECT_COMMITTED` — 已有 side-effect claim(`effect_claim_ref`);不得执行第二 Runtime;
  返回原事实或进入 Reconciliation。
- `COMPLETED` — finalized 且带 outcome;返回原事实。
- `FAILED/BLOCKED` — 副作用前失败/阻塞(security / budget 拒绝、deadline、cancelled、
  abstained、interrupted);可根据原计划 Retry,不执行 Legacy。
- `RECONCILIATION_REQUIRED` — 无已识别终端形态(未知副作用状态);Operator/Coordinator
  确认(`reconcile_generations` + `agent_reconciliation_findings`),不盲目 Retry。

## Side-effect Semantics

- Side-effect claim 由持久化 ledger(`agent_effect_claims` / `SideEffectLedger`)幂等保护:
  同一 idempotency key 的重复 claim 返回 duplicate / 抛 `Phase08SideEffectClaimError`。
- 副作用已提交后,任何第二 Runtime 执行都被阻止(claim 幂等 + retired surface 拒绝)。
- Shadow domain-commit suppression(`shadow_domain_commit_suppressed`)保留为 canonical
  图能力(不写 `agent_final_gate_receipts` / `agent_run_outcomes` / `agent_effect_claims`),
  不再是 cutover controller 功能。

## Retry/Reconciliation Semantics

- 重试不重复 Plan:`active_plan_version_id` 由 `run_id` 确定性派生,每次 attempt 仅创建
  一个 plan version。
- 重试不重复 Side Effect:ledger 幂等,重复 claim 被拒绝。
- Unknown effect → `reconcile_generations`(domain_ahead / checkpoint_ahead / orphan_* /
  stale_schema)→ `record_reconciliation_finding`(持久化、幂等)→ operator 确认。
- `record_cutover_audit_event` 持久化 API 保留(`agent_cutover_audit_events`),生产不再
  写入 `fallback_allowed=true`;测试 fixture 仅记录 `fallback_allowed=false`。

## Security/Budget Propagation

- Security denial:canonical `_authorize_run` → `stale_security_epoch` / `security-denied`
  → `failed`,直接传播,无 fallback。
- Budget denial:canonical `_plan_run` → plan 不创建 → 副作用前失败,直接传播,无 fallback。
- Product 层 security block(`input_security_block` 等)直接 fail task,无 fallback。

## Tests

- `tests/agent/runtime/test_phase08_cutover_shadow.py` — 旧 shadow/rollback/canary 成功
  测试转换为 retired fail-closed 测试(9 项)。
- `tests/agent/runtime/test_phase08_cutover_retired.py` — 新语义与静态 gate 测试
  (14 项):security/budget 拒绝不 fallback、effect committed 阻塞第二 Runtime、
  unknown effect 进入 reconciliation、重试不重复 plan/side effect、env var 无法恢复
  旧路径、restart 不选 Legacy、package 无 LegacyRunner export、全仓无
  `_fallback_to_legacy` 生产调用、audit 无 `fallback_allowed=True`、Product API /
  Queue Worker 只到 canonical runtime。
- `tests/integration/agent/test_phase08_runtime_closure_persistence.py` — 3 个 controller
  测试转换为 retired fail-closed + 持久化 ledger 测试;shadow suppression 测试改为
  直接图能力测试;repo 级持久化/幂等测试保留。
- `tests/api/test_workspace_task_runtime.py` — 3 个 cutover 测试转换为 canonical-only /
  retired 断言。

## Commit Attribution Note (v1 → v2)

- v1 分支 `claude/deepseek-phase22-retire-phase08-legacy-cutover`(commit 6bc05707,
  ab11e7d2)的 Trailer 使用 `Agent-Mode: worker`;仓库 commit-attribution gate
  (`verify_agent_commit_attribution.py`)仅允许
  `{Standard, Codex, Expert-Team, Goal, Human, Docs-Maintenance, Standard-Conversation}`。
- 按 Coordinator 对 PR #119 的 v2 先例,保留 v1 分支/PR #122(closed)作审计记录,
  从最新 `origin/main` 重建 `claude/deepseek-phase22-retire-phase08-legacy-cutover-v2`
  分支,内容一致,Trailer 改为 `Agent-Mode: Standard`。未使用 amend/rebase/force-push/
  cherry-pick;文件经 `git restore --source` 从 v1 commit 取回。
- `verify_agent_commit_attribution.py --base origin/main --head HEAD` 本地与 CI 均通过。

## Commands

```powershell
git fetch origin --prune
git rev-parse origin/main
git checkout -b claude/deepseek-phase22-retire-phase08-legacy-cutover origin/main
git diff --check
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python -m pytest -q tests/agent/runtime/test_phase08_cutover_shadow.py tests/agent/runtime/test_phase08_cutover_retired.py -p no:cacheprovider
python -m pytest -q tests/api/test_completion_unified_runtime.py -p no:cacheprovider
python -m pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
```

## Exit Codes

- `git diff --check` — 0(仅有 LF→CRLF 提示)。
- `verify_phase22_cleanup_boundary.py` — 0(passed)。
- `verify_repo_structure.py` — 0(passed)。
- `verify_agent_system.py` — 0(passed)。
- `test_phase08_cutover_shadow.py` + `test_phase08_cutover_retired.py` — 23 passed。
- `test_phase08_fixed_run_graph.py` + `test_phase08_step_graph.py` +
  `test_phase08_reconciliation_and_signals.py` — 10 passed(无回归)。
- `test_completion_unified_runtime.py` — 12 passed。
- `test_workspace_task_runtime.py` — 17 passed, 3 failed:
  - `test_workspace_task_runtime_runs_read_only_tool_and_streams_audit_events`
  - `test_workspace_task_runtime_requires_tool_approval_then_executes_brokered_tool`
  - `test_workspace_task_runtime_emits_security_approval_facts_from_active_tool_path`
  - 失败根因:Tool Security Approval 路径(`capability/runtime.py:627/739`)连接
    PostgreSQL `localhost:5432` 超时——本环境无本地 PostgreSQL,pre-existing
    环境依赖,与本次 phase08 修改无关(该路径未被我修改的任何代码行触及)。

## Tests Not Run

- `tools/scripts/verify_current_program.py` — 在此环境 pre-existing 失败
  ("No module named 'zuno'",脚本未配置 `src/backend` 到 sys.path;干净 base 同样失败),
  与本次修改无关。
- `tests/integration/agent/test_phase08_runtime_closure_persistence.py` — 需要本地
  PostgreSQL(`ZUNO_TEST_POSTGRES_URL`,默认 localhost:5432),本环境未运行;
  修改后文件通过语法/导入检查。
- 全仓 pytest 未运行。

## Remaining Gaps

- 本工作包不声明 PHASE22 完成,不声明 Production Ready。
- Product surface cutover(`completion.py` / `product/command_service.py` 的
  `cutover_mode` command-kind 校验)属于其他工作包所有权,保留;其 `rollback` 已
  fail-closed,非 phase08 legacy runtime 双路径。
- canonical 图 `_plan_run` budget-blocked 分支被后续 `validate_plan` 覆写为
  `plan_validation_failed`(pre-existing 图行为,不在本工作包范围)。
- `agent_cutover_audit_events` 表与 `record_cutover_audit_event` repo API 保留
  (历史 ledger);`PostgresPhase08CutoverLedger` 保留为持久化 effect/audit ledger。
