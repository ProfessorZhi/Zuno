# Round #013 — Batch 002 — Verifier

Status: `VERIFIED_AND_ARCHIVED`  
Question count: **100**

Batch 002 deliberately asks implementation-level questions that may legitimately exceed Human Narrative depth. A PARTIAL verdict means the closed-book interview source cannot fully support the answer; it does not prove the historical code lacked the behavior.

## A. Tool / MCP / Agent implementation deep dive

| Q | Verdict | Sev | Gap | Reason | Next |
|---|---|---|---|---|---|
| B2-Q001 | PASS | S0 | NONE | PF-032 preserves the before/after topology at the correct abstraction level. | DECREASE_WEIGHT |
| B2-Q002 | PASS | S0 | NONE | Blue correctly distinguishes removed nesting/scaffolding from an unproven live second-model call. | DECREASE_WEIGHT |
| B2-Q003 | PARTIAL | S1 | EVIDENCE_GAP | Original design rationale / alternative review is not recovered; Blue can only give a retrospective engineering interpretation. | CONTINUE_NEXT_BATCH |
| B2-Q004 | PASS | S0 | NONE | Blue identifies direct-tool exposure scaling risk without inventing measurements. | DECREASE_WEIGHT |
| B2-Q005 | PASS | S0 | NONE | `EmitEventAgentMiddleware` and call-time tool→server user-config injection are canonically preserved. | DECREASE_WEIGHT |
| B2-Q006 | PARTIAL | S2 | EVIDENCE_GAP | Exact request-local storage/concurrency isolation for per-user MCP config is not preserved. This is high-value because the resume claim involves user-specific config. | ESCALATE_FINDING |
| B2-Q007 | PARTIAL | S1 | EVIDENCE_GAP | Config gate tests exist, but complete missing/invalid-config failure semantics are not extractable. | CONTINUE_NEXT_BATCH |
| B2-Q008 | PARTIAL | S1 | EVIDENCE_GAP | MCP discovery timing and schema refresh/version behavior are not recovered. | CONTINUE_NEXT_BATCH |
| B2-Q009 | PARTIAL | S1 | EVIDENCE_GAP | Namespace/collision behavior across multiple MCP servers is not documented. | CONTINUE_NEXT_BATCH |
| B2-Q010 | PASS | S0 | NONE | Recursion trigger, function and fix are explained from canonical PF-032. | DECREASE_WEIGHT |
| B2-Q011 | PARTIAL | S1 | EVIDENCE_GAP | One regression is proven; no general property/invariant test is recorded. | CONTINUE_NEXT_BATCH |
| B2-Q012 | PASS | S0 | NONE | Weather parser before/after and deterministic expected call are source-supported. | DECREASE_WEIGHT |
| B2-Q013 | PARTIAL | S1 | TRADEOFF_GAP | Why parsing lived in Workspace instead of model-schema generation has no recovered original decision record. | CONTINUE_NEXT_BATCH |
| B2-Q014 | PASS | S0 | NONE | Deterministic regression scope is correctly bounded and not sold as E2E. | DECREASE_WEIGHT |
| B2-Q015 | PARTIAL | S1 | DOC_GAP | Routing principle is present, but only one concrete historical direct-route example is canonical. | CONTINUE_NEXT_BATCH |
| B2-Q016 | PASS | S0 | NONE | Blue correctly refuses to back-port current Effects/Security controls into the April direct route. | DECREASE_WEIGHT |
| B2-Q017 | PARTIAL | S2 | EVIDENCE_GAP | Direct failure → ReAct behavior is unknown; for side-effect tools this could change duplicate-action risk. | ESCALATE_FINDING |
| B2-Q018 | PASS | S0 | NONE | Selector scaffolding vs proven live selector is phrased correctly. | DECREASE_WEIGHT |
| B2-Q019 | PARTIAL | S1 | EVIDENCE_GAP | Schema transformation/truncation before model exposure is not recovered. | CONTINUE_NEXT_BATCH |
| B2-Q020 | PARTIAL | S1 | EVIDENCE_GAP | Structured-result presentation is proven, broader result sanitization/truncation is not. | CONTINUE_NEXT_BATCH |
| B2-Q021 | PARTIAL | S1 | EVIDENCE_GAP | Historical MCP timeout/disconnect/schema-error propagation is not preserved. | CONTINUE_NEXT_BATCH |
| B2-Q022 | PARTIAL | S1 | EVIDENCE_GAP | Historical Tool concurrency/join behavior is not recovered. | CONTINUE_NEXT_BATCH |
| B2-Q023 | PASS | S0 | NONE | Blue keeps later idempotency/Effects semantics separate from personal April implementation. | DECREASE_WEIGHT |
| B2-Q024 | PARTIAL | S1 | EVIDENCE_GAP | No concrete historical route trace/log fields are recovered. | CONTINUE_NEXT_BATCH |
| B2-Q025 | PASS | S0 | NONE | Blue refuses unmeasured token/latency claims. | DECREASE_WEIGHT |
| B2-Q026 | PASS | S0 | NONE | Deterministic regression scope and E2E non-coverage are well explained. | DECREASE_WEIGHT |
| B2-Q027 | PASS | S0 | NONE | Current schema-drift target is clearly separated from history. | DECREASE_WEIGHT |
| B2-Q028 | PASS | S0 | NONE | Rebuild-today answer is evidence/scale gated rather than framework driven. | DECREASE_WEIGHT |
| B2-Q029 | PASS | S0 | NONE | Protocol/provider vs Zuno Agent-side glue/semantics boundary is explicit. | DECREASE_WEIGHT |
| B2-Q030 | PASS | S0 | NONE | Strongest interview story is prioritized around the best-supported causal chain. | DECREASE_WEIGHT |
| B2-Q031 | PASS | S0 | NONE | Broad commit ownership is correctly limited to diff-supported paths. | DECREASE_WEIGHT |
| B2-Q032 | PARTIAL | S2 | PROJECT_REALITY_GAP | No Issue/Review/task-assignment/status-check evidence connects the code change to a recovered project requirement. | ESCALATE_FINDING |
| B2-Q033 | PASS | S0 | NONE | Canonical PF-032 now supports a whiteboard-level minimal recursion repro. | DECREASE_WEIGHT |
| B2-Q034 | PASS | S0 | NONE | Later Effects design is not appropriated into the April claim. | DECREASE_WEIGHT |
| B2-Q035 | PASS | S0 | NONE | Engineering lesson is derived from evidenced simplification and boundary separation. | DECREASE_WEIGHT |

## B. Context / Memory implementation deep dive

| Q | Verdict | Sev | Gap | Reason | Next |
|---|---|---|---|---|---|
| B2-Q036 | PARTIAL | S1 | EVIDENCE_GAP | Function-level signature/input/output is not preserved in canonical interview evidence. | CONTINUE_NEXT_BATCH |
| B2-Q037 | PARTIAL | S2 | EVIDENCE_GAP | Exact `same-scope` key is central to the resume claim but not frozen in canonical docs. | ESCALATE_FINDING |
| B2-Q038 | PARTIAL | S2 | EVIDENCE_GAP | Cross-Matter/cross-Workspace negative isolation predicate cannot be reconstructed closed-book. | ESCALATE_FINDING |
| B2-Q039 | PARTIAL | S1 | EVIDENCE_GAP | Structured-memory field schema is not preserved. | CONTINUE_NEXT_BATCH |
| B2-Q040 | PARTIAL | S1 | EVIDENCE_GAP | APPROVED filtering layer (store query vs Python) is unknown. | CONTINUE_NEXT_BATCH |
| B2-Q041 | PARTIAL | S1 | PROJECT_REALITY_GAP | Full review state lifecycle and owner are not recovered. | CONTINUE_NEXT_BATCH |
| B2-Q042 | PARTIAL | S1 | EVIDENCE_GAP | Task-summary generator and failure semantics are not recovered. | CONTINUE_NEXT_BATCH |
| B2-Q043 | PARTIAL | S1 | IMPLEMENTATION_GAP | Summary freshness/staleness handling is not implementation-proven for the historical slice. | CONTINUE_NEXT_BATCH |
| B2-Q044 | PARTIAL | S1 | EVIDENCE_GAP | Source-trace storage location / exact record shape is not preserved. | CONTINUE_NEXT_BATCH |
| B2-Q045 | PARTIAL | S1 | EVIDENCE_GAP | Multi-source provenance cardinality and source-deletion behavior are unknown. | CONTINUE_NEXT_BATCH |
| B2-Q046 | PASS | S0 | NONE | Blue cleanly distinguishes proven policy elements from unproven token/ranking policy. | DECREASE_WEIGHT |
| B2-Q047 | PARTIAL | S1 | EVIDENCE_GAP | Prompt assembly order/template is not recovered. | CONTINUE_NEXT_BATCH |
| B2-Q048 | PARTIAL | S1 | IMPLEMENTATION_GAP | Duplicate-context handling is not proven. | CONTINUE_NEXT_BATCH |
| B2-Q049 | PARTIAL | S2 | IMPLEMENTATION_GAP | Conflict handling between summary and approved memory is not proven; stronger Domain authority exists only in later design. | ESCALATE_FINDING |
| B2-Q050 | PARTIAL | S1 | IMPLEMENTATION_GAP | Memory-store failure/degradation policy is not recovered. | CONTINUE_NEXT_BATCH |
| B2-Q051 | PASS | S0 | NONE | No latency/cache measurement is claimed. | DECREASE_WEIGHT |
| B2-Q052 | PARTIAL | S2 | IMPLEMENTATION_GAP | Context overflow/token-budget behavior is not proven for Zuno. | ESCALATE_FINDING |
| B2-Q053 | PARTIAL | S2 | IMPLEMENTATION_GAP | No relevance ranking/selection beyond scope+approval is proven, creating an obvious scale ceiling for long-term memory. | ESCALATE_FINDING |
| B2-Q054 | PASS | S0 | NONE | Review gate is accurately scoped to contract/readback hardening, not a full review platform. | DECREASE_WEIGHT |
| B2-Q055 | PARTIAL | S2 | EVIDENCE_GAP | No source proves all write paths cannot bypass review; only the readback gate is supported. | ESCALATE_FINDING |
| B2-Q056 | PASS | S0 | NONE | V2 write path and later PR #8 readback chronology is clear. | DECREASE_WEIGHT |
| B2-Q057 | PARTIAL | S1 | DOC_GAP | Minimal ContextOrchestrator vs GeneralAgent responsibility split is only partially preserved. | CONTINUE_NEXT_BATCH |
| B2-Q058 | PASS | S0 | NONE | Typed-contract value is explained without inventing implementation framework details. | DECREASE_WEIGHT |
| B2-Q059 | PARTIAL | S1 | EVIDENCE_GAP | Test counts are recovered, exact fixtures/test names are not. | CONTINUE_NEXT_BATCH |
| B2-Q060 | PARTIAL | S1 | EVIDENCE_GAP | Focused-test storage/backend (real DB vs mock) is not recorded. | CONTINUE_NEXT_BATCH |
| B2-Q061 | PARTIAL | S2 | EVIDENCE_GAP | Scope testing is claimed, but an exact cross-scope negative case is not extractable. | ESCALATE_FINDING |
| B2-Q062 | PARTIAL | S2 | IMPLEMENTATION_GAP | Prompt-injection / instruction-data isolation is not proven for the historical Context slice. | ESCALATE_FINDING |
| B2-Q063 | PARTIAL | S2 | IMPLEMENTATION_GAP | DocumentVersion-driven stale-memory invalidation is not proven; old APPROVED memory may remain readable in the historical model. | ESCALATE_FINDING |
| B2-Q064 | PASS | S0 | NONE | OpenViking and later V2/PR #8 evidence are correctly kept separate. | DECREASE_WEIGHT |
| B2-Q065 | PASS | S0 | NONE | Blue refuses to invent OpenViking build/buy rationale. | DECREASE_WEIGHT |
| B2-Q066 | PASS | S0 | NONE | Architecture evolution is explained as authority narrowing rather than denial of earlier work. | DECREASE_WEIGHT |
| B2-Q067 | PASS | S0 | NONE | Memory has a clear deletion/shrink condition when owner stores can reconstruct context. | DECREASE_WEIGHT |
| B2-Q068 | PASS | S0 | NONE | User-authored V2 chain is separated from the false “from-zero Memory” claim. | DECREASE_WEIGHT |
| B2-Q069 | PARTIAL | S2 | PROJECT_REALITY_GAP | The original product requirement / customer incident for the Context/Memory chain is not recovered; engineering causality stops at repository evolution. | ESCALATE_FINDING |
| B2-Q070 | PASS | S0 | NONE | Resume outcome is correctly restricted to tested policy/readback behavior. | DECREASE_WEIGHT |

## C. Project reality and personal ownership

| Q | Verdict | Sev | Gap | Reason | Next |
|---|---|---|---|---|---|
| B2-Q071 | PARTIAL | S1 | PROJECT_REALITY_GAP | March-to-April/June work chronology is incomplete. | CONTINUE_NEXT_BATCH |
| B2-Q072 | PARTIAL | S1 | PROJECT_REALITY_GAP | Team size/lead role are partially known, but task assignment/review chain is not. | CONTINUE_NEXT_BATCH |
| B2-Q073 | PARTIAL | S2 | PROJECT_REALITY_GAP | No version mapping proves the candidate's specific Tool/Memory changes entered a court-side test/Pilot build. | ESCALATE_FINDING |
| B2-Q074 | PASS | S0 | NONE | Customer quality feedback is correctly kept independent from PF-031. | DECREASE_WEIGHT |
| B2-Q075 | PARTIAL | S1 | OWNERSHIP_GAP | Later Target-document AI assistance / human review attribution is not canonically recorded, although historical implementation ownership remains correctly bounded. | CONTINUE_NEXT_BATCH |
| B2-Q076 | PASS | S0 | NONE | Research-product story is explicitly a Target/Product Hypothesis until measured. | DECREASE_WEIGHT |
| B2-Q077 | PASS | S0 | NONE | Candidate's irreducible personal contribution is evidence-ranked rather than inflated. | DECREASE_WEIGHT |
| B2-Q078 | PARTIAL | S1 | EVIDENCE_GAP | Database debugging bullet remains direction-level; no SQL/Issue/result loop is recovered. | CONTINUE_NEXT_BATCH |
| B2-Q079 | PASS | S0 | NONE | Current-code understanding is not treated as authorship. | DECREASE_WEIGHT |
| B2-Q080 | PASS | S0 | NONE | Pilot-vs-Production one-line answer is precise. | DECREASE_WEIGHT |
| B2-Q081 | PASS | S0 | NONE | First product slice is correctly framed as research/product strategy, not user-validated fact. | DECREASE_WEIGHT |
| B2-Q082 | PARTIAL | S1 | RESUME_CLAIM_RISK | “法律智能 Agent 平台” can over-prime interviewer expectations relative to the candidate's bounded ownership; body text mitigates but does not eliminate the risk. | CONTINUE_NEXT_BATCH |
| B2-Q083 | PASS | S0 | NONE | Evidence hierarchy is credible and does not invent business metrics. | DECREASE_WEIGHT |
| B2-Q084 | PASS | S0 | NONE | Implementation authorization and diagnostic-review boundary are explained correctly. | DECREASE_WEIGHT |
| B2-Q085 | PASS | S0 | NONE | Two-month prioritization favors correctness/evidence over feature expansion. | DECREASE_WEIGHT |

## D. Backend / distributed-systems fundamentals

| Q | Verdict | Sev | Gap | Reason | Next |
|---|---|---|---|---|---|
| B2-Q086 | PASS | S0 | NONE | Correct asyncio shared-state race explanation; explicitly not asserted as historical implementation. | DECREASE_WEIGHT |
| B2-Q087 | PASS | S0 | NONE | ContextVar / global / thread-local distinction is technically correct and bounded. | DECREASE_WEIGHT |
| B2-Q088 | PASS | S0 | NONE | Composite-index reasoning is appropriately conditional on query/cardinality. | DECREASE_WEIGHT |
| B2-Q089 | PASS | S0 | NONE | Transaction atomicity reasoning is correct without back-porting to PF-029. | DECREASE_WEIGHT |
| B2-Q090 | PASS | S0 | NONE | Read-Committed concurrency and CAS/locking alternatives are coherent. | DECREASE_WEIGHT |
| B2-Q091 | PASS | S0 | NONE | At-least-once / ACK crash / idempotent consumer explanation is correct. | DECREASE_WEIGHT |
| B2-Q092 | PASS | S0 | NONE | Logical-action identity is correctly distinguished from body hashing. | DECREASE_WEIGHT |
| B2-Q093 | PASS | S0 | NONE | Network uncertainty explanation is technically sound and consistent with Effects semantics. | DECREASE_WEIGHT |
| B2-Q094 | PASS | S0 | NONE | Cache authority / stale security distinction is correct. | DECREASE_WEIGHT |
| B2-Q095 | PASS | S0 | NONE | Optimistic version/CAS reasoning connects correctly to changing business prerequisites. | DECREASE_WEIGHT |
| B2-Q096 | PASS | S0 | NONE | Lease/fencing stale-writer scenario is correct and not claimed Current. | DECREASE_WEIGHT |
| B2-Q097 | PASS | S0 | NONE | Eventual projection lag vs owner truth is explained correctly. | DECREASE_WEIGHT |
| B2-Q098 | PASS | S0 | NONE | Expand/contract migration reasoning is sound and current Alembic blocker is honestly acknowledged. | DECREASE_WEIGHT |
| B2-Q099 | PASS | S0 | NONE | Provider quota/backpressure reasoning is correct. | DECREASE_WEIGHT |
| B2-Q100 | PASS | S0 | NONE | Tool/MCP is correctly selected as the stronger five-minute implementation story based on evidence depth. | DECREASE_WEIGHT |

## Batch 002 Verifier Summary

```text
PASS: 55
PARTIAL: 45
FAIL: 0
UNSUPPORTED_CLAIM: 0
```

The higher PARTIAL count is intentional: Batch 002 moved from architecture narrative into function/data-path/project-reality depth. The strongest split is now clear:

- **Tool/MCP:** core diff, middleware, recursion/weather defects and deterministic regressions are well supported; surrounding concurrency, discovery/version, error propagation, observability and original project rationale are not.
- **Context/Memory:** commit/PR chronology and readback policy are strong; exact scope/schema/query/reviewer/failure/token/relevance/security details are not sufficiently recoverable from canonical interview sources.
- **Fundamentals:** backend/distributed-systems reasoning derived from project claims is broadly defensible.

High-value deduplication targets for findings:

1. Tool/MCP surrounding runtime semantics + project-causality evidence gap.
2. Context/Memory exact scope/security/failure/scale evidence gap.
3. Specific personal changes cannot be tied to a recovered Pilot/court-test version.
4. Resume title still creates a mild “full Agent platform ownership” expectation risk.

No new Target Architecture contradiction was discovered in Batch 002.
