# Phase 00: Docs And Agent Workflow

## Goal

Make `docs/`, `AGENTS.md`, `.agent/`, and `docs/architecture/history/` self-maintaining and unambiguous.

## Scope

Documentation and workflow files only.

## Files to change

- `AGENTS.md`
- `.agent/`
- `.gitignore`
- `docs/architecture/`

## Files not to change

- `src/backend/zuno/`
- `apps/web/`
- `apps/desktop/`
- `infra/`
- package and lock files

## Acceptance gates

- `AGENTS.md` is the only repository-level Agent entrypoint.
- `.agent/` contains references, templates, scripts, and current architecture references.
- `docs/architecture/README.md` points to this program.
- Superseded programs live under `docs/architecture/history/`.

## Verification commands

```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
git diff --check
```

## Evidence to return

- changed file list
- verification output summary
- git commit and push result
