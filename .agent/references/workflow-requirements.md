# Workflow Requirements

## When To Use

当需要查看用户已经明确提出的长期工作流要求，或需要登记新的长期要求时，使用本文件。

## Mental Model

```text
requirement id
  -> status
  -> durable requirement
  -> affected workflow files
```

## Current Truth

### WR-001: AGENTS.md and `.agent/references` form an organic workflow

Status: Current

Requirement: AGENTS.md 是 boot entry 和 route map；`.agent/references` 是 Agent-facing operating memory。二者共同组成 Zuno 的 Agent 工作流文档系统。

Affected files: `AGENTS.md`、`.agent/references/project-map.md`、`.agent/references/workflow-governance.md`。

### WR-002: The workflow must be self-maintaining

Status: Current

Requirement: 当用户提出新的长期工作方式要求时，Agent 不能只在本轮照做，必须判断是否需要更新 AGENTS.md、`.agent/references`、`.agent/templates`、`.agent/programs`、`docs/architecture`、`architecture.html` 和 verifier。

Affected files: `.agent/references/workflow-update-policy.md`、`.agent/references/workflow-maintenance-checklist.md`、`.agent/references/workflow-change-log.md`。

### WR-003: Architecture documentation must stay synchronized

Status: Current

Requirement: 架构相关变更必须检查并同步 `docs/architecture`、`docs/architecture/architecture.html`、`.agent/references`、`.agent/templates` 和 `.agent/programs`。

Affected files: `.agent/references/architecture-docs-map.md`、`.agent/references/documentation-governance.md`、`.agent/references/architecture-update-policy.md`、`.agent/references/diagram-inventory.md`。

### WR-004: Templates must evolve with workflow rules

Status: Current

Requirement: 如果新工作流规则影响未来生成内容，必须同步更新 `.agent/templates`。

Affected files: `.agent/templates/architecture-doc-template.md`、`.agent/templates/mermaid-diagram-template.md`、`.agent/templates/architecture-change-note-template.md`、`.agent/templates/verification-report-template.md`、`.agent/templates/workflow-change-note-template.md`。

### WR-005: Final product definition uses five systems and eight deliverables

Status: Current

Requirement: Zuno 对外表达为五个成熟系统：Agent 工作流文档系统、元工作流自我维护系统、正式架构文档系统、架构 HTML 展示系统、干净清晰且可验证的代码结构。内部验收拆成八大交付物：Agent 工作流文档系统、元工作流自我维护系统、模板与执行计划系统、正式架构文档系统、架构 HTML 展示系统、完善的 Zuno 目标架构、清晰干净的代码和目录、一致性与验证系统。

Affected files: `AGENTS.md`、`.agent/references/project-map.md`、`.agent/references/workflow-governance.md`、`docs/architecture/README.md`。

### WR-006: docs stay small and stable, `.agent` carries volatile operating memory

Status: Current

Requirement: `docs/` must stay small, curated, and relatively stable. It holds human-facing formal conclusions. `.agent/` holds frequently changing Agent operating memory, execution plans, templates, inventories, workflow policies, and change logs. Do not duplicate high-frequency `.agent` details into `docs/`.

Affected files: `AGENTS.md`、`.agent/references/project-map.md`、`.agent/references/architecture-docs-map.md`、`.agent/references/documentation-governance.md`、`docs/architecture/README.md`。

### WR-007: repository root must stay clean

Status: Current

Requirement: 项目根目录只保留稳定项目入口和配置。临时截图、浏览器截图、PDF 预览、测试产物、本地报告、缓存和导出物不得遗留在根目录。正式附件进入对应 `docs/**/assets/`；临时调试产物进入 `.local/` 或 `tmp/`；可复现报告进入受控 `reports/` 路径。

Affected files: `AGENTS.md`、`.agent/references/workflow.md`、`.agent/references/workflow-maintenance-checklist.md`、`.agent/scripts/verify_repo_hygiene.py`、`docs/architecture/deliverables.md`。

## Target Direction

后续新增长期要求用 `WR-008` 继续编号。每条要求必须说明状态和受影响文件。

## Must Preserve

- 不要把一次性任务指令写成 WR。
- 不要把未验证的新机制写成 Current。
- 规则变化后必须记录到 `workflow-change-log.md`。

## Before Editing

1. 确认新要求是否长期。
2. 选择状态：Current、Target、Future 或 History。
3. 更新受影响文件。
4. 记录 change log。

## Allowed Changes

- 新增、修正、退休 workflow requirement。

## Forbidden Changes

- 不要删除历史 requirements；过时要求标记为 History 并说明替代规则。

## Common Failure Patterns

- requirement 写得像愿望，没有可执行影响。
- requirement 没有列出受影响文件。

## Debug Playbooks

- 如果 requirements 和 AGENTS.md 冲突，先按最新用户长期要求修正 reference，再把 AGENTS.md 保持为简短入口。

## Focused Tests

```powershell
python .agent/scripts/verify_agent_system.py
```

## Docs Sync

修改本文件时检查：

- `.agent/references/workflow-change-log.md`
- `.agent/references/workflow-update-policy.md`
- `AGENTS.md`

## Lessons Learned

长期要求应该能让未来 Agent 少读一段对话，直接做对一类任务。
