# Platform Middleware 边界

## 当前角色

`src/backend/zuno/platform/middleware/` 承载 FastAPI app startup 使用的 HTTP middleware 实现。旧 `zuno.middleware.*` import path 继续通过 compatibility shell 指向这里。

## Target role

Middleware 是 Platform 层的 HTTP 底座能力：它处理 trace id、白名单状态和请求链横切行为，不拥有 API route、DTO 或业务用例。

## 禁止事项

- 禁止改变 trace id header、error response 或 whitelist matching 语义。
- 禁止把 API route、auth service 或业务逻辑放入 middleware。
- 禁止删除旧 `zuno.middleware.*` 兼容路径，除非 legacy guard 明确退休。

## Focused tests

- `tests/legacy_guards/test_zuno_alias_imports.py`
- API startup/import focused tests
