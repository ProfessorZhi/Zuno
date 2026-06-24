# Phase 01: Legacy Surface Audit

## Goal

Create a read-only inventory of legacy, Domain Pack, old query mode, agentchat,
compat, and alias surfaces across the repo.

## Why This Phase Exists

The current code still contains active Domain Pack APIs, frontend pages,
retrieval aliases, compat tests, and launcher names. Deletion before inventory
would be guesswork.

## Required Reading

- `../implementation-roadmap.md`
- `.agent/architecture/decisions/03-retired-surfaces.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/audits/tests-folder-organization-audit.md`

## Scope

Read-only scan of runtime, frontend, tests, docs, tools, launchers, infra, and
Domain Pack assets.

## Non-goals

- no file edits
- no code deletion
- no commit
- no push

## Candidate Files

- `src/backend/zuno/`
- `apps/web/`
- `apps/desktop/`
- `tests/`
- `tools/`
- `infra/`
- `domain-packs/`
- `docs/architecture/`
- `.agent/`

## Execution Order

1. Capture `git branch --show-current`, `git status --short`, and
   `git log -1 --oneline`.
2. Run legacy grep commands for Domain Pack, query modes, `agentchat`,
   `services/api`, `zuno/legacy`, and `compat`.
3. Classify every hit as active runtime, frontend public contract, test-only,
   tool/eval, docs current, docs history/audit, or migration note.
4. Mark each hit as migrate, delete later, keep until final closure, or
   high-risk dependency.
5. Return a migration inventory with next-phase blockers.

## Acceptance Criteria

- Every retired term has path, line summary, classification, and recommended
  phase.
- Domain Pack runtime and frontend surfaces are not deleted.
- `tests/compat/` is classified as test protection, not removed.
- Evidence is enough for Phase 02 and Phase 03 to act.

## Verification Commands

```powershell
git status --short
git grep -n "domain_pack_id"
git grep -n "Domain Pack"
git grep -n "DomainPack"
git grep -n "rag_graph_deep"
git grep -n "local_graphrag"
git grep -n "community_global"
git grep -n "drift_like"
git grep -n "agentchat"
git grep -n "services/api"
git grep -n "zuno/legacy"
git grep -n "compat"
```

## GitHub Sync Requirements

This phase is read-only. Do not commit or push.

Before ending, run:

```powershell
git status --short
```

## Stop Conditions

- Worktree is dirty before audit.
- A grep command would require generated output files to be committed.
- The inventory cannot distinguish active code from history.

## Evidence Package Required

- branch and status
- classified grep table
- high-risk dependency list
- recommended Phase 02 and Phase 03 starting files

## Risks

- Broad grep output can hide critical active hits.
- Tests may intentionally preserve legacy behavior until final closure.

## Follow-up Phase

Phase 02: Docs / Spec / Current Truth Cleanup.
