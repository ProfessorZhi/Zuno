# Phase 02: Docs / Spec / Current Truth Cleanup

## Goal

Clean current docs, specs, and Agent references so they do not present retired
Domain Pack or old query-mode surfaces as the future mainline.

## Why This Phase Exists

Implementation workers need current docs to point at GraphRAG Project and
query methods without losing historical evidence.

## Required Reading

- Phase 01 evidence package
- `docs/architecture/README.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `.agent/references/current-program.md`
- `.agent/references/docs-map.md`

## Scope

Docs and Agent workflow references only.

## Non-goals

- runtime behavior changes
- frontend implementation changes
- deleting history/audit evidence
- moving large docs trees

## Candidate Files

- `docs/architecture/README.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/specs/`
- `.agent/programs/official-graphrag-cleanup-v1/`
- `.agent/references/`
- `.agent/architecture/near-term/`
- `AGENTS.md`

## Execution Order

1. Start from the Phase 01 inventory.
2. Update only current entrypoints that mislead implementation work.
3. Leave old terms in `history/`, `audits/`, retired terminology, and migration
   notes.
4. Ensure `.agent` points to the implementation roadmap and phase map.
5. Run docs verification.

## Acceptance Criteria

- Current docs point to GraphRAG Project, query methods, and Enhanced Mode.
- Domain Pack is not described as the future mainline.
- History and audits remain reachable as evidence.
- Future items are not near-term acceptance requirements.

## Verification Commands

```powershell
powershell -ExecutionPolicy Bypass -File .agent\scripts\verify-workflow.ps1
python tools\scripts\verify_docs_entrypoints.py
pytest -q tests\test_docs_entrypoints.py
git diff --check
git status --short
```

## GitHub Sync Requirements

Before editing:

```powershell
git branch --show-current
git status --short
git log -1 --oneline
```

Before commit:

```powershell
git status --short
git diff --stat
git diff --check
```

After validation passes:

```powershell
git add docs .agent AGENTS.md
git commit -m "docs: align graphrag current truth"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Updating current docs requires runtime code changes.
- A historical doc is the only source for a claim.
- Phase 01 evidence is missing or stale.

## Evidence Package Required

- changed docs list
- current-vs-history grep classification
- verification output summary
- commit hash and push result

## Risks

- Over-cleaning history can destroy useful evidence.
- Under-cleaning current docs can mislead later runtime work.

## Follow-up Phase

Phase 03: Domain Pack Contract Retirement.
