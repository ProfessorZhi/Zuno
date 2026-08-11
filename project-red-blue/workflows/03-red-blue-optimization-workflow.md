# 03 Red-Blue Optimization Workflow

## 定位

这是完整的 Red/Blue Campaign，也是唯一允许从红队 Gap 进入架构、项目模型、实施策略或简历修复的工作流。它不保护旧 Target；如果红队证明成熟方案足够、复杂度不合理或项目因果链断裂，蓝队必须允许 KEEP、SIMPLIFY、ADOPT、EXTEND、BUILD、DEFER、REMOVE 或 ARCH_REDESIGN。

优化目标不是“让下一次更容易回答”，而是：

> **让下一次问题更难，但系统仍能给出可信回答。**

## 目标模式

```text
PROJECT_POSITIONING
PROJECT_PACKAGE
ARCHITECTURE
MODULE
IMPLEMENTATION_STRATEGY
BUILD_BUY
MODEL_DEPLOYMENT
DEVELOPMENT_PROCESS
TEAM_OWNERSHIP
RESUME
FULL_PROJECT
```

## 完整循环

```text
Pin Inputs
  ↓
Red Question
  ↓
Blue Source-Constrained Answer
  ↓
Red Score / Judge
  ↓
Next Dynamic Question
  ↓
Question Budget / Stop Boundary
  ↓
Gap Clustering
  ↓
Campaign Escalation Plan
  ↓
Blue Project Package / Architecture Review
  ↓
Research if needed
  ↓
KEEP / SIMPLIFY / ADOPT / EXTEND / BUILD / DEFER / REMOVE
  ↓
Blue Change Set
  ↓
User Architecture Gate
  ↓
Canonical Sync
  ↓
Red Retest
```

允许形成的 Change Set 不只包括 Architecture Proposal，还可以是：

```text
Project Positioning Proposal
Team / Ownership Reconstruction Candidate
Delivery Evolution Reconstruction
Build-vs-Buy Decision
Model Deployment Strategy
Architecture Change Set
Resume Scope Change
Implementation / Eval Task
```

历史事实仍必须经过 User Fact Gate；重建候选不得被写成真实开发过程、客户关系、部署记录或个人贡献。

## 评分：回答防守能力与架构适配度分开

每个重要问题至少记录两个分数，不能用回答完整掩盖架构不合理：

### Answer Defensibility

```text
0  当前材料无法回答或存在冲突
1  只有术语，没有因果和边界
2  有设计结论，但缺因果或边界
3  有机制和取舍
4  机制、Failure、Alternative、Boundary 较完整
5  设计、Current Evidence、Trade-off 和反事实都能防守
```

### Architecture / Project Fitness

```text
0  明显错误或项目故事矛盾
1  严重过度设计或没有用户原因
2  能工作，但选型依据弱
3  基本合理
4  边界、替代方案和失败语义清楚
5  简洁、可替换、可恢复、可验证，并能经受复杂度压缩
```

`Answer Defensibility = 5` 不代表 `Architecture / Project Fitness = 5`。文档可以完整解释一个错误架构。

## Action Classification

逐题 Gap 必须先分类，再决定是否修改。支持：

```text
NO_CHANGE
DOC_CLARIFY
PROJECT_FACT_RESEARCH
PROJECT_POSITIONING_REVIEW
SCOPE_DOWN
ARCH_REDESIGN
ADOPT_EXTEND_REVIEW
IMPLEMENTATION_TASK
EVAL_TASK
SECURITY_REVIEW
RESUME_SCOPE_DOWN
```

不要因为有 100 道问题就做 100 次架构修改。

## Gap Clustering

相同根因的问题必须聚类。例如多个问题都攻击 Graph：为什么需要 Graph、Graph 如何成为 Evidence、错 Relation 怎么办、为什么不用 GraphRAG、有没有 Benchmark，应聚类成一个 `03 Knowledge / Graph Retrieval` Cluster，统一记录：

```text
Pain Mapping
Build-vs-Buy
Evidence Materialization
Failure
Measurement
```

Blue Architect 先针对 Cluster 产生统一 Change Proposal，再决定影响哪些模块、Contract、实施任务和证据任务。

## Blue Change Set 与 User Gate

Change Set 至少包含：

```text
Change ID
Target
Problem
Current Design
Proposed Design
Decision
Why
Alternatives
Affected Modules
Contract Changes
Migration / Implementation Implication
Evidence Needed
User Gate
Canonical Destination
```

只有用户通过 Architecture Gate 后，才允许同步到 `docs/project/architecture/`、`docs/project/modules/`、ADR、Status 或 Evidence 的正式 Owner。没有用户确认的内容保持 `[BLUE_PROPOSAL]`，不进入 Current。

## Red Retest

复测必须改变至少一个变量：问法、反例、Failure、规模、版本、权限或替代方案。不能只让候选人重复上一轮答案。

```text
上一轮 Gap
  → 修复或范围收缩
  → Mutation Question
  → Blue / User Answer
  → Red Score
  → PASS / REOPEN
```

如果旧 Gap 在新问法下重新出现，状态为 `REOPEN`，不能因为文档已经更新就宣称关闭。

## Campaign 级升级

下一轮不能把上一轮问题原样重放。默认从三类问题源动态分配预算，比例是治理建议，不是静态题库：

```text
REGRESSION             30%–50%
ADVERSARIAL_MUTATION   30%–50%
NEW_SURFACE            10%–30%
```

`REGRESSION` 检查上一轮 CLOSED Gap 是否重新出现；`ADVERSARIAL_MUTATION` 保持 Claim 不变但改变问法、Failure、规模、版本、权限、开源替代、团队约束、预算、时间或部署模式；`NEW_SURFACE` 攻击修复后新产生的 Architecture Claim。下一轮通过 `parent_session_id`、`baseline_session_id`、`campaign_phase` 和 `defense_base_sha` 连接上一轮，不能把三个 Markdown Session 当成互相独立的成绩单。

Campaign Score 使用按 Attack Area 聚合的 **Campaign Quality Profile**，至少观察回答防守度、项目/架构适配度、P0/P1、Unsupported Rate、Coverage Status 和 Reopened Gap；平均分只作辅助，不产生一个掩盖危险缺口的总分。

## Canonical Sync 追踪

`blue-change-set.md` 的每个 Change 必须记录来源 Cluster、User Gate、Sync Status、Canonical Paths、Applied Commit SHA、Validation Run、Validation Not Run 和 Retest IDs。`NOT_APPLIED`、`PARTIAL` 或 `REJECTED` 的 Change 仍是提案或未完成修复；只有 `APPLIED` 且通过 User Gate 的 Change 才能被 Retest 当作正式修复。

## 边界

Workflow 03 允许研究和提出架构修改，但仍禁止：

- 在红队 Session 内直接改正式架构；
- 把研究候选写成历史事实；
- 为通过面试虚构用户、团队、指标或实现；
- 生成新的大规模静态 QA 题库；
- 在未完成真实 Session 和用户审查前生成正式 `SKILL.md`。
