# Zuno 架构与项目演进历史

`docs/history/` 记录已经发生的设计讨论、架构审查和仍有复盘价值的历史材料。它回答的是：

> 为什么今天的设计会变成这样？

它不回答今天系统应该如何实现。当前项目故事看 [Project](../project/README.md)，当前 Target 看[总体架构](../architecture/architecture.md)，当前代码和运行证据看 [Evidence](../evidence/README.md)，长期决定看[有效 ADR](../decisions/README.md)。

## 怎么读 History

如果只是想快速理解架构为什么变化，先读 [Red / Blue 架构审查入口](./red-blue/README.md)。它提供每一轮的背景、主要发现和当前状态。

如果需要审计当时到底问了什么、怎样回答、哪些问题被追问，再打开对应的完整 Round Archive。完整记录保留原始问答，不应被当作标准答案或当前架构。

## 当前保留的主要历史

- [Red / Blue Architecture Reviews](./red-blue/README.md)：总体架构和候选责任边界的对抗式审查。
- [Legacy Automated Red / Blue Summary](./red-blue/legacy-automated-rounds.md)：旧自动化审查程序的压缩摘要，只保留仍有复盘价值的内容。

普通文件演进和已删除工作区材料由 Git history 承担；本目录不维护第二套项目事实、架构正文或证据台账。
