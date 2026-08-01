# Goal05 PHASE22 — Runtime Evidence Binding Contract

Status: contract implemented, v2 repair (validation only, not wired to any
runtime).  Version 2 fixes the PR #58 review findings: fixed gap code
vocabulary, Mapping-only never-raise validator, frozen INCOMPARABLE
semantics, and a uniform hash-helper exception contract.

## Problem

Fields alone are not evidence.  A runtime can return `runtime_status`,
`trace_id`, `budget_settlement_ref` or any number of receipt-shaped fields —
and even declare `is_test_double = false` or
`__zuno_product_authority__ = ...` — without any of that being true.  If the
eval layer treats "the runtime returned these fields" as "a formal Product
Runtime execution happened", then a test double, a stub, a degraded adapter,
or a hallucinated payload can be reported as an official benchmark result.

Formal runtime evidence must therefore **prove and bind**:

- Eval Run / Case / Requested Profile / Actual Profile
- Runtime Name / Runtime Version
- Corpus Snapshot / Trace
- SecurityDecision / PlanVersion / RunOutcome
- UsageReceipt / BudgetSettlement / ArtifactReceipt
- Result Payload / Receipt Owner / Payload Hash / Reference Binding Hash

A binding is a single serialized record in which every reference, owner,
version, snapshot and hash is internally consistent, and whose
`reference_binding_hash` is the canonical SHA-256 of the bound fields.  A
binding that validates is *self-consistent evidence*; it is not a claim that
a runtime ran.

This contract is **validation only**:

- It never creates a Product Runtime, a composition root, a receipt, or any
  evidence.
- It never calls a model or an external service.
- It never auto-completes missing evidence and never returns
  `RUNTIME_OBSERVED` or `MEASURED`.
- It accepts only serialized evidence data (a mapping) — never runtime
  objects and never self-declared authority fields.

## Ownership

Every receipt type has exactly one factual owner.  The owner map is defined
once in `tools/evals/zuno/rag_eval/runtime_evidence_binding.py`
(`RECEIPT_OWNERS`) and is the single source of truth for both the validator
and the tests.

| Receipt type        | Factual owner    |
| ------------------- | ---------------- |
| SecurityDecision    | security         |
| PlanVersion         | agent_core       |
| RunOutcome          | agent_core       |
| UsageReceipt        | model_gateway    |
| BudgetSettlement    | budget           |
| Trace               | observability    |
| ArtifactReceipt     | artifact_store   |

A receipt whose claimed owner differs from the map is untrustworthy and
blocks the binding.

### Required receipts per profile

| Profile          | Required receipts                                                                 |
| ---------------- | --------------------------------------------------------------------------------- |
| standard_rag     | SecurityDecision, Trace, UsageReceipt, BudgetSettlement, ArtifactReceipt           |
| local_graphrag   | SecurityDecision, Trace, UsageReceipt, BudgetSettlement, ArtifactReceipt           |
| deep_graphrag    | SecurityDecision, Trace, UsageReceipt, BudgetSettlement, ArtifactReceipt           |
| agentic_graphrag | SecurityDecision, PlanVersion, RunOutcome, UsageReceipt, BudgetSettlement, Trace, ArtifactReceipt |

PlanVersion / RunOutcome are **not forced** for non-agentic profiles: the
repository contract provides no evidence that they are mandatory there
(`CanonicalCaseResult` declares the ref fields as receipts that are empty
until formal receipt types exist).  An extra known receipt type is allowed
only when it is bound one-to-one with a non-empty top-level reference.

For `local_graphrag`, the graph index is covered by the top-level binding:
the artifact receipt must carry the same snapshot as the top-level
`corpus_snapshot_ref` (INCOMPARABLE otherwise).  No separate "index"
receipt type exists, and none is invented.

### tenant_id / workspace_id

The repository task contracts require `tenant_id` / `workspace_id`, so the
binding validates them when they are present: explicitly present-but-empty
values are INVALID.  Absent values are simply not part of the binding — no
default tenant, workspace or snapshot is ever invented.

## Validation Flow

```
Input (Mapping only)
  └─ 1. Input Structure        → mapping of strings, receipts list      INVALID
       └─ 2. Identity          → eval_run_id, case_id non-empty         INVALID
            └─ 3. Profile      → known profile, requested == actual     INVALID / INCOMPARABLE
                 └─ 4. Runtime → runtime_name, runtime_version          BLOCKED
                      └─ 5. Snapshot → corpus_snapshot_ref, trace_id    BLOCKED
                           └─ 6. Receipts → required per profile        BLOCKED
                                └─ 7. Owner → owner map matches         BLOCKED
                                     └─ 8. Version → receipt == main    INCOMPARABLE
                                          └─ 9. Snapshot → receipt == main INCOMPARABLE
                                               └─ 10. Hash format       INVALID
                                                    └─ 11. Ref binding  BLOCKED
                                                         └─ 12. Reference binding hash BLOCKED
                                                              └─ Result
```

Every stage that can be safely evaluated runs; gap codes are returned in
stage order.  The result state is the state of the highest-priority failing
stage.  The reference binding hash stage only runs when the binding fields
are complete and every hash format is legal, so a broken record reports its
real cause instead of a spurious hash mismatch.

## State Semantics

| State       | Meaning                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------- |
| VALID       | Evidence is structurally complete and consistently bound (owner, hashes, snapshot, runtime version, references, reference binding hash). VALID ≠ RUNTIME_OBSERVED, ≠ MEASURED, ≠ QUALITY_PROVEN, ≠ PRODUCTION_READY. |
| INCOMPARABLE| Evidence cannot be compared as-is: `requested_profile` ≠ `actual_profile`; any receipt `runtime_version` ≠ top-level `runtime_version`; any receipt `snapshot_ref` ≠ top-level `corpus_snapshot_ref`; local GraphRAG artifact snapshot mismatch. |
| BLOCKED     | Evidence is missing, incomplete, untrustworthy, or a binding failed: runtime version missing, snapshot missing, receipt missing, owner mismatch, reference binding errors, reference binding hash mismatch. |
| INVALID     | Input structure, profile name or hash format is illegal: wrong field types, missing keys, illegal receipt structure, unknown profile, malformed SHA-256. |

When an early INVALID and a later INCOMPARABLE occur together, the earliest
failing stage's state wins while gap codes are still returned completely for
every stage that can safely run.

The contract never produces `RUNTIME_OBSERVED`, `MEASURED`,
`QUALITY_PROVEN` or `PRODUCTION_READY` — those are measurement-gate and
release-gate concepts, not binding concepts.

### Gap codes

Gap codes are a **fixed closed vocabulary**:

- Pure lowercase snake_case, matching `^[a-z][a-z0-9_]*$`.
- The complete set is exported as `ALL_GAP_CODES`; the validator only ever
  returns codes from that set.
- No code contains input values: no ref, hash, tenant, workspace, raw
  receipt type, secret or runtime name ever appears in a gap code.
- Unknown receipt types are unified to the single fixed code
  `unknown_receipt_type`, reported at most once regardless of how many
  distinct unknown types are present.
- Known receipt types use fixed per-type codes, e.g.
  `security_decision_receipt_owner_mismatch`,
  `trace_receipt_snapshot_mismatch`.
- Same input always yields the same ordered result.

## Public API and exception contract

- `RuntimeEvidenceBindingValidator.validate(binding)` accepts a `Mapping`
  (serialized evidence) only.  A `RuntimeEvidenceBinding` instance or any
  other object is INVALID with `input_type_invalid`.  The immutable
  dataclasses are internal frozen structures and are never an unvalidated
  public input.  The validator never raises on malformed input and never
  mutates its input.
- `compute_reference_binding_hash(binding)` raises a uniform `ValueError`
  (fixed message, never containing input values) for missing fields, wrong
  types, non-mapping receipts and illegal collections.  The validator
  converts any such condition into a validation state and never raises.

## Hash Contract

`compute_reference_binding_hash(...)` in
`tools/evals/zuno/rag_eval/runtime_evidence_binding.py`:

- Python standard library only (`json`, `hashlib`).
- Canonical JSON: `sort_keys=True`, stable separators `(",", ":")`, UTF-8.
- SHA-256, output lowercase 64-char hex.
- Field insertion order and receipt list order do not affect the result;
  any change to a bound field changes the result.
- The canonical payload contains no secret, no token, no expected answer,
  no gold document, no gold evidence and no citation ground truth.
- The validator only verifies a provided `reference_binding_hash`; it never
  generates or writes a hash back, and it never mutates its input.

## Current

This PR (replacement for #58, stacked on the #59 governance base)
implements:

- The deterministic, fail-closed evidence binding contract
  (`RuntimeEvidenceBinding`, `RuntimeReceiptBinding`,
  `BindingValidationState`, `BindingValidationResult`).
- The Mapping-only validator (`RuntimeEvidenceBindingValidator`) with the
  12-stage fixed priority flow above.
- The fixed gap code vocabulary (`ALL_GAP_CODES`) with the review-mandated
  repair (no raw input in codes, unknown types unified and deduplicated).
- The frozen INCOMPARABLE semantics (profile, runtime version, snapshot,
  local GraphRAG artifact snapshot).
- The uniform ValueError contract for the hash helper.
- 90 unit tests covering all four profiles, every gap-code class, hash
  determinism, gold/secret exclusion, input immutability, never-raise
  hostile inputs, and the neutrality of self-declared authority fields.

No static VALID JSON is committed anywhere in this PR: nothing here pretends
to be running evidence.

## Target

In the future, real evidence is produced jointly by:

- Product Runtime
- Composition Root
- Model Gateway
- Security
- Budget
- Observability
- Artifact Store

Each owner will emit its own receipts with factual owner, runtime version,
snapshot and payload hashes; the composition root will assemble and sign the
binding; this validator will verify it before any measurement gate consumes
it.

## Not Claimed

- Product Runtime is wired to this contract.
- A Product Runtime has run.
- `RUNTIME_OBSERVED`.
- A benchmark has been measured.
- Agentic GraphRAG effectiveness has been proven.
- PHASE22 is complete.
- Production readiness.
