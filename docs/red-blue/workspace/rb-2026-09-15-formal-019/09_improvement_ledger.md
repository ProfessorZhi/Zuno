# Improvement Ledger — rb-2026-09-15-formal-019

status: `DRAFT_REVIEW`
change_effective_scope: `NEXT_ROUND_ONLY`
base_alignment_checked_against: `main@5844fe59` (2026-10-07)

## Base alignment (2026-10-07)

本轮冻结的 `zuno_base_sha = a8b0e540`（2026-09-15）已过时。收口前按当前 `main` 核对每项 Finding 的现状。**只标注现状，不重写本轮 verdict。**

- `IMP-019-03`：restart replay 把未完成 Reconciliation 错误升级为 `completed` 的缺陷**已在 main 修复**（`18e49733 fix: preserve effect certainty across reconciliation replay`；evidence `UNKNOWN EFFECT RESTART REPLAY: FIX VERIFIED / UNKNOWN PRESERVED`）。残余部分——remote-query 收敛 writer/consumer 仍未建立，现已按 `DEFERRED_BY_PROVIDER_CAPABILITY` 显式 Defer，属正当 Gap，不是静默缺陷。
- `IMP-019-04`：`MANDATORY_BEFORE_EFFECT` 存在但挡不住 send 的缺陷**已在 main 修复**（`2f709ec9` gate + `1b7b795b` requirement binding + `9b7891c6` capacity lifecycle；main 测试 `tests/security/test_mandatory_audit_postgres_boundary.py::test_external_effect_requires_durable_mandatory_audit_before_dispatch`；evidence `MANDATORY AUDIT BEFORE EFFECT: FIX VERIFIED / MISSING PROOF FAILS CLOSED`）。

其余项（01/02/05/06/07/08/09）经核对在 main 上**仍未闭合**，维持 `PENDING_USER_REVIEW`。

| ID | Priority | Classification | Primary Owner | Finding | Proposed action | Measurement / Retest | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-019-01 | P0 | ARCHITECTURE_GAP | Cross-cutting Architecture Owner | Structured long-term Memory retained as an optional Target, but record / recall eligibility / review / lifecycle Owner is not fully closed across 01/04/08/Provider boundaries | Keep no 10th business module; explicitly define Memory Provider facts, 08 recall/lifecycle authority, consumer boundaries, and that reviewed memory never becomes Domain truth; alternatively delete structured long-term Memory Target until A/B proves value | Future Red asks scope escalation, review bypass, revocation after packet build, conflict/delete ownership | PENDING_USER_REVIEW |
| IMP-019-02 | P0 | DOC_GAP | 04 Runtime + 05 Capability + 06 Effects + 08 Security | CapabilityVersion / ProviderBinding config / ToolVersion / SecurityEpoch / CredentialVersion exist but their dispatch-time consistency story is fragmented | Expand 04 resolved input-version set and add one plan-time v1 → dispatch-time v2 failure scenario; no new service/object unless needed | Schema/config drift fault test; paused run + provider/tool version change | PENDING_USER_REVIEW |
| IMP-019-03 | P0 | IMPLEMENTATION_GAP + DOC_GAP | 06 Effects + 04 Runtime | UNKNOWN Effect replay can be promoted to completed; final Reconciliation convergence writer/consumer is not established | Update Current docs to state the blocker explicitly; implementation plan for remote/manual convergence → conclusive receipt/resolved Effect truth | Re-run restart replay fault probe; require unresolved remains unknown until conclusive reconciliation | RESOLVED_ON_MAIN (replay bug fixed by 18e49733); RESIDUAL: convergence DEFERRED_BY_PROVIDER_CAPABILITY |
| IMP-019-04 | P0 | IMPLEMENTATION_GAP + DOC_GAP | 08 Security + 06 Effects | `MANDATORY_BEFORE_EFFECT` requirement exists but missing durable audit proof does not block current provider dispatch | Update Current docs; wire matching AuditPersistenceReceipt as send gate before dangerous effect | Negative probe: requirement exists, no receipt → executor must be 0 calls | RESOLVED_ON_MAIN (2f709ec9 / 1b7b795b / 9b7891c6; main gate test present) |
| IMP-019-05 | P1 | EVIDENCE_GAP | 03 Knowledge + 09 Evaluation | GraphRAG accumulated fusion/seed/alias/path heuristics without holdout/ablation; 5-query smoke only proves regression repair | Run frozen independent multi-hop eval: Hybrid, +fusion, incremental/leave-one-out; quality+citation+latency/cost/fallback | Delete heuristics that do not add stable holdout gain | PENDING_USER_REVIEW |
| IMP-019-06 | P1 | DOC_GAP / NARRATIVE_GAP | Cross-cutting Architecture Owner | Context source trace/provenance can be misread as truth or semantic-preservation proof | Add invariant: provenance proves origin/transformation, not truth, authorization, or semantic preservation; mark non-compressible/reference-preserving content | Future Red asks summary dropped qualifier / false-source provenance | PENDING_USER_REVIEW |
| IMP-019-07 | P1 | RESUME_GAP | Resume Builder | Workspace direct route is real work but weakly measured and consumes too much interview surface | Merge direct-route hardening into Tool/MCP bullet in next resume candidate | Future Red should still be able to ask route boundary without a separate headline bullet | PENDING_USER_REVIEW |
| IMP-019-08 | P2 | RED_SKILL_GAP | Red Skill Maintainer | Historical questions occasionally presuppose mature Target objects | Add rule: historical pressure may ask capability boundary/failure, but must not mark absence of later Target object as historical failure | Next round audit Red1 wording | PENDING_USER_REVIEW |
| IMP-019-09 | P2 | BLUE_SKILL_GAP | Blue Skill Maintainer | Candidate answers are technically strong but often longer/more architecture-complete than realistic interview speech | Default 20–60s answer; answer one layer first, expand only after follow-up | Human-read sample of 20 Blue answers for spoken naturalness | PENDING_USER_REVIEW |
| IMP-019-10 | P2 | NO_CHANGE | Cross-cutting Architecture Owner | No evidence that Persistent Multi-Agent / Specialist or always-on Native Runtime is required | Keep Tool → Subgraph → worker → Specialist → Persistent Multi-Agent ladder and measurement gate | A/B only when real workload exposes context/policy/recovery/throughput need | KEEP |
| IMP-019-11 | P2 | NO_CHANGE | Cross-cutting Architecture Owner | Generic Host + minimal Legal Backend survives subtraction test | Preserve ADR-0008 baseline; do not make Zuno own commodity session/workflow/MCP infrastructure | A/B/C benchmark before Runtime expansion | KEEP |

## Approval rule

`PENDING_USER_REVIEW` items are proposals only. No canonical Architecture / Modules / implementation truth changes until the user approves all or a subset. Current round verdict remains immutable.
