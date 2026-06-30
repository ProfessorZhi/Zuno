# 模板

`.agent/templates/` 只保存 skill 执行模板和报告骨架。模板回答“输出成什么样”，不保存项目知识、历史事实、目标架构正文或失败模式。

## Mental Model

```text
references = why / when / what to preserve / how to debug
templates  = reusable output shape
programs   = current phase execution plan
docs       = formal human truth
```

## Current Templates

- `requirement-intake.md`：需求澄清骨架。
- `readonly-audit-prompt.md`：只读审计提示骨架。
- `phase-plan.md`：phase 计划骨架。
- `phase-closure-report.md`：phase 收口报告骨架。
- `goal-mode-prompt.md`：目标模式提示骨架。
- `target-mode-prompt.md`：目标模式批处理骨架。
- `codex-batch-prompt.md`：Codex 批处理骨架。
- `spec-coding-checklist.md`：规格实现检查骨架。
- `architecture-doc-template.md`：正式架构文档骨架。
- `mermaid-diagram-template.md`：Mermaid 图文档骨架。
- `architecture-change-note-template.md`：架构变更记录骨架。
- `verification-report-template.md`：验证报告骨架。
- `workflow-change-note-template.md`：工作流自我维护变更记录骨架。

## Allowed Content

- 标题层级。
- 需要填写的字段。
- 验收报告格式。
- 只引用 skill 或 docs 的路径，不复制其正文。

## Forbidden Content

- 不保存项目事实、当前架构结论或目标架构正文。
- 不保存 lessons learned、known pitfalls、debug playbooks。
- 不保存一次性调查流水账。
- 不替代 `.agent/references/` 或 `.agent/programs/`。

## Before Editing

新增模板前先确认：

1. 是否已有模板可复用。
2. 是否只是项目知识；如果是，放 `.agent/references/`。
3. 是否是当前 phase 计划；如果是，放 `.agent/programs/`。
4. 是否能被 `.agent/system.yaml` 或 phase 文件引用。

新增模板必须能被 `.agent/system.yaml` 或 phase 文件引用；不能被路由或执行计划引用的模板先不要放进前台。

如果用户提出新的长期工作流规则，并且该规则会影响未来生成内容，必须同步检查并更新相关模板。模板更新后还要检查 `.agent/references/workflow-update-policy.md`、`.agent/references/workflow-requirements.md` 和 `.agent/references/workflow-change-log.md`。

## Docs Sync

修改模板边界时检查：

- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/README.md`
- `.agent/references/workflow.md`
- `.agent/references/docs-map.md`
- `tests/repo/test_agent_system.py`

## Lessons Learned

模板越“聪明”，越容易变成第二套项目真相。Zuno 模板应保持瘦，只提供骨架，把判断交给 references skills。
