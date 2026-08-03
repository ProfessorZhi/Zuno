# Workflow Change Log

## When To Use

当 AGENTS.md、`.agent/references`、`.agent/templates`、`.agent/programs`、`docs/architecture` 或 architecture HTML 的工作流规则发生变化时，在这里记录原因和影响范围。

## Mental Model

```text
date
  -> summary
  -> reason
  -> affected files
  -> status layer
  -> validation
```

## Current Truth

### 2026-08-03: Zuno worker worktrees anchored under internship resume project

Summary: 明确 `F:\internship-work\resume project\Zuno` 是最终集成入口，临时 worker worktree 统一放在 `F:\internship-work\resume project\worktrees\`，每个 agent 使用独立 branch/worktree，完工提交后由主线程审查 diff、吸收、验证、push，并在完成后清理临时 worktree。

Reason: 用户明确要求多 agent 分工时最终只保留 Zuno 主项目文件夹，临时工作区集中放置并可清理。这是长期执行规则，不是本轮一次性路径选择。

Affected files:

- `.agent/references/workflow.md`
- `.agent/references/command-catalog.md`
- `.agent/references/workflow-change-log.md`
- `.agent/scripts/verify-workflow.ps1`

Status: Current workflow truth for Zuno multi-agent worktree placement in the internship workspace.

Validation: 由 `git diff --check`、`python .agent/scripts/verify_agent_system.py`、`powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1` 和 focused workflow review 保护。

### 2026-08-02: command-line and worktree safety rules added to local workflow memory

Summary: 把本轮暴露出的工作树错位、嵌套 PowerShell 参数透传、PATH 污染和结构化输入被二次解析等问题，沉淀进 `.agent/references` 的长期工作流、已知坑和命令目录。

Reason: 这些问题不是一次性提示噪音，而是会反复影响后续 worker dispatch、fake runner 测试和本地脚本执行的长期执行风险。只有进入 reference 体系，后续 Agent 才会在读工作流时主动做 worktree 先验校验、命令行安全处理和 PATH 隔离。

Affected files:

- `.agent/references/workflow.md`
- `.agent/references/known-pitfalls.md`
- `.agent/references/command-catalog.md`
- `.agent/scripts/verify-workflow.ps1`

Status: Current workflow truth for command-line safety and worktree hygiene.

Validation: 由 `git diff --check`、后续 workflow/agent system 基线验证和本次 dispatcher 测试覆盖共同保护。

### 2026-07-01: workflow rule evidence made machine-checkable

Summary: 工作流规则变化必须留下规则分类证据和写回路径证据，并由 phase 收口模板、workflow change note、Agent verifier 和 repo test 共同检查。

Reason: PHASE03 的目标是让工作流自我维护不依赖对话记忆。只写“以后注意”或只改一份 reference，无法证明未来 Agent 知道规则类型、写回路径和验证边界。

Affected files:

- `.agent/references/workflow-update-policy.md`
- `.agent/references/workflow-requirements.md`
- `.agent/references/workflow-maintenance-checklist.md`
- `.agent/references/workflow-change-log.md`
- `.agent/templates/workflow-change-note-template.md`
- `.agent/templates/phase-closure-report.md`
- `.agent/scripts/verify_agent_system.py`
- `tests/repo/test_agent_system.py`

Status: Current workflow truth for PHASE03 and later workflow-rule changes.

Validation: 本条随 PHASE03 由 `git diff --check`、`python tools/agent/render_architecture.py --check`、`python .agent/scripts/verify_agent_system.py`、`python .agent/scripts/verify_doc_boundaries.py`、`powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`、`python tools/scripts/verify_docs_entrypoints.py`、`python tools/scripts/verify_repo_structure.py` 和 focused repo tests 验证通过。

### 2026-06-30: runtime-full program archived and no-active restored

Summary: 完成 `zuno-target-architecture-runtime-full-implementation-v1` 的 PHASE01-PHASE12，归档 program，并把 `.agent/programs/` 切回 no-active 等待态。

Reason: 本轮已经以完整 vertical slice 证明第一版 runtime 闭环，不应继续把历史 phase 文件留在前台作为 active 执行入口；下一轮 program 必须由用户明确打开并从 PHASE01 重新冻结事实源。

Affected files:

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/references/current-program.md`
- `.agent/references/verification-map.md`
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`
- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- verifier and repo tests

Status: Current workflow truth after PHASE12 release closure.

Validation: 本条随 PHASE12 由 full pytest、architecture renderer check、docs / repo / agent / workflow verifier、contract eval 和 `git diff --check` 验证。

### 2026-06-30: runtime-first active program acceptance

Summary: 打开 `zuno-target-architecture-runtime-full-implementation-v1`，把下一轮验收口径从 contract foundation 改为 runtime-first / vertical-slice-first。

Reason: 用户明确指出上一轮“完整执行 program”仍以最小可测 contract 关闭，未等同于完整目标架构 runtime。新 program 必须以“上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback”的真实闭环作为主线，不能只靠 schema、README 或 contract 关闭 runtime phase。

Affected files:

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_program-reopen-and-truth-source-freeze.md`
- `.agent/references/current-program.md`
- `AGENTS.md`
- `README.md`
- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- verifier and repo tests

Status: Active workflow truth for `zuno-target-architecture-runtime-full-implementation-v1`.

Validation: 本条随 PHASE01 由 `git diff --check`、`python .agent/scripts/verify_agent_system.py`、`python tools/scripts/verify_repo_structure.py`、`powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1` 和相关 repo tests 验证。

### 2026-06-30: Architecture Documentation Governance and Agent Workflow Self-Maintenance

Summary: 建立架构文档治理工作流和元工作流自我维护机制，并明确最终成品的五个成熟系统与八大交付物。

Reason: 用户要求 Zuno 不只是补文档，而是让 AGENTS.md、`.agent/references`、`.agent/templates`、`.agent/programs`、`docs/architecture`、`architecture.html` 组成可读取、可执行、可验证、可自我维护的项目操作系统。

Affected files:

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/project-map.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `.agent/references/architecture-update-policy.md`
- `.agent/references/diagram-inventory.md`
- `.agent/references/current-target-future-rules.md`
- `.agent/references/workflow-governance.md`
- `.agent/references/workflow-update-policy.md`
- `.agent/references/workflow-requirements.md`
- `.agent/references/workflow-maintenance-checklist.md`
- `.agent/templates/architecture-doc-template.md`
- `.agent/templates/mermaid-diagram-template.md`
- `.agent/templates/architecture-change-note-template.md`
- `.agent/templates/verification-report-template.md`
- `.agent/templates/workflow-change-note-template.md`
- `docs/architecture/README.md`
- `tools/agent/render_architecture.py`

Status: Current workflow truth after verifier and repo tests pass.

Validation: 本条在执行后由 `git diff --check`、`python tools/scripts/verify_docs_entrypoints.py`、`python tools/scripts/verify_repo_structure.py`、`python .agent/scripts/verify_agent_system.py`、`python tools/agent/render_architecture.py --check` 和相关 repo tests 验证。

### 2026-06-30: docs and `.agent` boundary tightened

Summary: 明确 `docs/` 少而精、稳定正式；`.agent/` 承载高频变化的 Agent operating memory、计划、模板、清单和 workflow change log。

Reason: 用户指出 `.agent` 文件夹和 `docs` 文件夹存在重合；`.agent` 是给 Agent 看的，经常变化；`docs` 应该少而精、相对固定。

Affected files:

- `AGENTS.md`
- `.agent/references/project-map.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `.agent/references/workflow-requirements.md`
- `docs/architecture/README.md`
- `tools/agent/render_architecture.py`

Status: Current workflow truth after verifier and repo tests pass.

Validation: 本条在执行后由 `git diff --check`、`python tools/agent/render_architecture.py --check`、docs verifier、repo structure verifier、Agent verifier 和相关 repo tests 验证。

### 2026-06-30: root cleanliness and ten architecture view categories

Summary: 明确项目根目录必须保持干净，并把 architecture HTML / diagrams 从“十张图”修正为“十类架构视图”。

Reason: 用户指出根目录出现临时图片，要求工作流沉淀根目录清洁规则；同时指出架构图不应是凑数量的十张图，而应是覆盖系统不同方面的十类视图，例如整体、记忆系统、工具层、Agent Loop 等。

Affected files:

- `AGENTS.md`
- `.agent/references/workflow.md`
- `.agent/references/workflow-requirements.md`
- `.agent/references/workflow-maintenance-checklist.md`
- `.agent/references/diagram-inventory.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/scripts/verify_repo_hygiene.py`
- `docs/architecture/architecture.md`
- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `tools/agent/render_architecture.py`

Status: Current workflow truth after verifier and repo tests pass.

Validation: 本条在执行后由 `git diff --check`、`python tools/agent/render_architecture.py --check`、docs verifier、repo structure verifier、Agent verifier、repo hygiene verifier 和相关 repo tests 验证。

## Target Direction

后续每次工作流规则变化都追加一条，不覆盖历史条目。完成的 program 归档到 `docs/history/programs/`，但本 change log 记录规则演进事实。

## Must Preserve

- 只记录会影响未来 Agent 行为的变化。
- 记录必须包含 reason、affected files、status 和 validation。

## Before Editing

1. 确认变化来自长期规则、治理变更或模板/计划生命周期变化。
2. 先更新实际规则文件，再更新本 log。
3. 执行验证后补充 validation。

## Allowed Changes

- 追加新 change log。
- 修正当前条目的验证结果。

## Forbidden Changes

- 不要把一次性任务日志写进本文件。
- 不要删除旧条目；如需退休，追加替代说明。

## Common Failure Patterns

- 只写 summary，不写 reason。
- 只记录文件，不记录验证。

## Debug Playbooks

- 找不到某条规则来源：先查 `workflow-requirements.md`，再查本文件。

## Focused Tests

```powershell
python .agent/scripts/verify_agent_system.py
```

## Docs Sync

修改本文件时检查：

- `.agent/references/workflow-requirements.md`
- `.agent/references/workflow-update-policy.md`

## Lessons Learned

change log 不是流水账，是为了让未来 Agent 知道规则为什么变了。
