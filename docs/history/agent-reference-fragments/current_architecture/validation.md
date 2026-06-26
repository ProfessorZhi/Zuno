# Validation

## Required Workflow Check

```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## Optional Docs Checks

Run when present:

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/test_docs_entrypoints.py
```

## Diff Checks

```powershell
git status --short
git diff --stat
git diff --check
```

## Grep Checks

```powershell
git grep -n ".agentmd"
git grep -n ".agent.md"
git grep -n "<legacy lowercase Agent entrypoint filename>"
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/grep-domain-pack.ps1
```

When running the second command, replace the placeholder with the retired
lowercase entrypoint filename. The Domain Pack helper excludes
`docs/history/**` and scans the Phase 11C legacy terms that need
classification: `Domain Pack`, `domain_pack`, `DomainQAGraph`,
`MultiAgentSupervisorGraph`, and `domain-packs`.
