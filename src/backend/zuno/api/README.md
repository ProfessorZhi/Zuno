# API 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/api/` 是当前 HTTP 边界，承载 route、DTO、auth、response envelope、SSE 和 API 兼容入口。它已经属于六层目标里的 `api` 层，但目录内仍有过渡期 service import，不能把它误读成业务实现已经全部下沉完成。

`src/backend/zuno/schema/` 仍是 API DTO / Pydantic schema 的 migration-source。短期内 API 层可以引用旧 schema，但公开字段、response envelope 和前端 contract 仍由 API 边界负责。

## Target role

目标状态下，API 层只负责传输协议、公开契约、认证、校验、错误映射和响应形状；业务用例编排继续进入 application service 或更明确的 owner 层。前端只能依赖公开 DTO 和 response key，不能依赖 Agent、GraphRAG、DB 或内部 service 对象。

## 允许新增内容

- 新的 HTTP route、request / response DTO、auth 或 middleware 边界说明。
- 保持旧 response key 的兼容 wrapper。
- 不触发重 runtime import 的轻量 facade 导出。

## 禁止事项

- 禁止在 API 层直接实现 Agent loop、retrieval、GraphRAG、memory commit 或数据库 schema 逻辑。
- 禁止为了目录整洁直接迁移或删除旧 `zuno.api.*` import path。
- 禁止改变 URL、DTO 字段、SSE event、auth 行为或 response envelope，除非有单独 public API 变更计划。

## Focused tests

- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/api/**`
- `tests/frontend/test_product_wiring_v1_api_contract.py`
- `tests/repo/test_backend_facade_layers.py`
