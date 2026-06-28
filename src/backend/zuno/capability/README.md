# Capability 层边界

## 当前角色

`src/backend/zuno/capability/` 目前是 capability metadata 和 selector foundation 的 facade，公开 CapabilityRecord、CapabilityRegistry、DynamicCapabilitySelector 和 selection trace 等 contract。真实实现仍在 `src/backend/zuno/services/application/capabilities/` 和相关 registry 路径。

## Target role

目标状态下，Capability 层负责 ToolCard / capability metadata、权限、健康状态、成本提示、能力召回与 schema selection。它为 Agent 提供可选择能力，不直接拥有工具执行 runtime 或 API response shape。

## 允许新增内容

- capability contract、selector trace、permission / health / cost 相关轻量类型。
- 不加载 provider、DB、tool runtime 的 facade re-export。
- 指向旧 application capability owner 的边界说明。

## 禁止事项

- 禁止把 ToolCard retrieval、Native BM25 capability search 或生产级 dynamic orchestration 写成已完成 Current。
- 禁止直接迁移或删除 `zuno.services.application.capabilities`、`zuno.services.capability_registry` 等旧 import path。
- 禁止改变工具权限、执行模式、API capability search response key 或 runtime tool wiring。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_capability_system.py`
- `tests/agent/test_capability_registry.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
