# Red / Blue Architecture Review History

本目录是 Zuno 的 Architecture Review Process Record。Red / Blue 是对总体架构或稳定责任边界的压力测试，用来记录问题、回答、反驳和 Main Judgment，帮助回看某个架构选择为什么被接受、收窄、否决或留作假设。

它不是：

- Canonical Project Fact；
- Current Implementation Evidence；
- Current Overall Architecture；
- ADR；
- 自动实施授权。

正式关系是：

```text
Architecture Baseline
  → Red Attack
  → Blue Defense
  → Main Judgment
  → Architecture Revision / ADR
```

因此，当前架构始终以 [`docs/architecture/architecture.md`](../../architecture/architecture.md) 为准；项目事实以 [`docs/project/`](../../project/project-background.md) 为准；长期决定以 [`docs/decisions/`](../../decisions/README.md) 为准。Red / Blue 中出现的 `FACT GAP` 不能自动升级为项目事实，必须经过用户确认后单独更新项目文档。

## 当前记录

- [Manual Round 01 — Overall Architecture](manual-round-01-overall-architecture.md)：手动协调三个 ChatGPT 线程完成的第一轮完整对抗记录，保留原始 Questions、Answers、Review、Reflection 和 Main Judgment。
- [Legacy Automated Red / Blue Summary](legacy-automated-rounds.md)：旧自动化架构审查程序的压缩摘要，只保留仍有复盘价值的状态、发现和处置；不构成当前 Protocol。

## 新 Round 归档规则

只有正式 Architecture Review 才进入本目录。每份 Round Archive 至少记录 Round Scope、Architecture Baseline SHA、Red Questions、Blue Answers、Red Review、Main Judgment、Accepted/Rejected Changes、Open Questions 和 Architecture Revision Commit SHA（如已发生）。临时聊天、重复 Prompt、无结论 brainstorming 和 Codex 中间输出不归档。

每一轮保留原始对抗内容，不把 Archive 改写成标准答案；但一旦 Main 接受架构变化，正式结果必须写回 `docs/architecture/` 或 `docs/decisions/`，不能只停留在 Round 文件。
