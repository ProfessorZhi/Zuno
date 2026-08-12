# Legal Eval & Benchmark：怎样证明做得对？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 如何公平测量法律质量、效率、安全和服务复杂度收益？
owner: Eval / Observability
replaces: `docs/project/modules/10-observability-eval.md`（Superseded）

## A/B/C

| Variant | fixed | variable |
|---|---|---|
| A | same base model, raw corpus, tools, legal prompt/skills, token/time budget | WorkBuddy Generic Legal Agent |
| B | same as A | WorkBuddy + Zuno Legal Capabilities via MCP/API |
| C | same as A/B and same capabilities | Zuno Native Runtime + first-class Domain State/staleness/HITL |

Interpretation: `C > B > A` supports Legal Intelligence and Runtime; `C ≈ B > A` supports Legal Backend, not Native Runtime; `C ≈ B ≈ A` deletes unmeasured complexity.

## Metrics

- Quality：Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict/Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Task Completion。
- Efficiency：Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、re-plan/retry rate、Domain State Reuse Rate。
- Service：queue lag、CPU/GPU、memory、failure isolation、retry storm、deployment rollback、cross-service trace completeness。
- Security：no-egress、allowlist、secret leakage、cross-tenant、prompt injection/tool、sandbox escape、revoked permission、stale credential、duplicate effect、SBOM/signature。

不得只报告 LLM Judge；每个结果要绑定 dataset/version/model/provider/service profile、trace 和 evidence。

## Legal Evaluation Layers

研究背景只提供 PUBLIC_CONTEXT，不是 Zuno Current，也不证明 Zuno 已复现论文结果。它为
评测分层提供了可借鉴的方向：LawBench 将中文法律能力拆成 20 个任务和记忆、理解、应用
三个认知层级；LJPCheck 说明总体 Accuracy/F1 不能替代针对公平性、鲁棒性和边界行为的
功能测试；JIA 以事件抽取、事件对齐和冲突检测显式构造案件中间结构；Fact–Article
Correspondence 说明细粒度事实—法条关系可以作为独立任务测量；InternLM-Law 同时报告
自动任务、人工法律咨询和长文本评测。详见
[`legal-ai-capability-matrix.md`](../../../project-reconstruction-lab/sources/legal-ai-capability-matrix.md)。

据此，Zuno Target Eval 分为：

| 层级 | 测量对象 | 不能推出的结论 |
|---|---|---|
| L1 Domain Capability | Event、Fact、Fact–Article、Conflict、Evidence Retrieval 等能力 Contract | 不能推出 Runtime 或产品整体更好 |
| L2 Legal Cognition | 法律知识记忆、理解、应用/推理 | 不能替代真实案件任务 |
| L3 Functional Behavior | 缺证、冲突、无关属性变化、法条版本变化、应拒答/应过期等行为 | 不能只用平均 Accuracy 概括 |
| L4 Real Task Outcome | 法院/法律 QA、证据充分性、引用正确性、人工接受率、完整性、耗时 | 不能把历史 Demo 当作测量结果 |
| L5 Agent System | Task Completion、Recovery、Domain State Reuse、Tool/Model/Retrieval 成本与延迟 | 不能归因于 Domain-aware Runtime 而不做 B 对照 |

### H2 — Runtime–Domain Integration Advantage

A/B/C 的主要目的，是把 Legal Intelligence 的价值与 Native Runtime 的额外价值拆开：

```text
A Generic Host
  < B Generic Host + Zuno Legal Capabilities
  < C Zuno Runtime + first-class Domain State
```

只有在相同模型、语料、工具、能力、Prompt/Skill 质量、Token/时间预算和独立数据切片
下，C 相对 B 的收益仍然可重复，并能归因于 Domain State、EvidenceRequirement、
staleness/dependency 或 Review 对账，才可以支持 Native Runtime 的保留。否则应将结论
收敛为 `C ≈ B > A`，保留 Legal Backend、删除或缩减 Native Runtime。

## Worker boundary

Eval/benchmark runs are asynchronous batch jobs. Product API submits a job and returns receipt; Eval Worker owns dataset/run/result/release gate facts. It不能提升 Domain Finding、质量或 Production Readiness，除非有通过的证据协议。

`A/B/C` 是 `Q039-B / P0-E` 的 Target Contract，不是已执行结果。相同模型、语料、工具、预算和
评测集下，只有 `C >> B >> A` 且收益可归因于 first-class Domain State、EvidenceRequirement、
staleness/dependency 或 Review 对账，才允许 Native Runtime 继续存在；`C ≈ B >> A` 应收缩为
Legal Backend；`C ≈ B ≈ A` 必须删除无证据复杂度。

## Current / Target / Gap

- Current：仓库有 eval tooling、trace structures and blocked/not-measured status；没有公平 A/B/C 运行结果。
- Target：独立 Eval/Trace Worker 与可复现 release gate。
- Gap：法律真实数据、标注、reviewer protocol、重复运行、成本/延迟和 service-level evidence。
