# Skill Spec: architecture-red-blue

## Purpose

攻击架构中没有证据的复杂度，经过 Blue Response 和 Counter Attack 后形成 KEEP、SIMPLIFY、EXTERNALIZE、DEFER 或 DELETE 决策。

## Inputs

Repository Reality、Fact Baseline、Target constraints、Canonical Docs、ADR、替代方案、Benchmark/Spike 结果。

## Workflow

```text
Claim Registry
→ Red Attack
→ Blue Contract
→ Counter Attack
→ Kill Test / Benchmark
→ Decision Candidate
→ ADR / Canonical Sync
```

## Outputs

Attack Registry、Blue Response、Counter Attack、Kill Tests、Decision Candidate、ADR Backlog 和 Architecture Review Report。

## V2 Scored Round Contract

`ZUNO-RED-BLUE-WORKFLOW-V2` 是可重复执行的 Round 协议，不是脱离项目上下文的静态题库。每个
Round 固定记录 100 个独立问题，并按 A–J 配额分布：10/10/15/15/10/10/10/8/7/5。每题同时
记录 Answer Defensibility 与 Architecture / Project Fitness（0–5），保留 Raw Score、Normalized
Score、P0/P1、Gap、Blue Revision、Counter Retest 和 User Gate。

Round 完整记录位于 `project-reconstruction-lab/sessions/<session-id>/`，至少包含
`manifest.yaml`、`transcript.md`、`scorecard.md`、`gaps.md`、`blue-change-set.md`、`retest.md`
和 `round-report.md`。分数不能单独通过 Round：Canonical State、不可逆副作用、权限/审批、
重复执行、数据损坏、版本冲突、跨服务一致性和证据完整性等 Critical Gate 仍为 OPEN 时，
状态必须保持 `NOT_PASSED_PENDING_USER_GATE`。

Round 可以修订 Candidate Architecture，但不得直接写正式 `docs/`。只有经过 Counter Attack、
证据追踪和用户 Architecture Gate 的 Change 才能进入 Canonical Sync。这里的“禁止静态题库”
是指禁止脱离 Round 生成无审计的通用问题池；并不禁止在每个可追溯 Round 中固定生成并验证 100
个独立问题。

## Guardrails

- 不因“企业级”保留服务；
- 不将 GraphRAG、Multi-Agent、Memory 或自研 Runtime 视为默认必要；
- WorkBuddy/Dify/Pi/LangGraph/RAGFlow 按层级比较；
- 任何质量、效率、安全和生产声明必须绑定测量证据。
