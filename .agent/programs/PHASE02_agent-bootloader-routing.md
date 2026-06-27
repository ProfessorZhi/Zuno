# PHASE02：Agent Bootloader 与 Routing 收口

## 目标

让 `AGENTS.md` 成为清晰、短、稳定的项目级 bootloader；让 `.agent/system.yaml` 负责机器可读路由；让二者不重复长篇知识。

## 范围

- `AGENTS.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/task-routing.md`
- `.agent/references/workflow.md`
- `.agent/references/current-program.md`
- 必要的 verifier / repo tests

## 可并行线程

本 phase 建议单一写入线程执行。可以先开只读 review 线程审计 `AGENTS.md` 和 `.agent/system.yaml`，但最终写入必须串行。

## 不做

- 不改 runtime。
- 不改 target architecture 正文。
- 不新增新的工作模式术语，除非同步到 `.agent/system.yaml` 和 verifier。

## 验收

- `AGENTS.md` 只保留入口、边界、阅读顺序、任务路由、收尾规则。
- `.agent/system.yaml` 能表达 work modes、program rules、skill routes、stop conditions。
- `current-program.md` 与 `.agent/programs/current.md` 不冲突。

## 验证

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```
