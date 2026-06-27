# PHASE03：Skill / Template / Program 系统收口

## 目标

把 `.agent/references`、`.agent/templates` 和 `.agent/programs` 的职责分开，形成可复用的本地 skill system。

## 范围

- `.agent/references/README.md`
- `.agent/references/*.md`
- `.agent/templates/README.md`
- `.agent/templates/*.md`
- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/architecture/future/programs/**`

## 可并行线程

- Thread A：references skill 文件结构和重复内容审计/收口。
- Thread B：templates 是否只保留执行骨架，不混入项目事实。
- Thread C：active program 与 queued program 边界检查。

最终写入必须由一个 integration 线程统一合并。

## 不做

- 不把 queued program 移入 `.agent/programs/`。
- 不把一次性运行日志写进 skill。
- 不删除历史证据。

## 验收

- 每个 skill 文件能回答何时使用、读哪些文件、禁止什么、跑哪些验证。
- `.agent/references` 只沉淀 skill / lesson / playbook，不变成普通目录索引。
- 每个 template 只提供输出骨架或提示词骨架。
- `.agent/programs` 仍然只有一层 active program。

## 验证

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_repo_hygiene.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```
