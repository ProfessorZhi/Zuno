# PHASE05 Security Control Plane Evidence

status: partial_implementation_available

phase_completion: `not_approved`

date: 2026-07-19

## 目标

记录 PHASE05 Security Control Plane 的当前可复现证据，覆盖审批事实持久化、pre-effect 重新验证、SecretLease、Redaction fail-closed、mandatory audit requirement 和最小 security eval。本文不是 Phase Closure Decision。

## 已证明

- Security-owned PostgreSQL schema 已提供 Principal、Epoch、Authorization Decision、Approval Request、Approval Decision、Secret Ref、Secret Lease、Redaction Decision、Audit Requirement 和 Security Outbox 事实表。
- Tool Runtime approval path 可通过 `PostgresSecurityApprovalFactSink` 写入 Security facts。
- blocked path 会在 effect 前写入 `failed_closed_before_effect` fact，并记录 `DENY` authorization decision、`failed_closed` audit requirement 和 Security outbox event。
- Security sink outage 会在 side effect executor 前中断。
- `SecurityRepository.validate_pre_effect_authorization(...)` 在 effect 前重新校验 `prepared_action_hash`、epoch active、approval status 和 deadline；参数变更、过期 approval、revoked/stale epoch 均 fail-closed。
- `SecurityRepository.record_secret_ref(...)`、`issue_secret_lease(...)` 和 `validate_secret_lease(...)` 已证明 Secret material 不落业务表，wrong audience、expired lease、revoked secret 均 fail-closed。
- `SecurityRepository.record_redaction_decision(...)` 在 redaction 失败时把 requested allow 降为 `block`，只保存 redacted payload hash 与 decision hash。
- `PostgresSecurityProductActionGuard`、`SecurityProductActionRequest` 和共享 `security_admin_actions` 提供 Product/API action 重新授权端口；workspace artifact read/download、workspace citation refs、workspace approval resume、MCP admin 管理 override、Agent/Tool/Dialog/MCP Agent/LLM/Knowledge/Knowledge File admin override 已接入 guard，生产 `init_config()` 默认配置 `PostgresSecurityProductActionGuard(engine)`；artifact read/download/resume/citation refs 调用路径会重新授权，deny 时返回 403 且 resume 不会越过 `approval_waiting`；admin override deny 时会在 DAO 写入/删除前中断。
- `goal01-closure-matrix.md` 已冻结 PHASE05/06/07/11 四张有限 Closure Matrix，记录 fetch 后集成分支 Start SHA。
- Legacy `approved: bool` 只保留为 Tool Runtime 的 `temporary.adapter.tool_runtime.approved_bool` versioned adapter，删除 Phase 绑定为 `PHASE16`；workspace approval resume 默认路径已传入 `security-approval-decision:*` decision ref，PHASE05 verifier 阻止新增 legacy boolean owner。
- 最小 eval evidence 覆盖：
  - adaptive attack side-effect request must require approval or deny；
  - benign read-only request must preserve utility；
  - security sink outage must fail closed before effect。

## 可复现验证

```powershell
python tools/scripts/verify_phase05_security_persistence.py
python tools/scripts/verify_phase05_security_eval.py
pytest -q tests/agent/test_tool_control_plane_runtime.py::test_high_side_effect_tool_waits_for_approval_then_uses_brokered_credentials tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_emits_security_approval_facts_from_active_tool_path tests/api/test_workspace_task_runtime.py::test_workspace_artifact_read_and_download_reauthorize_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_artifact_download_returns_403_when_security_reauthorization_denies tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_reauthorizes_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_returns_403_when_security_guard_denies tests/api/test_workspace_agentic_product_contract.py::test_workspace_artifact_citation_refs_reauthorize_through_security_guard tests/api/test_workspace_agentic_product_contract.py::test_workspace_task_snapshot_citation_refs_return_403_when_security_guard_denies tests/agent/test_mcp_server_service.py::test_mcp_admin_override_reauthorizes_through_security_guard tests/agent/test_mcp_server_service.py::test_mcp_admin_override_denial_blocks_before_permission_success tests/agent/test_mcp_server_service.py::test_mcp_owner_update_does_not_require_admin_override_security_guard tests/agent/test_mcp_stdio_server_security.py tests/agent/test_phase05_admin_action_reauthorization.py tests/security/test_phase05_security_eval_gate.py tests/fault/security tests/integration/test_phase05_security_persistence_runtime.py -p no:cacheprovider
```

## 未证明

- 尚未覆盖完整 PEP/PDP cutover。
- 尚未形成 PHASE05 closure decision。
- PHASE07 与 PHASE11 不得引用本文作为依赖已完成证明。
