# Middleware 兼容边界

分类：`compatibility-shell`

## 当前角色

`src/backend/zuno/middleware/` 现在只保留旧 `zuno.middleware.*` import path。真实 HTTP middleware 实现已迁入 `src/backend/zuno/platform/middleware/`，`src/backend/zuno/main.py` 也直接使用新路径。

## Target role

HTTP middleware 属于 Platform 层的请求底座能力。它支撑 FastAPI app startup 和 request context，不拥有 API route、业务用例或 Agent runtime 行为。

## 允许新增内容

- 只允许保留无副作用的兼容 alias。
- 允许记录旧路径到 `platform/middleware/` 的迁移说明。

## 禁止事项

- 禁止把 middleware 实现文件放回本目录。
- 禁止改变 `TraceIDMiddleware` 的 trace header、error response 或 context 写入行为。
- 禁止改变 `WhitelistMiddleware` 的白名单匹配语义。

## Focused tests

- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_repo_structure_consistency.py`
- API startup/import focused tests
