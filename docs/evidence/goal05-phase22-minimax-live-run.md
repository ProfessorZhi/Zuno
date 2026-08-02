# Goal05 PHASE22 MiniMax Provider Wrapper Smoke

status: provider_wrapper_smoke_observed
phase: PHASE22
parent_pr: 97
source_sha_at_generation: 6a3400688507d2d2d393ec7066557af681a7cf43

## What This Evidence Records

This file records a **provider wrapper smoke**: the controller invoked the
`run-claude-with-metrics.ps1` wrapper directly from the main session, with
a tiny `claude -p "echo ZUNO_TEST_OK"` payload, and the metrics wrapper
returned a real `RUN_ID`, a real `session_id`, and a real
`api_equivalent_cost`.

It is **not** evidence of a complete live Worker E2E. A full Worker E2E
would require:

- A real Worker task card accepted by the dispatcher
- The full dispatcher flow (Worktree gates, schema validation, lock,
  worker completion, COMPLETION_CANDIDATE gate)
- A Worker Result that satisfies the Worker Result schema
- A controller review of Diff / Branch / Forbidden Paths
- Promotion to COMPLETED with explicit attribution

None of these steps completed in this session. The MM-4 task card was
launched but its Claude session was stopped after exceeding the
controller's runtime budget.

## Captured Run Metadata

```text
provider        : MiniMax
launcher        : claude  (claude-minimax unavailable → fallback per spec)
metrics_runner  : F:/funny_project/agent-metrics-workspace/agent-metrics-collector/scripts/run-claude-with-metrics.ps1
run_id          : 19214a04-8f12-4066-89ab-69c71c80a505
session_id      : e7e0beae-e2d0-420a-a791-4d82694d6a84
model           : MiniMax-M3
claude_version  : 2.1.220
```

## Quota Snapshot

`quota_snapshot_available = CONFIG_REQUIRED` — recorded in the dispatcher
output. The provider is still `AVAILABLE` and the run completed. Per the
spec, `CONFIG_REQUIRED` must not block execution; the run confirms that
gate. Note: with the new dispatcher contract, the default is
`NOT_QUERIED`; this observation was recorded before the contract change.

## Observed Behaviour

- The MiniMax model was reached, accepted the prompt, executed one tool
  call (`echo ZUNO_TEST_OK`), and emitted a stream-json result.
- The metrics wrapper captured a valid `RUN_ID` and a real `session_id`.
- Token usage was tracked in the stream-json output and reported by the
  wrapper.

## Why This Is a Smoke, Not a Live Worker E2E

The controller intentionally limited this run to a `claude -p "echo
ZUNO_TEST_OK"` invocation. The run did not:

- Use the full `dispatch_claude_worker.ps1` flow
- Validate the Worker Result against the schema
- Reach `COMPLETION_CANDIDATE`
- Receive a controller review

A full Worker task (MM-4) was launched in parallel with task card at
`.agent/programs/thread-prompts/phase22-final-closure/MM-4-minimax-live-probe.md`,
but its Claude session was stopped after exceeding the controller's
runtime budget — the controller is not allowed to spend unbounded
tokens on a probe when the spec records MiniMax quota snapshot as
`CONFIG_REQUIRED`.

## Worker Run IDs (cumulative)

| Run ID | Provider | Status | Source |
| --- | --- | --- | --- |
| `19214a04-8f12-4066-89ab-69c71c80a505` | MiniMax | provider_wrapper_smoke_observed | This controller smoke via metrics wrapper |
| `5227c4d2-ea06-4eed-8f60-deb68e182fe0` | DeepSeek | ineffective_segment | DS-1 initial (historical) |
| `dc8f94d2-6941-4293-a83b-0d412de50d67` | DeepSeek | reviewed_partial | DS-1 retry (historical, Codex absorbed fix) |

## Boundary

This evidence does not claim PHASE22 completed, fixed benchmark measured,
release gate passed, production ready, archive or no-active reset.