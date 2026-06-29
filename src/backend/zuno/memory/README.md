# Memory 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/memory/` 目前是 memory foundation 的轻量 facade，暴露 raw event、task summary、memory scope、retention policy 和 in-memory layer store 等基础 contract。真实实现仍在 `src/backend/zuno/services/memory/` 等旧路径中。

## Target role

目标状态下，Memory 层负责上下文前的可检索记忆、对话后的 raw event 追加、summary compression、structured extraction 和 source event 追踪。它不等同于聊天历史拼接，也不拥有外部知识检索本体。

## 允许新增内容

- 无副作用的 memory contract、scope、policy、trace 类型。
- 指向旧 `services/memory` owner 的 lazy facade 或 README 边界说明。
- 不触碰持久化和 runtime 行为的小型 wrapper。

## 禁止事项

- 禁止直接迁移 DB-backed memory、事件存储、summary 写入或 GeneralAgent memory runtime。
- 禁止破坏 `zuno.services.memory.*` 旧 import path。
- 禁止把成熟记忆提取、检索、合并能力写成已经完成的 Current runtime。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_memory_layers.py`
- `tests/agent/test_generalagent_context_memory_runtime.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
