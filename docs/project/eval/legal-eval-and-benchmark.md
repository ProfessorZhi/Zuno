# Legal Eval & Benchmark：怎样证明做得对？

status: normative-target
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

## Worker boundary

Eval/benchmark runs are asynchronous batch jobs. Product API submits a job and returns receipt; Eval Worker owns dataset/run/result/release gate facts. It不能提升 Domain Finding、质量或 Production Readiness，除非有通过的证据协议。

## Current / Target / Gap

- Current：仓库有 eval tooling、trace structures and blocked/not-measured status；没有公平 A/B/C 运行结果。
- Target：独立 Eval/Trace Worker 与可复现 release gate。
- Gap：法律真实数据、标注、reviewer protocol、重复运行、成本/延迟和 service-level evidence。
