# Phase 07: GeneralAgent Runtime Integration

## Goal

Move the front-path conversation runtime to one `GeneralAgent` loop.

## Dependency

Phases 02 through 06 complete. Legacy runtime deletion must be authorized by
the active cleanup program evidence.

## Scope

- Route chat execution through `GeneralAgent`.
- Use Context Orchestrator before model calls.
- Use Post-turn Pipeline after model/tool turns.
- Call knowledge, action, MCP, and skill-selected capabilities through one
  capability boundary.
- Remove or retire parallel conversational runtimes only when evidence proves
  they are unused.

## Files To Change

- backend Agent/runtime modules
- API service orchestration
- integration tests
- launchers or frontend contracts only if the runtime boundary changes

## Files Not To Change

- Java, microservices, event workers, or default multi-agent surfaces
- unrelated frontend design

## Acceptance Gates

- One front-path conversation loop handles model calls and tool calls.
- Parallel chat runtimes are removed or marked migration-only with proof.
- Post-turn persistence runs after user/model/tool activity.
- Streaming, interrupts, permissions, and trace behavior remain covered.

## Verification Commands

```powershell
pytest -q tests
npm run frontend:lint
npm run frontend:build
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- runtime call chain
- integration test names
- before/after legacy reference evidence
