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

- Complete. Capabilities are selected from task context, allowed types, health,
  and optional permission scopes.
- Complete. Selection emits `CapabilitySelectionTrace` with selected names,
  dropped names, reasons, and scores.
- Complete. Tools, MCP entries, skills, and knowledge are capability records,
  not parallel conversational agents.
- Deferred to Phase 08. `GeneralAgent` runtime integration will inject selected
  capabilities into the single agent loop.

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

## Closure Evidence

- Registry schema:
  `CapabilityRecord(name, type, description, schema, permissions, cost, health, source, owner)`.
- Capability types:
  `Knowledge`, `ActionTool`, `MCPTool`, `MCPResource`, `MCPPrompt`, `Skill`.
- Selector:
  `DynamicCapabilitySelector.select(CapabilitySelectionRequest)` returns a
  bounded `CapabilitySelectionResult`, not the full registry.
- Compatibility:
  `CapabilityRegistryService.search()` still returns existing API keys such as
  `kind`, `status`, `display_name`, and `invoke_ref`, and now also returns
  unified metadata fields.
- Focused tests:
  `python -m pytest -q tests/test_capability_system.py tests/test_capability_registry.py`
  passed.
