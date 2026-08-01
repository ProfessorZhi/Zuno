# Goal05 PHASE22 Benchmark Preflight Contract (v3)

status: contract_v3_complete
date: 2026-08-01
branch: agent/minimax/phase22-benchmark-preflight-contract-v2
base_branch: docs/phase22-agent-performance-governance
base_sha: 3fa2f4734c88f9e4510cf0c2f3a99d82b06226a1
supersedes: PR #57 (agent/minimax/phase22-benchmark-preflight-contract)

## Repair Scope

This v2 supersedes PR #57 because the original first commit lacked the
attribution trailers required by the governance base. The replacement
re-applies the same files with the v2 code review fixes applied:

- Contract review feedback (3 P1, 2 P2) is addressed.
- The replacement commits carry full attribution trailers.

## Problem

A green contract CI run does **not** mean a formal PHASE22 benchmark can
be started. Several upstream surfaces must be simultaneously satisfied
before the canonical four-profile benchmark is even *allowed to request*
runtime:

* governance -- reviewer, eligibility, license, integrity
* dataset and snapshot -- non-empty refs, valid SHA-256, positive
  candidate count, snapshot agreement across profiles
* gold evidence firewall -- the runtime request schema must be
  gold-free, and the firewall must be **explicitly** proven on the input
  (it cannot be inferred from function / file / adapter names)
* runtime -- attestations for product runtime, formal adapter wiring,
  knowledge, trace, result store, artifact store, usage, and budget
  settlement providers; ``local_graphrag`` additionally needs index
  runtime, ``agentic_graphrag`` additionally needs agent-run runtime
* security -- authorization, non-stale security epoch, formal execution
  approval
* budget -- human-approved budget, valid policy ref, finite positive
  cost limit, positive token limit, non-empty deadline
* credentials and formal execution -- credential ref present, formal
  credentials available, formal execution explicitly requested
* output contract -- a stable output artifact ref must be present

The Contract CI only proves that the *code* of the contract compiles and
passes tests. It does not prove that the *input* payload carries the
upstream attestations needed to launch a benchmark. The Preflight
Contract closes that gap.

## State Semantics

| State           | Meaning                                                                                                |
|-----------------|--------------------------------------------------------------------------------------------------------|
| ``READY``       | All ten gates passed. The benchmark caller may *request* a formal benchmark start.                     |
| ``BLOCKED``     | One or more required upstream surfaces are missing. The contract is satisfied; the upstream is not.    |
| ``INCOMPARABLE``| The four canonical profiles disagree on case set, snapshot, security epoch, or budget policy.          |
| ``INVALID``     | Input structure, profile set, or field type is illegal. Future calls must use a corrected payload.    |

### State Ownership (frozen)

* ``INVALID`` is reserved for:
  * top-level payload not an object (``input_not_object``)
  * unknown / extra top-level field (``input_unknown_field``)
  * required field type error (``input_type_invalid_<field>``)
  * NaN / Infinity in numeric field (``input_invalid_number``)
  * profile set error (missing / duplicate / unknown / extra)
  * unparseable structure

* ``BLOCKED`` is reserved for value-level surface failures:
  * reviewer not approved, benchmark not eligible, license / integrity
    not verified
  * non-positive candidate_count, non-positive cost / token limit
  * empty / missing required refs (case_set_ref, dataset_version,
    dataset_hash, snapshot, authorization_ref, security_epoch,
    budget_policy_ref, deadline, credential_ref, output_artifact_ref)
  * ``runtime_request_schema_gold_free`` missing or false
  * missing / false attestations (runtime / adapter / store / provider)
  * security_epoch_stale true, formal_execution_approved false
  * human_budget_approved false, formal_credentials false,
    formal_execution_requested false

  A missing required field is always a BLOCKED produced by the gate that
  owns it -- never INVALID.

* ``INCOMPARABLE`` is reserved for cross-profile disagreement on the
  shared comparability surface (case_set_ref, dataset_version,
  corpus_snapshot_ref, security_epoch, budget_policy_ref).

``READY`` deliberately does **not** mean:

* runtime has executed
* ``RUNTIME_OBSERVED`` has been recorded
* ``MEASURED`` evidence has been produced
* quality has been proven
* the platform is production-ready

When a comparability field is empty on any profile / top-level field,
the appropriate ownership gate (Dataset / Security / Budget) produces
the ``*_missing`` gap code; the Comparability gate skips the mismatch
check so the missing-surface gap code is not preempted.

## Gate Priority

The evaluator enforces the gate order strictly. Lower-numbered gates
short-circuit; later successes never mask earlier failures. Eleven
gates are defined; the fixed order is:

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

Any disagreement is ``INCOMPARABLE`` -- not ``BLOCKED``. The contract
does not attempt to resolve mismatches; it fails closed.

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

* reads UTF-8 JSON (strict; rejects NaN / Infinity via ``parse_constant``)
* does not access the network
* does not read environment secrets
* does not modify the input file
* creates the output directory if it does not exist
* outputs deterministic JSON (sorted keys, fixed separators, no NaN/Inf)
* appends a trailing newline
* writes only structured report data, never credential values
* any output write failure (mkdir / open / write) maps to exit 4

Exit codes:

| Code | State           |
|------|-----------------|
| 0    | ``READY``       |
| 2    | ``BLOCKED``     |
| 3    | ``INCOMPARABLE``|
| 4    | ``INVALID`` (or input / parse / write / CLI usage failure) |

The CLI never runs the benchmark itself. Argparse errors map to exit
code 4 (not the argparse default of 2) and never print a Python
traceback. Output write failures (directory creation, open, write) all
map to exit code 4 with a fixed error code (``output_dir_creation_failed``
or ``output_write_failed``); the absolute path, Windows user name, and
raw OS exception are never copied into stderr.

## Input Fingerprint

``input_fingerprint`` is a 64-character lowercase SHA-256 hex over the
canonicalised payload. The canonicalisation normalises the profile list
to canonical order so reordering does not change the fingerprint, and
the canonicalisation never depends on the evaluator's state. Any
failure mode that produces a meaningful payload (INCOMPARABLE,
BLOCKED, INVALID with a structured payload) still produces a
fingerprint based on the *raw* payload, so that two structurally
different inputs always produce different fingerprints and two
structurally identical inputs always produce the same fingerprint.

No real credentials are included in the fingerprint;
``credential_ref`` is treated as a plain non-secret reference.

## Gap Code Vocabulary

Every gap code emitted by the contract matches the fixed regular
expression ``^[a-z][a-z0-9_]*$``. No gap code embeds the raw profile
name, a secret, a ref, a hash, a runtime name, user input, a newline,
or any other arbitrary substring. All profile set errors share the
fixed code ``profile_unknown``; profile string-field type errors share
``profile_string_field_type_invalid``; profile boolean-field type
errors share ``profile_boolean_field_type_invalid``.

## Current

This PR provides:

* ``tools/evals/zuno/rag_eval/benchmark_preflight.py`` -- the contract,
  with frozen dataclasses for ``BenchmarkPreflightInput``,
  ``ProfilePreflightInput``, ``BenchmarkPreflightReport``,
  ``ProfilePreflightResult``, and the ``BenchmarkPreflightEvaluator``
  enforcing eleven gates in fixed order
* ``tools/evals/zuno/rag_eval/run_phase22_preflight.py`` -- the CLI
  entry point with strict JSON parsing, argparse exit-4 handling, and
  write-failure handling
* ``tests/evals/test_phase22_benchmark_preflight.py`` -- 114
  deterministic unit tests covering all eleven gates, the CLI, the
  fingerprint invariants, the state-ownership rules, the gap-code
  vocabulary, and the I/O fail-closed behaviour
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
* Real credentials, agents, or retrievers have been invoked
* Human review has been completed for the current candidate dataset
* Agentic GraphRAG effectiveness has been proven
* PHASE22 has been completed
* The platform is production-ready

The static ``READY`` produced by the unit tests is a self-consistency
check, not a benchmark execution. It must not be submitted as a formal
benchmark evidence artifact.
