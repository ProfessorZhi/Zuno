# System Skills 目录边界

分类：`app-resource`

## 当前角色

`src/backend/zuno/resources/system_skills/` 当前保存 runtime skill resource 和系统技能相关内容。它是应用资源，不是 Agent 工作流里的 `.agent/references/` skill，也不是仓库维护模板。

## Target role

目标状态下，系统技能作为 Capability 或 Agent resource 被选择、加载和注入；当前先作为 app-resource 收敛到 `resources/system_skills/`，直到 capability skill loading、resource path 和 focused tests 证明可以继续细分 owner。

## 允许新增内容

- skill resource 的边界说明、加载路径说明和迁移计划。
- 不改变 skill 内容语义的 README 或 metadata 说明。
- 指向 Capability / Agent resource owner 的分类文档。

## 禁止事项

- 禁止改变 runtime skill loading、默认系统 prompt、权限或工具注入行为。
- 禁止把 Codex `.agent/references/` 工作流 skill 混入 runtime `system_skills/`。
- 禁止删除资源文件或移动目录，除非有消费者 grep 和 focused tests。
- 禁止恢复顶层 `src/backend/zuno/system_skills/`。

## Focused tests

- skill / tool focused tests
- `tests/repo/test_repo_structure_consistency.py`
- `python tools/scripts/verify_repo_structure.py`
