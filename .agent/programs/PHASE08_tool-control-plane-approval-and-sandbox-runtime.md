# PHASE08 tool-control-plane-approval-and-sandbox-runtime

status: completed

## 目标

把 ToolCard、ApprovalGate、ToolSecurityProfile 和 SandboxAuditEvent 接到真实 executor、approval API/UI、credential broker、sandbox profile 和 network policy。

## 范围

- 实现只读工具自动通行路径。
- 实现高副作用工具强制审批路径。
- 所有工具执行都产生 NormalizedToolResult、audit trace 和 security decision。

## 禁止范围

- 不让高风险工具绕过 approval。
- 不把 sandbox profile 写成注释而无执行边界。
- 不把 credentials 放进 prompt、trace 明文或 sandbox filesystem。

## 验收闸门

- tests 覆盖只读工具、高副作用工具、拒绝、审批后执行、credential 注入和 sandbox audit。
- UI 或 API 能完成 approval decision。
- trace 中可追踪 model intent 与 policy final decision。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_tool_control_plane_runtime.py tests/agent/test_tool_control_plane_contract.py tests/agent/test_capability_layer_surfaces.py tests/security tests/api/test_workspace_task_runtime.py tests/frontend/test_workspace_product_loop_types.py tests/frontend/test_frontend_workspace_features.py -p no:cacheprovider
```

## 完成证据

- `src/backend/zuno/capability/runtime.py` 新增 `ToolControlPlaneRuntime`、`ToolRuntimeRequest`、`InMemoryCredentialBroker`、`SandboxPolicyEnforcer`、`ToolSandboxContext` 和 default runtime builder。
- `ToolControlPlaneRuntime` 已复用 `ApprovalGate`、`ToolSecurityGate`、`ToolSecurityProfile`、`ToolResultNormalizer`，并生成 `tool_call`、`sandbox_audit`、`approval_required` 和 `tool_result` task events。
- `WorkspaceTaskRuntimeService` 已让 `plugins` 中的 `filesystem.read` 自动执行，`mail.send` / `filesystem.write` 进入工具级 approval wait，审批后继续执行并生成 artifact。
- `apps/web/src/apis/workspace.ts` 与 `apps/web/src/pages/workspace/defaultPage/defaultPage.vue` 已暴露 tool approval / audit 字段和最小审批卡，可调用 `approveWorkspaceTaskAPI`。
- `tests/agent/test_tool_control_plane_runtime.py` 覆盖只读工具自动执行、高副作用工具审批后执行、disabled tool 阻断、credential ref broker、sandbox audit 和 trace redaction。
- `tests/api/test_workspace_task_runtime.py` 覆盖 workspace task event stream 中的 `tool_call`、`sandbox_audit`、`approval_required`、`tool_result`。

## Current / Target 边界

Current 是本地 deterministic Tool Control Plane runtime、workspace task tool approval bridge、credential reference broker、sandbox context enforcement 和最小前端审批入口。生产级 rootless / gVisor / Firecracker sandbox、真实网络代理 / egress enforcement、外部 vault / OAuth credential broker、持久 approval DB、exactly-once tool execution、完整 MCP runtime governance 和生产级 DLP 仍是 Target。
