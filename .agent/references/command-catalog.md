# Command Catalog

## Documentation Gates

Preferred:

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
```

## Agent Workflow Gates

Preferred:

```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## Module Boundary Gates

Preferred for target runtime V2 backend boundary work:

```powershell
python .agent/scripts/verify_module_boundaries.py
```

## Frontend Dependency Install

Preferred:

```powershell
npm ci
```

Avoid `npm install` unless dependency metadata intentionally changes.

## Git

Preferred:

```powershell
git status --short
git diff --check
git commit -m "<message>"
git push
```

Avoid force push, force-with-lease, amend, and reset unless explicitly requested.

## Canonical Architecture Checks

```powershell
git grep -n "Native BM25"
git grep -n "RRF"
git grep -n "Summary Compression"
git grep -n "Structured Extraction"
git grep -n "ToolCard"
git grep -n "auto router"
```
