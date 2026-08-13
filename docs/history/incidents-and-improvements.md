# Incidents and Improvements

status: canonical-history
canonical_question: 项目实际遇到过什么问题，如何定位、修改和验证？
owner: Project Facts / Engineering Incidents
replaces: 无；从 `development-evolution.md` 和 `delivery-and-usage.md` 拆出问题闭环

## 记录原则

研发问题、Demo 失败和质量反馈都可以记录为 Incident；Incident 不等于生产事故。每条记录
必须区分已观察症状、根因假设、调查过程、实际变更和验证结果。

```text
Issue
 → Symptom
 → Root Cause Hypothesis
 → Investigation
 → Change
 → Result
 → Evidence
```

## 当前唯一稳定锚点

| Issue | 状态 | 已知 | 未知 |
|---|---|---|---|
| 客户认为回答质量需要继续提高 | `[USER_CONFIRMED]` / E1 | 反馈确实存在 | 事实错误、漏召回、引用、完整性、延迟、Prompt、Memory、Tool 或其他根因均 UNKNOWN |

这不是“已经修复”的记录，也不是质量指标。没有前后对照、错误样本或提交证据，不得写成
“通过 Retrieval/Prompt/Memory 调整解决”。

## Incident Ledger

| ID | Symptom | Root Cause | Investigation | Change | Result | State |
|---|---|---|---|---|---|---|
| INC-HIST-001 | 回答质量需要提高 | `[UNKNOWN]` | `[UNKNOWN]` | `[UNKNOWN]` | `[UNKNOWN]` | OPEN |

## 候选排查方向

以下只是下一轮调查分类，不是历史结论：

- Retrieval Recall / Rerank；
- Citation 或 Evidence Sufficiency；
- Context Assembly / Memory Scope；
- Tool Selection / Preconditions；
- Prompt / Model / Output Validation；
- 数据版本、权限或业务规则；
- 延迟、超时或其他交互问题。

排查时必须用真实错误样本、Trace、QA 对照、提交或用户回忆关闭根因；不能从架构名词反推。

## Owner 边界

本文件负责历史问题与改进闭环；Current 运行故障进入 [`../evidence/`](../evidence/README.md)，
Target 的 Failure/Recovery 跨层边界进入 [`../architecture/architecture.md`](../architecture/architecture.md)
和对应 ADR。
