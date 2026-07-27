# PHASE16 Tool Side Effect and Reconciliation

phase_id: PHASE16
status: in_progress
depends_on: PHASE05, PHASE06, PHASE15
owner: Module 08 Tool Runtime

## Phase 目标

实现有副作用 Tool 的完整受治理顺序：PreparedToolAction→Security Prepare→Approval→Security Execute/latest Epoch→Mandatory Audit→IdempotencyClaim→SecretLease→ToolAttempt→EffectReceipt 或 EffectReconciliation→Agent Observation，并支持 Cancellation、Compensation、Manual Assessment。UNKNOWN 禁止盲目 Retry。

## Minimal Read Set

- `docs/modules/08-tool-runtime.md`
- Wave 1 canonical side-effect sequence
- PHASE05 Security/Approval/Secret
- PHASE06 Audit/Trace
- PHASE04 Claim/Lease/Fencing
- PHASE15 Tool Domain/Adapters

## Current Anchors

```text
current approval/resume/tool claim code
CLI/OpenAPI/MCP/SDK/browser write adapters
agent runtime tool bridge
workspace approval API/UI contract
```

## Goal04 PR B Current Evidence

当前 PR B 分支：`codex/goal04-phase16-tool-side-effect`

当前 PR head：以 GitHub PR #46 / remote branch 为准；本 evidence sync 基线为 `77dec8a0`。

当前 Evidence：`docs/evidence/goal04-phase16-startup-audit.md`

已完成并验证的当前切片：

- P16-T01 Effect Classification 与 TargetResourceSet。
- P16-T02 Prepare Gate 与 Approval Binding。
- P16-T03 Execute Gate、Audit、Claim、Lease 与 SecretLease。
- P16-T04 Effect Attempt 与 Known EffectReceipt。
- P16-T05 UNKNOWN Effect 与 Reconciliation。
- P16-T06 Async Callback 与 Cancellation Receipt。
- P16-T07 Compensation 与 Manual Effect Assessment。
- P16-T08 Side-effect Cutover 与 Bypass Zero Guard。
- P16-T08R Default ToolControlPlane Gateway Cutover Repair。
- P16-T09 Restart Recovery、Age Escalation 与 Async Timeout。
- P16-T10 Side-effect Idempotency Replay。
- P16-T11 Async Callback Completion 与 Forged Callback Fencing。
- P16-T12 Async Cancellation State 与 Timeout Fencing。
- P16-T13 Manual Effect Assessment Authorization Boundary。
- P16-T14 Compensation from Reconciliation Requires Escalation。
- P16-T15 Execute Latest Epoch Reauthorization。
- P16-T16 Approval Deadline Reauthorization。
- P16-T17 SecretLease Revocation Fail-Closed。

当前验证状态：

- `zuno-postgres` 已通过 Docker Compose 恢复为 healthy。
- P16-T17 focused test `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_blocks_revoked_secret_before_effect_dispatch -p no:cacheprovider --tb=short` 已在显式 worktree `sys.path` wrapper 下通过。
- PHASE16 仍为 `in_progress`。本节只同步当前实现证据，不构成 Coordinator Closure Approval，不把 Program、Manifest 或 Production Readiness 改为 completed/ready。

## Allowed Paths

```text
src/backend/zuno/capability/tool_runtime/**
src/backend/zuno/platform/database/tool_runtime/**
worker/reconciler entrypoints
alembic/**
tests/tool_runtime/**
tests/integration/tool_runtime/**
tests/fault/tool_runtime/**
tests/security/tool_runtime/**
docs/evidence/**
```

## Forbidden Paths

- Provider write 在审批、审计、Claim 前执行。
- UNKNOWN 状态直接 Retry 或标记成功。
- Compensation 覆盖原 EffectReceipt。
- Tool Runtime 自己批准权限或生成 Agent ControlDecision。

## Work Packages

### P16-T01 Side-effect Classification and TargetResourceSet
- Goal：定义 NONE/READ/REVERSIBLE_WRITE/IRREVERSIBLE_WRITE/ASYNC_EXTERNAL 等 effect class、resource conflict、approval/audit policy。
- Tests：misclassified operation、dynamic target、same-resource conflict、unknown class fail-closed。
- Acceptance：分类由 versioned definition/policy，不由模型自由文本决定。

### P16-T02 Prepare Gate and Approval Binding
- Goal：PreparedAction 经 Security Prepare，创建 ApprovalRequest，绑定 hash/args/resource/epoch/deadline/operation version。
- Tests：arg mutation、version change、approval replay/expire/deny、multiple approvals。
- Acceptance：Approval 只接受完全相同的 PreparedAction。

### P16-T03 Execute Gate, Audit, Claim and SecretLease
- Goal：执行前重新授权 latest epoch，持久 mandatory audit receipt，获取 idempotency claim/lease/fencing/secret lease。
- Tests：epoch revoked、audit unavailable、claim conflict、lease loss、secret expiry/wrong audience。
- Acceptance：任一 Gate 失败不 dispatch provider。

### P16-T04 Effect Attempt and Known Receipt
- Goal：执行 adapter，记录 native result、provider effect id、item receipts、confirmed/failed/no-effect。
- Tests：idempotent provider、partial item success、duplicate callback、late result、response schema。
- Acceptance：HTTP 2xx 需满足 effect protocol 才生成 EffectReceipt。

### P16-T05 UNKNOWN Effect and Reconciliation
- Goal：当 dispatch 可能发生但结果未知时进入 UNKNOWN，创建 persistent reconciliation query/poll/manual workflow。
- Tests：provider performed but response lost、status endpoint unavailable、duplicate reconcile、restart、age escalation。
- Acceptance：UNKNOWN 不重新执行原动作；Agent/UI 只见受控 Reconcile/Wait/Manual action。

### P16-T06 Cancellation and Async Job Lifecycle
- Goal：实现 cancellation request/receipt、async job/callback/status、deadline、callback authenticity/order。
- Tests：cancel before/after dispatch、callback replay/out-of-order/forged、job timeout、lease transfer。
- Acceptance：Cancel receipt 不保证外部 Effect 已撤销。

### P16-T07 Compensation and Manual Assessment
- Goal：实现 versioned CompensationDefinition/Attempt、approval/audit/claim、manual effect assessment。
- Tests：compensation partial failure、double compensation、wrong original effect、human unauthorized、audit outage。
- Acceptance：Compensation 是新受治理副作用，不改写原事实。

### P16-T08 Side-effect Cutover, Fault Suite and Bypass Zero
- Goal：迁移至少一个幂等写 Tool、一个不可逆/人工确认 Tool、一个 async Tool；切流所有写旁路。
- Tests：audit commit 后 crash、dispatch 后 crash、response lost、duplicate queue、lease expiry、approval duplicate、epoch change。
- Acceptance：生产写 Tool 旁路为零；无 `legacy_tool_runtime`/直接 execute；临时 flag PHASE22 删除。

## Phase 完成定义

- Canonical side-effect sequence 真实运行。
- Known/Unknown/Cancel/Compensation/Manual 状态可恢复。
- Security、Audit、Claim、Secret、Fencing Fault Test 通过。
- 所有写 Tool 进入唯一 Gateway。

## Validation

```bash
git diff --check
python tools/scripts/verify_tool_runtime_target_protocols.py
pytest -q tests/tool_runtime tests/integration/tool_runtime tests/fault/tool_runtime tests/security/tool_runtime -p no:cacheprovider
python tools/scripts/verify_tool_execution_bypass.py
```
