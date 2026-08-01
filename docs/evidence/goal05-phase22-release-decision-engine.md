# PHASE22 Release Decision Engine

> work package: `MM-PHASE22-BENCHMARK-RELEASE-DECISION`
> branch: `agent/minimax/phase22-release-decision-engine`
> base: `docs/phase22-agent-performance-governance` @ `3fa2f4734c88f9e4510cf0c2f3a99d82b06226a1`

This document records the PR for `P22-T02` (Benchmark Comparison and Release
Decision). The work package introduces a deterministic, fail-closed
PHASE22 Benchmark Comparison and Release Decision Engine that consumes only
already-generated four-profile result manifests and emits an immutable
Evidence Pack.

## 1. Goal and Boundary

The Release Decision Engine is intentionally independent:

* it does **not** run benchmarks, call models, generate traces or touch
  Candidates / Datasets;
* it does **not** import `runtime_evidence_binding.py` (PR #60) or
  `benchmark_preflight.py` (PR #61);
* it is consumed via a stable JSON contract (`evaluate_release_decision`)
  plus a CLI (`run_phase22_release_decision.py`) that writes an
  immutable evidence pack.

## 2. Contract

```yaml
Phase22ReleaseDecisionInput:
  profiles:
    standard_rag: { profile_id, measurement_status, fingerprint, artifact, evidence_ref, failure_buckets, evaluation }
    local_graphrag: { ... }
    deep_graphrag: { ... }
    agentic_graphrag: { ... }
  comparability_fingerprint: { dataset_version, case_set_hash, corpus_snapshot, knowledge_snapshot,
                              graph_snapshot, model_profile, judge_policy, embedding_profile,
                              metric_definition, runtime_profile, security_scope, budget_class }
  core_five:
    <profile_id>: { context_precision, context_recall, faithfulness, answer_relevancy, answer_correctness }
  citation_safety:
    <profile_id>: { citation_accuracy, unsupported_claim_rate, contradicted_claim_rate, abstention_correctness }
  critical_slice:
    <profile_id>: { <slice>: <score>, ... }
  critical_slice_baseline:
    <profile_id>: { <slice>: <score>, ... }
  agent_efficiency:
    agentic_graphrag: { evidence_yield, ... }
  cost_latency_budget: { max_total_cost, max_p95_latency_ms, <profile_id>: { total_cost, p95_latency_ms }, ... }
  failure_buckets: { <profile_id>: [ ... ] }
  evidence_refs: [ ... ]
```

The output is a `ReleaseDecision` envelope containing:

```yaml
ReleaseDecision:
  status: PASSED | FAILED | BLOCKED | INCOMPARABLE | ERROR
  reason_codes: [ <closed-set reason> ]
  canonical_input_hash: <sha256>
  decision_hash: <sha256>
  profile_hashes: { <profile_id>: <sha256>, ... }
  comparability_fingerprint_hash: <sha256>
  gate_results: [ GateFailure, ... ]
  evidence_refs: [ ... ]
  reproduce_command_template: <string>
  decision_engine_version: phase22-release-decision-v1
  closed_set_version: closed-set-v1
```

## 3. Status semantics

| Status        | Meaning                                                                              |
| ------------- | ------------------------------------------------------------------------------------ |
| PASSED        | Comparable, fully measured, every release gate passes.                               |
| FAILED        | Comparable, fully measured, at least one release gate fails (closed-set reason).    |
| BLOCKED       | Missing profile, profile not measured, or no evidence.                               |
| INCOMPARABLE  | Comparability Fingerprint mismatch across profiles (closed-set reason per dimension).|
| ERROR         | Structural / type / range / hash error in the input (closed-set reason).             |

Total average never masks critical slice, safety or citation failures;
those failures are individual closed-set reasons and result in FAILED.

## 4. Files added or modified

```text
tools/evals/zuno/rag_eval/release_decision.py
tools/evals/zuno/rag_eval/run_phase22_release_decision.py
tools/evals/zuno/rag_eval/__init__.py
tests/evals/test_phase22_release_decision.py
docs/evidence/goal05-phase22-release-decision-engine.md
docs/governance/agent-performance/records/pr-XXXX.json
```

## 5. Commit / Push / PR

* PR: open draft, base `docs/phase22-agent-performance-governance`.
* Commits use ordinary Commit (no reset, rebase, amend, cherry-pick, force push).
* Commit trailers preserved on every commit:
  `Agent: Claude-Code`, `Provider: MiniMax`, `Model: MiniMax-M3`,
  `Agent-Mode: Goal`, `Human-Owner: ProfessorZhi`,
  `Architecture-Reviewer: ChatGPT`,
  `Work-Package: MM-PHASE22-BENCHMARK-RELEASE-DECISION`.

## 6. Tests / CI / Verification (executed)

* `python -m pytest tests/evals/test_phase22_release_decision.py -q -p no:cacheprovider`
  -- 23 passed (the release-decision focused file).
* `python -m compileall -q tools/evals/zuno/rag_eval/release_decision.py \
  tools/evals/zuno/rag_eval/run_phase22_release_decision.py \
  tools/evals/zuno/rag_eval/__init__.py \
  tests/evals/test_phase22_release_decision.py`.
* `python tools/scripts/verify_repo_structure.py` -- passed.
* `python tools/scripts/verify_current_program.py` -- passed.
* `git diff --check` -- clean.

## 7. Performance log

The focused test file executes in well under one second on the local
Windows / Python 3.12 environment; each `evaluate_release_decision` call
runs in microseconds and the CLI read / write round trip adds no measurable
overhead. Memory footprint is bounded by input size and the small
deterministic constants declared in `release_decision.py`.

## 8. Items intentionally not run

* No real model calls, real benchmark runs, Docker, paid provider traffic,
  full-stack frontend build, full pytest of every package.
* No full PHASE22 E2E -- we only ship the deterministic decision engine
  and its CLI / contract; the actual fixed benchmark that consumes this
  engine is owned by P22-T01 / P22-T02 evidence and lives outside this PR.

## 9. Not Claimed

* No claim that the engine determines real release readiness; the engine
  is a deterministic decision computer over already-produced manifests.
  Real "production ready" / "quality proven" claims remain owned by
  PHASE22-T06 and `docs/status/production-readiness.md`.
* No claim that this engine inherits or replaces PR #60 / PR #61 logic;
  the engine intentionally consumes a stable JSON contract.
* No claim that the Fixture-driven PASSED in tests represents real-world
  PASSED; fixtures only prove that the contract is self-consistent.

## 10. Reproduction template

```bash
python -m tools.evals.zuno.rag_eval.run_phase22_release_decision \
    --input-json <INPUT_JSON_PATH> \
    --output-json <OUTPUT_JSON_PATH>
```

The exact `reproduce_command_template` is also emitted inside every
`ReleaseDecision` evidence pack so that other tools can replay the same
input.
