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

## Agent System Verification

```powershell
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## Focused Docs / Agent Pytest

```powershell
pytest -q tests/test_docs_entrypoints.py tests/test_repo_structure_consistency.py tests/test_publish_boundary.py tests/test_agent_system.py tests/test_repo_hygiene.py -p no:cacheprovider
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

## Canonical Architecture Grep Checks

```powershell
git grep -n "zuno-ideal-architecture-and-repo-layout.html"
git grep -n "Native BM25"
git grep -n "RRF"
git grep -n "Summary Compression"
git grep -n "Structured Extraction"
git grep -n "ToolCard"
git grep -n "GraphRAGProjectSnapshot"
git grep -n "auto router"
```
