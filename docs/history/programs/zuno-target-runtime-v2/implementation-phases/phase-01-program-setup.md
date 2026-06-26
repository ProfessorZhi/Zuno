# Phase 01 Program Setup

## Goal

Open `zuno-target-runtime-v2` as the active executable Agent program.

## Scope

- Add program README, roadmap, phase files, and evidence directory.
- Update current-program pointers.
- Update the architecture roadmap at a high level.
- Update workflow references to the active program.

## Non-Goals

- Runtime changes.
- Backend package moves.
- Test or verifier changes unrelated to recognizing the new active program.

## Verification

```powershell
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python tools/scripts/verify_docs_entrypoints.py
git diff --check
```
