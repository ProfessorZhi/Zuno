# Future Skill Design Spec：Project Red-Blue Architect

## 状态

`DRAFT / NOT A SKILL.md`

这是未来自动运行 Red → Blue → Repair → Retest 的接口规格，不是当前可安装、可执行或拥有架构事实的 Skill。它只能组合 [03 Red-Blue Optimization Workflow](../workflows/03-red-blue-optimization-workflow.md)。

## 定位

使用红队攻击、Source-Constrained Blue Answer、Red Judge、Gap Clustering 和 Blue Architect Review，优化项目定位、架构、Build-vs-Buy、实施策略和 Resume Claim。

## 内部模式

```text
Red Interviewer Mode
  → Blue Defender Mode
  → Red Judge Mode
  → Gap Clustering
  → Blue Architect Mode
  → Research / Evidence Task
  → User Gate
  → Canonical Sync
  → Red Retest
```

## 输入

```text
Project Facts
Resume / Project Material
Target Role JD
Current + Target Architecture
Module Documents
Evidence
Open-source Candidate Review
Pinned Git / Source Versions
Question Budget
```

## 输出

```text
Red Transcript
Blue Source-Constrained Answers
Scorecard
Gap Clusters
Blue Change Set
Research / Implementation / Eval Tasks
User Gate Status
Canonical Sync Record
Red Retest Result
```

## 不可绕过的 Gate

- `User Fact Gate`：历史背景、团队、用户规模和个人贡献不能由 Skill 猜成事实；
- `Architecture Gate`：Target 变化必须由用户确认；
- `Current / Target Boundary`：目标设计不能冒充已实现；
- `Canonical Sync`：只有确认后的结果进入正确的 `docs/` Owner；
- `Session Record`：公开问答、评分、Gap、Change Set 和 Retest 必须可审计；
- `Red Retest`：修复后必须用变体问题验证，不得只复读答案。

## 禁止

不得为了提高面试分数虚构项目历史、增加未经证实的复杂度、把 Blue Proposal 写成 Current、绕过 Security/Approval 或直接生成正式 `SKILL.md`。

## 成熟条件

只有在真实 Session 足够多、红队提问稳定、蓝队不偷偷补答案、Gap 能稳定聚类、Change Set 真正改善架构、Retest 能发现回归且用户审查通过后，才允许从本规格生成正式 Skill。
