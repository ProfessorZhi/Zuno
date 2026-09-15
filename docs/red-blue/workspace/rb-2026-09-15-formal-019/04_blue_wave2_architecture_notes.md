# Blue Wave 2 Architecture Notes — SEALED FROM RED

status: `COMPLETE`
visibility: `SEALED_FROM_RED`

这些是 Blue Architecture Reviewer 的第二次初诊，不是候选人口头答案。Red Final 禁止读取。

## Provisional findings

### B2-A — Historical Tool/MCP and current Tool Authority are easy to conflate
- signal: Red2 repeatedly exposed that the 2026-04 path had binding/config hardening but no durable Effect semantics.
- canonical check: project provenance explicitly forbids backporting PreparedAction / Approval / Idempotency / EffectReceipt / Reconcile into April history.
- classification: `NARRATIVE_GAP` + `OWNERSHIP_GAP`, not necessarily current architecture gap.
- simplest fix: architecture/project docs should keep one short historical call-chain section and one separate current Tool authority section.
- retest: ask future Blue to answer “April Tool Calling safe for state-changing effects?” in one sentence without borrowing current runtime.

### B2-B — Tool identity/config/schema lifecycle needs one explicit version-consistency story
- signal: user-bound Agent instance, call-time config drift, schema refresh, canonical tool identity and retry consistency required many open-design answers.
- current/target check: current architecture has stronger SecurityEpoch/effect semantics, but the cross-document story for ToolVersion/CapabilitySnapshot/ConfigVersion is less obvious than the Effect story.
- classification: likely `DOC_GAP`; promote to `ARCHITECTURE_GAP` only if Owner/Authority/Version semantics are actually inconsistent in canonical docs.
- simplest fix: add one end-to-end failure scenario: plan sees Tool schema/config v1 → config/schema changes → execution must reject/replan or bind a frozen version.
- exit condition: do not create a new service merely to document this; reuse Capability/Security/Runtime owners.

### B2-C — Direct route should remain an optimization, not an architectural branch
- signal: no latency/cost/reliability benchmark; rules risk growing into a custom NLU layer.
- classification: `EVIDENCE_GAP` / possibly resume simplification; `NO_ZUNO_CHANGE` unless current architecture grants direct route independent authority.
- recommendation: one unified Tool execution authority; deterministic route may only choose candidate Tool/args and must be deletable.

### B2-D — GraphRAG current implementation has a clean regression story but accumulated heuristics lack causal evidence
- signal: threshold 6/9, min-rank protection, seed cap 8, alias/path heuristics, tiny latency sample, no holdout/ablation.
- classification: `EVIDENCE_GAP`; not architecture gap while GraphRAG remains query-class/measurement gated.
- simplest experiment: baseline Hybrid → +fusion → add each seed/alias/path change separately; independent multi-hop holdout; report quality + citation + latency/cost + fallback reason.
- deletion rule: if fusion-only restores baseline and other changes do not add stable holdout gain, delete the extra heuristics.

### B2-E — Memory V2 foundation exposes a real Authority boundary: scope equality is not authorization
- signal: project/thread omission can widen effective scope; reviewer authority, APPROVED bypass, revocation after ContextPack build, async re-materialization, dedupe/conflict all need a policy owner.
- canonical direction: Security should own authorization/lifecycle policy; Memory owns memory state/readback; Context consumes an authorized snapshot.
- classification: `DOC_GAP` if canonical docs already assign these owners consistently; `ARCHITECTURE_GAP` if Memory can mutate/read authoritative scope without Security enforcement.
- required scenario: approved memory enters packet → permission/delete changes before model call → SecurityEpoch/MemoryVersion revalidation blocks stale readback.

### B2-F — Memory lifecycle needs a clearer distinction between expiry, supersession, conflict and privacy deletion
- signal: Blue2 had to invent a lifecycle explanation from general principles.
- classification: likely `DOC_GAP`, possibly `IMPLEMENTATION_GAP` for current runtime.
- simplest design: do not add another Memory state machine unless current canonical lifecycle cannot express these cases; first document owner and required facts.

### B2-G — Context trace is observability, not correctness authority
- signal: source ids and compression trace cannot prove a summary preserved a legal qualifier.
- classification: `NARRATIVE_GAP` / `DOC_GAP`.
- recommendation: docs should state which content is reference-preserving/non-compressible and which can be summarized; trace only proves what transformation happened.

### B2-H — Generic Host + Zuno Legal Backend remains the right complexity baseline
- signal: Blue2 consistently reduced the system to Generic Host/Single Agent + controlled RAG + Tool adapter + PostgreSQL domain backend, and only added Native Runtime/Multi-Agent/GraphRAG/long-term Memory under measurement gates.
- classification: `NO_ZUNO_CHANGE` for topology.
- recommendation: preserve ADR-0008 baseline; do not introduce Multi-Agent just because interview questions make it sound sophisticated.

### B2-I — Durable recovery must reconcile Domain / Effect / Security truth before trusting Runtime checkpoint
- signal: remote effect succeeds then checkpoint write fails; stale specialist returns after replan.
- canonical direction: checkpoint is control progress, not business/effect truth.
- classification: inspect final canonical docs before deciding. Known effect-reconciliation convergence remains a likely implementation/evidence blocker.

## Provisional priority

1. Clarify Tool version/config/schema consistency across Capability/Security/Runtime without adding a new service.
2. Clarify Memory authorization + lifecycle/revocation boundary and Context pre-call freshness check.
3. Reduce GraphRAG claims to regression-fix + measurement-gated optional path; run proper ablation before preserving all heuristics.
4. Keep direct route explicitly deletable and subordinate to one Tool execution authority.
5. Preserve Generic Host + Legal Backend baseline and Single Controller default; do not upgrade topology without evidence.
