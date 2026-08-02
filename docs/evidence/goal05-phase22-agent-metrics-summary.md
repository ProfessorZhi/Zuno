# Goal05 PHASE22 Agent Metrics Summary

status: partial_pr97_metrics_available
phase: PHASE22
parent_pr: 97
metrics_json: `docs/evidence/goal05-phase22-agent-metrics.json`

## Scope

This file summarizes the machine-collected PR #97 worker metrics. It does not estimate tokens, cost or quota from provider percentages. It does not claim PHASE22 completed, benchmark measured, release passed or production ready.

## Tool Path

- Objective metrics path: `F:\funny_project\agent-metrics-collector`
- Actual available metrics root: `F:\funny_project\agent-metrics-workspace\agent-metrics-collector`

The objective path was not present on this machine. Controller used the actual available metrics root for read-only doctor, snapshot, wrapper execution and PR aggregate export.

## Provider Status

- DeepSeek: AVAILABLE in preflight snapshot.
- MiniMax: CONFIG_REQUIRED in preflight snapshot; MM-1, MM-2 and MM-3 were not launched.
- Codex quota: PARTIAL from cockpit app data.
- controller_token_status: NOT_AVAILABLE_APP_SESSION.

## Worker Runs

| Worker | Run ID | Provider | Status | Notes |
| --- | --- | --- | --- | --- |
| DS-1 | `5227c4d2-ea06-4eed-8f60-deb68e182fe0` | DeepSeek | ineffective_segment | Prompt delivery issue; worker received only the heading and made no changes. |
| DS-1 retry1 | `dc8f94d2-6941-4293-a83b-0d412de50d67` | DeepSeek | reviewed_partial | Worker identified a valid measurement gate blank-reference gap but left an uncommitted change and did not create a child PR. Codex absorbed the valid semantic fix with tests. |

The aggregate also reported one unreadable run excluded from metrics:

- `e6804fbd-fb2f-4e1f-9ded-ff5cd12caa4f`: `integrity_or_schema_error`.

## Aggregated Usage From Metrics

Values below are copied from the metrics aggregate and are not manually estimated.

- input_tokens: 143314
- output_tokens: 31205
- reasoning_tokens: 0
- cache_read_tokens: 3684224
- cache_write_tokens: 0
- total_tokens: 174519
- pricing_status: UNVERIFIED
- actual_billed_cost_usd: null

## Boundary

This summary is an interim PR #97 metrics snapshot. Final PHASE22 reporting still requires reviewer-approved case set, formal four-profile benchmark, final verification, Release Decision, Production Readiness truth and, only after gates pass, Program archive/no-active preparation.

