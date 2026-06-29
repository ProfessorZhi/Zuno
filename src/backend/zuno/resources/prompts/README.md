# Prompts 目录边界

分类：`app-resource`

## 当前角色

`src/backend/zuno/resources/prompts/` 当前保存 completion、LLM、MCP、rewrite、skill、template 和 tool prompt 资源。它是 runtime prompt resource，不是 `.agent/templates/` 执行骨架。

## Target role

目标状态下，prompt 资源应按 Agent、Knowledge、Capability 或 Platform owner 被引用和版本化；短期内 `resources/prompts/` 作为 app-resource，由 README 和 verifier 说明它不是新业务层。

## 允许新增内容

- prompt resource 的用途、owner 和迁移说明。
- 不改变 prompt 文本和加载路径的 README 或 metadata 说明。
- 指向 Agent / Knowledge / Capability resource 边界的分类。

## 禁止事项

- 禁止修改 prompt 内容、prompt id 或默认模型行为。
- 禁止把 `.agent/templates/` 的 Codex 执行模板放入 runtime prompts。
- 禁止把 prompt 资源写成已完成的 mature memory/capability/knowledge product behavior。
- 禁止恢复顶层 `src/backend/zuno/prompts/`。

## Focused tests

- prompt consumer focused tests
- `tests/repo/test_repo_structure_consistency.py`
- `python tools/scripts/verify_repo_structure.py`
