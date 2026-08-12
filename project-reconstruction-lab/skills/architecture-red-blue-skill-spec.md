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

## Guardrails

- 不因“企业级”保留服务；
- 不将 GraphRAG、Multi-Agent、Memory 或自研 Runtime 视为默认必要；
- WorkBuddy/Dify/Pi/LangGraph/RAGFlow 按层级比较；
- 任何质量、效率、安全和生产声明必须绑定测量证据。
