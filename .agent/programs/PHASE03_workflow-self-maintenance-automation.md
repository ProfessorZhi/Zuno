# PHASE03 Workflow Self Maintenance Automation

status: pending

## 目标

让工作流自洽和自我维护成为机器可检查能力：长期规则能被分类、写回、模板化并进入 verifier / tests。

## 范围

- 梳理 `AGENTS.md`、`.agent/references/workflow*.md`、`.agent/templates/*`、`.agent/scripts/*`。
- 为 program open / phase closure / archive / docs sync 增加或修正检查。
- 明确一次性指令、长期规则、架构治理、Codex 执行规则和模板规则的写回路径。

## 禁止范围

- 不把高频执行细节塞进 `docs/`。
- 不让 `.agent/templates/` 承载项目事实。
- 不新增无法被 verifier 或 tests 约束的长期规则。

## 验收闸门

- workflow 更新规则有入口、模板、verifier 和 repo test 覆盖。
- Program closure 自维护审查可复用。
- 旧规则不再依赖对话记忆。

## 验证命令

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```
