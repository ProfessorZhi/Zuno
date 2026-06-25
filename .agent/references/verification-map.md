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
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/grep-domain-pack.ps1
```

When running the second command, replace the placeholder with the retired
lowercase entrypoint filename. The Domain Pack helper scans `Domain Pack`,
`domain_pack`, `DomainQAGraph`, `MultiAgentSupervisorGraph`, and
`domain-packs` while excluding `docs/architecture/history/**`; remaining hits
must be classified as Current compatibility, Target reference, Blocked Legacy,
or a bug to fix.
