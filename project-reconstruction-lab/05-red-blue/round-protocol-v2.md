# ZUNO-RED-BLUE-WORKFLOW-V2 Round Protocol

## Canonical Question

如何重复执行一轮可评分、可回放、可反驳的 100 Question Architecture Review？

## 状态边界

```text
Facts：USER_CONFIRMED / USER_PARTIAL_RECALL / ARTIFACT_EVIDENCE /
       PARTIAL_REPOSITORY_EVIDENCE / PUBLIC_CONTEXT / RECONSTRUCTED_CANDIDATE /
       CONTRADICTED / UNKNOWN / TARGET_ONLY / FUTURE

Architecture：PROPOSED / UNDER_ATTACK / SURVIVED / REJECTED / DEFERRED /
              ACCEPTED_TARGET / IMPLEMENTED / MEASURED / PRODUCTION_PROVEN

Gap：OPEN / BLUE_PROPOSED / UNDER_COUNTER_ATTACK / RESOLVED / DEFERRED / REJECTED
```

Facts 的结构冻结，事实内容可以通过 Evidence Intake 和 Memory Recovery 增量恢复。Target
Architecture 可以在 Red/Blue 中大幅修改，但不能反写历史事实。

## 角色与循环

```text
Red：提出问题、攻击假设、执行 Kill Test、批评 Blue、评分
Blue：基于当前证据回答、修复候选架构、声明 Unknown 和验证计划
Counter Red：改变问法、Failure、规模、权限或替代方案再次攻击
Evidence Auditor：检查来源、状态、Scope、Cannot Infer
Canonical Owner：判断是否具备写回正式文档的 Owner 和 Contract
User Gate：批准、拒绝或要求继续研究；不由模型代签
```

## Round 完成条件

1. Question ID 恰好 `Q001..Q100`；
2. A–J 配额准确；
3. 每题有 Blue Answer、Red Critique、Revision、Final Assessment 和 Score；
4. Scorecard 覆盖 100 题并给出类别汇总、Raw/Normalized Score；
5. Fact Gap、Architecture Gap、Blocker 有 Question traceability；
6. Blue Change Set 有 User Gate、Sync Status、Validation 和 Rollback；
7. Counter Attack 记录结果；
8. P0 Critical Gate 未关闭时，Round 不能标记通过；
9. 未经 User Architecture Gate 不写正式 `docs/project/`，不生成实现任务。

## Score

每题 `Red Score ∈ [0,5]`，Raw Score 最大 500：

```text
Normalized Score = Raw Score / 5
Category Score = category_raw / (category_count * 5) * 100
```

分数用于发现弱点，不用于制造“越来越高”的叙事。下一轮至少 70% 问题应是新的攻击面，
最多 30% 用于旧 Gap Regression；如果无法计算新颖度，必须显式标记 `NOT_ASSESSED`。

## Round 文件契约

```text
manifest.yaml          Round、基线、配额、状态和来源
transcript.md          Q001..Q100 的完整 QA / Red critique / Revision
scorecard.md           每题分数、类别分数、总分、P0/P1 和 Pass Gate
gaps.md                Fact Gap、Architecture Gap、Blocker Burn-down
blue-change-set.md     Before/Attack/Decision/After/Complexity/Evidence/Rollback
retest.md              Counter Attack、Mutation Variable、结果
round-report.md        本轮摘要、Technology Survival、Next Round Focus
```

在当前仓库中，这组文件放在 `project-reconstruction-lab/sessions/<session-id>/`，由旧有
Session verifier 与 V2 verifier 联合检查。
