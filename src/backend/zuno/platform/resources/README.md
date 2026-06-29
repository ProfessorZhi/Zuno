# Zuno Runtime Resources

## 当前角色

分类：`app-resource`

`resources/` 收纳运行时资源：prompt 文本、内置知识库 fixture、系统技能包。它们不是 API、Agent、Memory、Capability、Knowledge 或 Platform 的业务实现层。

## Target role

目标是让 `src/backend/zuno` 顶层不再同时暴露 `prompts/`、`fixtures/`、`system_skills/` 三个资源目录，而是统一从 `resources/` 进入。

## 禁止事项

- 禁止把 `.agent/references/` 的本地工作流 skill 放进 runtime resources。
- 禁止把运行生成物、缓存或用户上传文件放进本目录。
- 禁止恢复旧的顶层 `prompts/`、`fixtures/`、`system_skills/` 目录。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`
