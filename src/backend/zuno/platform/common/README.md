# Utils 迁移源

分类：`migration-source`

## 当前角色

`src/backend/zuno/utils/` 当前保存通用 helper，例如文件路径、context、模型输出、runtime observability 和配置转换。它被 core、services、tools 和 tests 共同引用，因此不能直接整体搬迁。

## Target role

目标状态下，helper 不应长期停留在泛化 utils 桶里。每个 helper 要按实际 owner 迁入 `agent/`、`capability/`、`knowledge/`、`platform/` 或具体 service 边界；旧 `zuno.utils.*` import path 在迁移期继续兼容。

## 允许新增内容

- 允许小型纯函数 helper 暂留，前提是职责明确且有测试。
- 允许按 owner 小切片迁移，并保留旧路径 re-export。

## 禁止事项

- 禁止把新业务逻辑放进泛化 utils。
- 禁止无测试移动被 core/services/tools 共享的 helper。
- 禁止改变 trace id、文件路径、模型输出或 MCP config 转换语义。

## Focused tests

- `tests/agent/test_runtime_observability.py`
- `tests/storage/test_storage_utils.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
