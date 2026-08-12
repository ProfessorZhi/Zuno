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

## Shared Contracts

复用 `00-charter/state-model.md`、`01-facts/evidence-ledger.md`、`07-interview-red-team/challenge-log.md` 和 `08-decisions/decision-candidates.md`。
