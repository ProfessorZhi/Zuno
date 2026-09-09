# Findings — rb-2026-09-09-memory-task-003

Round result: `CLOSED_WITH_INTERVIEWABLE_TASK_AND_EVIDENCE_LIMIT`  
Resume claim verdict: `PASS`  
Highest severity: `S2`

本轮复测 `rb-2026-09-09-resume-claims-002` 剩余的任务级 Evidence Gap。v3 Resume 的 Context / Memory 主 bullet 已能由 PR #8、历史 commit 和 tests 支撑；只保留一个仍会改变面试回答边界的 Finding。

## F1 — PR #8 已形成可追问工程任务，但原始触发与真实运行结果仍未恢复

Severity: `S2`  
Type: `EVIDENCE_GAP`

### What is now proven

可以稳定证明并展开：

- 2026-06-29 PR #8 / commit `f3c74338c042074ae6d912e80de5f2b31511b290` 是一个有边界的 Context Builder / Memory foundation slice；
- 父提交中 `GeneralAgent.prepare_context()` 尚未读取 Memory；该 PR 接入 same-scope task summary 与仅 `APPROVED` 的 structured memory；
- Context Pack 增加 policy / source-id trace，Memory 增加 review / provenance contract；
- focused suite 记录 `32 passed`，另有 repo tests `66 passed`、legacy tests `11 passed` 与三 profile contract eval `status: ok`；
- simple baseline 仍可使用 recent window + task summary；外部 Memory Provider 可以继续承担存储 / 检索；
- PR 的个人 Claim 可以说“完成并集成这条 bounded slice”，同时明确使用 Codex / multi-agent 辅助，不能扩大成整套 Memory 独立实现。

这些证据已经解决上一轮“只能说参与 Memory，无法讲具体任务”的主要 S2 风险。

### What is still unknown

当前没有恢复：

- 谁最初提出 PHASE05 对应的真实产品 / 业务需求；
- 对应 Issue、客户原话或需求单；
- 跨 scope、未审批 Memory、provenance 丢失等 failure mode 是否真实发生过线上事故；
- 该 slice 在真实任务上的质量、效率、成本或用户结果。

因此不能把这条故事包装成“客户发现线上 Memory 污染 → 我定位并修复 → 指标提升”。当前只能准确说成 planned foundation engineering task + tested failure modes。

### Decision impact

**不再削弱 v3 Resume。** 当前 bullet 的 Claim 强度与证据匹配，可以作为 Zuno 的首要个人技术故事候选。

面试回答必须保留三条边界：

1. 任务来源说成仓库计划中的 PHASE05，除非以后恢复真实需求来源；
2. scope / approval / provenance 说成设计并测试的 failure mode，不冒充真实事故；
3. `32 passed` 说成 focused test suite 结果，不解释成 Memory 质量收益。

### Evidence still worth recovering

按信息增益排序：

```text
原始 Issue / 需求 / 任务说明
→ PR 前后的真实运行记录或 Bad Case
→ Review / 设计讨论
→ 与 PHASE05 相关的真实 Bug / Trace
→ 如果存在，真实任务质量或效率结果
```

如果这些材料长期找不到，不需要继续修改 Resume；保持当前边界即可。

### Retest scenario

若未来补到新证据，Red 只需追两问：

> 这条任务最初为什么启动？
> 上线 / 试运行后发生了什么可验证变化？

回答必须来自 History / Evidence，不能用今天的 Target Architecture 补齐。

## Resolved from the previous round

- `OWNERSHIP_GAP`：从方向级“参与 Memory”升级到 PR #8 的 bounded task ownership，同时明确 Codex / multi-agent 辅助边界。
- task-level `EVIDENCE_GAP`：已经能回答具体文件、状态 / contract、failure mode、tests 和 simpler alternative。
- Resume truthfulness：v3 不依赖 OpenViking artifact 作为主 bullet，也没有把 PR #8 说成第一批 Memory、生产级 Memory 或质量 benchmark。
