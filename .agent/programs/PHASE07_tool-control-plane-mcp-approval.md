# PHASE07 Tool Control Plane MCP Approval

status: pending

## 目标

把工具层从零散函数集合升级成 Tool Control Plane：ToolCard / manifest、selector、policy、approval、executor adapter、MCP 和 sandbox 都由统一 contract 治理。

## 步骤

- [ ] 定义 ToolCard manifest 字段和执行模式。
- [ ] ToolCard 字段至少包含：`tool_id`、`owner`、`capability_domain`、`description_for_model`、`input_schema`、`output_schema`、`execution_mode`、`trust_tier`、`side_effect_level`、`approval_policy`、`sandbox_profile`、`credential_policy`、`network_policy`、`audit_policy`、`budget`、`failure_modes`。
- [ ] 区分 capability domain 与 execution adapter。
- [ ] 建立 executor registry，支持 local function、SDK、API、CLI、SSH、MCP local、MCP remote 和 sandbox。
- [ ] 建立 side-effect 风险矩阵：`none`、`read`、`write_local`、`write_external`、`destructive`。
- [ ] 对高副作用工具建立 approval gate。
- [ ] 定义 MCP trust governance：server trust list、transport、auth、allowed tools、scope、origin / network policy、credential broker、untrusted content labeling。
- [ ] 定义 result normalizer，所有 executor 输出统一成 `status`、`data`、`summary`、`error`、`audit_ref`、`trace_span_id`。
- [ ] 更新 send_email、CLI、OpenAPI、MCP provider 的测试。

## 输入 / 输出文件

输入：

- `src/backend/zuno/capability/**`
- `src/backend/zuno/capability/tools/**`
- `src/backend/zuno/capability/mcp/**`
- 现有 send_email / CLI / OpenAPI / MCP provider tests。

输出：

- ToolCard v1 schema。
- executor registry。
- policy / approval gate。
- MCP local / remote trust contract。
- result normalizer。
- tool trajectory trace fields。

## 依赖与阻塞

- 依赖 PHASE02 ownership matrix，工具域按 capability domain 归属，不按 API / CLI 顶层分类。
- 依赖 PHASE05 runtime interrupt / resume，approval gate 必须能暂停并恢复 task。
- PHASE09 sandbox 必须消费本 phase 的 `side_effect_level`、`sandbox_profile`、`network_policy`、`credential_policy`。

## 首批工具切片

- `file.read_scoped`：只读 workspace 文件，验证 ACL、path allowlist 和 audit。
- `knowledge.agentic_graphrag_query`：返回 EvidenceBundle，不返回裸 chunk。
- `code.run_python_sandbox`：进入 execution sandbox，默认 no-network，无 secrets。
- `mail.draft_and_send`：draft 可自动，真正 send 必须 approval。

## 验收

- 工具不再按 API / CLI 顶层分类；API / CLI 是 execution adapter。
- 高副作用工具不会裸跑。
- Tool call 有 trace、audit、result normalization。
- 未完成 approval / sandbox 的高副作用工具不能写成 Current；只能写成 Target 或 disabled capability。

## 验证

```powershell
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_layer_surfaces.py tests/tools -p no:cacheprovider
```
