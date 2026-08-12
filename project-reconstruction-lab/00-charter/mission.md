# Lab Mission

## Canonical Question

这套 Lab 为什么存在，以及它如何从模糊记忆和不完整代码恢复一个可审计、可攻击、可实施的项目模型？

## Mission

Lab 的任务不是把项目包装得更复杂，而是让以下陈述可以被追问、被证据支持、被反驳并在必要时收缩：

```text
历史上发生了什么？
当前仓库实际上有什么？
哪些只是候选解释？
Target 为什么值得存在？
下一步真实代码要改什么？
```

## Non-goals

- 不补造历史名称、客户、法院、用户量、SLA、指标或个人贡献。
- 不把论文、当前依赖或 Target 文档当成历史实现证据。
- 不把 Interview Answer 当成 Production Evidence。
- 不在 Lab 中复制一套长期 Canonical Architecture。

## Done Criteria

一轮 Lab 只有在以下条件满足时才算收口：

1. 重要 Claim 有状态和 Evidence ID，或明确 `UNKNOWN`。
2. 历史和当前仓库没有混写。
3. Architecture Claim 经过 Red、Blue、Counter Attack，结果明确。
4. 面试风险、事实缺口和架构缺口分别记录。
5. Survived 设计能路由到 Canonical Docs 或 ADR。
6. 需要实现的变化能形成 Gap，而不是直接修改 Runtime。
