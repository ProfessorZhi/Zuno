# Evals 兼容边界

分类：`compatibility-shell`

## 当前角色

`src/backend/zuno/evals/` 当前是 import namespace bridge。真实 eval 工具、runner、数据集和报告入口在 `tools/evals/zuno/`，本目录只让历史 `zuno.evals.*` import 可以解析到工具侧。

## Target role

Eval 不属于后端 runtime 一等层。长期主路径是 `tools/evals/zuno/`，后端包内只允许保留必要兼容桥，避免 eval runner 被误认为 runtime feature。

## 允许新增内容

- 只允许无副作用 namespace bridge。
- 允许记录 eval import 迁移说明和 focused verification。

## 禁止事项

- 禁止把 eval runner、数据集、运行报告或本地产物放回后端 package。
- 禁止把 eval bridge 写成 runtime current capability。

## Focused tests

- `tests/repo/test_repo_structure_consistency.py`
- `tests/evals/`
- `tools/evals/zuno/AGENTS.md` 中列出的 eval focused tests
