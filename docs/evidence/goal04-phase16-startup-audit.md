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

## 实施进展

### P16-T01 Effect Classification 与 TargetResourceSet

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- 新增 `src/backend/zuno/capability/tool_runtime/effect_policy.py`，定义 `ToolEffectClass`、`TargetResourceSet`、`ToolEffectPolicy` 和 `classify_tool_effect`。
- 默认 `ToolInvocationGateway` 在 publish、adapter binding、activation 和 PreparedToolAction 前统一计算 effect policy。
- PreparedAction Hash 输入新增 `action_proposal_ref`、`target_resource_set_ref`、`target_conflict_keys`、`effect_policy_version` 和 `effect_policy_hash`。
- 有副作用 Tool 仍保持 fail-closed，不 dispatch provider；阻断 observation/receipt 写入 effect class 与 TargetResourceSet 信息。
- 默认 capability runtime 的 Tool Runtime facts 同步写入 effect policy 元数据。

验证：

- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking -p no:cacheprovider`：3 passed。
- Failure Fingerprint：首次失败为 PreparedAction hash expected 使用未脱敏邮箱，实际 runtime 使用 `redact_sensitive_payload(args)`；修复测试预期后 targeted rerun 通过。


### P16-T02 Prepare Gate 与 Approval Binding

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolRepository.prepare_action` 返回唯一 `prepared_action_hash`，作为 Tool Runtime 与 Security 的共同绑定事实。
- `ToolInvocationGateway` 支持注入 `SecurityUnitOfWork`，在 PreparedToolAction 之后写入 `security_effective_epochs`、`security_principal_contexts`、`security_authorization_decisions` 和 pending `security_approval_requests`。
- 有副作用 Tool 的 authorization decision 为 `REQUIRES_APPROVAL`，`prepared_action_hash` 必须与 PreparedToolAction 完全一致。
- provider dispatch 仍 fail-closed；pending approval 的 `validate_pre_effect_authorization` 失败原因进入 Tool observation/receipt hash 输入。

验证：

- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_binds_security_prepare_to_prepared_action_hash -p no:cacheprovider`：4 passed。
- Failure Fingerprint：首次失败为测试查询 `tool_observations.payload`，实际表只存 `redacted_payload_hash`；改为断言 hash 后 targeted rerun 通过。

### P16-T03 Execute Gate、Audit、Claim、Lease 与 SecretLease

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 支持注入 `InfrastructureUnitOfWork`，在 Security pre-effect authorization 通过后才获取 infra idempotency claim 与 worker lease/fencing token。
- Security prepare helper 在 authorization decision 后写入 mandatory `security_audit_requirements`。
- 已审批有副作用 Tool 必须提供已存在的 `secret_ref`，并通过 `security_secret_leases` 与 `validate_secret_lease` 绑定 workload identity、approval request、audience 和过期时间。
- 任一 Security、SecretLease、Idempotency 或 Fencing Gate 失败都不会 dispatch provider。
- 即使全部前置门禁通过，当前切片仍保持 provider dispatch fail-closed，等待 P16-T04 Known EffectReceipt。

验证：

- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_binds_security_prepare_to_prepared_action_hash tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_execute_prerequisites_after_approval -p no:cacheprovider`：5 passed。
- Failure Fingerprint：本切片 focused suite 首次通过，无失败重试。

### P16-T04 Effect Attempt 与 Known EffectReceipt

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- 新增 append-only Alembic revision `20260727_42_phase16_tool_effect_receipts.py`，创建 `tool_effect_receipts` 作为 Tool Runtime 的正式 Known EffectReceipt 持久事实。
- `ToolRepository` 新增 `ToolEffectReceiptInput` 与 `record_effect_receipt`，绑定 `PreparedToolAction`、`ToolAttempt`、`ToolExecutionReceipt`、provider effect id、idempotency claim、fencing token 和 SecretLease。
- 已审批且 Security/Audit/SecretLease/Idempotency/Fencing 全部通过的 side-effect Tool 会 dispatch provider，并记录 `ToolExecutionReceipt(effect_certainty=CONFIRMED_EFFECT)` 与 `tool_effect_receipts`。
- EffectReceipt 写入后将 infra idempotency claim 标记为 `completed`，`result_ref` 指向 effect receipt，不以 HTTP 2xx 或普通 receipt 冒充 effect success。

验证：

- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_binds_security_prepare_to_prepared_action_hash tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_known_effect_receipt_after_approval -p no:cacheprovider`：5 passed。
- Failure Fingerprint 1：fixture TRUNCATE 未包含新增 FK 子表 `tool_effect_receipts`，PostgreSQL 报 `FeatureNotSupported cannot truncate a table referenced in a foreign key constraint`；补充清理表后通过该 setup gate。
- Failure Fingerprint 2：旧 `security_approval_requests` 未清理导致 approval deadline expired；补充 PHASE16 Security prepare/approval/audit/epoch 表和 infra claim/lease 表清理后 targeted rerun 通过。
## 当前结论

PHASE16 已在独立 PR B worktree 启动为 `in_progress`。P16-T01、P16-T02、P16-T03 与 P16-T04 当前切片已完成并验证，但 UNKNOWN/Reconciliation、Cancellation/Async、Compensation/Manual Assessment 和 Side-effect Cutover/Bypass Zero 仍是 Mandatory Gap；本文不证明 PHASE16 completed、quality fully proven 或 production ready。
