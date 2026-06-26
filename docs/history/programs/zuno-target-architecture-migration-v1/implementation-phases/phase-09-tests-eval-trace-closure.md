# Phase 09: Tests Eval Trace Closure

## Goal

Close the target migration with full tests, eval baseline comparison, trace
proof, docs sync, and final grep classification.

## Dependency

Phase 01 through Phase 08 complete.

## Scope

- Run full `pytest -q`.
- Run formal Eval baseline comparison.
- Classify legacy grep output.
- Update `docs/architecture/current-architecture.md`,
  `docs/architecture/target-architecture.md`, `docs/architecture/roadmap.md`,
  and `.agent/references/`.
- Commit and push closure evidence.

## Files To Change

- docs and `.agent` status surfaces
- eval evidence docs
- tests only if closure reveals missing coverage

## Files Not To Change

- New features after closure starts.
- Future Java/microservice/event-worker/multi-agent work.

## Acceptance Gates

- Full pytest passes.
- Eval baseline comparison is recorded.
- Legacy terms appear only in allowed history/migration/compat locations.
- Current docs match runtime evidence.
- Target docs do not claim unimplemented Future work.

## Verification Commands

```powershell
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q
git grep -n "domain_pack_id"
git grep -n "DomainQAGraph"
git grep -n "MultiAgentSupervisorGraph"
git diff --check
```

## Evidence To Return

- command matrix
- eval report paths and summary metrics
- final grep classification
- commit hash and push result
