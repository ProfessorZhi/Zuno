# Improvement Ledger — rb-2026-09-15-formal-019

status: `APPROVED`
change_effective_scope: `NEXT_ROUND_ONLY`
base_alignment_checked_against: `main@5844fe59` (2026-10-07)
user_improvement_review: `APPROVED 2026-10-07 — IMP-019-01 / 02 / 05 / 06 approved; IMP-019-07 / 08 / 09 deferred`
approval_recheck: `2026-10-07 — IMP-019-01 / 02 / 06 verified ALREADY_IMPLEMENTED_ON_MAIN; only IMP-019-05 actionable`
application_status: `APPLIED_WITH_BLOCKER — IMP-019-05 deliverable landed on main; its measurement is BLOCKED_PENDING_DATA`
applied_changes: `IMP-019-05 → docs/governance/rb019-graphrag-ablation-protocol.md @ main@da321b1a (PR #277)`

## Base alignment (2026-10-07)

本轮冻结的 `zuno_base_sha = a8b0e540`（2026-09-15）已过时。收口前按当前 `main` 核对每项 Finding 的现状。**只标注现状，不重写本轮 verdict。**

- `IMP-019-03`：restart replay 把未完成 Reconciliation 错误升级为 `completed` 的缺陷**已在 main 修复**（`18e49733 fix: preserve effect certainty across reconciliation replay`；evidence `UNKNOWN EFFECT RESTART REPLAY: FIX VERIFIED / UNKNOWN PRESERVED`）。残余部分——remote-query 收敛 writer/consumer 仍未建立，现已按 `DEFERRED_BY_PROVIDER_CAPABILITY` 显式 Defer，属正当 Gap，不是静默缺陷。
- `IMP-019-04`：`MANDATORY_BEFORE_EFFECT` 存在但挡不住 send 的缺陷**已在 main 修复**（`2f709ec9` gate + `1b7b795b` requirement binding + `9b7891c6` capacity lifecycle；main 测试 `tests/security/test_mandatory_audit_postgres_boundary.py::test_external_effect_requires_durable_mandatory_audit_before_dispatch`；evidence `MANDATORY AUDIT BEFORE EFFECT: FIX VERIFIED / MISSING PROOF FAILS CLOSED`）。

其余项经核对在 main 上的现状：

- `IMP-019-01`（Memory/Context Authority 收口）：**已实现**。`docs/architecture/architecture.md` §Context 和 Memory 不形成第十个业务 Authority 逐点覆盖本项要求（不新增第 10 模块 / Memory 为非权威 Context Provider / 08 定 Recall 与 lifecycle / 01·04 消费当前 snapshot / 02 拥有更高 Authority）。引入于 `c7c4f249 docs: tighten project and 1+9 architecture narrative`（2026-09-15 15:36）。
- `IMP-019-02`（版本依赖链串联）：**已实现**。`docs/architecture/architecture.md` §版本变化沿依赖链处理，以及 `docs/modules/runtime/reference.md`（line 79 / 101 / 156）已明确 resolved input-version set 的覆盖面与各 Owner 的兼容性判断。同属 `c7c4f249` / `4a1875c1`。
- `IMP-019-06`（provenance invariant）：**已实现**。`docs/architecture/architecture.md:125-129` 逐字含 `Provenance != Truth != Authorization != Semantic Preservation`。引入于 `c7c4f249`，并由 `256c9812 docs: sharpen architecture narrative ownership`（#276）精修。
- `IMP-019-05`（GraphRAG holdout/ablation）：**协议已落地，测量仍被阻塞**。冻结协议已作为 `docs/governance/rb019-graphrag-ablation-protocol.md` 并入 `main@da321b1a`（PR #277）。协议本身不声称任何收益结论；它把「逐项 heuristic 是否有稳定 holdout 增益、无增益即删」写成可执行且可证伪的判据。**执行仍为 `BLOCKED_PENDING_DATA`**：本机无数据集、无模型凭证与运行时索引，且 `docs/evidence/current-eval-baseline.md` 自身即 `MEASUREMENT_BLOCKED`。因此在数据就绪前，不得据此项声称 GraphRAG 质量或启发式有效性。
- `IMP-019-07` / `08` / `09`：流程项，已 defer。

> Workflow finding：本轮 `zuno_base_sha = a8b0e540`（2026-09-15）与实现上述架构改动的提交 `c7c4f249` 同日，导致 ledger 重新发现了已上线的架构改动。后续轮次必须把 base 钉在当前 `main`。

| ID | Priority | Classification | Primary Owner | Finding | Proposed action | Measurement / Retest | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-019-01 | P0 | ARCHITECTURE_GAP | Cross-cutting Architecture Owner | Structured long-term Memory retained as an optional Target, but record / recall eligibility / review / lifecycle Owner is not fully closed across 01/04/08/Provider boundaries | Keep no 10th business module; explicitly define Memory Provider facts, 08 recall/lifecycle authority, consumer boundaries, and that reviewed memory never becomes Domain truth; alternatively delete structured long-term Memory Target until A/B proves value | Future Red asks scope escalation, review bypass, revocation after packet build, conflict/delete ownership | ALREADY_IMPLEMENTED_ON_MAIN (c7c4f249) |
| IMP-019-02 | P0 | DOC_GAP | 04 Runtime + 05 Capability + 06 Effects + 08 Security | CapabilityVersion / ProviderBinding config / ToolVersion / SecurityEpoch / CredentialVersion exist but their dispatch-time consistency story is fragmented | Expand 04 resolved input-version set and add one plan-time v1 → dispatch-time v2 failure scenario; no new service/object unless needed | Schema/config drift fault test; paused run + provider/tool version change | ALREADY_IMPLEMENTED_ON_MAIN (c7c4f249 / 4a1875c1; 04 reference L79/101/156) |
| IMP-019-03 | P0 | IMPLEMENTATION_GAP + DOC_GAP | 06 Effects + 04 Runtime | UNKNOWN Effect replay can be promoted to completed; final Reconciliation convergence writer/consumer is not established | Update Current docs to state the blocker explicitly; implementation plan for remote/manual convergence → conclusive receipt/resolved Effect truth | Re-run restart replay fault probe; require unresolved remains unknown until conclusive reconciliation | RESOLVED_ON_MAIN (replay bug fixed by 18e49733); RESIDUAL: convergence DEFERRED_BY_PROVIDER_CAPABILITY |
| IMP-019-04 | P0 | IMPLEMENTATION_GAP + DOC_GAP | 08 Security + 06 Effects | `MANDATORY_BEFORE_EFFECT` requirement exists but missing durable audit proof does not block current provider dispatch | Update Current docs; wire matching AuditPersistenceReceipt as send gate before dangerous effect | Negative probe: requirement exists, no receipt → executor must be 0 calls | RESOLVED_ON_MAIN (2f709ec9 / 1b7b795b / 9b7891c6; main gate test present) |
| IMP-019-05 | P1 | EVIDENCE_GAP | 03 Knowledge + 09 Evaluation | GraphRAG accumulated fusion/seed/alias/path heuristics without holdout/ablation; 5-query smoke only proves regression repair | Run frozen independent multi-hop eval: Hybrid, +fusion, incremental/leave-one-out; quality+citation+latency/cost/fallback | Delete heuristics that do not add stable holdout gain | APPLIED_AS_FROZEN_PROTOCOL (main@da321b1a / PR #277); MEASUREMENT_BLOCKED_PENDING_DATA |
| IMP-019-06 | P1 | DOC_GAP / NARRATIVE_GAP | Cross-cutting Architecture Owner | Context source trace/provenance can be misread as truth or semantic-preservation proof | Add invariant: provenance proves origin/transformation, not truth, authorization, or semantic preservation; mark non-compressible/reference-preserving content | Future Red asks summary dropped qualifier / false-source provenance | ALREADY_IMPLEMENTED_ON_MAIN (c7c4f249; refined by 256c9812) |
| IMP-019-07 | P1 | RESUME_GAP | Resume Builder | Workspace direct route is real work but weakly measured and consumes too much interview surface | Merge direct-route hardening into Tool/MCP bullet in next resume candidate | Future Red should still be able to ask route boundary without a separate headline bullet | PENDING_USER_REVIEW |
| IMP-019-08 | P2 | RED_SKILL_GAP | Red Skill Maintainer | Historical questions occasionally presuppose mature Target objects | Add rule: historical pressure may ask capability boundary/failure, but must not mark absence of later Target object as historical failure | Next round audit Red1 wording | PENDING_USER_REVIEW |
| IMP-019-09 | P2 | BLUE_SKILL_GAP | Blue Skill Maintainer | Candidate answers are technically strong but often longer/more architecture-complete than realistic interview speech | Default 20–60s answer; answer one layer first, expand only after follow-up | Human-read sample of 20 Blue answers for spoken naturalness | PENDING_USER_REVIEW |
| IMP-019-10 | P2 | NO_CHANGE | Cross-cutting Architecture Owner | No evidence that Persistent Multi-Agent / Specialist or always-on Native Runtime is required | Keep Tool → Subgraph → worker → Specialist → Persistent Multi-Agent ladder and measurement gate | A/B only when real workload exposes context/policy/recovery/throughput need | KEEP |
| IMP-019-11 | P2 | NO_CHANGE | Cross-cutting Architecture Owner | Generic Host + minimal Legal Backend survives subtraction test | Preserve ADR-0008 baseline; do not make Zuno own commodity session/workflow/MCP infrastructure | A/B/C benchmark before Runtime expansion | KEEP |

## Applied changes (2026-10-07)

批准项中唯一 actionable 的 `IMP-019-05`，已落地的**只是协议**，不是结论：

```text
IMP-019-05 → docs/governance/rb019-graphrag-ablation-protocol.md
             main@da321b1a (PR #277)
```

协议冻结了 9 条待检验启发式与各自可关闭开关的位置、结论判据（无稳定 holdout 增益即删除）、指标（含首要指标 `FullChainHit@5` / `Recall@5`）、冻结切分、`real_runtime` 执行流程与报告要求，并显式声明当前状态 `BLOCKED_PENDING_DATA`。

**没有发生的事**（必须保持，直到新 Evidence 出现）：

- 没有删除任何启发式 —— 还没有 holdout 数据来支持「该删」或「该留」；
- 没有产生任何 GraphRAG 收益结论 —— `limit=10/20/50` 的调参结果不是 holdout，不能替代；
- 没有把任何 Target 升级成 Current。

`IMP-019-01 / 02 / 06` 经核对已在 main 实现（见上方 Base alignment），无需重复落地。

## Approval rule

`PENDING_USER_REVIEW` items are proposals only. No canonical Architecture / Modules / implementation truth changes until the user approves all or a subset. Current round verdict remains immutable.
