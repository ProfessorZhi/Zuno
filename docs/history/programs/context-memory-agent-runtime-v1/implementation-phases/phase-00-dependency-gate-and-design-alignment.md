# Phase 00: Dependency Gate And Design Alignment

## Goal

Prove whether Context Memory Agent Runtime V1 can begin as implementation work
or must remain design-only until `official-graphrag-cleanup-v1` Phase 11C and
Phase 12 are closed.

## Current Status

Blocked for implementation until 11C/12 closure or fresh dependency
re-verification.

## Scope

- Check current branch, current program status, and runtime legacy references.
- Confirm whether Domain Pack and `DomainQAGraph` are still active.
- Confirm whether `MultiAgentSupervisorGraph` and `tests/compat/` still block
  cleanup.
- Update this program status only from evidence.

## Files To Change

- `.agent/programs/context-memory-agent-runtime-v1/implementation-plan.md`
- `.agent/programs/context-memory-agent-runtime-v1/implementation-phases/README.md`
- optional phase evidence note under this program

## Files Not To Change

- runtime source files
- frontend source files
- tests, unless the phase only adds a read-only status verifier

## Acceptance Gates

- Evidence says whether implementation can start or is blocked by legacy runtime.
- No destructive runtime changes are made.
- Any blocker names the exact active import, route, launcher, or test surface.

## Verification Commands

```powershell
git status --short
rg -n "DomainQAGraph|domain_pack|domain-pack|domain packs|domain packs" src apps tests tools .agent docs
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Evidence To Return

- current branch and dirty status
- legacy reference count by major area
- pass/fail output for verification commands
