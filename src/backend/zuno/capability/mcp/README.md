# MCP Capability 边界

## 当前角色

`capability/mcp/` 是 MCP tool binding、LangChain tool adapter 和工具注册表的唯一 capability 入口。它只描述工具能力和执行约束，不拥有 Product API、Agent Run 状态或持久化 schema。

所有产品工具调用都经过 `ToolInvocationGateway`。缺少注册 adapter、显式安全决策、持久化 Unit of Work 或 effect receipt 时，调用必须在 provider effect 之前停止。

## 允许与禁止

- 允许定义 MCP binding、工具 manifest、adapter 和 capability-level result normalization。
- 禁止在 request handler 中直接调用 provider 或 `binding.ainvoke`。
- 禁止在此目录定义 Product response shape、Agent Run lifecycle 或数据库 owner。
- side-effect 工具必须携带显式 `approval_decision_ref` 与 `approval_adapter_ref`。

## 验证入口

- `python tools/scripts/verify_tool_execution_bypass.py`
- `tests/agent/test_tool_control_plane_runtime.py`
- `tests/capability/test_tool_runtime_batch.py`
