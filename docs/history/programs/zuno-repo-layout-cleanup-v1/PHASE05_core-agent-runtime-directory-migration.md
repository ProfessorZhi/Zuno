# PHASE05：Core Agent Runtime Directory Migration

> 状态：planned。目标 PR：Program3 PR5。

## 目标

让 `core/` 从旧 runtime 主线变薄，把 Agent 主入口和模型网关相关边界迁入 `agent/` 或 `platform/`。

## 迁移范围

| 当前来源 | 目标位置 | 策略 |
| --- | --- | --- |
| `core/agents/` | `agent/` | 先 facade，再拆 runtime/context/tool_bridge/post_turn |
| model/provider 管理 | `platform/model_gateway.py` 或 `platform/model_gateway/` | 只迁移清晰边界，不改模型调用语义 |

## 禁止范围

- 不重写 Agent 主循环行为。
- 不把 LangGraph/runtime upgrade 混进 Program3。
- 不改 streaming contract。

## 验收

- `core/` 不再作为 active 架构入口。
- 旧 `zuno.core.*` import 有兼容 guard。
- `agent/` 是 Agent runtime 的正式入口。

## 验证命令

- `pytest -q tests/agent tests/api/test_completion* tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
