# Zuno 后端目录边界

## 当前角色

`src/backend/zuno/` 是当前 Python 后端 runtime 真相。它已经有六个目标 facade 目录：`api/`、`agent/`、`memory/`、`capability/`、`knowledge/`、`platform/`，并把资源类目录收进 `resources/`，把兼容类目录收进 `compatibility/`。当前仍保留 `core/`、`services/`、`schema/`、`database/`、`config/`、`tools/` 等旧 runtime 来源和基础设施目录。

## Target role

目标状态是让第一次打开 VS Code / Explorer 的人先看到六层表达，再能从 README 判断哪些目录是 target-layer、哪些是 migration-source、哪些是 infrastructure 或 app-resource。物理迁移必须小切片推进，不能为了视觉清爽破坏旧 import path 或 runtime 行为。

## 本批 verifier 覆盖分类

| 分类 | 目录 |
| --- | --- |
| `target-layer` | `api/`、`agent/`、`memory/`、`capability/`、`knowledge/`、`platform/` |
| `infrastructure` | `config/`、`database/` |
| `migration-source` | `schema/`、`tools/` |
| `app-resource` | `resources/` |
| `compatibility-shell` | `compatibility/` |

## 本批延后分类

`core/`、`services/`、`mcp_servers/`、`utils/` 仍按 PHASE06 的 audit 处理，但本批不把它们纳入 README/verifier 分类契约。原因是这些目录牵涉 runtime 主循环、service implementation、MCP adapter 或 legacy helper，后续必须按单独小切片补充 grep、focused tests 和 rollback plan。

## 已退休顶层路径

- `src/backend/fastapi_jwt_auth/`：runtime 直接使用 `zuno.compatibility.vendor.fastapi_jwt_auth`。
- `src/backend/zuno/prompts/` -> `src/backend/zuno/resources/prompts/`
- `src/backend/zuno/fixtures/` -> `src/backend/zuno/resources/fixtures/`
- `src/backend/zuno/system_skills/` -> `src/backend/zuno/resources/system_skills/`
- `src/backend/zuno/legacy/` -> `src/backend/zuno/compatibility/legacy/`
- `src/backend/zuno/vendor/` -> `src/backend/zuno/compatibility/vendor/`

## 允许新增内容

- 无副作用的目录 README、facade re-export、contract 或 helper。
- 能用 repo verifier 回归检查的目录分类规则。
- 明确旧路径和目标层关系的迁移说明。

## 禁止事项

- 禁止一次性移动 `services/`、拆 `general_agent.py`、改 public API schema、改 DB schema 或改 GraphRAG runtime 行为。
- 禁止把 Target 状态写成 Current。
- 禁止删除旧 import path，除非先有 grep、focused tests 和 rollback plan。

## Focused tests

- `pytest -q tests/repo/test_backend_facade_layers.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
- `python .agent/scripts/verify_agent_system.py`
