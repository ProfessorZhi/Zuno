# Phase 04: Long-term Memory Stores

## Goal

Consolidate long-term memory into governed semantic, episodic, and procedural
stores.

## Dependency

Phase 03 complete.

## Scope

- Define semantic, episodic, and procedural memory types.
- Add user, agent, project, thread, and workspace scopes.
- Add dedupe, conflict resolution, confidence, TTL, provenance, and privacy
  deletion semantics.
- Retrieve long-term memory selectively for current context assembly.

## Files To Change

- `src/backend/zuno/services/memory/`
- backend memory tests
- eval fixtures for memory retrieval

## Files Not To Change

- knowledge corpus indexing
- GraphRAG project settings
- frontend UI unless scoped explicitly

## Acceptance Gates

- Long-term memory is not treated as RAG/GraphRAG knowledge.
- Memory candidates are not promoted without provenance and confidence.
- Privacy deletion removes or masks retrievable memory according to policy.
- Retrieval respects scope and permission.

## Verification Commands

```powershell
pytest -q tests
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- memory type schema
- scope rules
- tests for dedupe, conflict, TTL, and privacy deletion
