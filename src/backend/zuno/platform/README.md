# Platform 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/platform/` 目前是平台能力的轻量 facade，当前公开 execution policy 相关 contract 和 helper，并提供 `model_gateway.py`、`security/`、`observability/`、`storage/` 和 `vendor/` import guard。PHASE09 已在 `security/governance.py` 固定 input / retrieval / tool / output gate、ToolSecurityProfile、SandboxAuditEvent 和 redaction contract。真实 DB、settings、storage、queue、MCP、LLM、rootless/gVisor/Firecracker sandbox、vendor compat 等底座仍分布在旧路径或仍是 Target。

`config/` 和 `database/` 本批保持 infrastructure source：前者保存配置资源和 helper，后者保存 DB session、metadata、DAO 和 models。它们是 Platform 的目标归属，不是已经完成物理迁移的证据。

## Target role

目标状态下，Platform 层负责配置、数据库 wiring、外部 provider、存储、队列、MCP server、sandbox、vendor compatibility 和执行策略等底座能力。它支撑上层，不反向依赖 API 或 Agent 业务编排。

`platform/vendor/` 是第三方 shim 的目标 owner；`platform/compatibility/` 是旧 import registry 和当前兼容路径。PHASE02 不移动 `fastapi_jwt_auth`，只固定两者的归属和 verifier guard。

## 允许新增内容

- 无副作用的 platform contract、execution policy helper、compat facade 和边界说明。
- Security governance contract、policy decision schema、sandbox audit event、redaction helper。
- 指向旧 settings、database、vendor、MCP、storage owner 的迁移说明。
- 不改变默认配置、schema 或外部 entrypoint 的 wrapper。

## 禁止事项

- 禁止直接迁移 DB schema、DAO、settings defaults、MCP server、queue worker、storage、model gateway 或 vendor compat 包。
- 禁止破坏 `zuno.database.*`、`zuno.settings`、`zuno.services.execution_policy`、`zuno.mcp_servers.*` 或 `zuno.compatibility.vendor.fastapi_jwt_auth` 兼容 import path。
- 禁止在 platform 中承载 API route、GeneralAgent loop、GraphRAG query behavior 或 product use case 编排。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_platform_layer_surfaces.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/api/test_fastapi_jwt_auth_compat.py`
- policy / tool / storage / queue focused tests
- `tests/repo/test_static_target_layer_imports.py`
