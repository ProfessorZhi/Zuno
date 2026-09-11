# Findings — rb-2026-09-11-architecture-thesis-009

Round result: `PASS_WITH_THREE_NARRATIVE_GAPS`  
Highest severity: `MEDIUM`

This round deliberately avoided generic system-design questions such as “how do you scale workers?” or “what is the HA plan?”. It tested whether the overall Architecture exposes the deeper thesis of a long-running legal-AI system: how independently versioned facts can be combined safely, how uncertainty is represented, and what auditability means when model execution is nondeterministic.

## F1 — Formal Admission lacks an explicit overall causal-coherence explanation

**Type:** `NARRATIVE_GAP`  
**Severity:** `MEDIUM`

The Engineering Reference already requires Admission to bind normalized business input, expected DomainVersion and causation refs, and the Domain Reference already checks freshness/version/security/human prerequisites. The design therefore contains the pieces.

The overall Part A does not yet explain the stronger invariant those pieces serve: a formal result must be based on a set of independently versioned facts that can still coexist in one valid business world. It is not enough that every referenced object exists individually.

A candidate produced from DocumentVersion V3 / KnowledgeGeneration G7 / CapabilityVersion C2 can become unsafe if, before admission, V4 changes the relevant premise, SecurityEpoch advances, the professional semantic contract changes, or the human review applies to a different candidate. The architecture must revalidate the dependencies that affect business correctness rather than compose “latest” or “available” refs from different times.

The repair should explain **causal coherence as a property**, not introduce a new `ValidityEnvelope`, `CausalSnapshot` or other object unless a later implementation task proves one is required.

**Primary sources:**
- `docs/architecture/reference.md` — Version / Freshness / Causation Bindings
- `docs/modules/domain/reference.md` — Admission guards and non-domain provenance refs
- `docs/modules/reference.md` — late-result acceptance checks

## F2 — Uncertainty preservation is present in examples but not stated as a cross-cutting architecture thesis

**Type:** `NARRATIVE_GAP`  
**Severity:** `MEDIUM`

Several modules already handle different forms of insufficient evidence correctly:

- Knowledge distinguishes retrieval miss from proof of absence and exposes incomplete coverage;
- Effects preserves Outcome Unknown after a possible send;
- Security fails closed when authorization freshness or mandatory prerequisites cannot be established;
- model/Capability output remains candidate material until semantic and business acceptance occurs.

These are not four unrelated error-handling tricks. They express one architectural discipline: **when the system lacks evidence required to strengthen a claim, it preserves the weaker state instead of guessing the stronger one.**

The overall Architecture currently demonstrates the cases but does not name the common principle. Making the relationship explicit would explain why Zuno repeatedly uses readiness, candidate/admission, unknown/reconcile and fail-closed boundaries without turning them into one generic status machine.

The repair must also preserve the distinction between uncertainty classes: incomplete knowledge calls for more coverage or abstention; unknown external effects call for reconciliation; unknown security eligibility blocks protected action; uncertain model quality remains a candidate / evaluation problem. A shared principle does not imply shared states.

**Primary sources:**
- `docs/modules/knowledge/README.md` — retrieval miss versus absence
- `docs/modules/effects/README.md` — Outcome Unknown and Reconcile
- `docs/modules/security/README.md` — stale/unknown security prerequisites fail closed
- `docs/modules/model-gateway/README.md` and Capability docs — transport success does not create business truth

## F3 — Overall Architecture does not distinguish auditability from deterministic rerun

**Type:** `NARRATIVE_GAP`  
**Severity:** `MEDIUM`

The Model Gateway Part A already acknowledges that the same model name can drift and that model output is not naturally reproducible. The overall Architecture, however, still uses “recover”, “rebuild” and “reproduce” language without making the audit contract explicit for nondeterministic model execution.

For a legal work product, the strongest realistic audit guarantee may be: reconstruct the material/version scope, exact inputs and configuration available to Zuno, Provider/model identity and available version metadata, returned output, human edits, security context, and the reasons the result was formally admitted. A later rerun is a new computation and may produce different tokens or reasoning even when the original Provider name is unchanged.

This distinction matters because a legal audit asks “why did the system accept this result then?”, not merely “can today’s model say something similar?”. Exact deterministic replay should only be promised where the underlying component actually supports immutable snapshots and deterministic execution.

The repair should define this as an overall evidentiary boundary without claiming that all required Current persistence already exists.

**Primary sources:**
- `docs/modules/model-gateway/README.md` — model drift and non-reproducible output
- `docs/modules/evaluation/README.md` — versioned reproducible evaluation
- `docs/architecture/architecture.md` — state/recovery and historical WorkProduct narrative

## Scenarios reviewed but not promoted to overall findings

The round also attacked negative legal claims under incomplete corpus coverage, historical truth versus current validity, action-bound human/security authority, post-delivery invalidation, generation activation isolation, and Capability semantic versioning. Those concerns are already sufficiently explained by their Owner narratives or by the newly deepened overall consistency/recovery sections. Duplicating their full local semantics into `architecture.md` would reduce readability rather than deepen the overall design.

The correct repair is therefore bounded to the three cross-cutting thesis gaps above.
