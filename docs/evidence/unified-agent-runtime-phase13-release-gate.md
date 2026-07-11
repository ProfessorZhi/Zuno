# Unified Agent Runtime PHASE13 Release Gate Evidence

date: 2026-07-11
program: zuno-unified-agent-runtime-closure-v1
status: implementation_complete_measurement_blocked

## Measured Status

PHASE13 did not produce a fixed EnterpriseRAG measured pass.

```text
implementation available
measurement blocked
quality not yet proven
```

## Sample-8 Run

Command:

```powershell
python tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py --questions-file tools/evals/zuno/rag_eval/datasets/mixed_realistic_v1_eval.jsonl --output-root .local/evals/zuno/phase13/sample8 --sample-size 8 --allow-blocked --no-spawn-dev-embedding-server
```

Result:

```json
{
  "status": "blocked",
  "metrics_source": "blocked_not_measured",
  "output_root": ".local\\evals\\zuno\\phase13\\sample8"
}
```

Metrics summary:

```text
status=blocked
measurement_status=blocked_not_measured
selected_case_count=8
measured_case_count=0
blocked_reason=profile_runner_unavailable
profile_runner_error=local embedding model name and base url are required
release_gate.status=blocked_not_measured
release_gate.measured=false
```

## Sample-80 Status

`sample_80` remains blocked by the PHASE01 baseline manifest because the repository does not contain a tracked fixed 80-case EnterpriseRAG set.

```text
blocked_reason=no_tracked_fixed_80_case_enterprise_rag_set_available_in_repo; local .local runs are not committed truth source
```

## Runner Semantics Fixed

PHASE13 changed the paired benchmark runner so partial profile output cannot be promoted to measured fixed benchmark status:

- `standard_rag`, `deep_graphrag`, and `agentic_graphrag` are required profiles.
- Every required profile must write the same expected case set.
- `profile_completeness` records case counts and case-id hashes by profile.
- Missing or incomplete profiles produce `blocked_not_measured`.
- Provider/runtime configuration failures write blocked reports when `allow_blocked=True`.

This evidence does not prove Agentic GraphRAG quality superiority. It proves the release gate no longer fakes measured status when benchmark prerequisites are missing.
