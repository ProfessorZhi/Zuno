# Platform 层边界

## 当前角色

`src/backend/zuno/platform/` 目前是平台能力的轻量 facade，当前只公开 execution policy 相关 contract 和 helper。真实 DB、settings、storage、queue、MCP、LLM、sandbox、vendor compat 等底座仍分布在旧路径中。

## Target role

目标状态下，Platform 层负责配置、数据库 wiring、外部 provider、存储、队列、MCP server、sandbox、vendor compatibility 和执行策略等底座能力。它支撑上层，不反向依赖 API 或 Agent 业务编排。

## 允许新增内容

- 无副作用的 platform contract、execution policy helper、compat facade 和边界说明。
- 指向旧 settings、database、vendor、MCP、storage owner 的迁移说明。
- 不改变默认配置、schema 或外部 entrypoint 的 wrapper。

## 禁止事项

- 禁止直接迁移 DB schema、DAO、settings defaults、MCP server、queue worker、storage、model gateway 或 vendor compat 包。
- 禁止破坏 `zuno.database.*`、`zuno.settings`、`zuno.services.execution_policy`、`zuno.mcp_servers.*` 或 `fastapi_jwt_auth` 旧 import path。
- 禁止在 platform 中承载 API route、GeneralAgent loop、GraphRAG query behavior 或 product use case 编排。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/api/test_fastapi_jwt_auth_compat.py`
- policy / tool / storage / queue focused tests
