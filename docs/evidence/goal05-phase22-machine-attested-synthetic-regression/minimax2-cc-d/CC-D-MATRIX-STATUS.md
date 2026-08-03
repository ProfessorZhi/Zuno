# PHASE22 CC-D Matrix Status (MiniMax2)

Worker: minimax2
Provider: MiniMax
Worker-Task: PHASE22-CC-D
Base-SHA: 87f6eeed994d1db28f25ad916e052b3a3cd00992
Branch: claude/minimax2-phase22-cc-d
Dependency-PR: codex/phase22-real-synthetic-benchmark-readiness
Dependency-Head-SHA: NOT_RUN_DEPENDENCY_BLOCKED

## Matrix Status

```
matrix_status: NOT_RUN_DEPENDENCY_BLOCKED
snapshot_id: null
profile_run_ids: []
case_count: 22
status_counts: {NOT_RUN_DEPENDENCY_BLOCKED: 22, PASSED: 0, FAILED: 0, BLOCKED: 0, NOT_RUN: 0}
```

Every fault / security / resume / idempotency case is fully specified with
all required fields, but every row stays `NOT_RUN_DEPENDENCY_BLOCKED` until
DeepSeek CC-B delivers `snapshot_id` plus the three visibility receipts and
CC-C delivers `profile_run_ids`. This is the structural enforcement of
"no fake receipts", "no fake PASSED", and "no port reachable == write/read
verified".

## What this PR Adds

* `tools/evals/zuno/synthetic_benchmark/phase22_cc_d_fault_matrix.yaml` —
  static matrix with the 22 cases required by the CC-D task card. Every
  case carries every required field; no receipt_ref / trace_ref / status
  is forged.
* `tools/evals/zuno/synthetic_benchmark/phase22_cc_d_fault_matrix.py` —
  loader and structural contract enforcer. Used by tests and the verifier.
* `tools/scripts/phase22_environment_probe.py` — Docker / environment
  probe. Records service versions, ports, namespace, and exit codes.
  Always sets `service_write_read_verified: false` (port reachable !=
  write/read verified).
* `tools/scripts/phase22_fault_matrix_runner.py` — per-case structural
  recorder. Never executes live runtime while matrix is blocked.
* `tools/scripts/phase22_evidence_builder.py` — evidence bundle
  generator with secret / credential redaction.
* `tools/scripts/verify_phase22_cc_d_evidence.py` — verifier that
  enforces the structural and redaction contracts.
* `tests/evals/test_phase22_cc_d_fault_security_resume_matrix.py` —
  dependency-free structural tests (parametrized owner namespace, all
  required fields, no receipts, status accuracy, redaction).
* `tests/integration/test_phase22_cc_d_environment_probe.py` —
  dependency-free integration tests that exercise the probe binary,
  the verifier, and the forgery-rejection path.
* `docs/evidence/goal05-phase22-machine-attested-synthetic-regression/minimax2-cc-d/`
  — generated evidence directory containing:
    * `environment_probe.json` (probe output, no secrets)
    * `fault_matrix_run.json` (per-case run records, recorded-not-executed)
    * `evidence_bundle.json` (structured bundle with commands, exit codes,
      versions, cleanup, redaction manifest)

## Forbidden Actions Respected

| Rule                                               | Enforced by                                              |
| -------------------------------------------------- | -------------------------------------------------------- |
| Port reachable != write/read verified              | env probe `service_write_read_verified = false`          |
| No handwritten receipt                             | matrix loader; verifier; tests                           |
| No handwritten trace                               | matrix loader; verifier; tests                           |
| No deleted failure assertions                      | all required fields kept; tests enforce presence         |
| No secret leakage                                  | redaction regex in builder + verifier + tests            |
| No UNKNOWN side effect blind retry                 | D-UNKNOWN-SIDE-EFFECT row says `reconciliation_required` |
| No snapshot activation without receipt             | matrix says `snapshot_activation_blocked`                |
| No BLOCKED rewritten as PASSED                     | verifier + tests reject status flips                    |

## Required Fields per Case

The CC-D task card requires the following fields per matrix row, all of
which are present and validated by `phase22_cc_d_fault_matrix.verify_matrix()`:

* case_id
* trigger
* state_before
* state_after
* owner
* failure_class
* propagation
* retryability
* recovery
* idempotency_key
* receipt_ref (null while blocked)
* trace_ref (null while blocked)
* test_command
* exit_code
* cleanup
* status
* not_run_reason

## Owner Namespace

Each case declares its owner from one of:

* knowledge_ingestion
* object_store
* postgres_domain
* knowledge_index
* snapshot_activation
* observability
* gold_isolation
* release_decision
* fault_recovery
* security_isolation
* runtime_resume
* evidence_reproducibility

The verifier enforces that all 12 owners are declared.

## Dependency Linkage

This PR explicitly records its dependency on the DeepSeek hand-off PR
(`codex/phase22-real-synthetic-benchmark-readiness`). Once that PR
delivers `snapshot_id` and the four `profile_run_ids`, the matrix rows
that have authentic `receipt_ref` and `trace_ref` may flip from
`NOT_RUN_DEPENDENCY_BLOCKED` to `PASSED`. No row may flip without those
runtime receipts.

## Remaining Gaps

1. DeepSeek CC-B must produce the three visibility receipts and
   `snapshot_id` before any ingestion-related row can move.
2. DeepSeek CC-C must produce four `profile_run_ids` and the measurement
   attestation before any profile-related row can move.
3. Once the receipts land, the verifier will need to be re-run end-to-end
   against the live bundle.