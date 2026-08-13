# Skill Spec: project-reconstruction

## Purpose

恢复一个真实但记忆模糊、代码不完整、文档不完善的项目，并把稳定事实与可证伪 Target 转成工程计划。

## Inputs

Repository、Git history、简历/Artifact、用户记忆、公开背景、现有架构和目标岗位上下文。

## Workflow

```text
Evidence Intake
→ Fact Recovery
→ Memory Recovery
→ Historical Timeline
→ Current Reality
→ Product Reconstruction
→ architecture-red-blue
→ big-tech-interviewer-red-team
→ Red 100Q
→ Blue Answer / Red Score / Blue Decision
→ Canonical Delta Sync
→ Architecture-to-Code Gap
```

## Document Quality V3.1

进入 Canonical Sync 前先做 Part A/Part B baseline audit。每个 Canonical Owner Doc 必须在同一
文件中同时解释为什么存在以及怎样实现；Round Decision 记录 `document_impact`、两部分的变更
标记和唯一 Owner。文档质量门槛通过后才能标记 `DOC_QUALITY_COMPLETE`，但仍不能把 Target
升级为 Current、Measured 或 Production。

## Outputs

Fact Baseline、Evidence Ledger、Open Questions、History、Current Audit、Challenge Log、Architecture Decisions、Implementation Gaps 和 Mentor Package。

## Guardrails

- 不创造历史事实；
- 不把 Target 当 Current；
- 不扩大个人贡献；
- 不在证据不足时创建 implementation task；
- 需要用户确认的事实必须停在 `USER_CONFIRMATION_REQUIRED`。
- Red/Blue 不能自动修改 Facts；Fact Gap 进入 Fact Recovery Queue。
- Canonical Sync 只能升级 Target Design，不能升级 Current、Measured 或 Production。
- Lab Session 是证据和攻击工作区；Canonical Docs 只保留去过程化的正式事实和 Target，不能把
  Round changelog、问题编号或评分明细写进 Canonical 正文。

## Shared Contracts

复用 `00-charter/state-model.md`、`01-facts/evidence-ledger.md`、`07-interview-red-team/challenge-log.md` 和 `08-decisions/decision-candidates.md`。

## V3.1.3 Extensions

在 Architecture Red/Blue 阶段共享 Closure Class Integrity、Distribution Audit 和 Human Continuity。Fact Recovery 仍然不能被架构题库反向填空；`A/I/E/X` 只描述当前 Claim 的主要阻塞 Gate，不改变历史事实状态。Canonical Sync 前必须完成整篇 Part A 阅读，并把复杂度收益、实现缺口、测量缺口和外部资格缺口分开记录。
