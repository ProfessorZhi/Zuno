# Goal05 PHASE22 Benchmark Preflight Contract

status: contract_complete
date: 2026-08-01
branch: agent/minimax/phase22-benchmark-preflight-contract
base_branch: codex/goal05-phase15-sandbox-repair
base_sha: 09dc44164bfe6ca47afcbe655985ba76013b4387

## Problem

A green contract CI run does **not** mean a formal PHASE22 benchmark can
be started. Several upstream surfaces must be simultaneously satisfied
before the canonical four-profile benchmark is even *allowed to request*
runtime:

* governance — reviewer, eligibility, license, integrity
* dataset and snapshot — non-empty refs, valid SHA-256, positive candidate
  count, snapshot agreement across profiles
* gold evidence firewall — the runtime request schema must be
  gold-free, and the firewall must be **explicitly** proven on the input
  (it cannot be inferred from function / file / adapter names)
* runtime — every profile must be covered by attestations for product
  runtime, formal adapter wiring, knowledge, trace, result store,
  artifact store, usage, and budget settlement providers; ``local_graphrag``
  additionally needs index runtime, ``agentic_graphrag`` additionally needs
  agent-run runtime
* security — authorization, non-stale security epoch, formal execution
  approval
* budget — human-approved budget, valid policy ref, finite positive cost
  limit, positive token limit, non-empty deadline
* credentials and formal execution — credential ref present, formal
  credentials available, formal execution explicitly requested
* output contract — a stable output artifact ref must be present

The Contract CI only proves that the *code* of the contract compile and
passes tests. It does not prove that the *input* payload carries the
upstream attestations needed to launch a benchmark. The Preflight
Contract closes that gap.

## State Semantics

| State          | Meaning                                                                                                |
|----------------|--------------------------------------------------------------------------------------------------------|
| ``READY``      | All eleven gates passed. The benchmark caller may *request* a formal benchmark start.                  |
| ``BLOCKED``    | One or more required upstream surfaces are missing. The contract is satisfied; the upstream is not.    |
| ``INCOMPARABLE`` | The four canonical profiles disagree on case set, dataset version, snapshot, security epoch, or budget policy. |
| ``INVALID``    | Input structure, profile set, or field type is illegal. Future calls must use a corrected payload.    |

``READY`` deliberately does **not** mean:

* runtime has executed
* ``RUNTIME_OBSERVED`` has been recorded
* ``MEASURED`` evidence has been produced
* quality has been proven
* the platform is production-ready

## Gate Priority

The evaluator enforces the gate order strictly. Lower-numbered gates
short-circuit; later successes never mask earlier failures.

1. Input Structure
2. Profile Set
3. Comparability
4. Governance
5. Dataset and Snapshot
6. Gold Evidence Firewall
7. Runtime
8. Security
9. Budget
10. Credentials and Formal Execution
11. Output Contract

## Comparability Contract

All four canonical profiles must share the same:

* ``case_set_ref``
* ``dataset_version``
* ``corpus_snapshot_ref``
* ``security_epoch``
* ``budget_policy_ref``

Any disagreement is ``INCOMPARABLE`` — not ``BLOCKED``. The contract does
not attempt to resolve mismatches; it fails closed.

## Fixed Profile Set

The evaluator only accepts exactly the four canonical profiles:

* ``standard_rag``
* ``local_graphrag``
* ``deep_graphrag``
* ``agentic_graphrag``

Missing, duplicate, unknown, or extra profiles are ``INVALID``. Input
order does not affect the verdict; output is always in canonical order.

## CLI

```text
python tools/evals/zuno/rag_eval/run_phase22_preflight.py \
    --input <json path> \
    --output <json path>
```

The CLI:

* reads UTF-8 JSON (strict)
* does not access the network
* does not read environment secrets
* does not modify the input file
* creates the output directory if it does not exist
* outputs deterministic JSON (sorted keys, fixed separators, no NaN/Inf)
* appends a trailing newline
* writes only structured report data, never the credential value

Exit codes:

| Code | State           |
|------|-----------------|
| 0    | ``READY``       |
| 2    | ``BLOCKED``     |
| 3    | ``INCOMPARABLE``|
| 4    | ``INVALID``     |

The CLI never runs the benchmark itself.

## Input Fingerprint

``input_fingerprint`` is a 64-character lowercase SHA-256 hex over a
canonical JSON form of the structured input. Profile order changes do
not change the fingerprint; field changes do. No real credentials are
included; ``credential_ref`` is treated as a plain non-secret reference.

## Current

This PR provides:

* ``tools/evals/zuno/rag_eval/benchmark_preflight.py`` — the contract,
  with frozen dataclasses for ``BenchmarkPreflightInput``,
  ``ProfilePreflightInput``, ``BenchmarkPreflightReport``,
  ``ProfilePreflightResult``, and the ``BenchmarkPreflightEvaluator``
* ``tools/evals/zuno/rag_eval/run_phase22_preflight.py`` — the CLI
  entry point
* ``tests/evals/test_phase22_benchmark_preflight.py`` — 71 deterministic
  unit tests covering all 11 gates, the CLI, and the fingerprint
  invariants
* this evidence document

## Target

The future formal PHASE22 Benchmark Runner must call the Preflight
Evaluator before any retrieval, agent, or model invocation. A
non-``READY`` verdict must short-circuit the runner. The preflight
report (``input_fingerprint`` in particular) is the only allowed
upstream evidence for the "formal benchmark may start" claim.

## Not Claimed

This PR does **not** claim any of the following:

* Product Runtime has been wired or observed
* A real PHASE22 benchmark run has been executed
* Real credentials, AGENTS, or retrievers have been invoked
* Human review has been completed for the current candidate dataset
* Agentic GraphRAG effectiveness has been proven
* PHASE22 has been completed
* The platform is production-ready

In particular, the static ``READY`` produced by the unit tests is a
self-consistency check, not a benchmark execution. It must not be
submitted as a formal benchmark evidence artifact.
