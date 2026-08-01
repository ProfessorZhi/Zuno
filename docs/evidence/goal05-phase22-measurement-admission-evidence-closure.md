# PHASE22 Measurement Admission Evidence Closure

> work package: `DS-PHASE22-MEASUREMENT-ADMISSION-EVIDENCE-CLOSURE`
> base: `docs/phase22-agent-performance-governance` @ `07b60aa2372a9fcb327f3cc8e7ac99a4993f7235`
> supersedes: #60 (Runtime Evidence Binding) and #61 (Benchmark Preflight)
> after architecture acceptance

This document records the consolidated evidence for the two deterministic
control boundaries that gate whether a PHASE22 benchmark may be requested
and whether any claimed runtime execution binds to serialized evidence:

1. **Benchmark Preflight** (`tools/evals/zuno/rag_eval/benchmark_preflight.py`)
   -- answers exactly one question: is the upstream confirmed-contract
   surface sufficient to *request the start* of a formal benchmark?
2. **Runtime Evidence Binding** (`tools/evals/zuno/rag_eval/runtime_evidence_binding.py`)
   -- validates-only contract that binds a claimed Product Runtime
   execution to its serialized receipts.

Both boundaries are deterministic, fail-closed, read-only and never-raise.
Neither executes retrieval, agents, models, or paid providers; neither
touches the network, environment secrets, real credentials, the Candidate
Dataset or the Product Runtime.

## 1. Control surface ownership

| Control boundary             | Module                                    | Public entry                                  |
| ---------------------------- | ----------------------------------------- | --------------------------------------------- |
| Benchmark Preflight          | `tools/evals/zuno/rag_eval/benchmark_preflight.py` | `evaluate_payload` / `BenchmarkPreflightEvaluator.evaluate` |
| Preflight CLI                | `tools/evals/zuno/rag_eval/run_phase22_preflight.py` | `run` / `main`                                |
| Runtime Evidence Binding     | `tools/evals/zuno/rag_eval/runtime_evidence_binding.py` | `RuntimeEvidenceBindingValidator.validate` / `compute_reference_binding_hash` |
| Release Decision (merged)    | `tools/evals/zuno/rag_eval/release_decision.py` | `evaluate_release_decision` (unchanged)       |

The merged Release Decision engine is untouched by this work package and
does not import either control module.

## 2. Benchmark Preflight fixed semantics

| State        | Meaning                                                                               |
| ------------ | ------------------------------------------------------------------------------------- |
| `READY`      | all 11 gates fully pass; the benchmark may be requested. `READY` is NOT `MEASURED`.    |
| `BLOCKED`    | valid structure but a required business precondition is missing, empty or whitespace-only, or a required surface value fails. |
| `INCOMPARABLE` | every compared value on the four canonical profiles is present and non-blank, and at least one pair differs. |
| `INVALID`    | input structure, profile set, field type, NaN / Infinity, or a non-empty illegal hash. |

Fixed ownership rules:

* `case_set_ref`, `dataset_version` (Dataset gate), `security_epoch`
  (Security gate) and `budget_policy_ref` (Budget gate) that are missing,
  empty or whitespace-only are BLOCKED by the gate that owns the field,
  at both top level and per-profile level.
* `dataset_hash` that is missing, empty or whitespace-only is BLOCKED with
  `dataset_hash_missing`; only a non-empty but illegal SHA-256 is INVALID.
* `bool` never impersonates `int`/`float`; NaN/Infinity are INVALID.
* `READY` requires every one of the 11 gates to pass.
* The public evaluator, the convenience wrapper and the CLI never raise.
  The CLI emits no traceback, no raw OS exception, no absolute path, no
  user name and no secret; CLI failures map to fixed codes and exit 4.
* Every gap code is fixed and never embeds user input.

### The 11 gates (evaluation priority order)

| #  | Gate                        | Owns / enforces                                                            |
| -- | --------------------------- | -------------------------------------------------------------------------- |
| 1  | Input Structure             | object shape, unknown fields, field types, bool-vs-number, NaN/Infinity, non-empty illegal dataset hash |
| 2  | Profile Set                 | exactly the four canonical profiles, no duplicates, no unknown profiles    |
| 3  | Comparability               | cross-profile agreement on case set, dataset version, corpus snapshot, security epoch, budget policy |
| 4  | Governance                  | run identity, reviewer approval, eligibility, license, integrity           |
| 5  | Dataset and Snapshot        | case_set_ref, dataset_version, dataset_hash, candidate_count, corpus snapshot, per-profile owned refs |
| 6  | Gold Evidence Firewall      | runtime request schema proven gold-free                                    |
| 7  | Runtime                     | per-profile attestation, adapter wiring, runtime name/version, provider availability |
| 8  | Security                    | authorization_ref, security_epoch (top + profile), staleness, formal execution approval |
| 9  | Budget                      | human approval, budget_policy_ref (top + profile), cost/token limits, deadline |
| 10 | Credentials and Formal Execution | credential_ref, formal credentials, formal execution requested         |
| 11 | Output Contract             | output_artifact_ref                                                        |

## 3. Runtime Evidence Binding fixed semantics

| State          | Meaning                                                                                  |
| -------------- | ---------------------------------------------------------------------------------------- |
| `VALID`        | structure, owner, reference, hash, version and snapshot are all complete and consistent. `VALID` is NOT `RUNTIME_OBSERVED`, NOT `MEASURED`. |
| `BLOCKED`      | missing or blank value, untrusted owner, unbound reference, missing required receipt.    |
| `INCOMPARABLE` | both comparison sides are non-blank and differ (profile, runtime version or snapshot).   |
| `INVALID`      | input shape / type, illegal hash, unknown profile, unknown keys with wrong shapes.       |

Fixed ownership rules:

* Two identical unknown `receipt_type` values never raise `KeyError`; every
  unknown type (distinct or repeated) maps to the single fixed,
  deduplicated code `unknown_receipt_type`.
* Blank (empty or whitespace-only) top-level `runtime_version` and
  `corpus_snapshot_ref` are BLOCKED exactly like missing values.
* INCOMPARABLE is only produced when both sides are non-blank and differ.
* The public validator accepts serialized `Mapping` input only, never
  raises, and never returns VALID through a broad except.
* Every gap code belongs to the fixed closed `ALL_GAP_CODES` vocabulary and
  never contains raw input values, paths, hashes, accounts or secrets.
* The canonical reference binding hash never contains secrets, tokens,
  expected answers, gold documents or citation ground truth.

## 4. Cross-contract truths

* Preflight `READY` does not equal `MEASURED`.
* Runtime Binding `VALID` does not equal `RUNTIME_OBSERVED` or `MEASURED`.
* Without formal measurement facts, the merged Release Decision remains
  `BLOCKED` no matter how complete the preflight surface is.
* `runtime_evidence_binding`, `benchmark_preflight` and the merged
  `release_decision` import together on this governance base without
  circular dependencies; the Release Decision engine imports neither
  control module.
* The control surface never emits `RUNTIME_OBSERVED`, `MEASURED`,
  `QUALITY_PROVEN` or `PRODUCTION_READY`.

## 5. Tests

* `tests/evals/test_runtime_evidence_binding.py` -- ported from #60 plus
  the V3 closure tests (duplicate unknown receipt types never raise,
  deduplicated unknown reason, blank runtime_version / snapshot_ref BLOCKED,
  non-empty mismatch INCOMPARABLE).
* `tests/evals/test_phase22_benchmark_preflight.py` -- ported from #61 plus
  the V4 blank-field fail-closed tests (missing / empty / whitespace-only
  owned fields BLOCKED, dataset_hash blank BLOCKED, non-empty malformed
  hash INVALID, none ever READY, 11 gates documented).
* `tests/evals/test_phase22_measurement_control_contracts.py` -- six
  cross-contract truth tests.

## 6. Intentionally not run / not claimed

* No real model calls, no paid provider traffic, no real benchmark runs,
  no real credentials.
* No Product Runtime wiring, no Candidate Dataset or Product Runtime
  changes, no migration / database model changes, no shared Performance
  Ledger changes, no workflow changes.
* No reset, rebase, amend, cherry-pick or force push.
* This evidence does not claim production readiness or program completion.
* Final status: `BOUNDARY_ACCEPTED_NOT_MERGE_READY`.
