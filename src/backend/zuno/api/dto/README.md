# Schema 目录边界

分类：`migration-source`

## 当前角色

`src/backend/zuno/api/dto/` 当前保存 DTO、Pydantic schema 和 API request / response 相关类型。旧 public import path `zuno.schema.*` 由 `platform/compatibility/legacy_aliases.py` 映射到这里；它是兼容 alias，不是仍存在的物理目录。

## Target role

目标状态下，公开 HTTP DTO 应由 API 层拥有或通过 API 层清晰暴露；仍被旧路径消费的 `zuno.schema.*` 先通过 legacy alias 保留。是否整理 DTO 文件、字段或导出面，必须由 API contract tests 证明。

## 允许新增内容

- DTO 归属说明、兼容 re-export 和不会改变字段语义的 contract 文档。
- 将 schema 分组映射到 API / Agent / Knowledge / Capability / Platform 的迁移说明。
- 小型、无副作用、已有 API contract tests 覆盖的类型整理。

## 禁止事项

- 禁止改变 public API 字段、默认值、response envelope、SSE event 或前端 contract。
- 禁止直接删除 `zuno.schema.*` import path 或把它误写成物理 `src/backend/zuno/schema/` Current 目录。
- 禁止把 GraphRAG runtime、DB model 或 Agent loop 状态混入 API DTO。

## Focused tests

- `tests/api/**`
- `tests/frontend/test_product_wiring_v1_api_contract.py`
- `tests/repo/test_backend_facade_layers.py`
- `python tools/scripts/verify_repo_structure.py`
