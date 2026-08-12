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

## V3.1 Document Quality Contract

V3.1 在每个 Canonical Owner Doc 内固定同文件双层结构：Part A — Architecture Narrative
回答问题、场景、职责边界、Happy Path、主要失败、取舍、替代方案、反转条件和
Current/Target/Gap；Part B — Detailed Architecture Specification 定义输入输出、状态/版本、
错误传播、重试恢复、幂等、安全、审计、可观测性、所有权、扩缩容、兼容性和验证证据。
不创建 `-human.md`、`-spec.md` 或第二套 Canonical 文档；Part A 与 Part B 不复制同一状态机。

每道 Round-003 问题必须记录 `document_impact: PART_A | PART_B | BOTH | NONE`，同时记录
Part A/Part B Change Required 和 Canonical Owner Doc。Part A 质量门槛为 80，Part B 为 85；
门槛只衡量文档可读性和契约完整性，不代表 Runtime、法律回答、安全或 Production 证据。
Round/Dxxx/Qxxx 追踪只保留在 Lab Session、Delta 和 Review Package，不写回 Canonical 正文。

## Guardrails

- 不因“企业级”保留服务；
- 不将 GraphRAG、Multi-Agent、Memory 或自研 Runtime 视为默认必要；
- WorkBuddy/Dify/Pi/LangGraph/RAGFlow 按层级比较；
- 任何质量、效率、安全和生产声明必须绑定测量证据。
- `AUTO_APPLY` 只允许不改变 Facts、Runtime、Schema/Migration、基础架构原则或 Active ADR 的
  Target/document refinement；否则必须升级 ADR 或 User Gate。
