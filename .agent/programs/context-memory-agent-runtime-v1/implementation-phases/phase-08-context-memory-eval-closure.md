# Phase 08: Context Memory Eval Closure

## Goal

Prove the context and memory architecture works with behavior evidence, not
only static types.

## Dependency

Phase 07 complete.

## Scope

- Add evals for recall, false memory rate, summary faithfulness, context token
  cost, cross-session consistency, privacy deletion, and tool-result
  compression completeness.
- Capture context traces and memory update traces.
- Add regression gates for budget eviction and source-event provenance.

## Files To Change

- eval tools under `tools/evals/zuno/`
- backend tests and fixtures
- Agent verification scripts if a durable gate is needed

## Files Not To Change

- core runtime behavior without a failing eval or test
- public docs unless the implementation is actually verified

## Acceptance Gates

- Evals report recall and false-memory behavior.
- Summary faithfulness is checked against source events.
- Privacy deletion is tested.
- Tool-result compression keeps errors, permission results, paths, hashes, and
  evidence pointers.
- Token cost is measured from trace data.

## Verification Commands

```powershell
pytest -q tests
python tools/evals/zuno/run_context_memory_eval.py
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- eval command output
- context trace sample
- memory trace sample
- residual risk list
