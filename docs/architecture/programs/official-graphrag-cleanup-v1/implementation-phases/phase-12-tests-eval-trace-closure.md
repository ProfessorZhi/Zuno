# Phase 12: Tests / Eval / Trace Closure

## Goal

Close the implementation program with tests, evals, trace proof, docs sync, and
final legacy grep classification.

## Why This Phase Exists

Passing unit tests alone does not prove the architecture is implemented. Final
closure needs end-to-end evidence for contracts, routing, Enhanced Mode, evals,
and docs.

## Required Reading

- evidence packages from Phases 01-11
- `../implementation-roadmap.md`
- `.agent/architecture/near-term/16-near-term-acceptance-gates.md`
- `docs/architecture/audits/real-runtime-multihop-eval-results.md`

## Scope

Unit tests, docs entrypoint tests, GraphRAG Project tests, query router tests,
Enhanced Mode trace tests, frontend contract tests, eval fixtures, final grep
gate, docs sync, commit, and push.

## Non-goals

- new feature development
- future Java/microservices/event-worker/multi-agent work
- deleting historical evidence

## Candidate Files

- `tests/`
- `tools/evals/zuno/`
- `docs/architecture/audits/`
- `docs/architecture/programs/official-graphrag-cleanup-v1/`
- `.agent/references/`
- `.agent/architecture/near-term/`

## Execution Order

1. Re-run docs and workflow checks.
2. Run unit and contract test groups from all completed phases.
3. Run eval or smoke eval commands required by the current evidence gate.
4. Run final legacy grep classification.
5. Update docs with actual evidence, not intent.
6. Commit and push final closure.

## Acceptance Criteria

- Unit tests pass.
- Docs entrypoint tests pass.
- GraphRAG Project tests pass.
- Query method router tests pass.
- Enhanced Mode trace tests pass.
- Frontend contract tests pass.
- Eval evidence proves baseline preservation and trace coverage.
- Final grep gate allows old terms only in history, audits, retired
  terminology, migration notes, or compatibility tests kept by policy.
- Final docs match current runtime evidence.

## Verification Commands

```powershell
powershell -ExecutionPolicy Bypass -File .agent\scripts\verify-workflow.ps1
python tools\scripts\verify_docs_entrypoints.py
pytest -q tests\test_docs_entrypoints.py
pytest -q
git diff --check
git grep -n "domain_pack_id"
git grep -n "Domain Pack"
git grep -n "rag_graph_deep"
git grep -n "local_graphrag"
git grep -n "community_global"
git grep -n "drift_like"
git grep -n "agentchat"
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
git add tests tools docs .agent
git commit -m "test: close graphrag implementation evidence"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Eval evidence contradicts docs.
- Legacy grep hits remain in active public/runtime paths.
- Test coverage is too narrow for final closure claims.

## Evidence Package Required

- command-by-command validation table
- eval report paths and summary metrics
- final grep classification
- docs updated from fresh evidence
- commit hash and push result

## Risks

- Treating a narrow smoke test as full architecture proof.
- Letting stale audit text override fresh runtime evidence.

## Follow-up Phase

No near-term follow-up phase. Future Java, microservice, event-worker, or
multi-agent work requires a separate program.
