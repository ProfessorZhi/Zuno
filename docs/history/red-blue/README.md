# Red / Blue 架构审查历史

## 这是什么

Red / Blue 是 Zuno 用来压力测试架构的人工审查过程。Red Team 专门从真实任务、故障、边界冲突和替代方案出发提问；Blue Team 根据当时的架构和事实进行答辩；Main Coordinator 再判断哪些问题需要修改架构、哪些只是事实缺口或待测假设。

原始 Q/A/R 会永久保留在各轮 Archive 中，方便审计当时发生了什么。这个 README 提供人类阅读摘要，但不拥有当前事实、Target Architecture、ADR 或实施授权。

正式架构始终以[总体架构](../../architecture/architecture.md)为准，项目背景以 [Project](../../project/README.md) 为准，当前实现以 [Evidence](../../evidence/README.md) 为准，长期决定以 [有效 ADR](../../decisions/README.md) 为准。

## 阅读顺序

建议按下面顺序阅读：

```text
Round 01 — Overall Architecture Narrative
  → Round 02 — Overall Architecture Freeze Review
  → 后续 Round
```

先看本页的摘要；只有需要完整审计时，再打开具体 Round 的原始记录。

## Round 01 — Overall Architecture Narrative

第一轮主要检查 Zuno 是否真的需要成为一个复杂 Agent 平台，以及哪些能力应该自己拥有、哪些能力可以交给 Generic Host、LangGraph、Memory Provider、Graph Provider 或其他外部能力。它还让一条复杂法律任务从材料进入一直走到检索、工具调用、人工复核、正式结果和故障恢复。

这一轮的总体架构主线经受住了审查，但没有把所有高级能力提升为核心。Generic Host + Legal Backend 被保留为更可信的最小形态；Native Runtime、GraphRAG、长期 Memory 和 Persistent Multi-Agent 都继续接受可删除性检验。审查还要求补清 Knowledge Readiness、降级结果是否仍有正式资格、长任务持续授权和 Tool Capability Drift，并重新收敛 Microservice 的证据门槛。

Round 01 的目标架构修订已经记录在提交 `391e9f16e4d0cf12998e9b310470c454d2c92b50` 中，但模块分解闸门当时仍未打开。完整记录见 [Round 01 Archive](./manual-round-01-overall-architecture.md)。

## Round 02 — Overall Architecture Freeze Review

第二轮从“总体架构是否讲得通”进一步进入“候选责任边界是否精确到可以冻结”。Q1–Q38 的 Q/A/R 已全部完成，并追加了 Red Final Findings；讨论了简单回答的调用权、正式引用和 WorkProduct 的权威、Memory 删除、Domain Commit 与 Checkpoint 恢复、发布结果失效、关键审计重建，以及 Capability / Tool、Memory、Product Surface 和 Infrastructure 是否真的应当成为独立模块。

这一轮已经明确暴露出若干 Freeze Blocker。Red Final Findings 已将本轮标记为 `READY_FOR_MAIN_JUDGMENT`，随后 Main Judgment 将结果记录为 `ACCEPTED_WITH_REQUIRED_ARCHITECTURE_REVISION`。这不表示架构已经完成修订或整体冻结；Canonical Architecture Revision 尚未开始，未解决项涉及 Simple Answer / Invocation Ownership、Historical Citation Authority、Memory Delete Across Copies、Domain Commit / Checkpoint Recovery、Published Result Invalidation 和 Reconstruction Boundary。

因此 Round 02 的 Q/A/R 归档和 Main Judgment 记录已经完成，Outcome 为 `ACCEPTED_WITH_REQUIRED_ARCHITECTURE_REVISION`；Canonical Architecture Revision 尚未开始，Overall Architecture Freeze 仍为 not yet，Module Decomposition Gate 仍未打开。不要把这轮的 Red Concern 或 Blue Proposal 当作已经落实的架构正文。

完整记录见 [Round 02 Archive](./manual-round-02-overall-architecture-freeze-review.md)。

## Full Records

- [Round 01 — Overall Architecture Narrative](./manual-round-01-overall-architecture.md)
- [Round 02 — Overall Architecture Freeze Review](./manual-round-02-overall-architecture-freeze-review.md)
- [Legacy Automated Rounds](./legacy-automated-rounds.md)

原始 Round Archive 是审计记录，不是标准答案。只有在 Main Judgment 被明确接受、并完成独立的 Architecture 或 ADR 修改后，结果才会进入对应的正式文档。
