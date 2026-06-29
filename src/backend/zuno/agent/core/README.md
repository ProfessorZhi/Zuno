# Core 运行时迁移源

分类：`migration-source`

## 当前角色

`src/backend/zuno/core/` 当前仍承载 Single GeneralAgent runtime、模型管理、callbacks 和旧 runtime 编排来源。它是当前代码和测试证明的运行时来源，不是已经完成的目标 Agent 层物理形态。

## Target role

目标状态下，GeneralAgent 主循环和 `prepare_context -> agent_loop -> post_turn_commit` 相关 contract 应逐步迁入 `src/backend/zuno/agent/`；模型 gateway、provider wiring 和横切 callback 则按职责迁入 Platform 或对应治理边界。

## 允许新增内容

- 只允许为现有 runtime 添加低风险兼容 facade 或测试保护。
- 允许按小切片把明确归属的 helper 迁入 `agent/` 或 `platform/`，前提是旧 import path 有兼容层。

## 禁止事项

- 禁止一次性移动或拆分 `GeneralAgent` 主循环。
- 禁止把 Zuno runtime 改成多 Agent 架构。
- 禁止改变 streaming、tool execution、memory commit 或 GraphRAG query semantics。

## Focused tests

- `tests/agent/test_general_agent_project_query_runtime.py`
- `tests/agent/test_generalagent_context_memory_runtime.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
