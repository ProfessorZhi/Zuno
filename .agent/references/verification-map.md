# Verification Map

## Workflow Verification

```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## Docs Entrypoint Verification

Run these if present:

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/test_docs_entrypoints.py
```

## Git And Diff Checks

```powershell
git status --short
git diff --stat
git diff --check
```

## Legacy Grep Checks

```powershell
git grep -n ".agentmd"
git grep -n ".agent.md"
git grep -n "<legacy lowercase Agent entrypoint filename>"
git grep -n "Domain Pack"
git grep -n "domain_pack"
```

When running the second command, replace the placeholder with the retired lowercase entrypoint filename. Hits inside `docs/architecture/history/` or migration notes can be allowed when they are explicitly historical. Hits in current entrypoints must be fixed or explained.
