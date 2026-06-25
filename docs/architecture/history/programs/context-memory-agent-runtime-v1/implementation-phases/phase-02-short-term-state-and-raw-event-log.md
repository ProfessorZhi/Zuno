# Phase 02: Short-term State And Raw Event Log

## Goal

Make raw events the durable source of truth and keep short-term thread state
recoverable through checkpoints.

## Dependency

Phase 01 complete.

## Scope

- Normalize thread/session ids.
- Append user messages, model messages, tool calls, tool results, interrupts,
  and memory updates to a raw event log.
- Save LangGraph checkpoint state for short-term recovery.
- Inject only a recent coherent message window into `ModelContextPacket`.

## Files To Change

- backend event/checkpoint persistence modules
- backend Agent/runtime services
- persistence tests

## Files Not To Change

- long-term memory promotion logic
- summary compaction logic beyond placeholder contracts
- frontend memory management UI

## Acceptance Gates

- Raw events are append-only.
- Tool call/result groups are not split in the recent window.
- Checkpoint recovery does not depend on summaries.
- Tests prove event ids are stable and traceable.

## Verification Commands

```powershell
pytest -q tests
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- event schema
- checkpoint path or storage adapter
- test proving coherent recent-window selection
