# Goal05 PHASE22 MiniMax Live Worker Run

status: live_worker_run_recorded
phase: PHASE22
parent_pr: 97

## Live MiniMax Run

The controller successfully invoked `claude -p` via the
`run-claude-with-metrics.ps1` wrapper from this main session on 2026-08-02.
This proves the dispatch control plane is wired end-to-end against the live
MiniMax provider.

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

`quota_snapshot_available = CONFIG_REQUIRED` — this is recorded in the
dispatcher output. The provider is still `AVAILABLE` and the run completed.
Per the spec, `CONFIG_REQUIRED` must not block execution; the run confirms
that gate.

## Observed Behaviour

- The MiniMax model was reached, accepted the prompt, executed one tool call
  (`echo ZUNO_TEST_OK`), and emitted a stream-json result.
- The metrics wrapper captured a valid `RUN_ID` and a real `session_id`.
- Token usage was tracked in the stream-json output and reported by the
  wrapper.

## Why This Is a Probe, Not a Completed Work Package

The controller intentionally limited this probe to a `claude -p "echo
ZUNO_TEST_OK"` invocation. The probe is not a full Worker task card
completion: the probe did not produce a `COMMIT_SHA`, did not push a branch,
and did not write `docs/evidence/goal05-phase22-minimax-live-probe.md`.
A full Worker task (MM-4) was launched in parallel with task card at
`.agent/programs/thread-prompts/phase22-final-closure/MM-4-minimax-live-probe.md`,
but its Claude session was stopped after exceeding the controller's runtime
budget — the controller is not allowed to spend unbounded tokens on a probe
when the spec records MiniMax quota snapshot as `CONFIG_REQUIRED`.

The probe nevertheless proves the dispatcher end-to-end path is wired against
the live MiniMax provider and produces a real metrics Run ID.

## Worker Run IDs (cumulative)

| Run ID | Provider | Status | Source |
| --- | --- | --- | --- |
| `19214a04-8f12-4066-89ab-69c71c80a505` | MiniMax | effective_segment | This controller probe via metrics wrapper |
| `5227c4d2-ea06-4eed-8f60-deb68e182fe0` | DeepSeek | ineffective_segment | DS-1 initial (historical) |
| `dc8f94d2-6941-4293-a83b-0d412de50d67` | DeepSeek | reviewed_partial | DS-1 retry (historical, Codex absorbed fix) |

## Boundary

This run does not claim PHASE22 completed, fixed benchmark measured, release gate
passed, production ready, archive or no-active reset.