# Goal04 PHASE16 Startup Audit

status: frozen-gap-list
phase: PHASE16 Tool Side Effect and Reconciliation
branch: codex/goal04-phase16-tool-side-effect
base_branch: main
base_sha: 1f864961fcdc9b7674c5bfb5ed304dbe4c352d67
audit_date: 2026-07-27
alembic_head: 20260727_41

## 启动检查

- Worktree 从 `origin/main` 创建，未包含 PHASE10 PR A 改动。
- 启动前工作区干净。
- Alembic 单一 head：`20260727_41`。
- 已读取 Tool Runtime、Security、Agent Core、Product Surface 模块文档、ADR 0003、Wave 1 Contract Registry、Production Readiness、PHASE16 Program 和 `.agent` workflow。

## Frozen Gap List

### P16-G01 Side-effect 默认路径仍 fail-closed

`src/backend/zuno/capability/tool_runtime/invocation_gateway.py` 当前只执行 readonly；当 `readonly=False` 时写入 `effect_level = "PHASE16_REQUIRED"`，PreparedToolAction 状态为 `OBSOLETE`，随后记录 `PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL`，`dispatch_certainty="NOT_DISPATCHED"`，`effect_certainty="NO_EFFECT"`。这保护了 PHASE15，但不满足 PHASE16 有副作用 Tool 的正式执行链。

### P16-G02 PreparedToolAction 字段不足以绑定 PHASE16 Hash

`src/backend/zuno/platform/database/tool_runtime/domain.py` 当前 `PreparedToolActionInput` 只有 tool operation、canonical args、target resources、effect level、approval_required、idempotency_key、security_epoch_ref 和 status。缺少 PHASE16 要求的 prepared action hash 输入：tool definition/version/operation、canonical hash version、credential scope、policy snapshot、effective security epoch hash、deadline、approval binding version 和 action proposal ref。

### P16-G03 Security Prepare / Approval / Execute 未接入 Tool Gateway

Security persistence 已存在 approval、audit requirement 和 secret lease 基础，但 ToolInvocationGateway 当前没有调用 Security Prepare Gate、Approval Binding、Security Execute latest Epoch 或 approval replay/expiry/hash verification。

### P16-G04 Mandatory Audit / Claim / Lease / SecretLease 未形成执行前硬门禁

ToolInvocationGateway 当前没有在 provider dispatch 前取得 mandatory audit persistence receipt、infrastructure idempotency claim、lease/fencing 或 secret lease。PHASE16 要求任一 Gate 失败不得 dispatch provider。

### P16-G05 EffectReceipt / EffectReconciliation 仍是 batch contract，不是默认运行事实

`src/backend/zuno/capability/tool_runtime/runtime_batch.py` 已有 EffectReceipt、Reconciliation、Compensation、Cancellation 等 contract fixture，但默认 gateway/repository 没有持久化 `EffectReceipt` 或 `EffectReconciliation`，也没有 UNKNOWN reconciliation scheduler、restart recovery、age escalation 或 manual assessment workflow。

### P16-G06 写 Tool 旁路仍存在审计命中

启动检索发现旧直接执行表面仍存在，例如 `GeneralAgent` / `plan_execute_agent` 中 `tool.coroutine` 调用、`platform/services/user_defined_tool_runtime.py` 中 `adapter.execute`、OpenAPI/CLI adapter 测试直接调用 adapter。PHASE16 closure 前必须把所有生产写 Tool 旁路归零；当前只能作为待迁移清单。

### P16-G07 Async / Callback / Cancellation / Compensation 未实现默认路径

当前有 cancellation/async callback 的 contract fixture，但缺少真实 async job binding、callback authenticity/order、cancellation receipt、compensation attempt、manual assessment authorization 和对应 persistence/reconciler。

## 当前结论

PHASE16 已在独立 PR B worktree 启动为 `in_progress`，但没有任何 Work Package 可以关闭。本文只冻结启动 Gap，不证明 implementation available、quality proven 或 production ready。
