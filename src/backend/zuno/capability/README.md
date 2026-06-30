# Capability 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/capability/` 目前是 capability metadata、ToolCard retrieval 和 selector foundation 的 facade，公开 CapabilityRecord、ToolCard、CapabilityRegistry、ToolCardRegistry、NativeBM25Retriever、DynamicCapabilitySelector 和 selection trace 等 contract。当前已提供 `contracts.py`、`registry.py`、`selector.py`、`policy.py`、`execution.py`、`trace.py` 和 `retrieval.py` 这些无副作用目标层薄入口。真实实现仍在 `src/backend/zuno/platform/services/application/capabilities/` 和相关 registry 路径。

`capability/tools/` 不按 CLI / API 拆成两类顶层目录。CLI / API 是 execution adapter、runtime type 或 provider metadata，不是 capability 的主分类。

PHASE02 的 provider 分类入口是 `docs/architecture/repo-ownership-matrix.md` 和 `CAPABILITY_TOOL_PROVIDER_CLASSIFICATIONS` / `CAPABILITY_MCP_SERVER_CLASSIFICATIONS`。新增 tool 或 MCP server 目录前，必须先声明分类、target owner、compat path、测试和 verifier。

## Target role

目标状态下，Capability 层负责 ToolCard / capability metadata、权限、健康状态、成本提示、能力召回与 schema selection。它为 Agent 提供可选择能力，不直接拥有工具执行 runtime 或 API response shape。

工具目录优先按能力语义和 owner 管理；CLI / API 只作为执行适配信息进入 ToolCard、manifest 或 runtime metadata。

当前分类只表达目录治理，不改变 runtime 行为：`builtin-provider`、`provider-adapter`、`model-provider-adapter`、`api-provider-adapter`、`executor-adapter`、`builtin-converter`、`builtin-domain-tool`、`mcp-provider`、`mcp-smoke-server` 和 `mcp-compat-proxy` 都仍归 Capability 层管理。

## 允许新增内容

- capability contract、selector trace、permission / health / cost 相关轻量类型。
- 不加载 provider、DB、tool runtime 的 facade re-export。
- 指向旧 application capability owner 的边界说明。

## 禁止事项

- 禁止把生产级 ToolCard retrieval、optional vector capability search、完整 runtime tool filtering 或生产级 dynamic orchestration 写成已完成 Current。
- 禁止直接迁移或删除 `zuno.services.application.capabilities`、`zuno.services.capability_registry` 等旧 import path。
- 禁止改变工具权限、执行模式、API capability search response key 或 runtime tool wiring。
- 禁止把 `capability/tools/` 按 CLI / API 二分为顶层分类，除非后续有独立 ToolCard / execution adapter 迁移计划。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_capability_layer_surfaces.py`
- `tests/agent/test_capability_system.py`
- `tests/agent/test_capability_registry.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_static_target_layer_imports.py`
