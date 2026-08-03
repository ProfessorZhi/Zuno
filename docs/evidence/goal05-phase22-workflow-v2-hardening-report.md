# PHASE22 Workflow V2 Hardening Report

## Summary

This report records the PHASE22 Multi-Agent Workflow V2 hardening slice. It
does not close PHASE22, does not claim production readiness, and does not mark
the fixed benchmark as measured.

## Git Baseline

```text
origin/main_sha=c9d099d64a1af28102231751ce55df8217173e89
controller_start_head=8a5f4b186d112111527c4347f936a43e77920491
controller_branch=codex/phase22-canonical-closure-codex-gpt5-controller-001
pr=104
pr_base=main
base_drift=none
```

## Worker Resume Segments

| worker | model | session_id | resume segment status | commit | decision |
| --- | --- | --- | --- | --- | --- |
| CC-MM-1 | claude-minimax | `be9c0934-546c-452a-9231-a650fe5997a0` | `error_max_turns`; worker produced candidate code but stopped before autonomous commit/handoff; Codex amended Enum/direction root cause and committed worker branch | `410d439e224d13d8d5e10765fe389894bf98649a5` | `CONTROLLER_RECOVERED_PARTIAL` |
| CC-DS-1 | claude-deepseek | `b2624440-d104-4b55-aa64-b92712d844cf` | `error_max_budget_usd`; worker produced candidate code/tests but stopped before autonomous evidence/commit; Codex added evidence and committed worker branch | `4e01675311194eb2ac10a155442f560026450533` | `CONTROLLER_RECOVERED_PARTIAL` |

Both commits were created after Controller recovery and pushed to their isolated
worker branches, then selectively absorbed with
`git restore --source=<worker_sha> -- <exact paths>`. No worker branch was
merged as a whole. Session resume and code production are verified; autonomous
worker resume-to-commit/handoff remains unproven and is not claimed here.

## Accepted Paths

CC-MM-1:

```text
tools/evals/zuno/synthetic_benchmark/**
tests/evals/synthetic_benchmark/**
docs/evidence/goal05-phase22-worker-cc-mm-1-derivation-spec.md
```

CC-DS-1:

```text
tools/scripts/phase22_canonical_ingestion_preflight.py
tests/repo/test_phase22_canonical_ingestion_preflight.py
docs/evidence/goal05-phase22-worker-cc-ds-1-canonical-ingestion-preflight.md
```

Controller-owned integration:

```text
tools/scripts/phase22_execution_candidate_gate.py
tests/repo/test_phase22_execution_candidate_gate.py
```

## Worker Review Scores

### CC-MM-1

```text
identity and traceability: 8/10
scope containment: 15/15
requirement fit and correctness: 18/20
tests and reproducibility: 14/15
evidence honesty: 9/10
security / approval / audit: 15/15
cost and time efficiency: 3/5
integration risk: 8/10
total=90/100
decision=CONTROLLER_RECOVERED_PARTIAL
```

Review notes:

- Allowed paths only.
- Focused tests cover three cases, wrong direction, wrong temporal expectation,
  SourceSpan support and reproducible hash.
- Worker stopped at `max_turns`; Codex fixed the root cause where
  `@dataclass(frozen=True)` on `RelationDirection` broke Enum equality and made
  `OUTGOING == INCOMING` true.
- The package is candidate-only and makes no measured benchmark claim.

### CC-DS-1

```text
identity and traceability: 8/10
scope containment: 15/15
requirement fit and correctness: 18/20
tests and reproducibility: 15/15
evidence honesty: 10/10
security / approval / audit: 15/15
cost and time efficiency: 3/5
integration risk: 8/10
total=92/100
decision=CONTROLLER_RECOVERED_PARTIAL
```

Review notes:

- Allowed paths only.
- Tool is read-only: AST parsing, no imports of production runtime, no TCP
  readiness check, no writes, no receipts.
- Real repository verdict is based on explicit composition binding, not
  `*ObjectStore` class-name counting.
- Worker stopped at budget exhaustion before evidence/commit; Codex added
  evidence and committed the worker branch.

## Dependency Integration

Controller added `phase22_execution_candidate_gate.py`.

Canonical contract:

```text
derivation_pack_status=legal|invalid
canonical_ingestion_preflight_status=READY_FOR_CANONICAL_INGESTION|BLOCKED_WITH_EXACT_GAP
status=execution_candidate|blocked_with_exact_gap
dependency_status=DEPENDENCY_COMPATIBLE|DEPENDENCY_REWORKED_BY_CODEX|DEPENDENCY_BLOCKED
```

Rule:

```text
Derivation Pack legal AND Canonical Ingestion Preflight READY
  -> execution_candidate

Any derivation failure OR any preflight gap
  -> blocked_with_exact_gap
```

The gate normalizes Worker B's `verdict` field into the single Controller field
`canonical_ingestion_preflight_status`. It does not keep two permanent status
paths.

Current real-tree result:

```text
derivation_pack_status=legal
canonical_ingestion_preflight_status=READY_FOR_CANONICAL_INGESTION
dependency_status=DEPENDENCY_COMPATIBLE
status=execution_candidate
```

Dependency conclusion:

```text
DEPENDENCY_COMPATIBLE
```

## Cost Ledger

Scope: current resume segments only. Old Wave 1 values in
`goal05-phase22-controller-integration-report.md` remain historical and are not
summed into this handoff. Controller app-session tokens are not available from
the Codex desktop runtime.

| worker | session_id | segment_index | resume_of_session_id | run_started_at | run_ended_at | duration_ms_current_segment | duration_api_ms_current_segment | input_tokens_current_segment | cache_read_input_tokens_current_segment | cache_creation_input_tokens_current_segment | output_tokens_current_segment | total_cost_usd_current_segment | metrics_source | cost_scope | provider_quota_basis |
| --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| CC-MM-1 | `be9c0934-546c-452a-9231-a650fe5997a0` | 2 | `be9c0934-546c-452a-9231-a650fe5997a0` | 2026-08-03T13:37:07.2741482+08:00 | 2026-08-03T13:41:24.2606018+08:00 | 253203 | 228621 | 50230 | 774656 | 0 | 12026 | 0.939128 | stream-json final result | single-agent-pr-handoff | unknown |
| CC-DS-1 | `b2624440-d104-4b55-aa64-b92712d844cf` | 2 | `b2624440-d104-4b55-aa64-b92712d844cf` | 2026-08-03T13:37:07.2936955+08:00 | 2026-08-03T13:40:57.7941631+08:00 | 227226 | 190919 | 11944 | 1129472 | 0 | 23682 | 1.296542 | stream-json final result | single-agent-pr-handoff | unknown |
| Controller | `NOT_AVAILABLE_APP_SESSION` | current | n/a | 2026-08-03T13:34:26.0057639+08:00 | `pending_final_get_date` | `NOT_AVAILABLE_APP_SESSION` | `NOT_AVAILABLE_APP_SESSION` | `NOT_AVAILABLE_APP_SESSION` | `NOT_AVAILABLE_APP_SESSION` | `NOT_AVAILABLE_APP_SESSION` | `NOT_AVAILABLE_APP_SESSION` | `NOT_AVAILABLE_APP_SESSION` | Codex desktop app does not expose precise per-session usage | controller-pr-integration | unknown |

Excluded from current handoff totals:

```text
CC-MM-1 Wave 1 cost 0.225254 = historical, not counted
CC-DS-1 Wave 1 cost 0.377357 = historical, not counted
CC-MM-2 Wave 1 cost 0.666285 = historical, not counted
Any aggregate ChatGPT/Codex conversation token total = NOT_AVAILABLE_APP_SESSION
Any provider backend quota deduction = unknown
```

Current resume worker API estimated total:

```text
0.939128 + 1.296542 = 2.235670
```

No field with ambiguous current-vs-cumulative meaning was counted. If a future
log field cannot be proven to be current-segment only, record it as
`AMBIGUOUS_NOT_COUNTED`.

## Validation

Focused validation:

```powershell
python -c "import os, sys; sys.path.insert(0, os.getcwd()); import pytest; raise SystemExit(pytest.main(['tests/evals/synthetic_benchmark/test_derivation_spec.py','tests/repo/test_phase22_canonical_ingestion_preflight.py','tests/repo/test_phase22_execution_candidate_gate.py','-q']))"
python tools/scripts/phase22_execution_candidate_gate.py
git diff --check
```

Expected note: `phase22_execution_candidate_gate.py` exits `1` only when the
current preflight has an exact unresolved gap. After the object-store preflight
correction, the real tree exits `0` with `execution_candidate`.

Broader validation is recorded in the PR body after final run.

## State Boundary

```text
PHASE22=in_progress
fixed_benchmark=blocked_not_measured
production_readiness=not_established
program_archive=not_allowed
merge=not_approved
```
