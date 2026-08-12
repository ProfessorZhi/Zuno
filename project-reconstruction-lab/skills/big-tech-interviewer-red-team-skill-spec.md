# Skill Spec: big-tech-interviewer-red-team

## Purpose

模拟 Staff/Principal Backend、AI Infra、Agent Architect 和 Hiring Manager，攻击项目真实性、个人贡献、代码路径、架构取舍、故障恢复、性能、安全和替代方案。

## Inputs

Fact Baseline、Evidence Ledger、Current Repository Reality、Target Architecture、用户已有回答和岗位要求。

## Workflow

```text
Reality
→ Code
→ Architecture
→ Failure/Performance
→ Counterfactual
→ Challenge Log
→ Fact Gap / Architecture Gap
```

面试攻击结果必须可以回链到 Round Question、Blue Answer、Red Score、Blue Decision 和 Delta；
面试官不能用“你应该知道”补造历史事实。

针对 V3.1，面试问题必须同时检查两层深度：Part A 是否能讲清 Why/What、真实场景、职责与
非职责、Happy Path、失败和反转条件；Part B 是否能讲清 Contract、状态/版本、错误传播、
幂等、重试恢复、安全、审计、可观测性和验证。答不上时分别记录 Narrative Gap、Contract
Gap 或 Fact Gap，不用架构术语掩盖历史未知。

## Outputs

按 P0–P3 分级的 Challenge Log、当前回答、证据、薄弱点、行动和 Interview Readiness Report。

## Guardrails

- 历史不能确认时明确说 UNKNOWN；
- Target 回答必须显式标为 Target；
- 不为了面试补造 RabbitMQ、数据库、QPS、SLA、准确率或生产经历；
- Interview Ready 与 Production Ready 分开。
