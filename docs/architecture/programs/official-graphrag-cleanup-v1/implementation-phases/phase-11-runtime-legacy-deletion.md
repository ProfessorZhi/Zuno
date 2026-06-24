# Phase 11: Runtime Legacy Deletion

## Goal

Delete or archive old runtime surfaces only after earlier phases prove active
contracts no longer depend on them.

## Why This Phase Exists

Domain Pack services, DomainQAGraph naming, old query modes, agentchat launcher
names, and compat aliases are high-risk until contracts and tests migrate.

## Required Reading

- Phase 01 inventory
- Phase 03 through Phase 10 evidence packages
- `.agent/architecture/decisions/03-retired-surfaces.md`
- `docs/architecture/decisions/0002-retire-compat-namespace.md`

## Scope

Runtime deletion, imports, old route removal, alias cleanup, launcher names,
tests, migration docs, and final grep classification.

## Non-goals

- deleting evidence from history/audits
- removing `tests/compat/` before replacement tests exist
- changing future architecture scope

## Candidate Files

- `src/backend/zuno/services/domain_pack/`
- `src/backend/zuno/domain_packs/`
- `domain-packs/`
- `src/backend/zuno/api/v1/domain_packs.py`
- `src/backend/zuno/api/services/domain_pack.py`
- `src/backend/zuno/core/graphs/domain_qa_graph.py`
- `src/backend/zuno/core/graphs/states.py`
- `src/backend/zuno/legacy/`
- `tools/launchers/windows/_Zuno-Web-Common.cmd`
- `tests/compat/`

## Execution Order

1. Prove no active imports for each deletion candidate.
2. Move or delete one surface at a time.
3. Replace tests that still protect current behavior.
4. Update docs and migration notes.
5. Run grep gates and targeted runtime tests after each deletion group.

## Acceptance Criteria

- No hidden active import depends on deleted surfaces.
- Old terms appear only in allowed locations.
- Tests cover replacement behavior.
- Runtime startup and public entrypoint tests pass.

## Verification Commands

```powershell
pytest -q tests/test_zuno_public_entrypoints.py
pytest -q tests/test_zuno_runtime_chain_guard.py
pytest -q tests/test_phase25_legacy_boundary_hardening.py
pytest -q
git grep -n "domain_pack_id"
git grep -n "DomainQAGraph"
git grep -n "agentchat"
git diff --check
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
git add src/backend/zuno tests tools docs .agent domain-packs
git commit -m "refactor: delete legacy graphrag surfaces"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Any deletion candidate still has active imports.
- Compatibility tests are the only proof of a current behavior.
- Grep hits cannot be classified.

## Evidence Package Required

- active import proof
- deleted or archived surface list
- replacement test list
- grep classification
- full validation output
- commit hash and push result

## Risks

- Removing compatibility before replacement tests exist.
- Breaking local launchers or eval tools that still use old names.

## Follow-up Phase

Phase 12: Tests / Eval / Trace Closure.
