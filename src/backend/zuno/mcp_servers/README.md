# MCP Servers 兼容边界

分类：`compatibility-shell`

## 当前角色

`src/backend/zuno/mcp_servers/` 现在只保留旧 `zuno.mcp_servers.*` import path。真实 MCP server entrypoint 已迁入 `src/backend/zuno/capability/mcp/servers/`。

## Target role

MCP server、MCP tool provider 和远端 MCP proxy 属于 Capability 层的工具能力边界。旧 `mcp_servers/` 只作为 compatibility shell 暂留，等外部配置、历史脚本和 import guard 都迁完后再退休。

## 允许新增内容

- 只允许保留 `__init__.py` 这种无副作用兼容查找壳。
- 允许记录旧路径到新路径的迁移说明。

## 禁止事项

- 禁止把新的 MCP server 实现继续放回本目录。
- 禁止恢复 `zuno/mcp_servers/remote_proxy/main.py` 作为配置文件里的主 entrypoint。
- 禁止改变旧 `zuno.mcp_servers.*` import 的兼容语义，除非先更新 legacy guard 和配置迁移说明。

## Focused tests

- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/legacy_guards/test_zuno_config_resource_aliases.py`
- `tests/repo/test_repo_structure_consistency.py`
