# Architecture Review History

`docs/history/` 不保存 Current Project Facts、Current Implementation Evidence、Canonical Architecture 或长期 ADR。当前事实、架构和证据分别由：

- [项目文档](../project/project-background.md)；
- [总体架构](../architecture/architecture.md)；
- [Current Evidence](../evidence/README.md)；
- [有效 ADR](../decisions/README.md)

本目录只保留具有长期复盘价值的 Architecture Review Records。普通文件演进、临时讨论和已删除工作区由 Git history 承担，不再在当前树维护第二套历史垃圾场。

## Red / Blue 架构审查记录

进入 [Red / Blue Archive](./red-blue/README.md) 可以查看第一轮完整的 Red Questions、Blue Answers、Red Review、Blue Reflection 和 Main Judgment。

记录关系是：

```text
Architecture Baseline
  → Red Attack
  → Blue Defense
  → Main Judgment
  → Accepted Architecture / ADR Revision
```

Archive 解释“为什么后来这样设计”，不决定“当前系统是什么”。如果历史记录与 `docs/architecture/architecture.md` 冲突，以当前架构正文为准。
