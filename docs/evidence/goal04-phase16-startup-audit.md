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

### P16-T05 UNKNOWN Effect 与 Reconciliation

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- 新增 append-only Alembic revision `20260727_43_phase16_tool_effect_reconciliations.py`，创建 `tool_effect_reconciliations` 作为 UNKNOWN Effect 的正式持久事实。
- `ToolInvocationGateway` 新增 `ToolEffectUnknownError`，表达 provider dispatch 可能发生但结果丢失的状态。
- 已审批且全部前置门禁通过后，若 provider 抛出 `ToolEffectUnknownError`，gateway 记录 `ToolExecutionReceipt(status=UNKNOWN, effect_certainty=UNKNOWN_EFFECT)`，创建 `tool_effect_reconciliations`，并返回受控 `reconcile_required`。
- UNKNOWN 路径不会重新执行原动作；infra idempotency claim 标记为 `completed`，`result_ref` 指向 reconciliation，阻止重复请求重放 provider。
- Reconciliation 持久事实绑定 provider effect id、query hash、payload hash、idempotency generation、fencing token 和 SecretLease，并设置 age escalation 窗口。

验证：

- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_binds_security_prepare_to_prepared_action_hash tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_known_effect_receipt_after_approval tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_unknown_effect_reconciliation_without_retry -p no:cacheprovider`：6 passed。
- `python -m pytest -q tests\repo\test_goal03_wave_b_migration_contract.py -p no:cacheprovider`：5 passed。
- Failure Fingerprint：本切片 focused suite 首次通过，无失败重试。
### P16-T06 Async Callback 与 Cancellation Receipt

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- 新增 append-only Alembic revision `20260727_44_phase16_tool_async_cancellation.py`，创建 `tool_async_jobs`、`tool_async_callbacks` 和 `tool_cancellation_receipts` 三类正式持久事实。
- 已审批且 Security/Audit/SecretLease/Idempotency/Fencing 全部通过的 `ASYNC_EXTERNAL` Tool 会记录 `ToolExecutionReceipt(status=DISPATCHED, effect_certainty=UNKNOWN_EFFECT)`，创建 `tool_async_jobs`，并返回 `async_waiting`，不把 provider job dispatch 冒充为 effect success。
- Async job 持久事实绑定 provider job id、callback binding、deadline、idempotency generation、fencing token、SecretLease 和 job payload hash；infra idempotency claim 标记为 `completed`，`result_ref` 指向 async job。
- Gateway 新增 callback 记录入口，校验 callback binding 与 callback order；伪造或乱序 callback 写入审计事实但 `accepted=false`。
- Gateway 新增 cancellation request 记录入口，默认 `status=NOT_GUARANTEED` 且 `external_effect_revoked=false`，明确不声明外部副作用已撤销。

验证：

- `python -m py_compile src\backend\zuno\capability\tool_runtime\invocation_gateway.py src\backend\zuno\platform\database\tool_runtime\domain.py tests\integration\test_goal03_wave_b_persistence.py tests\repo\test_goal03_wave_b_migration_contract.py`：通过。
- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_binds_security_prepare_to_prepared_action_hash tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_known_effect_receipt_after_approval tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_unknown_effect_reconciliation_without_retry tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_async_job_callback_and_cancellation -p no:cacheprovider`：7 passed。
- `python -m pytest -q tests\repo\test_goal03_wave_b_migration_contract.py -p no:cacheprovider`：6 passed。
- Failure Fingerprint：本切片 focused suite 首次通过，无失败重试。
### P16-T07 Compensation 与 Manual Effect Assessment

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- 新增 append-only Alembic revision `20260727_45_phase16_tool_compensation_manual_assessment.py`，创建 `tool_compensation_definitions`、`tool_compensation_attempts` 和 `tool_manual_effect_assessments` 三类正式持久事实。
- Compensation 不走隐藏回滚：补偿动作必须先通过新的 `PreparedToolAction`、Security Prepare、Approval、Audit、Idempotency Claim、Fencing、SecretLease、ToolAttempt 和 `EffectReceipt`，随后 `tool_compensation_attempts` 以 FK 绑定该新动作。
- `tool_compensation_definitions` 记录 source effect 或 source reconciliation、compensation capability、operation ref、new action proposal ref、approval requirement、window deadline、residual impact 和 payload hash。
- `tool_compensation_attempts` 强制 `hidden_rollback=false`，绑定新 compensation call 的 prepared/attempt/execution receipt、audit requirement、idempotency generation 和 payload hash。
- `tool_manual_effect_assessments` 记录人工判断、证据 hash、置信度和剩余不确定性；它不伪造 Provider EffectReceipt，也不删除 UNKNOWN/Reconciliation 历史。

验证：

- `python -m py_compile src\backend\zuno\capability\tool_runtime\invocation_gateway.py src\backend\zuno\platform\database\tool_runtime\domain.py src\backend\zuno\platform\database\tool_runtime\__init__.py tests\integration\test_goal03_wave_b_persistence.py tests\repo\test_goal03_wave_b_migration_contract.py`：通过。
- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_binds_security_prepare_to_prepared_action_hash tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_known_effect_receipt_after_approval tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_unknown_effect_reconciliation_without_retry tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_async_job_callback_and_cancellation tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_compensation_as_new_governed_action -p no:cacheprovider`：8 passed。
- `python -m pytest -q tests\repo\test_goal03_wave_b_migration_contract.py -p no:cacheprovider`：7 passed。
- Failure Fingerprint 1：`test_phase16_gateway_records_unknown_effect_reconciliation_without_retry`，`AttributeError`，`ToolInvocationGateway` 缺少 `record_manual_effect_assessment`；原因是插入点换行格式未命中，补入 gateway 方法后 targeted rerun 通过。
- Failure Fingerprint 2：`test_phase16_gateway_records_compensation_as_new_governed_action`，`TypeError: 'NoneType' object is not subscriptable`，第二个 compensation Tool call 因同一 target resource 的现有 fencing lease 被阻断；测试改为使用独立 target resource，证明 compensation 动作本身走完整治理链后 targeted rerun 通过。
### P16-T08 Side-effect Cutover 与 Bypass Zero Guard

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- 新增 `src/backend/zuno/capability/tool_runtime/bypass_guard.py`，为 legacy direct tool caller 提供统一 fail-closed guard。
- `ReactAgent`、`PlanExecuteAgent` 和 `MCPManager.call_mcp_tools` 在直接调用 `tool.ainvoke`、`tool.invoke`、`tool.coroutine` 或 `tool.func` 前必须先执行 `ensure_legacy_direct_tool_allowed`。
- Guard 只允许名称上明确 readonly 的 legacy direct tool；写 Tool 或无法证明 readonly 的 Tool 使用固定原因 `PHASE16_DIRECT_TOOL_BYPASS_BLOCKED` fail-closed，不允许绕过 `ToolInvocationGateway` 直接 dispatch。
- 既有 user-defined CLI/OpenAPI Tool Runtime 已经通过 `ToolInvocationGateway.invoke_readonly` 包裹 adapter execution；新增 repo test 固定该默认路径。
- 本切片未新增 migration；它收口的是生产写 Tool direct execution 入口，不改变 `20260727_45` Alembic head。

验证：

- `python -m py_compile src\backend\zuno\capability\tool_runtime\bypass_guard.py src\backend\zuno\agent\core\agents\react_agent.py src\backend\zuno\agent\core\agents\plan_execute_agent.py src\backend\zuno\platform\services\mcp\manager.py tests\capability\test_phase16_tool_bypass_guard.py tests\repo\test_phase16_tool_bypass_zero.py`：通过。
- `python -m pytest -q tests\capability\test_phase16_tool_bypass_guard.py tests\repo\test_phase16_tool_bypass_zero.py -p no:cacheprovider`：4 passed。
- `python -m pytest -q tests\capability\test_phase16_tool_effect_policy.py tests\integration\test_goal03_wave_b_persistence.py::test_phase15_default_tool_runtime_records_readonly_gateway_and_blocks_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_side_effect_classification_before_blocking tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_binds_security_prepare_to_prepared_action_hash tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_known_effect_receipt_after_approval tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_unknown_effect_reconciliation_without_retry tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_async_job_callback_and_cancellation tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_compensation_as_new_governed_action -p no:cacheprovider`：8 passed。
- Failure Fingerprint：本切片 focused suite 首次通过，无失败重试。
### P16-T08R Default ToolControlPlane Gateway Cutover Repair

状态：completed-for-current-slice，未构成 PHASE16 closure。

修复内容：

- `build_default_tool_control_plane_runtime()` 不再保留 `readonly_cutover_only=True`；默认 Product/Agent ToolControlPlane 对 approved side-effect Tool 进入真实切流路径。
- 默认 runtime 注入 `ToolUnitOfWork`、`SecurityUnitOfWork` 和 `InfrastructureUnitOfWork`，side-effect Tool 分支通过 `ToolInvocationGateway.invoke_readonly(...)` 执行，不再由 `ToolControlPlaneRuntime` 直接写普通 execution receipt 冒充 effect success。
- 默认 runtime 将 brokered credential ref 注册为 Security secret ref，再由 Gateway 发行 `security_secret_leases`，并完成 idempotency claim、fencing、`ToolAttempt`、`ToolExecutionReceipt` 和 `tool_effect_receipts`。
- `tests/integration/test_goal03_wave_b_persistence.py::test_phase16_default_tool_runtime_records_readonly_gateway_and_executes_approved_side_effects` 增强为断言 `tool-effect-receipt:readonly-mail-1`、`security-secret-lease:readonly-mail-1` 和 `infra_idempotency_claims.result_ref = tool-effect-receipt:readonly-mail-1`。
- `tools/scripts/verify_tool_execution_bypass.py` 已从检查 `readonly_cutover_only=True` 更新为检查 `readonly_cutover_only=False` 和默认 provider success phrase。

验证环境注意事项：

- 本机 Python 运行时使用隔离 `_pth` 配置，会忽略 `PYTHONPATH`；直接 `python -m pytest` 会导入主 worktree 的 editable install，而不是 PHASE16 worktree。
- 本轮有效 pytest 证据均使用 `sys.path.insert(0, r'F:\internship-work\resume&resume project\02_projects\Zuno-goal04-phase16\src\backend')` 强制导入 PR B worktree 代码。

验证：

- `python -m py_compile src\backend\zuno\capability\runtime.py tests\integration\test_goal03_wave_b_persistence.py tests\fault\security\test_phase05_security_sink_fail_closed.py`：通过。
- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_default_tool_runtime_records_readonly_gateway_and_executes_approved_side_effects -p no:cacheprovider --tb=short`：1 passed。
- 使用显式 `sys.path.insert(...)` 运行 PHASE16 focused suite：`tests\capability\test_phase16_tool_effect_policy.py`、默认 ToolControlPlane cutover test、Gateway side-effect/security/known/unknown/async/compensation tests、`tests\capability\test_phase16_tool_bypass_guard.py`、`tests\repo\test_phase16_tool_bypass_zero.py`：12 passed。
- 使用显式 `sys.path.insert(...)` 运行 `tests\fault\security\test_phase05_security_pre_effect_faults.py tests\fault\security\test_phase05_security_sink_fail_closed.py -p no:cacheprovider --tb=short`：5 passed。
- 使用显式 `sys.path.insert(...)` 运行 `tests\repo\test_goal03_wave_b_migration_contract.py -p no:cacheprovider`：7 passed。
- `python tools\scripts\verify_tool_runtime_target_protocols.py`：通过。
- `python tools\scripts\verify_tool_execution_bypass.py`：通过。
- `alembic -c infra\db\alembic.ini heads`：单一 head `20260727_45 (head)`。
- `alembic -c infra\db\alembic.ini upgrade head`：通过。

Failure Fingerprint：

- command：合并运行 builder 相关安全/能力测试的旧命令。
- exception：timeout after 124s。
- first relevant frame：无 pytest 栈，命令被工具超时终止。
- environment signature：未显式 `sys.path.insert`，Python 默认导入主 worktree editable install。
- resolution：不重复同一大命令，改为拆分并显式插入 PHASE16 worktree source path。
## PHASE16 Closure Gate Audit

状态：closure_not_approved。

已运行 gate：

- `python tools\scripts\verify_tool_runtime_target_protocols.py`：通过，输出 `Tool Runtime target architecture verification passed.`。
- `python tools\scripts\verify_tool_execution_bypass.py`：通过，输出 `Tool execution bypass verification passed.`。
- `alembic -c infra\db\alembic.ini heads`：通过，单一 head 为 `20260727_45 (head)`。
- `alembic -c infra\db\alembic.ini upgrade head`：通过。
- `python -m pytest -q tests\fault\security\test_phase05_security_pre_effect_faults.py tests\fault\security\test_phase05_security_sink_fail_closed.py -p no:cacheprovider`：修正旧断言后 5 passed。

Failure Fingerprint：

- command：`python -m pytest -q tests\fault\security\test_phase05_security_pre_effect_faults.py tests\fault\security\test_phase05_security_sink_fail_closed.py -p no:cacheprovider`
- test：`test_security_sink_outage_blocks_approved_side_effect_before_executor_runs`
- exception：`AssertionError: Regex pattern did not match`
- first relevant frame：`tests/fault/security/test_phase05_security_sink_fail_closed.py:17`
- environment signature：PostgreSQL Alembic head `20260727_45`，PHASE16 default readonly cutover active。
- resolution：默认 ToolControlPlaneRuntime 对写 Tool 先 fail-closed，因此 security sink status 为 `failed_closed_before_effect`，不是旧 PHASE15 断言里的 `approved_before_effect`；更新 fault test 断言后 targeted rerun 通过。

Closure Reviewer 结论：

P16-T01 至 P16-T08R 的 focused implementation slices 已具备代码、migration、PostgreSQL integration、fault/security 和 verifier 证据；默认 Product/Agent ToolControlPlane 写 Tool 已由 `readonly_cutover_only=False` 切入 `ToolInvocationGateway`，并验证 EffectReceipt、SecretLease 和 IdempotencyClaim。后续 closure commit 必须同步 Program/Manifest、Production Readiness 和 Coordinator Approval，且不得声明 production ready。
## 当前结论

PHASE16 已在独立 PR B worktree 启动为 `in_progress`。P16-T01 至 P16-T08R 当前切片已完成并验证，默认 Product/Agent ToolControlPlane 写 Tool 已通过 Gateway 切流并产生 EffectReceipt/SecretLease/Claim 证据；PHASE16 closure 状态尚未在 Program/Manifest 中写入 completed，本文不证明 Goal04 completed、quality fully proven 或 production ready。
