# Agent 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/agent/` 目前是轻量 facade，通过 `__all__` 和 lazy import 暴露 `GeneralAgent`、agent config、stream state，以及 context runtime contract。当前已提供 `runtime.py`、`context.py`、`post_turn.py`、`state.py`、`streaming.py` 和 `tool_bridge.py` 这些无副作用目标层薄入口。真实 Single GeneralAgent runtime 仍主要在 `src/backend/zuno/agent/core/agents/` 和相关 application context 路径中。

## Target role

目标状态下，Agent 层拥有同步对话主线：prepare context、Single GeneralAgent loop、stream state、post-turn 边界和与 capability / knowledge / memory 的编排契约。它不是多 Agent runtime，也不是 GraphRAG 的独立聊天入口。

## 允许新增内容

- 小而纯的 agent contract、dataclass、enum 或 lazy re-export。
- 指向旧 runtime owner 的边界说明和迁移注释。
- 不改变执行顺序的 facade 层补充。

## 禁止事项

- 禁止搬动或重写 `GeneralAgent` 主循环、LangGraph runtime、streaming 行为或 tool execution 行为。
- 禁止直接迁移或删除 `zuno.core.agents`、`zuno.services.application.context` 等旧 import path。
- 禁止把 Codex 执行工作流里的多 agent 写成 Zuno runtime 当前架构。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_agent_layer_surfaces.py`
- `tests/agent/test_general_agent*`
- `tests/agent/test_generalagent_context_memory_runtime.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_static_target_layer_imports.py`
