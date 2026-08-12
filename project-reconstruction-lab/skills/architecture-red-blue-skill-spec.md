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

## V3 Scored Round Contract

`ZUNO-RED-BLUE-WORKFLOW-V3` 是可重复执行的 Round 协议，不是脱离项目上下文的静态题库。每个
Round 固定记录 100 个独立问题，按 11+1 Lens 配额分布；每题记录完整 Question、Blue Answer、
Red Score 和 Blue Decision。Round 还必须生成 Delta、Canonical Sync Record、完整性验证和
ChatGPT Review Package。

Round 完整记录位于 `project-reconstruction-lab/sessions/<session-id>/`，至少包含
`manifest.yaml`、`transcript.md`、`scorecard.md`、`gaps.md`、`blue-change-set.md`、`retest.md`
和 `round-report.md`。分数不能单独通过 Round：Canonical State、不可逆副作用、权限/审批、
重复执行、数据损坏、版本冲突、跨服务一致性和证据完整性等 Critical Gate 仍为 OPEN 时，
状态必须保持 `NOT_PASSED_PENDING_USER_GATE`。

Blue Decision 完成后，允许的 Contract/State/Failure/Owner/Provider/Eval/Reversal refinement
必须在同一 Round 通过 Delta trace 自动同步 Canonical Docs；改变基本原则、Active ADR、重大
安全边界或 Python-only/Microservice/Single Controller 的变化只能进入 ADR/User Gate Escalation。
Round 记录仍是 immutable history，后续错误使用 Errata，不无痕改写。

## Guardrails

- 不因“企业级”保留服务；
- 不将 GraphRAG、Multi-Agent、Memory 或自研 Runtime 视为默认必要；
- WorkBuddy/Dify/Pi/LangGraph/RAGFlow 按层级比较；
- 任何质量、效率、安全和生产声明必须绑定测量证据。
