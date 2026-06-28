# PHASE03：后端六层迁移计划
> 状态：pending。等待 PHASE01 审计结果后执行。

## 目标

把 `api / agent / memory / capability / knowledge / platform` 的物理迁移顺序和风险写清楚。

本 phase 重点解决用户指出的 `src` 目录杂乱问题。目标不是立刻大搬代码，而是形成可执行迁移计划：

```text
src/backend/
  zuno/
    api/
    agent/
    memory/
    capability/
    knowledge/
    platform/
```

`src/backend` 顶层除 `zuno/` 外，任何额外目录都必须被分类为：外部兼容包、临时 vendored 代码、测试夹具、历史残留或应迁移对象，并给出处理动作。

## PHASE01 输入

Thread B 的结论是：当前 `src/backend` 顶层只有 `zuno/` 和 `fastapi_jwt_auth/`；`fastapi_jwt_auth/` 是 public compatibility shell，不能直接删除。

`src/backend/zuno` 已经有 `api / agent / memory / capability / knowledge / platform` 的 facade 方向，但真实实现仍大量分布在 `core/`、`services/`、`database/`、`schema/`、`middleware/`、`mcp_servers/`、`vendor/` 等旧路径。PHASE03 必须写 facade-first migration plan，不做物理大搬家。

高风险约束：

- `tests/legacy_guards/test_zuno_alias_imports.py` 固定大量旧导入仍需可用。
- `tests/repo/test_backend_facade_layers.py` 固定六层 facade 是目标公开导入面。
- `GeneralAgent`、GraphRAG/retrieval、DB/settings/vendor 是高冲突区，不能在 PHASE03 直接迁移。

## 验收

每层都有迁移候选、禁止边界、focused tests、rollback plan。

输出至少包括：

```text
current path | target layer | move type | public API risk | tests | rollback
```
