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

## 需要先读取

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/workflow.md`
- `.agent/references/workflow-governance.md`
- `.agent/references/workflow-update-policy.md`
- `.agent/references/workflow-maintenance-checklist.md`
- `.agent/templates/README.md`
- `.agent/templates/phase-plan.md`
- `.agent/templates/phase-closure-report.md`

## 需要修改的文件

- `AGENTS.md`
- `.agent/references/workflow*.md`
- `.agent/templates/*`
- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify_doc_boundaries.py`
- `.agent/scripts/verify-workflow.ps1`
- `tests/repo/test_agent_system.py`

## 执行拆解

1. 分类长期规则：一次性指令、可复用项目规则、架构治理、Codex 执行规则、模板规则、机器可检查规则。
2. 将长期规则写入 `.agent/references/`，只把稳定入口保留在 `AGENTS.md`。
3. 检查 `.agent/templates/` 是否仍是骨架，不承载项目事实。
4. 为 program open、phase closure、archive、docs sync 增加 verifier/test。
5. 更新 workflow change log，只记录事实，不制造第二事实源。

## 多 agent 分工

- Thread A：审计 AGENTS 和 workflow references。
- Thread B：审计 templates 是否混入项目事实。
- Thread C：补 verifier/test。
- 主线程：合并规则并运行 workflow verification。

## 需要返回的证据

- 长期规则分类表。
- 写回路径表。
- 模板边界检查结果。
- 新增或更新的 verifier/test 证据。

## 停止条件

- 用户规则无法归类，且会改变后续 program 执行方式。
- 模板和事实源边界冲突，需要用户决定。
- verifier 无法覆盖规则，只能靠人工记忆。
