# MCP Capability 边界

## 当前角色

`src/backend/zuno/capability/mcp/` 承载 MCP 相关 capability entrypoint。当前已把 MCP server implementations 放到 `servers/`，旧 `zuno.mcp_servers.*` import 通过 compatibility shell 指向这里。

## Target role

MCP server、remote proxy 和 MCP tool provider 属于 Capability 层的工具能力来源。Capability 层负责把这些能力交给 Agent 选择和执行治理，不拥有 API response shape 或持久化 schema。

## 禁止事项

- 禁止在这里绕过旧 `zuno.mcp_servers.*` 兼容 guard。
- 禁止改变 MCP config JSON 的 public fields。
- 禁止把 MCP server runtime 写进 Platform 或 API use case。

## Focused tests

- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/legacy_guards/test_zuno_config_resource_aliases.py`
