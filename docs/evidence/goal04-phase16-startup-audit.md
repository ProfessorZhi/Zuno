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
### P16-T09 Restart Recovery、Age Escalation 与 Async Timeout

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolRepository.escalate_due_reconciliations(...)` 支持 restart 后扫描 `OPEN/WAITING_PROVIDER` 且超过 `created_at + age_escalation_after_seconds` 的 UNKNOWN reconciliation，并推进为 `status=ESCALATED`、`next_action=MANUAL_ASSESSMENT`、`manual_assessment_required=true`。
- `ToolRepository.timeout_due_async_jobs(...)` 支持 restart 后扫描过期 `WAITING_CALLBACK` async job，并推进为 `status=TIMEOUT`。
- `ToolInvocationGateway` 暴露同名 scanner 入口，证明 recovery 可以由新进程重新创建 gateway 后继续执行，不依赖进程内状态。
- 新增 integration tests 证明 recovery scanner 不会重新执行原 provider executor；UNKNOWN idempotency claim 仍指向 reconciliation，async idempotency claim 仍指向 async job。

验证：

- `python -m py_compile src\backend\zuno\platform\database\tool_runtime\domain.py src\backend\zuno\capability\tool_runtime\invocation_gateway.py tests\integration\test_goal03_wave_b_persistence.py`：通过。
- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_reconciliation_restart_age_escalates_without_retry tests\integration\test_goal03_wave_b_persistence.py::test_phase16_async_restart_times_out_due_job_without_callback_replay -p no:cacheprovider --tb=short`：2 passed。
- 使用显式 `sys.path.insert(...)` 运行 PHASE16 focused suite，包含 default ToolControlPlane gateway cutover、Known/UNKNOWN/Reconciliation age escalation、Async/Timeout、Cancellation、Compensation、Manual Assessment 和 bypass guard：14 passed。
- Failure Fingerprint：首次 focused run 未找到 async timeout test，原因是文本插入 marker 未命中；补入测试后 targeted run 通过，无业务失败栈。
### P16-T10 Side-effect Idempotency Replay

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 对已完成的 side-effect `infra_idempotency_claims` 不再返回含糊 blocked；当 claim 为 `completed` 且存在 `result_ref` 时，返回受控 `replayed` receipt 与原领域结果引用。
- completed replay 不重新 dispatch provider，不新建第二条 `tool_effect_receipts`，也不重复发行 `security_secret_leases`。
- SecretLease 发行从 Security Prepare 拆到 idempotency claim acquired 之后，保证 replay 路径仍执行最新 authorization/audit 检查，但不为已完成副作用再次取得 credential lease。
- 默认 `ToolControlPlaneRuntime` 明确接受 gateway `replayed` 作为 successful product path；产品面仍返回 `completed`，normalized result 暴露 `idempotency_replay=true` 与原 `result_ref`。
- `security_secret_refs` 登记改为同一 `secret_ref` 的幂等写入，避免默认 runtime 在 replay 前重复登记同一 brokered credential ref 时撞唯一约束。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_default_tool_runtime_records_readonly_gateway_and_executes_approved_side_effects tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_replays_completed_side_effect_idempotency_without_dispatch -p no:cacheprovider --tb=short`：首次 1 failed / 1 passed；失败指纹见下。
- 修复后同一 focused command targeted rerun：2 passed。
- 使用显式 `sys.path.insert(...)` 运行 PHASE16 focused suite，包含 effect policy、bypass guard、default ToolControlPlane cutover/replay、Gateway side-effect/security/known/idempotency replay/UNKNOWN/restart/async/timeout/compensation tests：13 passed。

Failure Fingerprint：

- command：上述两个 idempotency focused tests。
- test：`test_phase16_default_tool_runtime_records_readonly_gateway_and_executes_approved_side_effects`。
- exception：`sqlalchemy.exc.IntegrityError / psycopg.errors.UniqueViolation`。
- first relevant frame：`src\backend\zuno\platform\security\persistence.py:747`，`record_secret_ref` 插入重复 `credref://workspace-b/mail.send`。
- environment signature：PostgreSQL Alembic head `20260727_45`，显式 PHASE16 worktree `sys.path.insert`。
- resolution：将 `security_secret_refs` 的同一 `secret_ref` 记录改为幂等 `ON CONFLICT DO NOTHING`；targeted rerun 通过。
### P16-T11 Async Callback Completion 与 Forged Callback Fencing

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolRepository.record_async_callback(...)` 从 fire-and-forget insert 改为受控 upsert：乱序 callback 可以先作为 `OUT_OF_ORDER accepted=false` 留痕，待前序 callback 到达后，同一 order 可升级为 `VERIFIED accepted=true`。
- `ToolInvocationGateway.record_async_callback(...)` 新增 `REPLAY` 判定；已接受 order 的重复 callback 不推进 job，不覆盖原 verified 事实。
- accepted callback 会推进 `tool_async_jobs.callback_order`；当 callback payload `state/status` 为 `done/completed/succeeded/success` 时，job 从 `WAITING_CALLBACK` 推进为 `COMPLETED`。
- forged callback 仍写入 `tool_async_callbacks(authenticity_status=FORGED, accepted=false)`，不会推进 async job，也不会制造 EffectReceipt 或 provider replay。
- async timeout scanner 仍只处理 `WAITING_CALLBACK`，因此已经 completed 的 job 不会被后续 timeout 覆盖。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_async_job_callback_and_cancellation -p no:cacheprovider --tb=short`：1 passed。
- 使用显式 `sys.path.insert(...)` 运行 PHASE16 focused subset，包含 effect policy、bypass guard、default ToolControlPlane cutover/replay、Known/UNKNOWN/restart、Async completion/forged callback、Async timeout 和 Compensation：11 passed。
- Failure Fingerprint：本切片 focused test 首次通过，无失败重试。
### P16-T12 Async Cancellation State 与 Timeout Fencing

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolRepository.record_cancellation_receipt(...)` 在写入 `tool_cancellation_receipts` 后，会将仍处于 `WAITING_CALLBACK` 的 `tool_async_jobs` 推进为 `CANCEL_REQUESTED`。
- 已经进入 `COMPLETED` 的 async job 不会被 cancellation 覆盖；timeout scanner 仍只处理 `WAITING_CALLBACK`，不会把 `CANCEL_REQUESTED` job 改写成 `TIMEOUT`。
- Cancellation receipt 继续保持 `status=NOT_GUARANTEED`、`external_effect_revoked=false`，明确不声明 provider 外部副作用已经撤销。
- 本切片未新增 migration；既有 `20260727_44` 的 `tool_async_jobs.status` 枚举已经包含 `CANCEL_REQUESTED`。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_async_cancellation_moves_waiting_job_without_timeout_overwrite -p no:cacheprovider --tb=short`：1 passed。
- 使用显式 `sys.path.insert(...)` 运行 async 相邻路径：callback completion/forged fencing、async timeout、async cancellation timeout fencing：3 passed。
- Failure Fingerprint：本切片 focused test 首次通过，无失败重试。
### P16-T13 Manual Effect Assessment Authorization Boundary

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolRepository.record_manual_effect_assessment(...)` 在写入 `tool_manual_effect_assessments` 前强制校验 reconciliation 存在且属于同 tenant。
- Manual assessment 只能在 reconciliation 已进入 `manual_assessment_required=true` 后写入；OPEN/未升级 UNKNOWN 不能被提前人工裁决。
- Assessor principal 必须是明确的 manual reviewer，当前本地边界为 `workspace-user:manual-reviewer*`；普通 workspace user 不能写入 manual effect assessment。
- `ToolRuntimeConflict` 从 `zuno.platform.database.tool_runtime` package 导出，便于 gateway/integration/fault tests 固定该领域冲突语义。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_unknown_effect_reconciliation_without_retry -p no:cacheprovider --tb=short`：首次 collection error；补导出后 targeted rerun 1 passed。
- 使用显式 `sys.path.insert(...)` 运行 UNKNOWN/manual 相邻路径：unknown reconciliation/manual assessment boundary、restart age escalation：2 passed。

Failure Fingerprint：

- command：上述 manual assessment focused test。
- test：collection `tests/integration/test_goal03_wave_b_persistence.py`。
- exception：`ImportError: cannot import name 'ToolRuntimeConflict' from 'zuno.platform.database.tool_runtime'`。
- first relevant frame：`tests\integration\test_goal03_wave_b_persistence.py:18`。
- environment signature：显式 PHASE16 worktree `sys.path.insert`，PostgreSQL Alembic head `20260727_45`。
- resolution：从 `src/backend/zuno/platform/database/tool_runtime/__init__.py` 导出 `ToolRuntimeConflict`；targeted rerun 通过。
### P16-T14 Compensation from Reconciliation Requires Escalation

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolRepository.record_compensation_definition(...)` 当 compensation 绑定 `source_reconciliation_id` 时，要求该 reconciliation 已存在且 `manual_assessment_required=true`。
- 未升级的 UNKNOWN reconciliation 不能直接作为补偿源；只有升级为 `ESCALATED/MANUAL_ASSESSMENT` 后，compensation definition 才能落库。
- compensation source_effect_receipt 路径不受该 reconciliation-only 校验影响，仍保持原有 happy path。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_compensation_from_unresolved_reconciliation_requires_escalation -p no:cacheprovider --tb=short`：首次因测试缺少 compensation prepared action 事实失败；补充预热 call 后 targeted rerun 1 passed。
- 使用显式 `sys.path.insert(...)` 运行 compensation 相邻路径：source-effect happy path 与 source-reconciliation gated path => 2 passed。

Failure Fingerprint：

- command：上述 compensation focused test。
- test：`test_phase16_compensation_from_unresolved_reconciliation_requires_escalation`。
- exception：`sqlalchemy.exc.IntegrityError / psycopg.errors.ForeignKeyViolation`。
- first relevant frame：`src\backend\zuno\platform\database\tool_runtime\domain.py:991`，`fk_tool_comp_attempt_prepared`。
- environment signature：显式 PHASE16 worktree `sys.path.insert`，PostgreSQL Alembic head `20260727_45`。
- resolution：补充 compensation call 的实际 prepared action 预热；targeted rerun 通过。
### P16-T15 Execute Latest Epoch Reauthorization

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 在真正 dispatch provider 之前重新调用 `validate_pre_effect_authorization`，而不只是依赖 prepare 阶段的授权结果。
- 如果执行前最新 security epoch 已被 revoke 或变 stale，gateway 会记录 FAILED / NOT_DISPATCHED / NO_EFFECT，并返回 blocked receipt，不会发行 secret lease，也不会调用 provider executor。
- 正常已批准路径仍保持不变：latest epoch reauth 通过后继续进入 secret lease、provider dispatch 与 effect receipt 流程。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_reauthorizes_latest_epoch_before_effect_dispatch -p no:cacheprovider --tb=short`：1 passed。
- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_known_effect_receipt_after_approval tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_reauthorizes_latest_epoch_before_effect_dispatch -p no:cacheprovider --tb=short`：2 passed。
- Failure Fingerprint：本切片 focused test 首次通过，无失败重试。
### P16-T16 Approval Deadline Reauthorization

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 在真正 dispatch provider 之前再次验证 approval deadline。
- 若 approved request 在准备后、执行前过期，gateway 会在 dispatch 前失败关闭，记录 FAILED / NOT_DISPATCHED / NO_EFFECT，并且不发行 secret lease。
- 正常 approve 路径仍保持不变：未过期时继续进入 secret lease、provider dispatch 与 effect receipt 流程。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_reauthorizes_approval_deadline_before_effect_dispatch -p no:cacheprovider --tb=short`：1 passed。
- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_known_effect_receipt_after_approval tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_reauthorizes_approval_deadline_before_effect_dispatch -p no:cacheprovider --tb=short`：2 passed。
- Failure Fingerprint：本切片 focused test 首次通过，无失败重试。
### P16-T17 SecretLease Revocation Fail-Closed

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 在 provider dispatch 前发行并验证 `SecretLease`；若 `_issue_secret_lease(...)` 因 revoked/invalid secret 抛出 `SecurityPersistenceError`，gateway 会记录 FAILED / NOT_DISPATCHED / NO_EFFECT，并返回 blocked receipt。
- revoked secret 不会调用 provider executor，也不会写入 `tool_effect_receipts`，避免用失败副作用路径伪造成功。
- SecretLease 发行与验证处于同一 Security UoW；验证失败时 failed lease insert 回滚，运行时证据边界为未 dispatch、无 SecretLease、无 EffectReceipt 和 terminal execution receipt。

验证：

- `py_compile`：`src\backend\zuno\capability\tool_runtime\invocation_gateway.py` 与 `tests\integration\test_goal03_wave_b_persistence.py` 通过。
- 初次使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_blocks_revoked_secret_before_effect_dispatch -p no:cacheprovider --tb=short`：setup 阶段 PostgreSQL 连接超时，测试未执行到业务代码。
- 环境恢复：启动 `com.docker.service`、Docker Desktop engine，并运行 `docker compose -f infra/docker/docker-compose.yml up -d postgres`；`zuno-postgres` healthcheck 为 `healthy`。
- 环境恢复后从同一 focused test 命令继续：首次进入业务断言失败，因测试错误地期望 failed lease row 保留；修正为 `security_secret_leases` count `0` 后 targeted rerun：1 passed。

Failure Fingerprint：

- command：上述 revoked secret focused test。
- test：`test_phase16_gateway_blocks_revoked_secret_before_effect_dispatch` setup fixture `migrated_postgres`。
- exception：`sqlalchemy.exc.OperationalError / psycopg.errors.ConnectionTimeout`。
- first relevant frame：`infra\db\alembic\env.py:94`，`with connectable.connect() as connection`。
- environment signature：PHASE16 worktree `acea3822` 后本地修改，`ZUNO_TEST_POSTGRES_URL` 默认 `postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5`，Windows 未发现 PostgreSQL service，Docker Desktop Linux engine 未运行。
- recovery action：已启动 Docker Desktop 与 `zuno-postgres`，从相同 focused test 命令继续。

业务断言 Failure Fingerprint：

- command：上述 revoked secret focused test。
- test：`test_phase16_gateway_blocks_revoked_secret_before_effect_dispatch`。
- exception：`AssertionError`。
- first relevant frame：`tests\integration\test_goal03_wave_b_persistence.py:1026`。
- environment signature：`zuno-postgres` healthy，Alembic head `20260727_45`，PHASE16 worktree `bc4af119` 后本地修正。
- resolution：failed SecretLease insert 与 validation 位于同一 UoW，异常回滚 lease row；测试断言改为无 SecretLease row，targeted rerun 通过。
### P16-T18 Pre-held Idempotency Claim Fail-Closed Reason

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 在 side-effect execute prerequisites 被 infra idempotency claim 阻塞时，把 gateway receipt 的 `blocked_reason` 同步为真实 infra gate reason，而不是继续返回泛化的 `PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL`。
- pre-held `infra_idempotency_claims` 会在 provider dispatch 前失败关闭：不调用 executor、不发行 SecretLease、不写 EffectReceipt，并记录 FAILED / NOT_DISPATCHED / NO_EFFECT execution receipt。
- 已持有 claim 的 owner/status/result_ref 不被覆盖，避免把并发执行误判为可重放成功或抢占执行权。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_blocks_preheld_idempotency_claim_before_effect_dispatch -p no:cacheprovider --tb=short`：首次进入业务断言失败，因测试错误查询不存在的 `tool_execution_receipts.payload` 列；修正断言后 targeted rerun：1 passed。

Failure Fingerprint：

- command：上述 pre-held idempotency claim focused test。
- test：`test_phase16_gateway_blocks_preheld_idempotency_claim_before_effect_dispatch`。
- exception：`sqlalchemy.exc.ProgrammingError / psycopg.errors.UndefinedColumn`。
- first relevant frame：`tests\integration\test_goal03_wave_b_persistence.py:1146`。
- environment signature：`zuno-postgres` healthy，Alembic head `20260727_45`，显式 PHASE16 worktree `sys.path.insert`。
- resolution：`tool_execution_receipts` 只保存 receipt hash 而非 raw payload；测试改为断言 gateway receipt reason 与 durable status/certainty，targeted rerun 通过。
### P16-T19 Provider Exception Converts to UNKNOWN Reconciliation

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- approved side-effect executor 被调用后，如 provider adapter 抛出普通异常，`ToolInvocationGateway` 不再让异常逃逸并遗留 in-progress claim。
- 该路径记录 UNKNOWN / DISPATCHED / UNKNOWN_EFFECT execution receipt，创建 `tool_effect_reconciliations`，并将 infra idempotency claim completed 到 reconciliation ref。
- 不写 `tool_effect_receipts`，不把 provider timeout/exception 冒充为 `NO_EFFECT` 或成功；后续由 reconciliation/manual assessment 判定外部效果。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_records_provider_exception_as_unknown_reconciliation -p no:cacheprovider --tb=short`：1 passed。
- Failure Fingerprint：本切片 focused test 首次通过，无失败重试。
### P16-T20 Durable Effect Repairs Incomplete Idempotency Claim

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolRepository.existing_side_effect_result_ref(...)` 可按 call id 查找已持久化的 EffectReceipt / EffectReconciliation / AsyncJob result ref。
- `ToolInvocationGateway` 在 infra idempotency claim 未 acquired 且仍为 in-progress 时，若 Tool Runtime 已存在 durable side-effect result，会修复同 owner claim 到 completed 并返回 replay，而不是阻塞或重新 dispatch provider。
- 该恢复路径覆盖 EffectReceipt 已落库但 `_complete_execute_prerequisites(...)` 失败的危险窗口，避免外部副作用已经确认但 infra claim 永久卡住。
- 当前 gateway 不把该 infra completion 异常泄漏给调用方；第一次调用会进入受控 `reconcile_required / UNKNOWN_EFFECT_RECONCILIATION_REQUIRED`，第二次同 call id replay 从 durable EffectReconciliation 修复 claim，且不重新 dispatch provider。

验证：

- RED：`python -m pytest tests\integration\test_goal03_wave_b_persistence.py -q -p no:cacheprovider --tb=short` 失败于 `test_phase16_gateway_recovers_durable_effect_when_claim_completion_failed`，旧测试仍期望 `RuntimeError("infra completion outage after effect receipt")` 泄漏；当前实现已经将该故障转为受控 UNKNOWN reconciliation。
- 修正后使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_recovers_durable_effect_when_claim_completion_failed -p no:cacheprovider --tb=short`：1 passed。
- Failure Fingerprint：旧断言与当前恢复语义冲突；更新测试断言为第一次 `reconcile_required`、第二次 durable reconciliation replay 修复 claim。
### P16-T21 Effect Receipt Persistence Failure Falls Back to UNKNOWN Reconciliation

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 在 provider 返回结果后，如果 `tool_effect_receipts` 持久化失败，会将 execution receipt 先保持为 `DISPATCHED`，随后改写为 `UNKNOWN / DISPATCHED / UNKNOWN_EFFECT`，并写入 `tool_effect_reconciliations`。
- 该路径让已调用 provider 但未落 effect receipt 的副作用结果进入可恢复 reconciliation，而不会被误记为 completed 或遗留错误的 SUCCEEDED receipt。
- 继续复用同一 owner 的 idempotency claim，并将 claim 完成到 reconciliation ref，供后续 replay/reconciliation 读取。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_recovers_unknown_when_effect_receipt_persistence_fails -p no:cacheprovider --tb=short`：1 passed。
- Failure Fingerprint：本切片 focused test 首次通过，无失败重试。

### P16-T22 Async Job Persistence Failure Falls Back to UNKNOWN Reconciliation

状态：completed-for-current-slice，未构成 PHASE16 closure。

已实现内容：

- `ToolInvocationGateway` 在 provider 返回 async job handle 后，如果 `tool_async_jobs` 持久化或随后的 claim completion 失败，会将 execution receipt 回落为 `UNKNOWN / DISPATCHED / UNKNOWN_EFFECT`，并写入 `tool_effect_reconciliations`。
- 该路径让已触发 provider 但未完成 async job 记录的结果进入可恢复 reconciliation，而不会被误记为已完成或遗留半写入状态。
- 继续复用同一 owner 的 idempotency claim，并将 claim 完成到 reconciliation ref，供后续 replay/reconciliation 读取。

验证：

- 使用显式 `sys.path.insert(...)` 运行 `tests\integration\test_goal03_wave_b_persistence.py::test_phase16_gateway_recovers_unknown_when_async_job_persistence_fails -p no:cacheprovider --tb=short`：1 passed。
- Failure Fingerprint：本切片 focused test 首次通过，无失败重试。
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

P16-T01 至 P16-T22 的 focused implementation slices 已具备代码、migration、PostgreSQL integration、fault/security 和 verifier 证据；默认 Product/Agent ToolControlPlane 写 Tool 已由 `readonly_cutover_only=False` 切入 `ToolInvocationGateway`，并验证 EffectReceipt、SecretLease、IdempotencyClaim、completed side-effect replay、durable effect claim repair、pre-held idempotency claim fail-closed、provider exception UNKNOWN reconciliation、effect receipt persistence UNKNOWN reconciliation、async job persistence UNKNOWN reconciliation、UNKNOWN recovery、manual assessment authorization boundary、compensation source reconciliation gating、latest epoch reauthorization、approval deadline reauthorization、revoked SecretLease fail-closed、async completion/forged callback fencing、async cancellation state 和 async timeout。后续 closure commit 必须同步 Program/Manifest、Production Readiness 和 Coordinator Approval，且不得声明 production ready。
## 当前结论

PHASE16 已在独立 PR B worktree 启动为 `in_progress`。P16-T01 至 P16-T22 当前切片已完成并验证。默认 Product/Agent ToolControlPlane 写 Tool已通过 Gateway 切流并产生 EffectReceipt/SecretLease/Claim 证据，completed side-effect replay 和 durable effect claim repair 不会重复 dispatch provider，pre-held idempotency claim 不会 dispatch provider，provider exception 会进入 UNKNOWN reconciliation，effect receipt persistence failure 会进入 UNKNOWN reconciliation，async job persistence failure 会进入 UNKNOWN reconciliation，restart recovery 已覆盖 UNKNOWN age escalation、manual assessment authorization boundary、compensation source reconciliation gating、latest epoch reauthorization、approval deadline reauthorization、revoked SecretLease fail-closed、async callback completion/forged fencing、async cancellation state 与 async timeout；PHASE16 closure 状态尚未在 Program/Manifest 中写入 completed，本文不证明 Goal04 completed、quality fully proven 或 production ready。
