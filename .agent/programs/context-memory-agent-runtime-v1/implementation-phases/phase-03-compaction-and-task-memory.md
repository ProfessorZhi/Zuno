# Phase 03: Compaction And Task Memory

## Goal

Add structured task summaries and compaction without deleting or mutating raw
events.

## Dependency

Phase 02 complete.

## Scope

- Summarize older continuous messages into goal, facts, decisions, constraints,
  TODOs, artifact refs, and open questions.
- Store `source_event_ids` for every summary.
- Compress large tool results into artifacts plus concise window references.
- Trigger compaction by token thresholds.

## Files To Change

- context compaction modules
- task summary persistence modules
- tool-result artifact/reference modules
- compaction tests

## Files Not To Change

- long-term memory store promotion
- GraphRAG query service behavior

## Acceptance Gates

- Summaries never replace raw events as source truth.
- Tool result compression preserves errors, permission decisions, paths, hashes,
  and evidence pointers.
- Budget pressure evicts low-priority context before explicit constraints or
  key decisions.

## Verification Commands

```powershell
pytest -q tests
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- summary schema
- example source event pointer
- compaction trace sample
