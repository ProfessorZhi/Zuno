# Fixtures 目录边界

分类：`app-resource`

## 当前角色

`src/backend/zuno/fixtures/` 当前保存 runtime 或测试可能消费的内置资源。它是 app-resource，存在和 `tests/fixtures`、`examples/` 或 runtime default resource 的边界混合风险。

## Target role

目标状态下，fixtures 必须按用途拆清：测试专用进入 `tests/`，示例输入进入 `examples/`，runtime 默认资源才留在后端 app-resource 中。本轮不做物理迁移，只先固定分类和迁移前置条件。

## 允许新增内容

- fixture consumer、用途和迁移候选说明。
- 不改变资源内容和路径的 README 或 metadata。
- 后续把测试 fixture、example 和 runtime resource 分开的计划说明。

## 禁止事项

- 禁止移动或删除 fixture 资源，除非 grep 证明消费者并有 focused tests。
- 禁止把测试专用 fixture 当作 runtime default resource 推广。
- 禁止让 API、DB、GraphRAG 或 Agent runtime 隐式依赖未记录的 fixture 路径。

## Focused tests

- fixture consumer focused tests
- `tests/repo/test_repo_structure_consistency.py`
- `python tools/scripts/verify_repo_structure.py`
