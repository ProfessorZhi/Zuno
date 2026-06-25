# Phase 07: Capability System

## Goal

Create a capability boundary for tools, MCP connectors, skills, and knowledge
access.

## Dependency

Phase 05 and Phase 06 complete.

## Scope

- Define capability metadata: name, type, permissions, schema, cost, and health.
- Add a selector that chooses relevant tools, MCP tools, skills, memories, and
  knowledge evidence for a model call.
- Ensure not every capability is loaded every turn.

## Files To Change

- capability registry/selector modules under `src/backend/zuno/`
- Agent tool setup tests
- `.agent/references/runtime-call-chain.md`

## Files Not To Change

- Product-level multi-agent mode.
- External MCP implementations.
- Frontend visual UI unless API contracts change.

## Acceptance Gates

- Capabilities are selected from task context and permissions.
- Selection emits trace evidence.
- Tools and knowledge remain capabilities, not parallel conversational agents.

## Verification Commands

```powershell
pytest -q tests/test_capability_system.py
pytest -q tests/test_phase11b_single_generalagent_cutover.py
git diff --check
```

## Evidence To Return

- registry schema
- selector trace example
- focused tests
