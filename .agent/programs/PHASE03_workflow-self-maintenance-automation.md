# PHASE03 Workflow Self Maintenance Automation

status: completed
completed_at: 2026-07-01
next_phase: PHASE04_documentation-dedup-architecture-clarity

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

## 完成证据

PHASE03 已把 workflow self-maintenance 从“对话提醒”推进为可写回、可模板化、可验证的规则系统。新增规则是：工作流规则变化必须留下规则分类证据和写回路径证据；如果规则影响未来输出形状，必须同步模板；如果规则需要防漂移，必须进入 verifier 或 repo test。

### 长期规则分类表

| 规则 | 类型 | 状态 | 为什么 |
| --- | --- | --- | --- |
| 工作流规则变化必须留下规则分类证据 | long-term workflow rule | Current | 它决定未来 Agent 如何判断用户新要求是否应沉淀，不是本轮一次性步骤。 |
| 工作流规则变化必须留下写回路径证据 | long-term workflow rule | Current | 它决定未来 Agent 是否更新 `AGENTS.md`、`.agent/references/`、`.agent/templates/`、`.agent/programs/`、`docs/architecture/`、verifier / tests。 |
| phase 收口模板必须覆盖架构 Markdown / HTML 镜像和 verifier / tests | documentation template rule | Current | 它影响后续 phase closure report 的固定输出形状。 |

### 写回路径表

| Path | PHASE03 处理 |
| --- | --- |
| `AGENTS.md` | 现有入口已包含 Agent Workflow Self-Maintenance 和 Program Closure 自维护审查，本 phase 不扩写入口。 |
| `.agent/references/` | 更新 `workflow-update-policy.md`、`workflow-requirements.md`、`workflow-maintenance-checklist.md`、`workflow-change-log.md`。 |
| `.agent/templates/` | 更新 `workflow-change-note-template.md` 和 `phase-closure-report.md`。 |
| `.agent/programs/` | 本文件记录 PHASE03 closure evidence，并推进 current phase。 |
| `docs/architecture/` | 本 phase 不改变架构正文；仅在 phase 推进时同步 active program 状态并由 renderer 更新 HTML。 |
| verifier / tests | 更新 `.agent/scripts/verify_agent_system.py` 与 `tests/repo/test_agent_system.py`。 |

### 模板边界检查

- `workflow-change-note-template.md` 只新增待填写字段，不保存项目事实。
- `phase-closure-report.md` 删除重复的 `docs/architecture/architecture.md` 项，补齐 `.agent/architecture/architecture.md`、`docs/architecture/architecture.html`、`.agent/architecture/architecture.html`，仍只作为收口报告骨架。

### Verifier / Test 证据

- RED：`pytest -q tests/repo/test_agent_system.py -p no:cacheprovider` 首次失败 3 项，分别证明 verifier 函数、规则分类/写回证据和 phase 收口模板重复项尚未实现。
- GREEN：补实现后同一命令通过，`11 passed`。
- Agent verifier：`python .agent/scripts/verify_agent_system.py` 通过，新增检查函数为 `verify_workflow_update_policy_requires_classification_evidence` 和 `verify_phase_closure_template_self_maintenance_contract`。

### 最终收口验证

| Command | Result |
| --- | --- |
| `git diff --check` | exit 0，仅 Windows LF/CRLF 提示。 |
| `python tools/agent/render_architecture.py --check` | exit 0，architecture Markdown mirror 和 HTML outputs in sync。 |
| `python .agent/scripts/verify_agent_system.py` | exit 0，Agent system verification passed。 |
| `python .agent/scripts/verify_doc_boundaries.py` | exit 0，Doc boundary verification passed。 |
| `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1` | exit 0，Workflow verification passed。 |
| `python tools/scripts/verify_docs_entrypoints.py` | exit 0，documentation entrypoint verification passed。 |
| `python tools/scripts/verify_repo_structure.py` | exit 0，Repository structure verification passed。 |
| `pytest -q tests/repo/test_agent_system.py -p no:cacheprovider` | `11 passed`。 |
| `pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider` | `42 passed`。 |
