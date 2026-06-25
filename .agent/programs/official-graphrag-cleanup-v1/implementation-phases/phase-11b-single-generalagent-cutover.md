# Phase 11B: Single GeneralAgent Cutover

## Goal

Route knowledge-backed conversations through the single `GeneralAgent` loop,
with knowledge access exposed as a tool.

## Dependency

Phase 11A must pass first.

## Scope

- Replace `retrival_knowledge` with `search_knowledge_base`.
- Make the knowledge tool call the Phase 11A `KnowledgeQueryService`.
- Remove top-level `DomainQAGraph` hard handoff from `GeneralAgent.astream()`.
- Remove active `MultiAgentSupervisorGraph` use from the current chat runtime.

## Non-goals

- Deleting legacy source files.
- Rewriting memory, checkpointer, or context orchestration.
- Adding product-level multi-agent mode.

## Acceptance Criteria

- `GeneralAgent.astream()` has one current chat path.
- GraphRAG Project binding does not bypass normal tools, MCP, or skills.
- Knowledge tool returns readable content plus evidence/citation/trace metadata.
- Domain QA no longer owns an entire conversation turn.

## Verification Commands

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py
pytest -q tests/test_phase11b_single_generalagent_cutover.py
pytest -q tests/test_phase5_general_agent_real_runtime_flow.py
git diff --check
```

## Evidence Package Required

- single Agent loop test output
- tool-call path proof
- streaming/history/memory non-regression evidence
- commit hash and push result
