# Phase 05: Dynamic Context And Capability Selection

## Goal

Inject only task-relevant memories, skills, tool schemas, MCP tools, and
knowledge evidence into each model call.

## Dependency

Phases 01 through 04 complete.

## Scope

- Create or harden a Capability Registry.
- Rank capabilities by task relevance, permission, cost, schema size, and
  health.
- Select knowledge tools, action tools, MCP tools, and skills separately.
- Record selection and eviction reasons in `ContextTrace`.

## Files To Change

- capability registry/selection modules
- context orchestration modules
- Agent runtime tests

## Files Not To Change

- individual tool implementations unless a schema is invalid
- skill content unless needed for routing
- GraphRAG query internals

## Acceptance Gates

- The model window does not receive every registered capability.
- Skills remain guidance packages, not tools or business services.
- MCP remains a connector protocol, not a business capability category.
- Trace shows selected and rejected capabilities.

## Verification Commands

```powershell
pytest -q tests
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- capability metadata fields
- selection trace example
- tests proving irrelevant schemas are excluded
