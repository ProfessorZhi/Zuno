# Phase 06: GraphRAG Snapshot Query Boundary

## Goal

Separate Agent Context from GraphRAG query configuration by introducing
`GraphRAGProjectSnapshot` as immutable query input.

## Current Status

Not complete for this program. `GraphRAGProjectSnapshot` and
`GraphRAGQueryService` have partially landed in the cleanup program, but this
phase still depends on Context/Memory phases and must reuse the existing query
runtime instead of creating a second one.

## Dependency

Phase 05 complete and the current GraphRAG cleanup program no longer blocks
GraphRAG contract work.

## Scope

- Rename or replace misleading `GraphRAGRuntimeContext` concepts.
- Build `GraphRAGProjectSnapshot` from project id, settings, prompts, versions,
  readiness, and storage handles.
- Pass the snapshot into `GraphRAGQueryService.query(...)`.
- Return Knowledge Evidence to the Agent rather than mutating Agent Context.

## Files To Change

- GraphRAG project/query contract modules
- retrieval/knowledge service adapters
- backend tests and trace fixtures

## Files Not To Change

- long-term memory storage
- frontend UI unless API fields change
- Domain Pack compatibility surfaces outside the approved cleanup phase

## Acceptance Gates

- `Agent Context`, `GraphRAGProjectSnapshot`, and `Knowledge Evidence` are
  separate types.
- Snapshot includes project id, settings, prompts, versions, readiness, and
  storage handles or references.
- Query trace records requested/resolved method and snapshot version metadata.

## Verification Commands

```powershell
pytest -q tests
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- snapshot schema
- query service signature
- test proving snapshot immutability for a query
