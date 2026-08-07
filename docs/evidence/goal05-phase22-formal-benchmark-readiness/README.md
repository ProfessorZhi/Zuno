# PHASE22 Formal Benchmark Execution Readiness (P22-T01)

phase_id: PHASE22
work_package: PHASE22-T01-FORMAL-BENCHMARK-EXECUTION-READINESS
worker: deepseek2
agent_name: DeepSeek-PHASE22-Benchmark-Readiness
execution_client: Claude Code
provider: DeepSeek
base_sha: 83c1bbd0689d1b2b3b4ffd7f3983de813da11ebb
status: READY_FOR_FORMAL_EXECUTION_CONTRACT_AVAILABLE
measurement_status: blocked_not_measured

## Summary

The fixed EnterpriseRAG benchmark was previously only reachable through
contract smoke / `blocked_not_measured` evidence. This slice adds the
**formal execution entry** that turns "cannot measure" into a precise,
machine-readable contract:

- `tools/evals/zuno/rag_eval/run_phase22_formal_benchmark.py`
  (`phase22-formal-benchmark-entry.v1`)
- Example manifest:
  `tools/evals/zuno/rag_eval/configs/formal_benchmark_manifest.example.json`
  (`phase22-formal-benchmark-manifest.v1`)
- Test suite: `tests/evals/test_phase22_formal_benchmark_entry.py` (26 tests)

## Formal Execution Command

```bash
python tools/evals/zuno/rag_eval/run_phase22_formal_benchmark.py \
  --manifest tools/evals/zuno/rag_eval/configs/formal_benchmark_manifest.example.json \
  --output <artifact-dir> \
  [--profile-runtime-factory MODULE:ATTR] \
  [--check-only]
```

Exit codes: `0` READY_FOR_FORMAL_EXECUTION / MEASURED, `1` RUNTIME_OBSERVED,
`2` BLOCKED_NOT_MEASURED, `3` INCOMPARABLE, `4` ERROR. Missing external facts
never crash the command and never fabricate results: they produce
`BLOCKED_NOT_MEASURED` with fixed blocker codes.

## Current Inventory (audited)

| Item | State |
|---|---|
| Four Profile Runners | contract-smoke test doubles + canonical boundary adapters (Standard/Local/Deep/Agentic) via `CanonicalProfileRuntimeFactory`; formal execution adapters not wired |
| Dataset Hash | `public_dataset_registry.yaml` `expected_checksums` (3 public datasets); no jsonl case file declares `reviewer_status` |
| Case Manifest | `configs/benchmark_suite.yaml` `PublicBenchmarkSuiteV1` — `candidate_review_pending` |
| Corpus/Snapshot | `.local/evals/zuno/rag_eval/corpus`; per-profile `corpus_snapshot_ref` declared |
| Model/Judge/Embedding | declared `model_config_ref` / `judge_config_ref` / `embedding_config_ref` (not provisioned) |
| Security Policy | preflight security gate (authorization_ref / security_epoch / formal execution attestation) |
| Runtime Attestation | `phase22-product-runtime-attestation.v1` (hash-bound) — not yet issued for product runtime |
| Credential | `phase22-formal-credential-attestation.v1` — not provisioned |
| Reviewer Approval | `phase22-reviewer-attestation.v1` — `reviewer_approved_count=0`, `benchmark_eligible_count=0` |
| Budget | `phase22-human-budget-attestation.v1`; `release_gate_config.yaml` `pending_coordinator_approval` |
| Artifact Store | declared per profile (`artifact_store_available`); no formal receipt bundle |
| Trace | `ObservabilityTracePort` contract + in-memory prototype |
| RunOutcome | required for agentic profile (MeasurementTruthGate Rule 5) |
| Measurement Gate | `MeasurementTruthGate` 7 rules + `phase22-release-measurement-attestation.v1` |
| Release Decision | `phase22-release-decision-v3` (PASSED/FAILED/BLOCKED/INCOMPARABLE/ERROR) |

## Formal Entry Contract

The entry performs, in order:

1. Manifest Schema validation (`manifest_version`, dataset path, four-profile
   completeness, per-profile config refs) — `MANIFEST_SCHEMA_INVALID`.
2. **Actual** dataset file SHA-256 vs declared `dataset_hash` —
   `DATASET_HASH_MISMATCH`; missing file — `DATASET_UNAVAILABLE`.
3. **Actual** canonical case-id hash vs declared `case_set_hash` —
   `CASE_SET_HASH_MISMATCH`; declared vs actual candidate count —
   `CANDIDATE_COUNT_MISMATCH`.
4. Four-profile configuration completeness — `PROFILE_SET_INCOMPLETE`.
5. Preflight contract v8 (11 gates): Runtime attestation
   (`RUNTIME_ATTESTATION_MISSING`/`INVALID`), Credential
   (`MISSING_FORMAL_CREDENTIAL`), Reviewer
   (`REVIEWER_ATTESTATION_NOT_APPROVED`), Budget
   (`BUDGET_APPROVAL_MISSING`), Security (`SECURITY_APPROVAL_MISSING`),
   Artifact store (`ARTIFACT_STORE_UNAVAILABLE`), plus the fixed preflight
   gap codes as `blocker_details`.
6. Output path validation — `OUTPUT_PATH_UNAVAILABLE`; write-once
   immutability — `OUTPUT_PATH_EXISTS`.
7. Execution of profiles that may run (injected `--profile-runtime-factory`
   or the canonical factory which fails closed with precise dependency gap
   codes when the composition root bundle is absent).
8. Per-profile measurement classification:
   `READY_FOR_FORMAL_EXECUTION` / `BLOCKED_NOT_MEASURED` /
   `RUNTIME_OBSERVED` / `MEASURED` / `INCOMPARABLE` / `ERROR`.
9. Immutable artifacts: `benchmark_report.json`, `profiles/<profile>.json`
   (deterministic facts, `\n` line endings, byte-identical across
   platforms), `profiles/<profile>.measurement-attestation.json`,
   `environment.json` (+ `.sha256`), SHA-256 of every artifact, Git SHA,
   command line, Python/platform environment.

### Per-profile output contract

`profile_id`, `runtime_adapter`, `dataset_version`, `case_set_hash`,
`corpus_snapshot`, `knowledge_snapshot`, `model_config_ref`,
`judge_config_ref`, `embedding_config_ref`, `security_policy_ref`,
`formal_credential_ref`, `reviewer_attestation_ref`, `budget_approval_ref`,
`runtime_attestation_ref`, `output_artifact_path`, `output_artifact_hash`,
`measurement_status`, `blocker_codes`.

### Anti-fabrication rules (enforced by tests)

- Test Double results can never be `MEASURED` (`TEST_DOUBLE_NOT_MEASURED`).
- `RUNTIME_OBSERVED` never auto-promotes to `MEASURED`.
- `MEASURED` requires a serialized Measurement Attestation bound to
  profile / artifact hash / fingerprint hash; missing → `MEASUREMENT_ATTESTATION_MISSING`,
  forged/mismatched → `MEASUREMENT_ATTESTATION_INVALID`.
- One blocked profile never fakes the other profiles' status.
- Single-profile `MEASURED` never makes the run `MEASURED`.
- Four profiles `MEASURED` but incomparable → overall `INCOMPARABLE`.
- Preflight `INCOMPARABLE` (cross-profile disagreement) short-circuits to
  `INCOMPARABLE` before execution.
- Declared environment variables / booleans are never credentials: formal
  credential attestation must be serialized and hash-verified.

## Actual Run (this environment)

```text
command: python tools/evals/zuno/rag_eval/run_phase22_formal_benchmark.py \
  --manifest tools/evals/zuno/rag_eval/configs/formal_benchmark_manifest.example.json \
  --output .local/evals/zuno/rag_eval/runs/formal-benchmark-readiness-final
exit code: 2 (BLOCKED_NOT_MEASURED — documented, not a crash)
overall_status: BLOCKED_NOT_MEASURED
preflight: BLOCKED [reviewer_not_approved, benchmark_not_eligible, reviewer_attestation_missing]
per-profile: standard_rag / local_graphrag / deep_graphrag / agentic_graphrag
  -> BLOCKED_NOT_MEASURED [REVIEWER_ATTESTATION_NOT_APPROVED]
```

Honest blockers for the current repository state: reviewer attestation not
approved (`reviewer_approved_count=0`), no formal credential attestation,
no product runtime attestation — exactly matching the audit of
`production-readiness.md` and the completion-blocker evidence.

## Tests

`tests/evals/test_phase22_formal_benchmark_entry.py` (26, all passing):

1. Manifest schema invalid → ERROR
2. Profile entry field missing → ERROR
3. Four-profile set incomplete → ERROR
4. Dataset hash mismatch (actual file) → DATASET_HASH_MISMATCH
5. Dataset file missing → DATASET_UNAVAILABLE
6. Case set hash mismatch (actual rows) → CASE_SET_HASH_MISMATCH
7. Candidate count mismatch → CANDIDATE_COUNT_MISMATCH
8. Runtime attestation forged → RUNTIME_ATTESTATION_INVALID
9. Credential attestation forged → MISSING_FORMAL_CREDENTIAL
10. Reviewer not approved → REVIEWER_ATTESTATION_NOT_APPROVED
11. Budget not approved → BUDGET_APPROVAL_MISSING
12. Security not approved → SECURITY_APPROVAL_MISSING
13. Artifact hashes present and equal to file bytes
14. Git SHA present in environment
15. Environment manifest present
16. Rerun reproducibility (two runs → identical artifact hashes + checksum)
17. One blocked profile does not fake the others
18. Test double can never be MEASURED
19. RUNTIME_OBSERVED never auto-promotes
20. Single MEASURED profile → not overall MEASURED (+ attestation gate)
21. Four MEASURED but incomparable → INCOMPARABLE
22. Measurement attestation missing → BLOCKED
23. Measurement attestation forged → BLOCKED
24. Formal fixture happy path → four MEASURED + immutable artifacts +
    attestation files
25. Output write-once immutability → OUTPUT_PATH_EXISTS
26. --check-only → READY_FOR_FORMAL_EXECUTION

Regression: `tests/evals/` 573 passed; the 10 pre-existing failures
(`test_rag_eval_metrics.py`, `test_agentic_graphrag_*`) fail identically on
the clean base (confirmed via stash).

## Blockers (machine-readable, current repo state)

`REVIEWER_ATTESTATION_NOT_APPROVED` (reviewer_status=pending,
`reviewer_approved_count=0`), `MISSING_FORMAL_CREDENTIAL` (no formal
credential attestation), `RUNTIME_ATTESTATION_MISSING` (no product runtime
attestation), `CORPUS_SNAPSHOT_UNAVAILABLE` (no formal corpus snapshot
binding), `BUDGET_APPROVAL_MISSING` / `SECURITY_APPROVAL_MISSING`
(coordinator approval pending), `ARTIFACT_STORE_UNAVAILABLE`.

## Declarations

不声明 `PHASE22_COMPLETED` / `PRODUCTION_READY` / `BENCHMARK_PASSED`。
无 Actual Measurement；无 Release Decision PASSED。四 Profile 正式执行
适配器与外部正式事实（credential / reviewer-approved case set / product
runtime attestation / budget / security approval）仍未提供；本 slice 只把
"blocked" 变成可复现、可校验、机器可读的正式执行契约。
