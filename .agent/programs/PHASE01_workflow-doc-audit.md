# PHASE01：工作流与文档系统只读审计

## 目标

在不改文件的前提下，审计当前 `AGENTS.md`、`.agent/`、`docs/`、`tools/scripts` 和 `tests/repo` 是否能组成自洽的本地 Agent 工作流。

## 范围

- `AGENTS.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/**`
- `.agent/templates/**`
- `.agent/programs/**`
- `docs/architecture/**`
- `tools/scripts/**`
- `tests/repo/**`

## 可并行线程

- Thread A：`AGENTS.md`、`.agent/README.md`、`.agent/system.yaml` 入口和路由审计。
- Thread B：`.agent/references`、`.agent/templates` skill / template 边界审计。
- Thread C：docs entrypoints、verifiers、repo tests 防漂移能力审计。

## 不做

- 不修改文件。
- 不运行 runtime tests。
- 不移动目录。
- 不归档旧计划。

## 验收

- 输出一张问题表：问题、证据文件、影响、建议 phase。
- 区分“必须修”和“可以后续优化”。
- 明确 Program 1 后续 phase 是否需要调整。

## 验证

只读审计不提交。可以运行：

```powershell
git status --short --branch
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_docs_entrypoints.py
```
