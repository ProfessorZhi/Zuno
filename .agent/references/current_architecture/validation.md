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
git grep -n "Domain Pack"
git grep -n "domain_pack"
```

When running the second command, replace the placeholder with the retired lowercase entrypoint filename. Historical hits are allowed when they live under `docs/architecture/history/` or explicitly describe a migration.
