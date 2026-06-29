# Zuno 后端目录边界

## 当前角色

`src/backend/zuno/` 是当前 Python 后端 runtime 真相。它已经有六个目标 facade 目录：`api/`、`agent/`、`memory/`、`capability/`、`knowledge/`、`platform/`，并把资源类目录收进 `resources/`，把兼容类目录收进 `compatibility/`。当前仍保留 `core/`、`services/`、`schema/`、`database/`、`config/`、`tools/`、`utils/` 等旧 runtime 来源和基础设施目录；旧 `mcp_servers`、`middleware`、`evals` import path 由同名 `.py` alias module 承接，不再占用顶层目录。

## Target role

目标状态是让第一次打开 VS Code / Explorer 的人先看到六层表达，再能从 README 判断哪些目录是 target-layer、哪些是 migration-source、哪些是 infrastructure 或 app-resource。物理迁移必须小切片推进，不能为了视觉清爽破坏旧 import path 或 runtime 行为。

## 本批 verifier 覆盖分类

| 分类 | 目录 |
| --- | --- |
| `target-layer` | `api/`、`agent/`、`memory/`、`capability/`、`knowledge/`、`platform/` |
| `infrastructure` | `config/`、`database/` |
| `migration-source` | `core/`、`services/`、`schema/`、`tools/`、`utils/` |
| `app-resource` | `resources/` |
| `compatibility-shell` | `compatibility/` |

兼容 alias module：`mcp_servers.py`、`middleware.py`、`evals.py`。

## 本批物理迁移

- `mcp_servers.py` 承接旧 `zuno.mcp_servers.*` import，真实 MCP server implementations 已迁入 `capability/mcp/servers/`。
- `middleware.py` 承接旧 `zuno.middleware.*` import，真实 HTTP middleware 已迁入 `platform/middleware/`。
- `evals.py` 承接旧 `zuno.evals.*` import，真实 eval tooling 位于 `tools/evals/zuno/`。
- `core/`、`services/`、`utils/`、`schema/`、`tools/`、`database/` 仍保留为当前 runtime 或 public compatibility source，但每个目录都有 README 和 verifier 分类，不再是无理由残留。

## 已退休顶层路径

- `src/backend/fastapi_jwt_auth/`：runtime 直接使用 `zuno.compatibility.vendor.fastapi_jwt_auth`。
- `src/backend/zuno/prompts/` -> `src/backend/zuno/resources/prompts/`
- `src/backend/zuno/fixtures/` -> `src/backend/zuno/resources/fixtures/`
- `src/backend/zuno/system_skills/` -> `src/backend/zuno/resources/system_skills/`
- `src/backend/zuno/legacy/` -> `src/backend/zuno/compatibility/legacy/`
- `src/backend/zuno/vendor/` -> `src/backend/zuno/compatibility/vendor/`
- `src/backend/zuno/mcp_servers/` -> `src/backend/zuno/mcp_servers.py` + `src/backend/zuno/capability/mcp/servers/`
- `src/backend/zuno/middleware/` -> `src/backend/zuno/middleware.py` + `src/backend/zuno/platform/middleware/`
- `src/backend/zuno/evals/` -> `src/backend/zuno/evals.py` + `tools/evals/zuno/`

## 允许新增内容

- 无副作用的目录 README、facade re-export、contract 或 helper。
- 能用 repo verifier 回归检查的目录分类规则。
- 明确旧路径和目标层关系的迁移说明。

## 禁止事项

- 禁止一次性移动 `services/`、拆 `general_agent.py`、改 public API schema、改 DB schema 或改 GraphRAG runtime 行为。
- 禁止把 Target 状态写成 Current。
- 禁止删除旧 import path，除非先有 grep、focused tests 和 rollback plan。
- 禁止把 MCP server implementation、HTTP middleware implementation 或 eval tooling 放回旧 compatibility directory。

## Focused tests

- `pytest -q tests/repo/test_backend_facade_layers.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
- `python .agent/scripts/verify_agent_system.py`
