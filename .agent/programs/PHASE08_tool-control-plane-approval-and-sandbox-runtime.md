# PHASE08 tool-control-plane-approval-and-sandbox-runtime

status: active

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
pytest -q tests/agent/test_tool_control_plane_contract.py tests/security tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
```
