# Closure Checklist

Use this checklist before closing a future `zuno-target-runtime-v2` phase.

## Scope

- Confirm the phase does not require Java services, microservices, event
  workers, database schema changes, dependency upgrades, full frontend
  migration, or eval baseline updates unless that phase explicitly authorizes
  them.
- Confirm Target behavior is not written as Current without code and tests.
- Confirm Domain Pack, `DomainQAGraph`, `MultiAgentSupervisorGraph`, and
  `AgentRuntime` are not restored.

## Required Checks

```powershell
git status --short
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
```

Add focused runtime or eval tests for phases that change runtime or eval code.

## Evidence

Record phase evidence in the active program while a phase is open. When a phase
is closed and superseded by a slimmer program surface, move detailed evidence
to:

```text
docs/architecture/history/programs/zuno-target-runtime-v2/
```
